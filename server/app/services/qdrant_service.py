from typing import List, Optional

from app.core.config import get_settings
from app.core.qdrant_api import QdrantAPI
from app.schemas.qdrant import (
    DeletePointsRequest,
    HybridSearchRequest,
    Point,
)

settings = get_settings()


class QdrantService:
    def __init__(self, host: str, collection: str):
        self.qdrant = QdrantAPI(host, collection)

    # -------- Collection --------

    def create_collection(self, vector_size: int = 1536):
        return self.qdrant.create_collection(vector_size)

    def delete_collection(self):
        return self.qdrant.delete_collection()

    def get_collection_info(self):
        return self.qdrant.get_collection_info()

    def create_snapshot(self):
        return self.qdrant.create_snapshot()

    # -------- Points --------

    def upsert_points(self, points: List[Point]):
        if not points:
            raise ValueError("Points list is empty")
        return self.qdrant.upsert_points(points)

    def delete_points(self, ids: List[str]):
        body = DeletePointsRequest(ids=ids)
        return self.qdrant.delete_points(body)

    def count_points(self):
        return self.qdrant.count_points()

    # -------- Search --------

    def hybrid_search(
        self,
        dense_vector: List[float],
        sparse_indices: List[int],
        sparse_values: List[float],
        dense_limit: int = 20,
        sparse_limit: int = 20,
        limit: int = 10,
        role_allowed: Optional[List[str]] = None,
    ):
        body = HybridSearchRequest(
            dense_vector=dense_vector,
            sparse_indices=sparse_indices,
            sparse_values=sparse_values,
            dense_limit=dense_limit,
            sparse_limit=sparse_limit,
            limit=limit,
            role_allowed=role_allowed,
        )
        return self.qdrant.hybrid_search(body)

    def scroll(self, filter_query: Optional[dict] = None, limit: int = 10):
        return self.qdrant.scroll(filter_query, limit)

    def recommend(self, positive_ids: List[str], limit: int = 5):
        return self.qdrant.recommend(positive_ids, limit)

    # -------- Payload --------

    def create_payload_index(self, field_name: str, field_type: str = "keyword"):
        return self.qdrant.create_payload_index(field_name, field_type)


# Dependency Injection
def get_qdrant_service() -> QdrantService:
    return QdrantService(
        host=settings.QDRANT_HOST,
        collection=settings.QDRANT_COLLECTION,
    )