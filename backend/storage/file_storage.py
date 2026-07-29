"""
ArogyaMitra AI — File Storage Service
Handles saving and retrieving uploaded reports and medical images.
"""

import os
import uuid
import aiofiles
from pathlib import Path
from fastapi import UploadFile, HTTPException, status
from backend.config import settings


class FileStorageService:
    """
    Async file storage backed by the local filesystem.
    Production environments can swap this for cloud object storage (S3, GCS).
    """

    def __init__(self, base_dir: str = settings.UPLOAD_DIR) -> None:
        self.base_dir = Path(base_dir)
        self._ensure_directories()

    def _ensure_directories(self) -> None:
        """Create the upload directory tree if it does not exist."""
        subdirs = ["reports", "images", "voice", "temp"]
        for subdir in subdirs:
            (self.base_dir / subdir).mkdir(parents=True, exist_ok=True)

    def _get_subdir(self, file_type: str) -> Path:
        """Map a logical file type to a storage subdirectory."""
        mapping = {
            "report": "reports",
            "image": "images",
            "voice": "voice",
        }
        subdir = mapping.get(file_type, "temp")
        return self.base_dir / subdir

    def _validate_file_type(self, file: UploadFile, allowed_types: list[str]) -> None:
        """Raise HTTP 415 if the content-type is not in the allowed list."""
        if file.content_type not in allowed_types:
            raise HTTPException(
                status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                detail=(
                    f"Unsupported file type '{file.content_type}'. "
                    f"Allowed: {', '.join(allowed_types)}"
                ),
            )

    def _validate_file_size(self, content: bytes) -> None:
        """Raise HTTP 413 if the file exceeds the configured size limit."""
        max_bytes = settings.MAX_FILE_SIZE_MB * 1024 * 1024
        if len(content) > max_bytes:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File exceeds the maximum size of {settings.MAX_FILE_SIZE_MB} MB.",
            )

    async def save_file(
        self,
        upload: UploadFile,
        file_type: str = "temp",
        allowed_types: list[str] | None = None,
    ) -> dict:
        """
        Save an uploaded file to disk.

        Args:
            upload: FastAPI UploadFile object.
            file_type: Logical category — 'report', 'image', 'voice', or 'temp'.
            allowed_types: List of permitted MIME types. If None, all types accepted.

        Returns:
            Dict with keys: file_path, file_name, content_type, size_bytes.
        """
        if allowed_types:
            self._validate_file_type(upload, allowed_types)

        content = await upload.read()
        self._validate_file_size(content)

        ext = Path(upload.filename or "file").suffix or ".bin"
        unique_name = f"{uuid.uuid4().hex}{ext}"
        subdir = self._get_subdir(file_type)
        dest = subdir / unique_name

        async with aiofiles.open(dest, "wb") as f:
            await f.write(content)

        return {
            "file_path": str(dest),
            "file_name": upload.filename or unique_name,
            "content_type": upload.content_type,
            "size_bytes": len(content),
        }

    def file_exists(self, file_path: str) -> bool:
        """Check whether a stored file still exists on disk."""
        return Path(file_path).exists()

    async def read_file_bytes(self, file_path: str) -> bytes:
        """
        Read a stored file as bytes.

        Raises:
            HTTPException(404): If the file does not exist.
        """
        path = Path(file_path)
        if not path.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"File not found: {file_path}",
            )
        async with aiofiles.open(path, "rb") as f:
            return await f.read()

    def delete_file(self, file_path: str) -> bool:
        """
        Delete a stored file.

        Returns:
            True if the file was deleted, False if it did not exist.
        """
        path = Path(file_path)
        if path.exists():
            path.unlink()
            return True
        return False


# Singleton instance
file_storage = FileStorageService()
