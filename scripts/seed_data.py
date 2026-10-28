
from datetime import time

from sqlalchemy import select

from app.database import SessionLocal
from app.models import Doctor, Patient, WorkingHours


def seed_data():
    with SessionLocal() as db:
        # Create a sample doctor if one doesn't already exist.
        doctor = db.scalar(
            select(Doctor).where(Doctor.name == "Dr. Jane Kamau")
        )

        if doctor is None:
            doctor = Doctor(
                name="Dr. Jane Kamau",
                specialty="General Practice",
                is_active=True,
            )
            db.add(doctor)
            db.flush()

        # Monday-Friday, 9:00 AM to 5:00 PM.
        for weekday in range(5):
            hours = db.scalar(
                select(WorkingHours).where(
                    WorkingHours.doctor_id == doctor.id,
                    WorkingHours.day_of_week == weekday,
                )
            )

            if hours is None:
                db.add(
                    WorkingHours(
                        doctor_id=doctor.id,
                        day_of_week=weekday,
                        start_time=time(9, 0),
                        end_time=time(17, 0),
                    )
                )

        # Create a sample patient if one doesn't already exist.
        patient = db.scalar(
            select(Patient).where(
                Patient.email == "test.patient@example.com"
            )
        )

        if patient is None:
            db.add(
                Patient(
                    name="Test Patient",
                    email="test.patient@example.com",
                )
            )

        db.commit()
        print(f"Seed data created or already exists. Doctor ID: {doctor.id}")


if __name__ == "__main__":
    seed_data()
