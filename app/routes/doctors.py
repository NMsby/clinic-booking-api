from datetime import date

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.doctor import AvailabilityResponse
from app.services.availability_service import get_availability

router = APIRouter(prefix="/doctors", tags=["doctors"])


@router.get("/{doctor_id}/availability", response_model=AvailabilityResponse)
async def read_doctor_availability(
    doctor_id: int,
    date: date,
    db: AsyncSession = Depends(get_db),
) -> AvailabilityResponse:
    return await get_availability(db, doctor_id, date)
