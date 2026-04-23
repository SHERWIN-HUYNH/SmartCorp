import uuid

from sqlalchemy import BIGINT, CheckConstraint, Column, DateTime, ForeignKey, Index, String, Text, func, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.database import Base


class Document(Base):
    __tablename__ = "documents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    filename = Column(String, nullable=False)
    file_url = Column(String, nullable=False)
    file_size_bytes = Column(BIGINT, nullable=True)
    mime_type = Column(String, nullable=True)
    file_hash = Column(String, nullable=False)

    effective_date = Column(DateTime(timezone=True), nullable=True)

    status = Column(String, nullable=False, default="pending", server_default="pending")
    error_message = Column(Text, nullable=True)

    deleted_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    user = relationship("User", back_populates="documents")
    permissions = relationship("DocumentPermission", back_populates="document", cascade="all, delete-orphan")
    memberships = relationship("DocumentMembership", back_populates="document", cascade="all, delete-orphan")

    __table_args__ = (
        CheckConstraint(
            "status IN ('pending', 'processing', 'ready', 'failed', 'deleted')",
            name="ck_documents_status",
        ),
        Index("idx_documents_user_status", "user_id", "status"),
        Index("idx_documents_effective_date", "effective_date"),
        Index(
            "idx_documents_active_created_id",
            "created_at",
            "id",
            postgresql_where=text("deleted_at IS NULL"),
        ),
        Index(
            "idx_documents_user_active_created_id",
            "user_id",
            "created_at",
            "id",
            postgresql_where=text("deleted_at IS NULL"),
        ),
        Index(
            "idx_documents_user_status_active_created_id",
            "user_id",
            "status",
            "created_at",
            "id",
            postgresql_where=text("deleted_at IS NULL"),
        ),
        Index(
            "uq_documents_file_hash_active",
            "file_hash",
            unique=True,
            postgresql_where=text("deleted_at IS NULL"),
        ),
    )