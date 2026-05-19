"""
Agent 1: The Explainer
======================
Fast, no-tools agent. Router calls this when the patient's blood test proteins
all map cleanly to entries in the pre-computed knowledge base (final_look_up.json).

This agent runs ALONE — it produces the complete final response that goes to
the frontend. Agent 2 (Explorer) is the alternative path; they never run together.

Public surface (imported by main.py):
    - AgentState                    : TypedDict, shared state schema
    - run_explainer(state)          : entrypoint; returns the final response dict
"""

import os
import json
from typing import TypedDict, List, Optional

from langgraph.graph import StateGraph, END
from groq import Groq


# ---------------------------------------------------------------------------
# Shared state schema (router fills inputs, this agent reads them)
# ---------------------------------------------------------------------------
class AgentState(TypedDict, total=False):
    # Inputs
    blood_proteins: List[str]
    ml_proba: float

    # Router fills
    matched_genes: List[dict]
    unmatched_proteins: List[str]
    route: str

    # Agent fills its own final response dict here
    final_response: dict


# ---------------------------------------------------------------------------
# Groq client (lazy init)
# ---------------------------------------------------------------------------
_GROQ_CLIENT: Optional[Groq] = None
GROQ_MODEL = "llama-3.3-70b-versatile"


def _get_groq_client() -> Groq:
    global _GROQ_CLIENT
    if _GROQ_CLIENT is None:
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise RuntimeError("GROQ_API_KEY env var not set")
        _GROQ_CLIENT = Groq(api_key=api_key)
    return _GROQ_CLIENT


# ---------------------------------------------------------------------------
# Deterministic helpers (pathway graph is built in code, not by the LLM,
# so the structure is reliable and 3D rendering never breaks)
# ---------------------------------------------------------------------------
def _pick_lead_gene(matched_genes: List[dict]) -> dict:
    """Highest-confidence matched gene = the one we anchor the narrative on."""
    tier_rank = {"tier-1": 0, "tier-2": 1, "literature_only": 2}
    return sorted(
        matched_genes,
        key=lambda g: (tier_rank.get(g.get("tier"), 99), -(g.get("proba_m1") or 0.0)),
    )[0]


def _first_pdb(entry: dict) -> Optional[str]:
    pdbs = entry.get("pdb_structures") or []
    return pdbs[0] if pdbs else None


def _build_pathway_graph(lead: dict) -> dict:
    """Frontend reads this to draw the flowchart + load 3D structures."""
    scenario = lead.get("scenario", "unknown")
    main_name = lead["gene_name"]

    main_node = {
        "name": main_name,
        "protein_name": lead.get("protein_name"),
        "role": "Primary disease node",
        "uniprot_id": lead.get("uniprot_id"),
        "pdb_id": _first_pdb(lead),
        "blood_status": "elevated",
    }

    # Commander TF only exists in Scenario A
    if scenario == "A" and lead.get("regulating_tf"):
        commander_tf = {
            "name": lead["regulating_tf"],
            "role": "Master Transcription Factor",
            "uniprot_id": None,     # not stored in JSON for TFs
            "pdb_id": None,
        }
    else:
        commander_tf = None
        if scenario == "B":
            main_node["role"] = "TF + primary disease node"

    soldier_nodes = [
        {
            "name": s["gene_name"],
            "protein_name": s.get("protein_name"),
            "role": "Downstream activation marker",
            "uniprot_id": s.get("uniprot_id"),
            "pdb_id": _first_pdb(s),
            "blood_status": "elevated",
        }
        for s in lead.get("soldier_genes", [])
    ]

    # Edges: A = TF activates everything; B = main gene activates soldiers
    edges = []
    if commander_tf:
        edges.append({"from": commander_tf["name"], "to": main_name, "type": "activates"})
        for s in soldier_nodes:
            edges.append({"from": commander_tf["name"], "to": s["name"], "type": "activates"})
    else:
        for s in soldier_nodes:
            edges.append({"from": main_name, "to": s["name"], "type": "activates"})

    graph = {
        "commander_tf": commander_tf,
        "main_disease_node": main_node,
        "soldier_nodes": soldier_nodes,
        "edges": edges,
    }
    return graph


# ---------------------------------------------------------------------------
# LLM-facing context builder (compact, no JSON dump in the prompt)
# ---------------------------------------------------------------------------
def _summarize_gene_for_llm(g: dict) -> str:
    """One-line factual descriptor of a matched gene for the prompt."""
    parts = [
        f"- {g['gene_name']} ({g.get('protein_name', 'unknown protein')})",
        f"tier={g.get('tier')}",
        f"lfc={g.get('lfc_mean'):.2f}" if g.get("lfc_mean") is not None else "",
        f"scenario={g.get('scenario')}",
    ]
    if g.get("regulating_tf"):
        parts.append(f"regulated_by={g['regulating_tf']}")
    soldier_names = [s["gene_name"] for s in g.get("soldier_genes", [])]
    if soldier_names:
        parts.append(f"soldiers=[{', '.join(soldier_names[:8])}]")
    return " | ".join(p for p in parts if p)


def _build_llm_context(state: AgentState, lead: dict) -> str:
    matched = state.get("matched_genes", [])
    gene_lines = "\n".join(_summarize_gene_for_llm(g) for g in matched)
    return f"""
PATIENT INPUTS:
- Blood test elevated proteins/genes: {state.get('blood_proteins')}
- ML symptom-based PCOS probability: {state.get('ml_proba'):.2f}

LEAD GENE (anchor of the narrative):
- Name: {lead['gene_name']}
- Protein: {lead.get('protein_name')}
- Scenario: {lead.get('scenario')}  (A = shared upstream TF; B = gene's own protein is the TF)
- Regulating TF: {lead.get('regulating_tf')}
- Soldiers (co-regulated genes confirming network activation): \
{[s['gene_name'] for s in lead.get('soldier_genes', [])]}

ALL MATCHED SUS GENES FROM BLOOD TEST:
{gene_lines}
""".strip()


# ---------------------------------------------------------------------------
# LLM system prompt (locks output to the 3-section structure)
# ---------------------------------------------------------------------------
SYSTEM_PROMPT = """You are a factual, evidence-based clinical bioinformatics agent.
You do NOT diagnose patients. You do NOT prescribe. You cross-examine ML outputs
against blood work and ovarian scRNA-seq transcriptomic data, and report findings
in a strictly scientific tone.

You will be given:
1. CLINICAL ML SCORE (phenotypic probability of PCOS)
2. BLOOD WORK signal (which sus genes/proteins are elevated)
3. scRNA-seq REASONING CONTEXT (matched genes from theca cell DE analysis,
   their scenario classification, their regulating TFs, and soldier genes)

RULES:
- Ground every claim in established biochemistry (LH→theca→CYP17A1 androgens,
  insulin→INSR→steroidogenic synergy, GATA6/SREBF axes, activation gap concept).
- The "activation gap" = a main gene may be transcriptionally up but its protein
  may not yet appear elevated in blood; the soldier genes' proteins being
  elevated in blood is what confirms the regulon is active.
- Neutral analytical tone, no patient-facing reassurance, no treatment talk.
- Output STRICT JSON only, no preamble, no markdown fences, no commentary.

Output JSON shape (every field required):
{
  "diagnostic_status": "PCOS_POSITIVE" | "PCOS_NEGATIVE" | "INCONCLUSIVE",
  "matched_scenario": "Scenario_A" | "Scenario_B",
  "ai_clinical_summary": {
    "phenotypic_synthesis": {
      "headline": "<one sentence>",
      "explanation": "<2-3 sentences interpreting the ML score in context>",
      "ml_score_interpretation": "<short label e.g. 'high symptom match'>"
    },
    "endocrine_transcriptomic_alignment": {
      "headline": "<one sentence connecting blood markers to cellular pathway>",
      "explanation": "<2-3 sentences>",
      "mappings": [
        {
          "blood_marker": "<protein/gene name from blood test>",
          "patient_value": "elevated",
          "cellular_pathway": "<short pathway descriptor>",
          "explanation": "<one factual sentence>"
        }
      ],
      "activation_gap_warning": "<sentence if relevant, else empty string>"
    },
    "consensus_conclusion": {
      "headline": "<one sentence>",
      "explanation": "<2-3 sentences>",
      "confidence": "high" | "moderate" | "low"
    }
  }
}
"""


# ---------------------------------------------------------------------------
# LangGraph node: the single LLM call
# ---------------------------------------------------------------------------
def _explainer_node(state: AgentState) -> dict:
    matched = state.get("matched_genes", [])
    if not matched:
        # Defensive: router should never send us an empty match list, but guard anyway
        return {
            "final_response": {
                "diagnostic_status": "INCONCLUSIVE",
                "matched_scenario": "unknown",
                "ml_probability": state.get("ml_proba", 0.0),
                "ai_clinical_summary": {
                    "phenotypic_synthesis": {
                        "headline": "Insufficient molecular evidence in blood panel.",
                        "explanation": "No elevated proteins matched the knowledge base.",
                        "ml_score_interpretation": "n/a",
                    },
                    "endocrine_transcriptomic_alignment": {
                        "headline": "No mappings available.",
                        "explanation": "",
                        "mappings": [],
                        "activation_gap_warning": "",
                    },
                    "consensus_conclusion": {
                        "headline": "Cannot reach a transcriptomic conclusion.",
                        "explanation": "Routing error or empty match set.",
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
        }

    lead = _pick_lead_gene(matched)
    pathway_graph = _build_pathway_graph(lead)
    llm_context = _build_llm_context(state, lead)

    client = _get_groq_client()
    completion = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": llm_context},
        ],
        temperature=0.2,
        response_format={"type": "json_object"},
    )
    llm_json = json.loads(completion.choices[0].message.content)

    # Merge: LLM gives the narrative, we attach the deterministic pathway_graph
    # and the raw ML probability (so the LLM can't hallucinate that number).
    final_response = {
        "diagnostic_status": llm_json.get("diagnostic_status", "INCONCLUSIVE"),
        "matched_scenario": llm_json.get("matched_scenario", f"Scenario_{lead.get('scenario', 'unknown')}"),
        "ml_probability": state.get("ml_proba", 0.0),
        "ai_clinical_summary": llm_json.get("ai_clinical_summary", {}),
        "pathway_graph": pathway_graph,
    }
    return {"final_response": final_response}


# ---------------------------------------------------------------------------
# Build the graph once at module load
# ---------------------------------------------------------------------------
def _build_graph():
    g = StateGraph(AgentState)
    g.add_node("explainer", _explainer_node)
    g.set_entry_point("explainer")
    g.add_edge("explainer", END)
    return g.compile()


_EXPLAINER_GRAPH = _build_graph()


# ---------------------------------------------------------------------------
# Public entrypoint (this is what main.py imports)
# ---------------------------------------------------------------------------
def run_explainer(state: AgentState) -> dict:
    """
    Called by main.py when the router has decided this is the Explainer path.
    Returns the complete final response dict ready to send to the frontend.
    """
    result_state = _EXPLAINER_GRAPH.invoke(state)
    return result_state["final_response"]
