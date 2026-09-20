import sys
from pathlib import Path

from app.extractor import ExtractionError, extract_invoice
from app.file_utils import detect_file_type

if len(sys.argv) != 2:
    print("Usage: python extract_test.py samples\\invoice1.pdf")
    sys.exit(1)

data = Path(sys.argv[1]).read_bytes()
kind = detect_file_type(data)
if kind is None:
    print("Only PDF, JPG and PNG files are supported")
    sys.exit(1)

try:
    result = extract_invoice(data, kind)
except ExtractionError as e:
    print("Extraction failed:", e)
    sys.exit(1)

print(result.model_dump_json(indent=2))