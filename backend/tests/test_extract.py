from app.extraction_schema import ExtractedInvoice
from app.extractor import ExtractionError, normalize
from app.routers import extract as extract_router
from tests.test_auth import USER, client, fresh_db, login  # noqa: F401
from tests.test_upload import auth_headers, make_pdf, upload, upload_dir  # noqa: F401


def fake(**over):
    base = {name: None for name in ExtractedInvoice.model_fields}
    base["items"] = []
    base.update(over)
    return ExtractedInvoice(**base)


def upload_one():
    headers = auth_headers()
    r = upload("bill.pdf", make_pdf(1), "application/pdf", headers)
    return headers, r.json()["id"]


def test_extract_returns_data(monkeypatch):
    monkeypatch.setattr(
        extract_router,
        "extract_invoice",
        lambda data, kind: fake(supplier_name="ABC Traders", total_amount=1180.0),
    )
    headers, invoice_id = upload_one()
    r = client.post(f"/invoices/{invoice_id}/extract", headers=headers)
    assert r.status_code == 200
    assert r.json()["supplier_name"] == "ABC Traders"
    assert r.json()["total_amount"] == "1180.00"
    assert r.json()["items"] == []


def test_extract_provider_error_returns_502(monkeypatch):
    def boom(data, kind):
        raise ExtractionError("provider down")

    monkeypatch.setattr(extract_router, "extract_invoice", boom)
    headers, invoice_id = upload_one()
    r = client.post(f"/invoices/{invoice_id}/extract", headers=headers)
    assert r.status_code == 502


def test_extract_unknown_invoice():
    r = client.post("/invoices/999/extract", headers=auth_headers())
    assert r.status_code == 404


def test_extract_requires_login():
    assert client.post("/invoices/1/extract").status_code == 401


def test_cannot_extract_other_users_invoice(monkeypatch):
    monkeypatch.setattr(extract_router, "extract_invoice", lambda d, k: fake())
    _, invoice_id = upload_one()
    other = {"email": "other@example.com", "password": "strongpass123"}
    client.post("/auth/register", json=other)
    token = login(other["email"], other["password"]).json()["access_token"]
    r = client.post(
        f"/invoices/{invoice_id}/extract", headers={"Authorization": f"Bearer {token}"}
    )
    assert r.status_code == 404


def test_extract_missing_file(upload_dir):
    headers, invoice_id = upload_one()
    for f in upload_dir.rglob("*.pdf"):
        f.unlink()
    r = client.post(f"/invoices/{invoice_id}/extract", headers=headers)
    assert r.status_code == 404


def test_normalize_gstin():
    result = normalize(fake(supplier_gstin=" 27abcde1234f1z5 ", buyer_gstin=None))
    assert result.supplier_gstin == "27ABCDE1234F1Z5"
    assert result.buyer_gstin is None


def test_extraction_is_saved_to_db(monkeypatch):
    monkeypatch.setattr(
        extract_router,
        "extract_invoice",
        lambda data, kind: fake(
            supplier_name="ABC Traders",
            invoice_number="INV-1",
            total_amount=1180.0,
        ),
    )
    headers, invoice_id = upload_one()
    client.post(f"/invoices/{invoice_id}/extract", headers=headers)

    r = client.get(f"/invoices/{invoice_id}", headers=headers)
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "done"
    assert body["supplier_name"] == "ABC Traders"
    assert body["total_amount"] == "1180.00"


def test_list_invoices(monkeypatch):
    monkeypatch.setattr(extract_router, "extract_invoice", lambda d, k: fake())
    headers, _ = upload_one()
    r = client.get("/invoices", headers=headers)
    assert r.status_code == 200
    assert len(r.json()) == 1
    assert r.json()[0]["issue_count"] == 0


def test_list_invoices_only_shows_own(monkeypatch):
    monkeypatch.setattr(extract_router, "extract_invoice", lambda d, k: fake())
    headers, _ = upload_one()

    other = {"email": "other2@example.com", "password": "strongpass123"}
    client.post("/auth/register", json=other)
    other_token = login(other["email"], other["password"]).json()["access_token"]
    other_headers = {"Authorization": f"Bearer {other_token}"}

    r = client.get("/invoices", headers=other_headers)
    assert r.status_code == 200
    assert r.json() == []


def test_get_invoice_detail_with_items(monkeypatch):
    from app.extraction_schema import ExtractedItem

    monkeypatch.setattr(
        extract_router,
        "extract_invoice",
        lambda d, k: fake(items=[ExtractedItem(description="Chair", hsn_code="9401")]),
    )
    headers, invoice_id = upload_one()
    client.post(f"/invoices/{invoice_id}/extract", headers=headers)

    r = client.get(f"/invoices/{invoice_id}", headers=headers)
    assert r.status_code == 200
    assert len(r.json()["items"]) == 1
    assert r.json()["items"][0]["description"] == "Chair"


def test_reextract_replaces_old_items(monkeypatch):
    from app.extraction_schema import ExtractedItem

    headers, invoice_id = upload_one()

    monkeypatch.setattr(
        extract_router, "extract_invoice", lambda d, k: fake(items=[ExtractedItem(description="A")])
    )
    client.post(f"/invoices/{invoice_id}/extract", headers=headers)

    monkeypatch.setattr(
        extract_router, "extract_invoice", lambda d, k: fake(items=[ExtractedItem(description="B")])
    )
    client.post(f"/invoices/{invoice_id}/extract", headers=headers)

    r = client.get(f"/invoices/{invoice_id}", headers=headers)
    items = r.json()["items"]
    assert len(items) == 1
    assert items[0]["description"] == "B"


def test_extract_failure_marks_invoice_failed(monkeypatch):
    monkeypatch.setattr(
        extract_router, "extract_invoice", lambda d, k: (_ for _ in ()).throw(ExtractionError("boom"))
    )
    headers, invoice_id = upload_one()
    client.post(f"/invoices/{invoice_id}/extract", headers=headers)

    r = client.get(f"/invoices/{invoice_id}", headers=headers)
    assert r.json()["status"] == "failed"
    assert r.json()["error_message"] == "boom"