# Frontend — Đài Quan Sát Đầu Tư (Dashboard)

Next.js + Tailwind. Deploy lên **Vercel** (free tier).

## Chạy local
```bash
cp .env.example .env.local   # NEXT_PUBLIC_API_URL trỏ tới backend
npm install
npm run dev
```

## Cấu hình Vercel
- Root Directory: `frontend`
- Environment Variable: `NEXT_PUBLIC_API_URL` = URL backend (Render)
