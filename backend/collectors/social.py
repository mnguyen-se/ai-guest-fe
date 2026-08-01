"""
Thu thập tín hiệu mạng xã hội:
- Google Trends (miễn phí, qua pytrends, không cần API key)
- Reddit (miễn phí nhưng cần đăng ký app -> REDDIT_CLIENT_ID / REDDIT_CLIENT_SECRET,
  nếu không có key thì bước này sẽ tự bỏ qua, không lỗi)
"""
import os
import time
from datetime import datetime, timezone
from .config import TRENDS_KEYWORDS, REDDIT_SUBREDDITS


def collect_google_trends() -> list[dict]:
    try:
        from pytrends.request import TrendReq
    except ImportError:
        print("[social] Chưa cài pytrends, bỏ qua Google Trends.")
        return []

    rows = []
    today = datetime.now(timezone.utc).date().isoformat()
    try:
        pytrends = TrendReq(hl="en-US", tz=0)
        # pytrends giới hạn 5 từ khóa / lần gọi
        for i in range(0, len(TRENDS_KEYWORDS), 5):
            batch = TRENDS_KEYWORDS[i : i + 5]
            pytrends.build_payload(batch, timeframe="now 7-d")
            df = pytrends.interest_over_time()
            if df.empty:
                continue
            latest = df.iloc[-1]
            for kw in batch:
                if kw not in latest:
                    continue
                rows.append(
                    {
                        "platform": "google_trends",
                        "topic": kw,
                        "mention_count": None,
                        "sentiment_score": None,  # Google Trends chỉ đo mức độ quan tâm, không đo sentiment
                        "trend_score": float(latest[kw]),
                        "sample_date": today,
                        "source_detail": "pytrends interest_over_time (7d)",
                    }
                )
            time.sleep(1)  # tránh bị rate-limit
    except Exception as e:
        print(f"[social] Lỗi Google Trends: {e}")
    print(f"[social] Google Trends: {len(rows)} bản ghi.")
    return rows


def collect_reddit_sentiment() -> list[dict]:
    client_id = os.environ.get("REDDIT_CLIENT_ID")
    client_secret = os.environ.get("REDDIT_CLIENT_SECRET")
    if not client_id or not client_secret:
        print("[social] Thiếu REDDIT_CLIENT_ID/SECRET, bỏ qua Reddit.")
        return []

    try:
        import praw
        from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
    except ImportError:
        print("[social] Chưa cài praw, bỏ qua Reddit.")
        return []

    analyzer = SentimentIntensityAnalyzer()
    today = datetime.now(timezone.utc).date().isoformat()
    reddit = praw.Reddit(
        client_id=client_id,
        client_secret=client_secret,
        user_agent="ai-investment-assistant/1.0 (personal use)",
    )

    rows = []
    for sub_name in REDDIT_SUBREDDITS:
        try:
            subreddit = reddit.subreddit(sub_name)
            scores, count = [], 0
            for post in subreddit.hot(limit=25):
                text = f"{post.title}. {post.selftext[:300]}"
                scores.append(analyzer.polarity_scores(text)["compound"])
                count += 1
            if not scores:
                continue
            avg_score = sum(scores) / len(scores)
            rows.append(
                {
                    "platform": "reddit",
                    "topic": sub_name,
                    "mention_count": count,
                    "sentiment_score": round(avg_score, 3),
                    "trend_score": None,
                    "sample_date": today,
                    "source_detail": "top 25 hot posts",
                }
            )
        except Exception as e:
            print(f"[social] Lỗi subreddit {sub_name}: {e}")
            continue
    print(f"[social] Reddit: {len(rows)} bản ghi.")
    return rows


def collect_social_sentiment() -> list[dict]:
    return collect_google_trends() + collect_reddit_sentiment()


if __name__ == "__main__":
    print(collect_social_sentiment())
