#!/usr/bin/env python3
"""
Module 02: Runnable LangGraph Cyclic State Machine with Self-Correction
Demonstrates:
1. TypedDict State definition
2. Deterministic Node implementations
3. Adversarial Critic Node with Groundedness calculation
4. Conditional Edges enabling a cyclic self-correction loop
5. Circuit breaker pattern preventing infinite cycles
"""

import sys
from typing import TypedDict, List, Dict, Any, Optional
from langgraph.graph import StateGraph, START, END

# ==============================================================================
# 1. State Definition
# ==============================================================================

class FinancialState(TypedDict):
    doc_id: str
    raw_filing_text: str
    extracted_metrics: List[Dict[str, Any]]
    groundedness_score: float
    flagged_hallucinations: List[str]
    refinement_count: int
    executive_memo: Optional[str]
    status: str

# ==============================================================================
# 2. Node Implementations
# ==============================================================================

def ingestion_node(state: FinancialState) -> Dict[str, Any]:
    """Simulates initial metric extraction (may contain noisy/hallucinated claims)."""
    print(f"\n[IngestionNode] Processing document: {state['doc_id']}")
    
    # Simulate extraction containing 1 true metric and 1 synthetic hallucination
    metrics = [
        {
            "name": "Total Revenue",
            "value": "$391,035 million",
            "source_span": "Total net sales were $391,035 million",
            "grounded": False
        },
        {
            "name": "Adjusted EBITDA",
            "value": "$180,000 million",
            "source_span": "Fabricated text not present in filing",
            "grounded": False
        }
    ]
    return {
        "extracted_metrics": metrics,
        "status": "extracted"
    }

def critic_guardrail_node(state: FinancialState) -> Dict[str, Any]:
    """
    Adversarial Critic: Audits each extracted metric against raw_filing_text.
    Calculates exact groundedness ratio:
    Groundedness = (Number of metrics where source_span is in raw_text) / (Total metrics)
    """
    print(f"[CriticGuardrailNode] Auditing {len(state['extracted_metrics'])} claims against source text...")
    
    raw = state["raw_filing_text"]
    grounded_count = 0
    flagged = []
    audited_metrics = []

    for m in state["extracted_metrics"]:
        span = m.get("source_span", "")
        # Verbatim substring check against raw filing
        if span in raw and len(span) > 5:
            m["grounded"] = True
            grounded_count += 1
        else:
            m["grounded"] = False
            flagged.append(f"{m['name']} ({m['value']}): Span not found in filing")
        audited_metrics.append(m)

    score = grounded_count / len(audited_metrics) if audited_metrics else 0.0
    print(f"    Audited Score: {score:.1%} | Flagged Claims: {len(flagged)}")

    return {
        "extracted_metrics": audited_metrics,
        "groundedness_score": score,
        "flagged_hallucinations": flagged,
        "status": "audited"
    }

def refinement_node(state: FinancialState) -> Dict[str, Any]:
    """
    Self-Correction Loop: Purges ungrounded hallucinated claims and increments refinement_count.
    """
    attempt = state.get("refinement_count", 0) + 1
    print(f"[RefinementNode] Executing cyclic self-healing (Attempt #{attempt})...")
    print(f"    Purging hallucinated claims: {state['flagged_hallucinations']}")

    # Keep only verified metrics or re-extract
    sanitized_metrics = [m for m in state["extracted_metrics"] if m.get("grounded", False)]

    # Add a fallback verified metric to demonstrate recovery
    sanitized_metrics.append({
        "name": "Net Income",
        "value": "$93,736 million",
        "source_span": "Net income was $93,736 million",
        "grounded": True
    })

    return {
        "extracted_metrics": sanitized_metrics,
        "refinement_count": attempt,
        "flagged_hallucinations": [],
        "status": "refined"
    }

def synthesis_node(state: FinancialState) -> Dict[str, Any]:
    """Compiles institutional executive memo from verified metrics only."""
    print(f"[SynthesisNode] Compiling institutional briefing from verified metrics...")
    
    verified_lines = [f"- {m['name']}: {m['value']} (Verified in filing)" for m in state["extracted_metrics"]]
    memo = (
        f"INSTITUTIONAL RISK ASSESSMENT // DOC: {state['doc_id']}\n"
        f"Groundedness Pass Rate: {state['groundedness_score']:.1%}\n"
        f"Refinement Iterations: {state['refinement_count']}\n"
        f"Audited Metrics:\n" + "\n".join(verified_lines)
    )
    return {
        "executive_memo": memo,
        "status": "completed"
    }

# ==============================================================================
# 3. Dynamic Routing Function (Conditional Edge)
# ==============================================================================

def route_critic_decision(state: FinancialState) -> str:
    """
    Routes dynamically:
    - If groundedness >= 95% -> proceed to synthesis
    - If ungrounded AND refinement_count < 2 -> loop to refinement
    - Otherwise -> circuit breaker fallback to synthesis
    """
    if state["groundedness_score"] >= 0.95:
        print("    -> Decision: Groundedness SLA satisfied (>=95%). Routing to synthesis.")
        return "synthesis"
    
    if state.get("refinement_count", 0) >= 2:
        print("    -> Decision: Max refinement limit reached. Circuit-breaker routed to synthesis.")
        return "synthesis"
    
    print("    -> Decision: Hallucination detected! Routing BACK to refinement node.")
    return "refine"

# ==============================================================================
# 4. LangGraph Graph Assembly & Compilation
# ==============================================================================

def build_financial_graph():
    builder = StateGraph(FinancialState)

    # Add Nodes
    builder.add_node("ingestion", ingestion_node)
    builder.add_node("critic", critic_guardrail_node)
    builder.add_node("refine", refinement_node)
    builder.add_node("synthesis", synthesis_node)

    # Add Edges
    builder.add_edge(START, "ingestion")
    builder.add_edge("ingestion", "critic")

    # Conditional Routing from Critic
    builder.add_conditional_edges(
        "critic",
        route_critic_decision,
        {
            "synthesis": "synthesis",
            "refine": "refine"
        }
    )

    # Cyclic edge: Refinement routes BACK to Critic
    builder.add_edge("refine", "critic")

    # Final edge
    builder.add_edge("synthesis", END)

    return builder.compile()

# ==============================================================================
# 5. Execution Test
# ==============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("🚀 Running LangGraph Cyclic State Machine Execution")
    print("=" * 70)

    # Raw filing containing true sales and income, but NOT the hallucinated EBITDA
    sample_filing = """
    UNITED STATES SECURITIES AND EXCHANGE COMMISSION
    FORM 10-K // ANNUAL REPORT
    Total net sales were $391,035 million for fiscal year 2024.
    Net income was $93,736 million compared to $96,995 million in 2023.
    Operating cash flow reached $118,254 million.
    """

    initial_state: FinancialState = {
        "doc_id": "SEC-10K-AAPL-2024",
        "raw_filing_text": sample_filing,
        "extracted_metrics": [],
        "groundedness_score": 0.0,
        "flagged_hallucinations": [],
        "refinement_count": 0,
        "executive_memo": None,
        "status": "initialized"
    }

    graph = build_financial_graph()
    final_output = graph.invoke(initial_state)

    print("\n" + "=" * 70)
    print("📄 FINAL COMPILED EXECUTIVE MEMORANDUM:")
    print("=" * 70)
    print(final_output["executive_memo"])
    print("=" * 70)
    print(f"Final Status: {final_output['status']} | Refinements: {final_output['refinement_count']}")
    print("✨ LangGraph cyclic self-correction successfully demonstrated!")
