
from datetime import datetime

from pydantic import BaseModel


class AvailabilitySlot(BaseModel):
    start_at: datetime
    end_at: datetime
