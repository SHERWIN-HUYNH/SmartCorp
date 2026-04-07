# SmartCope Simple Schema + Processing Flow (No Version History)

## 1) Mục tiêu thiết kế
- Không dùng process_code, department, doc_key do user nhập.
- Không quản lý lịch sử version đầy đủ.
- Upload chỉ cần: role_allowed, effective_date, thông tin file.
- Quản lý duplicate bằng file_hash.
- Qdrant chỉ phục vụ retrieval theo chunk.

## 2) Database Schema (PostgreSQL)

### 2.1 roles
```sql
CREATE TABLE roles (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name        TEXT NOT NULL UNIQUE,
    description TEXT,
    created_at  TIMESTAMPTZ DEFAULT NOW()
);
```

### 2.2 users
```sql
CREATE TABLE users (
    id             UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    role_id        UUID NOT NULL REFERENCES roles(id),
    email          TEXT NOT NULL UNIQUE,
    last_login_at  TIMESTAMPTZ DEFAULT NULL,
    status         TEXT NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'suspended')),
    password_hash  TEXT NOT NULL,
    created_at     TIMESTAMPTZ DEFAULT NOW()
);
```

### 2.3 documents
Lưu metadata file + trạng thái xử lý. Mỗi document chỉ đại diện cho bản hiện hành.

```sql
CREATE TABLE documents (
    id                 UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id            UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,

    filename           TEXT NOT NULL,
    file_url           TEXT NOT NULL,
    file_size_bytes    BIGINT,
    mime_type          TEXT,
    file_hash          TEXT NOT NULL,

    effective_date     TIMESTAMPTZ,

    status             TEXT NOT NULL DEFAULT 'pending'
                       CHECK (status IN ('pending', 'processing', 'ready', 'failed', 'deleted')),
    error_message      TEXT,

    deleted_at         TIMESTAMPTZ DEFAULT NULL,
    created_at         TIMESTAMPTZ DEFAULT NOW(),
    updated_at         TIMESTAMPTZ DEFAULT NOW(),

    -- Chặn user upload cùng một file giống hệt nhiều lần
    UNIQUE (user_id, file_hash)
);

CREATE INDEX idx_documents_user_status ON documents(user_id, status);
CREATE INDEX idx_documents_effective_date ON documents(effective_date);
```

Ghi chú:
- Đã bỏ document_group_id và version.
- Update tài liệu sẽ là thay thế nội dung cho cùng document_id (không tạo version mới).

### 2.4 document_permissions
```sql
CREATE TABLE document_permissions (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    role_id     UUID NOT NULL REFERENCES roles(id) ON DELETE CASCADE,
    document_id UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    granted_at  TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE (role_id, document_id)
);
```

### 2.5 chat_sessions
```sql
CREATE TABLE chat_sessions (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id     UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title       TEXT,
    created_at  TIMESTAMPTZ DEFAULT NOW(),
    updated_at  TIMESTAMPTZ DEFAULT NOW()
);
```

### 2.6 messages
```sql
CREATE TABLE messages (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id  UUID NOT NULL REFERENCES chat_sessions(id) ON DELETE CASCADE,
    idx         INTEGER NOT NULL,
    role        TEXT NOT NULL CHECK (role IN ('user', 'assistant')),
    content     TEXT NOT NULL,
    created_at  TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE (session_id, idx)
);
```

### 2.7 citations
```sql
CREATE TABLE citations (
    id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id    UUID NOT NULL REFERENCES chat_sessions(id) ON DELETE CASCADE,
    message_idx   INTEGER NOT NULL,
    citation_no   INTEGER NOT NULL,

    document_id   UUID REFERENCES documents(id) ON DELETE SET NULL,
    page_number   INTEGER,
    chunk_text    TEXT NOT NULL,

    created_at    TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE (session_id, message_idx, citation_no)
);
```

## 3) Qdrant Point Schema (payload)

```json
{
  "document_id": "uuid-from-documents.id",
  "is_active": true,
  "effective_date": "2026-03-31T00:00:00Z",

  "role_allowed": ["admin", "manager"],

  "content": "chunk text",
  "type": "text|table|image",
  "page": 3,
  "parent_id": "section-1",
  "order": 12,
  "table_url": "https://...",
  "image_url": "https://..."
}
```

Payload index nên tạo:
- role_allowed (keyword)
- document_id (keyword)
- is_active (bool)
- effective_date (datetime)

## 4) Luồng xử lý theo giai đoạn

## 4.1 Upload - file mới hoàn toàn
Input:
- user_id
- role_allowed[]
- effective_date
- file (filename, mime_type, size)

Bước xử lý:
1. Tính file_hash.
2. Check duplicate theo (user_id, file_hash).
3. Nếu chưa trùng: tạo row mới trong documents với status=processing.
4. Ghi quyền vào document_permissions theo role_allowed.
5. Chunk + embedding + upsert vào Qdrant với payload:
   - document_id = documents.id
   - is_active=true
   - effective_date, role_allowed
6. Thành công: documents.status = ready.
7. Lỗi: documents.status = failed, error_message = ...

Bảng/giá trị dùng:
- documents: insert status=processing/ready/failed
- document_permissions: insert (role_id, document_id)
- qdrant payload: document_id, is_active=true, role_allowed, effective_date

## 4.2 Upload - file trùng (duplicate)
Điều kiện:
- Trùng theo (user_id, file_hash).

Hai cách xử lý:
- Cách A (khuyến nghị): trả no-op, không ingest lại.
- Cách B: cho phép replace nội dung cũ (cùng document_id).

Bảng/giá trị dùng:
- documents: query file_hash + user_id + deleted_at IS NULL
- Nếu no-op: không ghi Qdrant

## 4.3 Update (replace tài liệu hiện hành)
Input:
- document_id
- file mới + role_allowed + effective_date

Bước xử lý:
1. Tìm document theo document_id.
2. Cập nhật metadata file trong documents (filename, file_url, file_hash, size, mime, effective_date, status=processing).
3. Qdrant:
   - Deactivate hoặc delete chunk cũ theo document_id.
   - Upsert chunk mới với cùng document_id, is_active=true.
4. Cập nhật lại document_permissions nếu role thay đổi.
5. Thành công: status=ready.

Bảng/giá trị dùng:
- documents: update metadata + status
- document_permissions: cập nhật quyền
- qdrant payload: old chunk is_active=false (hoặc delete), new chunk is_active=true

## 4.4 Delete (soft delete)
Input:
- document_id

Bước xử lý:
1. documents: set deleted_at=NOW(), status='deleted'.
2. document_permissions: có thể giữ lại (soft delete) hoặc xóa tùy policy.
3. Qdrant: set is_active=false cho toàn bộ chunk thuộc document_id (hoặc delete point).

Bảng/giá trị dùng:
- documents: deleted_at, status='deleted'
- qdrant payload: is_active=false

## 4.5 Retrieve (search/chat)
Input:
- query
- user role (ví dụ manager)
- thời điểm hiện tại now()

Filter Qdrant bắt buộc:
- role_allowed any [user_role]
- is_active = true
- effective_date is null OR effective_date <= now()

Kết quả:
- Lấy top-k chunk
- Trả citation gồm document_id, page, chunk_text
- Lưu citations theo session_id/message_idx

Bảng/giá trị dùng:
- qdrant payload: role_allowed, is_active, effective_date, content, page, document_id
- citations: insert session_id, message_idx, citation_no, document_id, page_number, chunk_text

## 5) Mapping nhanh giữa DB và Qdrant
- documents.id -> payload.document_id
- documents.effective_date -> payload.effective_date
- document_permissions (role) -> payload.role_allowed
- Trạng thái kích hoạt truy vấn -> payload.is_active

## 6) Quy tắc tối thiểu nên giữ để hệ thống ổn định
- Không bỏ is_active ở Qdrant nếu muốn tránh lẫn dữ liệu cũ khi replace tài liệu.
- role_allowed phải có cả ở DB (quản trị) và Qdrant (filter realtime).
- file_hash nên lưu ở documents để phát hiện duplicate sớm, tránh tốn embedding/upsert.
- Retrieval phải filter đồng thời role_allowed + is_active + effective_date.
