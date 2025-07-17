import os
import pytest
from src.core.utils import parser
import re

TEST_PDF_PATH = os.path.join(os.path.dirname(__file__), '../../data/test/test_01.pdf')

@pytest.fixture(scope="module")
def sample_pdf_path():
    assert os.path.exists(TEST_PDF_PATH), f"Test PDF not found at {TEST_PDF_PATH}"
    return TEST_PDF_PATH

def test_extract_text_from_pdf(sample_pdf_path):
    text = parser.extract_text_from_pdf(sample_pdf_path)
    assert isinstance(text, str)
    assert len(text) > 0, "Extracted text should not be empty."
    # Optionally, check for known content if you know what's in the test PDF

def test_chunk_text_basic():
    text = "This is a test. " * 100  # 1700 chars
    chunk_size = 100
    chunks = parser.chunk_text(text, chunk_size)
    assert isinstance(chunks, list)
    assert all(isinstance(chunk, str) for chunk in chunks)
    assert all(len(chunk) <= chunk_size for chunk in chunks)
    assert ''.join(chunks).replace(' ', '') == text.replace(' ', '')  # No data loss

def test_chunk_text_edge_cases():
    # Empty string
    assert parser.chunk_text('', 100) == []
    # Chunk size larger than text
    assert parser.chunk_text('short text', 100) == ['short text']
    # Exact chunk size
    assert parser.chunk_text('a'*100, 100) == ['a'*100] 

def test_chunk_text_context_aware_basic():
    text = "This is sentence one. This is sentence two. This is sentence three. This is sentence four. This is sentence five."
    # Use a small max_words to force multiple chunks
    chunks = parser.chunk_text_context_aware(text, max_words=5, overlap=1)
    assert isinstance(chunks, list)
    assert all(isinstance(chunk, str) for chunk in chunks)
    # Each chunk should not exceed 5 words (except possibly the last)
    for chunk in chunks:
        assert len(chunk.split()) <= 5 + 5  # allow for overlap
    # Chunks should start/end at sentence boundaries
    for chunk in chunks:
        assert chunk.strip().endswith('.')
    # Overlap: last sentence of previous chunk should be first of next (if enough sentences)
    if len(chunks) > 1:
        def get_sentences(chunk):
            # Split on period, remove empty, and strip
            return [s.strip() for s in re.split(r'\.(?=\s|$)', chunk) if s.strip()]
        prev_sentences = get_sentences(chunks[0])
        next_sentences = get_sentences(chunks[1])
        assert prev_sentences[-1] == next_sentences[0]


def test_chunk_text_context_aware_edge_cases():
    # Empty string
    assert parser.chunk_text_context_aware('', max_words=5) == []
    # One sentence only
    assert parser.chunk_text_context_aware('Just one sentence.', max_words=5) == ['Just one sentence.']
    # Large max_words (should be one chunk)
    text = "Sentence one. Sentence two. Sentence three."
    chunks = parser.chunk_text_context_aware(text, max_words=100)
    assert len(chunks) == 1
    assert 'Sentence one.' in chunks[0]
    assert 'Sentence two.' in chunks[0]
    assert 'Sentence three.' in chunks[0] 