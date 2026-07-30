from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.appointment import Appointment, AppointmentStatus
from app.models.doctor import Doctor
from app.models.patient import Patient
from app.models.working_hours import WorkingHours
from app.schemas.patient import PatientCreate
from app.services.exceptions import (
    AppointmentAlreadyCancelledError,
    AppointmentNotFound,
    DoctorNotFound,
    InsufficientLeadTimeError,
    OffSlotGridError,
    OutsideWorkingHoursError,
    PatientNotFound,
    SlotAlreadyBookedError,
)
from app.services.schedule_utils import (
    is_bookable_time,
    is_on_slot_grid,
    is_within_working_hours,
    to_clinic_local,
)


async def _get_or_create_patient(db: AsyncSession, patient_data: PatientCreate) -> Patient:
    result = await db.execute(select(Patient).where(Patient.email == patient_data.email))
    patient = result.scalar_one_or_none()
    if patient is not None:
        return patient
    patient = Patient(
        name=patient_data.name,
        email=patient_data.email,
        phone=patient_data.phone,
    )
    db.add(patient)
    await db.flush()
    return patient


async def _validate_slot(db: AsyncSession, doctor_id: int, start_time: datetime, now: datetime) -> None:
    if not is_on_slot_grid(start_time):
        raise OffSlotGridError(start_time)

    day_of_week = to_clinic_local(start_time).weekday()
    result = await db.execute(
        select(WorkingHours).where(
            WorkingHours.doctor_id == doctor_id,
            WorkingHours.day_of_week == day_of_week,
        )
    )
    working_hours = result.scalar_one_or_none()
    if not is_within_working_hours(start_time, working_hours):
        raise OutsideWorkingHoursError(doctor_id, start_time)

    if not is_bookable_time(start_time, now):
        raise InsufficientLeadTimeError(start_time, now)


async def create_appointment(
    db: AsyncSession,
    doctor_id: int,
    start_time: datetime,
    patient_data: PatientCreate,
    now: datetime | None = None,
) -> Appointment:
    if now is None:
        now = datetime.now(timezone.utc)

    doctor = await db.get(Doctor, doctor_id)
    if doctor is None:
        raise DoctorNotFound(doctor_id)

    await _validate_slot(db, doctor_id, start_time, now)

    patient = await _get_or_create_patient(db, patient_data)

    appointment = Appointment(
        doctor_id=doctor_id,
        patient_id=patient.id,
        start_time=start_time,
        status=AppointmentStatus.BOOKED,
    )
    db.add(appointment)
    try:
        await db.commit()
    except IntegrityError as e:
        await db.rollback()
        if e.orig.diag.constraint_name == "uq_appointment_doctor_slot":
            raise SlotAlreadyBookedError(doctor_id, start_time) from e
        raise
    await db.refresh(appointment)
    return appointment


async def cancel_appointment(db: AsyncSession, appointment_id: int, reason: str) -> Appointment:
    appointment = await db.get(Appointment, appointment_id)
    if appointment is None:
        raise AppointmentNotFound(appointment_id)
    if appointment.status == AppointmentStatus.CANCELLED:
        raise AppointmentAlreadyCancelledError(appointment_id)

    appointment.status = AppointmentStatus.CANCELLED
    appointment.cancellation_reason = reason
    await db.commit()
    await db.refresh(appointment)
    return appointment


async def reschedule_appointment(
    db: AsyncSession,
    appointment_id: int,
    new_start_time: datetime,
    now: datetime | None = None,
) -> Appointment:
    if now is None:
        now = datetime.now(timezone.utc)

    appointment = await db.get(Appointment, appointment_id)
    if appointment is None:
        raise AppointmentNotFound(appointment_id)
    if appointment.status == AppointmentStatus.CANCELLED:
        raise AppointmentAlreadyCancelledError(appointment_id)

    doctor_id = appointment.doctor_id
    await _validate_slot(db, doctor_id, new_start_time, now)

    appointment.start_time = new_start_time
    try:
        await db.commit()
    except IntegrityError as e:
        await db.rollback()
        if e.orig.diag.constraint_name == "uq_appointment_doctor_slot":
            raise SlotAlreadyBookedError(doctor_id, new_start_time) from e
        raise
    await db.refresh(appointment)
    return appointment


async def get_patient_appointments(
    db: AsyncSession,
    patient_id: int,
    now: datetime | None = None,
) -> list[Appointment]:
    """Return this patient's upcoming appointments, sorted by start_time.
    Only booked appointments are included, a cancelled appointment is not
    something the patient needs to prepare for or attend. An appointment
    starting at exactly now is included as upcoming, not excluded, since
    it has not yet finished and the patient may still need to see it,
    this matches the inclusive boundary convention already used
    throughout schedule_utils. now defaults to the real current time and
    exists as a parameter only so tests can supply a fixed value instead
    of depending on the real clock.
    """
    if now is None:
        now = datetime.now(timezone.utc)

    patient = await db.get(Patient, patient_id)
    if patient is None:
        raise PatientNotFound(patient_id)

    result = await db.execute(
        select(Appointment)
        .where(
            Appointment.patient_id == patient_id,
            Appointment.status == AppointmentStatus.BOOKED,
            Appointment.start_time >= now,
        )
        .order_by(Appointment.start_time)
    )
    return list(result.scalars().all())
