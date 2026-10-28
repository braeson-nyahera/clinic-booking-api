
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class AppointmentCreate(BaseModel):
    doctor_id: int = Field(gt=0)
    patient_id: int = Field(gt=0)
    start_at: datetime


class AppointmentResponse(BaseModel):
    id: int
    doctor_id: int
    patient_id: int
    start_at: datetime
    end_at: datetime
    status: str

    model_config = ConfigDict(from_attributes=True)


class AppointmentCancel(BaseModel):
    reason: str = Field(min_length=1, max_length=1000)


class AppointmentReschedule(BaseModel):
    new_start_at: datetime
