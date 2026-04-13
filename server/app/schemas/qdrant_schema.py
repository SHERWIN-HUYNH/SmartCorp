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
    effective_date: int = Field(default_factory=lambda: int(datetime.utcnow().timestamp()))


class Point(BaseModel):
    id: str
    vector: Vector
    payload: Payload

    @staticmethod
    def _first_non_empty_string(value: object) -> Optional[str]:
        if value is None:
            return None

        if isinstance(value, str):
            value = value.strip()
            return value or None

        if isinstance(value, list):
            for item in value:
                if item is None:
                    continue
                item_str = str(item).strip()
                if item_str:
                    return item_str
            return None

        value_str = str(value).strip()
        return value_str or None

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
        effective_date: Optional[int] = None,
    ) -> "Point":
        if role_allowed is None:
            role_allowed = ["general"]

        if upload_date is None:
            upload_date = int(datetime.utcnow().timestamp())

        if effective_date is None:
            effective_date = upload_date

        chunk_type_value = chunk.get("type", ChunkType.TEXT.value)
        try:
            chunk_type = ChunkType(chunk_type_value)
        except ValueError:
            chunk_type = ChunkType.TEXT

        table_url_value = None
        image_url_value = None

        if chunk_type == ChunkType.TABLE:
            table_url_value = cls._first_non_empty_string(chunk.get("table_url"))
            if not table_url_value:
                table_url_value = cls._first_non_empty_string(chunk.get("raw_table"))

        if chunk_type == ChunkType.IMAGE:
            image_url_value = cls._first_non_empty_string(chunk.get("image_url"))
            if not image_url_value:
                image_url_value = cls._first_non_empty_string(chunk.get("image_b64"))

        payload = Payload(
            document_id=document_id,
            page=int(chunk.get("page", 0) or 0),
            role_allowed=role_allowed,
            content=str(chunk.get("text", "")),
            type=chunk_type,
            parent_id=str(chunk.get("parent_id", "")),
            order=int(chunk.get("order", 0) or 0),
            table_url=table_url_value,
            image_url=image_url_value,
            upload_date=upload_date,
            effective_date=effective_date,
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