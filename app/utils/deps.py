import uuid
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.security import decode_token
from app.db.database import get_db
from app.models.user import User

bearer_scheme = HTTPBearer()

# ── Role constants ─────────────────────────────────────────
ROLE_BOSS = 1
ROLE_ADMIN = 2
ROLE_TEKNISI = 3


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    payload = decode_token(credentials.credentials)
    if not payload or payload.get("type") != "access":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token tidak valid atau expired")
    user_id = payload.get("sub")
    result = await db.execute(select(User).where(User.id == uuid.UUID(user_id)))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User tidak ditemukan")
    return user


def require_roles(*role_ids: int):
    """Dependency factory — batasi akses berdasarkan role."""
    async def _check(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role_id not in role_ids:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Akses ditolak. Role kamu tidak memiliki izin untuk tindakan ini"
            )
        return current_user
    return _check


# ── Shortcut dependencies ──────────────────────────────────
def boss_only():
    return require_roles(ROLE_BOSS)

def boss_or_admin():
    return require_roles(ROLE_BOSS, ROLE_ADMIN)

def all_roles():
    return require_roles(ROLE_BOSS, ROLE_ADMIN, ROLE_TEKNISI)