#!/usr/bin/env python3
"""
Module 05: Runnable Async SQLAlchemy 2.0 Persistence & Audit Trail Example
Demonstrates:
1. Modern SQLAlchemy 2.0 declarative Mapped models
2. Asynchronous engine & session management with aiosqlite / asyncpg
3. Relational modeling for agent execution traces and financial metrics
4. Querying audit logs and calculating job-level statistics
"""

import asyncio
from datetime import datetime
from typing import List
from sqlalchemy import String, Float, Integer, ForeignKey, DateTime, select
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, selectinload
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

# ==============================================================================
# 1. Relational Schema Definition
# ==============================================================================

class Base(DeclarativeBase):
    pass

class AnalysisJob(Base):
    __tablename__ = "analysis_jobs"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    document_name: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(String(32), default="PENDING")
    groundedness_score: Mapped[float] = mapped_column(Float, default=0.0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    traces: Mapped[List["AgentTraceLog"]] = relationship(back_populates="job", cascade="all, delete-orphan")
    metrics: Mapped[List["FinancialMetricRecord"]] = relationship(back_populates="job", cascade="all, delete-orphan")

class AgentTraceLog(Base):
    __tablename__ = "agent_trace_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    job_id: Mapped[str] = mapped_column(ForeignKey("analysis_jobs.id"), nullable=False)
    step_number: Mapped[int] = mapped_column(Integer, nullable=False)
    agent_name: Mapped[str] = mapped_column(String(64), nullable=False)
    action_description: Mapped[str] = mapped_column(String(255), nullable=False)
    latency_ms: Mapped[float] = mapped_column(Float, default=0.0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    job: Mapped["AnalysisJob"] = relationship(back_populates="traces")

class FinancialMetricRecord(Base):
    __tablename__ = "financial_metric_records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    job_id: Mapped[str] = mapped_column(ForeignKey("analysis_jobs.id"), nullable=False)
    metric_name: Mapped[str] = mapped_column(String(128), nullable=False)
    numeric_value: Mapped[float] = mapped_column(Float, nullable=False)
    source_span: Mapped[str] = mapped_column(String(512), nullable=False)
    is_grounded: Mapped[bool] = mapped_column(default=True)

    job: Mapped["AnalysisJob"] = relationship(back_populates="metrics")

# ==============================================================================
# 2. Database Service Implementation
# ==============================================================================

class DocumentDatabaseService:
    def __init__(self, db_url: str = "sqlite+aiosqlite:///:memory:"):
        self.engine = create_async_engine(db_url, echo=False)
        self.session_factory = async_sessionmaker(bind=self.engine, expire_on_commit=False)

    async def init_db(self):
        """Initializes tables asynchronously."""
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    async def record_completed_job(
        self,
        job_id: str,
        doc_name: str,
        traces: List[dict],
        metrics: List[dict],
        groundedness: float
    ):
        """Persists a complete agent workflow run inside a single ACID transaction."""
        async with self.session_factory() as session:
            async with session.begin():
                job = AnalysisJob(
                    id=job_id,
                    document_name=doc_name,
                    status="COMPLETED",
                    groundedness_score=groundedness
                )
                session.add(job)

                for t in traces:
                    trace_record = AgentTraceLog(
                        job_id=job_id,
                        step_number=t["step"],
                        agent_name=t["agent"],
                        action_description=t["action"],
                        latency_ms=t["latency_ms"]
                    )
                    session.add(trace_record)

                for m in metrics:
                    metric_record = FinancialMetricRecord(
                        job_id=job_id,
                        metric_name=m["name"],
                        numeric_value=m["value"],
                        source_span=m["span"],
                        is_grounded=m["is_grounded"]
                    )
                    session.add(metric_record)

    async def get_job_audit_report(self, job_id: str):
        """Queries job with all related agent traces and financial metrics."""
        async with self.session_factory() as session:
            stmt = (
                select(AnalysisJob)
                .options(selectinload(AnalysisJob.traces), selectinload(AnalysisJob.metrics))
                .where(AnalysisJob.id == job_id)
            )
            result = await session.execute(stmt)
            return result.scalar_one_or_none()

# ==============================================================================
# 3. Demonstration Script
# ==============================================================================

async def main():
    print("=" * 75)
    print("🗄️ Async SQLAlchemy 2.0 Agent Persistence & Audit Trail Demo")
    print("=" * 75)

    db = DocumentDatabaseService()
    await db.init_db()
    print("✓ Asynchronous database tables created.")

    # Record a completed analysis run
    sample_job_id = "JOB-SEC-10K-2026-X1"
    sample_traces = [
        {"step": 1, "agent": "IngestionAgent", "action": "Parsed 12 chunks from 10-K filing", "latency_ms": 142.5},
        {"step": 2, "agent": "TaxonomyAgent", "action": "Classified SEC Form 10-K & mapped MD&A", "latency_ms": 210.0},
        {"step": 3, "agent": "CriticGuardrail", "action": "Audited metrics: 3 grounded, 0 violations", "latency_ms": 85.2},
        {"step": 4, "agent": "ExecutiveSynthesisAgent", "action": "Compiled C-Suite briefing memo", "latency_ms": 420.1},
    ]
    sample_metrics = [
        {"name": "Total Revenue", "value": 391035.0, "span": "Total net sales were $391,035 million", "is_grounded": True},
        {"name": "Operating Income", "value": 123216.0, "span": "Operating income was $123,216 million", "is_grounded": True},
        {"name": "Operating Margin", "value": 31.5, "span": "representing an operating margin of 31.5%", "is_grounded": True},
    ]

    print(f"\n[Persisting Job] Writing ACID transaction for {sample_job_id}...")
    await db.record_completed_job(
        job_id=sample_job_id,
        doc_name="AAPL_FY2024_10K.txt",
        traces=sample_traces,
        metrics=sample_metrics,
        groundedness=1.0
    )
    print("✓ Job and related entities committed successfully.")

    # Query audit record
    print(f"\n[Querying Audit Report] Retrieving {sample_job_id} with relationship preloading...")
    job_record = await db.get_job_audit_report(sample_job_id)
    assert job_record is not None, "Job should exist!"

    print(f"\n📋 AUDIT TRAIL FOR JOB: {job_record.id}")
    print(f"   Document:   {job_record.document_name}")
    print(f"   Status:     {job_record.status}")
    print(f"   Grounded:   {job_record.groundedness_score:.1%}")
    print(f"   Created At: {job_record.created_at}")

    print("\n   ⚡ Agent Trace Steps:")
    for t in sorted(job_record.traces, key=lambda x: x.step_number):
        print(f"     Step {t.step_number}: [{t.agent_name:<22}] {t.action_description} ({t.latency_ms}ms)")

    print("\n   📊 Persisted Financial Metrics:")
    for m in job_record.metrics:
        print(f"     • {m.metric_name:<18} = {m.numeric_value:<10} | Span: '{m.source_span}'")

    print("\n" + "=" * 75)
    print("✨ Async database persistence verified successfully!")
    print("=" * 75)

if __name__ == "__main__":
    asyncio.run(main())
