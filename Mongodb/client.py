#!/usr/bin/env python3
import argparse
import logging
import os
import requests
from datetime import datetime
from DGraph import modeldgraph

# Set logger
log = logging.getLogger()
log.setLevel('INFO')
handler = logging.FileHandler('project.log')
handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s"))
log.addHandler(handler)

# Read env vars related to API connection
PROJECT_API_URL = os.getenv("PROJECT_API_URL", "http://localhost:8003")

def print_object(objects):
    if isinstance(objects, list):  # Handle lists of dictionaries
        for obj in objects:
            if isinstance(obj, dict):
                for k, v in obj.items():
                    print(f"{k}: {v}")
                print("=" * 50)
    elif isinstance(objects, dict):  # Handle a single dictionary
        for k, v in objects.items():
            print(f"{k}: {v}")
        print("=" * 50)
    else:
        print("Unsupported object type.")


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




def get_user():
    get_all_users()
    user_id = input("Enter the User ID to retrieve: ")
    suffix = f"/users/{user_id}"
    endpoint = PROJECT_API_URL + suffix
    response = requests.get(endpoint)

    if response.ok:
        user = response.json()
        print("User Details:")
        print_object(user)  # Pass the user dictionary directly, not as a list
    else:
        print(f"Error: {response.status_code} - {response.text}")



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





def search_ticket_by():
    suffix = '/nothing'
    print("Filter Options:")
    print("1. Customer ID")
    print("2. Status")
    print("3. Priority")
    filter_choice = input("Choose a filter Option (1-3): ")

    if filter_choice == '1':  # Ensure that the input is a string, as input() returns a string
        customer_id = input("Insert CustomerId: ")
        suffix = f"/tickets/customerID/{customer_id}"

    elif filter_choice == '2':  # Use elif to avoid checking the other conditions
        print("Status Options:")
        print("1. Open")
        print("2. Resolved")
        print("3. In Progress")
        status_choice = input("Choose a Status(1-3): ")
        status_map = {'1': 'open', '2': 'resolved', '3': 'in_progress'}
        status = status_map.get(status_choice, None)
        suffix = f"/tickets/status/{status}"

    elif filter_choice == '3':  # Use elif for the last option
        print("Priority Options:")
        print("1. High")
        print("2. Medium")
        print("3. Low")
        priority_choice = input("Choose a Priority(1-3): ")
        priority_map = {'1': 'high', '2': 'medium', '3': 'low'}
        priority = priority_map.get(priority_choice, None)
        suffix = f"/tickets/priority/{priority}"

    # Send request based on the selected filter
    endpoint = PROJECT_API_URL + suffix
    response = requests.get(endpoint)
    print("\nTickets:\n")
    if response.ok:
        json_resp = response.json()
        if isinstance(json_resp, list):  # Handle list response
            if json_resp:  # Ensure the list is not empty
                for ticket in json_resp:
                    print_object(ticket)
            else:
                print("No ticket found with the provided filter.")
        else:
            print_object(json_resp)  # If the API unexpectedly returns a single dict
    else:
        print(f"Error: {response.status_code} - {response.text}")


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

    if not update_data:  # Ensure at least one field is being updated
        print("No valid updates provided. Exiting.")
        return

    endpoint = f"{PROJECT_API_URL}/tickets/{ticket_id}"
    response = requests.patch(endpoint, json=update_data)
    if response.ok:
        print("Ticket updated successfully:")
        # Llamar a funciones para actualizar Cassandra y Dgraph
        update_ticket_in_cassandra(session, ticket_id, update_data, agent_id)
        update_ticket_in_dgraph(dgraph_client, ticket_id, update_data)
        print_object(response.json())
    else:
        print(f"Error: {response.status_code} - {response.text}")

from cassandra.query import SimpleStatement

from cassandra.query import SimpleStatement
from datetime import datetime

def update_ticket_in_cassandra(session, ticket_id, updates, agent_id):
    # Obtener las claves necesarias para cada tabla
    ticket_id = int(ticket_id)  # Convertir ticket_id a entero

    def fetch_ticket_row(table_name, ticket_id, additional_conditions=None):
        base_query = f"SELECT * FROM {table_name} WHERE ticket_id = %s"
        query_params = [ticket_id]

        if additional_conditions:
            for field, value in additional_conditions.items():
                base_query += f" AND {field} = %s"
                query_params.append(value)

        base_query += " ALLOW FILTERING"

        result = session.execute(base_query, query_params)
        row = result.one()
        if row:
            return dict(row._asdict())  # Convierte Row en diccionario
        else:
            return None


    # Configuración de las tablas y condiciones adicionales necesarias
    tables_to_update = {
        "ticket_by_date": {},
        "tickets_by_agent_date": {"agent_id": agent_id},
        "tickets_by_customer": {},
        "urgent_tickets_by_time": {"agent_id": agent_id}
    }

    # Obtener los datos actuales de cada tabla
    table_data = {}
    for table, conditions in tables_to_update.items():
        row = fetch_ticket_row(table, ticket_id, conditions)
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
            WHERE customer_id = {table_data['tickets_by_customer']['customer_id']} AND ticket_id = {ticket_id}
        """))

    if new_priority:
        update_queries.append(SimpleStatement(f"""
            UPDATE tickets_by_agent_date 
            SET priority = '{new_priority}' 
            WHERE agent_id = {agent_id} AND ticket_id = {ticket_id} AND assigned_date = '{table_data['tickets_by_agent_date']['assigned_date']}'        
        """))
        session.execute("""
            DELETE FROM urgent_tickets_by_time 
            WHERE priority = %s AND created_timestamp = %s AND ticket_id = %s
        """, ( table_data['urgent_tickets_by_time']['priority'], table_data['urgent_tickets_by_time']['created_timestamp'], ticket_id))
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
        session.execute(activity_query, (ticket_id, datetime.now(), f"{field}_updated", new_value, agent_id))


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