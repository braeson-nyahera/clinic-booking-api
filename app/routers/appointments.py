
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Appointment, Doctor, Patient, WorkingHours
from app.schemas.appointment import (
    AppointmentCancel,
    AppointmentCreate,
    AppointmentResponse,
)

router = APIRouter(prefix="/appointments", tags=["Appointments"])

CLINIC_TIMEZONE = ZoneInfo("Africa/Nairobi")
SLOT_DURATION = timedelta(minutes=30)


@router.post(
    "",
    response_model=AppointmentResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_appointment(
    payload: AppointmentCreate,
    db: Session = Depends(get_db),
):
    # Require an explicit timezone so appointment times are unambiguous.
    if payload.start_at.tzinfo is None or payload.start_at.utcoffset() is None:
        raise HTTPException(
            status_code=422,
            detail="start_at must include a timezone, e.g. +03:00",
        )

    start_at = payload.start_at.astimezone(CLINIC_TIMEZONE)
    end_at = start_at + SLOT_DURATION
    now = datetime.now(CLINIC_TIMEZONE)

    if start_at <= now:
        raise HTTPException(
            status_code=400,
            detail="Appointments must be scheduled in the future",
        )

    doctor = db.scalar(
        select(Doctor).where(
            Doctor.id == payload.doctor_id,
            Doctor.is_active.is_(True),
        )
    )
    if doctor is None:
        raise HTTPException(status_code=404, detail="Doctor not found or inactive")

    patient = db.get(Patient, payload.patient_id)
    if patient is None:
        raise HTTPException(status_code=404, detail="Patient not found")

    # A slot must start and end on the same calendar date in Nairobi.
    if start_at.date() != (end_at - timedelta(microseconds=1)).date():
        raise HTTPException(
            status_code=400,
            detail="Appointments must fit within one clinic day",
        )

    working_hours = db.scalar(
        select(WorkingHours).where(
            WorkingHours.doctor_id == doctor.id,
            WorkingHours.day_of_week == start_at.weekday(),
        )
    )

    if working_hours is None:
        raise HTTPException(
            status_code=400,
            detail="Doctor does not work on this day",
        )

    clinic_start = datetime.combine(
        start_at.date(), working_hours.start_time, tzinfo=CLINIC_TIMEZONE
    )
    clinic_end = datetime.combine(
        start_at.date(), working_hours.end_time, tzinfo=CLINIC_TIMEZONE
    )

    if start_at < clinic_start or end_at > clinic_end:
        raise HTTPException(
            status_code=400,
            detail="Appointment is outside the doctor's working hours",
        )

    # Prevent overlapping bookings for the same doctor.
    overlapping = db.scalar(
        select(Appointment.id).where(
            Appointment.doctor_id == doctor.id,
            Appointment.status == "booked",
            Appointment.start_at < end_at,
            Appointment.end_at > start_at,
        ).limit(1)
    )

    if overlapping is not None:
        raise HTTPException(
            status_code=409,
            detail="This appointment slot is already booked",
        )

    appointment = Appointment(
        doctor_id=doctor.id,
        patient_id=patient.id,
        start_at=start_at,
        end_at=end_at,
        status="booked",
    )

    db.add(appointment)
    db.commit()
    db.refresh(appointment)

    return appointment


@router.patch(
    "/{appointment_id}/cancel",
    response_model=AppointmentResponse,
)
def cancel_appointment(
    appointment_id: int,
    payload: AppointmentCancel,
    db: Session = Depends(get_db),
):
    appointment = db.get(Appointment, appointment_id)

    if appointment is None:
        raise HTTPException(
            status_code=404,
            detail="Appointment not found",
        )

    if appointment.status == "cancelled":
        raise HTTPException(
            status_code=409,
            detail="Appointment is already cancelled",
        )

    reason = payload.reason.strip()
    if not reason:
        raise HTTPException(
            status_code=422,
            detail="Cancellation reason cannot be blank",
        )

    appointment.status = "cancelled"
    appointment.cancellation_reason = reason

    db.commit()
    db.refresh(appointment)

    return appointment

