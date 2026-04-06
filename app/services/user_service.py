import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status

from app.models.user import User
from app.models.role import Role
from app.core.security import hash_password
from app.schemas.user import InviteUserRequest, UpdateUserRequest


# Role IDs — sesuaikan dengan data di tabel roles
ROLE_BOSS = 1
ROLE_ADMIN = 2
ROLE_TEKNISI = 3

# Role yang boleh diundang oleh boss
INVITABLE_ROLES = [ROLE_ADMIN, ROLE_TEKNISI]


class UserService:

    async def _require_boss(self, current_user: User):
#        """Hanya boss (role_id=1) yang boleh manage user."""
#       if current_user.role_id != ROLE_BOSS:
        """Hanya boss (role_id=1) atau admin (role_id=2) yang boleh manage user."""
        # Izinkan ROLE_BOSS (1) ATAU ROLE_ADMIN (2)
        if current_user.role_id not in [ROLE_BOSS, ROLE_ADMIN]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Hanya boss yang dapat mengelola anggota tim"
            )

    async def get_all_roles(self, db: AsyncSession) -> list:
        result = await db.execute(select(Role))
        return result.scalars().all()

    async def get_company_users(self, db: AsyncSession, current_user: User) -> list:
        """List semua user dalam company yang sama."""
        result = await db.execute(
            select(User).where(User.company_id == current_user.company_id)
        )
        return result.scalars().all()

    async def invite_user(self, db: AsyncSession, payload: InviteUserRequest, current_user: User) -> User:
        """Boss mengundang user baru ke company."""
        await self._require_boss(current_user)

        if payload.role_id not in INVITABLE_ROLES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Role tidak valid. Hanya admin (2) dan teknisi (3) yang dapat diundang"
            )

        # Cek email sudah dipakai
        existing = await db.execute(select(User).where(User.email == payload.email))
        if existing.scalar_one_or_none():
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email sudah terdaftar")

        user = User(
            name=payload.name,
            email=payload.email,
            password=hash_password(payload.password),
            role_id=payload.role_id,
            company_id=current_user.company_id,
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user

    async def update_user(self, db: AsyncSession, user_id: uuid.UUID, payload: UpdateUserRequest, current_user: User) -> User:
        """Boss update data user dalam company-nya."""
        await self._require_boss(current_user)

        user = await self._get_user_in_company(db, user_id, current_user)

        if payload.role_id is not None and payload.role_id not in INVITABLE_ROLES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Role tidak valid"
            )

        for field, value in payload.model_dump(exclude_unset=True).items():
            setattr(user, field, value)

        await db.commit()
        await db.refresh(user)
        return user

    async def remove_user(self, db: AsyncSession, user_id: uuid.UUID, current_user: User) -> dict:
        """Boss menghapus user dari company."""
        await self._require_boss(current_user)

        user = await self._get_user_in_company(db, user_id, current_user)

        # Boss tidak bisa hapus diri sendiri
        if user.id == current_user.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Tidak bisa menghapus akun sendiri"
            )

        await db.delete(user)
        await db.commit()
        return {"message": f"User {user.name} berhasil dihapus dari company"}

    async def _get_user_in_company(self, db: AsyncSession, user_id: uuid.UUID, current_user: User) -> User:
        result = await db.execute(
            select(User).where(User.id == user_id, User.company_id == current_user.company_id)
        )
        user = result.scalar_one_or_none()
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User tidak ditemukan")
        return user


user_service = UserService()