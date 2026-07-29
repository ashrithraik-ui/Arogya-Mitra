"""
ArogyaMitra AI — Doctor Routing & Management Service
Finds available doctors and manages routing logic.
"""

import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from backend.models.doctor import Doctor

logger = logging.getLogger(__name__)


class DoctorService:
    """Handles doctor availability checks and routing decisions."""

    async def find_available_doctor(
        self,
        db: AsyncSession,
        specialization: str | None = None,
    ) -> Doctor | None:
        """
        Find the first available, active doctor.

        Args:
            db: Async DB session.
            specialization: If provided, prefer doctors with this specialization.

        Returns:
            A Doctor instance if one is available, otherwise None.
        """
        # Try preferred specialization first
        if specialization:
            result = await db.execute(
                select(Doctor).where(
                    and_(
                        Doctor.is_available == True,  # noqa: E712
                        Doctor.is_active == True,     # noqa: E712
                        Doctor.specialization.ilike(f"%{specialization}%"),
                    )
                ).limit(1)
            )
            doctor = result.scalars().first()
            if doctor:
                return doctor

        # Fall back to any available doctor
        result = await db.execute(
            select(Doctor).where(
                and_(
                    Doctor.is_available == True,  # noqa: E712
                    Doctor.is_active == True,     # noqa: E712
                )
            ).limit(1)
        )
        return result.scalars().first()

    async def get_doctor_by_id(self, db: AsyncSession, doctor_id: int) -> Doctor | None:
        """Fetch a doctor by primary key."""
        result = await db.execute(select(Doctor).where(Doctor.id == doctor_id))
        return result.scalars().first()

    async def get_doctor_by_email(self, db: AsyncSession, email: str) -> Doctor | None:
        """Fetch a doctor by email address (case-insensitive)."""
        result = await db.execute(
            select(Doctor).where(Doctor.email.ilike(email))
        )
        return result.scalars().first()

    async def list_available_doctors(self, db: AsyncSession) -> list[Doctor]:
        """Return all currently available, active doctors."""
        result = await db.execute(
            select(Doctor).where(
                and_(
                    Doctor.is_available == True,  # noqa: E712
                    Doctor.is_active == True,     # noqa: E712
                )
            )
        )
        return list(result.scalars().all())

    async def set_availability(
        self, db: AsyncSession, doctor_id: int, is_available: bool
    ) -> Doctor | None:
        """Toggle a doctor's availability flag."""
        doctor = await self.get_doctor_by_id(db, doctor_id)
        if doctor:
            doctor.is_available = is_available
            await db.flush()
        return doctor


# Singleton instance
doctor_service = DoctorService()
