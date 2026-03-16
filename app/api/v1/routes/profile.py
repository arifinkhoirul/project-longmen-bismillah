from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.schemas.profile import (
    UpdateProfileRequest,
    UpdateCompanyRequest,
    ProfileResponse,
    CompanyResponse,
)
from app.services.profile_service import profile_service
from app.utils.deps import get_current_user
from app.models.user import User

router = APIRouter(prefix="/profile", tags=["Profile"])


@router.get("", response_model=ProfileResponse)
async def get_profile(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Lihat profil user yang sedang login beserta data company."""
    return await profile_service.get_profile(db, current_user)


@router.put("", response_model=ProfileResponse)
async def update_profile(
    payload: UpdateProfileRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update nama dan/atau email profil."""
    return await profile_service.update_profile(db, payload, current_user)


@router.get("/company", response_model=CompanyResponse)
async def get_company(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Lihat profil company."""
    return await profile_service.get_company_profile(db, current_user)


@router.put("/company", response_model=CompanyResponse)
async def update_company(
    payload: UpdateCompanyRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Boss update profil company (nama, email, phone, address)."""
    return await profile_service.update_company_profile(db, payload, current_user)