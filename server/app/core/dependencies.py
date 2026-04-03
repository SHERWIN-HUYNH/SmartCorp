from app.core.config import get_settings
from app.services.qdrant_service import QdrantService


settings = get_settings()


def get_qdrant_service() -> QdrantService:
    return QdrantService(
        host=settings.QDRANT_HOST,
        collection=settings.QDRANT_COLLECTION,
    )
