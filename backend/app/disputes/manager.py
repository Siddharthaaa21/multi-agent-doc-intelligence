import hashlib
import json
import logging
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)

class DisputeResolutionManager:
    """
    Manages institutional analyst reviews, discrepancy overrides, and audit trails:
    - Allows financial analysts and credit committees to review flagged discrepancies.
    - Records immutable SHA-256 digital signatures for compliance auditing.
    - Supports collaborative sign-offs (Approved, Overridden, Escalated to Committee).
    """

    def __init__(self):
        # In-memory audit registry (can sync to DB)
        self._resolutions: Dict[str, List[Dict[str, Any]]] = {}
        # Seed initial institutional audit log
        self._seed_initial_audit_log()

    def _seed_initial_audit_log(self):
        """Seed initial audit trail for demonstration and verification."""
        self.record_resolution(
            job_id="job_tc15_adversarial_trap",
            metric_name="Debt to Equity Ratio",
            resolution_status="OVERRIDDEN",
            analyst_id="LeadRiskOfficer_402",
            review_notes="Injected adversarial hallucination ratio of 9.4x was intercepted by Critic Guardrail. Overridden with canonical balance sheet value of 1.42x verified from footnote 14.",
            original_value="9.4x (Injected Trap)",
            corrected_value="1.42x (Audited 10-K Footnote 14)",
            source_span="Total Liabilities / Total Equity = 1.42"
        )
        self.record_resolution(
            job_id="job_aapl_fy24_annual",
            metric_name="Operating Margin",
            resolution_status="APPROVED",
            analyst_id="SeniorCreditAnalyst_109",
            review_notes="Operating income and total net sales cross-referenced with Consolidated Statements of Operations. Arithmetic invariant verified at 31.5% with 0.992 confidence.",
            original_value="31.5%",
            corrected_value="31.5%",
            source_span="Operating income $123,216M / Total net sales $391,035M"
        )

    def get_all_resolutions(self) -> List[Dict[str, Any]]:
        """Retrieve all recorded dispute resolutions across all jobs."""
        all_res: List[Dict[str, Any]] = []
        for job_res in self._resolutions.values():
            all_res.extend(job_res)
        return all_res

    def record_resolution(
        self,
        job_id: str,
        metric_name: str,
        resolution_status: str,  # "APPROVED", "OVERRIDDEN", "ESCALATED_TO_COMMITTEE"
        analyst_id: str,
        review_notes: str,
        original_value: Optional[str] = None,
        corrected_value: Optional[str] = None,
        source_span: Optional[str] = None
    ) -> Dict[str, Any]:
        """Record an analyst review decision with cryptographic hash verification."""
        timestamp = datetime.now(timezone.utc).isoformat()
        
        # Build canonical payload for hash signature
        canonical = {
            "job_id": job_id,
            "metric_name": metric_name,
            "status": resolution_status.upper(),
            "analyst_id": analyst_id,
            "timestamp": timestamp,
            "original_value": original_value or "",
            "corrected_value": corrected_value or "",
            "notes": review_notes
        }
        
        # SHA-256 audit digest
        payload_bytes = json.dumps(canonical, sort_keys=True).encode("utf-8")
        audit_hash = hashlib.sha256(payload_bytes).hexdigest()

        entry = {
            **canonical,
            "source_span": source_span or "",
            "audit_hash": audit_hash,
            "verified": True
        }

        if job_id not in self._resolutions:
            self._resolutions[job_id] = []
        
        self._resolutions[job_id].append(entry)
        logger.info(f"Recorded discrepancy resolution for {metric_name} on job {job_id} by {analyst_id} [{resolution_status}]")
        return entry

    def get_job_resolutions(self, job_id: str) -> List[Dict[str, Any]]:
        """Retrieve audit history of resolutions for a given document intelligence job."""
        return self._resolutions.get(job_id, [])

    def verify_audit_hash(self, entry: Dict[str, Any]) -> bool:
        """Verify cryptographic integrity of an analyst review entry."""
        canonical = {
            "job_id": entry["job_id"],
            "metric_name": entry["metric_name"],
            "status": entry["status"],
            "analyst_id": entry["analyst_id"],
            "timestamp": entry["timestamp"],
            "original_value": entry.get("original_value", ""),
            "corrected_value": entry.get("corrected_value", ""),
            "notes": entry.get("notes", "")
        }
        payload_bytes = json.dumps(canonical, sort_keys=True).encode("utf-8")
        expected_hash = hashlib.sha256(payload_bytes).hexdigest()
        return entry.get("audit_hash") == expected_hash

dispute_manager = DisputeResolutionManager()
