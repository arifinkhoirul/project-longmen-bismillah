import uuid
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.schemas.user import InviteUserRequest, UpdateUserRequest, UserDetailResponse, RoleResponse
from app.services.user_service import user_service
from app.utils.deps import get_current_user
from app.models.user import User

router = APIRouter(prefix="/users", tags=["User Management"])


@router.get("/roles", response_model=list[RoleResponse])
async def get_roles(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List semua role yang tersedia."""
    return await user_service.get_all_roles(db)


@router.get("", response_model=list[UserDetailResponse])
async def get_company_users(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List semua user dalam company (semua role bisa akses)."""
    return await user_service.get_company_users(db, current_user)


@router.post("/invite", response_model=UserDetailResponse, status_code=201)
async def invite_user(
    payload: InviteUserRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Boss mengundang admin atau teknisi baru ke company."""
    return await user_service.invite_user(db, payload, current_user)


@router.put("/{user_id}", response_model=UserDetailResponse)
async def update_user(
    user_id: uuid.UUID,
    payload: UpdateUserRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Boss update nama atau role user."""
    return await user_service.update_user(db, user_id, payload, current_user)


@router.delete("/{user_id}")
async def remove_user(
    user_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Boss hapus user dari company."""
    return await user_service.remove_user(db, user_id, current_user)