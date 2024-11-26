#!/usr/bin/env python3
from fastapi import APIRouter, Body, Request, Response, HTTPException, status
from fastapi.encoders import jsonable_encoder
from typing import List
from pymongo import MongoClient

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
    db.tickets.insert_many([ticket.dict(by_alias=True) for ticket in tickets])
    return {"message": "Tickets added successfully"}

@router.post("/agent_assignments/")
async def create_assignments(assignments: List[AgentAssignment]):
    db.agent_assignments.insert_many([assignment.dict(by_alias=True) for assignment in assignments])
    return {"message": "Agent assignments added successfully"}

@router.post("/daily_reports/")
async def create_daily_reports(reports: List[DailyReport]):
    db.daily_reports.insert_many([report.dict(by_alias=True) for report in reports])
    return {"message": "Daily reports added successfully"} 



# Get Users By Id
@router.get("/users/{id}", response_description="Get User By Id", response_model=User)
def find_user(id: str, request: Request):
    print("hola")
    if (user := request.app.database["users"].find_one({"_uuid": id})) is not None:
        return user

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with ID: {id} not found")

@router.get("/users/", response_model=List[User])
async def get_users():
    users = list(db.users.find({}, {"_id": 0}))  # Excluir el _id si no lo quieres en la respuesta
    return users

@router.get("/")
async def root():
    return {"message": "Welcome to the API! Access /users/ to manage users."}