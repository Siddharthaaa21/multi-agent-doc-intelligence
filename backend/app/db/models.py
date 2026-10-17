from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy import String, Float, Integer, ForeignKey, DateTime, Text, Boolean, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.session import Base

def utc_now():
    return datetime.now(timezone.utc)


class AnalysisJobModel(Base):
    __tablename__ = "analysis_jobs"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    file_type: Mapped[str] = mapped_column(String(32), default="txt")
    doc_type_classified: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    status: Mapped[str] = mapped_column(String(32), default="queued")
    groundedness_score: Mapped[float] = mapped_column(Float, default=0.0)
    iterations: Mapped[int] = mapped_column(Integer, default=1)
    needs_refinement: Mapped[bool] = mapped_column(Boolean, default=False)
    total_turnaround_time_sec: Mapped[float] = mapped_column(Float, default=0.0)
    turnaround_reduction_pct: Mapped[float] = mapped_column(Float, default=0.0)
    llm_provider: Mapped[str] = mapped_column(String(32), default="simulation")
    error: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now, onupdate=utc_now)

    # Relationships
    traces: Mapped[List["AgentTraceModel"]] = relationship(
        back_populates="job", cascade="all, delete-orphan", order_by="AgentTraceModel.step_number"
    )
    metrics: Mapped[List["FinancialMetricModel"]] = relationship(
        back_populates="job", cascade="all, delete-orphan"
    )
    risk_factors: Mapped[List["RiskFactorModel"]] = relationship(
        back_populates="job", cascade="all, delete-orphan"
    )
    chunks: Mapped[List["SemanticChunkModel"]] = relationship(
        back_populates="job", cascade="all, delete-orphan", order_by="SemanticChunkModel.chunk_index"
    )

class AgentTraceModel(Base):
    __tablename__ = "agent_traces"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    job_id: Mapped[str] = mapped_column(ForeignKey("analysis_jobs.id"), nullable=False, index=True)
    step_number: Mapped[int] = mapped_column(Integer, nullable=False)
    node_name: Mapped[str] = mapped_column(String(64), nullable=False)
    agent_persona: Mapped[str] = mapped_column(String(64), nullable=False)
    action: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(String(32), default="completed")
    latency_ms: Mapped[float] = mapped_column(Float, default=0.0)
    payload_json: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now)

    job: Mapped["AnalysisJobModel"] = relationship(back_populates="traces")

class FinancialMetricModel(Base):
    __tablename__ = "financial_metrics"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    job_id: Mapped[str] = mapped_column(ForeignKey("analysis_jobs.id"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    raw_value: Mapped[str] = mapped_column(String(64), nullable=False)
    numeric_value: Mapped[float] = mapped_column(Float, nullable=False)
    unit: Mapped[str] = mapped_column(String(32), default="USD_MILLIONS")
    source_span: Mapped[str] = mapped_column(Text, nullable=False)
    period: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    is_grounded: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now)

    job: Mapped["AnalysisJobModel"] = relationship(back_populates="metrics")

class RiskFactorModel(Base):
    __tablename__ = "risk_factors"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    job_id: Mapped[str] = mapped_column(ForeignKey("analysis_jobs.id"), nullable=False, index=True)
    category: Mapped[str] = mapped_column(String(64), nullable=False)
    severity: Mapped[str] = mapped_column(String(32), default="Moderate")
    description: Mapped[str] = mapped_column(Text, nullable=False)
    cited_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now)

    job: Mapped["AnalysisJobModel"] = relationship(back_populates="risk_factors")
 
class SemanticChunkModel(Base):
    __tablename__ = "semantic_chunks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    job_id: Mapped[str] = mapped_column(ForeignKey("analysis_jobs.id"), nullable=False, index=True)
    chunk_index: Mapped[int] = mapped_column(Integer, nullable=False)
    section_title: Mapped[str] = mapped_column(String(128), default="General Section")
    content: Mapped[str] = mapped_column(Text, nullable=False)
    start_char: Mapped[int] = mapped_column(Integer, nullable=False)
    end_char: Mapped[int] = mapped_column(Integer, nullable=False)
    token_count: Mapped[int] = mapped_column(Integer, default=0)
    embedding_json: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now)

    job: Mapped["AnalysisJobModel"] = relationship(back_populates="chunks")
