"use client";
import { AIAnalysis } from "@/lib/api";
import ScoreGauge from "./ScoreGauge";

function Section({ title, items, accent }: { title: string; items: string[]; accent?: string }) {
  if (!items || items.length === 0) return null;
  return (
    <div>
      <h4
        className="mb-2 font-mono text-[11px] uppercase tracking-widest"
        style={{ color: accent || "var(--parchment-dim)" }}
      >
        {title}
      </h4>
      <ul className="space-y-1.5">
        {items.map((it, i) => (
          <li key={i} className="flex gap-2 text-sm leading-relaxed text-parchment/90">
            <span className="text-hairline" style={{ color: accent || "#2a3a50" }}>
              —
            </span>
            <span>{it}</span>
          </li>
        ))}
      </ul>
    </div>
  );
}

export default function AnalysisCard({ data }: { data: AIAnalysis }) {
  return (
    <div className="rounded-sm border hairline bg-ink2 p-6">
      <div className="mb-6 flex flex-col gap-6 border-b hairline pb-6 sm:flex-row sm:items-center sm:justify-between">
        <p className="font-display text-lg italic leading-snug text-parchment sm:max-w-xl">
          {data.summary}
        </p>
        <div className="flex gap-6">
          <ScoreGauge label="Độ tin cậy" value={data.confidence_score} tone="gold" />
          <ScoreGauge label="Rủi ro" value={data.risk_score} tone="down" />
        </div>
      </div>

      <div className="grid grid-cols-1 gap-8 md:grid-cols-2">
        <Section title="Yếu tố tích cực (Bullish)" items={data.bullish_factors} accent="var(--up)" />
        <Section title="Yếu tố tiêu cực (Bearish)" items={data.bearish_factors} accent="var(--down)" />
        <Section title="Số liệu / bằng chứng xác thực" items={data.facts} />
        <Section title="Ý kiến chuyên gia được trích dẫn" items={data.expert_opinions} />
        <Section title="Suy luận riêng của AI" items={data.ai_inferences} accent="var(--gold)" />
        <Section title="Điểm các nguồn mâu thuẫn nhau" items={data.disagreements} accent="var(--down)" />
        <Section title="Tin tức liên quan" items={data.related_news} />
        <Section title="Trường hợp lịch sử tương tự" items={data.historical_similar_cases} />
      </div>

      {data.outlook && (
        <div className="mt-8 grid grid-cols-1 gap-3 border-t hairline pt-6 sm:grid-cols-3">
          {(["3_months", "6_months", "12_months"] as const).map((k) => (
            <div key={k} className="rounded-sm border hairline bg-ink p-4">
              <div className="mb-1 font-mono text-[11px] uppercase tracking-widest text-gold">
                {k.replace("_", " ").replace("months", "tháng")}
              </div>
              <p className="text-sm leading-relaxed text-parchment/90">{data.outlook[k]}</p>
            </div>
          ))}
        </div>
      )}

      {data.data_limitations && (
        <p className="mt-6 border-t hairline pt-4 text-xs italic text-parchmentDim">
          ⚠ Giới hạn dữ liệu: {data.data_limitations}
        </p>
      )}
    </div>
  );
}
