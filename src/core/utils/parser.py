import os
from typing import List

try:
    from PyPDF2 import PdfReader
except ImportError:
    PdfReader = None

from PyPDF2.errors import PdfReadError

def extract_text_from_pdf(pdf_path: str) -> str:
    """
    Extract all text from a PDF file at the given path.
    """
    if PdfReader is None:
        raise ImportError("PyPDF2 is required for PDF parsing. Please install it.")
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")
    try:
        reader = PdfReader(pdf_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""
        return text.strip()
    except PdfReadError as e:
        raise ValueError(f"Failed to read PDF: {e}")

def chunk_text(text: str, chunk_size: int) -> List[str]:
    """
    Split text into chunks of at most chunk_size, preserving word boundaries where possible.
    """
    if not text:
        return []
    words = text.split()
    chunks = []
    current_chunk = ""
    for word in words:
        if len(current_chunk) + len(word) + 1 > chunk_size:
            if current_chunk:
                chunks.append(current_chunk.strip())
            current_chunk = word
        else:
            if current_chunk:
                current_chunk += " "
            current_chunk += word
    if current_chunk:
        chunks.append(current_chunk.strip())
    return chunks
