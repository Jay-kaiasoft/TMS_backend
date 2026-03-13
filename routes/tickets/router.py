from fastapi import APIRouter, Depends, status
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from database import get_db
from core.response import APIResponse, success_response
from .service import TicketService, get_current_user_id

router = APIRouter(prefix="/tickets", tags=["Tickets"])

# -----------------
# SCHEMAS
# -----------------
class TicketCreate(BaseModel):
    project_id: int
    title: str = Field(..., min_length=1)
    description: Optional[str] = None
    due_date: datetime
    as_customer: Optional[bool] = False
    for_customer: Optional[bool] = False
    status_id: Optional[int] = None
    assignees: List[int] = Field(..., min_length=1)

class TicketUpdate(BaseModel):
    project_id: int
    title: str = Field(..., min_length=1)
    description: Optional[str] = None
    due_date: datetime
    as_customer: Optional[bool] = False
    for_customer: Optional[bool] = False
    status_id: Optional[int] = None
    assignees: List[int] = Field(..., min_length=1)

class TicketResponse(BaseModel):
    id: int
    project_id: int
    title: str
    description: Optional[str]
    due_date: Optional[datetime]
    as_customer: bool
    for_customer: bool
    created_by: Optional[int]
    created_date: datetime
    status_id: Optional[int] = None
    status_name: Optional[str] = None
    assignees: List[int] = []
    attachments: List[dict] = []

# Add this schema near the other Pydantic models
class TicketFilter(BaseModel):
    as_customer: Optional[bool] = None
    for_customer: Optional[bool] = None
    startDueDate: Optional[datetime] = None
    endDueDate: Optional[datetime] = None

# Add this route after the existing ones
@router.post("/filter", response_model=APIResponse[List[TicketResponse]])
def filter_tickets(filter: TicketFilter, db=Depends(get_db), current_user_id: int = Depends(get_current_user_id)):
    result = TicketService.get_filtered_tickets(filter, db, current_user_id)
    return success_response(result, "Filtered tickets fetched successfully")
    
@router.post("", response_model=APIResponse[TicketResponse], status_code=status.HTTP_201_CREATED)
def create_ticket(ticket: TicketCreate, db=Depends(get_db), current_user_id: int = Depends(get_current_user_id)):
    result = TicketService.create_ticket(ticket, db, current_user_id)
    return success_response(result, "Ticket created successfully", 201)

@router.get("", response_model=APIResponse[List[TicketResponse]])
def get_all_tickets(db=Depends(get_db),current_user_id: int = Depends(get_current_user_id)):
    result = TicketService.get_all_tickets(db,current_user_id)
    return success_response(result, "Tickets fetched successfully")

@router.get("/{ticket_id}", response_model=APIResponse[TicketResponse])
def get_ticket(ticket_id: int, db=Depends(get_db)):
    result = TicketService.get_ticket(ticket_id, db)
    return success_response(result, "Ticket fetched successfully")

@router.put("/{ticket_id}", response_model=APIResponse[TicketResponse])
def update_ticket(ticket_id: int, ticket_update: TicketUpdate, db=Depends(get_db), current_user_id: int = Depends(get_current_user_id)):
    result = TicketService.update_ticket(ticket_id, ticket_update, db, current_user_id)
    return success_response(result, "Ticket updated successfully")

@router.delete("/{ticket_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_ticket(ticket_id: int, db=Depends(get_db)):
    TicketService.delete_ticket(ticket_id, db)
    return success_response(None, "Ticket deleted successfully", 204)
