# 🧠 Machine Learning & Multi-Agent Theory Reference Kit
### Autonomous Document Intelligence & Financial Risk Orchestrator

This reference kit provides **pure conceptual, mathematical, and algorithmic documentation** designed to establish deep domain mastery before writing or modifying any implementation code.

If you are an engineer or researcher with a machine learning background, this curriculum focuses on **evaluation theory, mathematical formulations, agentic state-machine dynamics, and continuous regression testing**.

---

## 🗺️ Conceptual Syllabus & Theory Modules

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                               THEORETICAL FOUNDATIONS                                  │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ [Module 01: ML Evaluation Theory, Formulations & Testing Methodology]                  │
│ • Mathematical definitions: Precision, Recall, F1, Groundedness Ratio, Faithfulness   │
│ • Why N-gram metrics (BLEU/ROUGE) fail on financial filings                            │
│ • Deterministic assertion suites vs. stochastic LLM-as-a-judge                        │
│ • Stratified golden benchmark dataset creation & inter-annotator agreement (Kappa)     │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ [Module 02: Multi-Agent Systems Theory, State Machines & Cognitive Architectures]      │
│ • Why single-prompt LLMs fail: Context window saturation & Attention Dilution          │
│ • Mathematical formalism: Agent pipelines as Partially Observable MDPs (POMDPs)       │
│ • The Actor-Critic paradigm in agentic workflows                                       │
│ • Cyclic state graphs, self-healing reflection, and finite halting guarantees          │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ [Module 03: The Mathematics of Hallucination & Adversarial Verification Guardrails]    │
│ • Epistemic uncertainty, exposure bias, and compounding hallucination drift            │
│ • Coordinate-based character-span grounding mathematics                                │
│ • Algebraic invariant auditing (Operating Margin, YoY Growth, Free Cash Flow)          │
│ • Adversarial red-teaming: Synthetic perturbation operators & 100% interception SLAs   │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ [Module 04: Document Intelligence, Structural Chunking & Financial NLP Theory]         │
│ • Multimodal challenges of SEC Form 10-K, 10-Q, 8-K filings                            │
│ • Structural chunking vs. naive fixed-size window chunking (context boundary loss)     │
│ • Information extraction (IE): Canonical numerical scalar normalization               │
│ • Multi-factor risk mapping & MD&A management sentiment analysis                       │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ [Module 05: Project Architecture, SLA Engineering & Resume Deconstruction]             │
│ • Mathematical deconstruction of the project resume claims                             │
│ • Turnaround time reduction analysis: 300s baseline vs. 1.84s pipeline (62.5% savings) │
│ • The 25 institutional benchmark scenarios breakdown                                   │
│ • The 124/125 assertions = 99.2% pass rate math (Why TC-15 creates 1 deliberate error) │
│ • The SLI ➔ SLO ➔ SLA institutional contract hierarchy                                │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 📚 Module Directory Links

1. **[Module 01: ML Evaluation Theory, Formulations & Testing Methodology](./01-ml-evaluation-theory-and-metrics/README.md)**
   *Formulas: Entity Precision, Entity Recall, $F_1$, Groundedness Ratio $\mathcal{G}$, Hallucination Drift $D_H$, Pass Rate $\mathcal{P}_{\text{suite}}$, Turnaround Reduction $T_{\text{reduction}}$.*

2. **[Module 02: Multi-Agent Systems Theory, State Machines & Cognitive Architectures](./02-multi-agent-systems-theory/README.md)**
   *Theory: POMDP formulation $\langle \mathcal{S}, \mathcal{A}, \mathcal{T}, \mathcal{R}, \Omega, \mathcal{O}, \gamma \rangle$, attention degradation, Actor-Critic agentic loops, cyclic self-healing, finite halting bounds.*

3. **[Module 03: The Mathematics of Hallucination & Adversarial Verification Guardrails](./03-hallucination-and-adversarial-guardrail-theory/README.md)**
   *Formulas: Substring grounding proofs $\phi(s_i) \sqsubseteq \phi(\mathcal{D}_{\text{raw}})$, algebraic margin invariants $|\Delta| \le \epsilon$, adversarial mutation operators $\mu(c)$, 100% trap interception.*

4. **[Module 04: Document Intelligence, Structural Chunking & Financial NLP Theory](./04-document-intelligence-and-nlp-theory/README.md)**
   *Theory: Section header parsing (Item 1A, Item 7, Item 8), tabular block preservation, numerical normalization $\eta(\text{token})$, multi-factor risk vectors $\vec{r} \in [0, 1]^4$, MD&A sentiment scoring.*

5. **[Module 05: Project Architecture, SLA Engineering & Resume Deconstruction](./05-project-architecture-and-sla-deep-dive/README.md)**
   *Deep Dive: The 5 agent personas, the 25 benchmark filings, the 125 assertions breakdown, why Case TC-15 yields 99.2% pass rate, and how CI/CD enforces contractual zero-defect SLAs.*

---

## 🎯 Conceptual Questions to Master Before Building

Before writing or modifying implementation code, ensure you can conceptually answer:
1. **Why does ROUGE/BLEU fail completely for financial extraction?**
   *(See Module 01: Negation inversion creates high token overlap despite opposite financial meaning).*
2. **Why do linear LangChain pipelines suffer from exponential hallucination compounding?**
   *(See Module 02: $D_H^{(t)} \approx 1 - (1-\delta)^t$; without a cyclic critic, errors compound at each step).*
3. **How does the system mathematically prove a number is not hallucinated?**
   *(See Module 03: By verifying character-span containment $s_i \subseteq \mathcal{D}_{\text{raw}}$ and algebraic accounting equations).*
4. **Why does naive sliding-window chunking destroy financial tables?**
   *(See Module 04: It decouples header definitions from numerical cells and footnotes).*
5. **How is the 99.2% pass rate calculated across the 25 benchmark cases?**
   *(See Module 05: 25 cases $\times$ 5 assertions = 125 assertions. Case TC-15 introduces 1 intentional non-fatal variance; $124/125 = 99.2\%$).*
