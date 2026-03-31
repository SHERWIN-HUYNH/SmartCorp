from types import SimpleNamespace
from typing import List

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

    def ingest_pdf(self, file_path: str, document_id: str, role_allowed: List[str]):
        elements = self.chunking_service.partition_document(file_path)

        chunks = self.chunking_service.create_chunks_by_title(elements)
        processed_chunks = self.chunking_service.summarise_chunks(chunks)
        all_chunks = self.chunking_service.split_chunks(processed_chunks)

        texts = [chunk.get('text', '') for chunk in all_chunks]

        try:
            dense_embeddings = self.embedding.embed_dense(texts)
            sparse_embeddings = self.embedding.embed_sparse(texts)
        except Exception as e:
            if self.verbose:
                print(f"Embedding pipeline failed: {e}")
            return

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

            point = self.qdrant.chunk_to_point(
                chunk,
                document_id,
                dense_embeddings[i],
                sparse_indices,
                sparse_values,
                role_allowed,
            )

            points.append(point)

        try:
            self.qdrant.upsert_points(points)
            if self.verbose:
                print(f"Inserted {len(points)} points")
        except Exception as e:
            if self.verbose:
                print(f"Qdrant insert failed: {e}")
