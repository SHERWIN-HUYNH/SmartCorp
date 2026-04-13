import requests
from datetime import datetime
from typing import List, Optional

from app.schemas.qdrant_schema import (
    DeletePointsRequest,
    HybridSearchRequest,
    Point,
)


class QdrantAPI:
    def __init__(self, host: str, collection: str):
        self.host = host
        self.collection = collection

    # ------------------------------ Collection ------------------------------

    def create_collection(self, vector_size: int = 1536):
        url = f"{self.host}/collections/{self.collection}"
        payload = {
            "vectors": {
                "dense": {
                    "size": vector_size,
                    "distance": "Cosine"
                }
            },
            "sparse_vectors": {
                "sparse": {}
            }
        }
        return requests.put(url, json=payload).json()

    def delete_collection(self):
        url = f"{self.host}/collections/{self.collection}"
        return requests.delete(url).json()

    def get_collection_info(self):
        url = f"{self.host}/collections/{self.collection}"
        return requests.get(url).json()

    def create_snapshot(self):
        url = f"{self.host}/collections/{self.collection}/snapshots"
        return requests.post(url).json()

    # ------------------------------ Points ------------------------------

    def upsert_points(self, points: List[Point]):
        url = f"{self.host}/collections/{self.collection}/points"

        payload = {
            "points": [
                {
                    "id": point.id,
                    "vector": {
                        "dense": point.vector.dense,
                        "sparse": {
                            "indices": point.vector.sparse.indices,
                            "values": point.vector.sparse.values,
                        }
                    },
                    "payload": point.payload.model_dump(mode="json")
                }
                for point in points
            ]
        }

        return requests.put(url, json=payload).json()

    def delete_points(self, body: DeletePointsRequest):
        url = f"{self.host}/collections/{self.collection}/points/delete"
        return requests.post(url, json={"points": body.ids}).json()

    def count_points(self):
        url = f"{self.host}/collections/{self.collection}/points/count"
        return requests.post(url, json={}).json()

    # ------------------------------ Search ------------------------------

    def hybrid_search(self, body: HybridSearchRequest):
        url = f"{self.host}/collections/{self.collection}/points/query"
        now_ts = int(datetime.utcnow().timestamp())

        query = {
            "prefetch": [
                {
                    "query": {
                        "indices": body.sparse_indices,
                        "values": body.sparse_values,
                    },
                    "using": "sparse",
                    "limit": body.sparse_limit,
                },
                {
                    "query": body.dense_vector,
                    "using": "dense",
                    "limit": body.dense_limit,
                }
            ],
            "query": {"fusion": "rrf"},
            "filter": {},
            "sort": [{"key": "upload_date", "order": "desc"}],
            "limit": body.limit,
            "with_payload": True,
        }

        active_filter = {
            "key": "is_active",
            "match": {"value": True}
        }
        effective_date_filter = {
            "key": "effective_date",
            "range": {"lte": now_ts},
        }

        must_filters = [active_filter, effective_date_filter]
        if body.role_allowed:
            must_filters.append(
                {
                    "key": "role_allowed",
                    "match": {"any": body.role_allowed}
                }
            )

        query["filter"] = {"must": must_filters}

        return requests.post(url, json=query).json()

    def scroll(self, filter_query: Optional[dict] = None, limit: int = 10):
        url = f"{self.host}/collections/{self.collection}/points/scroll"
        now_ts = int(datetime.utcnow().timestamp())

        payload = {"limit": limit, "sort": [{"key": "upload_date", "order": "desc"}]}

        active_filter = {
            "key": "is_active",
            "match": {"value": True}
        }
        effective_date_filter = {
            "key": "effective_date",
            "range": {"lte": now_ts},
        }

        if filter_query:
            if "must" in filter_query:
                filter_query["must"].append(active_filter)
                filter_query["must"].append(effective_date_filter)
            else:
                filter_query = {"must": [filter_query, active_filter, effective_date_filter]}
            payload["filter"] = filter_query
        else:
            payload["filter"] = {"must": [active_filter, effective_date_filter]}

        return requests.post(url, json=payload).json()

    def recommend(self, positive_ids: List[str], limit: int = 5):
        url = f"{self.host}/collections/{self.collection}/points/recommend"

        payload = {
            "positive": positive_ids,
            "limit": limit,
            "with_payload": True,
        }

        return requests.post(url, json=payload).json()

    # ------------------------------ Payload ------------------------------

    def create_payload_index(self, field_name: str, field_type: str = "keyword"):
        url = f"{self.host}/collections/{self.collection}/index"

        payload = {
            "field_name": field_name,
            "field_schema": field_type,
        }

        return requests.put(url, json=payload).json()
    
    def delete_payload_index(self, field_name: str):
        url = f"{self.host}/collections/{self.collection}/index/{field_name}"
        return requests.delete(url).json()