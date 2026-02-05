from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime
from uuid import UUID
from app.models import UserRole, EventType, EventStatus, FileKind


# User Schemas
class UserCreate(BaseModel):
    name: str = Field(..., min_length=3, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=8)


class UserUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=3, max_length=100)
    email: Optional[EmailStr] = None
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None


class UserResponse(BaseModel):
    id: UUID
    name: str
    email: str
    role: UserRole
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


# Auth Schemas
class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshRequest(BaseModel):
    refresh_token: str


# Event Schemas
class EventCreate(BaseModel):
    title: str = Field(..., min_length=3, max_length=200)
    type: EventType
    status: EventStatus = EventStatus.PLANEJADO
    start_at: datetime
    end_at: Optional[datetime] = None
    location: Optional[str] = None
    audience: Optional[str] = None
    description: Optional[str] = None
    tags: List[str] = []
    schools: List[str] = []


class EventUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=3, max_length=200)
    type: Optional[EventType] = None
    status: Optional[EventStatus] = None
    start_at: Optional[datetime] = None
    end_at: Optional[datetime] = None
    location: Optional[str] = None
    audience: Optional[str] = None
    description: Optional[str] = None
    tags: Optional[List[str]] = None
    schools: Optional[List[str]] = None


class EventResponse(BaseModel):
    id: UUID
    title: str
    type: EventType
    status: EventStatus
    start_at: datetime
    end_at: Optional[datetime]
    location: Optional[str]
    audience: Optional[str]
    description: Optional[str]
    tags: List[str]
    schools: List[str]
    created_by: UUID
    created_at: datetime
    updated_at: datetime
    creator: UserResponse
    
    class Config:
        from_attributes = True


class EventListResponse(BaseModel):
    id: UUID
    title: str
    type: EventType
    status: EventStatus
    start_at: datetime
    location: Optional[str]
    created_by: UUID
    created_at: datetime
    creator: UserResponse
    
    class Config:
        from_attributes = True


# File Schemas
class FileUploadResponse(BaseModel):
    id: UUID
    event_id: UUID
    kind: FileKind
    filename: str
    mime: str
    size: int
    url: str
    thumbnail_url: Optional[str]
    uploaded_by: UUID
    created_at: datetime
    uploader: UserResponse
    
    class Config:
        from_attributes = True


# Attendance Schemas
class AttendanceCreate(BaseModel):
    person_name: str = Field(..., min_length=3)
    person_role: Optional[str] = None
    school: Optional[str] = None
    present: bool = True


class AttendanceResponse(BaseModel):
    id: UUID
    event_id: UUID
    person_name: str
    person_role: Optional[str]
    school: Optional[str]
    present: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


# Note Schemas
class NoteCreate(BaseModel):
    text: str = Field(..., min_length=1)


class NoteUpdate(BaseModel):
    text: str = Field(..., min_length=1)


class NoteResponse(BaseModel):
    id: UUID
    event_id: UUID
    text: str
    created_by: UUID
    created_at: datetime
    updated_at: datetime
    author: UserResponse
    
    class Config:
        from_attributes = True


# Audit Log Schema
class AuditLogResponse(BaseModel):
    id: UUID
    user_id: UUID
    action: str
    entity: str
    entity_id: str
    metadata: dict
    created_at: datetime
    user: UserResponse
    
    class Config:
        from_attributes = True
