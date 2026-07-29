"""
ArogyaMitra AI — Patient ORM Model
"""

from datetime import datetime, timezone
from sqlalchemy import String, Integer, DateTime, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.database import Base


class Patient(Base):
    """Represents a patient registered in the system."""

    __tablename__ = "patients"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    phone: Mapped[str] = mapped_column(String(20), unique=True, index=True, nullable=False)
    email: Mapped[str | None] = mapped_column(String(150), unique=True, index=True, nullable=True)
    age: Mapped[int | None] = mapped_column(Integer, nullable=True)
    gender: Mapped[str | None] = mapped_column(String(20), nullable=True)
    blood_group: Mapped[str | None] = mapped_column(String(5), nullable=True)

    # Known allergies, free text
    allergies: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Known chronic conditions, free text
    known_conditions: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Current medications, free text
    current_medications: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    consultations: Mapped[list["Consultation"]] = relationship(  # noqa: F821
        "Consultation", back_populates="patient", cascade="all, delete-orphan"
    )
    timeline_events: Mapped[list["HealthTimeline"]] = relationship(  # noqa: F821
        "HealthTimeline", back_populates="patient", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Patient id={self.id} name={self.name!r}>"
