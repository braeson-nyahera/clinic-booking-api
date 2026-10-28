
from datetime import date, datetime, time, timedelta
from zoneinfo import ZoneInfo

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Appointment, Doctor, WorkingHours
from app.schemas.availability import AvailabilitySlot


router = APIRouter(prefix="/doctors", tags=["Doctors"])

CLINIC_TIMEZONE = ZoneInfo("Africa/Nairobi")
SLOT_DURATION = timedelta(minutes=30)


@router.get(
    "/{doctor_id}/availability",
    response_model=list[AvailabilitySlot],
)
def get_doctor_availability(
    doctor_id: int,
    appointment_date: date = Query(..., alias="date"),
    db: Session = Depends(get_db),
):
    # Confirm that the doctor exists and is active.
    doctor = db.scalar(
        select(Doctor).where(
            Doctor.id == doctor_id,
            Doctor.is_active.is_(True),
        )
    )

    if doctor is None:
        raise HTTPException(
            status_code=404,
            detail="Doctor not found or inactive",
        )

    # Monday = 0, Sunday = 6.
    weekday = appointment_date.weekday()

    working_hours = db.scalar(
        select(WorkingHours).where(
            WorkingHours.doctor_id == doctor_id,
            WorkingHours.day_of_week == weekday,
        )
    )

    # No schedule means there are no available slots.
    if working_hours is None:
        return []

    if working_hours.end_time <= working_hours.start_time:
        raise HTTPException(
            status_code=500,
            detail="Doctor has an invalid working-hours configuration",
        )

    clinic_start = datetime.combine(
        appointment_date,
        time.min,
        tzinfo=CLINIC_TIMEZONE,
    )
    clinic_end = clinic_start + timedelta(days=1)

    # Fetch existing bookings that overlap this clinic day.
    appointments = db.scalars(
        select(Appointment).where(
            Appointment.doctor_id == doctor_id,
            Appointment.status == "booked",
            Appointment.start_at < clinic_end,
            Appointment.end_at > clinic_start,
        )
    ).all()

    # Generate consecutive 30-minute slots within working hours.
    slot_start = datetime.combine(
        appointment_date,
        working_hours.start_time,
        tzinfo=CLINIC_TIMEZONE,
    )
    working_end = datetime.combine(
        appointment_date,
        working_hours.end_time,
        tzinfo=CLINIC_TIMEZONE,
    )

    available_slots = []

    while slot_start + SLOT_DURATION <= working_end:
        slot_end = slot_start + SLOT_DURATION

        overlaps_booking = any(
            appointment.start_at < slot_end
            and appointment.end_at > slot_start
            for appointment in appointments
        )

        # Don't return slots that have already started.
        if slot_start > datetime.now(CLINIC_TIMEZONE) and not overlaps_booking:
            available_slots.append(
                AvailabilitySlot(
                    start_at=slot_start,
                    end_at=slot_end,
                )
            )

        slot_start = slot_end

    return available_slots
