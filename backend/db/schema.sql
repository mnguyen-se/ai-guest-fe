-- =========================================================
-- AI Investment Assistant - Supabase (Postgres) Schema
-- Chạy toàn bộ file này trong Supabase SQL Editor 1 lần duy nhất
-- =========================================================

create extension if not exists "uuid-ossp";

-- 1) MACRO ECONOMY --------------------------------------------------
create table if not exists macro_indicators (
    id uuid primary key default uuid_generate_v4(),
    indicator_code text not null,       -- vd: CPI, PPI, GDP, UNRATE, M2SL, FEDFUNDS, DGS10, DGS2
    indicator_name text not null,       -- vd: "Consumer Price Index"
    country text default 'US',          -- US, EU, JP, CN...
    value numeric,
    unit text,                          -- '%', 'index', 'USD billion'...
    period_date date not null,          -- ngày dữ liệu áp dụng (không phải ngày thu thập)
    source text not null,               -- 'FRED', 'ECB', ...
    fetched_at timestamptz default now(),
    unique (indicator_code, country, period_date)
);
create index if not exists idx_macro_code_date on macro_indicators (indicator_code, period_date desc);

-- 2) FINANCIAL MARKETS ------------------------------------------------
create table if not exists market_prices (
    id uuid primary key default uuid_generate_v4(),
    symbol text not null,               -- vd: AAPL, ^GSPC, GC=F, BTC-USD, EURUSD=X, ^VIX
    asset_type text not null,           -- stock, etf, index, commodity, crypto, forex, volatility
    name text,
    price numeric,
    change_pct numeric,
    volume bigint,
    market_date date not null,
    source text default 'yfinance',
    fetched_at timestamptz default now(),
    unique (symbol, market_date)
);
create index if not exists idx_market_symbol_date on market_prices (symbol, market_date desc);

-- 3) COMPANY FUNDAMENTALS ---------------------------------------------
create table if not exists fundamentals (
    id uuid primary key default uuid_generate_v4(),
    symbol text not null,
    period_date date not null,          -- ngày báo cáo / ngày lấy snapshot
    pe_ratio numeric,
    pb_ratio numeric,
    eps numeric,
    revenue numeric,
    net_income numeric,
    gross_margin numeric,
    debt_to_equity numeric,
    free_cash_flow numeric,
    market_cap numeric,
    institutional_ownership_pct numeric,
    insider_ownership_pct numeric,
    source text default 'yfinance',
    fetched_at timestamptz default now(),
    unique (symbol, period_date)
);
create index if not exists idx_fund_symbol_date on fundamentals (symbol, period_date desc);

-- 4) NEWS ---------------------------------------------------------------
create table if not exists news_articles (
    id uuid primary key default uuid_generate_v4(),
    title text not null,
    url text unique not null,
    source text not null,               -- Reuters, CNBC, Yahoo Finance, FT, Government...
    published_at timestamptz,
    summary text,
    tickers text[],                     -- các mã liên quan được nhận diện
    topics text[],                      -- macro, earnings, geopolitics, crypto...
    sentiment_score numeric,            -- -1..1
    sentiment_label text,               -- positive / negative / neutral
    fetched_at timestamptz default now()
);
create index if not exists idx_news_published on news_articles (published_at desc);
create index if not exists idx_news_tickers on news_articles using gin (tickers);

-- 5) SOCIAL MEDIA SENTIMENT -----------------------------------------
create table if not exists social_sentiment (
    id uuid primary key default uuid_generate_v4(),
    platform text not null,             -- reddit, twitter, youtube, google_trends
    topic text not null,                -- ticker hoặc từ khóa, vd: "AAPL", "recession"
    mention_count integer,
    sentiment_score numeric,            -- -1..1
    trend_score numeric,                -- 0-100 (vd Google Trends interest)
    sample_date date not null,
    source_detail text,
    fetched_at timestamptz default now(),
    unique (platform, topic, sample_date)
);
create index if not exists idx_social_topic_date on social_sentiment (topic, sample_date desc);

-- 6) GLOBAL EVENTS --------------------------------------------------
create table if not exists global_events (
    id uuid primary key default uuid_generate_v4(),
    title text not null,
    category text not null,             -- war, election, pandemic, disaster, supply_chain, semiconductor, shipping
    description text,
    event_date date,
    impact_level text,                  -- low, medium, high
    related_regions text[],
    source text,
    fetched_at timestamptz default now()
);
create index if not exists idx_events_date on global_events (event_date desc);

-- 7) AI ANALYSIS REPORTS (lưu lại các báo cáo AI đã tạo để tra cứu lịch sử) ---
create table if not exists ai_reports (
    id uuid primary key default uuid_generate_v4(),
    report_type text not null,          -- 'daily_summary', 'ask_question', 'asset_outlook'
    question text,
    related_symbols text[],
    answer jsonb not null,              -- toàn bộ structured output (confidence, risk, evidence...)
    created_at timestamptz default now()
);
create index if not exists idx_reports_type_date on ai_reports (report_type, created_at desc);

-- 8) VIEW tiện lợi: dữ liệu mới nhất mỗi symbol ------------------------
create or replace view latest_market_prices as
select distinct on (symbol) *
from market_prices
order by symbol, market_date desc;

create or replace view latest_macro_indicators as
select distinct on (indicator_code, country) *
from macro_indicators
order by indicator_code, country, period_date desc;
