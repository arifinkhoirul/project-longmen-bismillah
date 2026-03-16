import uuid
import os
import aiofiles
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from fastapi.staticfiles import StaticFiles

from app.utils.deps import get_current_user
from app.models.user import User

router = APIRouter(prefix="/upload", tags=["Upload"])

UPLOAD_DIR = "uploads"
ALLOWED_TYPES = {"image/jpeg", "image/png", "image/webp"}
MAX_SIZE = 5 * 1024 * 1024  # 5MB

os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/image")
async def upload_image(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
):
    """Upload gambar dan return URL-nya."""
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(status_code=400, detail="Hanya file JPG, PNG, atau WebP yang diizinkan")

    content = await file.read()
    if len(content) > MAX_SIZE:
        raise HTTPException(status_code=400, detail="Ukuran file maksimal 5MB")

    # Generate unique filename
    ext = file.filename.split(".")[-1].lower()
    filename = f"{uuid.uuid4()}.{ext}"
    filepath = os.path.join(UPLOAD_DIR, filename)

    async with aiofiles.open(filepath, "wb") as f:
        await f.write(content)

    return {"url": f"/uploads/{filename}", "filename": filename}