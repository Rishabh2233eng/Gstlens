from app.routers import extract as extract_router
from tests.test_auth import USER, client, fresh_db, login  # noqa: F401
from tests.test_pipeline import clean_invoice  # noqa: F401
from tests.test_update import setup_invoice  # noqa: F401
from tests.test_upload import auth_headers, make_pdf, upload, upload_dir  # noqa: F401


def test_export_one_excel(monkeypatch):
    headers, invoice_id = setup_invoice(monkeypatch)
    r = client.get(f"/invoices/{invoice_id}/export/excel", headers=headers)
    assert r.status_code == 200
    assert r.headers["content-type"].startswith("application/vnd.openxmlformats")
    assert len(r.content) > 0


def test_export_one_csv(monkeypatch):
    headers, invoice_id = setup_invoice(monkeypatch)
    r = client.get(f"/invoices/{invoice_id}/export/csv", headers=headers)
    assert r.status_code == 200
    assert r.headers["content-type"].startswith("text/csv")
    assert b"Voucher Date" in r.content


def test_export_batch_excel(monkeypatch):
    headers, id1 = setup_invoice(monkeypatch)
    _, id2 = setup_invoice(monkeypatch)
    r = client.post("/invoices/export/excel", json={"invoice_ids": [id1, id2]}, headers=headers)
    assert r.status_code == 200
    assert len(r.content) > 0


def test_export_unknown_invoice():
    r = client.get("/invoices/999/export/excel", headers=auth_headers())
    assert r.status_code == 404


def test_export_requires_login():
    assert client.get("/invoices/1/export/excel").status_code == 401


def test_cannot_export_other_users_invoice(monkeypatch):
    headers, invoice_id = setup_invoice(monkeypatch)
    other = {"email": "export_other@example.com", "password": "strongpass123"}
    client.post("/auth/register", json=other)
    token = login(other["email"], other["password"]).json()["access_token"]
    r = client.get(
        f"/invoices/{invoice_id}/export/excel",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 404


def test_export_batch_rejects_empty_list():
    r = client.post("/invoices/export/excel", json={"invoice_ids": []}, headers=auth_headers())
    assert r.status_code == 422