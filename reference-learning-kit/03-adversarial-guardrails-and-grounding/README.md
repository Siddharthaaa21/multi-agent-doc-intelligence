# 🛡️ Module 03: Adversarial Critic Guardrails & Verifiable Metric Grounding

## 1. Why Probabilistic Models Need Deterministic Guardrails
Large Language Models generate text probabilistically: they maximize $P(w_t \mid w_{<t})$. They have no internal concept of accounting ledgers or SEC compliance.

In financial document intelligence:
- If a model summarizes an Apple 10-K and claims "Operating Margin was 32.5%" when the text says "Operating Margin was 31.2%", that 1.3% variance can alter a credit rating or discounted cash flow valuation by millions of dollars.
- Under **SEC Rule 10b-5**, distributing ungrounded or fabricated financial summaries creates direct regulatory and legal liability.

To build an enterprise-grade AI system, **probabilistic extraction must be surrounded by deterministic mathematical guardrails**.

---

## 2. The Verification Mathematics

### A. Character-Span Grounding
For each extracted claim $c_i = (\text{metric}, \text{value}, \text{source\_span})$:
$$\text{Grounding}(c_i) = \begin{cases} 1 & \text{if } \text{value} \in \text{source\_span} \text{ and } \text{source\_span} \subseteq \mathcal{D}_{\text{raw}} \\ 0 & \text{otherwise} \end{cases}$$

### B. Aggregate Groundedness Ratio ($\mathcal{G}$)
$$\mathcal{G} = \frac{1}{|C|} \sum_{i=1}^{|C|} \text{Grounding}(c_i)$$
- **Target SLA**: $\mathcal{G} \ge 95.0\%$.
- Any extraction batch scoring $< 95.0\%$ is rejected and routed to refinement.

### C. Arithmetic Invariant Audits
Accounting statements follow rigid mathematical invariants. The critic agent checks these invariants programmatically:
1. **Operating Margin Consistency**:
   $$\left| \text{Reported Margin} - \left( \frac{\text{Operating Income}}{\text{Total Revenue}} \right) \right| \le 0.005 \quad (\pm 0.5\%)$$
2. **Year-over-Year (YoY) Growth Consistency**:
   $$\left| \text{Reported YoY} - \left( \frac{\text{Revenue}_t - \text{Revenue}_{t-1}}{\text{Revenue}_{t-1}} \right) \right| \le 0.005$$

---

## 3. Adversarial Perturbation Traps (Red-Teaming)
To verify that the critic isn't rubber-stamping outputs, we inject **adversarial synthetic traps** into the evaluation suite:
- **Trap Type A (Value Mutation)**: Mutating \$391,035M to \$491,035M while leaving the cited span unchanged.
- **Trap Type B (Span Hallucination)**: Generating a plausible-sounding sentence ("EBITDA grew 14% due to cloud expansion") that does not exist in the raw document.
- **Trap Type C (Math Inconsistency)**: Reporting Operating Income of \$50M on \$100M revenue, but claiming a margin of 25% (instead of 50%).

The system enforces a **100% Hallucination Interception SLA**: every injected trap must be flagged and rejected.

---

## 4. How to Run the Example

Run the self-contained script:
```bash
python reference-learning-kit/03-adversarial-guardrails-and-grounding/runnable_critic_guardrail_example.py
```
This script runs character-span auditing, invariant arithmetic verification, and adversarial trap detection.
