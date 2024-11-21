from datetime import datetime
import json

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

def create_data(client):
    # Create a new transaction.
    txn = client.txn()
    try:
        p = [
            # Users (Pet Wellness Project)
            {
                'uid': f'_:user{1}',
                'dgraph.type': 'User',
                'user_id': str(uuid.uuid4()),
                'username': 'petlover1',
                'email': 'petlover1@example.com',
                'role': 'user'
            },
            {
                'uid': f'_:user{2}',
                'dgraph.type': 'User',
                'user_id': str(uuid.uuid4()),
                'username': 'petlover2',
                'email': 'petlover2@example.com',
                'role': 'agent'
            },
            {
                'uid': f'_:user{3}',
                'dgraph.type': 'User',
                'user_id': str(uuid.uuid4()),
                'username': 'vet1',
                'email': 'vet1@example.com',
                'role': 'agent'
            },
            {
                'uid': f'_:user{4}',
                'dgraph.type': 'User',
                'user_id': str(uuid.uuid4()),
                'username': 'trainer1',
                'email': 'trainer1@example.com',
                'role': 'user'
            },
            {
                'uid': f'_:user{5}',
                'dgraph.type': 'User',
                'user_id': str(uuid.uuid4()),
                'username': 'admin1',
                'email': 'admin1@example.com',
                'role': 'agent'
            },
            {
                'uid': f'_:user{6}',
                'dgraph.type': 'User',
                'user_id': str(uuid.uuid4()),
                'username': 'petlover3',
                'email': 'petlover3@example.com',
                'role': 'user'
            },
            {
                'uid': f'_:user{7}',
                'dgraph.type': 'User',
                'user_id': str(uuid.uuid4()),
                'username': 'vet2',
                'email': 'vet2@example.com',
                'role': 'agent'
            },
            {
                'uid': f'_:user{8}',
                'dgraph.type': 'User',
                'user_id': str(uuid.uuid4()),
                'username': 'trainer2',
                'email': 'trainer2@example.com',
                'role': 'user'
            },
            {
                'uid': f'_:user{9}',
                'dgraph.type': 'User',
                'user_id': str(uuid.uuid4()),
                'username': 'admin2',
                'email': 'admin2@example.com',
                'role': 'agent'
            },
            {
                'uid': f'_:user{10}',
                'dgraph.type': 'User',
                'user_id': str(uuid.uuid4()),
                'username': 'petlover4',
                'email': 'petlover4@example.com',
                'role': 'user'
            }
        ]

        # Mutate the data
        response = txn.mutate(set_obj=p)

        # Commit the transaction.
        commit_response = txn.commit()
        print(f"Commit Response: {commit_response}")
        print(f"UIDs: {response.uids}")
    finally:
        # Clean up. Calling this after txn.commit() is a no-op and hence safe.
        txn.discard()
