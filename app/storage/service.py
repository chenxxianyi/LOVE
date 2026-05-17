"""
Storage service for file uploads.
"""
import os
import uuid
from pathlib import Path
from typing import Optional

from fastapi import UploadFile

from app.core.config import settings


class StorageService:
    """Local file storage service."""

    def __init__(self):
        self.upload_dir = settings.upload_dir_path
        self.base_url = settings.PUBLIC_BASE_URL
        self.max_size = settings.max_upload_size_bytes

    def _ensure_upload_dir(self):
        """Ensure upload directory exists."""
        self.upload_dir.mkdir(parents=True, exist_ok=True)

    def _generate_filename(self, original_filename: str) -> str:
        """Generate a unique filename."""
        ext = Path(original_filename).suffix or ""
        unique_id = uuid.uuid4().hex
        return f"{unique_id}{ext}"

    async def save_file(self, file: UploadFile) -> str:
        """
        Save an uploaded file and return its URL.
        Raises ValueError if file is too large.
        """
        self._ensure_upload_dir()

        # Check file size
        content = await file.read()
        if len(content) > self.max_size:
            raise ValueError(f"File size exceeds maximum of {settings.MAX_UPLOAD_SIZE_MB}MB")

        # Generate unique filename
        filename = self._generate_filename(file.filename)
        file_path = self.upload_dir / filename

        # Write file
        with open(file_path, "wb") as buffer:
            buffer.write(content)

        # Return URL
        return f"{self.base_url}/uploads/{filename}"

    def delete_file(self, url: str) -> bool:
        """Delete a file by its URL."""
        try:
            # Extract filename from URL
            filename = url.split("/uploads/")[-1]
            file_path = self.upload_dir / filename

            if file_path.exists():
                file_path.unlink()
                return True
            return False
        except Exception:
            return False

    def get_file_path(self, filename: str) -> Optional[Path]:
        """Get the full path for a filename."""
        file_path = self.upload_dir / filename
        if file_path.exists() and file_path.is_relative_to(self.upload_dir):
            return file_path
        return None


# Global storage instance
storage_service = StorageService()