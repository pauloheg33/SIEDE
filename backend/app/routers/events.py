from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
from datetime import datetime

from app.database import get_db
from app.schemas import EventCreate, EventUpdate, EventResponse, EventListResponse
from app.models import Event, User, EventType, EventStatus
from app.auth import get_current_active_user, can_edit_event, can_delete_event
from app.audit import log_action

router = APIRouter(prefix="/events", tags=["events"])


@router.get("", response_model=List[EventListResponse])
def list_events(
    type: Optional[EventType] = None,
    status: Optional[EventStatus] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """List events with filters"""
    query = db.query(Event)
    
    if type:
        query = query.filter(Event.type == type)
    if status:
        query = query.filter(Event.status == status)
    if start_date:
        query = query.filter(Event.start_at >= start_date)
    if end_date:
        query = query.filter(Event.start_at <= end_date)
    if search:
        query = query.filter(Event.title.ilike(f"%{search}%"))
    
    events = query.order_by(Event.start_at.desc()).all()
    return events


@router.post("", response_model=EventResponse, status_code=status.HTTP_201_CREATED)
def create_event(
    event_data: EventCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create a new event"""
    event = Event(
        **event_data.model_dump(),
        created_by=current_user.id
    )
    
    db.add(event)
    db.commit()
    db.refresh(event)
    
    log_action(db, current_user.id, "CREATE", "event", str(event.id), {
        "title": event.title,
        "type": event.type.value
    })
    
    return event


@router.get("/{event_id}", response_model=EventResponse)
def get_event(
    event_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get event details"""
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    return event


@router.put("/{event_id}", response_model=EventResponse)
def update_event(
    event_id: UUID,
    event_data: EventUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update an event"""
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    # Check permission
    if not can_edit_event(event, current_user):
        raise HTTPException(status_code=403, detail="Not authorized to edit this event")
    
    update_data = event_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(event, field, value)
    
    db.commit()
    db.refresh(event)
    
    log_action(db, current_user.id, "UPDATE", "event", str(event.id), update_data)
    
    return event


@router.delete("/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_event(
    event_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Delete an event (admin only)"""
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    # Check permission
    if not can_delete_event(event, current_user):
        raise HTTPException(status_code=403, detail="Only admins can delete events")
    
    log_action(db, current_user.id, "DELETE", "event", str(event.id), {
        "title": event.title
    })
    
    db.delete(event)
    db.commit()
    
    return None
