"""
Thu thập dữ liệu vĩ mô từ FRED (Federal Reserve Economic Data) - MIỄN PHÍ.
Đăng ký API key free tại: https://fred.stlouisfed.org/docs/api/api_key.html
Biến môi trường cần: FRED_API_KEY
"""
import os
import requests
from datetime import datetime, timedelta
from .config import FRED_SERIES

FRED_BASE = "https://api.stlouisfed.org/fred/series/observations"


def fetch_series(series_id: str, api_key: str, lookback_days: int = 400):
    start = (datetime.utcnow() - timedelta(days=lookback_days)).strftime("%Y-%m-%d")
    params = {
        "series_id": series_id,
        "api_key": api_key,
        "file_type": "json",
        "observation_start": start,
        "sort_order": "desc",
        "limit": 6,  # lấy vài kỳ gần nhất để tính xu hướng
    }
    resp = requests.get(FRED_BASE, params=params, timeout=20)
    resp.raise_for_status()
    return resp.json().get("observations", [])


def collect_macro_indicators() -> list[dict]:
    api_key = os.environ.get("FRED_API_KEY")
    if not api_key:
        print("[macro] Thiếu FRED_API_KEY, bỏ qua thu thập macro.")
        return []

    rows = []
    for code, name in FRED_SERIES.items():
        try:
            observations = fetch_series(code, api_key)
        except Exception as e:
            print(f"[macro] Lỗi khi lấy {code}: {e}")
            continue

        for obs in observations:
            value = obs.get("value")
            if value in (None, ".", ""):
                continue
            rows.append(
                {
                    "indicator_code": code,
                    "indicator_name": name,
                    "country": "US",
                    "value": float(value),
                    "unit": "index/percent/level",
                    "period_date": obs["date"],
                    "source": "FRED",
                }
            )
    print(f"[macro] Thu thập {len(rows)} bản ghi.")
    return rows


if __name__ == "__main__":
    data = collect_macro_indicators()
    print(data[:5])
