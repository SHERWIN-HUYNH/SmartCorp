from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import and_, func, or_
from sqlalchemy.orm import Session

from app.core.dependencies import require_role_manager
from app.db.database import get_db
from app.helpers.role_helpers import normalize_role_name
from app.model.document import Document
from app.model.document_permission import DocumentPermission
from app.model.role import Role
from app.model.user import User
from app.schemas.role import (
    RoleCreateRequest,
    RoleDetailResponse,
    RoleDeleteResponse,
    RoleDocumentResponse,
    RoleDocumentsResponse,
    RoleListResponse,
    RoleSummaryResponse,
    RoleUserResponse,
    RoleUsersResponse,
    RoleUpdateRequest,
)

router = APIRouter(prefix="/roles", tags=["roles"])

SYSTEM_ROLE_NAMES = {"admin", "user"}
ROLE_DETAIL_PREVIEW_LIMIT = 12


def _is_system_role(role_name: str) -> bool:
    return normalize_role_name(role_name) in SYSTEM_ROLE_NAMES


def _role_user_match_clause(role: Role):
    normalized_name = normalize_role_name(role.name)
    return or_(
        User.role_id == role.id,
        and_(
            User.role_id.is_(None),
            func.lower(func.trim(User.role)) == normalized_name,
        ),
    )


def _query_role_users(db: Session, role: Role):
    return db.query(User).filter(_role_user_match_clause(role))


def _query_role_documents(db: Session, role: Role, include_deleted: bool = False):
    query = (
        db.query(Document)
        .join(DocumentPermission, DocumentPermission.document_id == Document.id)
        .filter(DocumentPermission.role_id == role.id)
    )
    if not include_deleted:
        query = query.filter(Document.deleted_at.is_(None))
    return query


def _to_role_user_response(user: User) -> RoleUserResponse:
    return RoleUserResponse(
        id=user.id,
        name=user.name,
        email=user.email,
        state=user.state,
        created_at=user.created_at,
    )


def _to_role_document_response(document: Document) -> RoleDocumentResponse:
    return RoleDocumentResponse(
        id=document.id,
        filename=document.filename,
        status=document.status,
        uploaded_by=document.user.name if document.user else "Unknown",
        effective_date=document.effective_date,
        created_at=document.created_at,
    )


def _build_role_summary(db: Session, role: Role) -> RoleSummaryResponse:
    normalized_name = normalize_role_name(role.name)

    user_count = _query_role_users(db, role).count()

    doc_count = (
        db.query(func.count(func.distinct(DocumentPermission.document_id)))
        .join(Document, Document.id == DocumentPermission.document_id)
        .filter(
            DocumentPermission.role_id == role.id,
            Document.deleted_at.is_(None),
        )
        .scalar()
        or 0
    )

    return RoleSummaryResponse(
        id=role.id,
        name=normalized_name,
        description=role.description,
        created_at=role.created_at,
        user_count=int(user_count),
        doc_count=int(doc_count),
        category="core" if _is_system_role(normalized_name) else "custom",
        is_system=_is_system_role(normalized_name),
    )


def _get_role_or_404(db: Session, role_id: uuid.UUID) -> Role:
    role = db.query(Role).filter(Role.id == role_id).first()
    if not role:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Role not found")
    return role


@router.get("", response_model=RoleListResponse)
def list_roles(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role_manager),
):
    _ = current_user
    roles = db.query(Role).order_by(Role.name.asc()).all()
    summaries = [_build_role_summary(db, role) for role in roles]
    return RoleListResponse(items=summaries, total=len(summaries))


@router.get("/{role_id}", response_model=RoleDetailResponse)
def get_role_detail(
    role_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role_manager),
):
    _ = current_user
    role = _get_role_or_404(db, role_id)
    summary = _build_role_summary(db, role)
    users = (
        _query_role_users(db, role)
        .order_by(User.created_at.desc())
        .limit(ROLE_DETAIL_PREVIEW_LIMIT)
        .all()
    )
    documents = (
        _query_role_documents(db, role)
        .order_by(Document.created_at.desc())
        .limit(ROLE_DETAIL_PREVIEW_LIMIT)
        .all()
    )

    return RoleDetailResponse(
        **summary.model_dump(),
        users=[_to_role_user_response(user) for user in users],
        documents=[_to_role_document_response(document) for document in documents],
    )


@router.get("/{role_id}/users", response_model=RoleUsersResponse)
def get_role_users(
    role_id: uuid.UUID,
    search: str | None = Query(default=None),
    state: str | None = Query(default=None),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role_manager),
):
    _ = current_user
    role = _get_role_or_404(db, role_id)

    query = _query_role_users(db, role)
    if search and search.strip():
        term = f"%{search.strip().lower()}%"
        query = query.filter(
            or_(
                func.lower(User.name).like(term),
                func.lower(User.email).like(term),
            )
        )
    if state and state.strip():
        query = query.filter(func.lower(User.state) == state.strip().lower())

    total = query.count()
    users = query.order_by(User.created_at.desc()).offset(offset).limit(limit).all()
    return RoleUsersResponse(items=[_to_role_user_response(user) for user in users], total=total)


@router.put("/{role_id}/users/{user_id}", response_model=RoleUserResponse)
def assign_user_to_role(
    role_id: uuid.UUID,
    user_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role_manager),
):
    _ = current_user
    role = _get_role_or_404(db, role_id)

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    user.role_id = role.id
    user.role = normalize_role_name(role.name)
    db.add(user)
    db.commit()
    db.refresh(user)
    return _to_role_user_response(user)


@router.delete("/{role_id}/users/{user_id}", response_model=RoleUserResponse)
def remove_user_from_role(
    role_id: uuid.UUID,
    user_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role_manager),
):
    _ = current_user
    role = _get_role_or_404(db, role_id)

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    match_user = (
        user.role_id == role.id
        or (user.role_id is None and normalize_role_name(user.role) == normalize_role_name(role.name))
    )
    if not match_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User is not assigned to this role")

    user.role_id = None
    user.role = "user"
    db.add(user)
    db.commit()
    db.refresh(user)
    return _to_role_user_response(user)


@router.get("/{role_id}/documents", response_model=RoleDocumentsResponse)
def get_role_documents(
    role_id: uuid.UUID,
    search: str | None = Query(default=None),
    status_filter: str | None = Query(default=None, alias="status"),
    include_deleted: bool = Query(default=False),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role_manager),
):
    _ = current_user
    role = _get_role_or_404(db, role_id)

    query = _query_role_documents(db, role, include_deleted=include_deleted)
    if search and search.strip():
        term = f"%{search.strip().lower()}%"
        query = query.filter(func.lower(Document.filename).like(term))
    if status_filter and status_filter.strip():
        query = query.filter(Document.status == status_filter.strip().lower())

    total = query.count()
    documents = query.order_by(Document.created_at.desc()).offset(offset).limit(limit).all()
    return RoleDocumentsResponse(
        items=[_to_role_document_response(document) for document in documents],
        total=total,
    )


@router.put("/{role_id}/documents/{document_id}", response_model=RoleDocumentResponse)
def grant_document_to_role(
    role_id: uuid.UUID,
    document_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role_manager),
):
    _ = current_user
    _get_role_or_404(db, role_id)

    document = (
        db.query(Document)
        .filter(Document.id == document_id, Document.deleted_at.is_(None))
        .first()
    )
    if not document:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")

    permission = (
        db.query(DocumentPermission)
        .filter(
            DocumentPermission.role_id == role_id,
            DocumentPermission.document_id == document_id,
        )
        .first()
    )
    if permission:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Document already granted to role")

    db.add(DocumentPermission(role_id=role_id, document_id=document_id))
    db.commit()
    db.refresh(document)
    return _to_role_document_response(document)


@router.delete("/{role_id}/documents/{document_id}", response_model=RoleDocumentResponse)
def revoke_document_from_role(
    role_id: uuid.UUID,
    document_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role_manager),
):
    _ = current_user
    _ = _get_role_or_404(db, role_id)

    permission = (
        db.query(DocumentPermission)
        .filter(
            DocumentPermission.role_id == role_id,
            DocumentPermission.document_id == document_id,
        )
        .first()
    )
    if not permission:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document access not found for role")

    document = permission.document
    db.delete(permission)
    db.commit()
    return _to_role_document_response(document)


@router.post("", response_model=RoleSummaryResponse, status_code=status.HTTP_201_CREATED)
def create_role(
    payload: RoleCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role_manager),
):
    _ = current_user
    normalized_name = payload.name

    existing = db.query(Role).filter(Role.name == normalized_name).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Role name already exists")

    role = Role(name=normalized_name, description=payload.description)
    db.add(role)
    db.commit()
    db.refresh(role)

    return _build_role_summary(db, role)


@router.put("/{role_id}", response_model=RoleSummaryResponse)
def update_role(
    role_id: uuid.UUID,
    payload: RoleUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role_manager),
):
    _ = current_user
    role = _get_role_or_404(db, role_id)

    if payload.name is not None:
        existing = db.query(Role).filter(Role.name == payload.name, Role.id != role.id).first()
        if existing:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Role name already exists")
        role.name = payload.name

    if payload.description is not None:
        role.description = payload.description

    db.add(role)
    db.commit()
    db.refresh(role)

    return _build_role_summary(db, role)


@router.delete("/{role_id}", response_model=RoleDeleteResponse)
def delete_role(
    role_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role_manager),
):
    _ = current_user
    role = _get_role_or_404(db, role_id)

    if _is_system_role(role.name):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="System roles cannot be deleted")

    user_count = (
        db.query(func.count(User.id))
        .filter(
            or_(
                User.role_id == role.id,
                and_(
                    User.role_id.is_(None),
                    func.lower(func.trim(User.role)) == normalize_role_name(role.name),
                ),
            )
        )
        .scalar()
        or 0
    )

    doc_count = (
        db.query(func.count(func.distinct(DocumentPermission.document_id)))
        .filter(DocumentPermission.role_id == role.id)
        .scalar()
        or 0
    )

    if user_count > 0 or doc_count > 0:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "message": "Role is still in use and cannot be deleted",
                "users": int(user_count),
                "documents": int(doc_count),
            },
        )

    db.delete(role)
    db.commit()

    return RoleDeleteResponse(message="Role deleted", role_id=role.id)
