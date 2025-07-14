from pydantic import BaseModel, Field
from typing import Optional

class PDFUploadMetadata(BaseModel):
    title: str = Field(..., description="Title of the PDF document")
    description: Optional[str] = Field(None, description="Description of the PDF document")
    tags: Optional[list[str]] = Field(default_factory=list, description="Tags for the document")

class PDFUploadResponse(BaseModel):
    filename: str
    status: str
    message: Optional[str] = None
    document_id: Optional[str] = None
