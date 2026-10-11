from typing import TypedDict, List, Dict, Any, Optional

class DocumentState(TypedDict, total=False):
    job_id: str
    raw_text: str
    metadata: Dict[str, Any]
    chunks: List[Dict[str, Any]]
    entities: List[Dict[str, Any]]
    financial_metrics: List[Dict[str, Any]]
    classification: Optional[Dict[str, Any]]
    risk_factors: List[Dict[str, Any]]
    guardrail_result: Optional[Dict[str, Any]]
    executive_summary: Optional[Dict[str, Any]]
    trace: List[Dict[str, Any]]
    iterations: int
    needs_refinement: bool
    inject_hallucination_trap: bool
    llm_provider: str
    error: Optional[str]
    status: str
    total_turnaround_time_sec: float
