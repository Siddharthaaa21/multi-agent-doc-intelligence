# 🗄️ Module 05: PostgreSQL, Async SQLAlchemy & Audit Trail Persistence

## 1. Why Agent Systems Require Relational Persistence
In experimental ML, results are saved to `.csv` or log files. But in production financial systems:
- If a server crashes during a 10-K extraction run, the job state cannot vanish.
- Institutional risk committees require an **immutable audit trail**: which agent made the claim, which character span was cited, and what did the critic decide?
- Regulators require **traceability**: every credit committee decision must link back to the exact version of the model and verbatim text span.

---

## 2. Core Concepts: SQLAlchemy 2.0 Async

SQLAlchemy 2.0 provides native async support using Python type annotations:

```python
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import String, Float, Integer, ForeignKey, DateTime
from datetime import datetime

class Base(DeclarativeBase):
    pass

class AnalysisJob(Base):
    __tablename__ = "analysis_jobs"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    document_name: Mapped[str] = mapped_column(String(255))
    status: Mapped[str] = mapped_column(String(32), default="PENDING")
    groundedness_score: Mapped[float] = mapped_column(Float, default=0.0)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    # One-to-many relationship with agent traces
    traces: Mapped[list["AgentTraceLog"]] = relationship(back_populates="job", cascade="all, delete-orphan")
```

### The Async Session Pattern
In async backends, you open sessions asynchronously:
```python
async with async_session_factory() as session:
    async with session.begin():  # Automatically commits on block exit, rolls back on error
        job = AnalysisJob(id="job-123", document_name="10K.txt", status="RUNNING")
        session.add(job)
```

---

## 3. How to Run the Example

Run the self-contained script:
```bash
python reference-learning-kit/05-postgresql-and-async-persistence/runnable_async_db_example.py
```
This script creates an asynchronous database in-memory (using `sqlite+aiosqlite`), initializes relational tables, stores multi-agent execution traces and extracted financial metrics, and performs relational queries with joins.
