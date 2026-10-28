
from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Doctor(Base):
    __tablename__ = "doctors"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    specialty: Mapped[str] = mapped_column(String(100), nullable=False)
    is_active: Mapped[bool] = mapped_column(
        Boolean, default=True, nullable=False
    )

    working_hours = relationship(
        "WorkingHours",
        back_populates="doctor",
        cascade="all, delete-orphan",
    )

    appointments = relationship(
        "Appointment",
        back_populates="doctor",
    )
