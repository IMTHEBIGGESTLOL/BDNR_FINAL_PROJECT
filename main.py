from contextlib import asynccontextmanager
import os

#CASSANDRA DRIVERS 
from cassandra.cluster import Cluster
from collections import defaultdict

from Cassandra import model

# Read env vars releated to Cassandra App
CLUSTER_IPS = os.getenv('CASSANDRA_CLUSTER_IPS', 'localhost')
KEYSPACE = os.getenv('CASSANDRA_KEYSPACE', 'final_project')
REPLICATION_FACTOR = os.getenv('CASSANDRA_REPLICATION_FACTOR', '1')

#DGRAPH DRIVERS AND LIBRERIES
import pydgraph

from DGraph import modeldgraph

DGRAPH_URI = os.getenv('DGRAPH_URI', 'localhost:9080')

def create_client_stub():
    return pydgraph.DgraphClientStub(DGRAPH_URI)


def create_client(client_stub):
    return pydgraph.DgraphClient(client_stub)


def close_client_stub(client_stub):
    client_stub.close()

#MONGODB DRIVERS
from fastapi import FastAPI
from pymongo import MongoClient

from Mongodb.routes import router as db_router

MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017')
DB_NAME = os.getenv('MONGODB_DB_NAME', 'final_project')

def print_menu():
    mm_options = {
        1: "Create data",
        2: "Search user",
        3: "Delete",
        4: "Search Channel",
        5: "Advanced Queries (Pagination, Count)",
        6: "Drop All",
        7: "Exit",
    }
    for key in mm_options.keys():
        print(key, '--', mm_options[key])

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Lógica de inicialización
    app.mongodb_client = MongoClient(MONGODB_URI)
    app.database = app.mongodb_client[DB_NAME]

    #Cassandra inicialization
    cluster = Cluster(CLUSTER_IPS.split(','))
    session = cluster.connect()

    model.create_keyspace(session, KEYSPACE, REPLICATION_FACTOR)
    session.set_keyspace(KEYSPACE)

    model.create_schema(session)

    #DGRAPH inicialization
     # Init Client Stub and Dgraph Client
    client_stub = create_client_stub()
    client = create_client(client_stub)

    # Create schema
    modeldgraph.set_schema(client)

    print(f"Connected to MongoDB at: {MONGODB_URI} \n\t Database: {DB_NAME}")
        
    # Esto permite que la aplicación funcione mientras se gestiona el ciclo de vida
    yield

    # Lógica de limpieza al finalizar
    app.mongodb_client.close()
    print("Bye bye...!!")

app = FastAPI(lifespan=lifespan)

app.include_router(db_router, tags=["project"], prefix="/project")

def main():

    print("hola santana")

if __name__ == '__main__':
    main()