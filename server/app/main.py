from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings
from app.db.database import Base, engine
from app.model import user  # noqa: F401
from app.routers.auth import router as auth_router

settings = get_settings()

app = FastAPI(title="SmartCope API")

app.add_middleware(
	CORSMiddleware,
	allow_origins=settings.cors_origins_list,
	allow_credentials=True,
	allow_methods=["*"],
	allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)

app.include_router(auth_router, prefix="/api")


@app.get("/healthz")
def health_check():
	return {"status": "ok"}
