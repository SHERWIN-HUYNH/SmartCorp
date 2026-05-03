Cách 1 — tăng concurrency trong 1 worker
Nếu bạn chỉ muốn test nhanh trên local:

Mở .env.docker
set:
INGESTION_MAX_LOCAL_CONCURRENCY=4
INGESTION_DISTRIBUTED_LIMIT_ENABLED=false
Restart stack:
docker compose --env-file .env.docker down
docker compose --env-file .env.docker up --build
Cách này cho phép cùng một worker process nhiều file hơn nếu Celery worker container đủ khả năng chạy song song.

Cách 2 — scale nhiều worker container để xử lý song song thật sự
Đây là cách mình khuyên dùng để test UX upload nhiều file.

Bước 1: bật distributed limit
Trong .env.docker:

INGESTION_MAX_LOCAL_CONCURRENCY=1
INGESTION_DISTRIBUTED_LIMIT_ENABLED=true
INGESTION_DISTRIBUTED_MAX_CONCURRENCY=4
INGESTION_DISTRIBUTED_REDIS_URL=redis://redis:6379/0
Ý nghĩa:

mỗi container worker chỉ xử lý 1 task tại một thời điểm
tổng toàn hệ thống được phép chạy tối đa 4 task ingest song song
Bước 2: scale worker
Chạy Docker Compose với nhiều worker:

docker compose --env-file .env.docker up --build --scale worker=4
Nếu bạn muốn tách riêng cho dễ quan sát:

docker compose --env-file .env.docker up -d redis qdrant server client
docker compose --env-file .env.docker up --build --scale worker=4 worker
Kết quả:

4 worker container cùng nhận task
4 file upload có thể ingest gần như đồng thời
không bị dồn hết vào một tiến trình
Cách test thực tế nhiều file
Cách nhanh nhất
Khởi động stack Docker như trên
Upload cùng lúc 3–10 file PDF
Quan sát logs:
docker compose logs -f worker
Bạn sẽ thấy nhiều document được xử lý xen kẽ hoặc song song thay vì chờ từng file xong mới tới file tiếp theo.

Nên chọn cấu hình nào?
Nếu bạn chỉ test trên máy cá nhân
INGESTION_MAX_LOCAL_CONCURRENCY=2 hoặc 4
INGESTION_DISTRIBUTED_LIMIT_ENABLED=false
Nếu bạn test đúng kiểu production-like
INGESTION_MAX_LOCAL_CONCURRENCY=1
INGESTION_DISTRIBUTED_LIMIT_ENABLED=true
docker compose --scale worker=N
Cách này phản ánh đúng mô hình:

mỗi worker xử lý 1 job
tổng job song song được điều phối bằng Redis
Lưu ý quan trọng
Nếu bạn scale nhiều worker nhưng không bật distributed limiter, mỗi container sẽ tự có semaphore riêng và tổng concurrency thực tế có thể vượt mức bạn muốn.

Vì vậy:

1 worker container → chỉ cần tăng INGESTION_MAX_LOCAL_CONCURRENCY
nhiều worker container → nên bật INGESTION_DISTRIBUTED_LIMIT_ENABLED=true
Gợi ý cấu hình test mình khuyên dùng
Để test UX upload nhiều file mà vẫn kiểm soát tốt:

INGESTION_MAX_LOCAL_CONCURRENCY=1
INGESTION_DISTRIBUTED_LIMIT_ENABLED=true
INGESTION_DISTRIBUTED_MAX_CONCURRENCY=3
INGESTION_DISTRIBUTED_REDIS_URL=redis://redis:6379/0
và chạy:

docker compose --env-file .env.docker up --build --scale worker=3
Nếu bạn muốn, mình có thể tiếp tục giúp bạn theo 1 trong 2 hướng sau:

soạn sẵn file .env.docker tối ưu cho test song song
chỉ cho bạn cách sửa docker-compose.yml để thêm worker replica / profile test dễ hơn