from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID

from app.database import get_db
from app.schemas import FileUploadResponse
from app.models import Event, EventFile, User, FileKind
from app.auth import get_current_active_user, can_edit_event
from app.storage import storage_service
from app.audit import log_action

router = APIRouter(prefix="/events/{event_id}/files", tags=["files"])

ALLOWED_PHOTO_TYPES = {"image/jpeg", "image/jpg", "image/png", "image/gif", "image/webp"}
ALLOWED_DOC_TYPES = {
    "application/pdf",
    "application/msword",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/vnd.ms-excel",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "application/zip",
    "image/jpeg",
    "image/png"
}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB


@router.post("", response_model=List[FileUploadResponse], status_code=status.HTTP_201_CREATED)
async def upload_files(
    event_id: UUID,
    files: List[UploadFile] = File(...),
    kind: FileKind = Query(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Upload files (photos or documents) to an event"""
    # Check if event exists
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    # Check permission
    if not can_edit_event(event, current_user):
        raise HTTPException(status_code=403, detail="Not authorized to edit this event")
    
    uploaded_files = []
    
    for file in files:
        # Validate file type
        content_type = file.content_type
        if kind == FileKind.PHOTO and content_type not in ALLOWED_PHOTO_TYPES:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid photo type: {content_type}. Allowed: JPEG, PNG, GIF, WebP"
            )
        elif kind == FileKind.DOC and content_type not in ALLOWED_DOC_TYPES:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid document type: {content_type}"
            )
        
        # Read file content
        content = await file.read()
        
        # Validate file size
        if len(content) > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=400,
                detail=f"File too large: {file.filename}. Max size: 10MB"
            )
        
        # Upload to storage
        try:
            if kind == FileKind.PHOTO:
                url, thumbnail_url = storage_service.upload_photo_with_thumbnail(
                    content, file.filename, content_type
                )
            else:
                url = storage_service.upload_file(content, file.filename, content_type)
                thumbnail_url = None
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to upload file: {str(e)}")
        
        # Save to database
        event_file = EventFile(
            event_id=event_id,
            kind=kind,
            filename=file.filename,
            mime=content_type,
            size=len(content),
            url=url,
            thumbnail_url=thumbnail_url,
            uploaded_by=current_user.id
        )
        
        db.add(event_file)
        db.commit()
        db.refresh(event_file)
        
        uploaded_files.append(event_file)
        
        log_action(db, current_user.id, "UPLOAD", "file", str(event_file.id), {
            "event_id": str(event_id),
            "filename": file.filename,
            "kind": kind.value
        })
    
    return uploaded_files


@router.get("", response_model=List[FileUploadResponse])
def list_files(
    event_id: UUID,
    kind: Optional[FileKind] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """List files for an event"""
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    query = db.query(EventFile).filter(EventFile.event_id == event_id)
    
    if kind:
        query = query.filter(EventFile.kind == kind)
    
    files = query.order_by(EventFile.created_at.desc()).all()
    return files


@router.delete("/{file_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_file(
    event_id: UUID,
    file_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Delete a file"""
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    # Check permission
    if not can_edit_event(event, current_user):
        raise HTTPException(status_code=403, detail="Not authorized to edit this event")
    
    file = db.query(EventFile).filter(
        EventFile.id == file_id,
        EventFile.event_id == event_id
    ).first()
    
    if not file:
        raise HTTPException(status_code=404, detail="File not found")
    
    # Delete from storage
    try:
        storage_service.delete_file(file.url)
        if file.thumbnail_url:
            storage_service.delete_file(file.thumbnail_url)
    except Exception as e:
        print(f"Warning: Failed to delete file from storage: {str(e)}")
    
    log_action(db, current_user.id, "DELETE", "file", str(file.id), {
        "event_id": str(event_id),
        "filename": file.filename
    })
    
    db.delete(file)
    db.commit()
    
    return None
