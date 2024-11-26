#!/usr/bin/env python3
from fastapi import APIRouter, Body, Request, Response, HTTPException, status
from fastapi.encoders import jsonable_encoder
from typing import List

from .modelmongo import User, Ticket, AgentAssignment, DailyReport, UpdateUser, UpdateTicket

router = APIRouter()

# DATA INSERT TO UVICORN:
@router.post("/userss/")
async def create_users(users: List[User]):
    db.users.insert_many([user.dict(by_alias=True) for user in users])
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

@router.get("/users/")
def get_users():
    users = list(db.users.find({}))
    for user in users:
        user["_id"] = str(user["_id"])  # Convertir ObjectId a string
    return users