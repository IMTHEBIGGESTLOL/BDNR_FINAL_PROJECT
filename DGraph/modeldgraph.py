from datetime import datetime
import json
import uuid


import pydgraph

def set_schema(client):
    schema = """
    type User {
        username
        email
        role
        assigned_tickets
        created_tickets
    }

    type Ticket {
        ticket_id
        status
        priority
        created_at
        updated_at
        assigned_to
        messages
        created_by
    }

    type Message {
        message_id
        sender
        message_text
        timestamp
    }

    username: string @index(exact) .
    email: string @index(exact) .
    role: string @index(exact) .
    
    ticket_id: string @index(exact) .
    status: string @index(term) .
    priority: string @index(term) .
    created_at: datetime @index(hour) .
    updated_at: datetime @index(hour) .
    
    message_id: string @index(exact) .
    sender: uid .
    message_text: string @index(fulltext) .
    timestamp: datetime @index(hour) .
    
    assigned_to: uid @reverse .
    messages: [uid] .
    created_by: uid @reverse .
    assigned_tickets: [uid] .
    created_tickets: [uid] .
    """
    return client.alter(pydgraph.Operation(schema=schema))

import uuid
from datetime import datetime

import uuid
from datetime import datetime

def create_data(client):
    # Create a new transaction
    txn = client.txn()
    try:
        data = [
            # Users
            {
                'uid': f'_:user1',
                'dgraph.type': 'User',
                'user_id': str(uuid.uuid4()),
                'username': 'petlover1',
                'email': 'petlover1@example.com',
                'role': 'customer',
                'created_tickets': [{'uid': f'_:ticket1'}]
            },
            {
                'uid': f'_:user2',
                'dgraph.type': 'User',
                'user_id': str(uuid.uuid4()),
                'username': 'agent1',
                'email': 'agent1@example.com',
                'role': 'agent',
                'assigned_tickets': [{'uid': f'_:ticket1'}]
            },
            {
                'uid': f'_:user3',
                'dgraph.type': 'User',
                'user_id': str(uuid.uuid4()),
                'username': 'petlover2',
                'email': 'petlover2@example.com',
                'role': 'customer',
                'created_tickets': [{'uid': f'_:ticket2'}]
            },
            {
                'uid': f'_:user4',
                'dgraph.type': 'User',
                'user_id': str(uuid.uuid4()),
                'username': 'agent2',
                'email': 'agent2@example.com',
                'role': 'agent',
                'assigned_tickets': [{'uid': f'_:ticket2'}]
            },
            {
                'uid': f'_:user5',
                'dgraph.type': 'User',
                'user_id': str(uuid.uuid4()),
                'username': 'admin1',
                'email': 'admin1@example.com',
                'role': 'admin'
            },

            # Tickets
            {
                'uid': f'_:ticket1',
                'dgraph.type': 'Ticket',
                'ticket_id': str(uuid.uuid4()),
                'status': 'open',
                'priority': 'high',
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat(),
                'customer_id': 'user1',
                'assigned_agent_id': 'user2',
                'assigned_to': {'uid': f'_:user2'}
            },
            {
                'uid': f'_:ticket2',
                'dgraph.type': 'Ticket',
                'ticket_id': str(uuid.uuid4()),
                'status': 'closed',
                'priority': 'medium',
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat(),
                'customer_id': 'user3',
                'assigned_agent_id': 'user4',
                'assigned_to': {'uid': f'_:user4'}
            },
            # Additional tickets...
            # Messages
            {
                'uid': f'_:message1',
                'dgraph.type': 'Message',
                'message_id': str(uuid.uuid4()),
                'sender_id': 'user1',
                'message_text': 'Need help with my pet\'s health.',
                'timestamp': datetime.now().isoformat(),
                'belongs_to_ticket': {'uid': f'_:ticket1'}
            },
            {
                'uid': f'_:message2',
                'dgraph.type': 'Message',
                'message_id': str(uuid.uuid4()),
                'sender_id': 'user2',
                'message_text': 'Your ticket has been assigned.',
                'timestamp': datetime.now().isoformat(),
                'belongs_to_ticket': {'uid': f'_:ticket1'}
            },
            # Additional messages...
        ]

        # Mutate the data
        response = txn.mutate(set_obj=data)

        # Commit the transaction
        commit_response = txn.commit()
        print(f"Commit Response: {commit_response}")
        print(f"UIDs: {response.uids}")
    finally:
        txn.discard()
