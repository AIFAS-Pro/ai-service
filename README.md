# AI Attendance System - Phase 1

This repository contains three independent services for a microservice-based AI attendance system:

- `frontend/` - React + Vite + TypeScript UI on `localhost:5173`
- `backend/` - Django REST Framework API on `localhost:8000`
- `ai-service/` - FastAPI face-recognition service on `localhost:8001`

React calls only Django. Django persists business data and calls the AI service over HTTP. The AI service never talks to React or the database and stores embeddings as local `.npy` files.

## Quick start

Start each service in a separate terminal.

### AI Service

```bash
cd ai-service
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --host 0.0.0.0 --port 8001
```

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python manage.py migrate
python manage.py runserver 0.0.0.0:8000
```

### Frontend

```bash
cd frontend
npm install
cp .env.example .env
npm run dev -- --host 0.0.0.0
```

## Local storage

The backend stores uploaded registration and verification images under school-code/class/section-aware media folders such as `media/students/<school_code>/<class>/<section>/` and `media/attendance/<school_code>/<class>/<section>/`. The AI service stores embeddings under matching scoped folders such as `media/embeddings/<school_code>/<class>/<section>/student_101.npy`.
