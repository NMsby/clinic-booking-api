from datetime import date, datetime, time, timezone
from uuid import uuid4

import pytest

from app.models import Appointment, AppointmentStatus, Patient
from app.services.availability_service import get_availability
from app.services.exceptions import DoctorNotFound
from app.services.schedule_utils import CLINIC_TIMEZONE

TARGET = date(2026, 8, 3)  # Monday, matches doctor_with_hours fixture


@pytest.mark.asyncio
async def test_get_availability_raises_for_unknown_doctor(db_session):
    fixed_now = datetime.combine(TARGET, time(8, 45), tzinfo=CLINIC_TIMEZONE).astimezone(timezone.utc)
    with pytest.raises(DoctorNotFound):
        await get_availability(db_session, 999999, TARGET, now=fixed_now)


@pytest.mark.asyncio
async def test_get_availability_filters_booked_slots_and_lead_time(db_session, doctor_with_hours):
    unique_email = f"avail_pytest_{uuid4().hex[:8]}@example.com"
    patient = Patient(name="Availability Test Patient", email=unique_email, phone="0000000020")
    db_session.add(patient)
    await db_session.commit()
    await db_session.refresh(patient)

    booked_slot = datetime.combine(TARGET, time(9, 30), tzinfo=CLINIC_TIMEZONE)
    existing = Appointment(
        doctor_id=doctor_with_hours.id,
        patient_id=patient.id,
        start_time=booked_slot,
        status=AppointmentStatus.BOOKED,
    )
    db_session.add(existing)
    await db_session.commit()

    fixed_now = datetime.combine(TARGET, time(8, 45), tzinfo=CLINIC_TIMEZONE).astimezone(timezone.utc)
    response = await get_availability(db_session, doctor_with_hours.id, TARGET, now=fixed_now)

    too_soon = datetime.combine(TARGET, time(9, 0), tzinfo=CLINIC_TIMEZONE)
    first_open_slot = datetime.combine(TARGET, time(10, 0), tzinfo=CLINIC_TIMEZONE)

    assert response.doctor_id == doctor_with_hours.id
    assert response.date == TARGET
    assert too_soon not in response.available_slots, "9:00 is inside the 1 hour lead time buffer"
    assert booked_slot not in response.available_slots, "9:30 is already booked"
    assert first_open_slot in response.available_slots, "10:00 is past the buffer and unbooked"
    # working hours are 9:00 to 17:00, 16 half hour slots total, minus the
    # 9:00 buffer exclusion and the 9:30 booked exclusion leaves 14
    assert len(response.available_slots) == 14


@pytest.mark.asyncio
async def test_get_availability_returns_empty_list_for_day_with_no_hours(db_session, doctor_with_hours):
    no_hours_day = date(2026, 8, 4)  # Tuesday, no WorkingHours row exists for this doctor on this day
    fixed_now = datetime.combine(TARGET, time(8, 45), tzinfo=CLINIC_TIMEZONE).astimezone(timezone.utc)
    response = await get_availability(db_session, doctor_with_hours.id, no_hours_day, now=fixed_now)
    assert response.available_slots == []
