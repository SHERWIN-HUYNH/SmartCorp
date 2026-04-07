# SmartCope Startup

## One-command Docker startup (recommended for team onboarding)

Run from project root `SmartCope`:

1. Create docker env file from template:
	- Copy `.env.docker.example` to `.env.docker`
	- Fill in required values (`DATABASE_URL`, JWT secrets, API keys)
2. Start full stack:
	- `docker compose --env-file .env.docker up --build`

Services:
- Client: `http://localhost:3000`
- API: `http://localhost:8000`
- API health: `http://localhost:8000/healthz`
- Qdrant: `http://localhost:6333`

Optional OCR profile:
- `docker compose --env-file .env.docker --profile ocr run --rm tesseract --version`
docker compose --env-file .env.docker exec server python -m app.tests.test_rag
Stop all services:
- `docker compose down`

## Legacy local mode (manual)

# Khởi động server
source ./smartcope/Scripts/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Khởi động client
pnpm run dev