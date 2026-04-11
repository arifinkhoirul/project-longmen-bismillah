import uuid
import os
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status

from app.models.land import Land
from app.models.pond import Pond
from app.models.user import User
from app.schemas.land import LandCreate, LandUpdate, LandResponse, PondCreate, PondUpdate, PondResponse
from sqlalchemy.orm import selectinload


class LandService:

    # ── Lands ──────────────────────────────────────────────

    async def get_all_lands(self, db: AsyncSession, current_user: User) -> list[LandResponse]:
        result = await db.execute(
            select(Land).where(Land.company_id == current_user.company_id)
        )
        return result.scalars().all()

    async def get_land(self, db: AsyncSession, land_id: uuid.UUID, current_user: User) -> LandResponse:
        land = await self._get_land_or_404(db, land_id, current_user)
        return land

    async def create_land(self, db: AsyncSession, payload: LandCreate, current_user: User) -> LandResponse:
        land = Land(
            company_id=current_user.company_id,
            name=payload.name,
            width=payload.width,
            length=payload.length,
            total_area=payload.total_area,
            image_url=payload.image_url,
        )
        db.add(land)
        await db.commit()
        await db.refresh(land)
        return land

    async def update_land(self, db: AsyncSession, land_id: uuid.UUID, payload: LandUpdate, current_user: User) -> LandResponse:
        land = await self._get_land_or_404(db, land_id, current_user)
        for field, value in payload.model_dump(exclude_unset=True).items():
            setattr(land, field, value)
        await db.commit()
        await db.refresh(land)
        return land

    # async def delete_land(self, db: AsyncSession, land_id: uuid.UUID, current_user: User) -> dict:
    #     land = await self._get_land_or_404(db, land_id, current_user)
    #     await db.delete(land)
    #     await db.commit()
    #     return {"message": "Land berhasil dihapus"}

    async def delete_land(self, db: AsyncSession, land_id: uuid.UUID, current_user: User) -> dict:
        # 1. Ambil data land dengan selectinload (Bungkus dengan kurung agar tidak syntax error)
        result = await db.execute(
            select(Land)
            .options(selectinload(Land.ponds))
            .where(Land.id == land_id, Land.company_id == current_user.company_id)
        )
        land = result.scalar_one_or_none()
        
        if not land:
            raise HTTPException(status_code=404, detail="Land tidak ditemukan")

        # 2. List semua path gambar yang perlu dihapus
        paths_to_delete = []
        if land.image_url:
            paths_to_delete.append(land.image_url)
        
        # Iterasi ponds karena sudah di-load menggunakan selectinload
        for pond in land.ponds:
            if pond.image_url:
                paths_to_delete.append(pond.image_url)

        # 3. Hapus data dari Database
        await db.delete(land)
        await db.commit()

        # 4. File Cleanup: Hapus file fisik dari folder uploads
        for path in paths_to_delete:
            relative_path = path.lstrip('/')
            try:
                if os.path.exists(relative_path):
                    os.remove(relative_path)
                    print(f"File cleanup success: {relative_path}")
            except Exception as e:
                print(f"File cleanup failed for {relative_path}: {e}")

        return {"message": "Land dan semua file terkait berhasil dihapus"}
        # 1. Tarik data secara manual dengan selectinload (Eager Loading)
        # Pastikan tanda kurung ( ) membungkus seluruh select untuk menyambung baris
        result = await db.execute(
            select(Land)
            .options(selectinload(Land.ponds))
            .where(Land.id == land_id, Land.company_id == current_user.company_id)
        )
        land = result.scalar_one_or_none()
        
        if not land:
            raise HTTPException(status_code=404, detail="Land tidak ditemukan")

        # 2. List semua path gambar yang perlu dihapus
        paths_to_delete = []
        if land.image_url:
            paths_to_delete.append(land.image_url)
        
        for pond in land.ponds:
            if pond.image_url:
                paths_to_delete.append(pond.image_url)

        # 3. Hapus data dari Database
        await db.delete(land)
        await db.commit()

        # 4. Cleanup: Hapus file fisik dari folder uploads
        for path in paths_to_delete:
            relative_path = path.lstrip('/')
            try:
                if os.path.exists(relative_path):
                    os.remove(relative_path)
                    print(f"File cleanup success: {relative_path}")
            except Exception as e:
                print(f"File cleanup failed for {relative_path}: {e}")

        return {"message": "Land dan semua file terkait berhasil dihapus"}

    async def _get_land_or_404(self, db: AsyncSession, land_id: uuid.UUID, current_user: User) -> Land:
        # Versi standar tanpa selectinload agar dashboard tidak blank/berat
        result = await db.execute(
            select(Land).where(Land.id == land_id, Land.company_id == current_user.company_id)
        )
        land = result.scalar_one_or_none()
        if not land:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Land tidak ditemukan")
        return land

    # ── Ponds ──────────────────────────────────────────────

    async def get_all_ponds(self, db: AsyncSession, land_id: uuid.UUID, current_user: User) -> list[PondResponse]:
        await self._get_land_or_404(db, land_id, current_user)
        result = await db.execute(
            select(Pond).where(Pond.land_id == land_id)
        )
        return result.scalars().all()

    async def get_pond(self, db: AsyncSession, land_id: uuid.UUID, pond_id: uuid.UUID, current_user: User) -> PondResponse:
        return await self._get_pond_or_404(db, land_id, pond_id, current_user)

    async def create_pond(self, db: AsyncSession, land_id: uuid.UUID, payload: PondCreate, current_user: User) -> PondResponse:
        await self._get_land_or_404(db, land_id, current_user)
        pond = Pond(
            land_id=land_id,
            name=payload.name,
            width=payload.width,
            length=payload.length,
            area=payload.area,
            image_url=payload.image_url,
        )
        db.add(pond)
        await db.commit()
        await db.refresh(pond)
        return pond

    async def update_pond(self, db: AsyncSession, land_id: uuid.UUID, pond_id: uuid.UUID, payload: PondUpdate, current_user: User) -> PondResponse:
        pond = await self._get_pond_or_404(db, land_id, pond_id, current_user)
        for field, value in payload.model_dump(exclude_unset=True).items():
            setattr(pond, field, value)
        await db.commit()
        await db.refresh(pond)
        return pond

    # async def delete_pond(self, db: AsyncSession, land_id: uuid.UUID, pond_id: uuid.UUID, current_user: User) -> dict:
    #     pond = await self._get_pond_or_404(db, land_id, pond_id, current_user)
    #     await db.delete(pond)
    #     await db.commit()
    #     return {"message": "Pond berhasil dihapus"}

    async def delete_pond(self, db: AsyncSession, land_id: uuid.UUID, pond_id: uuid.UUID, current_user: User) -> dict:
        # 1. Ambil data pond sebelum dihapus
        pond = await self._get_pond_or_404(db, land_id, pond_id, current_user)
        
        # 2. Simpan path gambarnya ke variabel sementara
        image_path = pond.image_url

        # 3. Hapus data dari Database
        await db.delete(pond)
        await db.commit()

        # 4. File Cleanup: Hapus file fisik jika path-nya ada
        if image_path:
            # Bersihkan '/' di awal path agar sesuai dengan path folder di server
            relative_path = os.path.join(os.getcwd(), path.lstrip('/'))
            try:
                if os.path.exists(relative_path):
                    os.remove(relative_path)
                    print(f"File cleanup success: {relative_path}")
            except Exception as e:
                # Kita gunakan try-except supaya kalau gagal hapus file, 
                # user tidak dapat error 500 (karena data di DB sudah berhasil terhapus)
                print(f"Gagal menghapus file fisik {relative_path}: {e}")

        return {"message": "Pond dan file gambar berhasil dihapus"}

    async def _get_pond_or_404(self, db: AsyncSession, land_id: uuid.UUID, pond_id: uuid.UUID, current_user: User) -> Pond:
        await self._get_land_or_404(db, land_id, current_user)
        result = await db.execute(
            select(Pond).where(Pond.id == pond_id, Pond.land_id == land_id)
        )
        pond = result.scalar_one_or_none()
        if not pond:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pond tidak ditemukan")
        return pond


land_service = LandService()