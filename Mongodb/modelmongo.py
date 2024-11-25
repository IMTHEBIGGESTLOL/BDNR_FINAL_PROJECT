#!/usr/bin/env python3
import uuid
from typing import Optional
from pydantic import BaseModel, Field

class User(BaseModel):
    uuid: str = Field( alias="_uuid")
    username: str = Field(...)
    email: str = Field(...)
    password: str = Field(...)  # hashed
    role: str = Field(...)  # "customer" or "agent"
    profile: dict = Field({
        "name": None,
        "phone_number": None,
        "preferences": None,  # e.g., preferred contact channels
        "profile_picture": None  # URL to the profile image
    })

    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "_uuid": "123e4567-e89b-12d3-a456-426614174000",
                "username": "john_doe",
                "email": "john.doe@example.com",
                "password": "hashedpassword123",
                "type": "customer",
                "profile": {
                    "name": "John Doe",
                    "phone_number": "+123456789",
                    "preferences": {"contact_channel": "email"},
                    "profile_picture": "https://example.com/image.jpg"
                }
            }
        }

class Ticket(BaseModel):
    uuid: str = Field(alias="_uuid")
    customer_id: str = Field(...)  # references Users collection
    description: str = Field(...)
    status: str = Field(...)  # e.g., "open", "closed"
    priority: str = Field(...)  # e.g., "low", "medium", "high", "urgent"
    created_timestamp: str = Field(...)
    updated_timestamp: str = Field(...)
    category: str = Field(...)  # e.g., "technical", "billing"
    messages: list = Field([])  # List of messages within the ticket
    feedback: dict = Field({
        "rating": None,
        "comments": None,
        "submitted_timestamp": None
    })
    resolution_steps: list = Field([])  # list of completed steps
    channel: str = Field(...)  # e.g., "email", "phone", "chat"

    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "_uuid": "123e4567-e89b-12d3-a456-426614174001",
                "customer_id": "123e4567-e89b-12d3-a456-426614174000",
                "description": "Cannot log in to my account",
                "status": "open",
                "priority": "high",
                "created_timestamp": "2024-11-13T10:00:00Z",
                "updated_timestamp": "2024-11-13T10:15:00Z",
                "category": "technical",
                "messages": [
                    {
                        "sender_id": "123e4567-e89b-12d3-a456-426614174000",
                        "timestamp": "2024-11-13T10:05:00Z",
                        "message_text": "I need help resetting my password."
                    }
                ],
                "feedback": {
                    "rating": 5,
                    "comments": "Resolved quickly!",
                    "submitted_timestamp": "2024-11-14T12:00:00Z"
                },
                "resolution_steps": ["Reset password link sent"],
                "channel": "chat"
            }
        }

class AgentAssignment(BaseModel):
    uuid: str = Field(default_factory=uuid.uuid4, alias="_uuid")
    agent_id: str = Field(...)  # references Users collection
    ticket_id: str = Field(...)  # references Tickets collection
    assigned_timestamp: str = Field(...)
    priority_level: str = Field(...)

    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "_uuid": "123e4567-e89b-12d3-a456-426614174002",
                "agent_id": "123e4567-e89b-12d3-a456-426614174003",
                "ticket_id": "123e4567-e89b-12d3-a456-426614174001",
                "assigned_timestamp": "2024-11-13T10:00:00Z",
                "priority_level": "high"
            }
        }

class DailyReport(BaseModel):
    uuid: str = Field(default_factory=uuid.uuid4, alias="_uuid")
    report_date: str = Field(...)
    ticket_count: int = Field(...)
    channel_stats: dict = Field({
        "email": 0,
        "phone": 0,
        "chat": 0
    })

    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "_uuid": "123e4567-e89b-12d3-a456-426614174003",
                "report_date": "2024-11-13",
                "ticket_count": 100,
                "channel_stats": {
                    "email": 40,
                    "phone": 30,
                    "chat": 30
                }
            }
        }

