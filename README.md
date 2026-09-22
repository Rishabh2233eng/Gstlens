# GSTLens

GST-aware invoice extraction and validation SaaS. Upload an invoice (PDF, JPG, PNG), extract its data with AI, and validate it against Indian GST rules.

## Stack
- Backend: FastAPI, PostgreSQL (Neon), SQLAlchemy, Alembic
- Extraction: Google Gemini (multimodal)
- Frontend: React (Vite), Tailwind
- Payments: Razorpay (subscriptions)
- Auth: JWT

## Features so far
- Email/password auth with JWT tokens
- Invoice upload with type, size and page-count checks
- AI-based extraction of supplier, buyer, GSTINs, dates, amounts and line items
- Invoice list and detail endpoints, extraction results stored in PostgreSQL

## Running locally
```bash
# backend
cd backend
python -m venv venv
venv\Scripts\Activate.ps1        # Windows PowerShell
pip install -r requirements.txt
# create backend/.env with DATABASE_URL, SECRET_KEY, GEMINI_API_KEY (see .env.example)
alembic upgrade head
python seed.py
uvicorn app.main:app --reload

# frontend
cd frontend
npm install
npm run dev
```

## Tests
```bash
cd backend
pytest -v
```

## Status
Work in progress, built in daily modules. See commit history for progress.