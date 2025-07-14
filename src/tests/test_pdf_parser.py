import os
import pytest
from src.core.utils import parser

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