from types import SimpleNamespace
from typing import List, Optional
from openai import OpenAI
from fastembed import SparseTextEmbedding


class EmbeddingService:
    def __init__(self, client: OpenAI, _sparse_model: Optional[SparseTextEmbedding]):
        self.client = client
        self.sparse_model = _sparse_model
        

    def embed_dense(self, texts: List[str], batch_size=50):
        all_embeddings = []

        try:
            for i in range(0, len(texts), batch_size):
                batch = texts[i:i+batch_size]

                response = self.client.embeddings.create(
                    model="text-embedding-3-small",
                    input=batch,
                )

                all_embeddings.extend([e.embedding for e in response.data])

            return all_embeddings

        except Exception as e:
            print(f"Embedding failed: {e}")

            return [None] * len(texts)


    def embed_sparse(self, texts: List[str]):
        if self.sparse_model is None:
            return [SimpleNamespace(indices=[], values=[]) for _ in texts]

        return list(self.sparse_model.embed(texts))