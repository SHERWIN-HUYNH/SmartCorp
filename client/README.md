<div align="center">
<img width="1200" height="475" alt="GHBanner" src="https://github.com/user-attachments/assets/0aa67016-6eaf-458a-adb2-6e31a0763ed6" />
</div>

# Run and deploy your AI Studio app

This contains everything you need to run your app locally.

View your app in AI Studio: https://ai.studio/apps/f7aaa30a-128b-4180-832f-31640f6dbaba

## Run Locally

**Prerequisites:**  Node.js


1. Install dependencies:
   `npm install`
2. Set the `GEMINI_API_KEY` in [.env.local](.env.local) to your Gemini API key
3. Run the app:
   `npm run dev`

## Run Full Project With Docker (Recommended for Team Onboarding)

From project root `SmartCope`:

1. Copy `.env.docker.example` to `.env.docker`
2. Fill required env vars (`DATABASE_URL`, JWT secrets, API keys)
3. Start all services:
   `docker compose --env-file .env.docker up --build`

Endpoints:
- Client: `http://localhost:3000`
- API: `http://localhost:8000`
- API health: `http://localhost:8000/healthz`
- Qdrant: `http://localhost:6333`

Optional OCR profile:
`docker compose --env-file .env.docker --profile ocr run --rm tesseract --version`
