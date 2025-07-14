import io
import os
from fastapi.testclient import TestClient
from src.main import app

def test_upload_pdf(tmp_path):
    client = TestClient(app)
    # Create a dummy PDF file in memory
    pdf_content = b'%PDF-1.4 test pdf content'
    files = {
        'file': ('test.pdf', io.BytesIO(pdf_content), 'application/pdf'),
    }
    data = {
        'title': 'Test PDF',
        'description': 'A test PDF file',
        'tags': 'test,example,upload'
    }
    response = client.post("/upload", files=files, data=data)
    assert response.status_code == 200
    resp_json = response.json()
    assert resp_json['filename'] == 'test.pdf'
    assert resp_json['status'] == 'success'
    assert resp_json['document_id']
    # Check file was saved
    upload_dir = 'data/uploads'
    files_in_dir = os.listdir(upload_dir)
    assert any(resp_json['document_id'] in fname for fname in files_in_dir) 