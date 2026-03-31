from typing import List, Optional
from datetime import datetime, timezone

from app.services.chunking_service import ChunkingService
from app.services.embedding_service import EmbeddingService
from app.services.qdrant_service import QdrantService
from app.services.cloudflare_service import CloudflareR2Service

class IngestionService:
    def __init__(
        self,
        chunking_service: ChunkingService,
        embedding_service: EmbeddingService,
        qdrant_service: QdrantService,
        cloudflare_service: CloudflareR2Service,
        verbose: bool = True,
    ):
        self.chunking_service = chunking_service
        self.embedding = embedding_service
        self.qdrant = qdrant_service
        self.cloudflare = cloudflare_service
        self.verbose = verbose

    def ingest_pdf(
        self,
        file_path: str,
        document_id: str,
        role_allowed: List[str],
        is_active: bool = True,
        effective_date: Optional[datetime] = None,
    ):
        effective_date = effective_date or datetime.now(timezone.utc)
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
            sparse = sparse_embeddings[i]
            
            # Upload media to Cloudflare R2 and store URLs
            chunk_type = chunk.get("type", "text")
            if chunk_type == "table" and chunk.get("raw_table"):
                try:
                    table_html = chunk.get("raw_table")[0]
                    table_url = self.cloudflare.upload_html_table(table_html)
                    chunk["table_url"] = table_url
                except Exception as e:
                    if self.verbose:
                        print(f"Failed to upload table: {e}")
            
            if chunk_type == "image" and chunk.get("image_b64"):
                try:
                    image_b64 = chunk.get("image_b64")[0]
                    image_url = self.cloudflare.upload_image_from_base64(image_b64)
                    chunk["image_url"] = image_url
                except Exception as e:
                    if self.verbose:
                        print(f"Failed to upload image: {e}")

            point = self.qdrant.chunk_to_point(
                chunk,
                document_id,
                dense_embeddings[i],
                sparse.indices.tolist(),
                sparse.values.tolist(),
                role_allowed,
                is_active=is_active,
                effective_date=effective_date,
            )

            points.append(point)

        try:
            self.qdrant.upsert_points(points)
            if self.verbose:
                print(f"Inserted {len(points)} points")
        except Exception as e:
            if self.verbose:
                print(f"Qdrant insert failed: {e}")
