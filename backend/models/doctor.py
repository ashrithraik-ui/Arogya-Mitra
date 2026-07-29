"""
ArogyaMitra AI — Doctor ORM Model
"""

from datetime import datetime, timezone
from sqlalchemy import String, Integer, DateTime, Boolean, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.database import Base


class Doctor(Base):
    """Represents a medical professional in the system."""

    __tablename__ = "doctors"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(150), unique=True, index=True, nullable=False)
    phone: Mapped[str | None] = mapped_column(String(20), nullable=True)
    specialization: Mapped[str] = mapped_column(String(100), nullable=False)
    qualification: Mapped[str | None] = mapped_column(String(200), nullable=True)
    registration_number: Mapped[str | None] = mapped_column(String(50), unique=True, nullable=True)

    # Hashed password for login
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)

    # Availability flags
    is_available: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Additional info
    bio: Mapped[str | None] = mapped_column(Text, nullable=True)
    hospital_affiliation: Mapped[str | None] = mapped_column(String(200), nullable=True)

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
        "Consultation", back_populates="doctor"
    )

    def __repr__(self) -> str:
        return f"<Doctor id={self.id} name={self.name!r} specialization={self.specialization!r}>"
