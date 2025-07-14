from fastapi import APIRouter, UploadFile, File, Form, HTTPException, status
from fastapi.responses import JSONResponse
from features.models.pydantic.upload import PDFUploadMetadata, PDFUploadResponse
from typing import Optional
import shutil
import os
import uuid

router = APIRouter()

UPLOAD_DIR = "data/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/upload", response_model=PDFUploadResponse)
async def upload_pdf(
    file: UploadFile = File(...),
    title: str = Form(...),
    description: Optional[str] = Form(None),
    tags: Optional[str] = Form(None)  # comma-separated tags
):
    # Validate file type
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only PDF files are allowed.")

    # Parse tags
    tag_list = [t.strip() for t in tags.split(",")] if tags else []

    # Save file to disk (or cloud, etc.)
    document_id = str(uuid.uuid4())
    save_path = os.path.join(UPLOAD_DIR, f"{document_id}_{file.filename}")
    with open(save_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Here you could trigger PDF parsing, chunking, embedding, etc.
    # For now, just return a success response
    return PDFUploadResponse(
        filename=file.filename,
        status="success",
        message="File uploaded successfully.",
        document_id=document_id
    )
