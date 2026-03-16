from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from fastapi import HTTPException, status

from app.models.user import User
from app.models.company import Company
from app.schemas.profile import UpdateProfileRequest, UpdateCompanyRequest


class ProfileService:

    async def get_profile(self, db: AsyncSession, current_user: User) -> User:
        """Ambil profil lengkap user beserta data company."""
        result = await db.execute(
            select(User)
            .options(selectinload(User.company))
            .where(User.id == current_user.id)
        )
        return result.scalar_one_or_none()

    async def update_profile(self, db: AsyncSession, payload: UpdateProfileRequest, current_user: User) -> User:
        """Update nama dan/atau email user."""
        if payload.email and payload.email != current_user.email:
            existing = await db.execute(
                select(User).where(User.email == payload.email)
            )
            if existing.scalar_one_or_none():
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Email sudah digunakan"
                )

        for field, value in payload.model_dump(exclude_unset=True).items():
            setattr(current_user, field, value)

        await db.commit()

        result = await db.execute(
            select(User)
            .options(selectinload(User.company))
            .where(User.id == current_user.id)
        )
        return result.scalar_one_or_none()

    async def get_company_profile(self, db: AsyncSession, current_user: User) -> Company:
        """Ambil data company milik user."""
        result = await db.execute(
            select(Company).where(Company.id == current_user.company_id)
        )
        company = result.scalar_one_or_none()
        if not company:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company tidak ditemukan")
        return company

    async def update_company_profile(self, db: AsyncSession, payload: UpdateCompanyRequest, current_user: User) -> Company:
        """Boss update profil company."""
        if current_user.role_id != 1:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Hanya boss yang dapat mengubah profil company"
            )

        company = await self.get_company_profile(db, current_user)

        for field, value in payload.model_dump(exclude_unset=True).items():
            setattr(company, field, value)

        await db.commit()
        await db.refresh(company)
        return company


profile_service = ProfileService()