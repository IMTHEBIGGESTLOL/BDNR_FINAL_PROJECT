#!/usr/bin/env python3
import argparse
import logging
import os
import requests
from datetime import datetime
#from DGraph import modeldgraph

# Set logger
log = logging.getLogger()
log.setLevel('INFO')
handler = logging.FileHandler('project.log')
handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s"))
log.addHandler(handler)

# Read env vars related to API connection
PROJECT_API_URL = os.getenv("PROJECT_API_URL", "http://localhost:8003")

# FUNCTION TO PRINT ALL THE COLLECTIONS
def print_object(objects):
    if isinstance(objects, list):  
        for obj in objects:
            if isinstance(obj, dict):
                for k, v in obj.items():
                    print(f"{k}: {v}")
                print("=" * 50)
    elif isinstance(objects, dict):  
        for k, v in objects.items():
            print(f"{k}: {v}")
        print("=" * 50)
    else:
        print("Unsupported object type.")

# FUNCTION TO GET ALL USERS FOR OTHER FUNCTIONS
def get_all_users():
    endpoint = f"{PROJECT_API_URL}/users"
    response = requests.get(endpoint)

    if response.ok:
        users = response.json()
        print("All Users (ID and Name):")
        for user in users:
            print(f"UUID: {user['uuid']}, Username: {user['username']}")
    else:
        print(f"Error: {response.status_code} - {response.text}")

# FUNCTION TO GET ALL CUSTOMERS FOR AGENTS
def get_all_customers():
    endpoint = f"{PROJECT_API_URL}/users/customers"
    response = requests.get(endpoint)

    if response.ok:
        customers = response.json()
        print("All Customers (ID and Name):")
        for customer in customers:
            print(f"UUID: {customer['uuid']}, Username: {customer['username']}")
    else:
        print(f"Error: {response.status_code} - {response.text}")

# GETTING ALL USERS
def get_user():
    get_all_users()
    user_id = input("Enter the User ID to retrieve: ")
    suffix = f"/users/{user_id}"
    endpoint = PROJECT_API_URL + suffix
    response = requests.get(endpoint)

    if response.ok:
        user = response.json()
        print("User Details:")
        print_object(user)
    else:
        print(f"Error: {response.status_code} - {response.text}")


# GETTING ALL CUSTOMERS
def get_customer():
    get_all_customers()
    customer_id = input("Enter the Customer ID to retrieve: ")
    suffix = f"/users/customers/{customer_id}"
    endpoint = PROJECT_API_URL + suffix
    response = requests.get(endpoint)

    if response.ok:
        customer = response.json()
        print("Customer Details:")
        print_object(customer)
    else:
        print(f"Error: {response.status_code} - {response.text}")


# FUNCTIONS TO SEARCH ALL TICKETS BY MULTIPLE FILTERS
def search_ticket_by(agent_id):
    # If no agent_id is provided, we prompt for it (assuming agent_id is required)
    if agent_id is None:
        agent_id = input("Enter your Agent ID: ")

    # Call the function to get the tickets assigned to the agent
    get_tickets_by_agent(agent_id)  # Show the tickets assigned to this agent

    print("Filter Options:")
    print("1. Customer ID")
    print("2. Status")
    print("3. Priority")
    filter_choice = input("Choose a filter Option (1-3): ")

    if filter_choice == '1':  
        customer_id = input("Insert CustomerId: ")
        suffix = f"/tickets/customerID/{customer_id}"

    elif filter_choice == '2': 
        print("Status Options:")
        print("1. Open")
        print("2. Resolved")
        print("3. In Progress")
        status_choice = input("Choose a Status(1-3): ")
        status_map = {'1': 'open', '2': 'resolved', '3': 'in_progress'}
        status = status_map.get(status_choice, None)
        suffix = f"/tickets/status/{status}"

    elif filter_choice == '3':  
        print("Priority Options:")
        print("1. High")
        print("2. Medium")
        print("3. Low")
        priority_choice = input("Choose a Priority(1-3): ")
        priority_map = {'1': 'high', '2': 'medium', '3': 'low'}
        priority = priority_map.get(priority_choice, None)
        suffix = f"/tickets/priority/{priority}"

    # Append the agent's ticket filter
    suffix += f"?agent_id={agent_id}"

    # Send the request to the API endpoint
    endpoint = PROJECT_API_URL + suffix
    response = requests.get(endpoint)

    print("\nTickets:\n")
    if response.ok:
        json_resp = response.json()
        if isinstance(json_resp, list):  
            if json_resp:  
                for ticket in json_resp:
                    print_object(ticket)
            else:
                print("No ticket found with the provided filter.")
        else:
            print_object(json_resp)  
    else:
        print(f"Error: {response.status_code} - {response.text}")


def search_ticket_admin_by():
    suffix = '/nothing'
    print("Filter Options:")
    print("1. Customer ID")
    print("2. Status")
    print("3. Priority")
    filter_choice = input("Choose a filter Option (1-3): ")

    if filter_choice == '1':  
        customer_id = input("Insert CustomerId: ")
        suffix = f"/tickets/admins/customerID/{customer_id}"

    elif filter_choice == '2': 
        print("Status Options:")
        print("1. Open")
        print("2. Resolved")
        print("3. In Progress")
        status_choice = input("Choose a Status(1-3): ")
        status_map = {'1': 'open', '2': 'resolved', '3': 'in_progress'}
        status = status_map.get(status_choice, None)
        suffix = f"/tickets/admins/status/{status}"

    elif filter_choice == '3':  
        print("Priority Options:")
        print("1. High")
        print("2. Medium")
        print("3. Low")
        priority_choice = input("Choose a Priority(1-3): ")
        priority_map = {'1': 'high', '2': 'medium', '3': 'low'}
        priority = priority_map.get(priority_choice, None)
        suffix = f"/tickets/admins/priority/{priority}"

    endpoint = PROJECT_API_URL + suffix
    response = requests.get(endpoint)
    print("\nTickets:\n")
    if response.ok:
        json_resp = response.json()
        if isinstance(json_resp, list):  
            if json_resp:  
                for ticket in json_resp:
                    print_object(ticket)
            else:
                print("No ticket found with the provided filter.")
        else:
            print_object(json_resp)  
    else:
        print(f"Error: {response.status_code} - {response.text}")



# FUNCTION FOR OTHER FUNCTIONS TO QUERY BY AGENTS TICKETS:
def get_tickets_by_agent(agent_id):
    suffix = f"/tickets/agent/{agent_id}"
    endpoint = PROJECT_API_URL + suffix
    response = requests.get(endpoint)
    if response.ok:
        tickets = response.json()
        if tickets:
            print(f"Tickets assigned to Agent {agent_id}:")
            for ticket in tickets:
                print(f"- Ticket ID: {ticket.get('uuid')}, Details: {ticket}")
        else:
            print(f"No tickets found for Agent {agent_id}.")
    else:
        print(f"Error: {response.status_code} - {response.text}")

# FUNCTION TO UPDATE A TICKET ACROSS ALL DBS
def update_ticket(session, dgraph_client, agent_id):
    ticket_id = input("Enter the Ticket ID to update: ")
    update_data = {}

    print("Update Options:")
    print("1. Status")
    print("2. Priority")
    print("3. Both Status and Priority")
    choice = input("Choose what to update (1-3): ")

    if choice == '1' or choice == '3':
        print("Status Options:")
        print("1. Open")
        print("2. Resolved")
        print("3. In Progress")
        status_choice = input("Choose a Status(1-3): ")
        status_map = {'1': 'open', '2': 'resolved', '3': 'in_progress'}
        update_data["status"] = status_map.get(status_choice, None)

    if choice == '2' or choice == '3':
        print("Priority Options:")
        print("1. High")
        print("2. Medium")
        print("3. Low")
        priority_choice = input("Choose a Priority(1-3): ")
        priority_map = {'1': 'high', '2': 'medium', '3': 'low'}
        update_data["priority"] = priority_map.get(priority_choice, None)

    if not update_data:  
        print("No valid updates provided. Exiting.")
        return

    endpoint = f"{PROJECT_API_URL}/tickets/{ticket_id}"
    response = requests.patch(endpoint, json=update_data)
    if response.ok:
        print("Ticket updated successfully:")
        # Llamar a funciones para actualizar Cassandra y Dgraph
        update_ticket_in_cassandra( dgraph_client ,session, ticket_id, update_data, agent_id)
        update_ticket_in_dgraph(dgraph_client, ticket_id, update_data)
        print_object(response.json())
    else:
        print(f"Error: {response.status_code} - {response.text}")

from cassandra.query import SimpleStatement
from cassandra.query import SimpleStatement
from datetime import datetime

def update_ticket_in_cassandra( dgraph_client,session, ticket_id, updates, agent_id):
    # Obtener las claves necesarias para cada tabla
    ticket_data = modeldgraph.search_ticket(dgraph_client, ticket_id)
    ticket_id = int(ticket_id)  # Convertir ticket_id a entero

    def fetch_ticket_row(table_name, conditions):
        # Construir la consulta dependiendo de las claves primarias
        base_query = f"SELECT * FROM {table_name} WHERE "
        query_params = []

        # Añadir las condiciones para la consulta basadas en las claves primarias y de agrupamiento
        for field, value in conditions.items():
            # Si el campo contiene "date", se usa un rango
            if "assigned_date" in field:
                base_query += f"{field} > %s AND "
            elif isinstance(value, datetime) and "timestamp" in field:  # Si es un campo timestamp
                base_query += f"{field} > %s AND "
            else:
                base_query += f"{field} = %s AND "
            query_params.append(value)
        base_query = base_query.rstrip(" AND ")  # Eliminar el último "AND" extra
        #input(f"{base_query}")
        result = session.execute(base_query, query_params)
        #input(f"{base_query}")
        row = result.one()
        if row:
            return dict(row._asdict())  # Convierte Row en diccionario
        else:
            return None

    # Fecha límite para la comparación de timestamp (por ejemplo, todas las fechas mayores a 2000-01-01)
    some_timestamp = datetime.now()  # Fecha y hora actual
    some_date = some_timestamp.date()  # Solo la fecha
    timestamp_limit = datetime(2000, 1, 1)  # Fecha límite para comparación de timestamp
    date_limit = datetime(2000, 1, 1).date() 
    #input(f"ticket: {ticket_id}, agent: {agent_id}, datelimit: {date_limit}, timestamp: {timestamp_limit}")

    customer_id_value = ticket_data[0]['created_by']['customer_id']
    #input(customer_id_value) 
    priority = ticket_data[0]['priority']
    customer_id_value = int(customer_id_value)

    # Configuración de las tablas y condiciones necesarias
    tables_to_update = {
        "ticket_by_date": {"ticket_id": ticket_id, "created_date": some_date, "created_timestamp": timestamp_limit},  # Para buscar fechas mayores a 2000-01-01
        "tickets_by_agent_date": {"agent_id": agent_id, "ticket_id": ticket_id, "assigned_date": date_limit},
        "tickets_by_customer": {"ticket_id": ticket_id, "customer_id": customer_id_value},
        "urgent_tickets_by_time": { "priority": priority, "agent_id": agent_id, "ticket_id": ticket_id, "created_timestamp": some_date}
    }

    # Obtener los datos actuales de cada tabla
    table_data = {}
    for table, conditions in tables_to_update.items():
        row = fetch_ticket_row(table, conditions)
        if row:
            table_data[table] = row
        else:
            print(f"Ticket {ticket_id} not found in table {table}")
            return  # Manejar el caso de no encontrar el ticket

    # Extraer el nuevo estado o prioridad, si están en la actualización
    new_status = updates.get("status")
    new_priority = updates.get("priority")

    # Generar sentencias de actualización para cada tabla relevante
    update_queries = []

    if new_status:
        update_queries.append(SimpleStatement(f"""
            UPDATE ticket_by_date SET status = '{new_status}' 
            WHERE ticket_id = {ticket_id} AND created_date = '{table_data['ticket_by_date']['created_date']}' AND created_timestamp = '{table_data['ticket_by_date']['created_timestamp']}'
        """))
        update_queries.append(SimpleStatement(f"""
            UPDATE tickets_by_agent_date 
            SET status = '{new_status}' 
            WHERE agent_id = {agent_id} AND ticket_id = {ticket_id} AND assigned_date = '{table_data['tickets_by_agent_date']['assigned_date']}'
        """))
        update_queries.append(SimpleStatement(f"""
            UPDATE tickets_by_customer 
            SET status = '{new_status}' 
            WHERE customer_id = {table_data['tickets_by_customer']['customer_id']} AND created_timestamp = '{table_data['tickets_by_customer']['created_timestamp']}'  AND ticket_id = {ticket_id}
        """))

    if new_priority:
        update_queries.append(SimpleStatement(f"""
            UPDATE tickets_by_agent_date 
            SET priority = '{new_priority}' 
            WHERE agent_id = {agent_id} AND ticket_id = {ticket_id} AND assigned_date = '{table_data['tickets_by_agent_date']['assigned_date']}'        
        """))
        session.execute("""
            DELETE FROM urgent_tickets_by_time 
            WHERE priority = %s AND agent_id = %s AND ticket_id = %s AND created_timestamp = %s
        """, (table_data['urgent_tickets_by_time']['priority'], agent_id, ticket_id, table_data['urgent_tickets_by_time']['created_timestamp']))
        update_queries.append(SimpleStatement(f"""
            INSERT INTO urgent_tickets_by_time (ticket_id, agent_id, created_timestamp, priority)
            VALUES ({ticket_id}, {agent_id}, '{table_data['urgent_tickets_by_time']['created_timestamp']}', '{new_priority}')
        """))
        update_queries.append(SimpleStatement(f"""
            UPDATE tickets_by_customer 
            SET priority = '{new_priority}' 
            WHERE customer_id = {table_data['tickets_by_customer']['customer_id']} AND created_timestamp = '{table_data['tickets_by_customer']['created_timestamp']}'  AND ticket_id = {ticket_id}
        """))

    # Ejecutar todas las actualizaciones
    for query in update_queries:
        session.execute(query)

    # Registrar la actividad en Cassandra
    activity_query = """
        INSERT INTO activity_by_ticket (ticket_id, activity_timestamp, activity_type, status, agent_id)
        VALUES (%s, %s, %s, %s, %s)
    """
    for field, new_value in updates.items():
        session.execute(activity_query, (ticket_id, datetime.now(), f"updated", new_value, agent_id))


def update_ticket_in_dgraph(dgraph_client, ticket_id, update_data):

    # Crear un objeto de cliente de Dgraph
    client = dgraph_client
    txn = client.txn()
    ticket_data = modeldgraph.search_ticket(dgraph_client, ticket_id)
    # Crear la mutación para actualizar los campos del ticket
    mutation = {
        'set': { }
    }

    # Agregar los datos a actualizar
    mutation['set']['uid'] = ticket_data[0]['uid']
    if 'status' in update_data:
        mutation['set']['status'] = update_data['status']
    if 'priority' in update_data:
        mutation['set']['priority'] = update_data['priority']

    # Especificamos el `ticket_id` en la mutación para asegurar que se actualiza el ticket correcto
    mutation['set']['ticket_id'] = ticket_id

    # Realizar la mutación para actualizar los datos en Dgraph
    try:
        # Realizar la mutación en Dgraph
        txn.mutate(set_obj=mutation)
        txn.commit()
        print(f"Ticket {ticket_id} actualizado en Dgraph.")
    except Exception as e:
        print(f"Error al actualizar el ticket en Dgraph: {e}")


# FUNCTIONS FOR AGGREGATIONS
def fetch_recent_admin_tickets():
    url = f"{PROJECT_API_URL}/tickets/admins/recent"
    print("Status Options:")
    print("1. Open")
    print("2. Resolved")
    print("3. In Progress")
    status_choice = input("Choose a Status(1-3): ")
    status_map = {'1': 'open', '2': 'resolved', '3': 'in_progress'}
    status = status_map.get(status_choice)

    if status is None:
        print("Invalid status choice")
        return

    params = {"status": status}  # Send the status as a query parameter
    response = requests.get(url, params=params)

    if response.status_code == 200:
        tickets = response.json()
        for ticket in tickets:
            print(ticket)
            print("=" * 50)

    else:
        print(f"Error fetching recent tickets: {response.status_code} - {response.text}")


def fetch_recent_tickets(agent_id):
    url = f"{PROJECT_API_URL}/tickets/recent"
    print("Status Options:")
    print("1. Open")
    print("2. Resolved")
    print("3. In Progress")
    status_choice = input("Choose a Status(1-3): ")
    status_map = {'1': 'open', '2': 'resolved', '3': 'in_progress'}
    status = status_map.get(status_choice)

    if status is None:
        print("Invalid status choice")
        return

    params = {"status": status, "agent_id": agent_id}  # Send the status as a query parameter
    response = requests.get(url, params=params)

    if response.status_code == 200:
        tickets = response.json()
        for ticket in tickets:
            print(ticket)
            print("=" * 50)

    else:
        print(f"Error fetching recent tickets: {response.status_code} - {response.text}")



def fetch_tickets_by_prioritylevels(agent_id):
    url = f"{PROJECT_API_URL}/tickets/priority_level"


    params = {"agent_id": agent_id}  # Send the status as a query parameter
    response = requests.get(url, params=params)

    if response.status_code == 200:
        tickets = response.json()
        for ticket in tickets:
            print(ticket)
            print("=" * 50)

    else:
        print(f"Error fetching recent tickets: {response.status_code} - {response.text}")



def fetch_tickets_admin_by_prioritylevels():
    url = f"{PROJECT_API_URL}/tickets/admins/priority_level"
    response = requests.get(url)

    if response.status_code == 200:
        tickets = response.json()
        for ticket in tickets:
            print(ticket)
            print("=" * 50)
    else:
        print(f"Error fetching recent tickets: {response.status_code} - {response.text}")


def get_ticket_feedback(agent_id):
    get_tickets_by_agent(agent_id)  
    try:
        ticket_uuid = input("Enter Desired Ticket ID: ")
        url = f"{PROJECT_API_URL}/tickets/{ticket_uuid}/feedback?agent_id={agent_id}"  
        
        response = requests.get(url)

        if response.status_code == 200:
            feedback = response.json()
            print("Ticket Feedback:")
            print(f"Rating: {feedback.get('rating')}")
            print(f"Comments: {feedback.get('comments')}")
            print(f"Submitted Timestamp: {feedback.get('submitted_timestamp')}")
            print("=" * 50)

        else:
            print(f"Error: {response.status_code} - {response.text}")
    
    except Exception as e:
        print(f"An error occurred: {e}")

def get_ticket_admin_feedback():
    try:
        ticket_uuid = input("Enter desired Ticket ID: ")
        url = f"{PROJECT_API_URL}/tickets/admins/{ticket_uuid}/feedback"  
        
        response = requests.get(url)

        if response.status_code == 200:
            feedback = response.json()
            print("Ticket Feedback:")
            print(f"Rating: {feedback.get('rating')}")
            print(f"Comments: {feedback.get('comments')}")
            print(f"Submitted Timestamp: {feedback.get('submitted_timestamp')}")
            print("=" * 50)

        else:
            print(f"Error: {response.status_code} - {response.text}")
    
    except Exception as e:
        print(f"An error occurred: {e}")
    
def add_message_to_ticket(customer_id):
    ticket_uuid = input("Please enter the Ticket ID you want to add your message to: ")
    message_text = input("Enter your message: ")

    # Define the URL for adding a message to the ticket
    url = f"{PROJECT_API_URL}/tickets/{ticket_uuid}/messages?customer_id={customer_id}"

    # Prepare the payload with the message text
    payload = {"text": message_text}

    try:
        # Send the POST request to the FastAPI route
        response = requests.post(url, json=payload)

        # Check if the request was successful
        if response.status_code == 200:
            # Print the response message
            result = response.json()
            print(result["message"])
            print(f"New message added: {result['new_message']}")
        else:
            print(f"Error: {response.status_code} - {response.text}")
    
    except Exception as e:
        print(f"An error occurred: {e}")



def fetch_daily_report(report_date):
    url = f"{PROJECT_API_URL}/daily_reports/{report_date}"

    try:
        response = requests.get(url)

        if response.status_code == 200:
            report = response.json()

            print(f"Daily Report for {report_date}")
            print(f"UUID: {report['uuid']}")
            print(f"Ticket Count: {report['ticket_count']}")
            print("Channel Stats:")
            for channel, count in report["channel_stats"].items():
                print(f"  {channel.capitalize()}: {count}")
        else:
            print(f"Error: {response.status_code} - {response.text}")
    
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    fetch_daily_report()