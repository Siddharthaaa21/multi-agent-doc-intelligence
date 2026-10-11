from typing import List, Dict, Any

BENCHMARK_CASES: List[Dict[str, Any]] = [
    {
        "case_id": "TC-01",
        "name": "Apple Inc. Form 10-K (FY2024)",
        "doc_type": "10-K (Annual Report)",
        "sector": "Technology / Consumer Hardware",
        "sample_file": "apple_10k_fy24.txt",
        "expected_metrics": {
            "Total Revenue": 94.93,
            "Operating Margin": 30.5,
            "Net Income": 21.45,
            "Gross Margin": 46.2,
            "Adjusted EBITDA": 32.10
        },
        "has_synthetic_trap": False,
        "expected_groundedness_min": 0.98
    },
    {
        "case_id": "TC-02",
        "name": "NVIDIA Corporation Form 10-Q (Q2 FY2025)",
        "doc_type": "10-Q (Quarterly Report)",
        "sector": "Semiconductors & AI Hardware",
        "sample_file": "nvidia_q2_fy25.txt",
        "expected_metrics": {
            "Total Revenue": 30.04,
            "Gross Margin": 75.1,
            "Operating Income": 18.64,
            "Adjusted EBITDA": 19.45,
            "Net Income": 16.60
        },
        "has_synthetic_trap": False,
        "expected_groundedness_min": 0.98
    },
    {
        "case_id": "TC-03",
        "name": "Stripe Inc. Series I Investment Memo",
        "doc_type": "M&A Investment Memo",
        "sector": "Fintech & Payments",
        "sample_file": "stripe_series_i_memo.txt",
        "expected_metrics": {
            "Net Revenue": 4.20,
            "Gross Margin": 78.4,
            "Adjusted EBITDA": 1.15,
            "Free Cash Flow": 0.82
        },
        "has_synthetic_trap": False,
        "expected_groundedness_min": 0.97
    },
    {
        "case_id": "TC-04",
        "name": "Barclays Corporate Credit Underwriting Memo",
        "doc_type": "Credit Assessment Memo",
        "sector": "Banking & Corporate Lending",
        "sample_file": "barclays_credit_memo.txt",
        "expected_metrics": {
            "Total Revenue": 840.5,
            "Adjusted EBITDA": 112.4,
            "Total Debt": 315.0,
            "Free Cash Flow": 45.7
        },
        "has_synthetic_trap": False,
        "expected_groundedness_min": 0.98
    },
    {
        "case_id": "TC-05",
        "name": "Adversarial Hallucination Injection Attack 1 (Invented TAM)",
        "doc_type": "10-K (Annual Report)",
        "sector": "Technology",
        "sample_file": "apple_10k_fy24.txt",
        "has_synthetic_trap": True,
        "trap_description": "Injected synthetic claim: 'Projected TAM $500B by 2030'",
        "expected_guardrail_catch": True,
        "expected_groundedness_min": 0.80
    },
    {
        "case_id": "TC-06",
        "name": "Adversarial Hallucination Injection Attack 2 (Exaggerated Margin)",
        "doc_type": "10-Q (Quarterly Report)",
        "sector": "Semiconductors",
        "sample_file": "nvidia_q2_fy25.txt",
        "has_synthetic_trap": True,
        "trap_description": "Injected synthetic claim: 'Operating margin exceeded 98.4%'",
        "expected_guardrail_catch": True,
        "expected_groundedness_min": 0.80
    },
    {
        "case_id": "TC-07",
        "name": "Microsoft Cloud Azure Earnings Release",
        "doc_type": "10-Q (Quarterly Report)",
        "sector": "Enterprise Cloud Software",
        "has_synthetic_trap": False,
        "expected_groundedness_min": 0.98
    },
    {
        "case_id": "TC-08",
        "name": "Alphabet Inc. Search & YouTube 10-K Excerpt",
        "doc_type": "10-K (Annual Report)",
        "sector": "Digital Advertising & Cloud",
        "has_synthetic_trap": False,
        "expected_groundedness_min": 0.98
    },
    {
        "case_id": "TC-09",
        "name": "Amazon Web Services AWS Infrastructure Review",
        "doc_type": "10-K (Annual Report)",
        "sector": "E-Commerce & Cloud Infrastructure",
        "has_synthetic_trap": False,
        "expected_groundedness_min": 0.98
    },
    {
        "case_id": "TC-10",
        "name": "Salesforce Inc. CRM Annual Report",
        "doc_type": "10-K (Annual Report)",
        "sector": "Enterprise SaaS",
        "has_synthetic_trap": False,
        "expected_groundedness_min": 0.98
    },
    {
        "case_id": "TC-11",
        "name": "Databricks Private Secondary Valuation Review",
        "doc_type": "M&A Investment Memo",
        "sector": "Data Intelligence & AI",
        "has_synthetic_trap": False,
        "expected_groundedness_min": 0.98
    },
    {
        "case_id": "TC-12",
        "name": "Snowflake Inc. Net Revenue Retention Memo",
        "doc_type": "Earnings Call Transcript",
        "sector": "Cloud Data Warehousing",
        "has_synthetic_trap": False,
        "expected_groundedness_min": 0.98
    },
    {
        "case_id": "TC-13",
        "name": "JPMorgan Chase Commercial Banking Facility Memo",
        "doc_type": "Credit Assessment Memo",
        "sector": "Banking & Syndicated Finance",
        "has_synthetic_trap": False,
        "expected_groundedness_min": 0.98
    },
    {
        "case_id": "TC-14",
        "name": "Tesla Energy & Automotive Q3 Filing",
        "doc_type": "10-Q (Quarterly Report)",
        "sector": "Automotive & Clean Energy",
        "has_synthetic_trap": False,
        "expected_groundedness_min": 0.98
    },
    {
        "case_id": "TC-15",
        "name": "Adversarial Hallucination Injection Attack 3 (Negative Debt Token)",
        "doc_type": "Credit Assessment Memo",
        "sector": "Banking",
        "sample_file": "barclays_credit_memo.txt",
        "has_synthetic_trap": True,
        "trap_description": "Injected synthetic debt covenant violation figure",
        "expected_guardrail_catch": True,
        "expected_groundedness_min": 0.80
    },
    {
        "case_id": "TC-16",
        "name": "CrowdStrike Cybersecurity ARR Assessment",
        "doc_type": "10-Q (Quarterly Report)",
        "sector": "Cybersecurity",
        "has_synthetic_trap": False,
        "expected_groundedness_min": 0.98
    },
    {
        "case_id": "TC-17",
        "name": "Broadcom VMWare Acquisition Integration Memo",
        "doc_type": "M&A Investment Memo",
        "sector": "Semiconductors & Infrastructure Software",
        "has_synthetic_trap": False,
        "expected_groundedness_min": 0.98
    },
    {
        "case_id": "TC-18",
        "name": "Blackstone Real Estate Credit Trust Memo",
        "doc_type": "Credit Assessment Memo",
        "sector": "Commercial Real Estate Credit",
        "has_synthetic_trap": False,
        "expected_groundedness_min": 0.98
    },
    {
        "case_id": "TC-19",
        "name": "ServiceNow Now Platform Operational Review",
        "doc_type": "10-K (Annual Report)",
        "sector": "Enterprise Workflow Automation",
        "has_synthetic_trap": False,
        "expected_groundedness_min": 0.98
    },
    {
        "case_id": "TC-20",
        "name": "Palo Alto Networks Next-Gen Security Earnings",
        "doc_type": "Earnings Call Transcript",
        "sector": "Cybersecurity",
        "has_synthetic_trap": False,
        "expected_groundedness_min": 0.98
    },
    {
        "case_id": "TC-21",
        "name": "Goldman Sachs Corporate Treasury Facility",
        "doc_type": "Credit Assessment Memo",
        "sector": "Investment Banking & Capital Markets",
        "has_synthetic_trap": False,
        "expected_groundedness_min": 0.98
    },
    {
        "case_id": "TC-22",
        "name": "Adversarial Hallucination Injection Attack 4 (Fabricated EBITDA)",
        "doc_type": "M&A Investment Memo",
        "sector": "Fintech",
        "sample_file": "stripe_series_i_memo.txt",
        "has_synthetic_trap": True,
        "trap_description": "Injected synthetic claim: 'EBITDA surpassed $10.5B'",
        "expected_guardrail_catch": True,
        "expected_groundedness_min": 0.80
    },
    {
        "case_id": "TC-23",
        "name": "Qualcomm CDMA Technologies Quarterly Filing",
        "doc_type": "10-Q (Quarterly Report)",
        "sector": "Mobile & Wireless Semiconductors",
        "has_synthetic_trap": False,
        "expected_groundedness_min": 0.98
    },
    {
        "case_id": "TC-24",
        "name": "SpaceX Commercial Satellite Operations Review",
        "doc_type": "M&A Investment Memo",
        "sector": "Aerospace & Satellite Communications",
        "has_synthetic_trap": False,
        "expected_groundedness_min": 0.98
    },
    {
        "case_id": "TC-25",
        "name": "Uber Technologies Mobility & Delivery Filing",
        "doc_type": "10-K (Annual Report)",
        "sector": "Consumer Platforms & Logistics",
        "has_synthetic_trap": False,
        "expected_groundedness_min": 0.98
    }
]
