from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
import csv
import io
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors

from app.database import get_db
from app.schemas import AttendanceCreate, AttendanceResponse
from app.models import Event, Attendance, User
from app.auth import get_current_active_user, can_edit_event
from app.audit import log_action

router = APIRouter(prefix="/events/{event_id}/attendance", tags=["attendance"])


@router.get("", response_model=List[AttendanceResponse])
def list_attendance(
    event_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """List attendance for an event"""
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    attendance = db.query(Attendance).filter(
        Attendance.event_id == event_id
    ).order_by(Attendance.person_name).all()
    
    return attendance


@router.post("", response_model=AttendanceResponse, status_code=status.HTTP_201_CREATED)
def add_attendance(
    event_id: UUID,
    attendance_data: AttendanceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Add an attendance record"""
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    # Check permission
    if not can_edit_event(event, current_user):
        raise HTTPException(status_code=403, detail="Not authorized to edit this event")
    
    attendance = Attendance(
        event_id=event_id,
        **attendance_data.model_dump()
    )
    
    db.add(attendance)
    db.commit()
    db.refresh(attendance)
    
    log_action(db, current_user.id, "CREATE", "attendance", str(attendance.id), {
        "event_id": str(event_id),
        "person_name": attendance.person_name
    })
    
    return attendance


@router.post("/import", status_code=status.HTTP_201_CREATED)
async def import_attendance(
    event_id: UUID,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Import attendance from CSV file"""
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    # Check permission
    if not can_edit_event(event, current_user):
        raise HTTPException(status_code=403, detail="Not authorized to edit this event")
    
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="File must be CSV")
    
    # Read CSV
    content = await file.read()
    decoded = content.decode('utf-8-sig')  # Handle BOM
    csv_reader = csv.DictReader(io.StringIO(decoded))
    
    expected_columns = {'person_name', 'person_role', 'school', 'present'}
    if not expected_columns.issubset(set(csv_reader.fieldnames or [])):
        raise HTTPException(
            status_code=400,
            detail=f"CSV must have columns: {', '.join(expected_columns)}"
        )
    
    imported_count = 0
    for row in csv_reader:
        present = row.get('present', '').lower() in ('true', '1', 'sim', 'yes', 'presente')
        
        attendance = Attendance(
            event_id=event_id,
            person_name=row['person_name'],
            person_role=row.get('person_role') or None,
            school=row.get('school') or None,
            present=present
        )
        db.add(attendance)
        imported_count += 1
    
    db.commit()
    
    log_action(db, current_user.id, "IMPORT", "attendance", str(event_id), {
        "count": imported_count
    })
    
    return {"message": f"Imported {imported_count} attendance records"}


@router.get("/export/csv")
def export_attendance_csv(
    event_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Export attendance to CSV"""
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    attendance = db.query(Attendance).filter(
        Attendance.event_id == event_id
    ).order_by(Attendance.person_name).all()
    
    # Create CSV
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['person_name', 'person_role', 'school', 'present'])
    
    for record in attendance:
        writer.writerow([
            record.person_name,
            record.person_role or '',
            record.school or '',
            'Sim' if record.present else 'Não'
        ])
    
    output.seek(0)
    
    log_action(db, current_user.id, "EXPORT_CSV", "attendance", str(event_id))
    
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename=frequencia_{event.title[:30]}.csv"
        }
    )


@router.get("/export/pdf")
def export_attendance_pdf(
    event_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Export attendance to PDF"""
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    attendance = db.query(Attendance).filter(
        Attendance.event_id == event_id
    ).order_by(Attendance.person_name).all()
    
    # Create PDF
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []
    
    styles = getSampleStyleSheet()
    
    # Title
    title = Paragraph(f"<b>Lista de Frequência</b><br/>{event.title}", styles['Title'])
    elements.append(title)
    elements.append(Spacer(1, 12))
    
    # Event info
    info = Paragraph(
        f"Data: {event.start_at.strftime('%d/%m/%Y %H:%M')}<br/>"
        f"Local: {event.location or 'N/A'}<br/>"
        f"Total de participantes: {len(attendance)}",
        styles['Normal']
    )
    elements.append(info)
    elements.append(Spacer(1, 12))
    
    # Table
    data = [['Nome', 'Função', 'Escola', 'Presente']]
    for record in attendance:
        data.append([
            record.person_name,
            record.person_role or '',
            record.school or '',
            'Sim' if record.present else 'Não'
        ])
    
    table = Table(data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    elements.append(table)
    
    doc.build(elements)
    buffer.seek(0)
    
    log_action(db, current_user.id, "EXPORT_PDF", "attendance", str(event_id))
    
    return StreamingResponse(
        buffer,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename=frequencia_{event.title[:30]}.pdf"
        }
    )


@router.delete("/{attendance_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_attendance(
    event_id: UUID,
    attendance_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Delete an attendance record"""
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    # Check permission
    if not can_edit_event(event, current_user):
        raise HTTPException(status_code=403, detail="Not authorized to edit this event")
    
    attendance = db.query(Attendance).filter(
        Attendance.id == attendance_id,
        Attendance.event_id == event_id
    ).first()
    
    if not attendance:
        raise HTTPException(status_code=404, detail="Attendance record not found")
    
    log_action(db, current_user.id, "DELETE", "attendance", str(attendance.id), {
        "person_name": attendance.person_name
    })
    
    db.delete(attendance)
    db.commit()
    
    return None
