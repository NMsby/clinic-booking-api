from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.appointment import AppointmentRead
from app.services.booking_service import get_patient_appointments

router = APIRouter(prefix="/patients", tags=["patients"])


@router.get("/{patient_id}/appointments", response_model=list[AppointmentRead])
async def read_patient_appointments(
    patient_id: int,
    db: AsyncSession = Depends(get_db),
) -> list[AppointmentRead]:
    appointments = await get_patient_appointments(db, patient_id)
    return [AppointmentRead.model_validate(a) for a in appointments]
