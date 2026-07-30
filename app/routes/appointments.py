from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.appointment import (
    AppointmentCancel,
    AppointmentCreate,
    AppointmentRead,
    AppointmentReschedule,
)
from app.services.booking_service import (
    cancel_appointment,
    create_appointment,
    reschedule_appointment,
)

router = APIRouter(prefix="/appointments", tags=["appointments"])


@router.post("", response_model=AppointmentRead, status_code=201)
async def book_appointment(
    payload: AppointmentCreate,
    db: AsyncSession = Depends(get_db),
) -> AppointmentRead:
    appointment = await create_appointment(db, payload.doctor_id, payload.start_time, payload.patient)
    return AppointmentRead.model_validate(appointment)


@router.patch("/{appointment_id}/cancel", response_model=AppointmentRead)
async def cancel_appointment_route(
    appointment_id: int,
    payload: AppointmentCancel,
    db: AsyncSession = Depends(get_db),
) -> AppointmentRead:
    appointment = await cancel_appointment(db, appointment_id, payload.cancellation_reason)
    return AppointmentRead.model_validate(appointment)


@router.patch("/{appointment_id}/reschedule", response_model=AppointmentRead)
async def reschedule_appointment_route(
    appointment_id: int,
    payload: AppointmentReschedule,
    db: AsyncSession = Depends(get_db),
) -> AppointmentRead:
    appointment = await reschedule_appointment(db, appointment_id, payload.new_start_time)
    return AppointmentRead.model_validate(appointment)
