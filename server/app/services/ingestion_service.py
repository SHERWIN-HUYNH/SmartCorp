from datetime import datetime
from types import SimpleNamespace
from typing import List, Optional

from app.services.chunking_service import ChunkingService
from app.services.embedding_service import EmbeddingService
from app.services.qdrant_service import QdrantService


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
        elements = self.chunking_service.partition_document(file_path)

        chunks = self.chunking_service.create_chunks_by_title(elements)
        processed_chunks = self.chunking_service.summarise_chunks(
            chunks,
            document_id=document_id,
        )
        all_chunks = self.chunking_service.split_chunks(processed_chunks)

        texts = [chunk.get('text', '') for chunk in all_chunks]
        upload_date = int(datetime.utcnow().timestamp())
        effective_date_ts = (
            int(effective_date.timestamp()) if effective_date is not None else upload_date
        )

        dense_embeddings = self.embedding.embed_dense(texts)
        sparse_embeddings = self.embedding.embed_sparse(texts)

        points = []
        for i, chunk in enumerate(all_chunks):
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

            point = self.qdrant.build_point_from_chunk(
                chunk,
                document_id,
                dense_embeddings[i],
                sparse_indices,
                sparse_values,
                role_allowed,
                upload_date=upload_date,
                effective_date=effective_date_ts,
            )

            points.append(point)

        self.qdrant.upsert_points(points)
        if self.verbose:
            print(f"Inserted {len(points)} points")

        return all_chunks
