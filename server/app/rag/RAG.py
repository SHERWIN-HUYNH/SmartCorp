import uuid
from typing import List
from openai import OpenAI
from fastembed import SparseTextEmbedding
from unstructured.partition.pdf import partition_pdf
from unstructured.chunking.title import chunk_by_title


_sparse_model = SparseTextEmbedding("Qdrant/bm25")

class RAG:
    def __init__(self, qdrant_api, openai_api_key: str):
        self.qdrant = qdrant_api
        self.client = OpenAI(api_key=openai_api_key)

        # BM25 model
        self.sparse_model = _sparse_model

    
    def partition_document(self, file_path: str):
        """Extract elements from PDF using unstructured"""
        print(f"Partitioning document: {file_path}")
        
        elements = partition_pdf(
            filename=file_path,  # Path to your PDF file
            strategy="hi_res", # Use the most accurate (but slower) processing method of extraction
            infer_table_structure=True, # Keep tables as structured HTML, not jumbled text
            extract_image_block_types=["Image"], # Grab images found in the PDF
            extract_image_block_to_payload=True # Store images as base64 data you can actually use
        )
        
        print(f"Extracted {len(elements)} elements")
        return elements
    

    def create_chunks_by_title(self, elements):
        """Create intelligent chunks using title-based strategy"""
        print("Creating smart chunks...")
        
        chunks = chunk_by_title(
            elements, # The parsed PDF elements from previous step
            max_characters=3000, # Hard limit - never exceed 3000 characters per chunk
            new_after_n_chars=2400, # Try to start a new chunk after 2400 characters
            combine_text_under_n_chars=500 # Merge tiny chunks under 500 chars with neighbors
        )
        
        print(f"Created {len(chunks)} chunks")
        return chunks


    def embed_dense(self, texts: List[str], batch_size=50):
        all_embeddings = []

        try:
            for i in range(0, len(texts), batch_size):
                batch = texts[i:i+batch_size]

                response = self.client.embeddings.create(
                    model="text-embedding-3-small",
                    input=batch
                )

                all_embeddings.extend([e.embedding for e in response.data])

            return all_embeddings

        except Exception as e:
            print(f"Embedding failed: {e}")
            return [None] * len(texts)


    def embed_sparse(self, texts: List[str]):
        return list(self.sparse_model.embed(texts))


    def ingest(self, documents, document_id=None, department=None):
        print("Ingesting documents...")

        if department is None:
            department = ["general"]

        valid_docs = [doc for doc in documents if doc.get("text")]
        texts = [doc["text"] for doc in valid_docs]

        try:
            dense_embeddings = self.embed_dense(texts)
            sparse_embeddings = self.embed_sparse(texts)

        except Exception as e:
            print(f" Embedding pipeline failed: {e}")
            return

        points = []

        for i, doc in enumerate(valid_docs):
            metadata = doc.get("metadata", {})
            sparse = sparse_embeddings[i]

            if dense_embeddings[i] is None:
                continue  # skip failed embedding

            point = {
                "id": str(uuid.uuid4()),
                "vector": {
                    "dense": dense_embeddings[i],
                    "sparse": {
                        "indices": sparse.indices.tolist(),
                        "values": sparse.values.tolist()
                    }
                },
                "payload": {
                    "document_id": document_id,
                    "department": department,
                    "content": doc["text"],
                    "type": "mixed",
                    "group_id": document_id,
                    "order": i,
                    "raw_table": metadata.get("tables", []),
                    "image_B64": metadata.get("images", [])
                }
            }

            points.append(point)

        try:
            self.qdrant.upsert_points(points)
            print(f"✅ Inserted {len(points)} points")
        except Exception as e:
            print(f"❌ Qdrant insert failed: {e}")


    def search(self, query: str, top_k=5):
        try:
            dense = self.embed_dense([query])[0]

            if dense is None:
                print("❌ Dense embedding failed")
                return {}

            sparse = list(self.sparse_model.embed([query]))[0]

            return self.qdrant.hybrid_search(
                dense_vector=dense,
                sparse_indices=sparse.indices.tolist(),
                sparse_values=sparse.values.tolist(),
                limit=top_k
            )

        except Exception as e:
            print(f"❌ Search failed: {e}")
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
            print(f"❌ LLM failed: {e}")
            return "⚠️ Error generating answer. Please try again."


    def ask(self, query: str, top_k=5):
        results = self.search(query, top_k=top_k)
        answer = self.generate_answer(query, results)
        return answer, results