from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from sqlalchemy.orm import Session

from app.core.chatbot_contract import ChatbotContractService, RetrievalContract
from app.core.qdrant_filters import build_allowed_document_filter, build_role_filter, merge_filters
from app.core.version_resolution import VersionResolver, VersionResolutionResult
from app.model.user import User
from app.services.embedding_service import EmbeddingService
from app.services.qdrant_service import QdrantService


@dataclass(slots=True)
class RetrievalResult:
    query: str
    contract: RetrievalContract
    qdrant_filter: dict[str, Any]
    role_filter: dict[str, Any]
    raw_results: dict[str, Any]
    documents: list[dict[str, Any]]
    resolved_documents: list[dict[str, Any]]
    version_resolution: VersionResolutionResult
    selected_version_cluster: dict[str, Any]
    selected_chunks: list[dict[str, Any]]
    clean_context: str
    resolution_reason: str


class RetrievalService:
    """
    Step 3 + 3.5: Retrieval contract execution.

    Responsibilities:
    - Resolve RBAC/effective-date contract from Postgres.
    - Build Qdrant filters.
    - Run hybrid search.
    - Normalize and version-resolve the results into a chatbot-friendly shape.
    """

    def __init__(
        self,
        db: Session,
        qdrant_service: QdrantService,
        embedding_service: EmbeddingService,
    ):
        self.db = db
        self.qdrant = qdrant_service
        self.embedding = embedding_service

    def build_contract(self, user: User) -> RetrievalContract:
        return ChatbotContractService.resolve_retrieval_contract(self.db, user)

    def search(self, *, user: User, query: str, top_k: int = 5) -> RetrievalResult:
        contract = self.build_contract(user)
        allowed_filter = build_allowed_document_filter(list(contract.allowed_document_ids), now_iso=contract.now_utc.isoformat())
        role_filter = build_role_filter([contract.role_name] if contract.role_name else None)
        qdrant_filter = merge_filters(allowed_filter, role_filter)

        if not contract.allowed_document_ids:
            empty_resolution = VersionResolutionResult(
                selected_version_key="",
                selected_documents=[],
                resolution_reason="no_authorized_documents",
                selected_clusters=[],
                clean_context="",
                cluster_summaries=[],
            )
            return RetrievalResult(
                query=query,
                contract=contract,
                qdrant_filter=qdrant_filter,
                role_filter=role_filter,
                raw_results={},
                documents=[],
                resolved_documents=[],
                version_resolution=empty_resolution,
                selected_version_cluster={},
                selected_chunks=[],
                clean_context="",
                resolution_reason=empty_resolution.resolution_reason,
            )

        dense_vector = self.embedding.embed_dense([query])[0]
        sparse_vector = self.embedding.embed_sparse([query])[0]

        raw_results = self.qdrant.hybrid_search(
            dense_vector=dense_vector,
            sparse_indices=getattr(sparse_vector, "indices", []) or [],
            sparse_values=getattr(sparse_vector, "values", []) or [],
            limit=top_k,
            role_allowed=[contract.role_name] if contract.role_name else None,
        )

        points = raw_results.get("result", {}).get("points", []) if isinstance(raw_results, dict) else []
        normalized_docs: list[dict[str, Any]] = []
        for point in points:
            payload = point.get("payload", {}) if isinstance(point, dict) else {}
            normalized_docs.append(
                {
                    "document_id": str(payload.get("document_id", "")),
                    "chunk_id": str(point.get("id", "")),
                    "content": payload.get("content", ""),
                    "page": int(payload.get("page", 0) or 0),
                    "score": float(point.get("score", 0.0) or 0.0),
                    "parent_id": payload.get("parent_id", ""),
                    "order": int(payload.get("order", 0) or 0),
                    "effective_date": payload.get("effective_date"),
                    "is_active": bool(payload.get("is_active", True)),
                    "role_allowed": payload.get("role_allowed", []),
                }
            )

        unique_docs = VersionResolver.deduplicate_documents(normalized_docs)
        valid_docs = [doc for doc in unique_docs if VersionResolver.is_temporally_valid(doc, contract.now_utc)]
        version_resolution = VersionResolver.resolve_latest_documents(valid_docs)

        selected_cluster = version_resolution.selected_clusters[0] if version_resolution.selected_clusters else {}
        return RetrievalResult(
            query=query,
            contract=contract,
            qdrant_filter=qdrant_filter,
            role_filter=role_filter,
            raw_results=raw_results,
            documents=normalized_docs,
            resolved_documents=version_resolution.selected_documents,
            version_resolution=version_resolution,
            selected_version_cluster=selected_cluster,
            selected_chunks=version_resolution.selected_documents,
            clean_context=version_resolution.clean_context,
            resolution_reason=version_resolution.resolution_reason,
        )
