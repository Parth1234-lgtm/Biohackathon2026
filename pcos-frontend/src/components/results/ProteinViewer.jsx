import { useEffect, useRef, useState } from "react";

async function fetchStructure(node) {
  const pdbId = node?.pdb_id;
  const uniprotId = node?.uniprot_id;

  if (pdbId) {
    const url = `https://files.rcsb.org/download/${pdbId}.pdb`;
    const res = await fetch(url);
    if (!res.ok) throw new Error(`Failed to fetch PDB ${pdbId}`);
    const data = await res.text();
    return { data, source: `RCSB PDB (${pdbId})` };
  }

  if (uniprotId) {
    const url = `https://alphafold.ebi.ac.uk/files/AF-${uniprotId}-F1-model_v4.pdb`;
    const res = await fetch(url);
    if (!res.ok) throw new Error(`Failed to fetch AlphaFold structure for ${uniprotId}`);
    const data = await res.text();
    return { data, source: `AlphaFold (${uniprotId})` };
  }

  return null;
}

export default function ProteinViewer({ selectedNode }) {
  const containerRef = useRef(null);
  const viewerRef = useRef(null);
  const [status, setStatus] = useState({ type: "idle", message: "" });
  const [loadSource, setLoadSource] = useState("");

  useEffect(() => {
    if (!containerRef.current || !window.$3Dmol) return;

    if (!viewerRef.current) {
      viewerRef.current = window.$3Dmol.createViewer(containerRef.current, {
        backgroundColor: "black",
      });
    }

    return () => {
      viewerRef.current = null;
    };
  }, []);

  useEffect(() => {
    const viewer = viewerRef.current;
    if (!viewer || !selectedNode) return;

    let cancelled = false;

    async function load() {
      setStatus({ type: "loading", message: "Loading structure…" });
      setLoadSource("");

      viewer.clear();
      viewer.render();

      const result = await fetchStructure(selectedNode);

      if (cancelled) return;

      if (!result) {
        setStatus({
          type: "unavailable",
          message: "No structure available for this protein.",
        });
        return;
      }

      try {
        viewer.addModel(result.data, "pdb");
        viewer.setStyle({}, { cartoon: { color: "spectrum" } });
        viewer.zoomTo();
        viewer.render();
        setLoadSource(result.source);
        setStatus({ type: "success", message: "Structure loaded successfully." });
      } catch (err) {
        setStatus({ type: "error", message: err.message || "Failed to render structure." });
      }
    }

    load();

    return () => {
      cancelled = true;
    };
  }, [selectedNode]);

  const displayName =
    selectedNode?.protein_name || selectedNode?.name || "Select a pathway node";

  return (
    <section className="glass-card rounded-2xl p-6">
      <h3 className="mb-4 font-display text-xl font-semibold text-burgundy">
        3D Protein Structure
      </h3>

      <div className="mb-4 rounded-xl border border-sand/60 bg-white/70 p-4 text-sm">
        <p className="font-semibold text-text-dark">{displayName}</p>
        <div className="mt-2 grid gap-1 text-text-light sm:grid-cols-3">
          <span>UniProt: {selectedNode?.uniprot_id || "—"}</span>
          <span>PDB: {selectedNode?.pdb_id || "—"}</span>
          <span>Source: {loadSource || "—"}</span>
        </div>
        {status.message && (
          <p
            className={`mt-2 text-xs font-medium ${
              status.type === "success"
                ? "text-emerald-700"
                : status.type === "error" || status.type === "unavailable"
                  ? "text-amber-700"
                  : "text-text-light"
            }`}
          >
            {status.message}
          </p>
        )}
      </div>

      <div
        ref={containerRef}
        className="relative h-[600px] w-full overflow-hidden rounded-xl border border-burgundy/20 bg-black"
        style={{ position: "relative", width: "100%", height: 600 }}
      />
    </section>
  );
}
