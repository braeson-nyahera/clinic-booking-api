
from datetime import datetime

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Appointment(Base):
    __tablename__ = "appointments"

    __table_args__ = (
        CheckConstraint(
            "end_at > start_at",
            name="ck_appointment_end_after_start",
        ),
        CheckConstraint(
            "status IN ('booked', 'cancelled')",
            name="ck_appointment_valid_status",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    doctor_id: Mapped[int] = mapped_column(
        ForeignKey("doctors.id"),
        nullable=False,
        index=True,
    )
    patient_id: Mapped[int] = mapped_column(
        ForeignKey("patients.id"),
        nullable=False,
        index=True,
    )
    start_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, index=True
    )
    end_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    status: Mapped[str] = mapped_column(
        String(20), default="booked", nullable=False
    )
    cancellation_reason: Mapped[str | None] = mapped_column(
        Text, nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    doctor = relationship("Doctor", back_populates="appointments")
    patient = relationship("Patient", back_populates="appointments")
