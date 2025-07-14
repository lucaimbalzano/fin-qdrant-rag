import io
import os
from fastapi.testclient import TestClient
from src.main import app
from unittest.mock import patch, AsyncMock

TEST_PDF_PATH = 'data/test/test_01.pdf'
UPLOAD_DIR = 'data/uploads'

@patch('core.qdrant_client.QdrantMemoryClient.connect', new_callable=AsyncMock)
@patch('core.qdrant_client.QdrantMemoryClient.create_collection', new_callable=AsyncMock)
@patch('core.qdrant_client.QdrantMemoryClient.store_memory_item', new_callable=AsyncMock)
@patch('core.utils.embedding.get_embeddings', return_value=[[0.1]*1536]*7)
def test_upload_pdf(mock_get_embeddings, mock_store_memory_item, mock_create_collection, mock_connect, tmp_path):
    client = TestClient(app)
    with open(TEST_PDF_PATH, 'rb') as f:
        pdf_content = f.read()
    files = {
        'file': ('test.pdf', io.BytesIO(pdf_content), 'application/pdf'),
    }
    data = {
        'title': 'Test PDF',
        'description': 'A test PDF file',
        'tags': 'test,example,upload'
    }
    uploaded_file_path = None
    try:
        response = client.post("/upload", files=files, data=data)
        assert response.status_code == 200
        resp_json = response.json()
        assert resp_json['filename'] == 'test.pdf'
        assert resp_json['status'] == 'success'
        assert resp_json['document_id']
        # Check that the file was created in the uploads directory
        files_in_dir = os.listdir(UPLOAD_DIR)
        uploaded_file_path = os.path.join(UPLOAD_DIR, resp_json['document_id'] + '_test.pdf')
        assert any(resp_json['document_id'] in fname for fname in files_in_dir)
        print("test is working /upload endpoint")
    finally:
        # Only delete the file created by this test
        if uploaded_file_path and os.path.exists(uploaded_file_path):
            os.remove(uploaded_file_path)

@patch('core.qdrant_client.QdrantMemoryClient.connect', new_callable=AsyncMock)
@patch('core.qdrant_client.QdrantMemoryClient.create_collection', new_callable=AsyncMock)
@patch('core.qdrant_client.QdrantMemoryClient.store_memory_item', new_callable=AsyncMock)
@patch('core.utils.embedding.get_embeddings', return_value=[[0.1]*1536]*7)
@patch('core.utils.parser.chunk_text', return_value=["chunk"]*7)
def test_upload_pdf_with_mocked_qdrant(mock_chunk_text, mock_get_embeddings, mock_store_memory_item, mock_create_collection, mock_connect, tmp_path):
    client = TestClient(app)
    with open(TEST_PDF_PATH, 'rb') as f:
        pdf_content = f.read()
    files = {
        'file': ('test.pdf', io.BytesIO(pdf_content), 'application/pdf'),
    }
    data = {
        'title': 'Test PDF',
        'description': 'A test PDF file',
        'tags': 'test,example,upload'
    }
    uploaded_file_path = None
    try:
        response = client.post("/upload", files=files, data=data)
        assert response.status_code == 200
        resp_json = response.json()
        assert resp_json['filename'] == 'test.pdf'
        assert resp_json['status'] == 'success'
        assert resp_json['document_id']
        # Check that the file was created in the uploads directory
        files_in_dir = os.listdir(UPLOAD_DIR)
        uploaded_file_path = os.path.join(UPLOAD_DIR, resp_json['document_id'] + '_test.pdf')
        assert any(resp_json['document_id'] in fname for fname in files_in_dir)
        # Assert store_memory_item called for each chunk
        assert mock_store_memory_item.await_count == 7
        print("test is working /upload endpoint with mocked qdrant")
    finally:
        # Only delete the file created by this test
        if uploaded_file_path and os.path.exists(uploaded_file_path):
            os.remove(uploaded_file_path) 