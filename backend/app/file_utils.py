from io import BytesIO

from pypdf import PdfReader


def detect_file_type(data: bytes) -> str | None:
    """Detect the real file type from the first bytes, not from the filename."""
    if data.startswith(b"%PDF-"):
        return "pdf"
    if data.startswith(b"\x89PNG\r\n\x1a\n"):
        return "png"
    if data.startswith(b"\xff\xd8\xff"):
        return "jpg"
    return None


def count_pdf_pages(data: bytes) -> int:
    reader = PdfReader(BytesIO(data))
    if reader.is_encrypted:
        raise ValueError("Password-protected PDFs are not supported")
    return len(reader.pages)