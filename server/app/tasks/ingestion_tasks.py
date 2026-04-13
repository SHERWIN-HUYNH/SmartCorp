from __future__ import annotations

import tempfile
from pathlib import Path
from urllib.parse import unquote, urlparse

import requests
from fastembed import SparseTextEmbedding
from openai import OpenAI
from sqlalchemy.exc import OperationalError, SQLAlchemyError

from app.core.celery_app import celery_app
from app.core.config import get_settings
from app.db.database import SessionLocal
from app.model.document import Document
from app.services.chunking_service import ChunkingService
from app.services.cloudflare_service import CloudflareR2Service
from app.services.embedding_service import EmbeddingService
from app.services.ingestion_service import IngestionService
from app.services.qdrant_service import QdrantService

settings = get_settings()


def _update_document_status(document_id: str, status: str, error_message: str | None = None) -> None:
    status_db = SessionLocal()
    try:
        document = status_db.query(Document).filter(Document.id == document_id).first()
        if not document:
            return

        document.status = status
        document.error_message = error_message
        status_db.add(document)
        status_db.commit()
    except SQLAlchemyError:
        status_db.rollback()
    finally:
        status_db.close()


def _is_transient_db_error(exc: Exception) -> bool:
    text = str(exc).lower()
    markers = (
        "ssl connection has been closed unexpectedly",
        "server closed the connection unexpectedly",
        "connection reset by peer",
        "could not receive data from server",
        "connection not open",
    )
    return any(marker in text for marker in markers)


def _resolve_local_file_path(file_url: str) -> Path:
    parsed = urlparse(file_url)
    if parsed.scheme != "file":
        raise ValueError("Not a local file URL")

    file_path = unquote(parsed.path or "")
    # On Windows file:// URLs, parsed path looks like /C:/...
    if file_path.startswith("/") and len(file_path) >= 3 and file_path[2] == ":":
        file_path = file_path[1:]

    resolved = Path(file_path)
    if not resolved.exists():
        raise FileNotFoundError(f"File not found: {resolved}")

    return resolved


def _download_to_temp_file(file_url: str) -> Path:
    file_bytes: bytes | None = None
    primary_error: Exception | None = None

    try:
        response = requests.get(file_url, timeout=60)
        response.raise_for_status()
        file_bytes = response.content
    except requests.RequestException as exc:
        primary_error = exc

        # Fallback: if public URL fetch fails, try authenticated R2 object download.
        parsed = urlparse(file_url)
        object_key = unquote(parsed.path or "").lstrip("/")
        if not object_key:
            raise RuntimeError(f"Cannot resolve object key from URL: {file_url}") from exc

        try:
            cloudflare = CloudflareR2Service()
            object_response = cloudflare.s3_client.get_object(
                Bucket=cloudflare.bucket_name,
                Key=object_key,
            )
            body = object_response.get("Body")
            if body is None:
                raise RuntimeError("R2 get_object returned empty body")
            file_bytes = body.read()
        except Exception as fallback_exc:
            raise RuntimeError(
                "Failed to download file from public URL and authenticated R2 fallback failed. "
                f"public_error={primary_error}; fallback_error={fallback_exc}"
            ) from fallback_exc

    if not file_bytes:
        raise RuntimeError("Downloaded file is empty")

    suffix = Path(urlparse(file_url).path).suffix or ".bin"
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
    temp_file.write(file_bytes)
    temp_file.flush()
    temp_file.close()
    return Path(temp_file.name)


def _resolve_input_file(file_url: str) -> tuple[Path, bool]:
    parsed = urlparse(file_url)
    if parsed.scheme == "file":
        return _resolve_local_file_path(file_url), False

    if parsed.scheme in {"http", "https"}:
        downloaded = _download_to_temp_file(file_url)
        return downloaded, True

    raise ValueError(f"Unsupported file URL scheme: {parsed.scheme or 'unknown'}")


def _build_ingestion_service() -> IngestionService:
    api_key = settings.OPENAI_API_KEY
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is not configured")

    client = OpenAI(api_key=api_key)
    sparse_model = SparseTextEmbedding("Qdrant/bm25")
    qdrant_service = QdrantService(settings.QDRANT_HOST, settings.QDRANT_COLLECTION)

    # Best effort index setup; no-op if already created.
    for field_name, field_type in (
        ("role_allowed", "keyword"),
        ("document_id", "keyword"),
        ("is_active", "bool"),
        ("upload_date", "integer"),
        ("effective_date", "integer"),
    ):
        try:
            qdrant_service.create_payload_index(field_name, field_type)
        except Exception:
            pass

    chunking_service = ChunkingService(client, verbose=False)
    embedding_service = EmbeddingService(client, sparse_model)
    return IngestionService(chunking_service, embedding_service, qdrant_service, verbose=False)


@celery_app.task(
    name="app.tasks.ingestion_tasks.process_document_ingestion",
    bind=True,
    max_retries=3,
    default_retry_delay=30,
)
def process_document_ingestion(self, document_id: str):
    db = SessionLocal()
    temp_file_path: Path | None = None

    try:
        document = db.query(Document).filter(Document.id == document_id).first()
        if not document:
            return {"status": "not_found", "document_id": document_id}

        role_allowed = [permission.role.name for permission in document.permissions if permission.role and permission.role.name]
        if not role_allowed:
            role_allowed = ["general"]

        document.status = "processing"
        document.error_message = None
        db.add(document)
        db.commit()

        input_file, should_cleanup = _resolve_input_file(document.file_url)
        if should_cleanup:
            temp_file_path = input_file

        ingestion_service = _build_ingestion_service()
        chunks = ingestion_service.ingest_pdf(
            file_path=str(input_file),
            document_id=str(document.id),
            role_allowed=role_allowed,
            effective_date=document.effective_date,
        )

        if chunks is None:
            raise RuntimeError("Ingestion pipeline returned no output")

        document.status = "ready"
        document.error_message = None
        db.add(document)
        db.commit()

        return {
            "status": "ready",
            "document_id": document_id,
            "chunks": len(chunks),
        }
    except OperationalError as exc:
        db.rollback()

        error_text = str(exc)
        retry_count = int(getattr(self.request, "retries", 0))
        max_retries = int(getattr(self, "max_retries", 3))
        if _is_transient_db_error(exc) and retry_count < max_retries:
            _update_document_status(
                document_id=document_id,
                status="processing",
                error_message=f"Retrying DB ({retry_count + 1}): {error_text}",
            )
            countdown = min(60 * (2 ** retry_count), 300)
            raise self.retry(exc=exc, countdown=countdown)

        _update_document_status(
            document_id=document_id,
            status="failed",
            error_message=error_text,
        )
        return {
            "status": "failed",
            "document_id": document_id,
            "error": error_text,
        }
    except SQLAlchemyError as exc:
        db.rollback()
        raise exc
    except Exception as exc:
        db.rollback()

        # Configuration errors are not transient and should fail fast.
        error_text = str(exc)
        non_retryable_markers = (
            "OPENAI_API_KEY is not configured",
            "Missing required Cloudflare R2 env var",
        )
        if any(marker in error_text for marker in non_retryable_markers):
            _update_document_status(
                document_id=document_id,
                status="failed",
                error_message=error_text,
            )

            return {
                "status": "failed",
                "document_id": document_id,
                "error": error_text,
            }

        retry_count = int(getattr(self.request, "retries", 0))
        if retry_count < int(getattr(self, "max_retries", 3)):
            _update_document_status(
                document_id=document_id,
                status="processing",
                error_message=f"Retrying ({retry_count + 1}): {exc}",
            )

            countdown = min(60 * (2 ** retry_count), 300)
            raise self.retry(exc=exc, countdown=countdown)

        _update_document_status(
            document_id=document_id,
            status="failed",
            error_message=str(exc),
        )

        return {
            "status": "failed",
            "document_id": document_id,
            "error": str(exc),
        }
    finally:
        if temp_file_path and temp_file_path.exists():
            try:
                temp_file_path.unlink(missing_ok=True)
            except OSError:
                pass
        db.close()