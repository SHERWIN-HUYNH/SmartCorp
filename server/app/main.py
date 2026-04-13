from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings
from app import model  # noqa: F401
from app.routers.auth import router as auth_router
from app.routers.items import router as document_router
from app.routers.qdrant import router as qdrant_router
from app.routers.role_management import router as role_management_router

settings = get_settings()

app = FastAPI(title="SmartCope API")

app.add_middleware(
	CORSMiddleware,
	allow_origins=settings.cors_origins_list,
	allow_credentials=True,
	allow_methods=["*"],
	allow_headers=["*"],
)

app.include_router(auth_router, prefix="/api")
app.include_router(document_router, prefix="/api")
app.include_router(qdrant_router, prefix="/api")
app.include_router(role_management_router, prefix="/api")


@app.get("/healthz")
def health_check():
	return {"status": "ok"}
