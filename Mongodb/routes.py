#!/usr/bin/env python3
from fastapi import APIRouter, Body, Request, Response, HTTPException, status
from fastapi.encoders import jsonable_encoder
from typing import List
from pymongo import MongoClient
from pymongo import ReturnDocument
import requests

from .modelmongo import User, Ticket, AgentAssignment, DailyReport, UpdateUser, UpdateTicket

router = APIRouter()

# Configura la conexión a MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["final_project"]

# DATA INSERT TO UVICORN:
@router.post("/users/")
async def create_users(users: List[User]):
    # Usa model_dump en lugar de dict
    db.users.insert_many([user.model_dump(by_alias=True) for user in users])
    return {"message": "Users added successfully"}

@router.post("/tickets/")
async def create_tickets(tickets: List[Ticket]):
    db.tickets.insert_many([ticket.model_dump(by_alias=True) for ticket in tickets])
    return {"message": "Tickets added successfully"}

@router.post("/AgentAssignments/")
async def create_assignments(assignments: List[AgentAssignment]):
    db.agent_assignments.insert_many([assignment.model_dump(by_alias=True) for assignment in assignments])
    return {"message": "Agent assignments added successfully"}

@router.post("/dailyReports/")
async def create_daily_reports(reports: List[DailyReport]):
    db.daily_reports.insert_many([report.model_dump(by_alias=True) for report in reports])
    return {"message": "Daily reports added successfully"} 



# Showing all collections
@router.get("/users/", response_model=List[User])
async def get_users():
    users = list(db.users.find({}, {"_id": 0})) 
    return users

@router.get("/users", response_description="Get all users (ID and Name)")
async def get_all_users():
    users = db.users.find({}, {"uuid": 1, "username": 1})  # Project only _id and name
    user_list = [{"uuid": user["uuid"], "username": user["username"]} for user in users]
    if not user_list:
        raise HTTPException(status_code=404, detail="No users found.")
    return user_list


@router.get("/users/customers", response_description="Get all customers (ID and Name)")
async def get_all_customers():
    customers = db.users.find({"role": "customer"}, {"uuid": 1, "username": 1})  # Filter by role and project only _id and name
    customer_list = [{"uuid": customer["uuid"], "username": customer["username"]} for customer in customers]
    if not customer_list:
        raise HTTPException(status_code=404, detail="No customers found.")
    return customer_list


@router.get("/tickets/", response_model=List[Ticket])
async def get_tickets():
    tickets = list(db.tickets.find({}, {"_id": 0}))  
    return tickets

@router.get("/dailyReports/", response_model=List[DailyReport])
async def get_daily_Reports():
    daily_reports = list(db.daily_reports.find({}, {"_id": 0}))  
    return daily_reports
    
@router.get("/AgentAssignments/", response_model=List[AgentAssignment])
async def get_Agent_Assignments():
    agent_assignments = list(db.agent_assignments.find({}, {"_id": 0})) 
    return agent_assignments

# Search by Id in users
@router.get("/users/{id}", response_description="Get a user by ID", response_model=List[User])
async def get_users_id(id: str, request: Request):
    if (user := list(db.users.find({"uuid": id}))) is not None:
        return user

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with ID {id} not found")

@router.get("/users/customers/{id}", response_description="Get a customer by ID", response_model=List[User])
async def get_customer_by_id(id: str, request: Request):
    if (user := list(db.users.find({"uuid": id, "role": "customer"}))) is not None:
        return user

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with ID {id} not found")




# ROUTES FOR FILTER IN TICKETS
@router.get("/tickets/customerID/{customer_id}", response_description="Get Ticket by customer ID", response_model=List[Ticket])
async def get_tickets_custID(customer_id: str, request: Request):
    tickets = list(db.tickets.find({"customer_id": customer_id}))
    if tickets is None:
        raise HTTPException(status_code=404, detail=f"Ticket with Customer ID: {customer_id} not found.")
    
    return tickets

@router.get("/tickets/status/{status}", response_description="Get a ticket by their Status", response_model=List[Ticket])
async def get_tickets_status(status: str, request: Request):
    tickets = list(db.tickets.find({"status": status}))
    if tickets is None:
        raise HTTPException(status_code=404, detail=f"Ticket with status: {status} not found.")
    
    return tickets

@router.get("/tickets/priority/{priority}", response_description="Get a ticket by their priority", response_model=List[Ticket])
async def get_tickets_priority(priority: str, request: Request):
    tickets = list(db.tickets.find({"priority": priority}))
    if tickets is None:
        raise HTTPException(status_code=404, detail=f"Ticket with priority: {priority} not found.")
    
    return tickets
    
# GET ALL TICKETS
@router.get("/tickets/", response_model=List[Ticket])
async def get_tickets():
    tickets = list(db.tickets.find({}, {"_id": 0})) 
    if tickets is None:
        raise HTTPException(status_code=404, detail=f"No tickets")
    
    return tickets

# UPDATES

# TICKET UPDATE STATUS OR PRIORITY

@router.patch("/tickets/{ticket_id}", response_model=Ticket, response_description="Update ticket status or priority")
async def update_ticket(ticket_id: str, updates: dict):
    allowed_updates = {"status", "priority"}
    
    # Validar campos permitidos
    if not all(field in allowed_updates for field in updates.keys()):
        raise HTTPException(status_code=400, detail="Invalid fields. Only 'status' and 'priority' are allowed.")

    # Obtener estado actual del ticket
    existing_ticket = db.tickets.find_one({"uuid": ticket_id})
    if not existing_ticket:
        raise HTTPException(status_code=404, detail=f"Ticket with ID {ticket_id} not found.")
    
    # Actualizar ticket en MongoDB
    updated_ticket = db.tickets.find_one_and_update(
        {"uuid": ticket_id},
        {"$set": updates},
        return_document=ReturnDocument.AFTER
    )
    
    return updated_ticket




#Base URL
@router.get("/")
async def root():
    return {"message": "Welcome to the API! Access /users/ to manage users."}
    
@router.get("/nothing/")
async def base_result():
    return {"message": "No results for query found"}