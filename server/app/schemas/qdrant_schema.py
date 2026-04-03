from enum import Enum
from pydantic import BaseModel, model_validator, Field
from datetime import datetime
from typing import List, Optional
import uuid


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

    table_url: Optional[str] = None
    image_url: Optional[str] = None

    is_active: bool = True
    upload_date: int = Field(default_factory=lambda: int(datetime.utcnow().timestamp()))


class Point(BaseModel):
    id: str
    vector: Vector
    payload: Payload

    @classmethod
    def from_chunk(
        cls,
        chunk: dict,
        document_id: str,
        dense_vector: List[float],
        sparse_indices: List[int],
        sparse_values: List[float],
        role_allowed: Optional[List[str]] = None,
        upload_date: Optional[int] = None,
    ) -> "Point":
        if role_allowed is None:
            role_allowed = ["general"]

        if upload_date is None:
            upload_date = int(datetime.utcnow().timestamp())

        chunk_type_value = chunk.get("type", ChunkType.TEXT.value)
        try:
            chunk_type = ChunkType(chunk_type_value)
        except ValueError:
            chunk_type = ChunkType.TEXT

        payload = Payload(
            document_id=document_id,
            page=int(chunk.get("page", 0) or 0),
            role_allowed=role_allowed,
            content=str(chunk.get("text", "")),
            type=chunk_type,
            parent_id=str(chunk.get("parent_id", "")),
            order=int(chunk.get("order", 0) or 0),
            table_url=(
                chunk.get("raw_table")[0]
                if chunk_type == ChunkType.TABLE and chunk.get("raw_table")
                else None
            ),
            image_url=(
                chunk.get("image_b64")[0]
                if chunk_type == ChunkType.IMAGE and chunk.get("image_b64")
                else None
            ),
            upload_date=upload_date,
            is_active=True,
        )

        vector = Vector(
            dense=dense_vector,
            sparse=SparseVector(indices=sparse_indices, values=sparse_values),
        )

        return cls(
            id=str(uuid.uuid4()),
            vector=vector,
            payload=payload,
        )


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