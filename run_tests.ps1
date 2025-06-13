# PowerShell script to run pytest with src in PYTHONPATH
$env:PYTHONPATH = "src"
pytest tests
