from app.routers import extract as extract_router
from app.usage import current_month_key
from tests.test_auth import USER, client, fresh_db, login  # noqa: F401
from tests.test_pipeline import clean_invoice  # noqa: F401
from tests.test_upload import auth_headers, make_pdf, upload, upload_dir  # noqa: F401


def test_usage_starts_at_zero():
    headers = auth_headers()
    r = client.get("/invoices/usage/me", headers=headers)
    assert r.status_code == 200
    body = r.json()
    assert body["plan_name"] == "Free"
    assert body["monthly_limit"] == 10
    assert body["pages_used"] == 0
    assert body["pages_remaining"] == 10


def test_usage_increases_after_upload():
    headers = auth_headers()
    upload("bill.pdf", make_pdf(3), "application/pdf", headers)
    r = client.get("/invoices/usage/me", headers=headers)
    body = r.json()
    assert body["pages_used"] == 3
    assert body["pages_remaining"] == 7


def test_upload_blocked_when_over_limit():
    headers = auth_headers()
    upload("bill1.pdf", make_pdf(8), "application/pdf", headers)
    r = upload("bill2.pdf", make_pdf(5), "application/pdf", headers)
    assert r.status_code == 402
    assert "remain" in r.json()["detail"]


def test_upload_allowed_exactly_at_limit():
    headers = auth_headers()
    upload("bill1.pdf", make_pdf(7), "application/pdf", headers)
    r = upload("bill2.pdf", make_pdf(3), "application/pdf", headers)
    assert r.status_code == 201


def test_blocked_upload_does_not_increase_usage():
    headers = auth_headers()
    upload("bill1.pdf", make_pdf(9), "application/pdf", headers)
    upload("bill2.pdf", make_pdf(5), "application/pdf", headers)  # rejected, 402
    r = client.get("/invoices/usage/me", headers=headers)
    assert r.json()["pages_used"] == 9


def test_usage_requires_login():
    assert client.get("/invoices/usage/me").status_code == 401


def test_usage_is_per_user():
    headers1 = auth_headers()
    upload("bill.pdf", make_pdf(4), "application/pdf", headers1)

    other = {"email": "usage_other@example.com", "password": "strongpass123"}
    client.post("/auth/register", json=other)
    token = login(other["email"], other["password"]).json()["access_token"]
    headers2 = {"Authorization": f"Bearer {token}"}

    r = client.get("/invoices/usage/me", headers=headers2)
    assert r.json()["pages_used"] == 0


def test_current_month_key_format():
    from datetime import date
    assert current_month_key(date(2026, 3, 5)) == "2026-03"
    assert current_month_key(date(2026, 11, 20)) == "2026-11"