from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field, field_validator

from app.helpers.role_helpers import normalize_role_name


class RoleCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    description: str | None = Field(default=None, max_length=500)

    @field_validator("name")
    @classmethod
    def normalize_name(cls, value: str) -> str:
        normalized = normalize_role_name(value)
        if not normalized:
            raise ValueError("Role name must not be empty")
        return normalized


class RoleUpdateRequest(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=100)
    description: str | None = Field(default=None, max_length=500)

    @field_validator("name")
    @classmethod
    def normalize_name(cls, value: str | None) -> str | None:
        if value is None:
            return None

        normalized = normalize_role_name(value)
        if not normalized:
            raise ValueError("Role name must not be empty")
        return normalized


class RoleSummaryResponse(BaseModel):
    id: UUID
    name: str
    description: str | None = None
    created_at: datetime | None = None
    user_count: int = 0
    doc_count: int = 0
    category: str = "custom"
    is_system: bool = False


class RoleUserResponse(BaseModel):
    id: UUID
    name: str
    email: str
    state: str
    created_at: datetime | None = None


class RoleDocumentResponse(BaseModel):
    id: UUID
    filename: str
    status: str
    uploaded_by: str
    effective_date: datetime | None = None
    created_at: datetime | None = None


class RoleDetailResponse(RoleSummaryResponse):
    users: list[RoleUserResponse]
    documents: list[RoleDocumentResponse]


class RoleListResponse(BaseModel):
    items: list[RoleSummaryResponse]
    total: int


class RoleUsersResponse(BaseModel):
    items: list[RoleUserResponse]
    total: int


class RoleDocumentsResponse(BaseModel):
    items: list[RoleDocumentResponse]
    total: int


class RoleDeleteResponse(BaseModel):
    message: str
    role_id: UUID
