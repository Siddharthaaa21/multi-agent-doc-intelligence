# 🚀 Module 01: Async Python, FastAPI & Server-Sent Events (SSE)

## 1. Overview for ML Engineers
When transitioning from ML research to SDE-1 backend engineering, the biggest architectural shift is moving from **synchronous, blocking execution** (e.g. running scripts or notebook cells top-to-bottom) to **asynchronous, non-blocking I/O**.

In an AI agent system, waiting for an LLM API call or an external document parser takes 500ms to 5,000ms. In synchronous Python (Flask or standard Django), a single worker thread is locked during this entire wait. In asynchronous Python (FastAPI + `asyncio`), a single thread can handle thousands of concurrent requests by yielding control while waiting for I/O.

---

## 2. Core Concepts

### A. The `asyncio` Event Loop
- An **event loop** runs in a single OS thread. It maintains a queue of tasks.
- When an `async def` function hits `await some_io_operation()`, it pauses execution and yields control back to the event loop.
- The event loop switches to execute another task. When the I/O operation finishes, the event loop resumes the paused function.

> [!CAUTION]
> **The #1 Trap for ML Engineers in Async Python:**
> Never execute heavy CPU-bound code (e.g. matrix multiplication, tokenizer training, large regex loops) or blocking I/O (e.g. `requests.get()`, `time.sleep()`, standard `open()`) directly inside an `async def` function!
> This **blocks the entire event loop**, freezing all API requests for all users.
>
> **The Fix:**
> Offload CPU-bound or legacy blocking tasks to a threadpool:
> ```python
> import asyncio
> 
> # Good: Non-blocking offload
> result = await asyncio.to_thread(cpu_intensive_function, data)
> ```

---

### B. Pydantic v2 Data Modeling
Pydantic v2 compiles its core validation logic in Rust (`pydantic-core`), making it 5–10x faster than v1.

```python
from pydantic import BaseModel, Field, field_validator
from typing import List, Optional

class FinancialMetricExtraction(BaseModel):
    metric_name: str = Field(..., description="Name of financial metric, e.g. Revenue")
    raw_value: str = Field(..., description="Value as extracted from text")
    numeric_value: float = Field(..., description="Parsed float value")
    source_span: str = Field(..., description="Exact verbatim text span from filing")
    confidence: float = Field(ge=0.0, le=1.0, description="Extraction confidence")

    @field_validator("source_span")
    @classmethod
    def validate_non_empty_span(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("source_span cannot be empty")
        return v
```

---

### C. Server-Sent Events (SSE) Streaming
When an autonomous multi-agent pipeline runs, the analyst needs real-time feedback:
1. `IngestionAgent` finished parsing document chunks.
2. `ClassifierAgent` tagged document as 10-K.
3. `GuardrailCritic` checked 5 metrics and found an arithmetic variance.
4. `RefinementNode` corrected the variance.

Instead of heavy bi-directional WebSockets, **Server-Sent Events (SSE)** uses standard HTTP streaming:
- HTTP Header: `Content-Type: text/event-stream`
- Connection: `keep-alive`
- Wire format: `data: {"event": "agent_step", "message": "..."}\n\n` (ending with two newlines)

---

## 3. How to Run the Example

Run the self-contained script:
```bash
python reference-learning-kit/01-async-fastapi-sse/runnable_fastapi_sse_example.py
```
This script runs a complete mock agent pipeline over an SSE event stream and prints each chunk in real-time.
