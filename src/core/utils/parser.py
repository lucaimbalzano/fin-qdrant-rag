import os
from typing import List

try:
    from PyPDF2 import PdfReader
except ImportError:
    PdfReader = None

from PyPDF2.errors import PdfReadError

try:
    import spacy
    _spacy_nlp = spacy.blank("en")
    _spacy_nlp.add_pipe("sentencizer")
except ImportError:
    spacy = None
    _spacy_nlp = None


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


def chunk_text_context_aware(text: str, max_words: int = 200, overlap: int = 1) -> List[str]:
    """
    Split text into context-aware chunks using sentence boundaries (via spaCy).
    Each chunk will have up to max_words words, and optionally overlap with the previous chunk by N sentences.
    If spaCy is not available, falls back to naive chunking.
    """
    if not text:
        return []
    if not spacy or not _spacy_nlp:
        # Fallback to naive chunking
        return chunk_text(text, chunk_size=max_words * 5)  # crude estimate
    # Use spaCy to split into sentences
    doc = _spacy_nlp(text)
    sentences = [sent.text.strip() for sent in doc.sents if sent.text.strip()]
    chunks = []
    current_chunk = []
    current_len = 0
    i = 0
    while i < len(sentences):
        sent = sentences[i]
        sent_words = len(sent.split())
        if current_len + sent_words > max_words and current_chunk:
            # Finish current chunk
            chunks.append(" ".join(current_chunk))
            # Start new chunk with overlap
            overlap_sents = current_chunk[-overlap:] if overlap > 0 else []
            current_chunk = list(overlap_sents)
            current_len = sum(len(s.split()) for s in current_chunk)
        current_chunk.append(sent)
        current_len += sent_words
        i += 1
    if current_chunk:
        chunks.append(" ".join(current_chunk))
    return chunks
