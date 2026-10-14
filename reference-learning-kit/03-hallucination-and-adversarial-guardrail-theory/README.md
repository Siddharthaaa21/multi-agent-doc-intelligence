# 🛡️ Module 03: The Mathematics of Hallucination & Adversarial Verification Guardrails

## 1. Epistemic Uncertainty in Autoregressive Token Generation

Large Language Models generate text sequentially by sampling from a conditional probability distribution:

$$P(y_1, y_2, \dots, y_T \mid x) = \prod_{t=1}^T P(y_t \mid y_{<t}, x)$$

### The Origin of Hallucination Drift
Autoregressive token generation does not query a deterministic database; it produces tokens that are **statistically probable** given prior context.

1. **Epistemic Uncertainty**: Arises from parameter compression. A 70B parameter model compresses trillions of tokens of web corpora into static weights. Detailed financial numbers (e.g. debt maturities in footnote 14) are rarely stored memorized in weights.
2. **Exposure Bias & Error Compounding**: If the model samples an erroneous digit at step $t$ (e.g. generating `4` instead of `3` in `391,035`), that incorrect token enters the conditioning prefix $y_{<t+1}$. The model subsequently conditions future tokens on its own mistake, resulting in **hallucination cascade**.

---

## 2. Taxonomy of Financial Hallucinations

```
                              FINANCIAL HALLUCINATIONS
                                         │
                 ┌───────────────────────┴───────────────────────┐
                 ▼                                               ▼
     [INTRINSIC HALLUCINATION]                       [EXTRINSIC HALLUCINATION]
     Direct contradiction of filing                  Fabrication of ungrounded facts
     • Swapping $391B revenue to $491B               • Inventing an unannounced merger
     • Changing debt maturity from 2026 to 2031      • Citing a non-existent bank facility
     • Inverting net margin (+12% to -12%)           • Fabricating management commentary
```

In institutional credit underwriting and risk analysis, **both intrinsic and extrinsic hallucinations violate SEC Rule 10b-5**, creating catastrophic liability for investment managers.

---

## 3. The Grounding Mathematics: Verbatim Span Verification

To eliminate hallucination, every extracted metric must be tied to a **verifiable coordinate span** in the raw document string $\mathcal{D}_{\text{raw}}$.

### Formal Coordinate Definition
Let $\mathcal{D}_{\text{raw}}$ be a sequence of unicode characters of length $L$:
$$\mathcal{D}_{\text{raw}} = [d_0, d_1, d_2, \dots, d_{L-1}]$$

An extraction claim $c_i = (k_i, v_i, s_i)$ consists of:
- $k_i \in \mathcal{K}$: Metric identifier (e.g. `Total Net Sales`)
- $v_i \in \mathbb{R}$: Extracted numeric scalar ($391035.0$)
- $s_i$: Cited text span string from the document

### Normalization Mapping ($\phi$)
Because PDFs and HTML filings contain irregular whitespace, line breaks, and typographic quotes, we apply an idempotent normalization homomorphism $\phi: \Sigma^* \to \Sigma^*$:
$$\phi(\text{text}) = \text{regex\_replace}(\text{r"\s+", " ", text.strip()})$$

### The Span Grounding Proof
A claim $c_i$ is proven grounded if and only if two deterministic conditions hold:

$$\text{SpanCheck}(c_i) = \mathbb{I}\left( \phi(s_i) \sqsubseteq \phi(\mathcal{D}_{\text{raw}}) \right)$$
$$\text{ValueCheck}(c_i) = \mathbb{I}\left( \text{format}(v_i) \sqsubseteq \phi(s_i) \lor \text{repr}(v_i) \sqsubseteq \phi(s_i) \right)$$

$$\text{Grounding}(c_i) = \text{SpanCheck}(c_i) \land \text{ValueCheck}(c_i)$$

Where $A \sqsubseteq B$ denotes that $A$ is a contiguous substring of $B$.

---

## 4. Algebraic Invariant Auditing (Accounting Consistency Proofs)

Financial filings are governed by the laws of double-entry bookkeeping and GAAP accounting equations. Even if a model quotes a real sentence, it may synthesize conflicting figures across different paragraphs.

The Adversarial Critic enforces **Deterministic Algebraic Invariant Audits**:

### Invariant 1: Operating Margin Consistency
$$\Delta_{\text{margin}} = \left| M_{\text{rep}} - \left( \frac{\text{Operating Income}}{\text{Total Revenue}} \times 100 \right) \right|$$
$$\text{InvariantSatisfied}_1 = \mathbb{I}\left( \Delta_{\text{margin}} \le \epsilon_{\text{margin}} \right) \quad (\epsilon_{\text{margin}} = 0.5\%)$$

### Invariant 2: Year-over-Year (YoY) Growth Consistency
$$\Delta_{\text{growth}} = \left| G_{\text{rep}} - \left( \frac{\text{Revenue}_t - \text{Revenue}_{t-1}}{\text{Revenue}_{t-1}} \times 100 \right) \right|$$
$$\text{InvariantSatisfied}_2 = \mathbb{I}\left( \Delta_{\text{growth}} \le \epsilon_{\text{growth}} \right) \quad (\epsilon_{\text{growth}} = 0.5\%)$$

### Invariant 3: Free Cash Flow (FCF) Identity
$$\text{FCF} = \text{Cash Flow from Operations (CFO)} - \text{Capital Expenditures (CapEx)}$$
$$\Delta_{\text{FCF}} = \left| \text{FCF}_{\text{rep}} - (\text{CFO} - \text{CapEx}) \right| \le 1.0 \text{ (USD Millions)}$$

If any invariant test evaluates to $0$, the critic flags an arithmetic discrepancy and forces the LangGraph state machine into the **Self-Correction Refinement Loop**.

---

## 5. Adversarial Red-Teaming & Synthetic Perturbation Theory

To prove that the evaluation test suite is not a "rubber stamp," we employ **Adversarial Red-Teaming**:

### Synthetic Perturbation Operators

1. **Numeric Mutation ($\mu_{\text{val}}$)**:
   Alters a valid financial scalar by a random perturbation factor $\alpha \in [1.1, 2.0]$:
   $$\mu_{\text{val}}(c_i) = (k_i, v_i \cdot \alpha, s_i)$$
   *Objective*: Ensures the critic catches when an LLM hallucinated a number while copying a true sentence.

2. **Counterfactual Span Insertion ($\mu_{\text{span}}$)**:
   Injects plausible-sounding financial disclosures generated by an adversarial model:
   $$s_{\text{trap}} = \text{"Free cash flow reached record highs of \$150,000 million in Q4."}$$
   $$\mu_{\text{span}}(c_i) = (k_i, v_i, s_{\text{trap}}) \quad \text{where } s_{\text{trap}} \not\subseteq \mathcal{D}_{\text{raw}}$$
   *Objective*: Proves that the span grounding check intercepts unanchored claims.

3. **Entity Transposition Trap ($\mu_{\text{entity}}$)**:
   Swaps values between competing corporate divisions (e.g. assigning Azure revenue to Google Cloud).

### The 100% Interception SLA Guarantee
The pipeline guarantees an **Adversarial Interception Rate** of:
$$H_{\text{catch}} = \frac{\sum_{t \in \mathcal{T}_{\text{traps}}} \mathbb{I}(\text{Flagged}(t) = \text{True})}{|\mathcal{T}_{\text{traps}}|} = 100.0\%$$
Zero tolerance: any uncaught hallucination trap fails the continuous regression CI pipeline.
