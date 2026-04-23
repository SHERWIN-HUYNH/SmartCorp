from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field, field_validator, model_validator


DocumentStatus = Literal["pending", "processing", "ready", "failed", "deleted"]


class DuplicateDocumentSummary(BaseModel):
    id: UUID
    filename: str
    status: DocumentStatus
    created_at: datetime


class PrecheckDocumentRequest(BaseModel):
    file_hash: str = Field(min_length=16, max_length=128)

    @field_validator("file_hash")
    @classmethod
    def normalize_hash(cls, value: str) -> str:
        return value.strip().lower()


class PrecheckDocumentResponse(BaseModel):
    duplicate: bool
    existing_document: DuplicateDocumentSummary | None = None


class DocumentUploadResponse(BaseModel):
    upload_token: str
    filename: str
    file_url: str
    file_hash: str
    file_size_bytes: int
    mime_type: str | None = None


class ConfirmDocumentUploadRequest(BaseModel):
    upload_token: str | None = None
    file_hash: str | None = None
    role_ids: list[UUID] = Field(min_length=1)
    effective_date: datetime | None = None
    client_file_hash: str | None = None

    @model_validator(mode="after")
    def validate_upload_identifier(self) -> "ConfirmDocumentUploadRequest":
        if not self.upload_token and not self.file_hash:
            raise ValueError("Either upload_token or file_hash is required")
        if self.file_hash:
            self.file_hash = self.file_hash.strip().lower()
        return self


class DocumentResponse(BaseModel):
    id: UUID
    filename: str
    file_url: str
    file_size_bytes: int | None = None
    mime_type: str | None = None
    file_hash: str
    effective_date: datetime | None = None
    status: DocumentStatus
    error_message: str | None = None
    deleted_at: datetime | None = None
    created_at: datetime
    updated_at: datetime | None = None
    role_ids: list[UUID]


class ConfirmDocumentUploadResponse(BaseModel):
    message: str
    document: DocumentResponse
    task_id: str | None = None
    merged: bool = False
    qdrant_sync_queued: bool = False


class DocumentListResponse(BaseModel):
    items: list[DocumentResponse]
    total: int
    total_count: int


class QueueDocumentResponse(BaseModel):
    id: UUID
    filename: str
    file_size_bytes: int | None = None
    mime_type: str | None = None
    status: DocumentStatus
    error_message: str | None = None
    created_at: datetime
    updated_at: datetime | None = None


class DocumentQueueResponse(BaseModel):
    items: list[QueueDocumentResponse]
    total: int


class UpdateDocumentPermissionsRequest(BaseModel):
    role_ids: list[UUID] = Field(min_length=1)


class DocumentStatsResponse(BaseModel):
    total: int
    pending: int
    processing: int
    ready: int
    failed: int
    deleted: int
