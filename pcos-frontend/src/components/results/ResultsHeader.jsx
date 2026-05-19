export default function ResultsHeader({ diagnostic_status, ml_probability }) {
  const isPositive = diagnostic_status?.includes("POSITIVE");
  const pct = ((ml_probability ?? 0) * 100).toFixed(1);
  const circumference = 2 * Math.PI * 54;
  const offset = circumference - (ml_probability ?? 0) * circumference;

  const statusLabel = isPositive ? "PCOS POSITIVE" : "PCOS NEGATIVE";

  return (
    <header className="glass-card mb-8 rounded-3xl p-8">
      <div className="flex flex-col items-center gap-8 lg:flex-row lg:justify-between">
        <div className="flex items-center justify-center">
          <span
            className={`rounded-2xl px-6 py-3 font-display text-2xl font-bold tracking-wide text-white shadow-lg ${
              isPositive ? "bg-burgundy" : "bg-emerald-700"
            }`}
          >
            {statusLabel}
          </span>
        </div>

        <div className="flex items-center gap-8">
          <div className="relative h-32 w-32">
            <svg className="h-32 w-32 -rotate-90" viewBox="0 0 120 120">
              <circle cx="60" cy="60" r="54" fill="none" stroke="#d8c4ac" strokeWidth="8" />
              <circle
                cx="60"
                cy="60"
                r="54"
                fill="none"
                stroke="#4d0e13"
                strokeWidth="8"
                strokeLinecap="round"
                strokeDasharray={circumference}
                strokeDashoffset={offset}
                className="transition-all duration-700"
              />
            </svg>
            <div className="absolute inset-0 flex flex-col items-center justify-center">
              <span className="font-display text-3xl font-bold text-burgundy">{pct}%</span>
              <span className="text-xs text-text-light">ML Probability</span>
            </div>
          </div>
        </div>
      </div>
    </header>
  );
}
