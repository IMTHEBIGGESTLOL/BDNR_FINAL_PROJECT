import datetime
import random
import uuid

import time_uuid
from cassandra.query import BatchStatement
import datetime

CREATE_KEYSPACE = """
        CREATE KEYSPACE IF NOT EXISTS {}
        WITH replication = {{ 'class': 'SimpleStrategy', 'replication_factor': {} }}
"""

CREATE_TEST = """
    CREATE TABLE IF NOT EXISTS users_by_id (
        user_id UUID, 
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
        ticket_id UUID,
        customer_id UUID,
        description TEXT,
        status TEXT,
        PRIMARY KEY ((created_date), created_timestamp)
    ) WITH CLUSTERING ORDER BY (created_timestamp ASC);
"""

CREATE_ACTIVITY_BY_TICKET_TABLE = """
    CREATE TABLE IF NOT EXISTS activity_by_ticket (
        ticket_id UUID,
        activity_timestamp TIMESTAMP,
        activity_type TEXT,
        status TEXT,
        agent_id UUID,
        PRIMARY KEY ((ticket_id), activity_timestamp)
    ) WITH CLUSTERING ORDER BY (activity_timestamp ASC);
"""

CREATE_TICKETS_BY_AGENT_DATE_TABLE = """
    CREATE TABLE IF NOT EXISTS tickets_by_agent_date (
        agent_id UUID,
        assigned_date DATE,
        ticket_id UUID,
        priority TEXT,
        status TEXT,
        PRIMARY KEY ((agent_id), ticket_id, assigned_date)
    ) WITH CLUSTERING ORDER BY (ticket_id ASC, assigned_date ASC);
"""

CREATE_FEEDBACK_BY_AGENT_TABLE = """
    CREATE TABLE IF NOT EXISTS feedback_by_agent (
        agent_id UUID,
        ticket_id UUID,
        feedback_rating INT,
        feedback_comments TEXT,
        PRIMARY KEY ((agent_id), ticket_id)
    );
"""

CREATE_URGENT_TICKETS_BY_TIME_TABLE = """
    CREATE TABLE IF NOT EXISTS urgent_tickets_by_time (
        priority_level TEXT,
        created_timestamp TIMESTAMP,
        ticket_id UUID,
        customer_id UUID,
        description TEXT,
        agent_id UUID,
        PRIMARY KEY ((priority_level), created_timestamp)
    ) WITH CLUSTERING ORDER BY (created_timestamp ASC);
"""

CREATE_TICKETS_BY_CUSTOMER_TABLE = """
    CREATE TABLE IF NOT EXISTS tickets_by_customer (
        customer_id UUID,
        ticket_id UUID,
        created_timestamp TIMESTAMP,
        status TEXT,
        priority TEXT,
        PRIMARY KEY ((customer_id), created_timestamp)
    ) WITH CLUSTERING ORDER BY (created_timestamp ASC);
"""

CREATE_ESCALATION_BY_TICKET_TABLE = """
    CREATE TABLE IF NOT EXISTS escalation_by_ticket (
        ticket_id UUID,
        escalation_timestamp TIMESTAMP,
        escalation_level TEXT,
        agent_id UUID,
        comments TEXT,
        PRIMARY KEY ((ticket_id), escalation_timestamp)
    ) WITH CLUSTERING ORDER BY (escalation_timestamp ASC);
"""

CREATE_TICKET_COUNT_BY_CHANNEL_DATE_TABLE = """
    CREATE TABLE IF NOT EXISTS ticket_count_by_channel_date (
        created_date DATE,
        support_channel TEXT,
        ticket_id UUID,
        ticket_count INT,
        PRIMARY KEY ((created_date), support_channel, ticket_id)
    ) WITH CLUSTERING ORDER BY (support_channel ASC, ticket_id ASC);
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