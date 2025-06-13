from pathlib import Path
import mimetypes

def detect_file_type(file_path: Path) -> str:
    """Returns the file type based on extension and mime type."""
    mime, _ = mimetypes.guess_type(str(file_path))
    ext = file_path.suffix.lower()
    if ext == ".pdf" or (mime and "pdf" in mime):
        return "pdf"
    if ext == ".epub" or (mime and "epub" in mime):
        return "epub"
    if ext == ".txt" or (mime and "text" in mime):
        return "txt"
    if ext == ".docx" or (mime and "word" in mime):
        return "docx"
    if ext == ".html" or ext == ".htm" or (mime and "html" in mime):
        return "html"
    return "unknown"
