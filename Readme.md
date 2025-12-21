# Decomposed-Evidence-Consolidation-Adversarial-Fact-Checking

## Overview

This project implements a **decomposed, evidence-driven, adversarial fact-checking system** that verifies complex claims by breaking them into atomic subclaims and reasoning over competing evidence.

Instead of relying on single top-k evidence or collapsing predictions early, the system treats fact-checking as an **adversarial process** where *supporting and contradicting evidence explicitly compete*. Final decisions are made only after aggregating these opposing signals.

The system is modular, interpretable, and designed for research-oriented analysis rather than black-box prediction.

---

## Core Idea

**Fact-checking is framed as adversarial evidence consolidation.**

For each subclaim:
- evidence is evaluated for both *support* and *contradiction*
- opposing signals are aggregated and allowed to cancel each other
- unresolved disagreement is surfaced instead of hidden

This makes the system conservative, transparent, and suitable for controlled experimentation.

---

## High-Level Architecture

```
Claim 
  → Decomposer 
  → Subclaims 
  → Subclaim Pipeline 
      → Retrieval 
      → Reranking 
      → NLI Stance Scoring 
      → Evidence Aggregation 
      → Subclaim Verdict + Controversy 
  → Claim-Level Aggregation 
  → Final Claim Verdict
```

Each stage is implemented as a separate module with a clear responsibility.

---

## Claim Decomposer

### Purpose

The decomposer converts a **complex claim** into a small set of **atomic, independently verifiable subclaims**.

**Example:**

**Claim:**
> Transformers replaced recurrent models and improved NLP performance.

**Subclaims:**
- Self-attention replaced recurrence in NLP architectures
- Transformers enabled better parallelization
- Transformers improved performance over RNN-based models

### Design

- Produces short declarative subclaims
- No retrieval or verification at this stage
- Designed to be replaceable (prompt-based now, trainable later)

The decomposer defines the **reasoning granularity** of the system.

---

## Subclaim Verification Pipeline

Each subclaim is verified independently using the same pipeline:

```
Subclaim 
  → Dense Retrieval (FAISS) 
  → Cross-Encoder Reranking 
  → Sentence-Level NLI 
  → Evidence Aggregation 
  → Subclaim Verdict + Controversy
```

---

## Sentence-Level NLI (Stance Scoring)

- Model: `roberta-large-mnli`
- Input: `(evidence_sentence, subclaim)`
- Output: soft probabilities over:
  - support
  - contradict
  - neutral

Important design choice:
- **No hard stance labels are assigned here**
- All downstream reasoning uses soft probabilities

---

## Evidence Aggregation (Adversarial Core)

This is the central reasoning component.

For each evidence sentence:

```
stance_score = P(support) − P(contradict)
weighted_score = stance_score × rerank_score
```

Aggregation produces:
- `support_strength`
- `contradict_strength`
- `total_strength`

Additional details:
- Deduplication is done by sentence text
- Neutral evidences are kept as context but do not add strength
- Repeated evidence does not inflate signal

This explicitly models **support vs contradiction as opposing forces**.

---

## Subclaim Verdict Logic

Based on aggregated strengths, each subclaim is assigned one of:
- `SUPPORT`
- `CONTRADICT`
- `MIXED`
- `INCONCLUSIVE`

Decision principles:
- Weak overall signal → INCONCLUSIVE
- One side dominates → SUPPORT / CONTRADICT
- Strong evidence on both sides → MIXED

The verdict depends on **relative dominance**, not absolute thresholds.

---

## Controversy Detection (Adversarial Signal)

Controversy is a **separate signal**, not a verdict.

A subclaim is marked controversial if:
- verdict is `MIXED`, or
- both support and contradiction contribute meaningfully

This allows outputs such as:
> "Mostly supported, but disputed"

Rather than forcing certainty, disagreement is surfaced explicitly.

---

## Subclaim Pipeline Output

For each subclaim, the pipeline returns:
- verdict
- controversy flag
- aggregated strengths
- grouped evidence:
  - supporting
  - contradicting
  - neutral

Evidence metadata (sentence id, document id, source, credibility) is preserved for higher-level reasoning.

---

## Claim-Level Aggregation

After all subclaims are verified, results are consolidated at the claim level.

Claim-level reasoning considers:
- number of supported vs contradicted subclaims
- strength of evidence per subclaim
- presence of widespread controversy
- overlap of sources across subclaims

Final claim verdicts follow the same philosophy:
- dominance-based
- conservative under uncertainty
- transparent about disagreement

---

## Why This Is Adversarial Fact-Checking

Unlike confirmation-based systems that search only for supporting evidence, this system:
- explicitly evaluates evidence for *contradiction*
- aggregates opposing signals instead of filtering them
- bases decisions on dominance, not presence
- exposes unresolved disagreement via a controversy flag

Fact-checking is treated as a **contest between evidence**, not a retrieval task.

---

## Running the System

### Environment Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate   # Windows
pip install -r requirements.txt
```

### Running Subclaim Pipeline

```bash
python -m app.subclaim_pipeline
```

Example subclaim:
```
Self-attention replaced recurrence in NLP models
```

Expected behavior:
- Pipeline runs end-to-end
- Verdict may be MIXED
- Controversy may be True
- Evidence grouped without duplicates

---

## Evaluation Strategy

### Subclaim Level

Manual gold labels for subclaims

Metrics:
- verdict correctness
- controversy detection accuracy

Error analysis via confusion matrices

### Claim Level

Qualitative evaluation against known factual claims

Analysis of disagreement patterns

---

## Ablation Studies

Planned and supported ablations include:
- removing reranker weights
- using hard sentence labels instead of soft aggregation
- disabling deduplication
- limiting evidence to top-k only

These highlight the importance of adversarial aggregation.

---

## Known Limitations

- MNLI models over-predict contradiction
- Decomposer is prompt-based
- Deduplication is string-based
- Claim-level logic is heuristic

These are acknowledged and intentional for research scope.

---

## Future Work

The following are intentionally deferred:
- CRAG integration
- adversarial evidence retrieval
- semantic deduplication
- joint retriever–reranker training
- larger-scale automated evaluation

---

## Research Orientation Summary

This project emphasizes:
- interpretability over black-box accuracy
- explicit handling of contradiction
- modular reasoning layers
- reproducibility and extensibility

It is designed as a foundation for research-grade adversarial fact-checking systems, not as a production QA tool.