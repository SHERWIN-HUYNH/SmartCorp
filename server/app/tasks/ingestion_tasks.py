from __future__ import annotations

import random
import tempfile
from contextlib import contextmanager
from pathlib import Path
from threading import BoundedSemaphore
from urllib.parse import unquote, urlparse

import requests
from fastembed import SparseTextEmbedding
from openai import OpenAI
from redis import Redis
from redis.exceptions import RedisError
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

_INGESTION_SLOT_SEMAPHORE = BoundedSemaphore(max(1, settings.INGESTION_MAX_LOCAL_CONCURRENCY))
_DISTRIBUTED_LIMIT_REDIS_CLIENT: Redis | None = None


class RetryableIngestionError(RuntimeError):
    """Raised for transient failures that should be retried by Celery."""


@contextmanager
def _ingestion_slot_guard() -> None:
    acquired = _INGESTION_SLOT_SEMAPHORE.acquire(
        timeout=max(1, settings.INGESTION_SLOT_ACQUIRE_TIMEOUT_SECONDS)
    )
    if not acquired:
        raise RetryableIngestionError("ingestion local concurrency limit reached")

    try:
        yield
    finally:
        _INGESTION_SLOT_SEMAPHORE.release()


def _get_distributed_limit_redis_client() -> Redis | None:
    global _DISTRIBUTED_LIMIT_REDIS_CLIENT

    if not settings.INGESTION_DISTRIBUTED_LIMIT_ENABLED:
        return None

    if _DISTRIBUTED_LIMIT_REDIS_CLIENT is not None:
        return _DISTRIBUTED_LIMIT_REDIS_CLIENT

    redis_url = settings.INGESTION_DISTRIBUTED_REDIS_URL or settings.CELERY_BROKER_URL
    if not redis_url.startswith(("redis://", "rediss://")):
        raise RetryableIngestionError(
            "INGESTION_DISTRIBUTED_LIMIT_ENABLED=true requires a redis URL for broker or INGESTION_DISTRIBUTED_REDIS_URL"
        )

    try:
        _DISTRIBUTED_LIMIT_REDIS_CLIENT = Redis.from_url(redis_url, decode_responses=True)
        return _DISTRIBUTED_LIMIT_REDIS_CLIENT
    except RedisError as exc:
        raise RetryableIngestionError(f"Unable to initialize distributed limiter Redis client: {exc}") from exc


def _acquire_distributed_slot() -> bool:
    client = _get_distributed_limit_redis_client()
    if client is None:
        return False

    key = settings.INGESTION_DISTRIBUTED_COUNTER_KEY
    limit = max(1, settings.INGESTION_DISTRIBUTED_MAX_CONCURRENCY)
    ttl_seconds = max(30, settings.INGESTION_DISTRIBUTED_SLOT_TTL_SECONDS)

    try:
        in_flight = int(client.incr(key))
        client.expire(key, ttl_seconds)

        if in_flight > limit:
            client.decr(key)
            raise RetryableIngestionError(
                f"distributed ingestion concurrency limit reached ({in_flight - 1}/{limit})"
            )
        return True
    except RedisError as exc:
        raise RetryableIngestionError(f"distributed limiter unavailable: {exc}") from exc


def _release_distributed_slot(acquired: bool) -> None:
    if not acquired:
        return

    client = _get_distributed_limit_redis_client()
    if client is None:
        return

    key = settings.INGESTION_DISTRIBUTED_COUNTER_KEY
    try:
        in_flight = int(client.decr(key))
        if in_flight <= 0:
            client.delete(key)
    except RedisError:
        # Best effort release; TTL handles stale counters on failures.
        pass


@contextmanager
def _distributed_ingestion_slot_guard() -> None:
    acquired = _acquire_distributed_slot()
    try:
        yield
    finally:
        _release_distributed_slot(acquired)


@contextmanager
def _ingestion_capacity_guard() -> None:
    with _distributed_ingestion_slot_guard():
        with _ingestion_slot_guard():
            yield


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


def _is_retryable_http_error(exc: Exception) -> bool:
    if not isinstance(exc, requests.RequestException):
        return False

    if isinstance(exc, requests.HTTPError):
        status_code = exc.response.status_code if exc.response is not None else None
        if status_code is None:
            return True
        if status_code in {408, 409, 425, 429}:
            return True
        return status_code >= 500

    return True


def _is_non_retryable_error(exc: Exception) -> bool:
    text = str(exc).lower()
    markers = (
        "openai_api_key is not configured",
        "missing required cloudflare r2 env var",
        "unsupported file url scheme",
        "uploaded file is empty",
        "cannot resolve object key",
        "not a local file url",
        "file not found:",
        "invalid upload token",
    )
    return any(marker in text for marker in markers)


def _is_retryable_error(exc: Exception) -> bool:
    if isinstance(exc, RetryableIngestionError):
        return True
    if isinstance(exc, OperationalError):
        return _is_transient_db_error(exc)
    if _is_retryable_http_error(exc):
        return True

    text = str(exc).lower()
    retryable_markers = (
        "rate limit",
        "too many requests",
        "temporarily unavailable",
        "service unavailable",
        "gateway timeout",
        "bad gateway",
        "timeout",
        "timed out",
        "connection reset",
        "connection aborted",
        "connection closed",
        "try again",
    )
    return any(marker in text for marker in retryable_markers)


def _retry_delay_seconds(retry_count: int) -> int:
    base = max(1, settings.INGESTION_RETRY_BASE_SECONDS)
    max_delay = max(base, settings.INGESTION_RETRY_MAX_SECONDS)
    exponential_delay = min(base * (2 ** retry_count), max_delay)
    jitter = random.uniform(0, min(base, 5))
    return int(exponential_delay + jitter)


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

        with _ingestion_capacity_guard():
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
    except Exception as exc:
        db.rollback()

        error_text = str(exc)
        if _is_non_retryable_error(exc):
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
        max_retries = int(getattr(self, "max_retries", 3))
        if _is_retryable_error(exc) and retry_count < max_retries:
            _update_document_status(
                document_id=document_id,
                status="processing",
                error_message=f"Retrying ({retry_count + 1}): {exc}",
            )

            countdown = _retry_delay_seconds(retry_count)
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


@celery_app.task(
    name="app.tasks.ingestion_tasks.sync_document_role_payload",
    bind=True,
    max_retries=3,
    default_retry_delay=15,
)
def sync_document_role_payload(self, document_id: str):
    db = SessionLocal()
    try:
        document = db.query(Document).filter(Document.id == document_id).first()
        if not document:
            return {"status": "not_found", "document_id": document_id}

        role_allowed = [
            permission.role.name
            for permission in document.permissions
            if permission.role and permission.role.name
        ]
        if not role_allowed:
            role_allowed = ["general"]

        qdrant_service = QdrantService(settings.QDRANT_HOST, settings.QDRANT_COLLECTION)
        qdrant_service.update_document_role_allowed(
            document_id=str(document.id),
            role_allowed=sorted(set(role_allowed)),
            timeout_seconds=5,
        )

        return {
            "status": "synced",
            "document_id": document_id,
            "role_allowed": role_allowed,
        }
    except Exception as exc:
        retry_count = int(getattr(self.request, "retries", 0))
        max_retries = int(getattr(self, "max_retries", 3))

        if _is_non_retryable_error(exc):
            return {
                "status": "failed",
                "document_id": document_id,
                "error": str(exc),
            }

        if _is_retryable_error(exc) and retry_count < max_retries:
            raise self.retry(exc=exc, countdown=_retry_delay_seconds(retry_count))

        return {
            "status": "failed",
            "document_id": document_id,
            "error": str(exc),
        }
    finally:
        db.close()