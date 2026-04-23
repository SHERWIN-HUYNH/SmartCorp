import hashlib
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status
from jose import JWTError, jwt
from sqlalchemy import and_, func, or_
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, selectinload

from app.core.config import get_settings
from app.core.dependencies import get_current_user, require_role_manager
from app.db.database import get_db
from app.helpers.role_helpers import normalize_role_name
from app.model.document import Document
from app.model.document_membership import DocumentMembership
from app.model.document_permission import DocumentPermission
from app.model.role import Role
from app.model.user import User
from app.schemas.document import (
	ConfirmDocumentUploadRequest,
	ConfirmDocumentUploadResponse,
	DocumentListResponse,
	DocumentStatsResponse,
	DocumentQueueResponse,
	DocumentResponse,
	DocumentUploadResponse,
	PrecheckDocumentRequest,
	PrecheckDocumentResponse,
	QueueDocumentResponse,
	UpdateDocumentPermissionsRequest,
)
from app.services.cloudflare_service import CloudflareR2Service
from app.services.qdrant_service import QdrantService
from app.tasks.ingestion_tasks import process_document_ingestion, sync_document_role_payload

router = APIRouter(prefix="/documents", tags=["documents"])
settings = get_settings()


def _compute_sha256(file_bytes: bytes) -> str:
	return hashlib.sha256(file_bytes).hexdigest()


def _create_upload_token(
	user_id: str,
	file_url: str,
	filename: str,
	mime_type: str | None,
	file_size_bytes: int,
	file_hash: str,
) -> str:
	expire = datetime.now(timezone.utc) + timedelta(minutes=15)
	payload = {
		"sub": user_id,
		"type": "document_upload",
		"exp": expire,
		"file_url": file_url,
		"filename": filename,
		"mime_type": mime_type,
		"file_size_bytes": file_size_bytes,
		"file_hash": file_hash,
	}
	return jwt.encode(payload, settings.JWT_ACCESS_SECRET, algorithm=settings.JWT_ALGORITHM)


def _decode_upload_token(upload_token: str) -> dict:
	try:
		payload = jwt.decode(upload_token, settings.JWT_ACCESS_SECRET, algorithms=[settings.JWT_ALGORITHM])
	except JWTError as exc:
		raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid upload token") from exc

	if payload.get("type") != "document_upload":
		raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid upload token type")

	return payload


def _store_file_locally(filename: str, file_bytes: bytes) -> str:
	safe_name = Path(filename).name or f"{uuid.uuid4()}.bin"
	save_dir = Path(settings.LOCAL_STORAGE_ROOT).resolve()
	save_dir.mkdir(parents=True, exist_ok=True)

	save_path = save_dir / f"{uuid.uuid4()}-{safe_name}"
	save_path.write_bytes(file_bytes)

	return f"file://{save_path.as_posix()}"


def _store_uploaded_file(file: UploadFile, file_bytes: bytes) -> str:
	safe_name = Path(file.filename or "upload.bin").name
	object_key = f"documents/{uuid.uuid4()}-{safe_name}"

	try:
		cloudflare = CloudflareR2Service()
		return cloudflare.upload_document_file(
			file_bytes=file_bytes,
			filename=object_key,
			content_type=file.content_type,
		)
	except Exception:
		return _store_file_locally(safe_name, file_bytes)


def _find_active_duplicate(db: Session, file_hash: str) -> Document | None:
	return (
		db.query(Document)
		.filter(
			Document.file_hash == file_hash,
			Document.deleted_at.is_(None),
		)
		.first()
	)


def _validate_role_ids(db: Session, role_ids: list[uuid.UUID]) -> list[uuid.UUID]:
	unique_role_ids = sorted(set(role_ids))
	existing_role_ids = {
		role_id
		for (role_id,) in db.query(Role.id).filter(Role.id.in_(unique_role_ids)).all()
	}
	if len(existing_role_ids) != len(unique_role_ids):
		raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="One or more role_ids are invalid")

	return unique_role_ids


def _upsert_document_permissions(db: Session, document_id: uuid.UUID, role_ids: list[uuid.UUID]) -> None:
	if not role_ids:
		return

	values = [{"role_id": role_id, "document_id": document_id} for role_id in role_ids]
	stmt = pg_insert(DocumentPermission).values(values)
	stmt = stmt.on_conflict_do_nothing(index_elements=["role_id", "document_id"])
	db.execute(stmt)


def _ensure_document_membership(db: Session, user_id: uuid.UUID, document_id: uuid.UUID) -> None:
	stmt = pg_insert(DocumentMembership).values(user_id=user_id, document_id=document_id)
	stmt = stmt.on_conflict_do_nothing(index_elements=["user_id", "document_id"])
	db.execute(stmt)


def _get_document_role_names(db: Session, document_id: uuid.UUID) -> list[str]:
	role_names = [
		role_name
		for (role_name,) in (
			db.query(Role.name)
			.join(DocumentPermission, DocumentPermission.role_id == Role.id)
			.filter(DocumentPermission.document_id == document_id)
			.distinct()
			.all()
		)
		if role_name
	]

	return sorted(set(role_names)) or ["general"]


def _visible_documents_query(db: Session, user_id: uuid.UUID):
	return (
		db.query(Document)
		.outerjoin(
			DocumentMembership,
			and_(
				DocumentMembership.document_id == Document.id,
				DocumentMembership.user_id == user_id,
			),
		)
		.filter(
			or_(
				Document.user_id == user_id,
				DocumentMembership.user_id.is_not(None),
			)
		)
	)


def _get_visible_document(
	db: Session,
	current_user: User,
	document_id: uuid.UUID,
	*,
	include_deleted: bool = False,
) -> Document:
	query = _visible_documents_query(db, current_user.id).filter(Document.id == document_id)
	if not include_deleted:
		query = query.filter(Document.deleted_at.is_(None))

	document = query.first()
	if not document:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")

	return document


def _to_document_response(document: Document) -> DocumentResponse:
	role_ids = [permission.role_id for permission in document.permissions]
	return DocumentResponse(
		id=document.id,
		filename=document.filename,
		file_url=document.file_url,
		file_size_bytes=document.file_size_bytes,
		mime_type=document.mime_type,
		file_hash=document.file_hash,
		effective_date=document.effective_date,
		status=document.status,
		error_message=document.error_message,
		deleted_at=document.deleted_at,
		created_at=document.created_at,
		updated_at=document.updated_at,
		role_ids=role_ids,
	)


def _get_owned_document(
	db: Session,
	current_user: User,
	document_id: uuid.UUID,
	*,
	include_deleted: bool = False,
) -> Document:
	query = db.query(Document).filter(Document.id == document_id, Document.user_id == current_user.id)
	if not include_deleted:
		query = query.filter(Document.deleted_at.is_(None))

	document = query.first()
	if not document:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")

	return document


def _try_sync_qdrant_role_allowed(document_id: uuid.UUID, role_allowed: list[str]) -> bool:
	qdrant_service = QdrantService(settings.QDRANT_HOST, settings.QDRANT_COLLECTION)
	qdrant_service.update_document_role_allowed(
		document_id=str(document_id),
		role_allowed=role_allowed,
		timeout_seconds=0.5,
	)
	return True


def _merge_duplicate_document_access(
	db: Session,
	current_user: User,
	document: Document,
	role_ids: list[uuid.UUID],
) -> ConfirmDocumentUploadResponse:
	_upsert_document_permissions(db, document.id, role_ids)
	_ensure_document_membership(db, current_user.id, document.id)
	document.updated_at = datetime.now(timezone.utc)
	db.add(document)
	db.commit()
	db.refresh(document)

	role_allowed = _get_document_role_names(db, document.id)
	qdrant_sync_queued = False
	task_id = None
	try:
		_try_sync_qdrant_role_allowed(document.id, role_allowed)
	except Exception:
		qdrant_sync_queued = True
		try:
			task = sync_document_role_payload.delay(str(document.id))
			task_id = task.id
		except Exception:
			pass

	return ConfirmDocumentUploadResponse(
		message="Document already exists. Permissions merged.",
		document=_to_document_response(document),
		task_id=task_id,
		merged=True,
		qdrant_sync_queued=qdrant_sync_queued,
	)


@router.post("/precheck", response_model=PrecheckDocumentResponse)
def precheck_document(
	payload: PrecheckDocumentRequest,
	db: Session = Depends(get_db),
	current_user: User = Depends(require_role_manager),
):
	duplicate = _find_active_duplicate(db, payload.file_hash)
	if not duplicate:
		return PrecheckDocumentResponse(duplicate=False, existing_document=None)

	return PrecheckDocumentResponse(duplicate=True, existing_document=None)


@router.post("/upload", response_model=DocumentUploadResponse)
async def upload_document_file(
	file: UploadFile = File(...),
	db: Session = Depends(get_db),
	current_user: User = Depends(require_role_manager),
):
	file_bytes = await file.read()
	if not file_bytes:
		raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Uploaded file is empty")

	file_hash = _compute_sha256(file_bytes)
	duplicate = _find_active_duplicate(db, file_hash)
	if duplicate:
		raise HTTPException(
			status_code=status.HTTP_409_CONFLICT,
			detail={"message": "Duplicate file detected"},
		)

	file_url = _store_uploaded_file(file, file_bytes)

	upload_token = _create_upload_token(
		user_id=str(current_user.id),
		file_url=file_url,
		filename=file.filename or "uploaded-file",
		mime_type=file.content_type,
		file_size_bytes=len(file_bytes),
		file_hash=file_hash,
	)

	return DocumentUploadResponse(
		upload_token=upload_token,
		filename=file.filename or "uploaded-file",
		file_url=file_url,
		file_hash=file_hash,
		file_size_bytes=len(file_bytes),
		mime_type=file.content_type,
	)


@router.post("/confirm", response_model=ConfirmDocumentUploadResponse)
def confirm_upload(
	payload: ConfirmDocumentUploadRequest,
	db: Session = Depends(get_db),
	current_user: User = Depends(require_role_manager),
):
	unique_role_ids = _validate_role_ids(db, payload.role_ids)

	upload_payload: dict | None = None
	resolved_hash = str(payload.file_hash or "").strip().lower()
	if payload.upload_token:
		upload_payload = _decode_upload_token(payload.upload_token)
		if upload_payload.get("sub") != str(current_user.id):
			raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Upload token does not belong to user")

		token_hash = str(upload_payload.get("file_hash", "")).strip().lower()
		if payload.client_file_hash and payload.client_file_hash.strip().lower() != token_hash:
			raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="File hash mismatch")
		resolved_hash = token_hash

	if not resolved_hash:
		raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Missing file hash")

	duplicate = _find_active_duplicate(db, resolved_hash)
	if duplicate:
		return _merge_duplicate_document_access(
			db=db,
			current_user=current_user,
			document=duplicate,
			role_ids=unique_role_ids,
		)

	if upload_payload is None:
		raise HTTPException(
			status_code=status.HTTP_409_CONFLICT,
			detail="Document does not exist yet. Please upload the file first.",
		)

	document = Document(
		user_id=current_user.id,
		filename=str(upload_payload.get("filename", "uploaded-file")),
		file_url=str(upload_payload.get("file_url", "")),
		file_size_bytes=int(upload_payload.get("file_size_bytes", 0) or 0),
		mime_type=upload_payload.get("mime_type"),
		file_hash=resolved_hash,
		effective_date=payload.effective_date,
		status="pending",
	)

	task_id = None
	try:
		db.add(document)
		db.flush()
		_upsert_document_permissions(db, document.id, unique_role_ids)
		_ensure_document_membership(db, current_user.id, document.id)

		try:
			task = process_document_ingestion.delay(str(document.id))
			task_id = task.id
		except Exception as exc:
			document.status = "failed"
			document.error_message = f"Queueing failed: {exc}"

		db.add(document)
		db.commit()
		db.refresh(document)
	except IntegrityError:
		db.rollback()
		race_duplicate = _find_active_duplicate(db, resolved_hash)
		if race_duplicate:
			return _merge_duplicate_document_access(
				db=db,
				current_user=current_user,
				document=race_duplicate,
				role_ids=unique_role_ids,
			)
		raise

	return ConfirmDocumentUploadResponse(
		message="Upload confirmed and ingestion queued",
		document=_to_document_response(document),
		task_id=task_id,
		merged=False,
		qdrant_sync_queued=False,
	)


@router.get("/roles")
def list_roles(
	db: Session = Depends(get_db),
	current_user: User = Depends(get_current_user),
):
	# Endpoint is user-scoped by auth dependency; currently returns all roles.
	roles = db.query(Role).order_by(Role.name.asc()).all()
	return [
		{
			"id": str(role.id),
			"name": normalize_role_name(role.name),
			"description": role.description,
		}
		for role in roles
	]


@router.get("/stats", response_model=DocumentStatsResponse)
def get_document_stats(
	db: Session = Depends(get_db),
	current_user: User = Depends(get_current_user),
):
	rows = (
		_visible_documents_query(db, current_user.id)
		.with_entities(Document.status, func.count(Document.id))
		.group_by(Document.status)
		.all()
	)

	counts = {status_name: count for status_name, count in rows}
	total = sum(counts.values())

	return DocumentStatsResponse(
		total=total,
		pending=int(counts.get("pending", 0)),
		processing=int(counts.get("processing", 0)),
		ready=int(counts.get("ready", 0)),
		failed=int(counts.get("failed", 0)),
		deleted=int(counts.get("deleted", 0)),
	)


@router.get("", response_model=DocumentListResponse)
def list_documents(
	status_filter: str | None = Query(default=None, alias="status"),
	search: str | None = Query(default=None),
	include_deleted: bool = Query(default=False),
	limit: int = Query(default=20, ge=1, le=200),
	offset: int = Query(default=0, ge=0, le=settings.DOCUMENTS_MAX_OFFSET),
	db: Session = Depends(get_db),
	current_user: User = Depends(get_current_user),
):
	base_query = _visible_documents_query(db, current_user.id)
	if not include_deleted:
		base_query = base_query.filter(Document.deleted_at.is_(None))
	if status_filter:
		base_query = base_query.filter(Document.status == status_filter)
	if search and search.strip():
		term = f"%{search.strip()}%"
		base_query = base_query.filter(
			or_(
				Document.filename.ilike(term),
				Document.file_hash.ilike(term),
			)
		)

	total_count = base_query.with_entities(func.count(func.distinct(Document.id))).scalar() or 0
	documents = (
		base_query
		.options(selectinload(Document.permissions))
		.order_by(Document.created_at.desc(), Document.id.desc())
		.offset(offset)
		.limit(limit)
		.all()
	)
	return DocumentListResponse(
		items=[_to_document_response(doc) for doc in documents],
		total=total_count,
		total_count=total_count,
	)


@router.get("/queue", response_model=DocumentQueueResponse)
def list_processing_queue(
	include_failed: bool = Query(default=False),
	db: Session = Depends(get_db),
	current_user: User = Depends(require_role_manager),
):
	statuses = ["pending", "processing"]
	if include_failed:
		statuses.append("failed")

	queue_documents = (
		db.query(Document)
		.filter(
			Document.user_id == current_user.id,
			Document.deleted_at.is_(None),
			Document.status.in_(statuses),
		)
		.order_by(Document.created_at.desc())
		.limit(50)
		.all()
	)

	return DocumentQueueResponse(
		items=[
			QueueDocumentResponse(
				id=document.id,
				filename=document.filename,
				file_size_bytes=document.file_size_bytes,
				mime_type=document.mime_type,
				status=document.status,
				error_message=document.error_message,
				created_at=document.created_at,
				updated_at=document.updated_at,
			)
			for document in queue_documents
		],
		total=len(queue_documents),
	)


@router.put("/{document_id}/permissions", response_model=DocumentResponse)
def update_document_permissions(
	document_id: uuid.UUID,
	payload: UpdateDocumentPermissionsRequest,
	db: Session = Depends(get_db),
	current_user: User = Depends(get_current_user),
):
	document = _get_owned_document(db, current_user, document_id)

	unique_role_ids = sorted(set(payload.role_ids))
	existing_role_ids = {
		role_id
		for (role_id,) in db.query(Role.id).filter(Role.id.in_(unique_role_ids)).all()
	}
	if len(existing_role_ids) != len(unique_role_ids):
		raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="One or more role_ids are invalid")

	(
		db.query(DocumentPermission)
		.filter(DocumentPermission.document_id == document.id)
		.delete(synchronize_session=False)
	)

	for role_id in unique_role_ids:
		db.add(DocumentPermission(role_id=role_id, document_id=document.id))

	db.commit()
	db.refresh(document)

	return _to_document_response(document)


@router.post("/{document_id}/retry", response_model=ConfirmDocumentUploadResponse)
def retry_document_ingestion(
	document_id: uuid.UUID,
	db: Session = Depends(get_db),
	current_user: User = Depends(require_role_manager),
):
	document = _get_owned_document(db, current_user, document_id)

	if document.status != "failed":
		raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only failed documents can be retried")

	document.status = "pending"
	document.error_message = None
	db.add(document)

	task_id = None
	try:
		task = process_document_ingestion.delay(str(document.id))
		task_id = task.id
	except Exception as exc:
		document.status = "failed"
		document.error_message = f"Queueing failed: {exc}"

	db.add(document)
	db.commit()
	db.refresh(document)

	return ConfirmDocumentUploadResponse(
		message="Retry queued",
		document=_to_document_response(document),
		task_id=task_id,
	)


@router.delete("/{document_id}")
def soft_delete_document(
	document_id: uuid.UUID,
	db: Session = Depends(get_db),
	current_user: User = Depends(get_current_user),
):
	document = _get_owned_document(db, current_user, document_id)
	document.deleted_at = datetime.now(timezone.utc)
	document.status = "deleted"
	db.add(document)
	db.commit()

	return {"message": "Document deleted", "document_id": str(document.id)}


@router.get("/{document_id}", response_model=DocumentResponse)
def get_document(
	document_id: uuid.UUID,
	db: Session = Depends(get_db),
	current_user: User = Depends(get_current_user),
):
	document = _get_visible_document(db, current_user, document_id, include_deleted=True)

	return _to_document_response(document)
