import io
import tempfile
import pytest
from flask import url_for
from src.webapp import app
from pathlib import Path

def test_webapp_upload_txt(monkeypatch, tmp_path):
    client = app.test_client()
    # Patch language model and cleaner to avoid heavy download
    monkeypatch.setattr('src.webapp.download_language_model', lambda: None)
    class DummyCleaner:
        def clean_text(self, text):
            return ["Cleaned text"]
        def filter_english(self, lines):
            return lines
    monkeypatch.setattr('src.webapp.TextCleaner', lambda lang_model=None: DummyCleaner())
    # Create a dummy file
    data = {
        'file': (io.BytesIO(b"This is a test PDF content."), 'test.pdf')
    }
    # Ensure output directory exists and create dummy cleaned file in src/output/cleaned_texts
    cleaned_dir = Path("src/output/cleaned_texts")
    cleaned_dir.mkdir(parents=True, exist_ok=True)
    cleaned_path = cleaned_dir / "test_cleaned.txt"
    cleaned_path.write_text("Cleaned text")
    response = client.post('/', data=data, content_type='multipart/form-data')
    assert response.status_code == 200
    assert b"Cleaned text" in response.data

def test_webapp_upload_fail(monkeypatch):
    client = app.test_client()
    # Patch everything to force fail
    monkeypatch.setattr('src.webapp.download_language_model', lambda: None)
    class DummyCleaner:
        def clean_text(self, text):
            return []
        def filter_english(self, lines):
            return []
    monkeypatch.setattr('src.webapp.TextCleaner', lambda lang_model=None: DummyCleaner())
    data = {
        'file': (io.BytesIO(b""), 'empty.pdf')
    }
    response = client.post('/', data=data, content_type='multipart/form-data')
    assert response.status_code == 500
    assert b"Processing failed" in response.data
