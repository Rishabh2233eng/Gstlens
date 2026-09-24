from app.routers import extract as extract_router
from tests.test_auth import USER, client, fresh_db, login  # noqa: F401
from tests.test_extract import fake, upload_one  # noqa: F401
from tests.test_upload import auth_headers, make_pdf, upload, upload_dir  # noqa: F401

VALID_GSTIN = "27AAPFU0939F1ZV"  # publicly documented example, passes checksum


def clean_invoice(**over):
    base = dict(
        supplier_gstin=VALID_GSTIN,
        buyer_gstin=VALID_GSTIN,
        invoice_number="INV-1",
        invoice_date="2026-09-15",
        taxable_value=1000,
        cgst=90,
        sgst=90,
        igst=0,
        total_amount=1180,
    )
    base.update(over)
    return fake(**base)


def test_clean_invoice_has_no_issues(monkeypatch):
    monkeypatch.setattr(extract_router, "extract_invoice", lambda d, k: clean_invoice())
    headers, invoice_id = upload_one()
    client.post(f"/invoices/{invoice_id}/extract", headers=headers)
    r = client.get(f"/invoices/{invoice_id}/issues", headers=headers)
    assert r.status_code == 200
    assert r.json() == []


def test_bad_gstin_creates_issue(monkeypatch):
    monkeypatch.setattr(
        extract_router,
        "extract_invoice",
        lambda d, k: clean_invoice(supplier_gstin="27ABCDE1234F1Z5"),  # fails checksum
    )
    headers, invoice_id = upload_one()
    client.post(f"/invoices/{invoice_id}/extract", headers=headers)
    r = client.get(f"/invoices/{invoice_id}/issues", headers=headers)
    codes = [i["code"] for i in r.json()]
    assert any("bad_checksum" in c for c in codes)
    assert any(i["field"] == "supplier_gstin" for i in r.json())


def test_tax_mismatch_creates_error_severity_issue(monkeypatch):
    monkeypatch.setattr(
        extract_router,
        "extract_invoice",
        lambda d, k: clean_invoice(total_amount=5000),
    )
    headers, invoice_id = upload_one()
    client.post(f"/invoices/{invoice_id}/extract", headers=headers)
    r = client.get(f"/invoices/{invoice_id}/issues", headers=headers)
    issue = next(i for i in r.json() if i["code"] == "invoice_total_mismatch")
    assert issue["severity"] == "error"


def test_reextract_replaces_old_issues(monkeypatch):
    headers, invoice_id = upload_one()

    monkeypatch.setattr(
        extract_router,
        "extract_invoice",
        lambda d, k: clean_invoice(supplier_gstin="27ABCDE1234F1Z5"),
    )
    client.post(f"/invoices/{invoice_id}/extract", headers=headers)
    r1 = client.get(f"/invoices/{invoice_id}/issues", headers=headers)
    assert len(r1.json()) >= 1

    monkeypatch.setattr(extract_router, "extract_invoice", lambda d, k: clean_invoice())
    client.post(f"/invoices/{invoice_id}/extract", headers=headers)
    r2 = client.get(f"/invoices/{invoice_id}/issues", headers=headers)
    assert r2.json() == []


def test_issues_requires_login():
    assert client.get("/invoices/1/issues").status_code == 401


def test_issues_for_unknown_invoice():
    assert client.get("/invoices/999/issues", headers=auth_headers()).status_code == 404


def test_list_invoices_shows_issue_count(monkeypatch):
    monkeypatch.setattr(
        extract_router,
        "extract_invoice",
        lambda d, k: clean_invoice(supplier_gstin="27ABCDE1234F1Z5"),
    )
    headers, invoice_id = upload_one()
    client.post(f"/invoices/{invoice_id}/extract", headers=headers)
    r = client.get("/invoices", headers=headers)
    assert r.json()[0]["issue_count"] >= 1