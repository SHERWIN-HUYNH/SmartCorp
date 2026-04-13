# 🏢 SmartCorp Oracle - Agentic RAG Internal Procedure System

![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688?logo=fastapi&logoColor=white)
![Next.js](https://img.shields.io/badge/Next.js-14-black?logo=next.js&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?logo=docker&logoColor=white)
![Qdrant](https://img.shields.io/badge/Qdrant-Vector_DB-FF5252)

## 📌 1. Giới thiệu Đồ án (Overview)
SmartCorp Oracle là hệ thống hỏi đáp nội bộ ứng dụng kiến trúc lai giữa Agentic RAG, giao diện Next.js và cơ chế phân quyền bảo mật. Hệ thống tự động bóc tách dữ liệu đa định dạng, suy luận qua LLM và cung cấp hướng dẫn nghiệp vụ từng bước một cách minh bạch và chính xác.

---

## 🛠️ 2. Công nghệ sử dụng (Tech Stack)
* **Frontend:** Next.js, Vercel AI SDK (Streaming UI).
* **Backend & Agent:** FastAPI (Python), LangGraph.
* **Database:** Qdrant (Vector DB), PostgreSQL (Relational DB).
* **AI & Search:** Hybrid Search (BM25 + Semantic 1356d), Cohere/BGE-Reranker, LlamaParse/Unstructured.io.

---

## ✨ 3. Chức năng chính & Giao diện (Core Features)
<img width="1897" height="911" alt="Screenshot 2026-04-04 201901" src="https://github.com/user-attachments/assets/9fb9953c-a7e0-4a26-a416-aa5aa8c5198d" />
<img width="1906" height="903" alt="image" src="https://github.com/user-attachments/assets/72847aa9-60d0-4c5e-a6f1-799fa4aa4847" />

### 3.1. Tìm kiếm Lai Tích hợp Phân quyền (Role-based Hybrid Search)
* Kết hợp sức mạnh tìm kiếm Vector và BM25.
* Lọc kết quả ngay từ tầng Database thông qua trường `role_allowed` trong cấu trúc Payload.
* Tích hợp Reranker để đẩy các kết quả chính xác nhất lên đầu.

<img width="2048" height="1747" alt="image" src="https://github.com/user-attachments/assets/39b179cb-4605-47bc-8576-14f9b49763eb" />

### 3.2. Tác tử Điều phối & Tự sửa lỗi (Router & Self-Correction Agent)
* Router Agent tự động phân loại ý định người dùng.
* Vòng lặp Self-Correction tự động đánh giá và biến đổi câu truy vấn nếu tìm kiếm ban đầu thất bại.
* Lịch sử ngữ cảnh được duy trì liên tục qua cơ chế `thread_id` của LangGraph.


### 3.3. Minh bạch Trích dẫn (Citation UX) & Quản lý Phiên bản (Versioning)
* **Citation UX:** Hiển thị trực tiếp nội dung gốc tại Panel bên phải khi click vào nguồn trích dẫn. Dữ liệu trích dẫn (`chunk_text`) được lưu độc lập để bảo toàn lịch sử hội thoại.
* **Collision & Versioning:** Phát hiện trùng lặp file qua thuật toán băm (file hash). Qdrant sử dụng `effective_date` (Unix timestamp) để phân loại và chỉ đưa ngữ cảnh mới nhất, sạch nhất vào LLM.
<img width="1919" height="911" alt="Screenshot 2026-04-04 202134" src="https://github.com/user-attachments/assets/3d431a8a-6aa5-4623-95e0-247071e1e99f" />

---

## 🚀 4. Hướng dẫn Cài đặt & Kiểm thử (Getting Started)

### 4.1. Yêu cầu môi trường (Prerequisites)
* Docker Desktop (khuyến nghị khi onboarding team).
* Node.js 20+ và `pnpm` (nếu chạy local frontend).
* Python 3.11+ (nếu chạy local backend).
* PostgreSQL URL hợp lệ (đang dùng Neon theo `.env.docker.example`).

---

### 4.2. Cách 1 - Chạy nhanh toàn bộ bằng Docker (Khuyến nghị)
Chạy từ thư mục gốc dự án `SmartCope`.

1. Tạo file môi trường Docker:
```bash
cp .env.docker.example .env.docker
```

2. Cập nhật các biến bắt buộc trong `.env.docker`:
* `DATABASE_URL`
* `JWT_ACCESS_SECRET`
* `JWT_REFRESH_SECRET`
* `OPENAI_API_KEY` (nếu dùng tính năng LLM)

3. Khởi động toàn bộ services:
```bash
docker compose --env-file .env.docker up --build
```

4. Truy cập các endpoint sau khi container healthy:
* Client: `http://localhost:3000`
* API: `http://localhost:8000`
* API Health: `http://localhost:8000/healthz`
* Qdrant: `http://localhost:6333`

5. Dừng hệ thống:
```bash
docker compose down
```

OCR profile (tuỳ chọn):
```bash
docker compose --env-file .env.docker --profile ocr run --rm tesseract --version
```

---

### 4.3. Cách 2 - Chạy local (Backend + Frontend riêng)

#### Bước A - Chạy hạ tầng phụ trợ (Redis + Qdrant)
Từ thư mục gốc `SmartCope`:
```bash
docker compose up -d redis qdrant
```

#### Bước B - Chạy Backend (FastAPI)
Từ thư mục `server`:
```bash
cd server
source smartcope/Scripts/activate
pip install -r requirements.txt
```

Tạo file `.env` trong `server` (có thể copy từ root `.env.docker.example` rồi chỉnh lại cho local). Tối thiểu cần:
```env
DATABASE_URL=postgresql://USER:PASSWORD@YOUR-NEON-HOST/DATABASE?sslmode=require
JWT_ACCESS_SECRET=change-me-access-secret
JWT_REFRESH_SECRET=change-me-refresh-secret
QDRANT_HOST=http://localhost:6333
CORS_ORIGINS=http://localhost:3000
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/1
ROLE_MANAGER_ALLOWLIST=admin,manager
OPENAI_API_KEY=your-openai-api-key
```

Lưu ý: `OPENAI_API_KEY` là bắt buộc nếu bạn muốn chạy luồng ingest tài liệu (chunking/embedding).

Chạy migration và start API:
```bash
alembic upgrade head
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Chạy worker (terminal khác, tuỳ chọn nhưng khuyến nghị khi ingest tài liệu):
```bash
cd server
source smartcope/Scripts/activate
celery -A app.core.celery_app.celery_app worker --loglevel=info -Q ingestion
```

Nếu chạy local trên Windows và gặp lỗi `PermissionError: [WinError 5] Access is denied` từ `billiard/pool`, chạy worker với pool `solo`:
```bash
cd server
source smartcope/Scripts/activate
celery -A app.core.celery_app.celery_app worker --loglevel=info -Q ingestion -P solo --concurrency=1
```

#### Bước C - Chạy Frontend (Next.js)
Từ thư mục `client`:
```bash
cd client
pnpm install
```

Tạo `.env.local` và cấu hình API base URL:
```env
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000/api
```

Start frontend:
```bash
pnpm dev
```

Mặc định frontend chạy tại `http://localhost:3000`.

---

### 4.4. Kiểm tra nhanh sau khi khởi động
```bash
curl http://localhost:8000/healthz
```

Kết quả kỳ vọng:
```json
{"status":"ok"}
```


