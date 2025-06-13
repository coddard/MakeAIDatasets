from flask import Flask, request, render_template_string, send_file, abort
from pathlib import Path
from src.main import process_single_file, TextCleaner, download_language_model
import os

app = Flask(__name__)

UPLOAD_FOLDER = "web_uploads"
Path(UPLOAD_FOLDER).mkdir(exist_ok=True)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        file = request.files["file"]
        if file:
            file_path = Path(UPLOAD_FOLDER) / file.filename
            file.save(file_path)
            lang_model = download_language_model()
            cleaner = TextCleaner(lang_model=lang_model) if lang_model else TextCleaner()
            process_single_file(file_path, cleaner)
            cleaned_path = Path("output/cleaned_texts") / f"{file_path.stem}_cleaned.txt"
            if cleaned_path.exists():
                return send_file(cleaned_path, as_attachment=True)
            return "Processing failed.", 500
    return render_template_string('''
        <h1>MakeAIDatasets Web</h1>
        <form method="post" enctype="multipart/form-data">
            <input type="file" name="file">
            <input type="submit" value="Upload and Clean">
        </form>
    ''')

@app.errorhandler(500)
def handle_500(e):
    return "Processing failed.", 500

if __name__ == "__main__":
    app.run(debug=True)
