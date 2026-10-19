# 🤖 Module 02: Multi-Agent Systems Theory, State Machines & Cognitive Architectures

## 1. Why Single-Prompt LLMs Fail on Complex Documents

When building document intelligence pipelines, developers often start with a monolithic prompt:
> *"Read this 100-page 10-K filing. Extract all financial metrics, check the math, categorize the risks, and write an investment memo."*

In production, monolithic prompts fail catastrophically due to three foundational ML limitations:

### A. Attention Dilution & "Lost-in-the-Middle" (Liu et al., 2023)
Standard Transformer self-attention computes:
$$\text{Attention}(Q, K, V) = \text{softmax}\left(\frac{QK^T}{\sqrt{d_k}}\right)V$$
As sequence length $n$ increases (80+ pages of SEC filings), the attention distribution across tokens flattens. Models preferentially attend to the beginning and end of the context window, frequently missing critical covenant footnotes buried on page 47.

### B. Task Interference in Monolithic Prompts
Simultaneously forcing an LLM to perform syntactic parsing (regex/table layout), semantic reasoning (risk classification), arithmetic computation (operating margins), and stylistic summarization causes **parameter interference**. The model trades off numerical precision for conversational fluency.

### C. Inability to Self-Correct in Linear DAGs
Linear chains execute sequentially:
$$x_0 \xrightarrow{f_1} x_1 \xrightarrow{f_2} x_2 \xrightarrow{f_3} x_3$$
If $f_1$ extracts an incorrect debt figure, $f_2$ and $f_3$ have no theoretical mechanism to revisit $x_0$ and correct the error. **Compounding epistemic error** guarantees an ungrounded final memo.

---

## 2. Multi-Agent Systems as Partially Observable Markov Decision Processes (POMDPs)

To formalize autonomous multi-agent pipelines mathematically, we frame them as a **Decentralized POMDP**:

$$\mathcal{M} = \langle \mathcal{S}, \{\mathcal{A}_i\}, \mathcal{T}, \mathcal{R}, \{\Omega_i\}, \{\mathcal{O}_i\}, \gamma \rangle$$

Where:
- $\mathcal{S}$ is the **Global Document State**:
  $$\mathcal{S} = (\mathcal{D}_{\text{raw}}, \mathcal{C}_{\text{chunks}}, \mathcal{E}_{\text{metrics}}, \mathcal{G}_{\text{score}}, \mathcal{L}_{\text{logs}}, k_{\text{refine}})$$
- $\mathcal{A}_i$ is the **Action Space** of Agent $i$:
  - $\mathcal{A}_{\text{Ingestion}}$: Chunk document, extract raw candidate entity tuples $(k, v, s)$.
  - $\mathcal{A}_{\text{Classifier}}$: Assign filing taxonomy $\tau \in \{10\text{-K}, 10\text{-Q}, \text{Credit Memo}\}$ and risk vector $\vec{r}$.
  - $\mathcal{A}_{\text{Critic}}$: Compute groundedness $\mathcal{G}$ and verify arithmetic invariants.
  - $\mathcal{A}_{\text{Refinement}}$: Filter hallucinated entities and re-anchor text spans.
  - $\mathcal{A}_{\text{Synthesis}}$: Produce committee-grade briefing memorandum.
- $\Omega_i$ is the **Observation Space**: Agent $i$ does not receive the entire raw filing if unneeded; it observes only its relevant projection $\mathcal{O}_i(\mathcal{S})$.
- $\mathcal{T}(s' \mid s, a)$ is the **Deterministic State Transition Function**: Governed by LangGraph's StateGraph reducers.
- $\mathcal{R}(s, a)$ is the **Verification Reward**:
  $$\mathcal{R}(s) = \begin{cases} 1 & \text{if } \mathcal{G} \ge 0.95 \text{ and Invariants Satisfied} \\ -\lambda & \text{otherwise} \end{cases}$$

---

## 3. Cognitive Agent Persona Decomposition

By enforcing the **Principle of Single Responsibility**, agents operate with specialized system prompts and constrained token budgets:

```
┌───────────────────────────────────────────────────────────────────────────────────────┐
│                           THE MULTI-AGENT STATE GRAPH                                 │
│                                                                                       │
│   [START]                                                                             │
│      │                                                                                │
│      ▼                                                                                │
│  ┌─────────────────────────┐                                                          │
│  │ 1. Ingestion Agent      │ ──► High-precision tokenization, layout chunking,        │
│  └───────────┬─────────────┘     and verbatim text-span anchoring                     │
│              ▼                                                                        │
│  ┌─────────────────────────┐                                                          │
│  │ 2. Classifier Agent     │ ──► SEC taxonomy categorization & multi-factor           │
│  └───────────┬─────────────┘     risk extraction (MD&A sentiment scoring)             │
│              ▼                                                                        │
│  ┌─────────────────────────┐      Groundedness < 95%      ┌────────────────────────┐  │
│  │ 3. Critic Guardrail     │ ───────────────────────────► │ 4. Refinement Node     │  │
│  │    (Adversarial Node)   │ ◄─────────────────────────── │ (Purge Hallucinations) │  │
│  └───────────┬─────────────┘       (Max 2 Re-loops)       └────────────────────────┘  │
│              │                                                                        │
│              │ Groundedness ≥ 95%                                                     │
│              ▼                                                                        │
│  ┌─────────────────────────┐                                                          │
│  │ 5. Synthesis Agent      │ ──► C-Suite briefings, credit facility approval          │
│  └───────────┬─────────────┘     ratings, and high-conviction risk directives         │
│              │                                                                        │
│              ▼                                                                        │
│            [END]                                                                      │
└───────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 4. The Actor-Critic Paradigm in Agentic Workflows

In Reinforcement Learning, Actor-Critic architectures decouple policy generation from value evaluation:
- The **Actor** proposes an action $\pi_\theta(a \mid s)$.
- The **Critic** estimates the value $V_\phi(s)$ or advantage $A(s, a)$.

In our autonomous financial pipeline:
1. **Generative Actors** (`IngestionAgent`, `ClassifierAgent`):
   Propose extractions and semantic tags based on language models.
2. **Deterministic Critic** (`CriticGuardrail`):
   Computes exact string-span alignment and audits algebraic accounting equations.
3. **Refinement Policy** (`RefinementNode`):
   Executes conditional reflection if the critic's score falls below the threshold $\tau$:
   $$\Delta \mathcal{S} = \text{Refine}(\mathcal{S}, \text{Discrepancies})$$

---

## 5. Convergence, Recursion Limits & Halting Guarantees

In cyclic state graphs, a critical theoretical failure mode is the **Infinite Loop / Divergence Hazard**:
- An agent makes a mistake $\to$ routes to refinement $\to$ re-extracts an invalid metric $\to$ routes to critic $\to$ loops infinitely.

### Formal Halting Guarantee
To guarantee that the state graph terminates in finite time ($|\text{Steps}| < \infty$), we enforce a **monotonically incrementing cycle counter** $k \in \mathbb{N}$:

$$\text{NextNode}(s) = \begin{cases} 
\text{SynthesisAgent} & \text{if } \mathcal{G}(s) \ge \tau \\ 
\text{RefinementNode} & \text{if } \mathcal{G}(s) < \tau \text{ and } k < k_{\max} \\ 
\text{SynthesisAgent (Variance Mode)} & \text{if } \mathcal{G}(s) < \tau \text{ and } k \ge k_{\max} 
\end{cases}$$

Where $k_{\max} = 2$.
- If discrepancies cannot be resolved after 2 cyclic iterations, the system gracefully degrades: it flags an annotated variance notice to human analysts rather than consuming unbounded compute.
- This guarantees termination with computational complexity bounded by $\mathcal{O}(k_{\max} \cdot |V|)$.
