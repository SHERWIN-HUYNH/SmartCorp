from typing import List, Optional

from app.core.qdrant_api import QdrantAPI
from app.schemas.qdrant_schema import (
    DeletePointsRequest,
    HybridSearchRequest,
    Point,
)


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
    
    def build_point_from_chunk(
        self,
        chunk: dict,
        document_id: str,
        dense_vector: List[float],
        sparse_indices: List[int],
        sparse_values: List[float],
        role_allowed: Optional[List[str]] = None,
        upload_date: Optional[int] = None,
        effective_date: Optional[int] = None,
    ) -> Point:
        return Point.from_chunk(
            chunk=chunk,
            document_id=document_id,
            dense_vector=dense_vector,
            sparse_indices=sparse_indices,
            sparse_values=sparse_values,
            role_allowed=role_allowed,
            upload_date=upload_date,
            effective_date=effective_date,
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
