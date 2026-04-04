# 🏢 SmartCorp - Agentic RAG Internal Procedure System

![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688?logo=fastapi&logoColor=white)
![Next.js](https://img.shields.io/badge/Next.js-14-black?logo=next.js&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?logo=docker&logoColor=white)
![Qdrant](https://img.shields.io/badge/Qdrant-Vector_DB-FF5252)

## 📌 1. Giới thiệu Đồ án (Project Overview)
[cite_start]SmartCorp là một hệ thống hỏi đáp nội bộ tiên tiến ứng dụng kiến trúc **Agentic RAG** (Retrieval-Augmented Generation)[cite: 17]. Hệ thống được phát triển nhằm giải quyết bài toán tra cứu và tổng hợp các quy trình nghiệp vụ nội bộ phức tạp, thường bị phân mảnh trong nhiều định dạng tài liệu khác nhau. 

Thay vì chỉ tìm kiếm theo từ khóa thông thường, SmartCorp đóng vai trò như một trợ lý AI thông minh:
* [cite_start]Tự động đọc hiểu, bóc tách dữ liệu từ các tệp PDF, Docx (bao gồm cả bảng biểu và biểu đồ phức tạp)[cite: 20].
* [cite_start]Kết hợp các mảnh thông tin rời rạc và suy luận thông qua mô hình tác tử đa bước (Multi-step LLM Agent)[cite: 22].
* [cite_start]Cung cấp cho nhân viên các hướng dẫn hành động (actionable steps) rõ ràng, giúp rút ngắn thời gian tra cứu và tối ưu hóa quy trình Onboarding[cite: 22].

---

## 🛠️ 2. Công nghệ sử dụng (Tech Stack)
[cite_start]Dự án được xây dựng dựa trên các công nghệ và framework hiện đại[cite: 19]:

* **AI & Machine Learning:**
  * [cite_start]**Framework:** LangGraph (cho Agentic Workflow)[cite: 19], LangChain.
  * [cite_start]**Xử lý tài liệu (Parsing):** LlamaParse, Unstructured.io, Tesseract OCR[cite: 20].
  * [cite_start]**Tìm kiếm (Search):** Hybrid Search (Semantic Vector Search + BM25) [cite: 21][cite_start], BGE-Reranker[cite: 21], FastEmbed.
* **Backend:** Python, FastAPI.
* [cite_start]**Frontend:** Next.js[cite: 19], React, TailwindCSS.
* [cite_start]**Database:** Qdrant (Vector Database)[cite: 19], PostgreSQL, Neo4j (Graph Database).
* **DevOps & Môi trường:** Docker, Docker Compose, Linux.

---

## ✨ 3. Chức năng chính & Giao diện (Core Features & Screenshots)
<img width="1897" height="911" alt="image" src="https://github.com/user-attachments/assets/acd4d8e3-d8f7-46c5-a467-eddca4062897" />

### 3.1. Truy vấn Quy trình Tích hợp (Hybrid Search Q&A)
Hệ thống cho phép người dùng đặt câu hỏi bằng ngôn ngữ tự nhiên. [cite_start]Nhờ kiến trúc Hybrid Search kết hợp BGE-Reranker, hệ thống truy xuất chính xác các mã quy trình đặc thù (như QT-01) mà không bị lỗi ảo giác (hallucination)[cite: 21].

![Uploading image.png…]()

> ![Truy vấn Quy trình](docs/images/feature_hybrid_search.png)
> *Giao diện Chatbot hiển thị câu trả lời trích xuất kèm theo trích dẫn nguồn tài liệu (Citations).*

### 3.2. Trợ lý Tổng hợp Đa bước (Agentic Synthesis)
[cite_start]Khi người dùng yêu cầu một quy trình tổng hợp, Agent (dựa trên LangGraph) sẽ tự động lên kế hoạch (planning), gọi các công cụ (tools) truy xuất nhiều lần để thu thập đủ dữ liệu, và tổng hợp thành các bước thực thi (step-by-step instructions)[cite: 22].

> **[Thêm ảnh tại đây]**
> ![Agentic Workflow](docs/images/feature_agentic_workflow.png)
> *Giao diện hiển thị quá trình Agent đang "suy nghĩ" (reasoning steps) và đưa ra bản hướng dẫn cuối cùng.*

### 3.3. Xử lý & Phân tích Tài liệu Đa định dạng (Document Parsing Pipeline)
Người dùng (Admin) tải lên các tài liệu nội bộ (PDF, Docx, Markdown). [cite_start]Pipeline sẽ tự động kích hoạt LlamaParse và Tesseract OCR để bóc tách text chất lượng cao, bảo toàn cấu trúc bảng biểu phức tạp[cite: 20].

> **[Thêm ảnh tại đây]**
> ![Document Upload](docs/images/feature_document_parsing.png)
> *Giao diện quản lý tài liệu, hiển thị trạng thái Chunking và Vector hóa vào Qdrant.*

---

## 🚀 4. Hướng dẫn Cài đặt (Getting Started)

Dự án được container hóa hoàn toàn để đảm bảo tính đồng nhất (Dev/Prod Parity).

### Yêu cầu hệ thống (Prerequisites)
* Docker và Docker Compose.
* Môi trường: Windows WSL2, Linux, hoặc macOS.

### Cấu hình & Khởi chạy
**1. Khởi tạo file cấu hình biến môi trường:**
```bash
cp .env.docker.example .env.docker
