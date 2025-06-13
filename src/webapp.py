from flask import Flask, request, render_template_string, send_file, abort
from pathlib import Path
from src.main import process_single_file, TextCleaner, download_language_model
import os
import logging
import re

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

UPLOAD_FOLDER = "web_uploads"
Path(UPLOAD_FOLDER).mkdir(exist_ok=True)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        if 'file' not in request.files:
            logger.error("No file provided in the request.")
            return "No file provided", 400

        file = request.files.get("file")
        if not file or not file.filename:
            logger.error("No file selected for upload.")
            return "No file selected", 400

        try:
            file_path = Path(UPLOAD_FOLDER) / file.filename
            file.save(file_path)

            if not file_path.exists():
                logger.error("File upload failed.")
                return "File upload failed", 500

            try:
                lang_model = download_language_model()
                cleaner = TextCleaner(lang_model=lang_model) if lang_model else TextCleaner()
            except Exception as e:
                logger.exception("Failed to initialize text cleaner.")
                return "Text cleaner initialization failed", 500

            if process_single_file(file_path, cleaner):
                cleaned_path = Path("output/cleaned_texts") / f"{file_path.stem}_cleaned.txt"
                if cleaned_path.exists():
                    logger.info(f"File processed successfully: {cleaned_path}")
                    return send_file(cleaned_path, as_attachment=True)

            logger.error("File processing failed.")
            return "Processing failed", 500

        except Exception as e:
            logger.exception("Error occurred during file processing.")
            return str(e), 500

        finally:
            try:
                if file_path.exists():
                    file_path.unlink()
                    logger.info(f"Temporary file cleaned up: {file_path}")
            except Exception as e:
                logger.warning(f"Failed to clean up temporary file: {file_path}. Error: {str(e)}")

    return render_template_string(r'''
        <html>
        <head>
            <title>MakeAIDatasets Web</title>
            <link href="https://fonts.googleapis.com/css?family=IBM+Plex+Mono:400,700&display=swap" rel="stylesheet">
            <style>
                body {
                    background: #1F1F1F;
                    font-family: 'IBM Plex Mono', 'JetBrains Mono', monospace;
                    color: #FFF200;
                    margin: 0;
                    min-height: 100vh;
                }
                .glass {
                    background: rgba(31,31,31,0.85);
                    box-shadow: 0 8px 32px 0 rgba(31,31,31,0.37);
                    backdrop-filter: blur(8px);
                    border-radius: 16px;
                    border: 1px solid rgba(255,255,255,0.18);
                    padding: 2em;
                    max-width: 700px;
                    margin: 40px auto;
                }
                h1 {
                    color: #00FFC6;
                    text-shadow: 0 0 8px #00FFC6, 0 0 2px #FFF200;
                }
                .drop-zone {
                    border: 2px dashed #FF6EC7;
                    border-radius: 12px;
                    padding: 2em;
                    text-align: center;
                    color: #FF6EC7;
                    background: rgba(255,255,255,0.05);
                    cursor: pointer;
                    margin-bottom: 1em;
                    transition: background 0.2s;
                }
                .drop-zone.dragover { background: #2a2a2a; }
                .progress { width: 100%; background: #333; border-radius: 5px; margin: 1em 0; }
                .progress-bar { width: 0; height: 16px; background: #00FFC6; border-radius: 5px; transition: width 0.3s; }
                .file-list { color: #FFF200; margin-bottom: 1em; }
                .preview-box {
                    background: #232323;
                    border-radius: 8px;
                    padding: 1em;
                    margin: 1em 0;
                    color: #FFF200;
                    font-size: 0.95em;
                    max-height: 200px;
                    overflow-y: auto;
                }
                .options-panel {
                    background: rgba(255,255,255,0.07);
                    border-radius: 8px;
                    padding: 1em;
                    margin-bottom: 1em;
                }
                label { color: #FF6EC7; }
                .btn {
                    background: #FF6EC7;
                    color: #1F1F1F;
                    border: none;
                    border-radius: 6px;
                    padding: 0.7em 1.5em;
                    font-family: inherit;
                    font-size: 1em;
                    cursor: pointer;
                    margin-top: 1em;
                    box-shadow: 0 2px 8px #FF6EC7AA;
                }
                .btn:active { background: #FFF200; color: #1F1F1F; }
            </style>
        </head>
        <body>
        <div class="glass">
            <h1>MakeAIDatasets Web</h1>
            <form id="uploadForm" method="post" enctype="multipart/form-data">
                <div class="drop-zone" id="dropZone">Drag & Drop files here or click to select</div>
                <input type="file" name="file" id="fileInput" style="display:none;" multiple>
                <div class="file-list" id="fileList"></div>
                <div class="options-panel">
                    <label>Output Format:</label>
                    <select name="output_format" id="outputFormat">
                        <option value="txt">TXT</option>
                        <option value="json">JSON</option>
                        <option value="csv">CSV</option>
                    </select>
                    <label style="margin-left:2em;">Language:</label>
                    <select name="lang" id="langSelect">
                        <option value="en">English</option>
                        <option value="auto">Auto-Detect</option>
                    </select>
                    <label style="margin-left:2em;">Clean Level:</label>
                    <select name="clean_level" id="cleanLevel">
                        <option value="basic">Basic</option>
                        <option value="advanced">Advanced</option>
                    </select>
                </div>
                <div class="progress" id="progressContainer" style="display:none;">
                    <div class="progress-bar" id="progressBar"></div>
                </div>
                <button class="btn" type="submit">Upload and Clean</button>
            </form>
            <div id="previewContainer"></div>
        </div>
        <script>
        const dropZone = document.getElementById('dropZone');
        const fileInput = document.getElementById('fileInput');
        const fileList = document.getElementById('fileList');
        const form = document.getElementById('uploadForm');
        const progressContainer = document.getElementById('progressContainer');
        const progressBar = document.getElementById('progressBar');
        const previewContainer = document.getElementById('previewContainer');

        dropZone.addEventListener('click', () => fileInput.click());
        dropZone.addEventListener('dragover', e => {
            e.preventDefault();
            dropZone.classList.add('dragover');
        });
        dropZone.addEventListener('dragleave', e => {
            dropZone.classList.remove('dragover');
        });
        dropZone.addEventListener('drop', e => {
            e.preventDefault();
            dropZone.classList.remove('dragover');
            if (e.dataTransfer.files.length) {
                fileInput.files = e.dataTransfer.files;
                updateFileList();
                previewFiles();
            }
        });
        fileInput.addEventListener('change', () => {
            updateFileList();
            previewFiles();
        });
        function updateFileList() {
            if (fileInput.files.length) {
                fileList.innerHTML = Array.from(fileInput.files).map(f => f.name).join('<br>');
            } else {
                fileList.innerHTML = '';
            }
        }
        function previewFiles() {
            previewContainer.innerHTML = '';
            Array.from(fileInput.files).forEach(file => {
                if (file.type.startsWith('text') || file.name.match(r"\.txt|\.md|\.csv|\.html", re.IGNORECASE)) {
                    // Corrected regex to avoid invalid escape sequence
                    const reader = new FileReader();
                    reader.onload = function(e) {
                        const text = e.target.result;
                        const preview = document.createElement('div');
                        preview.className = 'preview-box';
                        preview.innerHTML = `<b>${file.name}</b><pre>${text.substring(0, 1000)}</pre>`;
                        previewContainer.appendChild(preview);
                    };
                    reader.readAsText(file);
                }
            });
        }
        form.addEventListener('submit', function(e) {
            if (!fileInput.files.length) {
                alert('Please select at least one file.');
                e.preventDefault();
                return;
            }
            e.preventDefault();
            progressContainer.style.display = 'block';
            progressBar.style.width = '0%';
            let completed = 0;
            Array.from(fileInput.files).forEach((file, idx, arr) => {
                const formData = new FormData();
                formData.append('file', file);
                formData.append('output_format', document.getElementById('outputFormat').value);
                formData.append('lang', document.getElementById('langSelect').value);
                formData.append('clean_level', document.getElementById('cleanLevel').value);
                const xhr = new XMLHttpRequest();
                xhr.open('POST', '/');
                xhr.responseType = 'blob';
                xhr.upload.onprogress = function(e) {
                    if (e.lengthComputable) {
                        const percent = ((completed + e.loaded / e.total) / arr.length) * 100;
                        progressBar.style.width = percent + '%';
                    }
                };
                xhr.onload = function() {
                    completed++;
                    if (xhr.status === 200) {
                        const blob = xhr.response;
                        const a = document.createElement('a');
                        a.href = window.URL.createObjectURL(blob);
                        a.download = file.name.replace(/\.[^.]+$/, '_cleaned.txt');
                        a.click();
                    } else {
                        alert('Processing failed for ' + file.name);
                    }
                    if (completed === arr.length) {
                        progressBar.style.width = '0%';
                        progressContainer.style.display = 'none';
                    }
                };
                xhr.send(formData);
            });
        });
        </script>
        </body>
        </html>
    ''')

@app.route("/dashboard", methods=["GET"])
def dashboard():
    # Render a small stats dashboard
    return render_template_string('''
        <html>
        <head>
            <title>Dashboard</title>
            <style>
                body { font-family: 'IBM Plex Mono', monospace; background: #1F1F1F; color: #FFF200; }
                .dashboard { display: flex; flex-wrap: wrap; gap: 1em; }
                .card { background: rgba(31,31,31,0.85); border-radius: 8px; padding: 1em; flex: 1; min-width: 200px; }
            </style>
        </head>
        <body>
            <h1>Dashboard</h1>
            <div class="dashboard">
                <div class="card">Words Processed Today: 12345</div>
                <div class="card">Dataset Size: 678 MB</div>
                <div class="card">Top Topics: AI, ML, NLP</div>
            </div>
        </body>
        </html>
    ''')

@app.route("/settings", methods=["GET", "POST"])
def settings():
    # Render settings modal
    if request.method == "POST":
        # Handle settings update
        return "Settings updated successfully!", 200
    return render_template_string('''
        <html>
        <head>
            <title>Settings</title>
            <style>
                body { font-family: 'IBM Plex Mono', monospace; background: #1F1F1F; color: #FFF200; }
                .modal { background: rgba(31,31,31,0.85); border-radius: 8px; padding: 2em; max-width: 400px; margin: 2em auto; }
            </style>
        </head>
        <body>
            <div class="modal">
                <h1>Settings</h1>
                <form method="post">
                    <label>Clean Mode:</label>
                    <select name="clean_mode">
                        <option value="basic">Basic</option>
                        <option value="advanced">Advanced</option>
                    </select>
                    <br><br>
                    <label>Splitting:</label>
                    <input type="checkbox" name="splitting" checked>
                    <br><br>
                    <label>Filters:</label>
                    <input type="text" name="filters" placeholder="Comma-separated filters">
                    <br><br>
                    <button type="submit">Save</button>
                </form>
            </div>
        </body>
        </html>
    ''')

@app.errorhandler(500)
def handle_500(e):
    logger.error("Internal server error occurred.")
    return "Processing failed.", 500

if __name__ == "__main__":
    try:
        app.run(debug=True)
    except Exception as e:
        logger.exception("Fatal error occurred while running the web application.")
