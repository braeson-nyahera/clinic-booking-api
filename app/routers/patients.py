from datetime import datetime
from zoneinfo import ZoneInfo

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Appointment, Patient
from app.schemas.appointment import AppointmentResponse

router = APIRouter(prefix="/patients", tags=["Patients"])
CLINIC_TIMEZONE = ZoneInfo("Africa/Nairobi")


@router.get(
    "/{patient_id}/appointments",
    response_model=list[AppointmentResponse],
)
def get_patient_upcoming_appointments(
    patient_id: int,
    db: Session = Depends(get_db),
):
    patient = db.get(Patient, patient_id)

    if patient is None:
        raise HTTPException(status_code=404, detail="Patient not found")

    now = datetime.now(CLINIC_TIMEZONE)

    appointments = db.scalars(
        select(Appointment)
        .where(
            Appointment.patient_id == patient_id,
            Appointment.status == "booked",
            Appointment.start_at > now,
        )
        .order_by(Appointment.start_at.asc())
    ).all()

    return appointments