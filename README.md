# Yaude AI

AI coding and research assistant for African developers, students, and
researchers — starting in South Sudan. Bilingual by design (Juba Arabic +
English), built for constrained connectivity and local pricing.

## Structure

- `backend/` — model fine-tuning, evaluation, and FastAPI inference server.
  See `backend/README.md`.
- `frontend/` — Next.js web app. See `frontend/README.md`.
- `docs/` — business plan, pitch deck, brand guidelines, model eval notes.
- `infra/` — deployment config (Railway for backend, Vercel for frontend).

## Getting started

1. `cd backend`, follow `backend/README.md` to set up the Python
   environment and run the data/fine-tuning pipeline.
2. `cd frontend`, follow `frontend/README.md` to scaffold and run the web app.
3. Point the frontend at your local backend via `.env.local`
   (`NEXT_PUBLIC_API_URL=http://localhost:8000`).

## Status

Phase 1: coding + research assistant for South Sudanese students and
developers, fine-tuning Qwen2.5-Coder-1.5B-Instruct. See
`docs/model-eval-notes.md` for progress.
