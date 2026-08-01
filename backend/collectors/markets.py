"""
Thu thập giá thị trường: cổ phiếu, ETF, index, hàng hóa, crypto, forex, VIX.
Dùng yfinance - MIỄN PHÍ, không cần API key.
"""
from datetime import datetime, timezone
import yfinance as yf
from .config import STOCKS, ETFS, INDEXES, COMMODITIES, CRYPTO, FOREX


def _asset_type_for(symbol: str) -> str:
    if symbol in STOCKS:
        return "stock"
    if symbol in ETFS:
        return "etf"
    if symbol in INDEXES:
        return "volatility" if symbol == "^VIX" else "index"
    if symbol in COMMODITIES:
        return "commodity"
    if symbol in CRYPTO:
        return "crypto"
    if symbol in FOREX:
        return "forex"
    return "unknown"


def collect_market_prices() -> list[dict]:
    all_symbols = STOCKS + ETFS + INDEXES + list(COMMODITIES.keys()) + CRYPTO + FOREX
    today = datetime.now(timezone.utc).date().isoformat()
    rows = []

    # yfinance cho phép tải nhiều mã cùng lúc, nhanh hơn gọi từng mã
    data = yf.download(
        tickers=" ".join(all_symbols),
        period="5d",
        interval="1d",
        group_by="ticker",
        threads=True,
        progress=False,
    )

    for symbol in all_symbols:
        try:
            if len(all_symbols) == 1:
                hist = data
            else:
                hist = data[symbol]
            hist = hist.dropna()
            if hist.empty:
                continue
            last = hist.iloc[-1]
            prev_close = hist.iloc[-2]["Close"] if len(hist) > 1 else last["Close"]
            change_pct = ((last["Close"] - prev_close) / prev_close * 100) if prev_close else None

            name = COMMODITIES.get(symbol, symbol)
            rows.append(
                {
                    "symbol": symbol,
                    "asset_type": _asset_type_for(symbol),
                    "name": name,
                    "price": round(float(last["Close"]), 4),
                    "change_pct": round(float(change_pct), 3) if change_pct is not None else None,
                    "volume": int(last["Volume"]) if "Volume" in last and last["Volume"] == last["Volume"] else None,
                    "market_date": today,
                    "source": "yfinance",
                }
            )
        except Exception as e:
            print(f"[markets] Lỗi xử lý {symbol}: {e}")
            continue

    print(f"[markets] Thu thập {len(rows)} bản ghi.")
    return rows


if __name__ == "__main__":
    print(collect_market_prices()[:5])
