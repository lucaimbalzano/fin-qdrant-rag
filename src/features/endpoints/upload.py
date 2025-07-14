from fastapi import APIRouter, UploadFile, File, Form, HTTPException, status
from fastapi.responses import JSONResponse
from features.models.pydantic.upload import PDFUploadMetadata, PDFUploadResponse
from typing import Optional
import shutil
import os
import uuid
import logging

from core.utils.parser import extract_text_from_pdf, chunk_text
from core.utils.embedding import get_embeddings
from core.qdrant_client import QdrantMemoryClient

router = APIRouter()

UPLOAD_DIR = "data/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

logger = logging.getLogger("upload_endpoint")

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

    try:
        # 1. Extract text
        text = extract_text_from_pdf(save_path)
        if not text:
            raise ValueError("No text could be extracted from the PDF.")
        # 2. Chunk text
        chunks = chunk_text(text, chunk_size=1000)
        if not chunks:
            raise ValueError("No chunks generated from PDF text.")
        # 3. Get embeddings
        embeddings = get_embeddings(
            chunks,
            model=os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-ada-002"),
            api_key=os.getenv("OPENAI_API_KEY")
        )
        if len(embeddings) != len(chunks):
            raise ValueError("Mismatch between number of chunks and embeddings.")
        # 4. Store in Qdrant
        qdrant_client = QdrantMemoryClient.for_pdfs(qdrant_url=os.getenv("QDRANT_URL", "http://localhost:6333"))
        await qdrant_client.connect()
        await qdrant_client.create_collection()
        for chunk, embedding in zip(chunks, embeddings):
            await qdrant_client.store_memory_item(
                content=chunk,
                embedding=embedding,
                user_id="pdf_upload",  # Replace with real user ID if available
                memory_type="pdf_chunk",
                metadata={
                    "title": title,
                    "description": description,
                    "tags": tag_list,
                    "document_id": document_id,
                    "filename": file.filename
                }
            )
        logger.info(f"PDF {file.filename} processed and stored in Qdrant.")
    except Exception as e:
        logger.error(f"Error processing PDF: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to process PDF: {e}")

    return PDFUploadResponse(
        filename=file.filename,
        status="success",
        message="File uploaded and processed successfully.",
        document_id=document_id
    )
