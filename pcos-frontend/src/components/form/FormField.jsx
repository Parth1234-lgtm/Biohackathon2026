export function FormField({ label, name, type = "number", value, onChange, step, min, max, children }) {
  if (children) {
    return (
      <label className="flex flex-col gap-1.5">
        <span className="text-sm font-medium text-text-dark">{label}</span>
        {children}
      </label>
    );
  }

  return (
    <label className="flex flex-col gap-1.5">
      <span className="text-sm font-medium text-text-dark">{label}</span>
      <input
        type={type}
        name={name}
        value={value}
        onChange={onChange}
        step={step}
        min={min}
        max={max}
        required
        className="rounded-xl border border-sand/80 bg-white/90 px-3.5 py-2.5 text-sm transition-all focus:border-burgundy focus:outline-none focus:ring-2 focus:ring-burgundy/20"
      />
    </label>
  );
}

export function YesNoSelect({ label, name, value, onChange }) {
  return (
    <FormField label={label} name={name}>
      <select
        name={name}
        value={value}
        onChange={onChange}
        required
        className="rounded-xl border border-sand/80 bg-white/90 px-3.5 py-2.5 text-sm transition-all focus:border-burgundy focus:outline-none focus:ring-2 focus:ring-burgundy/20"
      >
        <option value="">Select…</option>
        <option value="0">No</option>
        <option value="1">Yes</option>
      </select>
    </FormField>
  );
}
