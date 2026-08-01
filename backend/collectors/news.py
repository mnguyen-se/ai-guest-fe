"""
Thu thập tin tức từ các nguồn RSS miễn phí + phân tích sentiment cục bộ
bằng VADER (nhẹ, chạy local, không tốn phí API).
Sentiment ở bước này chỉ mang tính sơ bộ (fast pass) - phân tích sâu hơn
(giải thích, liên hệ ngữ cảnh) sẽ do Gemini đảm nhiệm ở lớp AI Analysis.
"""
import re
import feedparser
from datetime import datetime, timezone
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from .config import RSS_FEEDS, STOCKS

_analyzer = SentimentIntensityAnalyzer()

TOPIC_KEYWORDS = {
    "macro": ["inflation", "cpi", "gdp", "unemployment", "fed", "interest rate", "central bank"],
    "earnings": ["earnings", "revenue", "profit", "eps", "guidance"],
    "geopolitics": ["war", "sanction", "election", "conflict", "tariff"],
    "crypto": ["bitcoin", "crypto", "ethereum", "blockchain"],
    "commodities": ["oil", "gold", "silver", "opec", "natural gas", "copper"],
    "supply_chain": ["supply chain", "shipping", "semiconductor", "chip shortage"],
}


def _guess_topics(text: str) -> list[str]:
    text_l = text.lower()
    return [topic for topic, kws in TOPIC_KEYWORDS.items() if any(k in text_l for k in kws)]


def _guess_tickers(text: str) -> list[str]:
    found = []
    for sym in STOCKS:
        if re.search(rf"\b{re.escape(sym)}\b", text):
            found.append(sym)
    return found


def _sentiment(text: str):
    score = _analyzer.polarity_scores(text)["compound"]
    if score >= 0.15:
        label = "positive"
    elif score <= -0.15:
        label = "negative"
    else:
        label = "neutral"
    return score, label


def collect_news(max_per_feed: int = 15) -> list[dict]:
    rows = []
    seen_urls = set()
    for source_name, feed_url in RSS_FEEDS.items():
        try:
            parsed = feedparser.parse(feed_url)
        except Exception as e:
            print(f"[news] Lỗi feed {source_name}: {e}")
            continue

        for entry in parsed.entries[:max_per_feed]:
            url = entry.get("link")
            if not url or url in seen_urls:
                continue
            seen_urls.add(url)

            title = entry.get("title", "").strip()
            summary = re.sub("<[^<]+?>", "", entry.get("summary", ""))[:500]
            full_text = f"{title}. {summary}"

            published = entry.get("published_parsed")
            published_at = (
                datetime(*published[:6], tzinfo=timezone.utc).isoformat()
                if published
                else datetime.now(timezone.utc).isoformat()
            )

            score, label = _sentiment(full_text)
            rows.append(
                {
                    "title": title,
                    "url": url,
                    "source": source_name,
                    "published_at": published_at,
                    "summary": summary,
                    "tickers": _guess_tickers(full_text),
                    "topics": _guess_topics(full_text),
                    "sentiment_score": round(score, 3),
                    "sentiment_label": label,
                }
            )
    print(f"[news] Thu thập {len(rows)} bài viết.")
    return rows


if __name__ == "__main__":
    for r in collect_news()[:5]:
        print(r["source"], "-", r["title"], "-", r["sentiment_label"])
