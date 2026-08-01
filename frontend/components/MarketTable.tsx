"use client";
import { useState } from "react";
import { MarketPrice } from "@/lib/api";

const TABS: { key: string; label: string }[] = [
  { key: "stock", label: "Cổ phiếu" },
  { key: "etf", label: "ETF" },
  { key: "index", label: "Chỉ số" },
  { key: "commodity", label: "Hàng hóa" },
  { key: "crypto", label: "Crypto" },
  { key: "forex", label: "Forex" },
];

export default function MarketTable({ data }: { data: MarketPrice[] }) {
  const [tab, setTab] = useState("stock");
  const filtered = data.filter((d) => d.asset_type === tab);

  return (
    <section>
      <div className="mb-4 flex items-baseline justify-between">
        <h2 className="font-display text-2xl text-parchment">Thị trường tài chính</h2>
      </div>
      <div className="mb-4 flex flex-wrap gap-1 border-b hairline">
        {TABS.map((t) => (
          <button
            key={t.key}
            onClick={() => setTab(t.key)}
            className={`px-4 py-2 font-mono text-xs uppercase tracking-widest transition ${
              tab === t.key ? "border-b-2 border-gold text-gold" : "text-parchmentDim hover:text-parchment"
            }`}
          >
            {t.label}
          </button>
        ))}
      </div>
      <table className="w-full border-collapse text-sm">
        <tbody>
          {filtered.map((m) => (
            <tr key={m.symbol} className="border-b hairline">
              <td className="py-2.5 font-mono text-parchmentDim">{m.symbol}</td>
              <td className="py-2.5 text-parchment/80">{m.name}</td>
              <td className="py-2.5 text-right font-mono text-parchment">
                {m.price?.toLocaleString(undefined, { maximumFractionDigits: 2 })}
              </td>
              <td className={`py-2.5 text-right font-mono ${m.change_pct >= 0 ? "text-up" : "text-down"}`}>
                {m.change_pct >= 0 ? "▲" : "▼"} {Math.abs(m.change_pct ?? 0).toFixed(2)}%
              </td>
            </tr>
          ))}
          {filtered.length === 0 && (
            <tr>
              <td colSpan={4} className="py-6 text-center text-sm text-parchmentDim">
                Chưa có dữ liệu cho nhóm này.
              </td>
            </tr>
          )}
        </tbody>
      </table>
    </section>
  );
}
