export default function LoadingOverlay({ message = "Analyzing patient data…" }) {
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-burgundy/40 backdrop-blur-sm">
      <div className="glass-card flex flex-col items-center gap-5 rounded-3xl px-12 py-10">
        <div className="h-14 w-14 animate-spin rounded-full border-4 border-sand border-t-burgundy" />
        <p className="font-display text-xl font-semibold text-burgundy">{message}</p>
        <p className="text-sm text-text-light">Running ML model & AI clinical synthesis</p>
      </div>
    </div>
  );
}
