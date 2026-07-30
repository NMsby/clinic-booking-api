from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.appointment import Appointment
    from app.models.working_hours import WorkingHours


class Doctor(Base):
    __tablename__ = "doctors"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)

    working_hours: Mapped[list["WorkingHours"]] = relationship(
        back_populates="doctor", cascade="all, delete-orphan", passive_deletes=True
    )
    appointments: Mapped[list["Appointment"]] = relationship(
        back_populates="doctor", passive_deletes=True
    )
