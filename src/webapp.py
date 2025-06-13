from flask import Flask, request, render_template_string, send_file, abort
from pathlib import Path
from src.main import process_single_file, TextCleaner, download_language_model
import os
import logging
import re
import mimetypes

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

# Configure necessary directories
UPLOAD_FOLDER = Path("web_uploads")
OUTPUT_FOLDER = Path("output/cleaned_texts")
UPLOAD_FOLDER.mkdir(exist_ok=True)
OUTPUT_FOLDER.mkdir(parents=True, exist_ok=True)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        try:
            if 'file' not in request.files:
                logger.error("No file provided in the request.")
                return "No file provided", 400

            file = request.files.get("file")
            if not file or not file.filename:
                logger.error("No file selected for upload.")
                return "No file selected", 400

            # Sanitize filename
            filename = Path(file.filename).name
            file_path = UPLOAD_FOLDER / filename

            try:
                file.save(str(file_path))
            except Exception as e:
                logger.error(f"Failed to save uploaded file: {e}")
                return "File upload failed", 500

            if not file_path.exists():
                logger.error("File upload failed - file not found after save.")
                return "File upload failed", 500

            try:
                lang_model = download_language_model()
                cleaner = TextCleaner(lang_model=lang_model) if lang_model else TextCleaner()
            except Exception as e:
                logger.exception(f"Failed to initialize text cleaner: {e}")
                return "Text cleaner initialization failed", 500

            try:
                if process_single_file(file_path, cleaner):
                    cleaned_path = OUTPUT_FOLDER / f"{file_path.stem}_cleaned.txt"
                    if cleaned_path.exists():
                        logger.info(f"File processed successfully: {cleaned_path}")
                        mime_type, _ = mimetypes.guess_type(str(cleaned_path))
                        return send_file(cleaned_path, 
                                      mimetype=mime_type or 'text/plain',
                                      as_attachment=True,
                                      download_name=cleaned_path.name)
            except Exception as e:
                logger.exception(f"Error processing file: {e}")
                return "Processing failed", 500

            logger.error("File processing failed.")
            return "Processing failed", 500

        except Exception as e:
            logger.exception(f"Unexpected error: {e}")
            return "An unexpected error occurred", 500

        finally:
            # Clean up uploaded file
            try:
                if 'file_path' in locals() and file_path.exists():
                    file_path.unlink()
                    logger.info(f"Temporary file cleaned up: {file_path}")
            except Exception as e:
                logger.warning(f"Failed to clean up temporary file: {e}")
                
    return render_template_string(r'''
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>MakeAIDatasets Web</title>
            <link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&display=swap" rel="stylesheet">
            <style>                body {
                    background: linear-gradient(135deg, #1F1F1F 0%, #2A2A2A 100%);
                    font-family: 'IBM Plex Mono', monospace;
                    color: #FFF200;
                    margin: 0;
                    min-height: 100vh;
                    padding: 20px;
                    box-sizing: border-box;
                }                .format-info {
                    text-align: center;
                    margin: 1.5em 0;
                }
                .info-link {
                    color: #FF6EC7;
                    text-decoration: none;
                    padding: 0.5em 1em;
                    border: 1px solid #FF6EC7;
                    border-radius: 4px;
                    transition: all 0.3s ease;
                }
                .info-link:hover {
                    background: rgba(255,110,199,0.1);
                    box-shadow: 0 0 10px rgba(255,110,199,0.3);
                }
                .glass {
                    background: rgba(31,31,31,0.95);
                    box-shadow: 0 8px 32px 0 rgba(0,0,0,0.3);
                    backdrop-filter: blur(8px);
                    -webkit-backdrop-filter: blur(8px);
                    border-radius: 16px;
                    border: 1px solid rgba(255,255,255,0.1);
                    padding: 2em;
                    max-width: 800px;
                    margin: 20px auto;
                    position: relative;
                    overflow: hidden;
                }                h1 {
                    color: #00FFC6;
                    text-shadow: 0 0 8px #00FFC6, 0 0 2px #FFF200;
                    margin-bottom: 1.5em;
                    text-align: center;
                    font-size: 2.5em;
                }                .drop-zone {
                    border: 2px dashed #FF6EC7;
                    border-radius: 12px;
                    padding: 3em 2em;
                    text-align: center;
                    color: #FF6EC7;
                    background: rgba(255,255,255,0.05);
                    cursor: pointer;
                    margin-bottom: 1.5em;
                    transition: all 0.3s ease;
                    position: relative;
                    overflow: hidden;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    min-height: 200px;
                }
                .drop-zone-content {
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                    gap: 1em;
                }
                .drop-zone-content svg {
                    stroke: #FF6EC7;
                    transition: all 0.3s ease;
                }
                .drop-zone-content p {
                    margin: 0;
                    font-size: 1.1em;
                    line-height: 1.5;
                }
                .drop-zone::before {
                    content: '';
                    position: absolute;
                    top: 0;
                    left: 0;
                    width: 100%;
                    height: 100%;
                    background: linear-gradient(45deg, transparent, rgba(255,110,199,0.1), transparent);
                    transform: translateX(-100%);
                    transition: transform 0.5s;
                }                .drop-zone.dragover { 
                    background: rgba(255,255,255,0.1);
                    transform: scale(1.02);
                }
                .drop-zone.dragover::before {
                    transform: translateX(100%);
                }
                .progress { 
                    width: 100%; 
                    background: rgba(51,51,51,0.5); 
                    border-radius: 8px; 
                    margin: 1.5em 0;
                    overflow: hidden;
                }
                .progress-bar { 
                    width: 0; 
                    height: 8px; 
                    background: linear-gradient(90deg, #00FFC6, #FF6EC7);
                    border-radius: 8px; 
                    transition: width 0.3s ease-out;
                }
                .file-list { 
                    color: #FFF200; 
                    margin: 1em 0;
                    padding: 1em;
                    background: rgba(255,255,255,0.05);
                    border-radius: 8px;
                }
                .preview-box {
                    background: rgba(35,35,35,0.8);
                    border-radius: 8px;
                    padding: 1em;
                    margin: 1em 0;
                    color: #FFF200;
                    font-size: 0.95em;
                    max-height: 200px;
                    overflow-y: auto;
                }                .options-panel {
                    background: rgba(255,255,255,0.07);
                    border-radius: 12px;
                    padding: 1.5em;
                    margin: 1.5em 0;
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                    gap: 1em;
                }
                label { 
                    color: #FF6EC7; 
                    display: block;
                    margin-bottom: 0.5em;
                }
                select {
                    width: 100%;
                    padding: 0.5em;
                    background: rgba(31,31,31,0.9);
                    border: 1px solid rgba(255,255,255,0.1);
                    border-radius: 4px;
                    color: #FFF200;
                    font-family: inherit;
                    cursor: pointer;
                }
                select:hover {
                    border-color: #FF6EC7;
                }
                .btn {
                    background: linear-gradient(45deg, #FF6EC7, #00FFC6);
                    color: #1F1F1F;
                    border: none;
                    border-radius: 8px;
                    padding: 1em 2em;
                    font-family: inherit;
                    font-size: 1.1em;
                    font-weight: 600;
                    cursor: pointer;
                    margin-top: 1.5em;
                    transition: all 0.3s ease;
                    text-transform: uppercase;
                    letter-spacing: 1px;
                    width: 100%;
                }
                .btn:hover {
                    transform: translateY(-2px);
                    box-shadow: 0 4px 15px rgba(255,110,199,0.4);
                }
                .btn:active { 
                    transform: translateY(1px);
                    background: linear-gradient(45deg, #00FFC6, #FF6EC7);
                }
            </style>
        </head>
        <body>
        <div class="glass">            <h1>MakeAIDatasets Web</h1>
            <form id="uploadForm" method="post" enctype="multipart/form-data">
                <div class="drop-zone" id="dropZone">
                    <div class="drop-zone-content">
                        <svg width="50" height="50" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
                            <polyline points="17 8 12 3 7 8"></polyline>
                            <line x1="12" y1="3" x2="12" y2="15"></line>
                        </svg>
                        <p>Drag & Drop files here<br>or click to select</p>
                    </div>
                </div>
                <input type="file" name="file" id="fileInput" style="display:none;" multiple>
                <div class="file-list" id="fileList"></div>                <div class="options-panel">
                    <div class="option-group">
                        <label>Output Format:</label>
                        <select name="output_format" id="outputFormat">
                            <option value="txt">TXT</option>
                            <option value="json">JSON</option>
                            <option value="csv">CSV</option>
                            <option value="jsonl">JSONL</option>
                            <option value="parquet">Parquet</option>
                            <option value="tfrecord">TFRecord</option>
                            <option value="arrow">Arrow</option>
                            <option value="tsv">TSV</option>
                            <option value="yaml">YAML</option>
                        </select>
                    </div>                    <div class="option-group">
                        <label>Language:</label>
                        <select name="lang" id="langSelect">
                            <option value="en">English</option>
                            <option value="es">Spanish</option>
                            <option value="fr">French</option>
                            <option value="de">German</option>
                            <option value="it">Italian</option>
                            <option value="pt">Portuguese</option>
                            <option value="nl">Dutch</option>
                            <option value="ru">Russian</option>
                            <option value="zh">Chinese</option>
                            <option value="ja">Japanese</option>
                            <option value="ko">Korean</option>
                            <option value="tr">Turkish</option>
                            <option value="auto">Auto-Detect</option>
                        </select>
                    </div>
                    <div class="option-group">
                        <label>Clean Level:</label>
                        <select name="clean_level" id="cleanLevel">
                            <option value="basic">Basic</option>
                            <option value="standard">Standard</option>
                            <option value="advanced">Advanced</option>
                            <option value="aggressive">Aggressive</option>
                        </select>
                    </div>
                </div>                <div class="progress" id="progressContainer" style="display:none;">
                    <div class="progress-bar" id="progressBar"></div>
                </div>
                <div class="format-info">
                    <a href="/output_formats" class="info-link" target="_blank">Overview of the output formats and types</a>
                </div>
                <button class="btn" type="submit">Upload And MakeAIDatasets</button>
            </form>
            <div id="previewContainer"></div>
        </div>
        <script>        const dropZone = document.getElementById('dropZone');
        const fileInput = document.getElementById('fileInput');
        const fileList = document.getElementById('fileList');
        const form = document.getElementById('uploadForm');
        const progressContainer = document.getElementById('progressContainer');
        const progressBar = document.getElementById('progressBar');
        const previewContainer = document.getElementById('previewContainer');

        // Handle click on drop zone
        dropZone.addEventListener('click', (e) => {
            e.preventDefault();
            fileInput.click();
        });
        
        // Handle file input change
        fileInput.addEventListener('change', (e) => {
            e.preventDefault();
            updateFileList();
            previewFiles();
        });        // Prevent default drag behaviors
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            dropZone.addEventListener(eventName, (e) => {
                e.preventDefault();
                e.stopPropagation();
            });
        });

        // Handle drag enter and over
        ['dragenter', 'dragover'].forEach(eventName => {
            dropZone.addEventListener(eventName, (e) => {
                dropZone.classList.add('dragover');
            });
        });

        // Handle drag leave and drop
        ['dragleave', 'drop'].forEach(eventName => {
            dropZone.addEventListener(eventName, (e) => {
                dropZone.classList.remove('dragover');
            });
        });

        // Handle dropped files
        dropZone.addEventListener('drop', (e) => {
            const droppedFiles = e.dataTransfer.files;
            
            // Set the files to the file input
            const dataTransfer = new DataTransfer();
            Array.from(droppedFiles).forEach(file => {
                dataTransfer.items.add(file);
            });
            fileInput.files = dataTransfer.files;
            
            updateFileList();
            previewFiles();
            
            // Visual feedback
            const dropContent = dropZone.querySelector('.drop-zone-content');
            dropContent.innerHTML = `<p>✅ ${droppedFiles.length} file(s) selected</p>`;
            setTimeout(() => {
                dropContent.innerHTML = `
                    <svg width="50" height="50" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
                        <polyline points="17 8 12 3 7 8"></polyline>
                        <line x1="12" y1="3" x2="12" y2="15"></line>
                    </svg>
                    <p>Drag & Drop files here<br>or click to select</p>
                `;
            }, 2000);
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
        function previewFiles() {            previewContainer.innerHTML = '';
            Array.from(fileInput.files).forEach(file => {
                if (file.type.startsWith('text') || /\.(txt|md|csv|html|pdf|epub|docx)$/i.test(file.name)) {
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

@app.route("/output_formats", methods=["GET"])
def output_formats():
    return render_template_string(r'''
        <html>
        <head>
            <title>Output Formats</title>
            <style>
                body { font-family: 'IBM Plex Mono', monospace; background: #1F1F1F; color: #FFF200; }
                .format { margin-bottom: 2em; padding: 1em; border: 1px solid #FFF200; border-radius: 8px; background: rgba(31,31,31,0.85); }
                h2 { color: #00FFC6; }
                pre { background: #232323; padding: 1em; border-radius: 8px; color: #FFF200; }
                p { margin: 0.5em 0; }
            </style>
        </head>
        <body>
            <h1>Supported Output Formats</h1>
            <div class="format">
                <h2>📄 CSV (Comma-Separated Values)</h2>
                <p>✅ Best for: Simple tabular data (structured, numeric/text)</p>
                <p>🔧 Use Case: Classification, regression, labeled datasets</p>
                <pre>text,label\n"Today is sunny",positive\n"I am sad",negative</pre>
                <pre>import pandas as pd\ndf = pd.read_csv("data.csv")</pre>
            </div>
            <div class="format">
                <h2>🧾 JSON (JavaScript Object Notation)</h2>
                <p>✅ Best for: Nested or hierarchical data</p>
                <p>🔧 Use Case: NLP tasks, Q&A, summarization, prompts</p>
                <pre>[\n  { "prompt": "What is the capital of France?", "completion": "Paris" },\n  { "prompt": "Translate to French: 'Good morning'", "completion": "Bonjour" }\n]</pre>
                <pre>import json\nwith open("data.json") as f:\n    data = json.load(f)</pre>
            </div>
            <div class="format">
                <h2>📘 JSONL (JSON Lines)</h2>
                <p>✅ Best for: Streaming datasets, memory efficiency</p>
                <p>🔧 Use Case: OpenAI fine-tuning, transformers, dialogue training</p>
                <pre>{"prompt": "What's 2 + 2?", "completion": "4"}\n{"prompt": "Who wrote '1984'?", "completion": "George Orwell"}</pre>
                <pre>with open("data.jsonl", "r") as f:\n    for line in f:\n        item = json.loads(line)</pre>
            </div>
            <div class="format">
                <h2>🧱 Parquet</h2>
                <p>✅ Best for: High-performance tabular data (large-scale)</p>
                <p>🔧 Use Case: Big data, ML pipelines</p>
                <pre>import pandas as pd\ndf = pd.read_parquet("data.parquet")</pre>
            </div>
            <div class="format">
                <h2>📦 TFRecord</h2>
                <p>✅ Best for: TensorFlow datasets (image/text/audio)</p>
                <p>🔧 Use Case: Deep learning (vision, NLP, etc.)</p>
                <pre># Save TFRecord\nwith tf.io.TFRecordWriter('data.tfrecord') as writer:\n    example = tf.train.Example(...)\n    writer.write(example.SerializeToString())</pre>
            </div>
            <div class="format">
                <h2>⚡ Arrow (Apache Arrow)</h2>
                <p>✅ Best for: Hugging Face datasets, in-memory optimized</p>
                <p>🔧 Use Case: Transformers datasets, fast loading</p>
                <pre>from datasets import load_dataset\ndataset = load_dataset("imdb")</pre>
            </div>
            <div class="format">
                <h2>🧮 TSV (Tab-Separated Values)</h2>
                <p>✅ Best for: Clean tabular data with embedded commas</p>
                <p>🔧 Use Case: Same as CSV, with tab separator</p>
                <pre>text\tlabel\n"How are you?"\tgreeting\n"Go away"\tcommand</pre>
                <pre>import pandas as pd\ndf = pd.read_csv("data.tsv", sep="\t")</pre>
            </div>
            <div class="format">
                <h2>🧬 YAML (YAML Ain’t Markup Language)</h2>
                <p>✅ Best for: Human-readable prompt templates or settings</p>
                <p>🔧 Use Case: Few-shot examples, prompt engineering</p>
                <pre>- prompt: "Define AI"\n  completion: "Artificial Intelligence is the simulation of human intelligence in machines."</pre>
                <pre>import yaml\nwith open("data.yaml") as f:\n    data = yaml.safe_load(f)</pre>
            </div>
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
