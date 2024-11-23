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

        if choice == 3:  # Exit
            print("Exiting...")
            break

        if choice == 1:  # Insert bulk data
            print("Inserting bulk data into MongoDB, Cassandra, and Dgraph...")
            #insert dgraph 
            modeldgraph.create_data(dgraph_client)
            #insert Cassandra
            model.bulk_insert(cassandra_session)
            print("Data inserted successfully.")
        
        if choice not in range(1, 9):
            print("Invalid option. Please try again.")
        else:
            print(f"Option {choice} selected.")
            # Aquí se puede implementar lógica específica para cada opción

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
