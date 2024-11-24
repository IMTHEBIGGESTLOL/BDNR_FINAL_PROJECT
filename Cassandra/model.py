import random
import uuid

import time_uuid
from cassandra.query import BatchStatement
from datetime import datetime

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
        PRIMARY KEY ((created_date), created_timestamp)
    ) WITH CLUSTERING ORDER BY (created_timestamp ASC);
"""

CREATE_ACTIVITY_BY_TICKET_TABLE = """
    CREATE TABLE IF NOT EXISTS activity_by_ticket (
        ticket_id INT,
        activity_timestamp TIMESTAMP,
        activity_type TEXT,
        status TEXT,
        agent_id INT,
        PRIMARY KEY ((ticket_id), activity_timestamp)
    ) WITH CLUSTERING ORDER BY (activity_timestamp ASC);
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
        priority_level TEXT,
        created_timestamp TIMESTAMP,
        ticket_id INT,
        customer_id INT,
        description TEXT,
        agent_id INT,
        PRIMARY KEY ((priority_level), created_timestamp)
    ) WITH CLUSTERING ORDER BY (created_timestamp ASC);
"""

CREATE_TICKETS_BY_CUSTOMER_TABLE = """
    CREATE TABLE IF NOT EXISTS tickets_by_customer (
        customer_id INT,
        ticket_id INT,
        created_timestamp TIMESTAMP,
        status TEXT,
        priority TEXT,
        PRIMARY KEY ((customer_id), created_timestamp)
    ) WITH CLUSTERING ORDER BY (created_timestamp ASC);
"""

CREATE_ESCALATION_BY_TICKET_TABLE = """
    CREATE TABLE IF NOT EXISTS escalation_by_ticket (
        ticket_id INT,
        escalation_timestamp TIMESTAMP,
        escalation_level TEXT,
        agent_id INT,
        comments TEXT,
        PRIMARY KEY ((ticket_id), escalation_timestamp)
    ) WITH CLUSTERING ORDER BY (escalation_timestamp ASC);
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

def bulk_insert(session):
    # Prepare the insert statements for all the tables
    ticket_by_date_stmt = session.prepare("INSERT INTO ticket_by_date (created_date, created_timestamp, ticket_id, customer_id, description, status) VALUES (?, ?, ?, ?, ?, ?)")
    activity_by_ticket_stmt = session.prepare("INSERT INTO activity_by_ticket (ticket_id, activity_timestamp, activity_type, status, agent_id) VALUES (?, ?, ?, ?, ?)")
    tickets_by_agent_date_stmt = session.prepare("INSERT INTO tickets_by_agent_date (agent_id, assigned_date, ticket_id, priority, status) VALUES (?, ?, ?, ?, ?)")
    feedback_by_agent_stmt = session.prepare("INSERT INTO feedback_by_agent (agent_id, ticket_id, feedback_rating, feedback_comments) VALUES (?, ?, ?, ?)")
    urgent_tickets_by_time_stmt = session.prepare("INSERT INTO urgent_tickets_by_time (priority_level, created_timestamp, ticket_id, customer_id, description, agent_id) VALUES (?, ?, ?, ?, ?, ?)")
    tickets_by_customer_stmt = session.prepare("INSERT INTO tickets_by_customer (customer_id, ticket_id, created_timestamp, status, priority) VALUES (?, ?, ?, ?, ?)")
    escalation_by_ticket_stmt = session.prepare("INSERT INTO escalation_by_ticket (ticket_id, escalation_timestamp, escalation_level, agent_id, comments) VALUES (?, ?, ?, ?, ?)")
    ticket_count_by_channel_date_stmt = session.prepare("INSERT INTO ticket_count_by_channel_date (created_date, support_channel, ticket_count, ticket_id) VALUES (?, ?, ?, ?)")
    
    # Prepare the data
    ticket_ids = [i for i in range(1, 11)]
    agent_ids = [i for i in range(1, 3)]
    customer_ids = [i for i in range(0, 2)]
    support_channels = ['phone', 'email', 'chat']
    statuses = ['open', 'resolved', 'in_progress']
    priorities = ['high', 'medium', 'low']
    feedback_ratings = [1, 2, 3, 4, 5]
    escalation_levels = ['level_1', 'level_2', 'level_3']

    # Batch for the inserts
    batch = BatchStatement()

    # 1. ticket_by_date (Retrieve all tickets created on a specific day, sorted by time)
    for ticket_id in ticket_ids:
        created_date = datetime.now().date()
        created_timestamp = datetime.now()
        customer_id = random.choice(customer_ids)
        description = "Ticket description"
        status = random.choice(statuses)
        batch.add(ticket_by_date_stmt, (created_date, created_timestamp, ticket_id, customer_id, description, status))
    
    # 2. activity_by_ticket (Fetch all activities for a specific ticket, sorted by timestamp)
    for ticket_id in ticket_ids:
        activity_timestamp = datetime.now()
        activity_type = random.choice(['status_update', 'comment', 'escalation'])
        status = random.choice(statuses)
        agent_id = random.choice(agent_ids)
        batch.add(activity_by_ticket_stmt, (ticket_id, activity_timestamp, activity_type, status, agent_id))
    
    # 3. tickets_by_agent_date (List of all tickets assigned to a particular agent on a specific date)
    for agent_id in agent_ids:
        for ticket_id in ticket_ids:
            assigned_date = datetime.now().date()
            priority = random.choice(priorities)
            status = random.choice(statuses)
            batch.add(tickets_by_agent_date_stmt, (agent_id, assigned_date, ticket_id, priority, status))
    
    # 4. feedback_by_agent (Get feedback for all tickets resolved by a specific agent)
    for agent_id in agent_ids:
        for ticket_id in ticket_ids:
            feedback_rating = random.choice(feedback_ratings)
            feedback_comments = f"Feedback for {ticket_id}"
            batch.add(feedback_by_agent_stmt, (agent_id, ticket_id, feedback_rating, feedback_comments))
    
    # 5. urgent_tickets_by_time (Retrieve all urgent tickets created within a specific time range)
    for ticket_id in ticket_ids:
        created_timestamp = datetime.now()
        customer_id = random.choice(customer_ids)
        description = f"Urgent ticket description for {ticket_id}"
        agent_id = random.choice(agent_ids)
        batch.add(urgent_tickets_by_time_stmt, ('urgent', created_timestamp, ticket_id, customer_id, description, agent_id))
    
    # 6. tickets_by_customer (Retrieve all tickets created by a specific customer)
    for customer_id in customer_ids:
        for ticket_id in ticket_ids:
            created_timestamp = datetime.now()
            status = random.choice(statuses)
            priority = random.choice(priorities)
            batch.add(tickets_by_customer_stmt, (customer_id, ticket_id, created_timestamp, status, priority))
    
    # 7. escalation_by_ticket (Track escalations over time for a specific ticket)
    for ticket_id in ticket_ids:
        escalation_timestamp = datetime.now()
        escalation_level = random.choice(escalation_levels)
        agent_id = random.choice(agent_ids)
        comments = f"Escalation details for {ticket_id}"
        batch.add(escalation_by_ticket_stmt, (ticket_id, escalation_timestamp, escalation_level, agent_id, comments))
    
    # 8. ticket_count_by_channel_date (Generate a report of ticket count per channel for a specific day)
    for ticket_id in ticket_ids:
        created_date = datetime.now().date()
        support_channel = random.choice(support_channels)
        ticket_count = 1
        batch.add(ticket_count_by_channel_date_stmt, (created_date, support_channel, ticket_count, ticket_id))
    
    # Execute the batch
    session.execute(batch)

    print("Bulk insert complete!")

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