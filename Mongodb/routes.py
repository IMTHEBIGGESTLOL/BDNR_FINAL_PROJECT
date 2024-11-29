#!/usr/bin/env python3
from fastapi import APIRouter, Body, Request, Response, HTTPException, status, Query, Body
from fastapi.encoders import jsonable_encoder
from typing import List
from pydantic import BaseModel
from pymongo import MongoClient
from pymongo import ReturnDocument
from pymongo.collection import Collection
import requests
from typing import List, Dict, Any
from datetime import datetime


from .modelmongo import User, Ticket, AgentAssignment, DailyReport, UpdateUser, UpdateTicket, UpdateResolutionSteps
from typing import Dict, Optional

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




# ROUTES FOR FILTER IN TICKETS (agents)
@router.get("/tickets/customerID/{customer_id}", response_description="Get Ticket by customer ID", response_model=List[Ticket])
async def get_tickets_custID(customer_id: str, agent_id: str, request: Request):
    agents = list(db.agent_assignments.find({"agent_id": agent_id}))
    if not agents:
        raise HTTPException(status_code=404, detail="Agent not found")

    ticket_ids = [assignment.get("ticket_id") for assignment in agents]
    if not ticket_ids:
        return {"message": "No tickets assigned to this agent"}

    tickets = list(db.tickets.find({"customer_id": customer_id, "uuid": {"$in": ticket_ids}}, {"_id": 0}))
    if not tickets:
        raise HTTPException(status_code=404, detail=f"No tickets found for Customer ID: {customer_id} assigned to Agent {agent_id}.")

    return tickets

@router.get("/tickets/status/{status}", response_description="Get a ticket by their Status", response_model=List[Ticket])
async def get_tickets_status(status: str, agent_id: str, request: Request):
    # Find agent assignments
    agents = list(db.agent_assignments.find({"agent_id": agent_id}))
    if not agents:
        raise HTTPException(status_code=404, detail="Agent not found")

    # Extract ticket IDs assigned to the agent
    ticket_ids = [assignment.get("ticket_id") for assignment in agents]
    if not ticket_ids:
        return {"message": "No tickets assigned to this agent"}

    # Find tickets by status and agent assignment
    tickets = list(db.tickets.find({"status": status, "uuid": {"$in": ticket_ids}}, {"_id": 0}))
    if not tickets:
        raise HTTPException(status_code=404, detail=f"No tickets found with status: {status} assigned to Agent {agent_id}.")

    return tickets


@router.get("/tickets/priority/{priority}", response_description="Get a ticket by their priority", response_model=List[Ticket])
async def get_tickets_priority(priority: str, agent_id: str, request: Request):
    agents = list(db.agent_assignments.find({"agent_id": agent_id}))
    if not agents:
        raise HTTPException(status_code=404, detail="Agent not found")

    ticket_ids = [assignment.get("ticket_id") for assignment in agents]
    if not ticket_ids:
        return {"message": "No tickets assigned to this agent"}

    tickets = list(db.tickets.find({"priority": priority, "uuid": {"$in": ticket_ids}}, {"_id": 0}))
    if not tickets:
        raise HTTPException(status_code=404, detail=f"No tickets found with priority: {priority} assigned to Agent {agent_id}.")

    return tickets


# ROUTES FOR FILTER IN TICKETS (admins)
@router.get("/tickets/admins/customerID/{customer_id}", response_description="Get Ticket by customer ID", response_model=List[Ticket])
async def get_tickets_custID(customer_id: str, request: Request):
    tickets = list(db.tickets.find({"customer_id": customer_id}))
    if tickets is None:
        raise HTTPException(status_code=404, detail=f"Ticket with Customer ID: {customer_id} not found.")
    
    return tickets

@router.get("/tickets/admins/status/{status}", response_description="Get a ticket by their Status", response_model=List[Ticket])
async def get_tickets_status(status: str, request: Request):
    tickets = list(db.tickets.find({"status": status}))
    if tickets is None:
        raise HTTPException(status_code=404, detail=f"Ticket with status: {status} not found.")
    
    return tickets

@router.get("/tickets/admins/priority/{priority}", response_description="Get a ticket by their priority", response_model=List[Ticket])
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


# AGGREGATIONS
@router.get("/tickets/admins/recent", response_model=List[Dict[str, Any]])
def get_recent_tickets(status, limit: int = 3):

    try:
        pipeline = [
            {"$match": {"status": status}},
            {"$sort": {"created_timestamp": 1}},
            {"$limit": limit},
            {"$project": {"_id": 0, "uuid": 1, "status": 1, "created_timestamp": 1}}
        ]
        result = list(db.tickets.aggregate(pipeline))
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching recent tickets: {str(e)}")

@router.get("/tickets/recent", response_model=List[Dict[str, Any]])
def get_recent_tickets(status, agent_id: str, limit: int = 3):

    try:
        pipeline = [
            {"$match": {"status": status}}, 
            {"$sort": {"created_timestamp": -1}},  
            {"$limit": limit},  
            {"$lookup": {  
                "from": "agent_assignments",
                "localField": "uuid",
                "foreignField": "ticket_id",
                "as": "assigned_agents"
            }},
            {"$match": {"assigned_agents.agent_id": agent_id}},
            {"$project": {"_id": 0, "uuid": 1, "status": 1, "created_timestamp": 1}}
        ]
        result = list(db.tickets.aggregate(pipeline))
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching recent tickets: {str(e)}")

@router.get("/tickets/priority_level", response_model=List[Dict[str, Any]])
def fetch_tickets_by_prioritylevels(agent_id: str, limit: int = 3):

    try:
        pipeline = [
            {"$lookup": {
                "from": "agent_assignments",
                "localField": "uuid",
                "foreignField": "ticket_id",
                "as": "assigned_agents"
            }},
            {"$match": {"assigned_agents.agent_id": agent_id}},  
            {"$addFields": {
                "priority_sort_order": {
                    "$switch": {  
                        "branches": [
                            {"case": {"$eq": ["$priority", "high"]}, "then": 1},
                            {"case": {"$eq": ["$priority", "medium"]}, "then": 2},
                            {"case": {"$eq": ["$priority", "low"]}, "then": 3}
                        ],
                        "default": 4 
                    }
                }
            }},
            {"$sort": {"priority_sort_order": 1, "created_timestamp": -1}}, 
            {"$limit": limit}, 
            {"$project": {"_id": 0, "uuid": 1, "priority": 1, "status": 1, "created_timestamp": 1}}  
        ]

        result = list(db.tickets.aggregate(pipeline))

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching recent tickets: {str(e)}")


@router.get("/tickets/admins/priority_level", response_model=List[Dict[str, Any]])
def fetch_tickets_admins_by_prioritylevels(limit: int = 6):

    try:
        pipeline = [
            {"$addFields": {
                "priority_sort_order": {
                    "$switch": { 
                        "branches": [
                            {"case": {"$eq": ["$priority", "high"]}, "then": 1},
                            {"case": {"$eq": ["$priority", "medium"]}, "then": 2},
                            {"case": {"$eq": ["$priority", "low"]}, "then": 3}
                        ],
                        "default": 4  
                    }
                }
            }},
            {"$lookup": {
                "from": "agent_assignments",  
                "localField": "uuid", 
                "foreignField": "ticket_id", 
                "as": "agent_info" 
            }},
            {"$unwind": "$agent_info"},

            {"$sort": {"priority_sort_order": 1, "created_timestamp": 1}}, 
            {"$limit": limit}, 
            {"$project": {"_id": 0, "uuid": 1, "priority": 1, "agent_id": "$agent_info.agent_id", "status": 1, "created_timestamp": 1}} 
        ]

        result = list(db.tickets.aggregate(pipeline))

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching recent tickets: {str(e)}")


# HELP TO QUERY TICKETS GIVEN TO AGENTS
@router.get("/tickets/agent/{agent_id}")
def get_tickets_by_agent(agent_id: str):
    agents = list(db.agent_assignments.find({"agent_id": agent_id}))
    if not agents:
        raise HTTPException(status_code=404, detail="Agent not found")

    ticket_ids = [assignment.get("ticket_id") for assignment in agents]
    if not ticket_ids:
        return {"message": "No tickets assigned to this agent"}

    tickets = list(db.tickets.find({"uuid": {"$in": ticket_ids}}, {"_id": 0, "uuid": 1, "status":1, "priority":1}))
    return tickets



# RETRIEVE TICKET FEEDBACK
@router.get("/tickets/{ticket_uuid}/feedback", response_model=Dict[str, Any])
async def get_ticket_feedback(ticket_uuid: str, agent_id: str = None):
    if not agent_id:
        raise HTTPException(status_code=422, detail="Agent ID is required")

    agents = list(db.agent_assignments.find({"agent_id": agent_id}))
    if not agents:
        raise HTTPException(status_code=404, detail="Agent not found")

    ticket_ids = [assignment.get("ticket_id") for assignment in agents]
    if not ticket_ids:
        return {"message": "No tickets assigned to this agent"}

    try:
        ticket = db.tickets.find_one({"uuid": ticket_uuid, "uuid": {"$in": ticket_ids}}, {"_id": 0, "feedback": 1})

        if not ticket:
            raise HTTPException(status_code=404, detail="Ticket not found")

        return ticket.get("feedback", {})

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving ticket feedback: {str(e)}")


@router.get("/tickets/admins/{ticket_uuid}/feedback", response_model=Dict[str, Any])
async def get_ticket_feedback(ticket_uuid: str):
    try:
        ticket = db.tickets.find_one({"uuid": ticket_uuid}, {"_id": 0, "feedback": 1})

        if not ticket:
            raise HTTPException(status_code=404, detail="Ticket not found")

        return ticket.get("feedback", {})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving ticket feedback: {str(e)}")



class MessageRequest(BaseModel):
    text: str

@router.post("/tickets/{ticket_uuid}/messages", response_model=Dict[str, Any])
async def add_message_to_ticket(ticket_uuid: str, customer_id: str, message: MessageRequest = Body(...)):
    try:
        ticket = db.tickets.find_one({"uuid": ticket_uuid, "customer_id": customer_id})
        
        if not ticket:
            raise HTTPException(status_code=404, detail="Ticket not found or does not belong to this customer")

        timestamp = datetime.utcnow().isoformat()

        new_message = {
            "sender_id": customer_id,
            "timestamp": timestamp,
            "message_text": message.text
        }

        db.tickets.update_one(
            {"uuid": ticket_uuid},
            {"$push": {"messages": new_message}}
        )

        return {"message": "Message added successfully", "ticket_uuid": ticket_uuid, "new_message": new_message}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error adding message to ticket: {str(e)}")

@router.get("/daily_reports/{report_date}", response_model=DailyReport)
async def get_daily_report(report_date: str):
    try:
        report = db.daily_reports.find_one({"report_date": report_date}, {"_id": 0})
        
        if not report:
            raise HTTPException(status_code=404, detail="Daily report not found for the given date")
        
        return report
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching daily report: {str(e)}")


class UpdateUserProfile(BaseModel):
    name: Optional[str] = None
    phone_number: Optional[str] = None
    preferences: Optional[Dict[str, str]] = None
    profile_picture: Optional[str] = None



# UPDATE USER PROFILE INFO
@router.put("/users/{user_id}/profile", response_model=Dict[str, str])
async def update_user_profile(user_id: str, profile_update: UpdateUserProfile):
    try:
        # Prepare the fields to update
        update_data = {f"profile.{key}": value for key, value in profile_update.dict(exclude_none=True).items()}

        if not update_data:
            raise HTTPException(status_code=400, detail="No fields provided to update")

        # Update the user's profile in the database
        result = db.users.update_one({"uuid": user_id},  {"$set": {"profile": update_data}})

        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="User not found")

        updated_user = db.users.find_one({"uuid": user_id}, {"_id": 0, "profile": 1})

        return {"message": "Profile updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating user profile: {str(e)}")

# TICKET UPDATE RESOLUTIONS STEPS
@router.put("/tickets/{ticket_uuid}/resolution_steps", response_model=Dict[str, str])
async def update_resolution_steps(
    ticket_uuid: str, 
    update_steps: UpdateResolutionSteps, 
    agent_id: str
):
    try:
        agents = list(db.agent_assignments.find({"agent_id": agent_id}))
        if not agents:
            raise HTTPException(status_code=404, detail="Agent not found")

        ticket_ids = [assignment.get("ticket_id") for assignment in agents]
        if not ticket_ids:
            return {"message": "No tickets assigned to this agent"}
        
        if ticket_uuid not in ticket_ids:
            return {"message": "Ticket not assigned to this agent"}


        result = db.tickets.update_one(
            {"uuid": ticket_uuid},
            {"$set": {"resolution_steps": update_steps.steps}}
        )

        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Ticket not found.")

        return {"message": "Resolution steps updated successfully."}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating resolution steps: {str(e)}")

@router.put("/tickets/admins/{ticket_uuid}/resolution_steps", response_model=Dict[str, str])
async def update_admins_resolution_steps(
    ticket_uuid: str, 
    update_steps: UpdateResolutionSteps, 
):
    try:
        result = db.tickets.update_one(
            {"uuid": ticket_uuid},
            {"$set": {"resolution_steps": update_steps.steps}}
        )

        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Ticket not found.")

        return {"message": "Resolution steps updated successfully."}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating resolution steps: {str(e)}")

@router.delete("/tickets/{ticket_id}", response_model=Dict[str, str])
async def delete_ticket(ticket_id: str):

    try:
        result = db.tickets.delete_one({"uuid": ticket_id})

        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Ticket not found.")

        return {"message": "Ticket deleted successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting ticket: {str(e)}")


@router.get("/tickets/customer/{customer_id}", response_model=List[Dict[str, Any]])
async def get_tickets_by_customer(customer_id: str):

    try:
        tickets = list(db.tickets.find({"customer_id": customer_id}, {"_id": 0}))

        if not tickets:
            raise HTTPException(status_code=404, detail="No tickets found for this customer.")

        return tickets
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving tickets: {str(e)}")


#Base URL
@router.get("/")
async def root():
    return {"message": "Welcome to the API! Access /users/ to manage users."}
    
@router.get("/nothing/")
async def base_result():
    return {"message": "No results for query found"}