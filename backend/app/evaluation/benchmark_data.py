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
        "name": "Microsoft Corporation Form 10-Q (Q1 FY2025)",
        "doc_type": "10-Q (Quarterly Report)",
        "sector": "Enterprise Cloud & Software",
        "sample_file": "microsoft_10q_fy25.txt",
        "expected_metrics": {
            "Total Revenue": 65.59,
            "Gross Margin": 69.3,
            "Operating Income": 30.55,
            "Net Income": 24.67,
            "Free Cash Flow": 15.18
        },
        "has_synthetic_trap": False,
        "expected_groundedness_min": 0.98
    },
    {
        "case_id": "TC-08",
        "name": "Amazon.com Inc Form 10-K (FY2024)",
        "doc_type": "10-K (Annual Report)",
        "sector": "Cloud Infrastructure & E-Commerce",
        "sample_file": "amazon_10k_fy24.txt",
        "expected_metrics": {
            "Total Revenue": 620.13,
            "Operating Income": 68.42,
            "Net Income": 49.21,
            "Free Cash Flow": 47.70,
            "Total Debt": 58.30
        },
        "has_synthetic_trap": False,
        "expected_groundedness_min": 0.98
    },
    {
        "case_id": "TC-09",
        "name": "Amazon Web Services AWS Infrastructure Review",
        "doc_type": "10-K (Annual Report)",
        "sector": "Cloud Infrastructure & E-Commerce",
        "sample_file": "amazon_10k_fy24.txt",
        "expected_metrics": {
            "Total Revenue": 620.13,
            "Operating Income": 68.42,
            "Free Cash Flow": 47.70
        },
        "has_synthetic_trap": False,
        "expected_groundedness_min": 0.98
    },
    {
        "case_id": "TC-10",
        "name": "Microsoft Intelligent Cloud Segment Review",
        "doc_type": "10-Q (Quarterly Report)",
        "sector": "Enterprise Cloud & Software",
        "sample_file": "microsoft_10q_fy25.txt",
        "expected_metrics": {
            "Total Revenue": 65.59,
            "Operating Income": 30.55,
            "Free Cash Flow": 15.18
        },
        "has_synthetic_trap": False,
        "expected_groundedness_min": 0.98
    },
    {
        "case_id": "TC-11",
        "name": "Stripe Private Secondary Valuation Review",
        "doc_type": "M&A Investment Memo",
        "sector": "Fintech & Payments",
        "sample_file": "stripe_series_i_memo.txt",
        "expected_metrics": {
            "Net Revenue": 4.20,
            "Adjusted EBITDA": 1.15,
            "Free Cash Flow": 0.82
        },
        "has_synthetic_trap": False,
        "expected_groundedness_min": 0.98
    },
    {
        "case_id": "TC-12",
        "name": "Snowflake Inc. Net Revenue Retention Memo",
        "doc_type": "Earnings Call Transcript",
        "sector": "Data Intelligence & Cloud Analytics",
        "sample_file": "snowflake_earnings_transcript.txt",
        "expected_metrics": {
            "Total Revenue": 942.8,
            "Gross Margin": 69.5,
            "Free Cash Flow": 85.3
        },
        "has_synthetic_trap": False,
        "expected_groundedness_min": 0.98
    },
    {
        "case_id": "TC-13",
        "name": "JPMorgan Commercial Banking Facility Memo",
        "doc_type": "Credit Assessment Memo",
        "sector": "Transportation & Cold-Chain Logistics",
        "sample_file": "jpmorgan_credit_memo.txt",
        "expected_metrics": {
            "Total Revenue": 2840.0,
            "Adjusted EBITDA": 412.5,
            "Total Debt": 1180.0,
            "Free Cash Flow": 168.4
        },
        "has_synthetic_trap": False,
        "expected_groundedness_min": 0.98
    },
    {
        "case_id": "TC-14",
        "name": "Tesla Energy & Automotive Q3 Filing",
        "doc_type": "10-Q (Quarterly Report)",
        "sector": "Electric Mobility & Clean Energy",
        "sample_file": "tesla_10q_fy24.txt",
        "expected_metrics": {
            "Total Revenue": 25.18,
            "Gross Margin": 19.8,
            "Operating Income": 2.72,
            "Net Income": 2.17,
            "Free Cash Flow": 2.74
        },
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
        "name": "Snowflake Q3 FY2025 Data Cloud Assessment",
        "doc_type": "Earnings Call Transcript",
        "sector": "Data Intelligence & Cloud Analytics",
        "sample_file": "snowflake_earnings_transcript.txt",
        "expected_metrics": {
            "Total Revenue": 942.8,
            "Gross Margin": 69.5,
            "Free Cash Flow": 85.3
        },
        "has_synthetic_trap": False,
        "expected_groundedness_min": 0.98
    },
    {
        "case_id": "TC-17",
        "name": "Microsoft Cloud & AI Infrastructure Review",
        "doc_type": "10-Q (Quarterly Report)",
        "sector": "Enterprise Cloud & Software",
        "sample_file": "microsoft_10q_fy25.txt",
        "expected_metrics": {
            "Total Revenue": 65.59,
            "Operating Income": 30.55,
            "Net Income": 24.67
        },
        "has_synthetic_trap": False,
        "expected_groundedness_min": 0.98
    },
    {
        "case_id": "TC-18",
        "name": "Blackstone Real Estate Debt Underwriting Memo",
        "doc_type": "Credit Assessment Memo",
        "sector": "Commercial Real Estate & Private Credit",
        "sample_file": "blackstone_real_estate_memo.txt",
        "expected_metrics": {
            "Total Revenue": 420.0,
            "Total Debt": 1925.0,
            "Free Cash Flow": 118.5
        },
        "has_synthetic_trap": False,
        "expected_groundedness_min": 0.98
    },
    {
        "case_id": "TC-19",
        "name": "Amazon North America Logistics Review",
        "doc_type": "10-K (Annual Report)",
        "sector": "Cloud Infrastructure & E-Commerce",
        "sample_file": "amazon_10k_fy24.txt",
        "expected_metrics": {
            "Total Revenue": 620.13,
            "Operating Income": 68.42,
            "Net Income": 49.21
        },
        "has_synthetic_trap": False,
        "expected_groundedness_min": 0.98
    },
    {
        "case_id": "TC-20",
        "name": "Snowflake Enterprise RPO Backlog Analysis",
        "doc_type": "Earnings Call Transcript",
        "sector": "Data Intelligence & Cloud Analytics",
        "sample_file": "snowflake_earnings_transcript.txt",
        "expected_metrics": {
            "Total Revenue": 942.8,
            "Gross Margin": 69.5,
            "Free Cash Flow": 85.3
        },
        "has_synthetic_trap": False,
        "expected_groundedness_min": 0.98
    },
    {
        "case_id": "TC-21",
        "name": "Titan Logistics Syndicated Facility Review",
        "doc_type": "Credit Assessment Memo",
        "sector": "Transportation & Cold-Chain Logistics",
        "sample_file": "jpmorgan_credit_memo.txt",
        "expected_metrics": {
            "Total Revenue": 2840.0,
            "Adjusted EBITDA": 412.5,
            "Total Debt": 1180.0
        },
        "has_synthetic_trap": False,
        "expected_groundedness_min": 0.98
    },
    {
        "case_id": "TC-22",
        "name": "Adversarial Hallucination Injection Attack 4 (Fabricated EBITDA)",
        "doc_type": "M&A Investment Memo",
        "sector": "Fintech & Payments",
        "sample_file": "stripe_series_i_memo.txt",
        "has_synthetic_trap": True,
        "trap_description": "Injected synthetic claim: 'EBITDA surpassed $10.5B'",
        "expected_guardrail_catch": True,
        "expected_groundedness_min": 0.80
    },
    {
        "case_id": "TC-23",
        "name": "NVIDIA Hopper & CoWoS Supply Chain Audit",
        "doc_type": "10-Q (Quarterly Report)",
        "sector": "Semiconductors & AI Hardware",
        "sample_file": "nvidia_q2_fy25.txt",
        "expected_metrics": {
            "Total Revenue": 30.04,
            "Gross Margin": 75.1,
            "Operating Income": 18.64
        },
        "has_synthetic_trap": False,
        "expected_groundedness_min": 0.98
    },
    {
        "case_id": "TC-24",
        "name": "Tesla Megapack Storage & Cash Flow Review",
        "doc_type": "10-Q (Quarterly Report)",
        "sector": "Electric Mobility & Clean Energy",
        "sample_file": "tesla_10q_fy24.txt",
        "expected_metrics": {
            "Total Revenue": 25.18,
            "Operating Income": 2.72,
            "Free Cash Flow": 2.74
        },
        "has_synthetic_trap": False,
        "expected_groundedness_min": 0.98
    },
    {
        "case_id": "TC-25",
        "name": "Blackstone Logistics Floating-Rate SOFR Cap Review",
        "doc_type": "Credit Assessment Memo",
        "sector": "Commercial Real Estate & Private Credit",
        "sample_file": "blackstone_real_estate_memo.txt",
        "expected_metrics": {
            "Total Revenue": 420.0,
            "Total Debt": 1925.0,
            "Free Cash Flow": 118.5
        },
        "has_synthetic_trap": False,
        "expected_groundedness_min": 0.98
    }
]
