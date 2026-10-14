# 🔄 Module 02: LangGraph Cyclic State Machines & Dynamic Self-Healing

## 1. Why Linear Chains Fail in Production
Traditional LLM frameworks (LangChain LCEL, LlamaIndex pipelines, simple DAGs) execute in a strict forward-only sequence:
$$\text{Ingest} \longrightarrow \text{Extract} \longrightarrow \text{Summarize}$$

In financial and legal analysis, forward-only pipelines suffer from **compounding hallucination drift**:
- If the extractor mistakes non-operating income for operating income, the summarizer outputs an erroneous credit rating.
- A forward-only chain cannot stop, inspect its own intermediate output, and route backward to fix the mistake.

**LangGraph** solves this by modeling multi-agent workflows as **Cyclic State Graphs**:
- Nodes read and update a shared, type-safe `State`.
- **Conditional edges** dynamically inspect state variables (e.g. `groundedness_score`).
- When a metric is ungrounded or an arithmetic equation fails, the graph **loops back** to a self-correction refinement node until invariants are satisfied.

---

## 2. Core Concepts

### A. The State Schema (`TypedDict`)
The state is the single source of truth passed across all nodes in the graph:

```python
from typing import TypedDict, List, Optional

class FinancialDocumentState(TypedDict):
    raw_text: str
    extracted_metrics: List[dict]
    groundedness_score: float
    refinement_attempts: int
    executive_memo: Optional[str]
    status: str
```

### B. Pure Function Nodes
Every node is a function with the signature:
$$\text{node\_fn}(\text{state: State}) \longrightarrow \text{Dict[str, Any]}$$
The returned dictionary is automatically merged into the graph's running state.

### C. Conditional Routing & Cyclic Self-Healing
A routing function inspects the state and returns the next node's name:

```python
def route_after_critic(state: FinancialDocumentState) -> str:
    # If groundedness meets SLA threshold (>= 95%), proceed to synthesis
    if state["groundedness_score"] >= 0.95:
        return "synthesis_agent"
    
    # Circuit breaker: stop after 2 refinement attempts to prevent infinite loop
    if state["refinement_attempts"] >= 2:
        return "synthesis_agent"  # Fallback to annotated variance memo
        
    return "refinement_node"  # Loop back to self-correction
```

Graph topology:
```
           ┌──────────────────────┐
           │   Ingestion Agent    │
           └──────────┬───────────┘
                      ▼
           ┌──────────────────────┐
    ┌─────►│  Critic Guardrail    │◄─────┐
    │      └──────────┬───────────┘      │
    │                 │                  │
    │ (Score < 95%)   │ (Score ≥ 95%)    │
    │                 ▼                  │
┌───┴──────────┐   ┌──────────────────┐  │
│  Refinement  │   │ Synthesis Agent  │  │
│  Node        ├───┤ (C-Suite Memo)   │  │
└──────────────┘   └──────────────────┘  │
       │                                 │
       └─────────────────────────────────┘
```

---

## 3. How to Run the Example

Run the self-contained script:
```bash
python reference-learning-kit/02-langgraph-state-machine/runnable_cyclic_graph_example.py
```
This script creates a 4-node LangGraph state machine, deliberately injects an ungrounded hallucination, and watches the cyclic self-healing loop intercept and repair it before compiling the final memo.
