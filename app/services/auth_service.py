import uuid, secrets, httpx
from datetime import datetime, timedelta, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status
from app.models.user import User
from app.models.company import Company
from app.models.password_reset import PasswordReset
from app.schemas.auth import (
    RegisterRequest, LoginRequest, TokenResponse,
    RegisterResponse, UserResponse,
    ForgotPasswordRequest, ResetPasswordRequest, ChangePasswordRequest,
)
from app.core.security import hash_password, verify_password, create_access_token, create_refresh_token, decode_token
from app.core.config import settings


class AuthService:

    async def _verify_recaptcha(self, token: str) -> bool:
        """Verifikasi reCAPTCHA token ke Google."""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://www.google.com/recaptcha/api/siteverify",
                data={
                    "secret": settings.RECAPTCHA_SECRET_KEY,
                    "response": token,
                },
            )
            result = response.json()
            return result.get("success", False)

    async def register(self, db: AsyncSession, payload: RegisterRequest) -> RegisterResponse:
        existing = await db.execute(select(User).where(User.email == payload.email))
        if existing.scalar_one_or_none():
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email sudah terdaftar")

        user = User(
            name=payload.name,
            email=payload.email,
            password=hash_password(payload.password),
            role_id=1,  # Boss
        )
        db.add(user)
        await db.flush()

        company = Company(
            name=payload.company_name,
            email=payload.company_email,
            phone=payload.company_phone,
            address=payload.company_address,
            owner_user_id=user.id,
        )
        db.add(company)
        await db.flush()

        user.company_id = company.id
        await db.commit()
        await db.refresh(user)

        return RegisterResponse(user=UserResponse.model_validate(user), tokens=self._tokens(user))

    async def login(self, db: AsyncSession, payload: LoginRequest) -> TokenResponse:
        # Verifikasi reCAPTCHA jika token dikirim
        if payload.recaptcha_token:
            is_valid = await self._verify_recaptcha(payload.recaptcha_token)
            if not is_valid:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Verifikasi CAPTCHA gagal, silakan coba lagi"
                )

        result = await db.execute(select(User).where(User.email == payload.email))
        user = result.scalar_one_or_none()
        if not user or not verify_password(payload.password, user.password):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Email atau password salah")
        return self._tokens(user)

    async def refresh_token(self, db: AsyncSession, refresh_token: str) -> TokenResponse:
        payload = decode_token(refresh_token)
        if not payload or payload.get("type") != "refresh":
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token tidak valid")
        result = await db.execute(select(User).where(User.id == uuid.UUID(payload["sub"])))
        user = result.scalar_one_or_none()
        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User tidak ditemukan")
        return self._tokens(user)

    async def get_me(self, current_user: User) -> UserResponse:
        return UserResponse.model_validate(current_user)

    async def forgot_password(self, db: AsyncSession, payload: ForgotPasswordRequest) -> dict:
        result = await db.execute(select(User).where(User.email == payload.email))
        user = result.scalar_one_or_none()
        if not user:
            return {"message": "Jika email terdaftar, link reset telah dikirim"}

        old = await db.execute(select(PasswordReset).where(PasswordReset.user_id == user.id))
        for t in old.scalars().all():
            await db.delete(t)

        token = secrets.token_urlsafe(32)
        db.add(PasswordReset(user_id=user.id, token=token, expired_at=datetime.now(timezone.utc) + timedelta(hours=1)))
        await db.commit()
        return {"message": "Reset token berhasil dibuat", "token": token}

    async def reset_password(self, db: AsyncSession, payload: ResetPasswordRequest) -> dict:
        result = await db.execute(select(PasswordReset).where(PasswordReset.token == payload.token))
        reset = result.scalar_one_or_none()
        if not reset:
            raise HTTPException(status_code=400, detail="Token tidak valid")
        if reset.expired_at < datetime.now(timezone.utc):
            await db.delete(reset)
            await db.commit()
            raise HTTPException(status_code=400, detail="Token sudah expired")
        result2 = await db.execute(select(User).where(User.id == reset.user_id))
        user = result2.scalar_one_or_none()
        user.password = hash_password(payload.new_password)
        await db.delete(reset)
        await db.commit()
        return {"message": "Password berhasil direset"}

    async def change_password(self, db: AsyncSession, current_user: User, payload: ChangePasswordRequest) -> dict:
        if not verify_password(payload.old_password, current_user.password):
            raise HTTPException(status_code=400, detail="Password lama salah")
        current_user.password = hash_password(payload.new_password)
        await db.commit()
        return {"message": "Password berhasil diubah"}

    def _tokens(self, user: User) -> TokenResponse:
        data = {"sub": str(user.id)}
        return TokenResponse(access_token=create_access_token(data), refresh_token=create_refresh_token(data))


auth_service = AuthService()