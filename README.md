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

**1. Khởi tạo & Cấu hình:**
```bash
cp .env.docker.example .env.docker
```bash
**2. Triển khai hệ thống bằng Docker:**
```bash
docker compose --env-file .env.docker up -d
```bash
Client UI: http://localhost:3000
Backend API: http://localhost:8000/docs
Qdrant Vector DB: http://localhost:6333/dashboard

