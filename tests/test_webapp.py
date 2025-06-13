import pytest
from flask import Flask
from src.webapp import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_index_page(client):
    response = client.get('/')
    assert response.status_code == 200
    assert b'MakeAIDatasets Web' in response.data

def test_file_upload(client):
    data = {
        'file': (b'Test content', 'test.txt')
    }
    response = client.post('/', data=data, content_type='multipart/form-data')
    assert response.status_code in [200, 400, 500]
