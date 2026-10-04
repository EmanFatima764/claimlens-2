# Backend quick start (run from the REPO ROOT, not from backend/)

    python -m venv venv && source venv/bin/activate        # Windows: venv\Scripts\activate
    pip install -r backend/requirements.txt
    cp backend/.env.example backend/.env                    # fill in keys
    uvicorn backend.app.main:app --reload --port 8000

1. Supabase SQL editor: run `backend/migrations/001_init_schema.sql`, then `002_report_fields.sql`.
2. With no SUPABASE_* set, the app uses an in-memory store (data lost on restart) - fine for local dev.
3. Docs: http://localhost:8000/docs   Tests: `cd backend && pytest`
4. Docker (from repo root): `docker build -f backend/Dockerfile -t claimlens-backend .`
