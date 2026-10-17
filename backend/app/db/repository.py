import logging
from typing import Dict, Any, List, Optional
from sqlalchemy import select, desc
from sqlalchemy.orm import selectinload
from app.db.session import async_session_factory
from app.db.models import AnalysisJobModel, AgentTraceModel, FinancialMetricModel, RiskFactorModel

logger = logging.getLogger(__name__)

class DocumentRepository:
    """Asynchronous repository for persisting multi-agent document analysis jobs and audit traces."""

    @staticmethod
    async def create_job(
        job_id: str,
        filename: str,
        file_type: str = "txt",
        llm_provider: str = "simulation"
    ) -> Optional[AnalysisJobModel]:
        try:
            async with async_session_factory() as session:
                async with session.begin():
                    job = AnalysisJobModel(
                        id=job_id,
                        filename=filename,
                        file_type=file_type,
                        status="queued",
                        llm_provider=llm_provider
                    )
                    session.add(job)
                await session.refresh(job)
                return job
        except Exception as e:
            logger.error(f"Failed to create job {job_id} in database: {e}", exc_info=True)
            return None

    @staticmethod
    async def record_trace_step(
        job_id: str,
        step_number: int,
        node_name: str,
        agent_persona: str,
        action: str,
        latency_ms: float = 0.0,
        payload_json: Optional[dict] = None
    ) -> bool:
        try:
            async with async_session_factory() as session:
                async with session.begin():
                    trace = AgentTraceModel(
                        job_id=job_id,
                        step_number=step_number,
                        node_name=node_name,
                        agent_persona=agent_persona,
                        action=action,
                        latency_ms=latency_ms,
                        payload_json=payload_json
                    )
                    session.add(trace)
            return True
        except Exception as e:
            logger.warning(f"Could not persist trace step for {job_id}: {e}")
            return False

    @staticmethod
    async def update_completed_job(
        job_id: str,
        state: Dict[str, Any]
    ) -> bool:
        try:
            async with async_session_factory() as session:
                async with session.begin():
                    stmt = select(AnalysisJobModel).where(AnalysisJobModel.id == job_id)
                    result = await session.execute(stmt)
                    job = result.scalar_one_or_none()
                    if not job:
                        # If job wasn't created initially in DB, instantiate it now
                        job = AnalysisJobModel(id=job_id, filename=state.get("metadata", {}).get("filename", "unknown"))
                        session.add(job)

                    # Update scalar fields
                    job.status = state.get("status", "completed")
                    job.iterations = state.get("iterations", 1)
                    job.needs_refinement = state.get("needs_refinement", False)
                    job.total_turnaround_time_sec = state.get("total_turnaround_time_sec", 0.0)
                    job.turnaround_reduction_pct = state.get("turnaround_reduction_pct", 0.0)
                    job.error = state.get("error")

                    classification = state.get("classification")
                    if classification:
                        job.doc_type_classified = classification.get("doc_type") if isinstance(classification, dict) else getattr(classification, "doc_type", None)

                    guardrail = state.get("guardrail_result")
                    if guardrail:
                        score = guardrail.get("overall_groundedness_score", 0.0) if isinstance(guardrail, dict) else getattr(guardrail, "overall_groundedness_score", 0.0)
                        job.groundedness_score = float(score)

                    # Save financial metrics
                    metrics = state.get("financial_metrics", [])
                    for m in metrics:
                        m_dict = m if isinstance(m, dict) else m.model_dump()
                        metric_row = FinancialMetricModel(
                            job_id=job_id,
                            name=m_dict.get("name", "Unknown"),
                            raw_value=str(m_dict.get("raw_value", "")),
                            numeric_value=float(m_dict.get("numeric_value", 0.0)),
                            unit=m_dict.get("unit", "USD_MILLIONS"),
                            source_span=m_dict.get("source_span", ""),
                            period=m_dict.get("period"),
                            is_grounded=bool(m_dict.get("is_grounded", True))
                        )
                        session.add(metric_row)

                    # Save risk factors
                    risks = state.get("risk_factors", [])
                    for r in risks:
                        r_dict = r if isinstance(r, dict) else r.model_dump()
                        risk_row = RiskFactorModel(
                            job_id=job_id,
                            category=r_dict.get("category", "General"),
                            severity=r_dict.get("severity", "Moderate"),
                            description=r_dict.get("description", ""),
                            cited_text=r_dict.get("cited_text")
                        )
                        session.add(risk_row)

            return True
        except Exception as e:
            logger.error(f"Failed to update completed job {job_id} in database: {e}", exc_info=True)
            return False

    @staticmethod
    async def get_job_by_id(job_id: str) -> Optional[Dict[str, Any]]:
        try:
            async with async_session_factory() as session:
                stmt = (
                    select(AnalysisJobModel)
                    .options(
                        selectinload(AnalysisJobModel.traces),
                        selectinload(AnalysisJobModel.metrics),
                        selectinload(AnalysisJobModel.risk_factors)
                    )
                    .where(AnalysisJobModel.id == job_id)
                )
                result = await session.execute(stmt)
                job = result.scalar_one_or_none()
                if not job:
                    return None

                return {
                    "job_id": job.id,
                    "filename": job.filename,
                    "file_type": job.file_type,
                    "doc_type_classified": job.doc_type_classified,
                    "status": job.status,
                    "groundedness_score": job.groundedness_score,
                    "iterations": job.iterations,
                    "needs_refinement": job.needs_refinement,
                    "total_turnaround_time_sec": job.total_turnaround_time_sec,
                    "turnaround_reduction_pct": job.turnaround_reduction_pct,
                    "llm_provider": job.llm_provider,
                    "error": job.error,
                    "created_at": job.created_at.isoformat() if job.created_at else None,
                    "traces": [
                        {
                            "step_number": t.step_number,
                            "node_name": t.node_name,
                            "agent_persona": t.agent_persona,
                            "action": t.action,
                            "latency_ms": t.latency_ms,
                            "payload": t.payload_json,
                            "timestamp": t.created_at.isoformat() if t.created_at else None
                        }
                        for t in job.traces
                    ],
                    "metrics": [
                        {
                            "name": m.name,
                            "raw_value": m.raw_value,
                            "numeric_value": m.numeric_value,
                            "unit": m.unit,
                            "source_span": m.source_span,
                            "period": m.period,
                            "is_grounded": m.is_grounded
                        }
                        for m in job.metrics
                    ],
                    "risk_factors": [
                        {
                            "category": r.category,
                            "severity": r.severity,
                            "description": r.description,
                            "cited_text": r.cited_text
                        }
                        for r in job.risk_factors
                    ]
                }
        except Exception as e:
            logger.error(f"Error fetching job {job_id} from database: {e}", exc_info=True)
            return None

    @staticmethod
    async def list_jobs(limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
        try:
            async with async_session_factory() as session:
                stmt = (
                    select(AnalysisJobModel)
                    .order_by(desc(AnalysisJobModel.created_at))
                    .limit(limit)
                    .offset(offset)
                )
                result = await session.execute(stmt)
                jobs = result.scalars().all()
                return [
                    {
                        "job_id": j.id,
                        "filename": j.filename,
                        "status": j.status,
                        "doc_type": j.doc_type_classified,
                        "groundedness_score": j.groundedness_score,
                        "turnaround_time_sec": j.total_turnaround_time_sec,
                        "turnaround_reduction_pct": j.turnaround_reduction_pct,
                        "created_at": j.created_at.isoformat() if j.created_at else None
                    }
                    for j in jobs
                ]
        except Exception as e:
            logger.error(f"Error listing jobs from database: {e}", exc_info=True)
            return []

repo = DocumentRepository()
