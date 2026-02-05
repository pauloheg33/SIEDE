"""Initial migration

Revision ID: 001
Revises: 
Create Date: 2026-02-05

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create users table
    op.create_table(
        'users',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('email', sa.String(), nullable=False, unique=True),
        sa.Column('password_hash', sa.String(), nullable=False),
        sa.Column('role', sa.Enum('ADMIN', 'TEC_FORMACAO', 'TEC_ACOMPANHAMENTO', name='userrole'), nullable=False),
        sa.Column('is_active', sa.Boolean(), default=True, nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
    )
    op.create_index('ix_users_email', 'users', ['email'])
    
    # Create events table
    op.create_table(
        'events',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('type', sa.Enum('FORMACAO', 'PREMIACAO', 'ENCONTRO', 'OUTRO', name='eventtype'), nullable=False),
        sa.Column('status', sa.Enum('PLANEJADO', 'REALIZADO', 'ARQUIVADO', name='eventstatus'), nullable=False),
        sa.Column('start_at', sa.DateTime(), nullable=False),
        sa.Column('end_at', sa.DateTime()),
        sa.Column('location', sa.String()),
        sa.Column('audience', sa.String()),
        sa.Column('description', sa.Text()),
        sa.Column('tags', sa.JSON()),
        sa.Column('schools', sa.JSON()),
        sa.Column('created_by', UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
    )
    
    # Create event_files table
    op.create_table(
        'event_files',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('event_id', UUID(as_uuid=True), sa.ForeignKey('events.id'), nullable=False),
        sa.Column('kind', sa.Enum('PHOTO', 'DOC', name='filekind'), nullable=False),
        sa.Column('filename', sa.String(), nullable=False),
        sa.Column('mime', sa.String(), nullable=False),
        sa.Column('size', sa.Integer(), nullable=False),
        sa.Column('url', sa.String(), nullable=False),
        sa.Column('thumbnail_url', sa.String()),
        sa.Column('uploaded_by', UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
    )
    
    # Create attendance table
    op.create_table(
        'attendance',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('event_id', UUID(as_uuid=True), sa.ForeignKey('events.id'), nullable=False),
        sa.Column('person_name', sa.String(), nullable=False),
        sa.Column('person_role', sa.String()),
        sa.Column('school', sa.String()),
        sa.Column('present', sa.Boolean(), default=True, nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
    )
    
    # Create event_notes table
    op.create_table(
        'event_notes',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('event_id', UUID(as_uuid=True), sa.ForeignKey('events.id'), nullable=False),
        sa.Column('text', sa.Text(), nullable=False),
        sa.Column('created_by', UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
    )
    
    # Create audit_logs table
    op.create_table(
        'audit_logs',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('action', sa.String(), nullable=False),
        sa.Column('entity', sa.String(), nullable=False),
        sa.Column('entity_id', sa.String(), nullable=False),
        sa.Column('metadata', sa.JSON()),
        sa.Column('created_at', sa.DateTime(), nullable=False),
    )


def downgrade() -> None:
    op.drop_table('audit_logs')
    op.drop_table('event_notes')
    op.drop_table('attendance')
    op.drop_table('event_files')
    op.drop_table('events')
    op.drop_index('ix_users_email')
    op.drop_table('users')
    
    # Drop enums
    sa.Enum(name='userrole').drop(op.get_bind())
    sa.Enum(name='eventtype').drop(op.get_bind())
    sa.Enum(name='eventstatus').drop(op.get_bind())
    sa.Enum(name='filekind').drop(op.get_bind())
