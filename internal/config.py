from pathlib import Path
from typing import Set

BASE_DIR = Path(__file__).parent.parent

TEMP_DIR = BASE_DIR / "temp"
TEMP_DIR.mkdir(exist_ok=True)

SUPPORTED_EXTENSIONS: Set[str] = {
    # DocxConverter
    ".docx",
    # PdfConverter
    ".pdf",
    # XlsxConverter
    ".xlsx",
    # XlsConverter
    ".xls",
    # PptxConverter
    ".pptx",
    # HtmlConverter
    ".htm",
    ".html",
}

# Maximum file size (in bytes)
# Default 50MB
MAX_FILE_SIZE: int = 50 * 1024 * 1024

API_V1_PREFIX = "/api/v1"

