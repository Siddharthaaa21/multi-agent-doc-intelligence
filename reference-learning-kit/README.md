# 🧭 SDE-1 AI Systems Engineering Master Learning Kit
### Multi-Agent Document Intelligence & Financial Risk Orchestrator

Welcome! This kit is specifically structured for **ML engineers and data scientists transitioning into Software Development Engineering (SDE-1 / AI Systems Engineering)**.

If you already understand machine learning (embeddings, attention, loss functions, token generation), but your backend development skills are rusty or you haven't built asynchronous microservices and production test harnesses before, this kit bridges that exact gap.

---

## 🎯 The Mental Shift: ML Mindset vs. SDE-1 AI Systems Mindset

| Dimension | Machine Learning Mindset | SDE-1 / AI Systems Engineering Mindset |
| :--- | :--- | :--- |
| **Execution Environment** | Jupyter Notebooks, script runs, ad-hoc execution | Async event loops (`asyncio`), stateless containers, connection pools |
| **Data Contracts** | Loose Python dicts, NumPy arrays, pandas DataFrames | Strict schema validation with Pydantic v2 and TypeScript interfaces |
| **Control Flow** | Sequential steps or linear DAGs (LangChain LCEL) | Deterministic cyclic state machines with dynamic self-healing (LangGraph) |
| **Error Handling** | Model output tolerance, probabilistic variance | Fail-fast validation, adversarial critic guardrails, bounded retry loops |
| **Testing & Quality** | Train/Validation loss, test set accuracy (probabilistic) | Automated regression test suites, zero-defect SLA gates, CI/CD blockers |
| **Deployment** | "It ran on my GPU workstation" | Multi-stage Docker containers, Docker Compose, automated GitHub Actions |
| **Persistence** | Pickled checkpoints (`.pt`, `.pkl`) | ACID relational storage (PostgreSQL), audit trails, event replay logs |

---

## 🗺️ Master Curriculum Roadmap

| Module | Core Concepts & Engineering Patterns | Runnable Code Example | Target Project Component |
| :--- | :--- | :--- | :--- |
| [**01. Async FastAPI & SSE**](./01-async-fastapi-sse/README.md) | `asyncio` event loop, cooperative concurrency, Pydantic v2 schemas, Server-Sent Events (SSE) streaming | [`runnable_fastapi_sse_example.py`](./01-async-fastapi-sse/runnable_fastapi_sse_example.py) | `backend/app/main.py`, `backend/app/api/` |
| [**02. LangGraph State Machine**](./02-langgraph-state-machine/README.md) | `StateGraph`, `TypedDict` state, pure node transitions, conditional routing edges, cyclic self-healing loops | [`runnable_cyclic_graph_example.py`](./02-langgraph-state-machine/runnable_cyclic_graph_example.py) | `backend/app/orchestrator/graph.py` |
| [**03. Adversarial Guardrails**](./03-adversarial-guardrails-and-grounding/README.md) | Character-span anchoring, exact/fuzzy substring matching, arithmetic invariant audits, adversarial trap injection | [`runnable_critic_guardrail_example.py`](./03-adversarial-guardrails-and-grounding/runnable_critic_guardrail_example.py) | `backend/app/agents/guardrail_agent.py` |
| [**04. Docker & Containerization**](./04-docker-and-containerization/README.md) | Multi-stage container builds, non-root users, layer caching, Docker Compose multi-service networks | [`Dockerfile.example`](./04-docker-and-containerization/Dockerfile.example), [`docker-compose.example.yml`](./04-docker-and-containerization/docker-compose.example.yml) | `Dockerfile`, `docker-compose.yml` |
| [**05. PostgreSQL & Persistence**](./05-postgresql-and-async-persistence/README.md) | Relational modeling for agent workflows, async SQLAlchemy 2.0, audit log persistence, connection pooling | [`runnable_async_db_example.py`](./05-postgresql-and-async-persistence/runnable_async_db_example.py) | Database layer, job state storage |
| [**06. Pytest & CI/CD SLA Harness**](./06-pytest-and-regression-sla-harness/README.md) | Unit vs integration vs regression testing, conftest fixtures, mock providers, asserting 99.2% pass rates | [`runnable_sla_test_example.py`](./06-pytest-and-regression-sla-harness/runnable_sla_test_example.py) | `backend/tests/`, `eval_runner.py`, CI |
| [**07. Financial Filings Domain Guide**](./07-financial-domain-for-engineers/README.md) | 10-K, 10-Q, 8-K structure; Item 1A Risks, Item 7 MD&A; EBITDA, leverage covenants; why hallucinations are fatal | Domain reference guide & checklist | Financial extraction prompts & benchmark data |

---

## ⚡ Quick Start: Running the Examples

All Python example files in this kit are self-contained and runnable using the repository virtual environment:

```bash
# 1. Activate the environment
cd /Users/siddhartha/Desktop/internal-project-stuff/ai-agentic-systems/multi-agent-doc-intelligence
source backend/venv/bin/activate

# 2. Run Module 01 (Async FastAPI & SSE Streaming)
python reference-learning-kit/01-async-fastapi-sse/runnable_fastapi_sse_example.py

# 3. Run Module 02 (LangGraph Cyclic State Machine)
python reference-learning-kit/02-langgraph-state-machine/runnable_cyclic_graph_example.py

# 4. Run Module 03 (Adversarial Critic Guardrails)
python reference-learning-kit/03-adversarial-guardrails-and-grounding/runnable_critic_guardrail_example.py

# 5. Run Module 05 (Async SQLAlchemy Persistence)
python reference-learning-kit/05-postgresql-and-async-persistence/runnable_async_db_example.py

# 6. Run Module 06 (Regression Evaluation Harness with Pytest)
python -m pytest reference-learning-kit/06-pytest-and-regression-sla-harness/runnable_sla_test_example.py -v
```

---

## 🏗️ How This Codebase Solves Real-World Production Challenges

1. **Why LangGraph instead of simple sequential chains?**
   Sequential chains fail whenever extraction extracts numbers that don't match the source text or violate accounting equations. LangGraph introduces **cycles**: an adversarial critic catches the error and sends the state back to a refinement node to fix it before final synthesis.

2. **Why Server-Sent Events (SSE) instead of WebSockets?**
   Multi-agent tasks take between 1 to 5 seconds. Streaming agent thought logs, extraction events, and guardrail decisions unidirectionally over standard HTTP/2 with SSE is far simpler, more reliable, and firewall-friendly than stateful bi-directional WebSockets.

3. **Why an Automated Regression Evaluation Harness?**
   In enterprise finance, "prompt changes" can silently degrade performance on edge-case filings. The 25-scenario evaluation harness validates 125 assertions on every commit. If pass rate drops below 99.0%, the CI pipeline aborts release.
