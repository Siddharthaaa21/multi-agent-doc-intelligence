# 📄 Module 04: Document Intelligence, Structural Chunking & Financial NLP Theory

## 1. The Challenge of Unstructured Institutional Filings

Unlike conversational text or Wikipedia articles, SEC filings (Form 10-K, 10-Q, 8-K) and institutional credit agreements present severe challenges for Natural Language Processing (NLP):
1. **Multimodal Information Mixing**: Dense prose narratives interspersed with 10-column financial tables, accounting schedules, and fine-print footnotes.
2. **Dense Domain Lexicon**: Complex terminology (*"senior secured floating-rate term loan B"*, *"non-amortizing revolvers"*, *"subordinated debentures"*).
3. **Restatements & Footnote Dependencies**: A headline revenue figure on page 12 is frequently adjusted, restated, or conditioned by footnote 4 on page 68.

---

## 2. Structural Chunking vs. Naive Fixed-Window Chunking

### The Failure of Naive Sliding Windows
Many generic RAG systems use fixed token chunking (e.g. 512 tokens with 50 token overlap). In financial document intelligence, this is fatal:

```
┌─────────────────────────────────────────────────────────────┐
│ NAIVE CHUNKING CUTOFF (Token 512)                           │
│                                                             │
│ Total Long-Term Debt: $97,800 million [CHUNK 1 ENDS]        │
│ ─────────────────────────────────────────────────────────── │
│ [CHUNK 2 BEGINS]                                            │
│ (1) Consists of $45,000 million in senior secured notes and │
│     $52,800 million maturing in 2026 under credit facility. │
└─────────────────────────────────────────────────────────────┘
```
- In Chunk 1, the model extracts \$97,800M debt without knowing its maturity or covenant terms.
- In Chunk 2, the model sees maturity dates without knowing which debt instrument they modify.

### Semantic / Structural Chunking
Our pipeline implements **Document-Aware Structural Chunking**:
1. **Section-Boundary Preservation**: Splits documents along canonical SEC filing headers:
   - `PART I, Item 1A: Risk Factors`
   - `PART II, Item 7: Management's Discussion and Analysis (MD&A)`
   - `PART II, Item 8: Financial Statements and Supplementary Data`
2. **Tabular Block Integrity**: Financial tables are extracted as unified markdown/tabular blocks rather than fragmented across line splits.
3. **Footnote Binding**: Cites and footnotes are appended directly to their referencing parent tables.

---

## 3. Financial Information Extraction (IE) Formulations

### A. Named Entity Recognition (NER) & Numerical Normalization
Financial text expresses numeric quantities with diverse lexical syntax:
- `"$391,035 million"`
- `"$391.04 billion"`
- `"€12.5M"`
- `"(4,200) thousand"` (GAAP accounting notation for negative \$4.2M)

The Ingestion Agent implements a **Canonical Normalization Mapping**:

$$\eta: \text{TokenString} \longrightarrow \mathbb{R}$$

$$\eta(\text{"\$391,035 million"}) = 391,035 \times 10^6 = 3.91035 \times 10^{11}$$
$$\eta(\text{"(4,200) thousand"}) = -4,200 \times 10^3 = -4.2 \times 10^6$$

This scalar conversion is essential so that the **Adversarial Critic** can execute exact mathematical assertions.

---

### B. Relation Extraction & Entity Disambiguation
Extracting a number is useless without its semantic attributes:
$$e_i = \langle \text{Entity}, \text{Metric}, \text{Value}, \text{Period}, \text{GAAP\_Status} \rangle$$

Example tuple:
$$\langle \text{"Apple Inc."}, \text{"Operating Income"}, \$123,216\text{M}, \text{"FY2024"}, \text{GAAP} \rangle$$

Without explicit period binding, models frequently compare Q3 revenue to Full-Year revenue, producing bogus growth rates.

---

## 4. Taxonomy Classification & Multi-Factor Risk Mapping

The Classifier Agent assigns each filing to an SEC reporting taxonomy and constructs a multi-factor risk vector:

### A. Filing Taxonomy Categorization
Let $\mathcal{X} = \{\text{10-K}, \text{10-Q}, \text{8-K}, \text{Credit Memo}, \text{Earnings Call Transcript}, \text{M\&A Memo}\}$.
The classification agent maps document tokens to a predicted category $\hat{y} \in \mathcal{X}$ with confidence score $p(\hat{y} \mid \mathcal{D})$.

### B. Multi-Factor Risk Vector ($\vec{r}$)
Risk factors from Item 1A are categorized into a 4-dimensional risk vector:

$$\vec{r} = \begin{bmatrix} r_{\text{liquidity}} \\ r_{\text{regulatory}} \\ r_{\text{market}} \\ r_{\text{operational}} \end{bmatrix}, \quad r_k \in [0.0, 1.0]$$

1. **Liquidity Risk ($r_{\text{liquidity}}$)**: Debt covenant headroom, short-term debt maturities, cash burn.
2. **Regulatory Risk ($r_{\text{regulatory}}$)**: Antitrust probes, SEC investigations, tax disputes.
3. **Market Risk ($r_{\text{market}}$)**: Interest rate sensitivity, foreign currency fluctuations, commodity inflation.
4. **Operational Risk ($r_{\text{operational}}$)**: Supply chain disruption, cybersecurity breaches, key-person dependencies.

### C. MD&A Sentiment Scoring
Management tone is quantified using a normalized sentiment polarity index:
$$S_{\text{MD\&A}} = \frac{N_{\text{positive}} - N_{\text{hedged}} - 2 \cdot N_{\text{litigation}}}{N_{\text{total\_tokens}}}$$
Hedged modal verbs (*"may"*, *"uncertain"*, *"could adversely affect"*) depress the sentiment score, directly alerting the committee to operational headwinds.
