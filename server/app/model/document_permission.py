import uuid

from sqlalchemy import Column, DateTime, ForeignKey, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.database import Base


class DocumentPermission(Base):
    __tablename__ = "document_permissions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    role_id = Column(UUID(as_uuid=True), ForeignKey("roles.id", ondelete="CASCADE"), nullable=False, index=True)
    document_id = Column(UUID(as_uuid=True), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False, index=True)
    granted_at = Column(DateTime(timezone=True), server_default=func.now())

    role = relationship("Role", back_populates="document_permissions")
    document = relationship("Document", back_populates="permissions")

    __table_args__ = (
        UniqueConstraint("role_id", "document_id", name="uq_role_document_permission"),
    )