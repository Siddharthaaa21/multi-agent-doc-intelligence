#!/usr/bin/env python3
"""
Module 03: Runnable Adversarial Critic Guardrail & Grounding Auditor
Demonstrates:
1. Verbatim character span substring matching
2. Groundedness ratio calculation
3. Arithmetic invariant auditing (Operating Margin = Operating Income / Revenue)
4. Interception of synthetic adversarial hallucination traps
"""

import re
from typing import List, Dict, Any, Tuple
from pydantic import BaseModel, Field

# ==============================================================================
# 1. Claim & Report Models
# ==============================================================================

class ExtractedMetric(BaseModel):
    name: str
    reported_str: str
    numeric_value: float
    source_span: str
    unit: str = "USD_MILLIONS"

class AuditResult(BaseModel):
    total_claims: int
    grounded_claims: int
    groundedness_ratio: float
    arithmetic_violations: List[str]
    flagged_discrepancies: List[str]
    is_approved: bool

# ==============================================================================
# 2. Guardrail Auditor Implementation
# ==============================================================================

class FinancialGuardrailAuditor:
    def __init__(self, raw_document: str, threshold: float = 0.95):
        self.raw_doc = raw_document
        self.threshold = threshold

    def normalize(self, text: str) -> str:
        """Normalizes whitespace and typography for reliable matching."""
        return re.sub(r"\s+", " ", text).strip()

    def audit_span_grounding(self, claim: ExtractedMetric) -> Tuple[bool, str]:
        """
        Validates:
        1. source_span exists verbatim in raw_document
        2. numeric_value or reported_str is contained within source_span
        """
        norm_raw = self.normalize(self.raw_doc)
        norm_span = self.normalize(claim.source_span)

        if norm_span not in norm_raw:
            return False, f"Source span not found in raw filing text."

        # Check that the number appears in the cited sentence
        clean_num_str = f"{claim.numeric_value:g}"
        if clean_num_str not in norm_span and claim.reported_str not in norm_span:
            return False, f"Reported number '{claim.reported_str}' not present inside cited span."

        return True, "Valid span grounding"

    def audit_arithmetic_invariants(self, claims: List[ExtractedMetric]) -> List[str]:
        """
        Audits accounting invariants.
        Example: Operating Margin = Operating Income / Revenue (tolerance: ±0.5%)
        """
        violations = []
        metrics_by_name = {c.name.lower(): c.numeric_value for c in claims}

        revenue = metrics_by_name.get("revenue") or metrics_by_name.get("total net sales")
        op_income = metrics_by_name.get("operating income")
        op_margin = metrics_by_name.get("operating margin")

        if revenue and op_income and op_margin is not None:
            expected_margin = (op_income / revenue) * 100.0
            variance = abs(op_margin - expected_margin)
            if variance > 0.5:  # Tolerance: 0.5%
                violations.append(
                    f"Arithmetic Invariant Violation: Reported Operating Margin is {op_margin:.1f}%, "
                    f"but Operating Income ({op_income}) / Revenue ({revenue}) yields {expected_margin:.1f}% "
                    f"(Variance: {variance:.2f}%)"
                )

        return violations

    def evaluate(self, claims: List[ExtractedMetric]) -> AuditResult:
        if not claims:
            return AuditResult(
                total_claims=0,
                grounded_claims=0,
                groundedness_ratio=1.0,
                arithmetic_violations=[],
                flagged_discrepancies=["No claims provided"],
                is_approved=False
            )

        grounded_count = 0
        discrepancies = []

        for c in claims:
            is_valid, reason = self.audit_span_grounding(c)
            if is_valid:
                grounded_count += 1
            else:
                discrepancies.append(f"[{c.name}] FAILED: {reason} | Span: '{c.source_span}'")

        arithmetic_violations = self.audit_arithmetic_invariants(claims)
        discrepancies.extend(arithmetic_violations)

        ratio = grounded_count / len(claims)
        is_approved = (ratio >= self.threshold) and (len(arithmetic_violations) == 0)

        return AuditResult(
            total_claims=len(claims),
            grounded_claims=grounded_count,
            groundedness_ratio=round(ratio, 4),
            arithmetic_violations=arithmetic_violations,
            flagged_discrepancies=discrepancies,
            is_approved=is_approved
        )

# ==============================================================================
# 3. Demonstration & Adversarial Trap Testing
# ==============================================================================

if __name__ == "__main__":
    print("=" * 75)
    print("🛡️ Adversarial Critic Guardrail: Span Grounding & Invariant Audit Demo")
    print("=" * 75)

    raw_filing = """
    ITEM 7. MANAGEMENT'S DISCUSSION AND ANALYSIS OF FINANCIAL CONDITION
    During fiscal 2024, Total Net Sales were $391,035 million, an increase of 2% from fiscal 2023.
    Operating income was $123,216 million, representing an operating margin of 31.5%.
    Net income reached $93,736 million, resulting in diluted earnings per share of $6.08.
    Total long-term debt stood at $97,800 million.
    """

    auditor = FinancialGuardrailAuditor(raw_filing, threshold=0.95)

    # Test Case 1: 100% Grounded and Arithmetically Consistent Claims
    print("\n--- Test Scenario 1: Clean Extraction (Expected: APPROVED) ---")
    clean_claims = [
        ExtractedMetric(
            name="Total Net Sales",
            reported_str="$391,035 million",
            numeric_value=391035.0,
            source_span="Total Net Sales were $391,035 million, an increase of 2% from fiscal 2023."
        ),
        ExtractedMetric(
            name="Operating Income",
            reported_str="$123,216 million",
            numeric_value=123216.0,
            source_span="Operating income was $123,216 million, representing an operating margin of 31.5%."
        ),
        ExtractedMetric(
            name="Operating Margin",
            reported_str="31.5%",
            numeric_value=31.5,
            source_span="representing an operating margin of 31.5%."
        ),
        ExtractedMetric(
            name="Net Income",
            reported_str="$93,736 million",
            numeric_value=93736.0,
            source_span="Net income reached $93,736 million, resulting in diluted earnings per share of $6.08."
        ),
    ]

    res1 = auditor.evaluate(clean_claims)
    print(f"Groundedness Ratio: {res1.groundedness_ratio:.1%}")
    print(f"Arithmetic Violations: {len(res1.arithmetic_violations)}")
    print(f"Status Approved: {res1.is_approved}")
    assert res1.is_approved, "Test 1 should pass!"
    print("✓ Clean scenario passed flawlessly.")

    # Test Case 2: Adversarial Injection Traps (Hallucinated Span + Math Inconsistency)
    print("\n--- Test Scenario 2: Adversarial Traps Injected (Expected: REJECTED) ---")
    adversarial_claims = [
        ExtractedMetric(
            name="Total Net Sales",
            reported_str="$391,035 million",
            numeric_value=391035.0,
            source_span="Total Net Sales were $391,035 million, an increase of 2% from fiscal 2023."
        ),
        ExtractedMetric(
            name="Operating Income",
            reported_str="$123,216 million",
            numeric_value=123216.0,
            source_span="Operating income was $123,216 million, representing an operating margin of 31.5%."
        ),
        # TRAP A: Arithmetic Invariant Mismatch (Claims 45% when math says 31.5%)
        ExtractedMetric(
            name="Operating Margin",
            reported_str="45.0%",
            numeric_value=45.0,
            source_span="representing an operating margin of 31.5%."
        ),
        # TRAP B: Hallucinated metric with fabricated source span
        ExtractedMetric(
            name="Free Cash Flow",
            reported_str="$150,000 million",
            numeric_value=150000.0,
            source_span="Free cash flow surged to record highs of $150,000 million in Q4."
        )
    ]

    res2 = auditor.evaluate(adversarial_claims)
    print(f"Groundedness Ratio: {res2.groundedness_ratio:.1%}")
    print(f"Arithmetic Violations: {len(res2.arithmetic_violations)}")
    print(f"Status Approved: {res2.is_approved}")
    print("\nIntercepted Discrepancies:")
    for d in res2.flagged_discrepancies:
        print(f"  ❌ {d}")

    assert not res2.is_approved, "Adversarial trap MUST be rejected!"
    print("\n✅ Adversarial traps successfully intercepted by critic guardrails!")
    print("=" * 75)
