from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from app.database import get_db
from app.schemas import NoteCreate, NoteUpdate, NoteResponse
from app.models import Event, EventNote, User
from app.auth import get_current_active_user, can_edit_event
from app.audit import log_action

router = APIRouter(prefix="/events/{event_id}/notes", tags=["notes"])


@router.get("", response_model=List[NoteResponse])
def list_notes(
    event_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """List notes for an event"""
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    notes = db.query(EventNote).filter(
        EventNote.event_id == event_id
    ).order_by(EventNote.created_at.desc()).all()
    
    return notes


@router.post("", response_model=NoteResponse, status_code=status.HTTP_201_CREATED)
def create_note(
    event_id: UUID,
    note_data: NoteCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create a note for an event"""
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    # Check permission
    if not can_edit_event(event, current_user):
        raise HTTPException(status_code=403, detail="Not authorized to edit this event")
    
    note = EventNote(
        event_id=event_id,
        text=note_data.text,
        created_by=current_user.id
    )
    
    db.add(note)
    db.commit()
    db.refresh(note)
    
    log_action(db, current_user.id, "CREATE", "note", str(note.id), {
        "event_id": str(event_id)
    })
    
    return note


@router.put("/{note_id}", response_model=NoteResponse)
def update_note(
    event_id: UUID,
    note_id: UUID,
    note_data: NoteUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update a note"""
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    note = db.query(EventNote).filter(
        EventNote.id == note_id,
        EventNote.event_id == event_id
    ).first()
    
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    
    # Check permission (only author or admin can edit)
    if str(note.created_by) != str(current_user.id) and not can_edit_event(event, current_user):
        raise HTTPException(status_code=403, detail="Not authorized to edit this note")
    
    note.text = note_data.text
    db.commit()
    db.refresh(note)
    
    log_action(db, current_user.id, "UPDATE", "note", str(note.id), {
        "event_id": str(event_id)
    })
    
    return note


@router.delete("/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_note(
    event_id: UUID,
    note_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Delete a note"""
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    note = db.query(EventNote).filter(
        EventNote.id == note_id,
        EventNote.event_id == event_id
    ).first()
    
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    
    # Check permission (only author or admin can delete)
    if str(note.created_by) != str(current_user.id) and not can_edit_event(event, current_user):
        raise HTTPException(status_code=403, detail="Not authorized to delete this note")
    
    log_action(db, current_user.id, "DELETE", "note", str(note.id), {
        "event_id": str(event_id)
    })
    
    db.delete(note)
    db.commit()
    
    return None
