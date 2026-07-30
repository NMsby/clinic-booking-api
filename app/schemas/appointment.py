from datetime import datetime, timedelta
from typing import Annotated

from pydantic import AfterValidator, BaseModel, ConfigDict, Field, computed_field

from app.models.appointment import AppointmentStatus
from app.schemas.patient import PatientCreate


def _ensure_timezone_aware(value: datetime) -> datetime:
    if value.tzinfo is None:
        raise ValueError(
            "start_time must include timezone information, for example an "
            "ISO 8601 string with a UTC offset or a trailing Z"
        )
    return value


AwareDatetime = Annotated[datetime, AfterValidator(_ensure_timezone_aware)]


class AppointmentCreate(BaseModel):
    doctor_id: int
    start_time: AwareDatetime
    patient: PatientCreate


class AppointmentCancel(BaseModel):
    cancellation_reason: str = Field(min_length=1, max_length=500)


class AppointmentReschedule(BaseModel):
    new_start_time: AwareDatetime


class AppointmentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    doctor_id: int
    patient_id: int
    start_time: datetime
    status: AppointmentStatus
    cancellation_reason: str | None
    created_at: datetime
    updated_at: datetime

    @computed_field
    @property
    def end_time(self) -> datetime:
        return self.start_time + timedelta(minutes=30)
