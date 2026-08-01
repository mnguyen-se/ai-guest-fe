"""
Script điều phối: chạy TẤT CẢ các collector rồi ghi vào Supabase.
Được gọi tự động mỗi ngày bởi GitHub Actions (xem .github/workflows/collect-data.yml)

Chạy thủ công: python collect_daily.py
"""
import traceback
from collectors.macro import collect_macro_indicators
from collectors.markets import collect_market_prices
from collectors.fundamentals import collect_fundamentals
from collectors.news import collect_news
from collectors.social import collect_social_sentiment
from collectors.events import derive_events_from_news
from db.supabase_client import upsert


def run_step(name: str, fn, table: str, on_conflict: str):
    print(f"\n===== [{name}] Bắt đầu =====")
    try:
        rows = fn()
        upsert(table, rows, on_conflict)
        print(f"===== [{name}] Hoàn tất: {len(rows)} bản ghi ghi vào '{table}' =====")
        return rows
    except Exception:
        print(f"===== [{name}] LỖI =====")
        traceback.print_exc()
        return []


def main():
    run_step("Macro", collect_macro_indicators, "macro_indicators", "indicator_code,country,period_date")
    run_step("Markets", collect_market_prices, "market_prices", "symbol,market_date")
    run_step("Fundamentals", collect_fundamentals, "fundamentals", "symbol,period_date")
    news_rows = run_step("News", collect_news, "news_articles", "url")
    run_step("Social", collect_social_sentiment, "social_sentiment", "platform,topic,sample_date")

    # Events được suy ra từ news vừa thu thập (không gọi nguồn riêng)
    print("\n===== [Events] Bắt đầu =====")
    try:
        event_rows = derive_events_from_news(news_rows)
        # global_events không có unique constraint tự nhiên dễ chọn -> dùng insert thường (bỏ trùng theo title+event_date thủ công nếu cần)
        from db.supabase_client import get_client

        if event_rows:
            get_client().table("global_events").insert(event_rows).execute()
        print(f"===== [Events] Hoàn tất: {len(event_rows)} bản ghi =====")
    except Exception:
        print("===== [Events] LỖI =====")
        traceback.print_exc()

    print("\n✅ Thu thập dữ liệu hằng ngày hoàn tất.")


if __name__ == "__main__":
    main()
