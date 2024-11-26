from datetime import datetime
import os
from cassandra.cluster import Cluster
from pymongo import MongoClient
import pydgraph
from fastapi import FastAPI
from contextlib import asynccontextmanager

from Cassandra import model
from DGraph import modeldgraph
from Mongodb.routes import router as db_router

# Configuración de entornos
CLUSTER_IPS = os.getenv('CASSANDRA_CLUSTER_IPS', 'localhost')
KEYSPACE = os.getenv('CASSANDRA_KEYSPACE', 'final_project')
REPLICATION_FACTOR = os.getenv('CASSANDRA_REPLICATION_FACTOR', '1')

DGRAPH_URI = os.getenv('DGRAPH_URI', 'localhost:9080')
MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017')
DB_NAME = os.getenv('MONGODB_DB_NAME', 'final_project')

dgraph_client_stub = pydgraph.DgraphClientStub(DGRAPH_URI)
dgraph_client = pydgraph.DgraphClient(dgraph_client_stub)

cassandra_cluster = Cluster(CLUSTER_IPS.split(','))
cassandra_session = cassandra_cluster.connect()
model.create_keyspace(cassandra_session, KEYSPACE, REPLICATION_FACTOR)
cassandra_session.set_keyspace(KEYSPACE)

mongodb_client = MongoClient(MONGODB_URI)
mongodb_database = mongodb_client[DB_NAME]

#Pruebas de MOngo
app = FastAPI()
app.include_router(db_router, tags=["users"], prefix="/user")


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Initializing databases...")

    # MongoDB
    mongodb_client = MongoClient(MONGODB_URI)
    mongodb_database = mongodb_client[DB_NAME]
    app.state.mongodb_client = mongodb_client
    app.state.mongodb_database = mongodb_database
    print(f"Connected to MongoDB at: {MONGODB_URI}, Database: {DB_NAME}")

    # Cassandra
    cassandra_cluster = Cluster(CLUSTER_IPS.split(','))
    cassandra_session = cassandra_cluster.connect()
    model.create_keyspace(cassandra_session, KEYSPACE, REPLICATION_FACTOR)
    cassandra_session.set_keyspace(KEYSPACE)
    model.create_schema(cassandra_session)
    app.state.cassandra_cluster = cassandra_cluster
    app.state.cassandra_session = cassandra_session
    print("Cassandra initialized.")

    # Dgraph
    dgraph_client_stub = pydgraph.DgraphClientStub(DGRAPH_URI)
    dgraph_client = pydgraph.DgraphClient(dgraph_client_stub)
    modeldgraph.set_schema(dgraph_client)
    app.state.dgraph_client_stub = dgraph_client_stub
    app.state.dgraph_client = dgraph_client
    print("Dgraph initialized.")

    # Yield control to the app
    try:
        yield
    finally:
        # Clean up resources
        print("Shutting down databases...")
        cassandra_session.shutdown()
        cassandra_cluster.shutdown()
        mongodb_client.close()
        dgraph_client_stub.close()
        print("All database connections closed.")

app = FastAPI(lifespan=lifespan)

# Rutas de FastAPI
app.include_router(db_router, tags=["project"], prefix="/project")

# Menú interactivo
def print_menu():
    menu_options = {
        # 1: "Create data",
        # 2: "Search user",
        # 3: "Delete",
        # 4: "Search Channel",
        # 5: "Advanced Queries (Pagination, Count)",
        # 6: "Drop All",
        1: "Insert Bulk Data into Databases",  # option to insert bulk data
        2: "Login",
        3: "Exit",
    }
    for key, value in menu_options.items():
        print(f"{key} -- {value}")

def print_customer_menu():
    menu_options = {
        1: "See my tickets",
        2: "Search my comments",
        3: "Log Out"
    }
    for key, value in menu_options.items():
        print(f"{key} -- {value}")

def print_admin_menu():
    menu_options = {
        1: "See all tickets in a given day",
        2: "All urgent tickets in a Date Range",
        3: "Feedback of an agent",
        4: "Daily report",
        5: "Logout"
    }
    for key, value in menu_options.items():
        print(f"{key} -- {value}")

def print_agent_menu():
    menu_options = {
        1: "See my assigned tickets",
        2: "See my feedback per ticket",
        3: "See escalation per ticket",
        4: "See activities per ticket",
        5: "Log Out"
    }
    for key, value in menu_options.items():
        print(f"{key} -- {value}")

def menu_handler():
    """
    Muestra un menú interactivo y maneja las opciones seleccionadas.
    """
    while True:
        print_menu()
        try:
            choice = int(input("Select an option: "))
        except ValueError:
            print("Invalid input. Please enter a number.")
            continue

        if choice == 2:
            print("Insert your credentials")
            user = input("Username: ")
            #get_dgraph_username
                #DGraph uses the same username
            user_data = modeldgraph.search_user(dgraph_client, user)
            if not user_data:
                print("wrong credentials \n Exiting...")
                break
            print(user_data)
            role = user_data[0]['role']
            if role == 'customer':
                customer_id = user_data[0]['customer_id']
                customer_id = int(customer_id)
                print(type(customer_id))
                print(f"Welcome {user}")
                #pint customer menu
                while True:
                    print_customer_menu()
                    choice_2 = int(input("Select an option: "))
                    if choice_2 == 1:
                        #cassandra call to tickets_by_customer
                        model.get_user_tickets(cassandra_session, customer_id)
                    if choice_2 == 2:
                        keyword = input("Keyword to search: ")
                        modeldgraph.search_messages_by_keyword(dgraph_client, keyword)
                    if choice_2 == 3:
                        print("Logging out")
                        break
            if role == 'agent':
                agent_id = user_data[0]['agent_id']
                agent_id = int(agent_id)
                print(f"Welcome agent {user}")
                while True:
                    print_agent_menu()
                    choice_2 = int(input("Select an option: "))
                    if choice_2 == 1:
                        model.get_tickets_by_agent_date(cassandra_session, agent_id)
                    elif choice_2 == 2:
                        model.get_feedback_by_agent(cassandra_session, agent_id)
                    elif choice_2 == 3:
                        print("this are your tickets: \n")
                        model.get_tickets_by_agent_date(cassandra_session, agent_id)
                        ticket_id = int(input("Insert ticket id you want to search: "))
                        model.get_escalations_by_ticket(cassandra_session, ticket_id, agent_id)
                    elif choice_2 == 3:
                        print("this are your tickets: \n")
                        model.get_tickets_by_agent_date(cassandra_session, agent_id)
                        ticket_id = int(input("Insert ticket id you want to search: "))
                        model.get_escalations_by_ticket(cassandra_session, ticket_id, agent_id)
                    elif choice_2 == 4:
                        print("this are your tickets: \n")
                        model.get_tickets_by_agent_date(cassandra_session, agent_id)
                        ticket_id = int(input("Insert ticket id you want to search: "))
                        model.get_activities_by_ticket(cassandra_session, ticket_id, agent_id)
                    elif choice_2 == 5:
                        print("Logging out...")
                        break

            if role == 'admin':
                print(f"Welcome allmighty {user}")
                while True:
                    print_admin_menu()
                    choice_2 = int(input("Select an option: "))
                    if choice_2 == 1:
                        #cassandra call to tickets_by_customer
                        date = input("Enter date to search (YYYY-MM-DD): ")
                        date_obj = datetime.strptime(date, '%Y-%m-%d').date()
                        model.get_tickets_by_date(cassandra_session, date_obj)
                    if choice_2 == 2:
                        start_date = input("Enter start date to search (YYYY-MM-DD): ")
                        start_date = datetime.strptime(start_date, '%Y-%m-%d')
                        end_date = input("Enter end date to search (YYYY-MM-DD): ")
                        end_date = datetime.strptime(end_date, '%Y-%m-%d')
                        model.get_urgent_tickets_by_time(cassandra_session, start_date, end_date)
                    if choice_2 == 3:
                        agent_id = int(input("Enter the agent id: "))
                        model.get_feedback_by_agent(cassandra_session, agent_id)
                    if choice_2 == 4:
                        channel = input("Enter the channel to filter [phone, email, chat]: ")
                        date = input("Enter date of the report: [YYYY-MM-DD]")
                        date = datetime.strptime(date, '%Y-%m-%d')
                        model.get_daily_channel_report(cassandra_session, date, channel)
                    if choice_2 == 5:
                        print("Logging out")
                        break
            #get_cassandra_username
                #Cassandra uses sequencial username id
            #Mongo_db username

        if choice == 3:  # Exit
            print("Exiting...")
            break

        if choice == 1:  # Insert bulk data
            print("Inserting bulk data into MongoDB, Cassandra, and Dgraph...")
            #insert dgraph 
            #modeldgraph.create_data(dgraph_client)
            #insert Cassandra
            model.bulk_insert(cassandra_session, dgraph_client, mongodb_client)
            print("Data inserted successfully.")
        
        if choice not in range(1, 9):
            print("Invalid option. Please try again.")

if __name__ == "__main__":
    print("Choose a mode to run:")
    print("1 -- Run FastAPI server")
    print("2 -- Run console menu")
    mode = input("Enter your choice (1/2): ").strip()

    if mode == "1":
        # Ejecutar servidor FastAPI
        import uvicorn
        uvicorn.run(app, host="127.0.0.1", port=8003)
    elif mode == "2":
        # Ejecutar menú interactivo
        menu_handler()
    else:
        print("Invalid mode selected. Exiting.")
