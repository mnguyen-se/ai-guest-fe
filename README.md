# 🧭 Đài Quan Sát Đầu Tư — AI Investment Assistant

Hệ thống cá nhân: thu thập → lưu trữ → phân tích → tổng hợp dữ liệu tài chính/vĩ mô,
dùng AI (Gemini) để **giải thích có bằng chứng**, không dự đoán mù quáng, không tự
quyết định thay bạn.

## Kiến trúc tổng thể

```
┌─────────────────────┐      ┌──────────────────┐      ┌───────────────────┐
│  GitHub Actions      │      │  Supabase         │      │  Backend API       │
│  (thu thập dữ liệu   │ ───► │  (Postgres free)  │ ◄─── │  FastAPI (Render)  │
│  1-2 lần/ngày, free) │      │  lưu toàn bộ data  │      │  gọi Gemini API    │
└─────────────────────┘      └──────────────────┘      └─────────┬─────────┘
                                                                    │ REST
                                                          ┌─────────▼─────────┐
                                                          │  Frontend          │
                                                          │  Next.js (Vercel)  │
                                                          │  Dashboard + Ask AI│
                                                          └────────────────────┘
```

| Phần | Công nghệ | Deploy ở đâu | Vai trò |
|---|---|---|---|
| **Data Collector** | Python, chạy theo lịch | GitHub Actions (miễn phí) | Thu thập macro/market/news/social, ghi vào Supabase |
| **BACKEND** | FastAPI (Python) | Render (free tier) | API phục vụ frontend + gọi Gemini để phân tích |
| **Database** | Postgres | Supabase (free tier, 500MB) | Lưu trữ toàn bộ dữ liệu lịch sử |
| **FRONTEND** | Next.js + Tailwind | Vercel (free tier) | Dashboard hiển thị + giao diện hỏi-đáp AI |
| **AI Analysis** | Gemini API (free tier) | — (gọi từ Backend) | Suy luận có cấu trúc: confidence, risk, evidence... |

Đây đều là các gói **miễn phí** như bạn yêu cầu. Không dùng Bloomberg/Reuters trả phí —
thay vào đó dùng FRED (macro), Yahoo Finance qua yfinance (giá + cơ bản DN), RSS công khai
(tin tức), Google Trends + Reddit free API (mạng xã hội).

## Cấu trúc thư mục

```
investment-assistant/
├── backend/              👉 BE - deploy lên Render
│   ├── collectors/        (macro, markets, fundamentals, news, social, events)
│   ├── db/                 schema.sql + supabase_client.py
│   ├── analysis/           gemini_analyzer.py (lớp AI reasoning)
│   ├── api/                main.py (FastAPI, các endpoint /api/...)
│   ├── collect_daily.py    script điều phối, chạy bởi GitHub Actions
│   ├── requirements.txt
│   └── .env.example
├── frontend/              👉 FE - deploy lên Vercel
│   ├── app/                page.tsx (dashboard), layout.tsx
│   ├── components/         TickerTape, MacroPanel, MarketTable, NewsFeed, AskAI...
│   ├── lib/api.ts           gọi tới Backend API
│   └── .env.example
└── .github/workflows/
    └── collect-data.yml    GitHub Actions - chạy collector 2 lần/ngày
```

## 🚀 Hướng dẫn deploy từng bước

### Bước 1 — Supabase (Database, làm trước tiên)
1. Tạo tài khoản free tại https://supabase.com → New Project.
2. Vào **SQL Editor** → copy toàn bộ nội dung `backend/db/schema.sql` → Run.
3. Vào **Project Settings → API** → lấy `Project URL` và `service_role key`
   (KHÔNG dùng anon key cho backend, vì cần quyền ghi).

### Bước 2 — Lấy các API key miễn phí
| Nguồn | Link đăng ký | Dùng để |
|---|---|---|
| FRED | https://fred.stlouisfed.org/docs/api/api_key.html | Dữ liệu vĩ mô (CPI, GDP, lãi suất...) |
| Gemini | https://aistudio.google.com/apikey | Lớp AI phân tích |
| Reddit (tùy chọn) | https://www.reddit.com/prefs/apps → chọn "script" | Tâm lý mạng xã hội |

### Bước 3 — GitHub Actions (thu thập dữ liệu tự động)
1. Đẩy toàn bộ thư mục này lên 1 GitHub repo (public hoặc private đều được,
   private vẫn có free minutes cho tài khoản cá nhân).
2. Vào **Settings → Secrets and variables → Actions** của repo, thêm các secret:
   - `SUPABASE_URL`, `SUPABASE_SERVICE_KEY`
   - `FRED_API_KEY`
   - `REDDIT_CLIENT_ID`, `REDDIT_CLIENT_SECRET` (nếu dùng)
3. Workflow `.github/workflows/collect-data.yml` sẽ tự chạy 2 lần/ngày (6:30 & 13:30 UTC).
   Có thể vào tab **Actions** → chọn workflow → **Run workflow** để chạy thử ngay.

### Bước 4 — Backend API lên Render
1. Tạo tài khoản free tại https://render.com → **New Web Service** → kết nối GitHub repo.
2. Cấu hình:
   - **Root Directory**: `backend`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn api.main:app --host 0.0.0.0 --port $PORT`
3. Thêm Environment Variables giống file `backend/.env.example`
   (`SUPABASE_URL`, `SUPABASE_SERVICE_KEY`, `GEMINI_API_KEY`, `ALLOWED_ORIGINS`...).
4. Deploy xong sẽ có URL dạng `https://xxx.onrender.com` — lưu lại để dùng ở Bước 5.

> ⚠️ Lưu ý: Render free tier sẽ "ngủ" sau ~15 phút không có traffic, lần gọi đầu
> sau khi ngủ sẽ chậm (~30-50s cold start). Phù hợp với việc dùng cá nhân, không
> phù hợp nếu cần phản hồi tức thời liên tục.

### Bước 5 — Frontend lên Vercel
1. Tạo tài khoản free tại https://vercel.com → **New Project** → chọn repo này.
2. **Root Directory**: `frontend`
3. Thêm Environment Variable: `NEXT_PUBLIC_API_URL` = URL backend ở Bước 4.
4. Deploy. Xong! Vào URL Vercel để xem dashboard.
5. Quay lại Render, cập nhật `ALLOWED_ORIGINS` bằng đúng domain Vercel để CORS hoạt động.

## Chạy thử ở local trước khi deploy

```bash
# Backend
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # rồi điền key thật vào
python collect_daily.py            # chạy thử thu thập 1 lần
uvicorn api.main:app --reload --port 8000

# Frontend (terminal khác)
cd frontend
cp .env.example .env.local   # NEXT_PUBLIC_API_URL=http://localhost:8000
npm install
npm run dev
```

Mở http://localhost:3000 để xem dashboard.

## Nguyên tắc AI Analysis (đã cấu hình sẵn trong `gemini_analyzer.py`)

- Không dự đoán giá chắc chắn — chỉ ước lượng xác suất, nêu bằng chứng.
- Luôn so sánh nhiều nguồn độc lập; nêu rõ nếu các nguồn mâu thuẫn nhau.
- Phân biệt rõ: **Fact** (số liệu xác thực) / **Expert opinion** (ý kiến chuyên gia
  trích dẫn từ tin tức) / **AI inference** (suy luận riêng của AI).
- Mỗi phân tích trả về: `confidence_score`, `risk_score`, `bullish_factors`,
  `bearish_factors`, `related_news`, `historical_similar_cases`, `outlook` (3/6/12 tháng),
  và `data_limitations` (điều dữ liệu hiện có KHÔNG đủ để kết luận).
- Không đưa ra khuyến nghị "nên mua/nên bán" — chỉ cung cấp phân tích để bạn tự quyết.

## Mở rộng thêm

- Thêm mã cổ phiếu theo dõi: sửa `backend/collectors/config.py`.
- Thêm nguồn tin tức RSS mới: thêm vào `RSS_FEEDS` trong cùng file.
- Muốn phân tích sâu hơn/nhanh hơn: đổi `GEMINI_MODEL` trong `gemini_analyzer.py`
  sang `gemini-2.5-pro` (chậm hơn, chất lượng suy luận cao hơn).
- Muốn thêm nguồn trả phí (Bloomberg, Twitter API Pro...) sau này: chỉ cần thêm
  1 file collector mới trong `backend/collectors/`, theo đúng pattern của các file hiện có.
