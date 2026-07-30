from collections.abc import AsyncGenerator
from datetime import date, time

import pytest_asyncio

from app.database import AsyncSessionLocal
from app.models import Doctor, WorkingHours

MONDAY = date(2026, 8, 3)


@pytest_asyncio.fixture
async def db_session() -> AsyncGenerator:
    """A fresh session per test, so a rollback inside one test can never
    expire objects tracked in a different test's session.
    """
    async with AsyncSessionLocal() as session:
        yield session


@pytest_asyncio.fixture
async def doctor_with_hours(db_session) -> Doctor:
    """A doctor working Monday 9 to 5, matching MONDAY above. Uses the
    same session the test itself receives.
    """
    doctor = Doctor(name="Test Doctor")
    db_session.add(doctor)
    await db_session.commit()
    await db_session.refresh(doctor)

    hours = WorkingHours(
        doctor_id=doctor.id,
        day_of_week=MONDAY.weekday(),
        start_time=time(9, 0),
        end_time=time(17, 0),
    )
    db_session.add(hours)
    await db_session.commit()

    return doctor
