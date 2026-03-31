import uuid
from datetime import datetime, timezone
from typing import List, Optional

from app.core.config import get_settings
from app.core.qdrant_api import QdrantAPI
from app.schemas.qdrant_schema import (
    DeletePointsRequest,
    HybridSearchRequest,
    Point,
    ChunkType,
    Vector,
    SparseVector,
    Payload
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
    
    def chunk_to_point(
        self,
        chunk: dict,
        document_id: str,
        dense_vector: List[float],
        sparse_indices: List[int],
        sparse_values: List[float],
        role_allowed: Optional[List[str]] = None,
        is_active: bool = True,
        effective_date: Optional[datetime] = None,
    ) -> Point:
        """Chuyển chunk thành Point theo qdrant_schema."""
        if role_allowed is None:
            role_allowed = ["general"]

        chunk_type_value = chunk.get("type", ChunkType.TEXT.value)
        try:
            chunk_type = ChunkType(chunk_type_value)
        except ValueError:
            chunk_type = ChunkType.TEXT

        payload = Payload(
            document_id=document_id,
            is_active=is_active,
            effective_date=effective_date or datetime.now(timezone.utc),
            page=int(chunk.get("page", 0) or 0),
            role_allowed=role_allowed,
            content=str(chunk.get("text", "")),
            type=chunk_type,
            parent_id=str(chunk.get("parent_id", "")),
            order=int(chunk.get("order", 0) or 0),
            table_url=chunk.get("table_url") if chunk_type == ChunkType.TABLE else None,
            image_url=chunk.get("image_url") if chunk_type == ChunkType.IMAGE else None,
        )

        vector = Vector(
            dense=dense_vector,
            sparse=SparseVector(indices=sparse_indices, values=sparse_values),
        )

        return Point(
            id=str(uuid.uuid4()),
            vector=vector,
            payload=payload,
        )

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
        effective_at: Optional[datetime] = None,
    ):
        body = HybridSearchRequest(
            dense_vector=dense_vector,
            sparse_indices=sparse_indices,
            sparse_values=sparse_values,
            dense_limit=dense_limit,
            sparse_limit=sparse_limit,
            limit=limit,
            role_allowed=role_allowed,
            effective_at=effective_at,
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