"use client";
import { NewsArticle } from "@/lib/api";

const sentimentColor: Record<string, string> = {
  positive: "var(--up)",
  negative: "var(--down)",
  neutral: "var(--parchment-dim)",
};

export default function NewsFeed({ data }: { data: NewsArticle[] }) {
  return (
    <section>
      <h2 className="mb-4 font-display text-2xl text-parchment">Tin tức &amp; Tâm lý thị trường</h2>
      <div className="divide-y hairline border-y hairline">
        {data.map((n) => (
          <a
            key={n.url}
            href={n.url}
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-start gap-4 py-4 transition hover:bg-ink2"
          >
            <span
              className="mt-1.5 h-2 w-2 shrink-0 rounded-full"
              style={{ background: sentimentColor[n.sentiment_label] || "#888" }}
              title={n.sentiment_label}
            />
            <div className="min-w-0 flex-1">
              <p className="text-sm leading-snug text-parchment/90">{n.title}</p>
              <div className="mt-1 flex flex-wrap items-center gap-2 font-mono text-[11px] text-parchmentDim">
                <span>{n.source}</span>
                <span>·</span>
                <span>{new Date(n.published_at).toLocaleDateString("vi-VN")}</span>
                {n.tickers?.map((t) => (
                  <span key={t} className="rounded-full border hairline px-2 py-0.5 text-gold">
                    {t}
                  </span>
                ))}
              </div>
            </div>
          </a>
        ))}
        {data.length === 0 && <p className="py-6 text-sm text-parchmentDim">Chưa có tin tức nào được thu thập.</p>}
      </div>
    </section>
  );
}
