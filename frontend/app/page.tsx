import { api } from "@/lib/api";
import TickerTape from "@/components/TickerTape";
import MacroPanel from "@/components/MacroPanel";
import MarketTable from "@/components/MarketTable";
import NewsFeed from "@/components/NewsFeed";
import AskAI from "@/components/AskAI";

// Không cache trang này ở build-time, vì dữ liệu tài chính cần luôn mới
export const dynamic = "force-dynamic";

async function safeFetch<T>(fn: () => Promise<T>, fallback: T): Promise<T> {
  try {
    return await fn();
  } catch {
    return fallback;
  }
}

export default async function Home() {
  const [macro, markets, news] = await Promise.all([
    safeFetch(() => api.macro(), []),
    safeFetch(() => api.markets(), []),
    safeFetch(() => api.news(20), []),
  ]);

  return (
    <main className="min-h-screen bg-ink">
      <header className="border-b hairline px-6 py-8 sm:px-10">
        <p className="font-mono text-xs uppercase tracking-[0.3em] text-gold">
          {new Date().toLocaleDateString("vi-VN", { weekday: "long", year: "numeric", month: "long", day: "numeric" })}
        </p>
        <h1 className="mt-2 font-display text-4xl text-parchment sm:text-5xl">Đài Quan Sát Đầu Tư</h1>
        <p className="mt-2 max-w-2xl text-sm text-parchmentDim">
          Tổng hợp vĩ mô, thị trường, cơ bản doanh nghiệp, tin tức và tâm lý mạng xã hội —
          phân tích có bằng chứng, không dự đoán mù quáng, không thay bạn ra quyết định.
        </p>
      </header>

      <TickerTape items={markets} />

      <div className="mx-auto max-w-6xl space-y-16 px-6 py-12 sm:px-10">
        <MacroPanel data={macro} />
        <MarketTable data={markets} />
        <NewsFeed data={news} />
        <AskAI />
      </div>

      <footer className="border-t hairline px-6 py-8 text-center font-mono text-[11px] text-parchmentDim sm:px-10">
        Chỉ phục vụ mục đích tham khảo cá nhân — không phải lời khuyên đầu tư.
      </footer>
    </main>
  );
}
