"""
Danh sách các mã / chỉ số cần thu thập. Chỉnh sửa file này để thêm/bớt
mã theo dõi mà KHÔNG cần đụng vào logic thu thập.
"""

# ---- Macro (FRED series codes: https://fred.stlouisfed.org/) ----
FRED_SERIES = {
    "CPIAUCSL": "CPI - Consumer Price Index (All Urban Consumers)",
    "PPIACO": "PPI - Producer Price Index",
    "GDP": "GDP - Gross Domestic Product",
    "UNRATE": "Unemployment Rate",
    "M2SL": "M2 Money Supply",
    "FEDFUNDS": "Federal Funds Effective Rate",
    "DGS10": "10-Year Treasury Yield",
    "DGS2": "2-Year Treasury Yield",
    "MANEMP": "Manufacturing Employment (proxy cho PMI trend)",
    "INDPRO": "Industrial Production Index",
}

# ---- Stocks tiêu biểu (có thể thêm mã bạn quan tâm) ----
STOCKS = ["AAPL", "MSFT", "NVDA", "GOOGL", "AMZN", "META", "TSLA", "AVGO", "JPM", "XOM"]

# ---- ETFs & Indexes ----
ETFS = ["SPY", "QQQ", "DIA", "IWM", "ARKK", "XLF", "XLE", "XLK"]
INDEXES = ["^GSPC", "^IXIC", "^DJI", "^VIX", "^TNX"]  # S&P500, Nasdaq, Dow, VIX, 10Y yield futures

# ---- Commodities (Yahoo Finance futures tickers) ----
COMMODITIES = {
    "GC=F": "Gold",
    "SI=F": "Silver",
    "CL=F": "Crude Oil WTI",
    "NG=F": "Natural Gas",
    "HG=F": "Copper",
}

# ---- Crypto ----
CRYPTO = ["BTC-USD", "ETH-USD", "SOL-USD", "BNB-USD"]

# ---- Forex ----
FOREX = ["EURUSD=X", "USDJPY=X", "GBPUSD=X", "DX-Y.NYB"]  # DX-Y.NYB = US Dollar Index

# Tất cả symbol cần fundamentals (chỉ áp dụng cho cổ phiếu)
FUNDAMENTALS_SYMBOLS = STOCKS

# ---- News RSS feeds (miễn phí, không cần API key) ----
RSS_FEEDS = {
    "Yahoo Finance": "https://finance.yahoo.com/news/rssindex",
    "CNBC Markets": "https://search.cnbc.com/rs/search/combinedcms/view.xml?partnerId=wrss01&id=20910258",
    "CNBC Economy": "https://search.cnbc.com/rs/search/combinedcms/view.xml?partnerId=wrss01&id=20910258",
    "Investing.com": "https://www.investing.com/rss/news.rss",
    "MarketWatch": "https://www.marketwatch.com/rss/topstories",
    "Reuters Business (Google News proxy)": "https://news.google.com/rss/search?q=reuters+business+markets&hl=en-US&gl=US&ceid=US:en",
    "Fed Announcements (Google News proxy)": "https://news.google.com/rss/search?q=Federal+Reserve+announcement&hl=en-US&gl=US&ceid=US:en",
}

# ---- Google Trends keywords ----
TRENDS_KEYWORDS = ["recession", "inflation", "stock market crash", "Bitcoin", "AI stocks", "interest rate"]

# ---- Reddit subreddits (cần REDDIT_CLIENT_ID/SECRET, optional) ----
REDDIT_SUBREDDITS = ["wallstreetbets", "stocks", "investing", "economy"]
