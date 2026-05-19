import { useState } from "react";
import { useNavigate } from "react-router-dom";
import FormSection from "../components/form/FormSection";
import { FormField, YesNoSelect } from "../components/form/FormField";
import LoadingOverlay from "../components/LoadingOverlay";
import { submitDiagnosis } from "../api/submit";
import { useResults } from "../context/ResultsContext";
import { DEMO_1, DEMO_2, EMPTY_ML_FEATURES } from "../data/demoData";

function parseMlFeatures(features) {
  const parsed = {};
  for (const [key, val] of Object.entries(features)) {
    if (val === "" || val === null || val === undefined) continue;
    const num = Number(val);
    parsed[key] = Number.isNaN(num) ? val : num;
  }
  return parsed;
}

export default function FormPage() {
  const navigate = useNavigate();
  const { setResults } = useResults();
  const [mlFeatures, setMlFeatures] = useState({ ...EMPTY_ML_FEATURES });
  const [bloodInput, setBloodInput] = useState("");
  const [bloodTags, setBloodTags] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleFieldChange = (key) => (e) => {
    setMlFeatures((prev) => ({ ...prev, [key]: e.target.value }));
  };

  const applyDemo = (demo) => {
    setMlFeatures({ ...demo.ml_features });
    setBloodTags(demo.blood_proteins);
    setBloodInput(demo.blood_proteins.join(", "));
    setError(null);
    window.scrollTo({ top: 0, behavior: "smooth" });
  };

  const handleBloodInput = (e) => {
    const text = e.target.value;
    setBloodInput(text);
    const tags = text
      .split(/[,;\s]+/)
      .map((s) => s.trim().toUpperCase())
      .filter(Boolean);
    setBloodTags(tags);
  };

  const removeTag = (tag) => {
    const next = bloodTags.filter((t) => t !== tag);
    setBloodTags(next);
    setBloodInput(next.join(", "));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    const payload = {
      ml_features: parseMlFeatures(mlFeatures),
      blood_report: { high_protein: bloodTags },
    };

    try {
      const data = await submitDiagnosis(payload);
      setResults(data);
      navigate("/results");
    } catch (err) {
      const msg =
        err.response?.data?.detail ||
        err.message ||
        "Failed to connect to backend. Is the server running on port 8000?";
      setError(typeof msg === "string" ? msg : JSON.stringify(msg));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="gradient-page min-h-screen">
      {loading && <LoadingOverlay />}

      <div className="mx-auto max-w-6xl px-4 py-10 sm:px-6 lg:px-8">
        <header className="mb-10 text-center">
          <p className="mb-2 text-sm font-semibold uppercase tracking-widest text-dusty-pink">
            scRNA-seq Powered Diagnostics
          </p>
          <h1 className="font-display text-4xl font-bold text-burgundy sm:text-5xl">
            PCOS Diagnostic Tool
          </h1>
          <p className="mt-3 text-text-light">
            Clinical phenotyping + blood proteomics → AI-assisted pathway analysis
          </p>
        </header>

        <div className="mb-8 grid gap-4 sm:grid-cols-2">
          <button
            type="button"
            onClick={() => applyDemo(DEMO_1)}
            className="group glass-card rounded-2xl p-5 text-left transition-all duration-300 hover:-translate-y-1 hover:scale-[1.02] hover:shadow-xl"
          >
            <span className="mb-1 block text-xs font-bold uppercase tracking-wider text-dusty-pink">
              Demo 1
            </span>
            <span className="font-display text-lg font-semibold text-burgundy">
              Main Gene Match
            </span>
            <p className="mt-1 text-sm text-text-light">
              PCOS-positive phenotype · INSIG1, CYP17A1, AMH
            </p>
          </button>
          <button
            type="button"
            onClick={() => applyDemo(DEMO_2)}
            className="group glass-card rounded-2xl p-5 text-left transition-all duration-300 hover:-translate-y-1 hover:scale-[1.02] hover:shadow-xl"
          >
            <span className="mb-1 block text-xs font-bold uppercase tracking-wider text-dusty-pink">
              Demo 2
            </span>
            <span className="font-display text-lg font-semibold text-burgundy">
              Activation Gap
            </span>
            <p className="mt-1 text-sm text-text-light">
              Same phenotype · soldier genes LDLR, STARD4 only
            </p>
          </button>
        </div>

        {error && (
          <div className="mb-6 rounded-2xl border border-red-300 bg-red-50 px-5 py-4 text-sm text-red-800">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-5">
          <FormSection title="Clinical Features" icon="🩺" defaultOpen>
            <FormField label="Age (years)" name="Age (yrs)" value={mlFeatures["Age (yrs)"]} onChange={handleFieldChange("Age (yrs)")} min={0} max={100} step="1" />
            <FormField label="BMI" name="BMI" value={mlFeatures.BMI} onChange={handleFieldChange("BMI")} step="0.1" min={0} />
            <FormField label="Cycle Length (days)" name="Cycle length(days)" value={mlFeatures["Cycle length(days)"]} onChange={handleFieldChange("Cycle length(days)")} step="1" min={0} />
            <FormField label="Cycle Regular/Irregular" name="Cycle(R/I)">
              <select name="Cycle(R/I)" value={mlFeatures["Cycle(R/I)"]} onChange={handleFieldChange("Cycle(R/I)")} required className="rounded-xl border border-sand/80 bg-white/90 px-3.5 py-2.5 text-sm focus:border-burgundy focus:outline-none focus:ring-2 focus:ring-burgundy/20">
                <option value="">Select…</option>
                <option value="0">Regular</option>
                <option value="1">Irregular</option>
              </select>
            </FormField>
            <YesNoSelect label="Hair Loss" name="Hair loss(Y/N)" value={mlFeatures["Hair loss(Y/N)"]} onChange={handleFieldChange("Hair loss(Y/N)")} />
            <YesNoSelect label="Pimples" name="Pimples(Y/N)" value={mlFeatures["Pimples(Y/N)"]} onChange={handleFieldChange("Pimples(Y/N)")} />
            <YesNoSelect label="Fast Food" name="Fast food (Y/N)" value={mlFeatures["Fast food (Y/N)"]} onChange={handleFieldChange("Fast food (Y/N)")} />
            <YesNoSelect label="Regular Exercise" name="Reg.Exercise(Y/N)" value={mlFeatures["Reg.Exercise(Y/N)"]} onChange={handleFieldChange("Reg.Exercise(Y/N)")} />
            <YesNoSelect label="Weight Gain" name="Weight gain(Y/N)" value={mlFeatures["Weight gain(Y/N)"]} onChange={handleFieldChange("Weight gain(Y/N)")} />
          </FormSection>

          <FormSection title="Medical Measurements" icon="📊" defaultOpen={false}>
            <FormField label="WHR" name="WHR" value={mlFeatures.WHR} onChange={handleFieldChange("WHR")} step="0.01" min={0} />
            <FormField label="MSI" name="MSI">
              <select name="MSI" value={mlFeatures.MSI} onChange={handleFieldChange("MSI")} required className="rounded-xl border border-sand/80 bg-white/90 px-3.5 py-2.5 text-sm focus:border-burgundy focus:outline-none focus:ring-2 focus:ring-burgundy/20">
                <option value="">Select…</option>
                <option value="0">0</option>
                <option value="1">1</option>
              </select>
            </FormField>
            <FormField label="Pulse Rate (bpm)" name="Pulse rate(bpm)" value={mlFeatures["Pulse rate(bpm)"]} onChange={handleFieldChange("Pulse rate(bpm)")} step="1" />
            <FormField label="RR (breaths/min)" name="RR (breaths/min)" value={mlFeatures["RR (breaths/min)"]} onChange={handleFieldChange("RR (breaths/min)")} step="1" />
            <FormField label="Hb (g/dl)" name="Hb(g/dl)" value={mlFeatures["Hb(g/dl)"]} onChange={handleFieldChange("Hb(g/dl)")} step="0.1" />
            <YesNoSelect label="Pregnant" name="Pregnant(Y/N)" value={mlFeatures["Pregnant(Y/N)"]} onChange={handleFieldChange("Pregnant(Y/N)")} />
            <FormField label="No. of Abortions" name="No. of abortions" value={mlFeatures["No. of abortions"]} onChange={handleFieldChange("No. of abortions")} step="1" min={0} />
          </FormSection>

          <FormSection title="Hormone Levels" icon="🧬" defaultOpen={false}>
            <FormField label="FSH (mIU/mL)" name="FSH(mIU/mL)" value={mlFeatures["FSH(mIU/mL)"]} onChange={handleFieldChange("FSH(mIU/mL)")} step="0.1" />
            <FormField label="LH (mIU/mL)" name="LH(mIU/mL)" value={mlFeatures["LH(mIU/mL)"]} onChange={handleFieldChange("LH(mIU/mL)")} step="0.1" />
            <FormField label="TSH (mIU/L)" name="TSH (mIU/L)" value={mlFeatures["TSH (mIU/L)"]} onChange={handleFieldChange("TSH (mIU/L)")} step="0.1" />
            <FormField label="AMH (ng/mL)" name="AMH(ng/mL)" value={mlFeatures["AMH(ng/mL)"]} onChange={handleFieldChange("AMH(ng/mL)")} step="0.1" />
            <FormField label="PRL (ng/mL)" name="PRL(ng/mL)" value={mlFeatures["PRL(ng/mL)"]} onChange={handleFieldChange("PRL(ng/mL)")} step="0.1" />
            <FormField label="Vit D3 (ng/mL)" name="Vit D3 (ng/mL)" value={mlFeatures["Vit D3 (ng/mL)"]} onChange={handleFieldChange("Vit D3 (ng/mL)")} step="0.1" />
            <FormField label="PRG (ng/mL)" name="PRG(ng/mL)" value={mlFeatures["PRG(ng/mL)"]} onChange={handleFieldChange("PRG(ng/mL)")} step="0.1" />
          </FormSection>

          <FormSection title="Ultrasound" icon="🔬" defaultOpen={false}>
            <FormField label="Follicle No. (L)" name="Follicle No. (L)" value={mlFeatures["Follicle No. (L)"]} onChange={handleFieldChange("Follicle No. (L)")} step="1" />
            <FormField label="Follicle No. (R)" name="Follicle No. (R)" value={mlFeatures["Follicle No. (R)"]} onChange={handleFieldChange("Follicle No. (R)")} step="1" />
            <FormField label="Avg. F Size (L) (mm)" name="Avg. F size (L) (mm)" value={mlFeatures["Avg. F size (L) (mm)"]} onChange={handleFieldChange("Avg. F size (L) (mm)")} step="0.1" />
            <FormField label="Avg. F Size (R) (mm)" name="Avg. F size (R) (mm)" value={mlFeatures["Avg. F size (R) (mm)"]} onChange={handleFieldChange("Avg. F size (R) (mm)")} step="0.1" />
            <FormField label="Endometrium (mm)" name="Endometrium (mm)" value={mlFeatures["Endometrium (mm)"]} onChange={handleFieldChange("Endometrium (mm)")} step="0.1" />
            <YesNoSelect label="Skin Darkening" name="Skin darkening (Y/N)" value={mlFeatures["Skin darkening (Y/N)"]} onChange={handleFieldChange("Skin darkening (Y/N)")} />
            <YesNoSelect label="Hair Growth" name="hair growth(Y/N)" value={mlFeatures["hair growth(Y/N)"]} onChange={handleFieldChange("hair growth(Y/N)")} />
          </FormSection>

          <FormSection title="Blood Test — Elevated Proteins" icon="🩸" defaultOpen>
            <div className="col-span-full">
              <label className="flex flex-col gap-2">
                <span className="text-sm font-medium text-text-dark">
                  Comma-separated gene/protein names
                </span>
                <input
                  type="text"
                  value={bloodInput}
                  onChange={handleBloodInput}
                  placeholder="e.g. INSIG1, CYP17A1, AMH"
                  required
                  className="rounded-xl border border-sand/80 bg-white/90 px-4 py-3 text-sm focus:border-burgundy focus:outline-none focus:ring-2 focus:ring-burgundy/20"
                />
              </label>
              {bloodTags.length > 0 && (
                <div className="mt-3 flex flex-wrap gap-2">
                  {bloodTags.map((tag) => (
                    <span
                      key={tag}
                      className="inline-flex items-center gap-1.5 rounded-full bg-burgundy/10 px-3 py-1 text-sm font-medium text-burgundy"
                    >
                      {tag}
                      <button
                        type="button"
                        onClick={() => removeTag(tag)}
                        className="ml-1 text-burgundy/60 hover:text-burgundy"
                        aria-label={`Remove ${tag}`}
                      >
                        ×
                      </button>
                    </span>
                  ))}
                </div>
              )}
            </div>
          </FormSection>

          <div className="flex justify-center pt-4">
            <button
              type="submit"
              disabled={loading || bloodTags.length === 0}
              className="rounded-2xl bg-burgundy px-12 py-4 font-semibold text-white shadow-lg transition-all duration-300 hover:-translate-y-0.5 hover:bg-burgundy/90 hover:shadow-xl disabled:cursor-not-allowed disabled:opacity-50"
            >
              Analyze Patient
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
