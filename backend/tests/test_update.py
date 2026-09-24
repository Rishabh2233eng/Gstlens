from app.routers import extract as extract_router
from tests.test_auth import USER, client, fresh_db, login  # noqa: F401
from tests.test_extract import fake, upload_one  # noqa: F401
from tests.test_pipeline import VALID_GSTIN, clean_invoice  # noqa: F401
from tests.test_upload import auth_headers, make_pdf, upload, upload_dir  # noqa: F401


def setup_invoice(monkeypatch, **fields):
    monkeypatch.setattr(extract_router, "extract_invoice", lambda d, k: clean_invoice(**fields))
    headers, invoice_id = upload_one()
    client.post(f"/invoices/{invoice_id}/extract", headers=headers)
    return headers, invoice_id


def test_update_field(monkeypatch):
    headers, invoice_id = setup_invoice(monkeypatch, supplier_gstin="27ABCDE1234F1Z5")
    r = client.patch(
        f"/invoices/{invoice_id}",
        json={"supplier_gstin": VALID_GSTIN},
        headers=headers,
    )
    assert r.status_code == 200
    assert r.json()["supplier_gstin"] == VALID_GSTIN


def test_update_revalidates_and_clears_issue(monkeypatch):
    headers, invoice_id = setup_invoice(monkeypatch, supplier_gstin="27ABCDE1234F1Z5")
    issues_before = client.get(f"/invoices/{invoice_id}/issues", headers=headers).json()
    assert len(issues_before) >= 1

    client.patch(f"/invoices/{invoice_id}", json={"supplier_gstin": VALID_GSTIN}, headers=headers)
    issues_after = client.get(f"/invoices/{invoice_id}/issues", headers=headers).json()
    assert issues_after == []


def test_update_can_introduce_new_issue(monkeypatch):
    headers, invoice_id = setup_invoice(monkeypatch)
    r = client.patch(
        f"/invoices/{invoice_id}",
        json={"total_amount": "99999.00"},
        headers=headers,
    )
    issues = client.get(f"/invoices/{invoice_id}/issues", headers=headers).json()
    assert any(i["code"] == "invoice_total_mismatch" for i in issues)


def test_update_partial_fields_only(monkeypatch):
    headers, invoice_id = setup_invoice(monkeypatch)
    r = client.patch(
        f"/invoices/{invoice_id}",
        json={"buyer_name": "New Buyer Pvt Ltd"},
        headers=headers,
    )
    assert r.json()["buyer_name"] == "New Buyer Pvt Ltd"
    assert r.json()["supplier_gstin"] == VALID_GSTIN  # unchanged


def test_update_existing_item(monkeypatch):
    headers, invoice_id = setup_invoice(monkeypatch)
    detail = client.get(f"/invoices/{invoice_id}", headers=headers).json()
    # clean_invoice has no items by default, so add one first via items=None path skip;
    # instead directly add a new item through PATCH
    r = client.patch(
        f"/invoices/{invoice_id}",
        json={"items": [{"description": "Chair", "hsn_code": "9401"}]},
        headers=headers,
    )
    assert r.status_code == 200
    assert len(r.json()["items"]) == 1
    item_id = r.json()["items"][0]["id"]

    r2 = client.patch(
        f"/invoices/{invoice_id}",
        json={"items": [{"id": item_id, "description": "Office Chair"}]},
        headers=headers,
    )
    assert len(r2.json()["items"]) == 1
    assert r2.json()["items"][0]["description"] == "Office Chair"


def test_update_omitting_items_leaves_them_unchanged(monkeypatch):
    headers, invoice_id = setup_invoice(monkeypatch)
    client.patch(
        f"/invoices/{invoice_id}",
        json={"items": [{"description": "Chair"}]},
        headers=headers,
    )
    r = client.patch(f"/invoices/{invoice_id}", json={"buyer_name": "X"}, headers=headers)
    assert len(r.json()["items"]) == 1


def test_update_requires_login():
    r = client.patch("/invoices/1", json={"buyer_name": "X"})
    assert r.status_code == 401


def test_update_unknown_invoice():
    r = client.patch("/invoices/999", json={"buyer_name": "X"}, headers=auth_headers())
    assert r.status_code == 404


def test_cannot_update_other_users_invoice(monkeypatch):
    headers, invoice_id = setup_invoice(monkeypatch)
    other = {"email": "upd_other@example.com", "password": "strongpass123"}
    client.post("/auth/register", json=other)
    token = login(other["email"], other["password"]).json()["access_token"]
    r = client.patch(
        f"/invoices/{invoice_id}",
        json={"buyer_name": "X"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 404