from fastapi import Cookie, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.db.database import get_db
from app.helpers.role_helpers import resolve_user_role_name
from app.model.user import User
from app.services.auth_service import decode_access_token, get_user_by_id
from app.services.qdrant_service import QdrantService
import logging

logger = logging.getLogger(__name__)

settings = get_settings()


def get_qdrant_service() -> QdrantService:
    return QdrantService(
        host=settings.QDRANT_HOST,
        collection=settings.QDRANT_COLLECTION,
    )


def get_current_user(
    access_token: str | None = Cookie(default=None),
    db: Session = Depends(get_db),
) -> User:
    if not access_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")

    payload = decode_access_token(access_token)
    if not payload or payload.get("type") != "access":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")

    user_id = payload.get("sub")
    user = get_user_by_id(user_id, db)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")

    return user


def require_role_manager(current_user: User = Depends(get_current_user)) -> User:
    current_role = resolve_user_role_name(current_user)
    logger.warning(
        "RBAC check user_id=%s role=%s allowlist=%s role_id=%s role_str=%s",
        current_user.id,
        current_role,
        settings.role_manager_allowlist,
        current_user.role_id,
        current_user.role,
    )
    if current_role not in settings.role_manager_allowlist:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient role privileges")

    return current_user
