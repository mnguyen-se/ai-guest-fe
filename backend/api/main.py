"""
FastAPI backend - phục vụ frontend:
- Trả về dữ liệu mới nhất đã thu thập (macro, markets, news, social)
- Nhận câu hỏi từ người dùng, gọi Gemini để phân tích, trả về JSON có cấu trúc
- Lưu lại các báo cáo AI vào bảng ai_reports để tra cứu lịch sử

Deploy: Render / Railway free tier (xem README ở thư mục gốc)
Chạy local: uvicorn api.main:app --reload --port 8000
"""
from dotenv import load_dotenv
load_dotenv()
import os
from datetime import datetime, timezone
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from db.supabase_client import get_client, fetch_latest
from analysis.gemini_analyzer import ask_question, daily_summary, asset_outlook

app = FastAPI(title="AI Investment Assistant API", version="1.0")

# Cho phép frontend (Vercel) gọi tới - chỉnh lại domain cụ thể sau khi deploy để bảo mật hơn
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.environ.get("ALLOWED_ORIGINS", "*").split(","),
    allow_methods=["*"],
    allow_headers=["*"],
)


def _gather_dataset(symbols: list[str] | None = None) -> dict:
    """Gom dữ liệu mới nhất từ Supabase để đưa vào Gemini phân tích."""
    client = get_client()

    macro = client.table("latest_macro_indicators").select("*").execute().data
    markets_q = client.table("latest_market_prices").select("*")
    if symbols:
        markets_q = markets_q.in_("symbol", symbols)
    markets = markets_q.execute().data

    fundamentals_q = client.table("fundamentals").select("*").order("period_date", desc=True).limit(50)
    if symbols:
        fundamentals_q = fundamentals_q.in_("symbol", symbols)
    fundamentals = fundamentals_q.execute().data

    news = client.table("news_articles").select("*").order("published_at", desc=True).limit(40).execute().data
    social = client.table("social_sentiment").select("*").order("sample_date", desc=True).limit(30).execute().data
    events = client.table("global_events").select("*").order("event_date", desc=True).limit(20).execute().data

    return {
        "macro": macro,
        "markets": markets,
        "fundamentals": fundamentals,
        "news": news,
        "social": social,
        "events": events,
    }


def _save_report(report_type: str, question: str | None, symbols: list[str] | None, answer: dict):
    get_client().table("ai_reports").insert(
        {
            "report_type": report_type,
            "question": question,
            "related_symbols": symbols,
            "answer": answer,
        }
    ).execute()


# ---------------------------------------------------------------------
# Endpoints: dữ liệu thô cho dashboard
# ---------------------------------------------------------------------
@app.get("/api/health")
def health():
    return {"status": "ok", "time": datetime.now(timezone.utc).isoformat()}


@app.get("/api/macro")
def get_macro():
    return fetch_latest("latest_macro_indicators", "period_date", limit=100)


@app.get("/api/markets")
def get_markets():
    return fetch_latest("latest_market_prices", "market_date", limit=100)


@app.get("/api/news")
def get_news(limit: int = 30):
    return fetch_latest("news_articles", "published_at", limit=limit)


@app.get("/api/social")
def get_social():
    return fetch_latest("social_sentiment", "sample_date", limit=50)


@app.get("/api/events")
def get_events():
    return fetch_latest("global_events", "event_date", limit=30)


@app.get("/api/summary")
def get_summary():
    """Gộp tất cả dữ liệu mới nhất cho trang dashboard chính."""
    return _gather_dataset()


# ---------------------------------------------------------------------
# Endpoints: AI Analysis (gọi Gemini, on-demand)
# ---------------------------------------------------------------------
class AskRequest(BaseModel):
    question: str
    symbols: list[str] | None = None


@app.post("/api/ask")
def ask(req: AskRequest):
    if not req.question or len(req.question.strip()) < 3:
        raise HTTPException(400, "Câu hỏi quá ngắn.")
    dataset = _gather_dataset(req.symbols)
    try:
        answer = ask_question(req.question, dataset)
    except Exception as e:
        raise HTTPException(502, f"Lỗi khi gọi Gemini API: {e}")
    _save_report("ask_question", req.question, req.symbols, answer)
    return answer


@app.get("/api/daily-report")
def get_daily_report(refresh: bool = False):
    """Trả về báo cáo tổng hợp hôm nay. Nếu chưa có hoặc refresh=true thì tạo mới."""
    client = get_client()
    if not refresh:
        today = datetime.now(timezone.utc).date().isoformat()
        existing = (
            client.table("ai_reports")
            .select("*")
            .eq("report_type", "daily_summary")
            .gte("created_at", today)
            .order("created_at", desc=True)
            .limit(1)
            .execute()
            .data
        )
        if existing:
            return existing[0]["answer"]

    dataset = _gather_dataset()
    try:
        answer = daily_summary(dataset)
    except Exception as e:
        raise HTTPException(502, f"Lỗi khi gọi Gemini API: {e}")
    _save_report("daily_summary", None, None, answer)
    return answer


class OutlookRequest(BaseModel):
    symbol: str


@app.post("/api/outlook")
def outlook(req: OutlookRequest):
    dataset = _gather_dataset([req.symbol])
    try:
        answer = asset_outlook(req.symbol, dataset)
    except Exception as e:
        raise HTTPException(502, f"Lỗi khi gọi Gemini API: {e}")
    _save_report("asset_outlook", None, [req.symbol], answer)
    return answer
