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
                if (file.type.startsWith('text') || file.name.match(/\.(txt|md|csv|html)$/i)) {
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

@app.errorhandler(500)
def handle_500(e):
    return "Processing failed.", 500

if __name__ == "__main__":
    app.run(debug=True)
