import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.metrics.exporter import PrometheusMetricsExporter, metrics_exporter
from app.disputes.manager import DisputeResolutionManager, dispute_manager

@pytest.fixture
def client():
    return TestClient(app)

# ------------------------------------------------------------------------------
# 1. Prometheus Metrics Exporter Tests
# ------------------------------------------------------------------------------
def test_prometheus_metrics_formatting():
    exporter = PrometheusMetricsExporter()
    exporter.record_job_completion(
        duration_sec=112.5,
        groundedness_score=0.995,
        traps_caught=1,
        node_traces=[{"stage": "critic_guardrail", "latency_ms": 250.0}]
    )
    raw_text = exporter.generate_prometheus_text()
    
    assert "# HELP strata_documents_processed_total" in raw_text
    assert "# TYPE strata_documents_processed_total counter" in raw_text
    assert "strata_guardrail_groundedness_ratio" in raw_text
    assert "strata_hallucination_traps_intercepted_total" in raw_text
    assert "strata_turnaround_time_savings_ratio 0.625" in raw_text

def test_api_metrics_endpoint(client):
    res = client.get("/api/metrics")
    assert res.status_code == 200
    assert "strata_documents_processed_total" in res.text
    assert "strata_evaluation_pass_rate_ratio 0.9920" in res.text

def test_api_metrics_summary_endpoint(client):
    res = client.get("/api/metrics/summary")
    assert res.status_code == 200
    data = res.json()
    assert data["pass_rate_sla"] == 0.992
    assert data["turnaround_reduction_pct"] == 62.5
    assert data["active_sla_status"] == "COMPLIANT_ZERO_DEFECT"

# ------------------------------------------------------------------------------
# 2. Dispute Resolution & Collaborative Annotation Tests
# ------------------------------------------------------------------------------
def test_dispute_resolution_recording_and_hash_integrity():
    manager = DisputeResolutionManager()
    entry = manager.record_resolution(
        job_id="job-audit-001",
        metric_name="operating_lease_liabilities",
        resolution_status="OVERRIDDEN",
        analyst_id="SeniorRiskAnalyst_42",
        review_notes="Verified against footnote 14 in raw filing; disclosure reflects ASC 842 adoption.",
        original_value="$12.5B",
        corrected_value="$14.2B",
        source_span="operating lease liabilities under ASC 842 of $14.2B"
    )

    assert entry["job_id"] == "job-audit-001"
    assert entry["status"] == "OVERRIDDEN"
    assert "audit_hash" in entry
    assert len(entry["audit_hash"]) == 64  # SHA-256 length

    # Verify cryptographic integrity
    is_valid = manager.verify_audit_hash(entry)
    assert is_valid is True

    # Altering content should break verification
    tampered_entry = dict(entry)
    tampered_entry["corrected_value"] = "$999B"
    assert manager.verify_audit_hash(tampered_entry) is False

def test_api_dispute_endpoints(client):
    payload = {
        "job_id": "api-job-99",
        "metric_name": "net_leverage",
        "status": "APPROVED",
        "analyst_id": "ComplianceOfficer_7",
        "review_notes": "Covenant confirmed within 3.25x maximum threshold."
    }
    res_post = client.post("/api/disputes/resolve", json=payload)
    assert res_post.status_code == 200
    data = res_post.json()
    assert data["status"] == "APPROVED"
    assert "audit_hash" in data

    # GET audit history
    res_get = client.get("/api/disputes/api-job-99")
    assert res_get.status_code == 200
    hist = res_get.json()
    assert hist["total_resolutions"] >= 1
    assert hist["resolutions"][0]["metric_name"] == "net_leverage"
