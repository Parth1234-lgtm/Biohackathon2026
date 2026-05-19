from pathlib import Path
import json
from typing import Dict, List, Tuple, Optional

from dotenv import load_dotenv
load_dotenv()  # must come before importing the agent (in case it inits Groq eagerly later)

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from schemas import RequestSchema,ResponseSchema
from models.run_model import run_model
from agents.explainer_agent import run_explainer, AgentState
from fastapi.middleware.cors import CORSMiddleware




# ---------------------------------------------------------------------------
# Load knowledge base + build reverse lookup ONCE at startup
# ---------------------------------------------------------------------------
_JSON_PATH = Path(__file__).parent / "final_look_up.json"

with open(_JSON_PATH, "r") as f:
    KNOWLEDGE_BASE: Dict[str, dict] = json.load(f)


def _build_protein_lookup() -> Dict[str, Tuple[str, str]]:
    """
    Flatten the knowledge base into a single dict:
        name (lowercased) -> (parent_gene_key, "main" | "soldier")

    "main"    = the name belongs to a top-level sus gene (or one of its aliases)
    "soldier" = the name belongs to a soldier gene under some parent

    For soldier matches we store the PARENT gene key so the Explainer always
    receives the parent context (activation gap story needs it).
    """
    lookup: Dict[str, Tuple[str, str]] = {}

    def _add(name: Optional[str], parent_gene: str, kind: str):
        if not name:
            return
        key = name.lower().strip()
        if key and key not in lookup:
            lookup[key] = (parent_gene, kind)

    for gene_key, entry in KNOWLEDGE_BASE.items():
        # Main gene: gene_name, protein_name, alternative_names
        _add(gene_key, gene_key, "main")
        _add(entry.get("gene_name"), gene_key, "main")
        _add(entry.get("protein_name"), gene_key, "main")
        for alt in entry.get("alternative_names", []) or []:
            _add(alt, gene_key, "main")

        # Soldier genes: each points back to its PARENT gene
        for soldier in entry.get("soldier_genes", []) or []:
            _add(soldier.get("gene_name"), gene_key, "soldier")
            _add(soldier.get("protein_name"), gene_key, "soldier")
            for alt in soldier.get("alternative_names", []) or []:
                _add(alt, gene_key, "soldier")

    return lookup


PROTEIN_LOOKUP: Dict[str, Tuple[str, str]] = _build_protein_lookup()


# ---------------------------------------------------------------------------
# Routing logic
# ---------------------------------------------------------------------------
def route_blood_proteins(
    blood_proteins: List[str],
) -> Tuple[str, List[dict], List[str]]:
    """
    Three-stage routing:
      Stage 1: any MAIN gene protein matches            -> "explainer"
      Stage 2: no main match, but a SOLDIER matches     -> "explainer" (activation-gap path)
      Stage 3: nothing matches                          -> "explorer"

    Returns:
      route             : "explainer" or "explorer"
      matched_genes     : full KB entries for every PARENT gene that was hit
                          (either directly via main, or indirectly via soldier).
                          Each entry gets an extra "_match_type" field so the
                          agent can shape its narrative around the activation gap.
      unmatched_proteins: blood proteins that didn't map to anything in the KB
    """
    main_hits: set = set()
    soldier_hits: set = set()
    unmatched: List[str] = []

    for protein in blood_proteins:
        key = protein.lower().strip()
        if key in PROTEIN_LOOKUP:
            parent_gene, kind = PROTEIN_LOOKUP[key]
            if kind == "main":
                main_hits.add(parent_gene)
            else:
                soldier_hits.add(parent_gene)
        else:
            unmatched.append(protein)

    matched_genes: List[dict] = []

    if main_hits:
        # Stage 1: main hits drive the story. Soldier-only parents tag along
        # so the agent has full pathway context.
        for gene in main_hits:
            entry = dict(KNOWLEDGE_BASE[gene])
            entry["_match_type"] = "main"
            matched_genes.append(entry)
        for gene in soldier_hits - main_hits:
            entry = dict(KNOWLEDGE_BASE[gene])
            entry["_match_type"] = "soldier_only"
            matched_genes.append(entry)
        return "explainer", matched_genes, unmatched

    if soldier_hits:
        # Stage 2: activation gap path — only soldiers matched, but we still
        # know the parent gene network and can tell the story.
        for gene in soldier_hits:
            entry = dict(KNOWLEDGE_BASE[gene])
            entry["_match_type"] = "soldier_only"
            matched_genes.append(entry)
        return "explainer", matched_genes, unmatched

    # Stage 3: nothing in the KB — needs the Explorer.
    return "explorer", [], unmatched


# ---------------------------------------------------------------------------
# Placeholder for Agent 2 (you'll replace this when you build it)
# ---------------------------------------------------------------------------
def run_explorer(state: AgentState) -> dict:
    return {
        "diagnostic_status": "INCONCLUSIVE",
        "matched_scenario": "unknown",
        "ml_probability": state.get("ml_proba", 0.0),
        "ai_clinical_summary": {
            "phenotypic_synthesis": {
                "headline": "Explorer agent not yet implemented.",
                "explanation": "Anomaly path will perform live research on unknown proteins.",
                "ml_score_interpretation": "n/a",
            },
            "endocrine_transcriptomic_alignment": {
                "headline": "Pending Agent 2 implementation.",
                "explanation": "",
                "mappings": [],
                "activation_gap_warning": "",
            },
            "consensus_conclusion": {
                "headline": "Routed to Explorer (no KB match).",
                "explanation": f"Unmatched proteins: {state.get('unmatched_proteins')}",
                "confidence": "low",
            },
        },
        "pathway_graph": {
            "commander_tf": None,
            "main_disease_node": None,
            "soldier_nodes": [],
            "edges": [],
        },
    }


# ---------------------------------------------------------------------------
# FastAPI app
# ---------------------------------------------------------------------------
app = FastAPI(title="PCOS Bio Diagnostic Backend")

# Add this right after app creation
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # for demo; tighten for production
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/submit", response_model=ResponseSchema)
def analysis(payload: RequestSchema):
    # Step 1: ML model on phenotypic features
    ml_feature = payload.ml_features.model_dump(by_alias=True)
    proba_score = float(run_model(ml_feature))

    # Step 2: route blood proteins through the knowledge base
    blood_proteins = payload.blood_report.high_protein
    if not blood_proteins:
        raise HTTPException(status_code=400, detail="blood_report.high_protein is empty")

    route, matched_genes, unmatched_proteins = route_blood_proteins(blood_proteins)

    # Step 3: build shared agent state
    state: AgentState = {
        "blood_proteins": blood_proteins,
        "ml_proba": proba_score,
        "matched_genes": matched_genes,
        "unmatched_proteins": unmatched_proteins,
        "route": route,
    }

    # Step 4: dispatch to exactly one agent
    if route == "explainer":
        final_response = run_explainer(state)
    else:
        final_response = run_explorer(state)

    return final_response