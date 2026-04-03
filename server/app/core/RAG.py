from typing import List, Optional
from openai import OpenAI
from fastembed import SparseTextEmbedding

from app.services.ingestion_service import IngestionService
from app.services.embedding_service import EmbeddingService


class RAG:
    def __init__(
        self,
        ingestion_service: IngestionService,
        _sparse_model: SparseTextEmbedding,
        embedding_service: EmbeddingService,
        qdrant_service,
        client: OpenAI,
        verbose=True,
    ):
        # BM25 model
        self.sparse_model = _sparse_model

        self.ingestion_service = ingestion_service
        self.embedding = embedding_service
        self.qdrant = qdrant_service
        self.client = client
        self.verbose = verbose

    def ingestion_pdf(self, file_path, document_id: str, role_allowed: List[str]):
        chunks = self.ingestion_service.ingest_pdf(file_path, document_id, role_allowed)

        return chunks


    def search(self, query: str, top_k=5, role_allowed: Optional[List[str]] = None):
        try:
            dense = self.embedding.embed_dense([query])[0]

            if dense is None:
                print("Dense embedding failed")
                return {}

            sparse = list(self.sparse_model.embed([query]))[0]

            return self.qdrant.hybrid_search(
                dense_vector=dense,
                sparse_indices=sparse.indices.tolist(),
                sparse_values=sparse.values.tolist(),
                limit=top_k,
                role_allowed=role_allowed,
            )

        except Exception as e:
            print(f"Search failed: {e}")
            return {}


    def generate_answer(self, query: str, search_results):
        try:
            points = search_results.get("result", {}).get("points", [])

            if not points:
                return "No relevant information found."

            # limit context
            context = ""
            for p in points:
                chunk = p["payload"]["content"]
                context += chunk + "\n\n"

            prompt = f"""
    You are a helpful assistant. Use the context below to answer the question.

    Context:
    {context}

    Question:
    {query}

    Answer:
    """

            response = self.client.chat.completions.create(
                model="gpt-4.1-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0
            )

            return response.choices[0].message.content

        except Exception as e:
            print(f"LLM failed: {e}")
            return "Error generating answer. Please try again."


    def ask(self, query: str, top_k=5, role_allowed: Optional[List[str]] = None):
        results = self.search(query, top_k=top_k, role_allowed=role_allowed)
        answer = self.generate_answer(query, results)
        return answer, results