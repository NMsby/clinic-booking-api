from datetime import date, datetime, time, timezone

import pytest

from app.schemas.patient import PatientCreate
from app.services.booking_service import cancel_appointment, create_appointment, reschedule_appointment
from app.services.exceptions import (
    AppointmentAlreadyCancelledError,
    AppointmentNotFound,
    DoctorNotFound,
    InsufficientLeadTimeError,
    OffSlotGridError,
    OutsideWorkingHoursError,
    SlotAlreadyBookedError,
)
from app.services.schedule_utils import CLINIC_TIMEZONE

TARGET = date(2026, 8, 3)  # Monday, matches doctor_with_hours fixture
FIXED_NOW = datetime.combine(TARGET, time(7, 0), tzinfo=CLINIC_TIMEZONE).astimezone(timezone.utc)


def _patient(suffix: str) -> PatientCreate:
    return PatientCreate(
        name=f"Test Patient {suffix}",
        email=f"booking_pytest_{suffix}@example.com",
        phone="0000000030",
    )


@pytest.mark.asyncio
async def test_create_appointment_raises_for_unknown_doctor(db_session):
    with pytest.raises(DoctorNotFound):
        await create_appointment(
            db_session, 999999,
            datetime.combine(TARGET, time(10, 0), tzinfo=CLINIC_TIMEZONE),
            _patient("a"), now=FIXED_NOW,
        )


@pytest.mark.asyncio
async def test_create_appointment_rejects_off_grid_time(db_session, doctor_with_hours):
    with pytest.raises(OffSlotGridError):
        await create_appointment(
            db_session, doctor_with_hours.id,
            datetime.combine(TARGET, time(10, 15), tzinfo=CLINIC_TIMEZONE),
            _patient("b"), now=FIXED_NOW,
        )


@pytest.mark.asyncio
async def test_create_appointment_rejects_time_outside_working_hours(db_session, doctor_with_hours):
    with pytest.raises(OutsideWorkingHoursError):
        await create_appointment(
            db_session, doctor_with_hours.id,
            datetime.combine(TARGET, time(8, 0), tzinfo=CLINIC_TIMEZONE),
            _patient("c"), now=FIXED_NOW,
        )


@pytest.mark.asyncio
async def test_create_appointment_rejects_insufficient_lead_time(db_session, doctor_with_hours):
    now = datetime.combine(TARGET, time(8, 30), tzinfo=CLINIC_TIMEZONE).astimezone(timezone.utc)
    too_soon = datetime.combine(TARGET, time(9, 0), tzinfo=CLINIC_TIMEZONE)
    with pytest.raises(InsufficientLeadTimeError):
        await create_appointment(db_session, doctor_with_hours.id, too_soon, _patient("d"), now=now)


@pytest.mark.asyncio
async def test_create_appointment_succeeds_and_creates_patient(db_session, doctor_with_hours):
    slot = datetime.combine(TARGET, time(10, 0), tzinfo=CLINIC_TIMEZONE)
    appointment = await create_appointment(db_session, doctor_with_hours.id, slot, _patient("e"), now=FIXED_NOW)
    assert appointment.id is not None
    assert appointment.start_time == slot


@pytest.mark.asyncio
async def test_create_appointment_reuses_existing_patient_by_email(db_session, doctor_with_hours):
    patient_data = _patient("f")
    slot_1 = datetime.combine(TARGET, time(10, 0), tzinfo=CLINIC_TIMEZONE)
    slot_2 = datetime.combine(TARGET, time(10, 30), tzinfo=CLINIC_TIMEZONE)

    first = await create_appointment(db_session, doctor_with_hours.id, slot_1, patient_data, now=FIXED_NOW)
    second = await create_appointment(db_session, doctor_with_hours.id, slot_2, patient_data, now=FIXED_NOW)

    assert second.patient_id == first.patient_id


@pytest.mark.asyncio
async def test_create_appointment_rejects_double_booking_same_slot(db_session, doctor_with_hours):
    slot = datetime.combine(TARGET, time(10, 0), tzinfo=CLINIC_TIMEZONE)
    await create_appointment(db_session, doctor_with_hours.id, slot, _patient("g1"), now=FIXED_NOW)

    with pytest.raises(SlotAlreadyBookedError):
        await create_appointment(db_session, doctor_with_hours.id, slot, _patient("g2"), now=FIXED_NOW)


@pytest.mark.asyncio
async def test_cancel_appointment_raises_for_unknown_id(db_session):
    with pytest.raises(AppointmentNotFound):
        await cancel_appointment(db_session, 999999, "test")


@pytest.mark.asyncio
async def test_cancel_appointment_succeeds(db_session, doctor_with_hours):
    slot = datetime.combine(TARGET, time(10, 0), tzinfo=CLINIC_TIMEZONE)
    appointment = await create_appointment(db_session, doctor_with_hours.id, slot, _patient("h"), now=FIXED_NOW)

    cancelled = await cancel_appointment(db_session, appointment.id, "patient requested cancellation")

    assert cancelled.status.value == "cancelled"
    assert cancelled.cancellation_reason == "patient requested cancellation"


@pytest.mark.asyncio
async def test_cancel_appointment_rejects_already_cancelled(db_session, doctor_with_hours):
    slot = datetime.combine(TARGET, time(10, 0), tzinfo=CLINIC_TIMEZONE)
    appointment = await create_appointment(db_session, doctor_with_hours.id, slot, _patient("i"), now=FIXED_NOW)
    appointment_id = appointment.id
    await cancel_appointment(db_session, appointment_id, "first cancellation")

    with pytest.raises(AppointmentAlreadyCancelledError):
        await cancel_appointment(db_session, appointment_id, "second attempt")


@pytest.mark.asyncio
async def test_cancelled_slot_is_bookable_again_by_different_patient(db_session, doctor_with_hours):
    slot = datetime.combine(TARGET, time(10, 0), tzinfo=CLINIC_TIMEZONE)
    first = await create_appointment(db_session, doctor_with_hours.id, slot, _patient("j1"), now=FIXED_NOW)
    await cancel_appointment(db_session, first.id, "freeing the slot")

    second = await create_appointment(db_session, doctor_with_hours.id, slot, _patient("j2"), now=FIXED_NOW)

    assert second.patient_id != first.patient_id
    assert second.start_time == slot


@pytest.mark.asyncio
async def test_reschedule_appointment_raises_for_unknown_id(db_session):
    with pytest.raises(AppointmentNotFound):
        await reschedule_appointment(
            db_session, 999999,
            datetime.combine(TARGET, time(11, 0), tzinfo=CLINIC_TIMEZONE),
            now=FIXED_NOW,
        )


@pytest.mark.asyncio
async def test_reschedule_appointment_moves_appointment_and_frees_old_slot(db_session, doctor_with_hours):
    old_slot = datetime.combine(TARGET, time(10, 0), tzinfo=CLINIC_TIMEZONE)
    new_slot = datetime.combine(TARGET, time(11, 0), tzinfo=CLINIC_TIMEZONE)
    appointment = await create_appointment(db_session, doctor_with_hours.id, old_slot, _patient("k"), now=FIXED_NOW)
    appointment_id = appointment.id

    rescheduled = await reschedule_appointment(db_session, appointment_id, new_slot, now=FIXED_NOW)
    assert rescheduled.id == appointment_id
    assert rescheduled.start_time == new_slot

    old_slot_reused = await create_appointment(
        db_session, doctor_with_hours.id, old_slot, _patient("k2"), now=FIXED_NOW,
    )
    assert old_slot_reused.id is not None


@pytest.mark.asyncio
async def test_reschedule_appointment_rejects_slot_already_booked_by_someone_else(db_session, doctor_with_hours):
    slot_1 = datetime.combine(TARGET, time(10, 0), tzinfo=CLINIC_TIMEZONE)
    slot_2 = datetime.combine(TARGET, time(10, 30), tzinfo=CLINIC_TIMEZONE)
    await create_appointment(db_session, doctor_with_hours.id, slot_1, _patient("l1"), now=FIXED_NOW)
    other = await create_appointment(db_session, doctor_with_hours.id, slot_2, _patient("l2"), now=FIXED_NOW)

    with pytest.raises(SlotAlreadyBookedError):
        await reschedule_appointment(db_session, other.id, slot_1, now=FIXED_NOW)


@pytest.mark.asyncio
async def test_reschedule_appointment_rejects_cancelled_appointment(db_session, doctor_with_hours):
    slot = datetime.combine(TARGET, time(10, 0), tzinfo=CLINIC_TIMEZONE)
    appointment = await create_appointment(db_session, doctor_with_hours.id, slot, _patient("m"), now=FIXED_NOW)
    appointment_id = appointment.id
    await cancel_appointment(db_session, appointment_id, "cancelled before reschedule attempt")

    with pytest.raises(AppointmentAlreadyCancelledError):
        await reschedule_appointment(
            db_session, appointment_id,
            datetime.combine(TARGET, time(13, 0), tzinfo=CLINIC_TIMEZONE),
            now=FIXED_NOW,
        )
