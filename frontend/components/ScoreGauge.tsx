"use client";

export default function ScoreGauge({
  label,
  value,
  tone,
}: {
  label: string;
  value: number;
  tone: "gold" | "down";
}) {
  const color = tone === "gold" ? "var(--gold)" : "var(--down)";
  const circumference = 2 * Math.PI * 34;
  const offset = circumference - (value / 100) * circumference;

  return (
    <div className="flex flex-col items-center gap-2">
      <div className="relative h-24 w-24">
        <svg viewBox="0 0 80 80" className="h-24 w-24 -rotate-90">
          <circle cx="40" cy="40" r="34" fill="none" stroke="#1a2739" strokeWidth="6" />
          <circle
            cx="40"
            cy="40"
            r="34"
            fill="none"
            stroke={color}
            strokeWidth="6"
            strokeDasharray={circumference}
            strokeDashoffset={offset}
            strokeLinecap="round"
          />
        </svg>
        <div className="absolute inset-0 flex items-center justify-center font-mono text-xl text-parchment">
          {value}
        </div>
      </div>
      <span className="text-xs uppercase tracking-wider text-parchmentDim">{label}</span>
    </div>
  );
}
