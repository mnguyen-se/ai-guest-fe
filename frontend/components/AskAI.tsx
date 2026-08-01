"use client";
import { useState } from "react";
import { api, AIAnalysis } from "@/lib/api";
import AnalysisCard from "./AnalysisCard";

const SUGGESTIONS = [
  "Vì sao thị trường tăng/giảm hôm nay?",
  "Ngành nào đang được dòng tiền quan tâm?",
  "Rủi ro nào tôi cần chú ý tuần này?",
  "Những sự kiện quan trọng nhất hôm nay là gì?",
];

export default function AskAI() {
  const [question, setQuestion] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<AIAnalysis | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function handleAsk(q?: string) {
    const finalQuestion = q ?? question;
    if (!finalQuestion.trim()) return;
    setLoading(true);
    setError(null);
    try {
      const data = await api.ask(finalQuestion);
      setResult(data);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Đã có lỗi xảy ra.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <section className="space-y-5">
      <div className="flex items-baseline justify-between">
        <h2 className="font-display text-2xl text-parchment">Hỏi AI phân tích</h2>
        <span className="font-mono text-xs text-parchmentDim">không đưa ra khuyến nghị mua/bán</span>
      </div>

      <div className="flex flex-col gap-3 sm:flex-row">
        <input
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && handleAsk()}
          placeholder="vd: Vì sao vàng tăng giá tuần này?"
          className="flex-1 border-b hairline bg-transparent px-1 py-3 text-parchment placeholder:text-parchmentDim/60 focus:border-gold focus:outline-none"
        />
        <button
          onClick={() => handleAsk()}
          disabled={loading}
          className="whitespace-nowrap border border-gold px-6 py-3 font-mono text-xs uppercase tracking-widest text-gold transition hover:bg-gold hover:text-ink disabled:opacity-40"
        >
          {loading ? "Đang phân tích…" : "Phân tích"}
        </button>
      </div>

      <div className="flex flex-wrap gap-2">
        {SUGGESTIONS.map((s) => (
          <button
            key={s}
            onClick={() => {
              setQuestion(s);
              handleAsk(s);
            }}
            className="rounded-full border hairline px-3 py-1.5 text-xs text-parchmentDim transition hover:border-gold hover:text-gold"
          >
            {s}
          </button>
        ))}
      </div>

      {error && <p className="text-sm text-down">{error}</p>}
      {loading && (
        <div className="animate-pulse rounded-sm border hairline bg-ink2 p-6 text-sm text-parchmentDim">
          Đang đọc dữ liệu vĩ mô, thị trường, tin tức và tổng hợp phân tích…
        </div>
      )}
      {result && !loading && <AnalysisCard data={result} />}
    </section>
  );
}
