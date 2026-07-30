from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from app.models.working_hours import WorkingHours

CLINIC_TIMEZONE = ZoneInfo("Africa/Nairobi")


def to_clinic_local(value: datetime) -> datetime:
    """Convert an aware datetime to the clinic's local time zone. Working
    hours, the slot grid, and day of week are civil, local concepts, while
    start_time is an absolute instant that may arrive in any offset, so
    every comparison or day of week lookup against WorkingHours must go
    through this first. value must be timezone aware, a naive value would
    otherwise be silently reinterpreted as being in the system's own local
    time zone rather than raising a clear error.
    """
    if value.tzinfo is None:
        raise ValueError("value must be a timezone-aware datetime")
    return value.astimezone(CLINIC_TIMEZONE)


def is_on_slot_grid(value: datetime) -> bool:
    """Return True if value falls exactly on a 30 minute slot boundary in
    the clinic's local time. The check is performed after converting to
    clinic local time, not on whatever offset value arrives in, since the
    slot grid is a local scheduling concept the same way working hours
    are, and offsets that are not a whole number of hours would otherwise
    shift the minute value and give a wrong answer.
    """
    local_value = to_clinic_local(value)
    return local_value.minute in (0, 30) and local_value.second == 0 and local_value.microsecond == 0


def is_within_working_hours(start_time: datetime, working_hours: WorkingHours | None) -> bool:
    """Return True if the 30 minute appointment starting at start_time fits
    entirely within the given working hours window. working_hours is the
    row for the doctor on the relevant day of week, already fetched by the
    caller, or None if the doctor does not work that day.
    """
    if working_hours is None:
        return False
    local_start = to_clinic_local(start_time)
    local_end = local_start + timedelta(minutes=30)
    return working_hours.start_time <= local_start.time() and local_end.time() <= working_hours.end_time


def is_bookable_time(start_time: datetime, now: datetime) -> bool:
    """Return True if start_time is at least 1 hour after now. now must be
    a timezone aware datetime, since start_time is guaranteed aware by the
    request schema and a naive comparison against it would raise TypeError.
    """
    if now.tzinfo is None:
        raise ValueError("now must be a timezone-aware datetime")
    return start_time >= now + timedelta(hours=1)
