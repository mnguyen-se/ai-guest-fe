// Wrapper gọi tới Backend API (FastAPI deploy trên Render/Railway...)
// Đặt biến môi trường NEXT_PUBLIC_API_URL trên Vercel trỏ tới URL backend.

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_URL}${path}`, {
    ...options,
    headers: { "Content-Type": "application/json", ...options?.headers },
    cache: "no-store",
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`API lỗi (${res.status}): ${text}`);
  }
  return res.json();
}

export interface MacroIndicator {
  indicator_code: string;
  indicator_name: string;
  value: number;
  unit: string;
  period_date: string;
  country: string;
}

export interface MarketPrice {
  symbol: string;
  asset_type: string;
  name: string;
  price: number;
  change_pct: number;
  market_date: string;
}

export interface NewsArticle {
  title: string;
  url: string;
  source: string;
  published_at: string;
  summary: string;
  sentiment_score: number;
  sentiment_label: "positive" | "negative" | "neutral";
  tickers: string[];
  topics: string[];
}

export interface SocialSentiment {
  platform: string;
  topic: string;
  sentiment_score: number | null;
  trend_score: number | null;
  sample_date: string;
}

export interface AIAnalysis {
  summary: string;
  confidence_score: number;
  risk_score: number;
  facts: string[];
  expert_opinions: string[];
  ai_inferences: string[];
  bullish_factors: string[];
  bearish_factors: string[];
  disagreements: string[];
  related_news: string[];
  historical_similar_cases: string[];
  outlook: { "3_months": string; "6_months": string; "12_months": string };
  data_limitations: string;
}

export const api = {
  macro: () => request<MacroIndicator[]>("/api/macro"),
  markets: () => request<MarketPrice[]>("/api/markets"),
  news: (limit = 30) => request<NewsArticle[]>(`/api/news?limit=${limit}`),
  social: () => request<SocialSentiment[]>("/api/social"),
  dailyReport: (refresh = false) => request<AIAnalysis>(`/api/daily-report?refresh=${refresh}`),
  ask: (question: string, symbols?: string[]) =>
    request<AIAnalysis>("/api/ask", { method: "POST", body: JSON.stringify({ question, symbols }) }),
  outlook: (symbol: string) =>
    request<AIAnalysis>("/api/outlook", { method: "POST", body: JSON.stringify({ symbol }) }),
};
