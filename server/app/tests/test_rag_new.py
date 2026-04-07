import os
from app.core.config import get_settings
from app.services.qdrant_service import QdrantService
from app.services.chunking_service import ChunkingService
from app.services.embedding_service import EmbeddingService
from app.services.ingestion_service import IngestionService
from app.core.RAG import RAG
from openai import OpenAI
from fastembed import SparseTextEmbedding
from dotenv import load_dotenv

load_dotenv()

settings = get_settings()
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# Khởi tạo các service
q = QdrantService(settings.QDRANT_HOST, 'test-cloudflare')
try: 
    print(q.create_collection())
except Exception as e: 
    print(f"Collection info: {e}")

s = SparseTextEmbedding('Qdrant/bm25')
emb = EmbeddingService(client, s)
ch = ChunkingService(client, verbose=True)
ing = IngestionService(ch, emb, q)
rag = RAG(ing, s, emb, q, client)

# Chạy test
print("Bắt đầu Ingest PDF...")
chunks = rag.ingestion_pdf(
    file_path="C:/Users/USER/CODE/AI PROJECTS/SmartCope/server/app/doc/attention-is-all-you-need.pdf",
    document_id='doc-cloudflare-1',
    role_allowed=['admin', 'manager', 'IT']
)

print(f"Tổng số chunks: {len(chunks)}")
print(f"Số table URLs: {sum(1 for c in chunks if c.get('table_url'))}")
print(f"Số image URLs: {sum(1 for c in chunks if c.get('image_url'))}")