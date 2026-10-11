import logging
from typing import Dict, Any, Literal
from langgraph.graph import StateGraph, START, END

from app.models.state import DocumentState
from app.agents.ingestion_agent import ingestion_agent
from app.agents.classification_agent import classification_agent
from app.agents.guardrail_agent import guardrail_agent
from app.agents.synthesis_agent import synthesis_agent
from app.config import settings

logger = logging.getLogger(__name__)

async def node_ingest(state: DocumentState) -> Dict[str, Any]:
    """Node 1: Document Ingestion, Semantic Chunking & Entity/Metric Extraction."""
    logger.info(f"[{state.get('job_id')}] Node 1: Ingestion & Extraction started")
    raw_text = state.get("raw_text", "")
    metadata = state.get("metadata", {})
    inject_trap = state.get("inject_hallucination_trap", False)

    result = await ingestion_agent.run(raw_text, metadata, inject_trap=inject_trap)
    
    current_trace = list(state.get("trace", []))
    current_trace.append(result["trace_event"])

    return {
        "chunks": result["chunks"],
        "entities": result["entities"],
        "financial_metrics": result["financial_metrics"],
        "trace": current_trace,
        "status": "ingested_and_extracted",
        "iterations": 1
    }

async def node_classify(state: DocumentState) -> Dict[str, Any]:
    """Node 2: Document Taxonomy, Sentiment & Multi-Factor Risk Categorization."""
    logger.info(f"[{state.get('job_id')}] Node 2: Classification started")
    raw_text = state.get("raw_text", "")
    entities = state.get("entities", [])
    metrics = state.get("financial_metrics", [])

    result = await classification_agent.run(raw_text, entities, metrics)

    current_trace = list(state.get("trace", []))
    current_trace.append(result["trace_event"])

    return {
        "classification": result["classification"],
        "risk_factors": result["risk_factors"],
        "trace": current_trace,
        "status": "classified"
    }

async def node_guardrails(state: DocumentState) -> Dict[str, Any]:
    """Node 3: Guardrail Verification & Hallucination Elimination."""
    logger.info(f"[{state.get('job_id')}] Node 3: Guardrails Verification started")
    raw_text = state.get("raw_text", "")
    metrics = state.get("financial_metrics", [])
    iteration = state.get("iterations", 1)
    inject_trap = state.get("inject_hallucination_trap", False)

    result = await guardrail_agent.run(raw_text, metrics, iteration=iteration, inject_trap=inject_trap)

    current_trace = list(state.get("trace", []))
    current_trace.append(result["trace_event"])

    return {
        "guardrail_result": result["guardrail_result"],
        "needs_refinement": result["needs_refinement"],
        "trace": current_trace,
        "status": "verified"
    }

async def node_refine(state: DocumentState) -> Dict[str, Any]:
    """Node 4: LangGraph Self-Correction Cycle - Purges hallucinated/flagged metrics."""
    logger.info(f"[{state.get('job_id')}] Node 4: Self-Correction Refinement Loop activated")
    guardrail_result = state.get("guardrail_result", {})
    metrics = state.get("financial_metrics", [])
    
    # Filter out flagged discrepancy items
    flagged_names = {
        item["metric_name"] for item in guardrail_result.get("items", [])
        if item["status"] == "FLAGGED_DISCREPANCY"
    }
    refined_metrics = [m for m in metrics if m.get("name") not in flagged_names]

    current_iter = state.get("iterations", 1) + 1

    current_trace = list(state.get("trace", []))
    current_trace.append({
        "agent_name": "LangGraph Self-Correction Loop",
        "stage": f"Refinement Cycle (Iteration {current_iter})",
        "status": "completed",
        "thought_process": f"Purged {len(flagged_names)} hallucinated/unverified metric(s): {list(flagged_names)}. Re-running guardrail audit to achieve 100% groundedness.",
        "latency_ms": 120,
        "tokens_used": 0
    })

    return {
        "financial_metrics": refined_metrics,
        "iterations": current_iter,
        "trace": current_trace,
        "status": "refined",
        # Turn off trap after catching it so loop converges
        "inject_hallucination_trap": False
    }

async def node_synthesize(state: DocumentState) -> Dict[str, Any]:
    """Node 5: Executive Summarization & Committee Briefing Generation."""
    logger.info(f"[{state.get('job_id')}] Node 5: Executive Synthesis started")
    raw_text = state.get("raw_text", "")
    entities = state.get("entities", [])
    metrics = state.get("financial_metrics", [])
    classification = state.get("classification", {})
    risk_factors = state.get("risk_factors", [])
    guardrail_result = state.get("guardrail_result", {})

    result = await synthesis_agent.run(
        raw_text=raw_text,
        entities=entities,
        metrics=metrics,
        classification=classification,
        risk_factors=risk_factors,
        guardrail_result=guardrail_result
    )

    current_trace = list(state.get("trace", []))
    current_trace.append(result["trace_event"])

    return {
        "executive_summary": result["executive_summary"],
        "trace": current_trace,
        "status": "completed"
    }

def route_after_guardrails(state: DocumentState) -> Literal["node_refine", "node_synthesize"]:
    """Conditional Edge: Determines whether to trigger a self-correction loop or proceed to synthesis."""
    needs_refine = state.get("needs_refinement", False)
    iterations = state.get("iterations", 1)

    if needs_refine and iterations <= settings.MAX_REFINEMENT_LOOPS:
        logger.info(f"Routing to node_refine (Iteration {iterations})")
        return "node_refine"
    
    logger.info("Routing to node_synthesize (Guardrails Satisfied)")
    return "node_synthesize"

def build_orchestrator_graph():
    """Build and compile the LangGraph StateGraph workflow."""
    workflow = StateGraph(DocumentState)

    # Add Nodes
    workflow.add_node("node_ingest", node_ingest)
    workflow.add_node("node_classify", node_classify)
    workflow.add_node("node_guardrails", node_guardrails)
    workflow.add_node("node_refine", node_refine)
    workflow.add_node("node_synthesize", node_synthesize)

    # Define Graph Topology
    workflow.add_edge(START, "node_ingest")
    workflow.add_edge("node_ingest", "node_classify")
    workflow.add_edge("node_classify", "node_guardrails")
    
    # Conditional Edge with Cyclic Reflection Loop
    workflow.add_conditional_edges(
        "node_guardrails",
        route_after_guardrails,
        {
            "node_refine": "node_refine",
            "node_synthesize": "node_synthesize"
        }
    )
    # Complete cyclic connection: refine -> guardrails
    workflow.add_edge("node_refine", "node_guardrails")
    
    # Terminal Edge
    workflow.add_edge("node_synthesize", END)

    return workflow.compile()

# Global compiled graph instance
orchestrator_graph = build_orchestrator_graph()
