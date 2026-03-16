# Khởi động server 
source ./smartcope/Scripts/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Khởi động client 
pnpm run dev