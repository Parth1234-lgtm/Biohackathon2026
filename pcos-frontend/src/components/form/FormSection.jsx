import { useState } from "react";

export default function FormSection({ title, icon, defaultOpen = true, children }) {
  const [open, setOpen] = useState(defaultOpen);

  return (
    <section className="glass-card overflow-hidden rounded-2xl transition-shadow hover:shadow-lg">
      <button
        type="button"
        onClick={() => setOpen(!open)}
        className="flex w-full items-center justify-between gap-4 px-6 py-5 text-left transition-colors hover:bg-white/40"
      >
        <div className="flex items-center gap-3">
          <span className="flex h-10 w-10 items-center justify-center rounded-xl bg-burgundy/10 text-lg">
            {icon}
          </span>
          <h2 className="font-display text-xl font-semibold text-burgundy">{title}</h2>
        </div>
        <span
          className={`text-burgundy transition-transform duration-300 ${open ? "rotate-180" : ""}`}
        >
          ▾
        </span>
      </button>
      <div
        className={`grid transition-all duration-300 ease-in-out ${
          open ? "grid-rows-[1fr] opacity-100" : "grid-rows-[0fr] opacity-0"
        }`}
      >
        <div className="overflow-hidden">
          <div className="grid gap-4 border-t border-sand/50 px-6 pb-6 pt-4 sm:grid-cols-2 lg:grid-cols-3">
            {children}
          </div>
        </div>
      </div>
    </section>
  );
}
