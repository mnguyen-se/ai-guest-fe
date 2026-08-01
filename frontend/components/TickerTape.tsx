"use client";
import { MarketPrice } from "@/lib/api";

export default function TickerTape({ items }: { items: MarketPrice[] }) {
  const doubled = [...items, ...items]; // để cuộn liền mạch vô hạn

  if (items.length === 0) return null;

  return (
    <div className="w-full overflow-hidden border-y hairline bg-ink2 py-2.5">
      <div className="flex w-max ticker-track gap-10 whitespace-nowrap pr-10">
        {doubled.map((m, i) => (
          <span key={`${m.symbol}-${i}`} className="flex items-center gap-2 font-mono text-[13px]">
            <span className="text-parchmentDim">{m.symbol}</span>
            <span className="text-parchment">{m.price?.toLocaleString(undefined, { maximumFractionDigits: 2 })}</span>
            <span className={m.change_pct >= 0 ? "text-up" : "text-down"}>
              {m.change_pct >= 0 ? "▲" : "▼"} {Math.abs(m.change_pct ?? 0).toFixed(2)}%
            </span>
          </span>
        ))}
      </div>
    </div>
  );
}
