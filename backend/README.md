# Backend — AI Investment Assistant API

Deploy lên **Render** (free tier). Xem hướng dẫn chi tiết ở README gốc (`../README.md`).

## Chạy local
```bash
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # điền key thật
python collect_daily.py          # thu thập dữ liệu 1 lần
uvicorn api.main:app --reload --port 8000
```

## Cấu hình Render
- Root Directory: `backend`
- Build Command: `pip install -r requirements.txt`
- Start Command: `uvicorn api.main:app --host 0.0.0.0 --port $PORT`
- Environment Variables: xem `.env.example`
