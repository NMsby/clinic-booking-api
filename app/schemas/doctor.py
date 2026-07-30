from datetime import date, datetime

from pydantic import BaseModel


class AvailabilityResponse(BaseModel):
    doctor_id: int
    date: date
    available_slots: list[datetime]
