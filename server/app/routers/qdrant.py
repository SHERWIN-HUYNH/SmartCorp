from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional
from pydantic import BaseModel

from app.services.qdrant_service import QdrantService, get_qdrant_service
from app.schemas.qdrant import (
    Point,
    HybridSearchRequest,
    DeletePointsRequest,
)

router = APIRouter(prefix="/qdrant", tags=["qdrant"])


# -------- Request bodies --------

class ScrollRequest(BaseModel):
    filter_query: Optional[dict] = None
    limit: int = 10

class RecommendRequest(BaseModel):
    positive_ids: List[str]
    limit: int = 5


# -------- Collection --------

@router.post("/collection")
def create_collection(service: QdrantService = Depends(get_qdrant_service)):
    try:
        return service.create_collection()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/collection")
def delete_collection(service: QdrantService = Depends(get_qdrant_service)):
    return service.delete_collection()


@router.get("/collection")
def get_collection(service: QdrantService = Depends(get_qdrant_service)):
    return service.get_collection_info()


@router.post("/snapshot")
def snapshot(service: QdrantService = Depends(get_qdrant_service)):
    return service.create_snapshot()


# -------- Points --------

@router.post("/points")
def upsert_points(
    points: List[Point],
    service: QdrantService = Depends(get_qdrant_service),
):
    return service.upsert_points(points)          # bỏ model_dump()


@router.delete("/points")
def delete_points(
    req: DeletePointsRequest,
    service: QdrantService = Depends(get_qdrant_service),
):
    return service.delete_points(req.ids)


@router.get("/points/count")
def count_points(service: QdrantService = Depends(get_qdrant_service)):
    return service.count_points()


# -------- Search --------

@router.post("/search")
def hybrid_search(
    req: HybridSearchRequest,
    service: QdrantService = Depends(get_qdrant_service),
):
    return service.hybrid_search(
        dense_vector=req.dense_vector,
        sparse_indices=req.sparse_indices,
        sparse_values=req.sparse_values,
        dense_limit=req.dense_limit,
        sparse_limit=req.sparse_limit,
        limit=req.limit,
        role_allowed=req.role_allowed,            # departments → role_allowed
    )


@router.post("/scroll")
def scroll(
    req: ScrollRequest,
    service: QdrantService = Depends(get_qdrant_service),
):
    return service.scroll(req.filter_query, req.limit)


@router.post("/recommend")
def recommend(
    req: RecommendRequest,
    service: QdrantService = Depends(get_qdrant_service),
):
    return service.recommend(req.positive_ids, req.limit)


# -------- Payload --------

@router.post("/payload/index")
def create_index(
    field_name: str,
    field_type: str = "keyword",
    service: QdrantService = Depends(get_qdrant_service),
):
    return service.create_payload_index(field_name, field_type)