"""
Global events: thay vì trả phí cho 1 nguồn event calendar riêng, ta suy ra
sự kiện toàn cầu quan trọng từ chính các tin tức đã gắn nhãn topic
(geopolitics, supply_chain, ...) thu thập ở news.py.
Đây là cách tiếp cận free-tier, chấp nhận độ chính xác thấp hơn so với
dịch vụ event-calendar chuyên dụng trả phí.
"""
from datetime import datetime, timezone

EVENT_TOPIC_MAP = {
    "geopolitics": "war_or_election",
    "supply_chain": "supply_chain",
}

HIGH_IMPACT_KEYWORDS = ["war", "invasion", "sanction", "default", "pandemic", "earthquake", "hurricane"]


def derive_events_from_news(news_rows: list[dict]) -> list[dict]:
    rows = []
    for article in news_rows:
        topics = article.get("topics", [])
        relevant = [t for t in topics if t in EVENT_TOPIC_MAP]
        if not relevant:
            continue

        text_l = (article["title"] + " " + (article.get("summary") or "")).lower()
        impact = "high" if any(k in text_l for k in HIGH_IMPACT_KEYWORDS) else "medium"

        rows.append(
            {
                "title": article["title"],
                "category": EVENT_TOPIC_MAP[relevant[0]],
                "description": article.get("summary"),
                "event_date": (article.get("published_at") or datetime.now(timezone.utc).isoformat())[:10],
                "impact_level": impact,
                "related_regions": [],
                "source": article.get("source"),
            }
        )
    print(f"[events] Suy ra {len(rows)} sự kiện toàn cầu từ tin tức.")
    return rows
