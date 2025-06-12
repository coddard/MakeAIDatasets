import pytest
from src.main import download_language_model

def test_download_language_model(monkeypatch, tmp_path):
    # Patch LANG_MODEL_PATH to a temp file
    from src import main
    monkeypatch.setattr(main, "LANG_MODEL_PATH", tmp_path / "dummy.ftz")
    # Patch requests.get to simulate download
    class DummyResponse:
        def __init__(self):
            self.status_code = 200
        def raise_for_status(self):
            pass
        def iter_content(self, chunk_size=8192):
            yield b"dummy model content"
    monkeypatch.setattr("requests.get", lambda *a, **k: DummyResponse())
    # Patch FastText.load_model to simulate loading
    import fasttext
    monkeypatch.setattr(fasttext.FastText, "load_model", lambda path: "dummy_model")
    model = download_language_model()
    assert model == "dummy_model"
