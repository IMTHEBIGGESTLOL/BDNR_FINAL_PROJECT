import random
import uuid

import time_uuid
from cassandra.query import BatchStatement
from datetime import datetime, timedelta
from DGraph import modeldgraph
import requests
from bson import ObjectId  # Importa para manejar los ObjectId


CREATE_KEYSPACE = """
        CREATE KEYSPACE IF NOT EXISTS {}
        WITH replication = {{ 'class': 'SimpleStrategy', 'replication_factor': {} }}
"""

CREATE_TEST = """
    CREATE TABLE IF NOT EXISTS users_by_id (
        user_id INT, 
        username TEXT, 
        email TEXT, 
        role TEXT,
        PRIMARY KEY ((user_id))
    );
"""

CREATE_TICKET_BY_DATE_TABLE = """
    CREATE TABLE IF NOT EXISTS ticket_by_date (
        created_date DATE,
        created_timestamp TIMESTAMP,
        ticket_id INT,
        customer_id INT,
        description TEXT,
        status TEXT,
        PRIMARY KEY ((created_date),ticket_id,  created_timestamp)
    ) WITH CLUSTERING ORDER BY (ticket_id ASC, created_timestamp ASC);
"""

CREATE_ACTIVITY_BY_TICKET_TABLE = """
    CREATE TABLE IF NOT EXISTS activity_by_ticket (
        ticket_id INT,
        activity_timestamp TIMESTAMP,
        activity_type TEXT,
        status TEXT,
        agent_id INT,
        PRIMARY KEY ((ticket_id), agent_id, activity_timestamp)
    ) WITH CLUSTERING ORDER BY (agent_id ASC, activity_timestamp ASC);
"""

CREATE_TICKETS_BY_AGENT_DATE_TABLE = """
    CREATE TABLE IF NOT EXISTS tickets_by_agent_date (
        agent_id INT,
        assigned_date DATE,
        ticket_id INT,
        priority TEXT,
        status TEXT,
        PRIMARY KEY ((agent_id), ticket_id, assigned_date)
    ) WITH CLUSTERING ORDER BY (ticket_id ASC, assigned_date ASC);
"""

CREATE_FEEDBACK_BY_AGENT_TABLE = """
    CREATE TABLE IF NOT EXISTS feedback_by_agent (
        agent_id INT,
        ticket_id INT,
        feedback_rating INT,
        feedback_comments TEXT,
        PRIMARY KEY ((agent_id), ticket_id)
    );
"""

CREATE_URGENT_TICKETS_BY_TIME_TABLE = """
    CREATE TABLE IF NOT EXISTS urgent_tickets_by_time (
        priority TEXT,
        created_timestamp DATE,
        ticket_id INT,
        customer_id INT,
        description TEXT,
        agent_id INT,
        PRIMARY KEY (priority, created_timestamp, ticket_id)
    );
"""

CREATE_TICKETS_BY_CUSTOMER_TABLE = """
    CREATE TABLE IF NOT EXISTS tickets_by_customer (
        customer_id INT,
        ticket_id INT,
        created_timestamp TIMESTAMP,
        status TEXT,
        priority TEXT,
        PRIMARY KEY ((customer_id), ticket_id, created_timestamp)
    ) WITH CLUSTERING ORDER BY (ticket_id ASC, created_timestamp ASC);
"""

CREATE_ESCALATION_BY_TICKET_TABLE = """
    CREATE TABLE IF NOT EXISTS escalation_by_ticket (
        ticket_id INT,
        escalation_timestamp TIMESTAMP,
        escalation_level TEXT,
        agent_id INT,
        comments TEXT,
        PRIMARY KEY ((ticket_id), agent_id, escalation_timestamp)
    ) WITH CLUSTERING ORDER BY (agent_id ASC, escalation_timestamp ASC);
"""

CREATE_TICKET_COUNT_BY_CHANNEL_DATE_TABLE = """
    CREATE TABLE IF NOT EXISTS ticket_count_by_channel_date (
        created_date DATE,
        support_channel TEXT,
        ticket_id INT,
        ticket_count INT,
        PRIMARY KEY ((created_date), support_channel, ticket_id)
    ) WITH CLUSTERING ORDER BY (support_channel ASC, ticket_id ASC);
"""

SELECT_TICKETS_BY_CUSTOMER = """
    SELECT ticket_id, customer_id, created_timestamp, status, priority
    FROM tickets_by_customer
    WHERE customer_id = ?
    ORDER BY created_timestamp ASC
"""

SELECT_TICKETS_BY_DATE = """
    SELECT ticket_id, created_timestamp, customer_id, description, status
    FROM ticket_by_date
    WHERE created_date = ?
    ORDER BY created_timestamp ASC
"""

SELECT_ACTIVITIES_BY_TICKET = """
    SELECT activity_timestamp, activity_type, status, agent_id, ticket_id
    FROM activity_by_ticket
    WHERE ticket_id = ?
    AND agent_id = ?
    ORDER BY activity_timestamp ASC
"""

SELECT_TICKETS_BY_AGENT_DATE = """
    SELECT assigned_date, ticket_id, priority, status, agent_id
    FROM tickets_by_agent_date
    WHERE agent_id = ?
    ORDER BY ticket_id ASC
"""

SELECT_FEEDBACK_BY_AGENT = """
    SELECT ticket_id, feedback_rating, feedback_comments, agent_id
    FROM feedback_by_agent
    WHERE agent_id = ?
    ORDER BY ticket_id ASC
"""

SELECT_URGENT_TICKETS_BY_TIME = """
    SELECT ticket_id, created_timestamp, customer_id, description, agent_id
    FROM urgent_tickets_by_time
    WHERE priority = 'high'
    AND created_timestamp <= ?
    AND created_timestamp >= ?
    ORDER BY created_timestamp ASC
"""
#FOR ADMIN
SELECT_ESCALATIONS_BY_TICKET_ADMIN = """
    SELECT escalation_timestamp, escalation_level, agent_id, comments
    FROM escalation_by_ticket
    WHERE ticket_id = ?
    ORDER BY escalation_timestamp ASC
"""
#FOR AGENTS
SELECT_ESCALATIONS_BY_TICKET_AGENT = """
    SELECT escalation_timestamp, escalation_level, agent_id, comments, ticket_id
    FROM escalation_by_ticket
    WHERE ticket_id = ?
    AND agent_id = ?
    ORDER BY escalation_timestamp ASC
"""

SELECT_TICKET_COUNT_BY_CHANNEL_DATE = """
    SELECT support_channel, ticket_count, ticket_id
    FROM ticket_count_by_channel_date
    WHERE created_date = ?
    AND support_channel = ?
    ORDER BY support_channel ASC, ticket_id ASC
"""

def create_keyspace(session, keyspace, replication_factor):
    session.execute(CREATE_KEYSPACE.format(keyspace, replication_factor))

def create_schema(session):
    session.execute(CREATE_TICKET_BY_DATE_TABLE)
    session.execute(CREATE_ACTIVITY_BY_TICKET_TABLE)
    session.execute(CREATE_TICKETS_BY_AGENT_DATE_TABLE)
    session.execute(CREATE_FEEDBACK_BY_AGENT_TABLE)
    session.execute(CREATE_URGENT_TICKETS_BY_TIME_TABLE)
    session.execute(CREATE_TICKETS_BY_CUSTOMER_TABLE)
    session.execute(CREATE_ESCALATION_BY_TICKET_TABLE)
    session.execute(CREATE_TICKET_COUNT_BY_CHANNEL_DATE_TABLE)

def bulk_insert(session, dgraph_client, mongo_client):
    base_url = "http://localhost:8003" 
    def convert_objectid(data):
        if isinstance(data, list):
            return [convert_objectid(item) for item in data]
        elif isinstance(data, dict):
            return {k: convert_objectid(v) for k, v in data.items()}
        elif isinstance(data, ObjectId):
            return str(data)
        else:
            return data

    # Prepare the insert statements for Cassandra
    ticket_by_date_stmt = session.prepare("INSERT INTO ticket_by_date (created_date, created_timestamp, ticket_id, customer_id, description, status) VALUES (?, ?, ?, ?, ?, ?)")
    activity_by_ticket_stmt = session.prepare("INSERT INTO activity_by_ticket (ticket_id, activity_timestamp, activity_type, status, agent_id) VALUES (?, ?, ?, ?, ?)")
    tickets_by_agent_date_stmt = session.prepare("INSERT INTO tickets_by_agent_date (agent_id, assigned_date, ticket_id, priority, status) VALUES (?, ?, ?, ?, ?)")
    feedback_by_agent_stmt = session.prepare("INSERT INTO feedback_by_agent (agent_id, ticket_id, feedback_rating, feedback_comments) VALUES (?, ?, ?, ?)")
    urgent_tickets_by_time_stmt = session.prepare("INSERT INTO urgent_tickets_by_time (priority, created_timestamp, ticket_id, customer_id, description, agent_id) VALUES (?, ?, ?, ?, ?, ?)")
    tickets_by_customer_stmt = session.prepare("INSERT INTO tickets_by_customer (customer_id, ticket_id, created_timestamp, status, priority) VALUES (?, ?, ?, ?, ?)")
    escalation_by_ticket_stmt = session.prepare("INSERT INTO escalation_by_ticket (ticket_id, escalation_timestamp, escalation_level, agent_id, comments) VALUES (?, ?, ?, ?, ?)")
    ticket_count_by_channel_date_stmt = session.prepare("INSERT INTO ticket_count_by_channel_date (created_date, support_channel, ticket_count, ticket_id) VALUES (?, ?, ?, ?)")

    # MongoDB Collections
    db = mongo_client["final_project"] 
    tickets_collection = db["tickets"]
    users_collection = db["users"]
    agent_assignments_collection = db["agent_assignments"]
    daily_reports_collection = db["daily_reports"]

    # Data generation
    ticket_ids = [i for i in range(1, 11)]
    agent_ids = [i for i in range(1, 3)]
    customer_ids = [i for i in range(1, 3)]
    support_channels = ['phone', 'email', 'chat']
    statuses = ['open', 'resolved', 'in_progress']
    priorities = ['high', 'medium', 'low']
    feedback_ratings = [1, 2, 3, 4, 5]
    escalation_levels = ['level_1', 'level_2', 'level_3']

    batch = BatchStatement()

    # Create agents and customers in the Users collection
    users_data = [
        {"uuid": f"{agent_id}_", "username": f"agent_{i+1}", "email": f"agent{agent_id}@example.com","role": "agent", "profile": {"name": f"Agent {i+1}"}} for i, agent_id in enumerate(agent_ids)
    ] + [
        {"uuid": f"{customer_id}", "username": f"customer_{i+1}", "email": f"customer{customer_id}@example.com","role": "customer", "profile": {"name": f"Customer {i+1}"}} for i, customer_id in enumerate(customer_ids)
    ]
    #users_collection.insert_many(users_data)
    
    users_data_serializable = convert_objectid(users_data)
    requests.post(f"{base_url}/users/", json=users_data_serializable)

    ticket_data = []
    for i, ticket_id in enumerate(ticket_ids):
        customer_id = random.choice(customer_ids)
        agent_id = random.choice(agent_ids)
        created_date = datetime.now().date()
        created_timestamp = datetime.now() + timedelta(seconds=i) #all are unique
        escalation_timestamp = datetime.now() + timedelta(seconds=i)
        description = f"Ticket {i+1} description"
        status = random.choice(statuses)
        priority = random.choice(priorities)
        feedback_rating = random.choice(feedback_ratings)
        escalation_level = random.choice(escalation_levels)
        support_channel = random.choice(support_channels)

        # Insert into Cassandra
        batch.add(ticket_by_date_stmt, (created_date, created_timestamp, ticket_id, customer_id, description, status))
        batch.add(tickets_by_agent_date_stmt, (agent_id, created_date, ticket_id, priority, status))
        batch.add(tickets_by_customer_stmt, (customer_id, ticket_id, created_timestamp, status, priority))
        batch.add(activity_by_ticket_stmt, (ticket_id, created_timestamp, "created", status, agent_id))
        batch.add(feedback_by_agent_stmt, (agent_id, ticket_id, feedback_rating, "Comments", ))
        batch.add(urgent_tickets_by_time_stmt, (priority, created_timestamp, ticket_id, customer_id, "description", agent_id))
        batch.add(escalation_by_ticket_stmt, (ticket_id, escalation_timestamp, escalation_level, agent_id, "Comments"))
        batch.add(ticket_count_by_channel_date_stmt, (created_timestamp, support_channel, i, ticket_id))

        # Collect data for Dgraph
        ticket_data.append({
            'uid': f'_:ticket{i+1}',
            'dgraph.type': 'Ticket',
            'ticket_id': ticket_id,
            'status': status,
            'priority': priority,
            'created_at': created_timestamp.isoformat(),
            'assigned_to': {'uid': f'_:agent{agent_ids.index(agent_id)+1}'},
            'created_by': {'uid': f'_:customer{customer_ids.index(customer_id)+1}'},
            'messages': [{'uid': f'_:message{i}', 'dgraph.type': 'Message', 'sender': { 'uid' : f'_:customer{customer_ids.index(customer_id)+1}'}, 'message_text': 'text', 'belongs_to': {'uid': f'_:ticket{i+1}'}},]
        })

        #Data to mongoDB
        # Mongo: Insert into Tickets Collection
        ticket_document = {
            "uuid": ticket_id,
            "customer_id": customer_id,
            "description": f"Ticket {i+1} issue description",
            "status": random.choice(statuses),
            "priority": random.choice(priorities),
            "created_timestamp": created_timestamp.isoformat(),
            "updated_timestamp": created_timestamp.isoformat(),
            "category": "technical",
            "messages": [],
            "feedback": {
                "rating": None,
                "comments": None,
                "submitted_timestamp": None
            },
            "resolution_steps": [],
            "channel": random.choice(support_channels)
        }

        ticket_document_serializable = [{
            'uuid': str(ticket_document['uuid']),  # Convert uuid to string
            'customer_id': str(ticket_document['customer_id']),  # Convert customer_id to string
            'description': ticket_document['description'],
            'status': ticket_document['status'],
            'priority': ticket_document['priority'],
            'created_timestamp': ticket_document['created_timestamp'],
            'updated_timestamp': ticket_document['updated_timestamp'],
            'category': ticket_document['category'],
            'messages': ticket_document['messages'],
            'feedback': ticket_document['feedback'],
            'resolution_steps': ticket_document['resolution_steps'],
            'channel': ticket_document['channel'],
        }]
        requests.post(f"{base_url}/tickets/", json=ticket_document_serializable)


        # Mongo: Insert into AgentAssignments Collection
        assignment_document = {
            "uuid": str(uuid.uuid4()),
            "agent_id": agent_id,
            "ticket_id": ticket_id,
            "assigned_timestamp": created_timestamp.isoformat(),
            "priority_level": ticket_document["priority"]
        }
        
        assignment_document_serializable = [{
            'uuid': str(assignment_document['uuid']),  # Convert uuid to string
            'agent_id': str(assignment_document['agent_id']),  # Convert customer_id to string
            'ticket_id': str(assignment_document['ticket_id']),
            'assigned_timestamp': assignment_document['assigned_timestamp'],
            'priority_level': assignment_document['priority_level'],
        }]    
        response = requests.post(f"{base_url}/AgentAssignments/", json=assignment_document_serializable)
        if response.status_code == 422:
            print(response.json())  

        
    
    # Generate and insert daily report
    daily_report = {
        "uuid": str(uuid.uuid4()),
        "report_date": datetime.now().date().isoformat(),
        "ticket_count": len(ticket_ids),
        "channel_stats": {
            channel: sum(1 for t in tickets_collection.find({"channel": channel})) for channel in support_channels
        }
    }
    

    daily_report_serializable = [convert_objectid(daily_report)]
    response = requests.post(f"{base_url}/dailyReports/", json=daily_report_serializable)
    if response.status_code == 422:
        print(response.json())  
    
    
    # Execute the batch
    session.execute(batch)
    
    # Insert data into Dgraph
    modeldgraph.create_data(dgraph_client, ticket_data, agent_ids, customer_ids)
    print("Bulk insert complete!")


#User the Tickets by Customer table, for usage on admin and customer
def get_user_tickets(session, customer_id):
    stmt = session.prepare(SELECT_TICKETS_BY_CUSTOMER)
    rows = session.execute(stmt, [customer_id])
    print("\n")
    for row in rows:
        print(f"=== Customer_id: {row.customer_id} ===")
        print(f"- Ticket_id: {row.ticket_id}")
        print(f"created on: {row.created_timestamp}")
        print(f"status: {row.status}")
        print(f"priority: {row.priority}")
    print("\n")
    input("Press any key to continue...")
    print("\n")

# 1. Retrieve Tickets by Date
def get_tickets_by_date(session, created_date):
    stmt = session.prepare(SELECT_TICKETS_BY_DATE)
    rows = session.execute(stmt, [created_date])
    print("\n")
    for row in rows:
        print(f"=== Customer_id: {row.customer_id} ===")
        print(f"- Ticket_id: {row.ticket_id}")
        print(f"created on: {row.created_timestamp}")
        print(f"status: {row.status}")
        print(f"Description: {row.description}")
    print("\n")
    input("Press any key to continue...")
    print("\n")


# 2. Fetch Activities for a Ticket
def get_activities_by_ticket(session, ticket_id, agent_id):
    stmt = session.prepare(SELECT_ACTIVITIES_BY_TICKET)
    rows = session.execute(stmt, [ticket_id, agent_id])
    print("\n")
    for row in rows:
        print(f"=== agent_id: {row.agent_id} ===")
        print(f"- Ticket_id: {row.ticket_id}")
        print(f"Update date: {row.activity_timestamp}")
        print(f"status: {row.status}")
        print(f"Type: {row.activity_type}")
        print("\n")
    print("\n")
    input("Press any key to continue...")
    print("\n")

# 3. List Tickets Assigned to Agent by Date
def get_tickets_by_agent_date(session, agent_id):
    stmt = session.prepare(SELECT_TICKETS_BY_AGENT_DATE)
    rows = session.execute(stmt, [agent_id])
    print("\n")
    for row in rows:
        print(f"=== agent_id: {row.agent_id} ===")
        print(f"- Ticket_id: {row.ticket_id}")
        print(f"assigned date: {row.assigned_date}")
        print(f"status: {row.status}")
        print(f"priority: {row.priority}")
        print("\n")
    print("\n")
    input("Press any key to continue...")
    print("\n")

# 4. Fetch Agent’s Ticket Feedback
def get_feedback_by_agent(session, agent_id):
    stmt = session.prepare(SELECT_FEEDBACK_BY_AGENT)
    rows = session.execute(stmt, [agent_id])
    print("\n")
    for row in rows:
        print(f"=== agent_id: {row.agent_id} ===")
        print(f"- Ticket_id: {row.ticket_id}")
        print(f" Comments: {row.feedback_comments}")
        print(f"Rating : {row.feedback_rating}")
        print("\n")
    print("\n")
    input("Press any key to continue...")
    print("\n")

# 5. Retrieve Urgent Tickets by Time Range
def get_urgent_tickets_by_time(session, start_time, end_time):
    stmt = session.prepare(SELECT_URGENT_TICKETS_BY_TIME)
    rows = session.execute(stmt, [end_time, start_time])
    print("\n")
    for row in rows:
        print(f"=== agent_id: {row.agent_id} ===")
        print(f"- Ticket_id: {row.ticket_id}")
        print(f" Description: {row.description}")
        print(f"Customer_id : {row.customer_id}")
        print(f"Created on: {row.created_timestamp}")
        print("\n")
    print("\n")
    input("Press any key to continue...")
    print("\n")

# 7. Track Escalations for a Ticket
def get_escalations_by_ticket(session, ticket_id, agent_id):
    stmt = session.prepare(SELECT_ESCALATIONS_BY_TICKET_AGENT)
    rows = session.execute(stmt, [ticket_id, agent_id])
    print("\n")
    for row in rows:
        print(f"=== agent_id: {row.agent_id} ===")
        print(f"- Ticket_id: {row.ticket_id}")
        print(f"Escalation date: {row.escalation_timestamp}")
        print(f"Comments: {row.comments}")
        print(f"Level of escalation: {row.escalation_level}")
        print("\n")
    print("\n")
    input("Press any key to continue...")
    print("\n")

# 8. Generate Daily Channel Report
def get_daily_channel_report(session, created_date, channel):
    stmt = session.prepare(SELECT_TICKET_COUNT_BY_CHANNEL_DATE)
    rows = session.execute(stmt, [created_date, channel])
    print("\n")
    for row in rows:
        print(f"- Ticket_id: {row.ticket_id}")
        print(f" Support Channel: {row.support_channel}")
        print(f" Count: {row.ticket_count}")
        print("\n")
    print("\n")
    input("Press any key to continue...")
    print("\n")
