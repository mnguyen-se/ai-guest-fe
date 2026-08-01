"""
Thu thập dữ liệu cơ bản của doanh nghiệp (fundamentals) qua yfinance - MIỄN PHÍ.
Lưu ý: yfinance lấy dữ liệu từ Yahoo Finance, độ trễ/độ đầy đủ tùy mã.
Insider trading & institutional holdings free-tier: yfinance có field
gần đúng (heldPercentInsiders, heldPercentInstitutions).
"""
from datetime import datetime, timezone
import yfinance as yf
from .config import FUNDAMENTALS_SYMBOLS


def collect_fundamentals() -> list[dict]:
    today = datetime.now(timezone.utc).date().isoformat()
    rows = []
    for symbol in FUNDAMENTALS_SYMBOLS:
        try:
            info = yf.Ticker(symbol).info
            rows.append(
                {
                    "symbol": symbol,
                    "period_date": today,
                    "pe_ratio": info.get("trailingPE"),
                    "pb_ratio": info.get("priceToBook"),
                    "eps": info.get("trailingEps"),
                    "revenue": info.get("totalRevenue"),
                    "net_income": info.get("netIncomeToCommon"),
                    "gross_margin": info.get("grossMargins"),
                    "debt_to_equity": info.get("debtToEquity"),
                    "free_cash_flow": info.get("freeCashflow"),
                    "market_cap": info.get("marketCap"),
                    "institutional_ownership_pct": info.get("heldPercentInstitutions"),
                    "insider_ownership_pct": info.get("heldPercentInsiders"),
                    "source": "yfinance",
                }
            )
        except Exception as e:
            print(f"[fundamentals] Lỗi khi lấy {symbol}: {e}")
            continue
    print(f"[fundamentals] Thu thập {len(rows)} bản ghi.")
    return rows


if __name__ == "__main__":
    print(collect_fundamentals()[:3])
