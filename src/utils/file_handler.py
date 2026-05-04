from pathlib import Path

SUPPORTED_EXTENSIONS = {
    ".csv": "csv",
    ".xlsx": "excel",
    ".xls": "excel",
    ".json": "json",
    ".pdf": "pdf",
    ".docx": "docx",
}


def detect_file_type(file_path: str) -> str:
    ext = Path(file_path).suffix.lower()
    file_type = SUPPORTED_EXTENSIONS.get(ext)
    if file_type is None:
        raise ValueError(f"Extensão não suportada: {ext}. Formatos aceitos: {list(SUPPORTED_EXTENSIONS)}")
    return file_type


def save_upload(uploaded_file, upload_dir: str = "uploads") -> str:
    """Salva o arquivo do Streamlit em disco e retorna o caminho."""
    import tempfile
    import os

    os.makedirs(upload_dir, exist_ok=True)
    suffix = Path(uploaded_file.name).suffix
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix, dir=upload_dir) as tmp:
        tmp.write(uploaded_file.getbuffer())
        return tmp.name
