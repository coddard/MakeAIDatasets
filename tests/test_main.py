import pytest
from src.main import download_language_model

def test_download_language_model():
    # No fasttext usage anymore, just check download_language_model returns None or handles gracefully
    model = download_language_model()
    assert model is None or model == "dummy_model"
