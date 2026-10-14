# 🧪 Module 06: Pytest, Continuous Regression Harness & CI/CD SLA Gatekeeping

## 1. Why ML Engineers Must Learn Production Testing
In academic or experimental ML, models are evaluated by computing loss or accuracy on a test dataset. If accuracy drops from 94% to 92%, you might still accept it.

In **Institutional Financial AI Systems**, that attitude leads to disaster.
- If an engineer updates a system prompt to be "more concise", that prompt change might inadvertently cause the model to round \$14.8 billion down to \$14 billion on an Apple filing, or miss a subordinated debt clause in a Barclays credit memo.
- You cannot manually review hundreds of pages of filings after every git commit.

**The Solution:**
Build an **Automated Continuous Regression Evaluation Harness** executed in CI/CD before any code is merged.

---

## 2. Testing Hierarchy in AI Systems

```
              ┌─────────────────────────────┐
              │    Continuous Regression    │  ◄── Evaluates prompt robustness,
              │      Evaluation Harness     │      hallucination traps & SLA pass rate
              ├─────────────────────────────┤
              │     Integration Tests       │  ◄── Tests FastAPI endpoints, SSE streams,
              │  (TestClient / AsyncClient) │      and database transactions
              ├─────────────────────────────┤
              │        Unit Tests           │  ◄── Tests individual agents, parsers,
              │    (Pytest + Mocks)         │      and regex tokenizers in isolation
              └─────────────────────────────┘
```

---

## 3. The 99.2% Pass Rate SLA Assertion Architecture

The test harness evaluates **25 institutional scenarios**, checking 5 deterministic assertions per scenario ($25 \times 5 = 125$ total assertions):
1. **Completion Assertion**: Graph completed in status `COMPLETED` within timeout.
2. **Taxonomy Assertion**: Document type classification matched expected filing taxonomy (10-K, 10-Q, Credit Memo).
3. **Extraction Completeness**: Required financial entity count met ($\ge 3$ core line items).
4. **Groundedness SLA**: Calculated groundedness score $\mathcal{G} \ge 95.0\%$.
5. **Adversarial Trap Defense**: If a synthetic trap was injected, the critic flagged it and triggered self-correction; if clean, zero false positives.

$$\text{Pass Rate} = \frac{124}{125} = 99.2\% \quad (\text{Benchmark SLA Gate}: \ge 99.0\%)$$

If any pull request drops the pass rate below 99.0%, the CI pipeline exits with code `1`, blocking deployment.

---

## 4. How to Run the Example

Run the pytest suite:
```bash
python -m pytest reference-learning-kit/06-pytest-and-regression-sla-harness/runnable_sla_test_example.py -v
```
You will see pytest evaluate the benchmark cases, run all assertions, and verify that the 99.2% SLA threshold is satisfied.
