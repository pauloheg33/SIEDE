import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Boolean, ForeignKey, Integer, Text, JSON, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import enum

from app.database import Base


class UserRole(str, enum.Enum):
    ADMIN = "ADMIN"
    TEC_FORMACAO = "TEC_FORMACAO"
    TEC_ACOMPANHAMENTO = "TEC_ACOMPANHAMENTO"


class EventType(str, enum.Enum):
    FORMACAO = "FORMACAO"
    PREMIACAO = "PREMIACAO"
    ENCONTRO = "ENCONTRO"
    OUTRO = "OUTRO"


class EventStatus(str, enum.Enum):
    PLANEJADO = "PLANEJADO"
    REALIZADO = "REALIZADO"
    ARQUIVADO = "ARQUIVADO"


class FileKind(str, enum.Enum):
    PHOTO = "PHOTO"
    DOC = "DOC"


class User(Base):
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=False)
    role = Column(SQLEnum(UserRole), default=UserRole.TEC_ACOMPANHAMENTO, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    events = relationship("Event", back_populates="creator", foreign_keys="Event.created_by")
    files = relationship("EventFile", back_populates="uploader")
    notes = relationship("EventNote", back_populates="author")
    audit_logs = relationship("AuditLog", back_populates="user")


class Event(Base):
    __tablename__ = "events"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String, nullable=False)
    type = Column(SQLEnum(EventType), nullable=False)
    status = Column(SQLEnum(EventStatus), default=EventStatus.PLANEJADO, nullable=False)
    start_at = Column(DateTime, nullable=False)
    end_at = Column(DateTime)
    location = Column(String)
    audience = Column(String)
    description = Column(Text)
    tags = Column(JSON, default=list)
    schools = Column(JSON, default=list)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    creator = relationship("User", back_populates="events", foreign_keys=[created_by])
    files = relationship("EventFile", back_populates="event", cascade="all, delete-orphan")
    attendance = relationship("Attendance", back_populates="event", cascade="all, delete-orphan")
    notes = relationship("EventNote", back_populates="event", cascade="all, delete-orphan")


class EventFile(Base):
    __tablename__ = "event_files"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    event_id = Column(UUID(as_uuid=True), ForeignKey("events.id"), nullable=False)
    kind = Column(SQLEnum(FileKind), nullable=False)
    filename = Column(String, nullable=False)
    mime = Column(String, nullable=False)
    size = Column(Integer, nullable=False)
    url = Column(String, nullable=False)
    thumbnail_url = Column(String)
    uploaded_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    event = relationship("Event", back_populates="files")
    uploader = relationship("User", back_populates="files")


class Attendance(Base):
    __tablename__ = "attendance"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    event_id = Column(UUID(as_uuid=True), ForeignKey("events.id"), nullable=False)
    person_name = Column(String, nullable=False)
    person_role = Column(String)
    school = Column(String)
    present = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    event = relationship("Event", back_populates="attendance")


class EventNote(Base):
    __tablename__ = "event_notes"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    event_id = Column(UUID(as_uuid=True), ForeignKey("events.id"), nullable=False)
    text = Column(Text, nullable=False)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    event = relationship("Event", back_populates="notes")
    author = relationship("User", back_populates="notes")


class AuditLog(Base):
    __tablename__ = "audit_logs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    action = Column(String, nullable=False)
    entity = Column(String, nullable=False)
    entity_id = Column(String, nullable=False)
    metadata = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="audit_logs")
