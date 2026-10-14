# 📑 Module 07: Financial Document Intelligence Domain Guide for SDEs

## 1. Why Financial NLP is High-Stakes
Unlike consumer chatbots (where a conversational summary can be slightly creative), **institutional financial document intelligence has zero tolerance for ambiguity**:
- If an autonomous agent extracts \$45.2M instead of \$45.2B, or assigns a 28% margin instead of 18%, an investment committee or credit underwriting desk could approve a multi-million dollar loan under invalid debt covenant assumptions.
- Under **SEC Rule 10b-5**, distributing ungrounded or misleading financial analysis can trigger securities fraud investigations, regulatory fines, and catastrophic reputational damage.

---

## 2. Anatomy of SEC Filings

| Filing Type | Frequency | Audit Status | Key Content & Purpose |
| :--- | :--- | :--- | :--- |
| **Form 10-K** | Annual | **Audited** (by independent CPA) | Comprehensive annual summary: audited financials, risk factors, executive compensation, debt disclosures, and full MD&A. |
| **Form 10-Q** | Quarterly (Q1, Q2, Q3) | **Unaudited** (reviewed) | Quarterly update on operations, seasonal trends, and updated liquidity. |
| **Form 8-K** | Unscheduled | Event-driven | Major material events: executive departures, M&A announcements, cyber breaches, bankruptcy, covenant defaults. |
| **Credit Memo** | Deal-driven | Internal Institutional | Loan underwriting analysis, debt service coverage, collateral valuation, and covenant restrictions. |

---

## 3. Key Sections Every AI Engineer Must Know

```
FORM 10-K / 10-Q STRUCTURE
├── PART I
│   ├── Item 1. Business
│   ├── Item 1A. Risk Factors            ◄── Extracted by Taxonomy & Risk Classifier
│   └── Item 1B. Unresolved Staff Comments
├── PART II
│   ├── Item 7. MD&A                     ◄── Management's Discussion & Analysis
│   │                                        (Extracted for executive sentiment & trends)
│   ├── Item 7A. Quantitative & Qualitative Disclosures About Market Risk
│   └── Item 8. Financial Statements     ◄── Extracted by Ingestion & Critic Guardrails
│       ├── Consolidated Statements of Operations (Income Statement)
│       ├── Consolidated Balance Sheets
│       ├── Consolidated Statements of Cash Flows
│       └── Footnotes to Financial Statements (Debt covenants, restatements)
└── PART III & IV (Corporate governance, exhibits)
```

---

## 4. Fundamental Financial Metrics & Invariant Equations

### A. Income Statement Metrics
1. **Total Net Sales / Revenue ($R$)**: Top-line inflow from goods/services.
2. **Gross Profit ($GP$)**: $\text{Revenue} - \text{Cost of Goods Sold (COGS)}$.
3. **Operating Income ($OI$ / EBIT)**: $\text{Gross Profit} - \text{Operating Expenses (R&D, SG&A)}$.
4. **Operating Margin ($\text{OM}$)**:
   $$\text{Operating Margin} = \frac{\text{Operating Income}}{\text{Total Revenue}}$$
5. **Net Income ($NI$)**: Bottom-line profit after interest and taxes.

---

### B. Cash Flow & Profitability Metrics
1. **EBITDA**: $\text{Operating Income} + \text{Depreciation} + \text{Amortization}$.
2. **Adjusted EBITDA (Non-GAAP)**: EBITDA adjusted for one-time restructuring costs and stock-based compensation (SBC).
3. **Free Cash Flow (FCF)**:
   $$\text{Free Cash Flow} = \text{Operating Cash Flow} - \text{Capital Expenditures (CapEx)}$$

---

### C. Credit Underwriting & Covenant Ratios
1. **Leverage Ratio**:
   $$\text{Leverage} = \frac{\text{Total Debt}}{\text{EBITDA}}$$
   *Typical Covenant Ceiling*: $\le 3.5\times$ to $4.0\times$. Exceeding this triggers a technical default.
2. **Interest Coverage Ratio**:
   $$\text{Interest Coverage} = \frac{\text{EBITDA}}{\text{Interest Expense}}$$
   *Typical Covenant Floor*: $\ge 3.0\times$. Falling below this triggers credit downgrade.

---

## 5. Engineer's Checklist for Prompt & Guardrail Design

When designing prompts and extraction nodes for financial documents:
- [ ] **Enforce Exact Character Spans**: Always force the LLM to return `source_span` quoting the verbatim sentence from the filing.
- [ ] **Separate GAAP from Non-GAAP**: Never compare GAAP Net Income directly against Non-GAAP Adjusted EBITDA without explicit labeling.
- [ ] **Check Reporting Periodicity**: Ensure figures compare FY2024 to FY2023, not Q3 to FY2023.
- [ ] **Validate Invariants**: Programmatically compute $\text{Operating Income} / \text{Revenue}$ and reject any LLM-reported margin that deviates by $> 0.5\%$.
- [ ] **Preserve Footnote Disclosures**: Covenants and restatements live in footnotes (Item 8), not the main text.
