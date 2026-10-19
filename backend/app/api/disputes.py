import logging
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

from app.disputes.manager import dispute_manager

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/disputes", tags=["Dispute Resolution Hub"])

class DiscrepancyResolutionRequest(BaseModel):
    job_id: str
    metric_name: str
    status: str = Field(..., description="'APPROVED', 'OVERRIDDEN', or 'ESCALATED_TO_COMMITTEE'")
    analyst_id: str = "SeniorRiskAnalyst_01"
    review_notes: str
    original_value: Optional[str] = None
    corrected_value: Optional[str] = None
    source_span: Optional[str] = None

@router.get("")
@router.get("/")
async def list_all_resolutions():
    """
    Retrieve all institutional dispute resolutions, audit signatures, and review history.
    """
    resolutions = dispute_manager.get_all_resolutions()
    return {
        "total": len(resolutions),
        "resolutions": resolutions
    }

@router.get("/metrics")
async def get_dispute_metrics():
    """
    Retrieve dispute resolution breakdown metrics for compliance audits.
    """
    resolutions = dispute_manager.get_all_resolutions()
    approved = sum(1 for r in resolutions if r.get("status") == "APPROVED")
    overridden = sum(1 for r in resolutions if r.get("status") == "OVERRIDDEN")
    escalated = sum(1 for r in resolutions if r.get("status") == "ESCALATED_TO_COMMITTEE")
    verified = sum(1 for r in resolutions if r.get("verified"))
    return {
        "total_disputes": len(resolutions),
        "approved": approved,
        "overridden": overridden,
        "escalated_to_committee": escalated,
        "cryptographically_verified_pct": (verified / len(resolutions) * 100.0) if resolutions else 100.0
    }

@router.post("/resolve")
async def resolve_discrepancy(req: DiscrepancyResolutionRequest):
    """
    Record an analyst discrepancy override or committee escalation with cryptographic audit hash.
    """
    valid_statuses = {"APPROVED", "OVERRIDDEN", "ESCALATED_TO_COMMITTEE"}
    if req.status.upper() not in valid_statuses:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid status '{req.status}'. Must be one of: {list(valid_statuses)}"
        )

    resolution = dispute_manager.record_resolution(
        job_id=req.job_id,
        metric_name=req.metric_name,
        resolution_status=req.status,
        analyst_id=req.analyst_id,
        review_notes=req.review_notes,
        original_value=req.original_value,
        corrected_value=req.corrected_value,
        source_span=req.source_span
    )
    return resolution

@router.get("/{job_id}")
async def get_resolutions_for_job(job_id: str):
    """
    Retrieve audit history and cryptographic verification hashes for a job's discrepancies.
    """
    resolutions = dispute_manager.get_job_resolutions(job_id)
    return {
        "job_id": job_id,
        "total_resolutions": len(resolutions),
        "resolutions": resolutions
    }
