from enum import Enum
from pydantic import BaseModel, model_validator
from typing import List, Optional


class ChunkType(str, Enum):
    TEXT = "text"
    TABLE = "table"
    IMAGE = "image"


class SparseVector(BaseModel):
    indices: List[int]
    values: List[float]

    @model_validator(mode="after")
    def check_lengths_match(self) -> "SparseVector":
        if len(self.indices) != len(self.values):
            raise ValueError("indices and values must have the same length")
        return self


class Vector(BaseModel):
    dense: List[float]
    sparse: SparseVector


class Payload(BaseModel):
    document_id: str
    page: int
    role_allowed: List[str]

    content: str
    type: ChunkType

    parent_id: str
    order: int

    raw_table: Optional[str] = None
    image_b64: Optional[str] = None


class Point(BaseModel):
    id: str
    vector: Vector
    payload: Payload


class HybridSearchRequest(BaseModel):
    dense_vector: List[float]
    sparse_indices: List[int]
    sparse_values: List[float]
    dense_limit: int = 20
    sparse_limit: int = 20
    limit: int = 10
    role_allowed: Optional[List[str]] = None


class DeletePointsRequest(BaseModel):
    ids: List[str]