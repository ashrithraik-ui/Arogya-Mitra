"""
ArogyaMitra AI — Health Timeline ORM Model
"""

from datetime import datetime, timezone
from sqlalchemy import String, Integer, DateTime, Text, ForeignKey, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.database import Base
import enum


class TimelineEventType(str, enum.Enum):
    SYMPTOM = "symptom"
    REPORT = "report"            # Uploaded lab / diagnostic report
    IMAGE = "image"              # Uploaded medical image
    PRESCRIPTION = "prescription"
    DOCTOR_NOTE = "doctor_note"
    CONSULTATION = "consultation"
    REFERRAL = "referral"
    VOICE_NOTE = "voice_note"


class HealthTimeline(Base):
    """
    Chronological health events for a patient.
    Each consultation, uploaded report, prescription, or doctor note
    creates one or more timeline entries.
    """

    __tablename__ = "health_timeline"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    patient_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("patients.id", ondelete="CASCADE"), nullable=False, index=True
    )

    event_type: Mapped[TimelineEventType] = mapped_column(
        SAEnum(TimelineEventType), nullable=False, index=True
    )

    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Flexible extra data: doctor name, file path, medicine list, etc.
    # Stored as a JSON string.
    metadata_json: Mapped[str | None] = mapped_column(Text, nullable=True, default="{}")

    # Optional reference to a consultation
    consultation_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("consultations.id", ondelete="SET NULL"), nullable=True
    )

    # File path if this event has an associated upload
    file_path: Mapped[str | None] = mapped_column(String(500), nullable=True)

    # The clinical date of this event (may differ from created_at)
    event_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    patient: Mapped["Patient"] = relationship("Patient", back_populates="timeline_events")  # noqa: F821

    def __repr__(self) -> str:
        return (
            f"<HealthTimeline id={self.id} patient_id={self.patient_id} "
            f"type={self.event_type} date={self.event_date.date()}>"
        )
