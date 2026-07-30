from datetime import date, datetime, time, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.appointment import Appointment, AppointmentStatus
from app.models.doctor import Doctor
from app.models.working_hours import WorkingHours
from app.schemas.doctor import AvailabilityResponse
from app.services.exceptions import DoctorNotFound
from app.services.schedule_utils import CLINIC_TIMEZONE, is_bookable_time


async def get_availability(
    db: AsyncSession,
    doctor_id: int,
    target_date: date,
    now: datetime | None = None,
) -> AvailabilityResponse:
    """Return every open 30 minute slot for doctor_id on target_date. now
    defaults to the real current time and exists as a parameter only so
    tests can supply a fixed value instead of depending on the real clock.
    """
    if now is None:
        now = datetime.now(timezone.utc)

    doctor = await db.get(Doctor, doctor_id)
    if doctor is None:
        raise DoctorNotFound(doctor_id)

    day_of_week = target_date.weekday()
    result = await db.execute(
        select(WorkingHours).where(
            WorkingHours.doctor_id == doctor_id,
            WorkingHours.day_of_week == day_of_week,
        )
    )
    working_hours = result.scalar_one_or_none()

    if working_hours is None:
        return AvailabilityResponse(doctor_id=doctor_id, date=target_date, available_slots=[])

    day_start = datetime.combine(target_date, time.min, tzinfo=CLINIC_TIMEZONE)
    day_end = day_start + timedelta(days=1)

    result = await db.execute(
        select(Appointment.start_time).where(
            Appointment.doctor_id == doctor_id,
            Appointment.status == AppointmentStatus.BOOKED,
            Appointment.start_time >= day_start,
            Appointment.start_time < day_end,
        )
    )
    booked_times = {row[0] for row in result.all()}

    slots: list[datetime] = []
    candidate = datetime.combine(target_date, working_hours.start_time, tzinfo=CLINIC_TIMEZONE)
    closing = datetime.combine(target_date, working_hours.end_time, tzinfo=CLINIC_TIMEZONE)

    while candidate + timedelta(minutes=30) <= closing:
        if candidate not in booked_times and is_bookable_time(candidate, now):
            slots.append(candidate)
        candidate += timedelta(minutes=30)

    return AvailabilityResponse(doctor_id=doctor_id, date=target_date, available_slots=slots)
