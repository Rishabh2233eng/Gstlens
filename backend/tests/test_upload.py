import io

import pytest
from pypdf import PdfWriter

from app import config
from tests.test_auth import USER, client, fresh_db, login  # noqa: F401


@pytest.fixture(autouse=True)
def upload_dir(tmp_path, monkeypatch):
    monkeypatch.setattr(config, "UPLOAD_DIR", tmp_path)
    return tmp_path


def make_pdf(pages=2) -> bytes:
    writer = PdfWriter()
    for _ in range(pages):
        writer.add_blank_page(width=200, height=200)
    buf = io.BytesIO()
    writer.write(buf)
    return buf.getvalue()


def auth_headers():
    client.post("/auth/register", json=USER)
    token = login().json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def upload(name, data, mime, headers):
    return client.post(
        "/invoices/upload", files={"file": (name, data, mime)}, headers=headers
    )


def test_upload_pdf(upload_dir):
    r = upload("bill.pdf", make_pdf(2), "application/pdf", auth_headers())
    assert r.status_code == 201
    body = r.json()
    assert body["page_count"] == 2
    assert body["status"] == "uploaded"
    assert body["filename"] == "bill.pdf"
    assert len(list(upload_dir.rglob("*.pdf"))) == 1


def test_upload_png():
    data = b"\x89PNG\r\n\x1a\n" + b"0" * 50
    r = upload("bill.png", data, "image/png", auth_headers())
    assert r.status_code == 201
    assert r.json()["page_count"] == 1


def test_upload_jpg():
    data = b"\xff\xd8\xff" + b"0" * 50
    r = upload("bill.jpg", data, "image/jpeg", auth_headers())
    assert r.status_code == 201


def test_reject_text_file():
    r = upload("notes.txt", b"hello world", "text/plain", auth_headers())
    assert r.status_code == 400


def test_reject_fake_pdf():
    r = upload("fake.pdf", b"this is not a pdf", "application/pdf", auth_headers())
    assert r.status_code == 400


def test_reject_too_large(monkeypatch):
    monkeypatch.setattr(config, "MAX_UPLOAD_BYTES", 100)
    r = upload("big.pdf", make_pdf(1), "application/pdf", auth_headers())
    assert r.status_code == 413


def test_reject_too_many_pages(monkeypatch):
    monkeypatch.setattr(config, "MAX_PDF_PAGES", 1)
    r = upload("long.pdf", make_pdf(2), "application/pdf", auth_headers())
    assert r.status_code == 400


def test_upload_requires_login():
    r = client.post("/invoices/upload", files={"file": ("a.pdf", make_pdf(1), "application/pdf")})
    assert r.status_code == 401