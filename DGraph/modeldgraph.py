from datetime import datetime
import json
import uuid
import pandas as pd
from tabulate import tabulate

import pydgraph
i = 10
def set_schema(client):
    schema = """
    type User {
        username
        email
        role
        assigned_tickets
        created_tickets
        customer_id
        agent_id
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
        belongs_to
    }

    username: string @index(exact) .
    email: string @index(exact) .
    role: string @index(exact) .
    
    ticket_id: string @index(exact) .
    status: string @index(term) .
    priority: string @index(term) .
    created_at: datetime @index(hour) .
    updated_at: datetime @index(hour) .
    customer_id: string @index(exact) .
    agent_id: string @index(exact) .
    
    message_id: string @index(exact) .
    sender: uid .
    belongs_to: uid .
    message_text: string @index(fulltext) .
    timestamp: datetime @index(hour) .
    
    assigned_to: uid @reverse .
    messages: [uid] @reverse .
    created_by: uid @reverse .
    assigned_tickets: [uid] .
    created_tickets: [uid] .
    """
    return client.alter(pydgraph.Operation(schema=schema))

import uuid
from datetime import datetime

import uuid
from datetime import datetime

def create_data(client, ticket_data, agent_ids, customer_ids):
    txn = client.txn()
    try:
        # Dgraph user data
        data = [
            {'uid': f'_:agent1', 'dgraph.type': 'User', 'username': 'agent1', 'role': 'agent', 'agent_id': agent_ids[0]},
            {'uid': f'_:agent2', 'dgraph.type': 'User', 'username': 'agent2', 'role': 'agent', 'agent_id': agent_ids[1]},
            {'uid': f'_:customer1', 'dgraph.type': 'User', 'username': 'petlover1', 'role': 'customer', 'customer_id': customer_ids[0]},
            {'uid': f'_:customer2', 'dgraph.type': 'User', 'username': 'petlover2', 'role': 'customer', 'customer_id': customer_ids[1]},
            {'uid': f'_:admin1', 'dgraph.type': 'User', 'username': 'admin1', 'role': 'admin', 'admin_id': 1},
            
        ] + ticket_data

        # Mutate and commit
        txn.mutate(set_obj=data)
        txn.commit()
        print("Dgraph data insertion complete!")
    finally:
        txn.discard()

def create_message(client, message_data, customer_id, ticket_id):
    txn = client.txn()
    ticket_data = search_ticket(client, ticket_id)
    try:
        # Create the message
        message_data = {
            'uid': '_:new_message',
            'dgraph.type': 'Message',
            'sender': {'uid': f'_:customer{customer_id}'},
            'message_text': message_data,
            'timestamp': datetime.now().isoformat(),
            'belongs_to': {'uid': ticket_data[0]['uid']}
        }

        # new mutation
        ticket_update = {
            
        }

        #Add to the mutation the update statements for the ticket
        ticket_update['uid'] = ticket_data[0]['uid']
        ticket_update['messages'] =  {'uid': '_:new_message'}
        # Execute the mutations
        txn.mutate(set_obj=[message_data, ticket_update], commit_now=True)
        print("Message created and added to the ticket")

    finally:
        txn.discard()

def search_user(client, username): 
    query = """query search_person($a: string) {
        all(func: eq(username, $a)) {
            username
            email
            role
            customer_id
            agent_id
        }
    }"""

    variables = {'$a': username}
    res = client.txn(read_only=True).query(query, variables=variables)
    ppl = json.loads(res.json)

    # return results.
    return ppl['all']

def search_ticket(client, ticket_id): 
    query = """query search_person($a: string) {
        all(func: eq(ticket_id, $a)) {
            uid
            priority
            created_by{
                customer_id
            }
        }
    }"""

    variables = {'$a': ticket_id}
    res = client.txn(read_only=True).query(query, variables=variables)
    ppl = json.loads(res.json)

    # return results.
    return ppl['all']

def search_messages_by_keyword(client, keyword):
    query = """
    query search_messages($a: string) {
        all_messages(func: anyoftext(message_text, $a)) {
            message_text
            timestamp
            belongs_to {
                ticket_id
                status
            }
        }
    }"""
    variables = {'$a': keyword}
    res = client.txn(read_only=True).query(query, variables=variables)
    messages = json.loads(res.json)

    # Print results
    table_data = []
    for message in messages["all_messages"]:
        row = {
            "message_text": message["message_text"],
            "ticket_id": message["belongs_to"]["ticket_id"],
            "status": message["belongs_to"]["status"]
        }
        table_data.append(row)

    # Create a pandas DataFrame
    df = pd.DataFrame(table_data)

    # Use tabulate to add a border around the table
    table = tabulate(df, headers="keys", tablefmt="grid", showindex=False)

    # Display the table with borders
    print(table)
