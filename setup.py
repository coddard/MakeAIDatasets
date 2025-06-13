from setuptools import setup, find_packages

setup(
    name="makeaidatasets",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "flask",
        "python-docx",
        "beautifulsoup4",
        "ebooklib",
        "PyPDF2",
        "pdf2image",
        "pytesseract",
        "datasets",
        "lingua-language-detector",
    ],
    python_requires=">=3.6",
)
