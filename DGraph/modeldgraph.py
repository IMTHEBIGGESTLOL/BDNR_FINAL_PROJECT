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
