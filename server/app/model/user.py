# models.py
import uuid
from sqlalchemy import Column, String, DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.database import Base

# Định nghĩa các field của bảng User
class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    name = Column(String, nullable=False)

    # Transition field: keep legacy role string while gradually moving to role_id.
    role_id = Column(UUID(as_uuid=True), ForeignKey("roles.id"), nullable=True, index=True)
    
    role = Column(String, default="user", nullable=False)
    state = Column(String, default="active", nullable=False)
    
    refresh_token = Column(String, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    role_ref = relationship("Role", back_populates="users")
    documents = relationship("Document", back_populates="user", cascade="all, delete-orphan")