"""
Media endpoints - file uploads and asset management.
"""
from typing import List

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from pydantic import BaseModel

from app.db import get_db
from app.storage.service import storage_service

router = APIRouter()


# Pydantic Schemas
class MediaUploadResponse(BaseModel):
    url: str
    filename: str
    size: int


class MediaAssetResponse(BaseModel):
    id: str
    url: str
    filename: str
    size: int
    mimeType: str


@router.post("/upload", response_model=MediaUploadResponse)
async def upload_file(file: UploadFile = File(...)):
    """Upload a file and return its URL."""
    try:
        url = await storage_service.save_file(file)

        # Get file size from content
        content = await file.read()
        size = len(content)

        # Extract filename from URL
        filename = url.split("/")[-1]

        return MediaUploadResponse(
            url=url,
            filename=filename,
            size=size
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/upload-multiple", response_model=List[MediaUploadResponse])
async def upload_multiple_files(files: List[UploadFile] = File(...)):
    """Upload multiple files."""
    results = []
    for file in files:
        try:
            url = await storage_service.save_file(file)
            content = await file.read()

            results.append(MediaUploadResponse(
                url=url,
                filename=url.split("/")[-1],
                size=len(content)
            ))
        except Exception as e:
            continue  # Skip failed uploads

    return results


@router.delete("/{url:path}")
def delete_file(url: str):
    """Delete a file by its URL."""
    success = storage_service.delete_file(url)
    if not success:
        raise HTTPException(status_code=404, detail="File not found")

    return {"success": True}