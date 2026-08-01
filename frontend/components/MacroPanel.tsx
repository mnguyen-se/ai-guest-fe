"use client";
import { MacroIndicator } from "@/lib/api";

export default function MacroPanel({ data }: { data: MacroIndicator[] }) {
  return (
    <section>
      <h2 className="mb-4 font-display text-2xl text-parchment">Vĩ mô</h2>
      <div className="grid grid-cols-2 gap-px overflow-hidden rounded-sm border hairline bg-hairline sm:grid-cols-3 lg:grid-cols-5">
        {data.map((m) => (
          <div key={m.indicator_code} className="bg-ink2 p-4">
            <div className="mb-1 truncate text-[11px] uppercase tracking-wider text-parchmentDim">
              {m.indicator_name}
            </div>
            <div className="font-mono text-xl text-parchment">
              {m.value?.toLocaleString(undefined, { maximumFractionDigits: 2 })}
            </div>
            <div className="mt-1 text-[11px] text-parchmentDim">{m.period_date}</div>
          </div>
        ))}
        {data.length === 0 && (
          <div className="col-span-full bg-ink2 p-6 text-sm text-parchmentDim">
            Chưa có dữ liệu vĩ mô — chạy collector hoặc kiểm tra FRED_API_KEY.
          </div>
        )}
      </div>
    </section>
  );
}
