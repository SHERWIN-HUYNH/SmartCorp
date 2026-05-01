from datetime import datetime
from time import perf_counter
from types import SimpleNamespace
from typing import List, Optional

from app.core.config import get_settings
from app.services.chunking_service import ChunkingService
from app.services.embedding_service import EmbeddingService
from app.services.qdrant_service import QdrantService

settings = get_settings()


class IngestionService:
    def __init__(
        self,
        chunking_service: ChunkingService,
        embedding_service: EmbeddingService,
        qdrant_service: QdrantService,
        verbose: bool = True,
    ):
        self.chunking_service = chunking_service
        self.embedding = embedding_service
        self.qdrant = qdrant_service
        self.verbose = verbose

    def ingest_pdf(
        self,
        file_path: str,
        document_id: str,
        role_allowed: List[str],
        effective_date: Optional[datetime] = None,
    ):
        started_at = perf_counter()

        partition_started = perf_counter()
        elements = self.chunking_service.partition_document(file_path)
        partition_seconds = perf_counter() - partition_started

        chunk_started = perf_counter()
        chunks = self.chunking_service.create_chunks_by_title(elements)
        processed_chunks = self.chunking_service.summarise_chunks(
            chunks,
            document_id=document_id,
        )
        all_chunks = self.chunking_service.split_chunks(processed_chunks)
        chunk_seconds = perf_counter() - chunk_started

        upload_date = int(datetime.utcnow().timestamp())
        effective_date_ts = (
            int(effective_date.timestamp()) if effective_date is not None else upload_date
        )

        embed_batch_size = max(1, settings.INGESTION_EMBED_BATCH_SIZE)
        upsert_batch_size = max(1, settings.INGESTION_UPSERT_BATCH_SIZE)
        total_points = 0

        embedding_seconds = 0.0
        upsert_seconds = 0.0

        for start in range(0, len(all_chunks), embed_batch_size):
            embed_batch = all_chunks[start : start + embed_batch_size]
            texts = [chunk.get("text", "") for chunk in embed_batch]

            embedding_started = perf_counter()
            dense_embeddings = self.embedding.embed_dense(texts)
            sparse_embeddings = self.embedding.embed_sparse(texts)
            embedding_seconds += perf_counter() - embedding_started

            points = []
            for i, chunk in enumerate(embed_batch):
                sparse = sparse_embeddings[i] or SimpleNamespace(indices=[], values=[])
                sparse_indices = (
                    sparse.indices.tolist()
                    if hasattr(sparse.indices, "tolist")
                    else list(sparse.indices)
                )
                sparse_values = (
                    sparse.values.tolist()
                    if hasattr(sparse.values, "tolist")
                    else list(sparse.values)
                )

                global_index = start + i
                point = self.qdrant.build_point_from_chunk(
                    chunk,
                    document_id,
                    dense_embeddings[i],
                    sparse_indices,
                    sparse_values,
                    role_allowed,
                    upload_date=upload_date,
                    effective_date=effective_date_ts,
                    point_id=f"{document_id}:{global_index}",
                )
                points.append(point)

            for upsert_start in range(0, len(points), upsert_batch_size):
                upsert_batch = points[upsert_start : upsert_start + upsert_batch_size]
                upsert_started = perf_counter()
                self.qdrant.upsert_points(upsert_batch)
                upsert_seconds += perf_counter() - upsert_started
                total_points += len(upsert_batch)

        total_seconds = perf_counter() - started_at

        if self.verbose:
            print(
                "Ingestion timing "
                f"document_id={document_id} "
                f"partition={partition_seconds:.2f}s "
                f"chunking+summary={chunk_seconds:.2f}s "
                f"embedding={embedding_seconds:.2f}s "
                f"upsert={upsert_seconds:.2f}s "
                f"total={total_seconds:.2f}s "
                f"chunks={len(all_chunks)} "
                f"points={total_points}"
            )

        return all_chunks
