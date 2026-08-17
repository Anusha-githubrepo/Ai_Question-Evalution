# AI Question Evaluator

Production-ready full-stack web application for evaluating student answers against reference answers using semantic similarity and optional Groq or Google Gemini reasoning.

## Features

- FastAPI REST API with layered architecture
- SQLite evaluation history
- Sentence Transformer embeddings with deterministic lexical fallback
- Optional Groq and Google Gemini API structured JSON evaluation
- React + Vite + Tailwind dashboard
- Dark mode, animated score cards, history, details, and about pages
- Docker and Docker Compose support
- Backend unit tests

## Quick Start

### Backend

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
uvicorn app.main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173`.

## Environment

`backend/.env.example` contains all supported settings. Groq and Gemini are optional:

```env
LLM_PROVIDER=groq
ALLOW_LOCAL_FALLBACK=false
GROQ_API_KEY=
GROQ_MODEL=openai/gpt-oss-120b
GEMINI_API_KEY=
GEMINI_MODEL=gemini-1.5-flash
DATABASE_URL=sqlite:///./app.db
```

With `LLM_PROVIDER=groq`, Groq is required and the API returns a `503` if the key is missing or invalid. Set `LLM_PROVIDER=local` only for offline development.

## API

- `POST /evaluate`
- `GET /history`
- `GET /evaluation/{id}`
- `DELETE /history/{id}`
- `GET /health`

Interactive docs are available at `http://localhost:8000/docs`.

## Docker

```bash
docker compose up --build
```

Frontend: `http://localhost:5173`

Backend: `http://localhost:8000`

## Testing

```bash
cd backend
pytest
```

## Deployment Notes

- Set `GROQ_API_KEY` or `GEMINI_API_KEY` in the backend environment for LLM-enhanced grading.
- Use a persistent volume for SQLite in small deployments.
- For larger deployments, swap SQLAlchemy URL to PostgreSQL and run behind a reverse proxy.
- Configure CORS origins with `ALLOWED_ORIGINS`.
