#!/usr/bin/env python3
from fastapi import APIRouter, Body, Request, Response, HTTPException, status
from fastapi.encoders import jsonable_encoder
from typing import List

from .modelmongo import User, Ticket, AgentAssignment, DailyReport

router = APIRouter()