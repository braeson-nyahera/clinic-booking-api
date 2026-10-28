
from sqlalchemy import ForeignKey, Integer, Time, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class WorkingHours(Base):
    __tablename__ = "working_hours"

    __table_args__ = (
        UniqueConstraint(
            "doctor_id",
            "day_of_week",
            name="uq_doctor_working_day",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    doctor_id: Mapped[int] = mapped_column(
        ForeignKey("doctors.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    day_of_week: Mapped[int] = mapped_column(
        Integer, nullable=False
    )
    start_time: Mapped[object] = mapped_column(Time, nullable=False)
    end_time: Mapped[object] = mapped_column(Time, nullable=False)

    doctor = relationship("Doctor", back_populates="working_hours")
