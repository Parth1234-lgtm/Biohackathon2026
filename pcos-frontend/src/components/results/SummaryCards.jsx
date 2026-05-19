function ConfidenceBadge({ confidence }) {
  const c = (confidence || "").toLowerCase();
  const styles =
    c === "high"
      ? "bg-emerald-100 text-emerald-800 border-emerald-200"
      : c === "moderate"
        ? "bg-amber-100 text-amber-800 border-amber-200"
        : "bg-red-100 text-red-800 border-red-200";
  const label =
    c === "high" ? "High Confidence" : c === "moderate" ? "Moderate Confidence" : "Low Confidence";

  return (
    <span className={`inline-block rounded-full border px-3 py-1 text-xs font-semibold ${styles}`}>
      {label}
    </span>
  );
}

export default function SummaryCards({ ai_clinical_summary }) {
  const pheno = ai_clinical_summary?.phenotypic_synthesis ?? {};
  const endo = ai_clinical_summary?.endocrine_transcriptomic_alignment ?? {};
  const consensus = ai_clinical_summary?.consensus_conclusion ?? {};

  return (
    <div className="mb-8 grid gap-6 lg:grid-cols-3">
      <article className="glass-card flex flex-col rounded-2xl p-6 transition-all duration-300 hover:-translate-y-1 hover:shadow-xl">
        <h3 className="mb-4 font-display text-lg font-semibold text-burgundy">Phenotypic Analysis</h3>
        <p className="mb-3 font-semibold text-text-dark">{pheno.headline}</p>
        <p className="mb-4 flex-1 text-sm leading-relaxed text-text-light">{pheno.explanation}</p>
        {pheno.ml_score_interpretation && (
          <span className="self-start rounded-full bg-dusty-pink/30 px-3 py-1 text-xs font-medium text-burgundy">
            {pheno.ml_score_interpretation}
          </span>
        )}
      </article>

      <article className="glass-card flex flex-col rounded-2xl p-6 transition-all duration-300 hover:-translate-y-1 hover:shadow-xl">
        <h3 className="mb-4 font-display text-lg font-semibold text-burgundy">
          Molecular Pathway Analysis
        </h3>
        <p className="mb-3 font-semibold text-text-dark">{endo.headline}</p>
        <p className="mb-4 text-sm leading-relaxed text-text-light">{endo.explanation}</p>
        <div className="mb-4 space-y-3">
          {(endo.mappings ?? []).map((m) => (
            <div
              key={m.blood_marker}
              className="rounded-xl border border-sand/60 bg-white/60 p-3 text-sm"
            >
              <p className="font-bold text-burgundy">{m.blood_marker}</p>
              <p className="text-text-light">
                {m.cellular_pathway} → <span className="font-medium text-text-dark">{m.patient_value}</span>
              </p>
              <p className="mt-1 text-text-light">{m.explanation}</p>
            </div>
          ))}
        </div>
        {endo.activation_gap_warning && endo.activation_gap_warning.trim() !== "" && (
          <div
            className="activation-gap-warning mt-2 rounded-2xl border-2 border-amber-400 bg-gradient-to-br from-amber-50 via-amber-100/90 to-orange-50 p-5 shadow-md"
            role="alert"
          >
            <div className="flex gap-4">
              <div className="flex h-14 w-14 shrink-0 items-center justify-center rounded-xl bg-amber-500/20 text-amber-700">
                <svg
                  className="h-9 w-9"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="2"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  aria-hidden
                >
                  <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z" />
                  <line x1="12" y1="9" x2="12" y2="13" />
                  <line x1="12" y1="17" x2="12.01" y2="17" />
                </svg>
              </div>
              <div className="min-w-0 flex-1">
                <p className="mb-1.5 font-display text-base font-bold tracking-wide text-amber-900">
                  Activation Gap Insight
                </p>
                <p className="text-[0.95rem] leading-relaxed text-amber-950/90">
                  {endo.activation_gap_warning}
                </p>
              </div>
            </div>
          </div>
        )}
      </article>

      <article className="glass-card flex flex-col rounded-2xl p-6 transition-all duration-300 hover:-translate-y-1 hover:shadow-xl">
        <h3 className="mb-4 font-display text-lg font-semibold text-burgundy">Clinical Consensus</h3>
        <p className="mb-3 font-semibold text-text-dark">{consensus.headline}</p>
        <p className="mb-4 flex-1 text-sm leading-relaxed text-text-light">{consensus.explanation}</p>
        <ConfidenceBadge confidence={consensus.confidence} />
      </article>
    </div>
  );
}
