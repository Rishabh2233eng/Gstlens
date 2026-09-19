import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app
from app.models import Plan

engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSession = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def override_get_db():
    db = TestingSession()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)

USER = {"email": "Test@Example.com", "password": "strongpass123", "full_name": "Test User"}


@pytest.fixture(autouse=True)
def fresh_db():
    Base.metadata.create_all(engine)
    db = TestingSession()
    db.add(Plan(name="Free", price_inr=0, monthly_page_limit=10))
    db.commit()
    db.close()
    yield
    Base.metadata.drop_all(engine)


def login(email=USER["email"], password=USER["password"]):
    return client.post("/auth/login", data={"username": email, "password": password})


def test_register_success():
    r = client.post("/auth/register", json=USER)
    assert r.status_code == 201
    body = r.json()
    assert body["email"] == "test@example.com"
    assert body["plan"]["name"] == "Free"
    assert "password" not in body and "hashed_password" not in body


def test_register_duplicate_email():
    client.post("/auth/register", json=USER)
    r = client.post("/auth/register", json=USER)
    assert r.status_code == 400


def test_register_short_password():
    r = client.post("/auth/register", json={**USER, "password": "short"})
    assert r.status_code == 422


def test_login_success():
    client.post("/auth/register", json=USER)
    r = login()
    assert r.status_code == 200
    assert r.json()["token_type"] == "bearer"
    assert r.json()["access_token"]


def test_login_wrong_password():
    client.post("/auth/register", json=USER)
    assert login(password="wrongpassword").status_code == 401


def test_me_with_token():
    client.post("/auth/register", json=USER)
    token = login().json()["access_token"]
    r = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200
    assert r.json()["email"] == "test@example.com"


def test_me_without_token():
    assert client.get("/auth/me").status_code == 401


def test_me_with_bad_token():
    r = client.get("/auth/me", headers={"Authorization": "Bearer not-a-real-token"})
    assert r.status_code == 401