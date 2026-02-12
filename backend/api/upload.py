"""
Upload API — Document upload endpoint.
POST /api/upload
"""

import os
import uuid
from datetime import datetime

import structlog
from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from models.schemas import (
    DocumentUpload,
    FileType,
    ProcessingStatus,
    UploadResponse,
)

logger = structlog.get_logger()
router = APIRouter()

# Allowed file extensions and their FileType mapping
ALLOWED_EXTENSIONS = {
    ".pdf": FileType.PDF,
    ".docx": FileType.DOCX,
    ".xlsx": FileType.XLSX,
    ".csv": FileType.CSV,
    ".png": FileType.IMAGE,
    ".jpg": FileType.IMAGE,
    ".jpeg": FileType.IMAGE,
    ".tiff": FileType.IMAGE,
}

MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB


@router.post("/upload", response_model=list[UploadResponse])
async def upload_documents(
    files: list[UploadFile] = File(...),
    uploaded_by: str = Form(default="anonymous"),
    organization_id: str = Form(default="default"),
):
    """
    Upload financial documents for extraction (supports bulk).

    Accepts multiple PDF, DOCX, XLSX, CSV, and image files.
    Max file size per file: 50MB.
    """
    responses = []
    
    for file in files:
        try:
            # Validate file extension
            ext = os.path.splitext(file.filename or "")[1].lower()
            if ext not in ALLOWED_EXTENSIONS:
                responses.append(UploadResponse(
                    document_id="error",
                    filename=file.filename or "unknown",
                    status=ProcessingStatus.FAILED,
                    message=f"Unsupported file type: {ext}"
                ))
                continue

            # Read file content
            content = await file.read()
            file_size = len(content)

            # Validate file size
            if file_size > MAX_FILE_SIZE:
                responses.append(UploadResponse(
                    document_id="error",
                    filename=file.filename or "unknown",
                    status=ProcessingStatus.FAILED,
                    message=f"File too large: {file_size / 1024 / 1024:.1f}MB. Max: 50MB."
                ))
                continue

            # Generate document ID
            document_id = str(uuid.uuid4())

            # Store file locally
            upload_dir = os.path.join(os.path.dirname(__file__), "..", "..", ".tmp", "uploads")
            os.makedirs(upload_dir, exist_ok=True)
            file_path = os.path.join(upload_dir, f"{document_id}{ext}")

            with open(file_path, "wb") as f:
                f.write(content)

            logger.info(
                "Document uploaded",
                document_id=document_id,
                filename=file.filename,
                file_type=ext,
                size_bytes=file_size,
            )

            responses.append(UploadResponse(
                document_id=document_id,
                filename=file.filename or "unknown",
                status=ProcessingStatus.PENDING,
                message="Document uploaded successfully."
            ))

        except Exception as e:
            logger.error("Upload failed", filename=file.filename, error=str(e))
            responses.append(UploadResponse(
                document_id="error",
                filename=file.filename or "unknown",
                status=ProcessingStatus.FAILED,
                message=f"Internal error during upload: {str(e)}"
            ))

    return responses
