from fastapi import APIRouter, UploadFile, File, Form, HTTPException, status, Query, Body
from fastapi.responses import JSONResponse
from features.models.pydantic.upload import PDFUploadMetadata, PDFUploadResponse
from typing import Optional, List
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
            model=os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small"),
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

@router.get("/qdrant/documents")
async def get_all_documents_id(collection_name: str = Query(..., description="Qdrant collection name")):
    """
    Get all document IDs from a Qdrant collection.
    """
    try:
        qdrant_client = QdrantMemoryClient(collection_name=collection_name, qdrant_url=os.getenv("QDRANT_URL", "http://localhost:6333"))
        await qdrant_client.connect()
        # Assume document_id is stored in payload["metadata"]["document_id"]
        points = await qdrant_client.get_all_points()
        document_ids = set()
        for point in points:
            doc_id = point.payload.get("metadata", {}).get("document_id")
            if doc_id:
                document_ids.add(doc_id)
        return {"document_ids": list(document_ids)}
    except Exception as e:
        logger.error(f"Error fetching document IDs from Qdrant: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch document IDs: {e}")

@router.delete("/qdrant/documents")
async def clean_all_documents_id_array(
    collection_name: str = Body(..., embed=True, description="Qdrant collection name"),
    document_ids: List[str] = Body(..., embed=True, description="Array of document IDs to delete")
):
    """
    Delete all documents in Qdrant with the given document_ids from the specified collection.
    """
    try:
        qdrant_client = QdrantMemoryClient(collection_name=collection_name, qdrant_url=os.getenv("QDRANT_URL", "http://localhost:6333"))
        await qdrant_client.connect()
        # Find all point IDs for the given document_ids
        points = await qdrant_client.get_all_points()
        to_delete = []
        for point in points:
            doc_id = point.payload.get("metadata", {}).get("document_id")
            if doc_id in document_ids:
                to_delete.append(point.id)
        if to_delete:
            await qdrant_client.delete_points(to_delete)
        return {"deleted_point_ids": to_delete, "count": len(to_delete)}
    except Exception as e:
        logger.error(f"Error deleting documents from Qdrant: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to delete documents: {e}")
