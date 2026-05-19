import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useResults } from "../context/ResultsContext";
import ResultsHeader from "../components/results/ResultsHeader";
import SummaryCards from "../components/results/SummaryCards";
import PathwayFlowchart from "../components/results/PathwayFlowchart";
import ProteinViewer from "../components/results/ProteinViewer";

function pickDefaultNode(pathway_graph) {
  const g = pathway_graph ?? {};
  return g.main_disease_node || g.commander_tf || g.soldier_nodes?.[0] || null;
}

export default function ResultsPage() {
  const navigate = useNavigate();
  const { results, clearResults } = useResults();
  const [selectedNode, setSelectedNode] = useState(null);

  useEffect(() => {
    if (!results) {
      navigate("/", { replace: true });
      return;
    }
    setSelectedNode(pickDefaultNode(results.pathway_graph));
  }, [results, navigate]);

  if (!results) return null;

  const handleNewAnalysis = () => {
    clearResults();
    navigate("/");
  };

  return (
    <div className="gradient-page min-h-screen">
      <div className="mx-auto max-w-7xl px-4 py-10 sm:px-6 lg:px-8">
        <div className="mb-6 flex items-center justify-between">
          <h1 className="font-display text-3xl font-bold text-burgundy">Diagnostic Results</h1>
          <button
            type="button"
            onClick={handleNewAnalysis}
            className="rounded-xl border-2 border-burgundy bg-transparent px-5 py-2.5 text-sm font-semibold text-burgundy transition-all hover:bg-burgundy hover:text-white"
          >
            New Analysis
          </button>
        </div>

        <ResultsHeader
          diagnostic_status={results.diagnostic_status}
          ml_probability={results.ml_probability}
        />

        <SummaryCards ai_clinical_summary={results.ai_clinical_summary} />

        <PathwayFlowchart
          pathway_graph={results.pathway_graph}
          selectedNode={selectedNode}
          onSelectNode={setSelectedNode}
        />

        <ProteinViewer selectedNode={selectedNode} />
      </div>
    </div>
  );
}
