import io
import os
from fastapi.testclient import TestClient
from src.main import app
from unittest.mock import patch, AsyncMock
import pytest
import json

TEST_PDF_PATH = 'data/test/test_01.pdf'
UPLOAD_DIR = 'data/uploads'

# Use the correct endpoint path based on router inclusion
QDRANT_DOCS_PATH = "/qdrant/documents"  # Change to "/upload/qdrant/documents" if router is included with prefix

def make_fake_points(ids):
    class FakePoint:
        def __init__(self, id, doc_id):
            self.id = id
            self.payload = {"metadata": {"document_id": doc_id}}
    return [FakePoint(i, doc_id) for i, doc_id in enumerate(ids)]

def test_get_all_documents_id():
    from src.main import app
    client = TestClient(app)
    with patch('core.qdrant_client.QdrantMemoryClient.get_all_points', new_callable=AsyncMock) as mock_get_all_points, \
         patch('core.qdrant_client.QdrantMemoryClient.connect', new_callable=AsyncMock):
        # Simulate points with document_ids
        mock_get_all_points.return_value = make_fake_points(["doc1", "doc2", "doc1"])
        response = client.get(QDRANT_DOCS_PATH + "?collection_name=test_collection")
        assert response.status_code == 200
        data = response.json()
        assert set(data["document_ids"]) == {"doc1", "doc2"}

def test_clean_all_documents_id_array():
    from src.main import app
    client = TestClient(app)
    with patch('core.qdrant_client.QdrantMemoryClient.get_all_points', new_callable=AsyncMock) as mock_get_all_points, \
         patch('core.qdrant_client.QdrantMemoryClient.connect', new_callable=AsyncMock), \
         patch('core.qdrant_client.QdrantMemoryClient.delete_points', new_callable=AsyncMock) as mock_delete_points:
        # Simulate points with document_ids
        points = make_fake_points(["doc1", "doc2", "doc3"])
        points[0].id = 101
        points[1].id = 102
        points[2].id = 103
        mock_get_all_points.return_value = points
        mock_delete_points.return_value = None
        payload = {"collection_name": "test_collection", "document_ids": ["doc1", "doc3"]}
        response = client.request(
            "DELETE",
            QDRANT_DOCS_PATH,
            data=json.dumps(payload),
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 200
        data = response.json()
        assert set(data["deleted_point_ids"]) == {101, 103}
        assert data["count"] == 2

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