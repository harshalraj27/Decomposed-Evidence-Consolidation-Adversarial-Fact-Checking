# Decomposed Evidence Consolidation Adversarial Fact-Checking

## Overview

This project implements a decomposed, evidence-driven, adversarial fact-checking system for verifying complex factual claims. Instead of treating fact-checking as a single retrieval or classification task, the system explicitly models **supporting and contradicting evidence as competing signals**.

A claim is decomposed into atomic subclaims, each subclaim is verified independently, and final decisions are produced only after aggregating opposing evidence.

### Research-Oriented Design Principles

The system is research-oriented by design:

- **Explanations matter more than verdicts**
- **Disagreement is surfaced, not hidden**
- **Uncertainty is a valid outcome**
- **Every architectural decision is inspectable and ablatable**

> **Note:** This is not a production QA system.

---

## Core Idea

Fact-checking is framed as **adversarial evidence consolidation**.

For each subclaim:

- Evidence is evaluated for support and contradiction
- Opposing signals are accumulated instead of filtered
- Weak or neutral evidence is preserved as context
- Unresolved disagreement is explicitly surfaced

Final verdicts depend on **relative dominance of evidence**, not the presence of a single strong sentence.

---

## High-Level Architecture

```
Claim
  → Decomposer
    → Subclaims
      → Subclaim Pipeline
        → Dense Retrieval (FAISS)
        → Cross-Encoder Reranking
        → NLI Stance Scoring
        → Evidence Aggregation
        → Subclaim Verdict
      → Claim-Level Aggregation
        → Final Claim Verdict + Explanation
```

Each stage has a **single, explicit responsibility** and can be evaluated or ablated independently.

---

## Repository Structure

```
ml-service/
├── app/
│   ├── claim_pipeline.py           # Claim-level wrapper (main API)
│   ├── subclaim_pipeline.py        # Per-subclaim verification
│   ├── llm_decomposer.py           # LLM-based claim decomposition
│   ├── rule_decomposer.py          # Heuristic decomposition gate
│   ├── search.py                   # FAISS dense retrieval
│   ├── reranker.py                 # Cross-encoder reranking
│   ├── stance_classifier.py        # NLI stance scoring (MNLI)
│   ├── stance_aggregator.py        # Adversarial signal aggregation
│   ├── subclaim_verdict.py         # Subclaim verdict logic
│   ├── build_metadata.py           # Sentence-level metadata builder
│   ├── build_index.py              # FAISS index construction
│   ├── online_ingestion.py         # Source-specific ingestion logic
│   ├── pdf_to_text.py              # arXiv PDF → text → metadata
│   ├── schemas.py                  # Output / error schemas
│   ├── claim_pipeline_eval/        # Evaluation & ablation scripts
│   └── peft/                       # PEFT experiments (deferred)
│
├── data/
│   ├── local_curated/              # Manually curated sources
│   ├── ingested/                   # Online ingested sources
│   │   ├── pdf/
│   │   ├── raw/
│   │   ├── cleaned/
│   │   └── meta/
│   ├── metas.jsonl                 # Sentence-level metadata store
│   └── index.faiss                 # FAISS vector index
│
├── run_online_ingestion.py         # Interactive ingestion runner
├── run_claim_pipeline.py           # Interactive claim verification runner
├── requirements.txt
└── README.md
```

---

## Environment Setup

**GPU is strongly recommended.** The system uses sentence transformers, cross-encoders, and MNLI models. CPU execution is possible but slow and not the intended mode.

### Installation Steps

```bash
python -m venv .venv
source .venv/bin/activate  # Linux / Mac
# .venv\Scripts\activate   # Windows

pip install -r requirements.txt
```

### Additional Requirements

You will also need the spaCy model:

```bash
python -m spacy download en_core_web_lg
```

---

## Data & Corpus Design

The system **does not accept arbitrary user uploads**. All evidence must come from:

- Manually curated sources (`data/local_curated/`)
- Admin-controlled online ingestion (Wikipedia, arXiv, PubMed, OpenReview)

### Why This Constraint?

This constraint is intentional:

- Ensures reproducibility
- Avoids noisy or adversarial inputs
- Keeps evaluation controlled

Downstream components do not distinguish between local and online sources.

---

## Metadata Construction

All documents are ultimately converted into **sentence-level metadata** stored in:

```
data/metas.jsonl
```

Each sentence is assigned:

- A stable ID
- Source metadata
- Credibility score
- Document provenance

### Building Metadata from Local Sources

1. Place `.txt`, `.md`, or `.csv` files inside:
   ```
   data/local_curated/
   ```

2. Run:
   ```bash
   python -m app.build_metadata
   ```

This step:

- Traverses directories recursively
- Splits text into sentences
- Filters noisy or malformed sentences
- Assigns stable sentence IDs
- Writes metadata to `metas.jsonl`

---

## Online Ingestion (Admin / Research Use)

Online ingestion is interactive and controlled via:

```bash
python run_online_ingestion.py
```

You will be prompted to select a source:

1. arxiv
2. wikipedia
3. pubmed
4. openreview

### arXiv Ingestion

- Fetches papers by category
- Downloads PDFs
- Writes source metadata
- Automatically runs PDF → text → sentence metadata
- **No manual post-processing step is required**

### Wikipedia Ingestion

- Fetches full article content
- Drops non-content sections
- Assigns heuristic credibility
- Passes text directly to metadata builder

### PubMed Ingestion

- Fetches abstracts (optionally PMC full text)
- Applies length and quality filters
- Stores biomedical metadata and credibility

### OpenReview Ingestion

- Fetches submissions from a venue invitation
- Optionally includes reviews
- Stores structured metadata and text

**All online ingestion paths end by calling `build_metadata`.**

---

## FAISS Index Construction

After any ingestion (local or online), rebuild the vector index:

```bash
python -m app.build_index
```

This step:

- Encodes all sentences in `metas.jsonl`
- Normalizes embeddings
- Builds a FAISS `IndexIDMap`
- Persists the index to `data/index.faiss`

**Index rebuilds are manual and explicit to keep experiments controlled.**

---

## Claim Decomposition

### Purpose

The decomposer converts a claim into **atomic, independently verifiable subclaims**. This defines the reasoning granularity of the system.

### Design

The system uses a **hybrid approach**:

- `rule_decomposer` as a cheap, conservative gate
- `llm_decomposer` for semantic decomposition

Rules catch obvious atomic cases early. LLM handles complex semantic splits.

The decomposer:

- Never adds external facts
- Never paraphrases content
- May return `NO_DECOMPOSE` or `UNCERTAIN`

---

## Subclaim Verification Pipeline

Each subclaim is verified independently:

```
Subclaim
  → FAISS Retrieval
  → Cross-Encoder Reranking
  → NLI Stance Scoring
  → Evidence Aggregation
  → Subclaim Verdict
```

**No early collapse occurs.** All evidence survives until aggregation.

---

## Sentence-Level NLI (Stance Scoring)

### Model

- **MNLI** (RoBERTa-based)

### Input

- `(evidence_sentence, subclaim)`

### Output

Soft probabilities over:

- `entailment` → **SUPPORT**
- `contradiction` → **CONTRADICT**
- `neutral` → **NEUTRAL**

**No hard labels are assigned at this stage.** This avoids amplifying MNLI biases and preserves uncertainty.

---

## Adversarial Evidence Aggregation

Each evidence sentence contributes a **signed signal**:

```
stance_score = P(support) − P(contradict)
weighted_score = stance_score × reranker_score
```

### Aggregation Tracks

- Strong vs weak support
- Strong vs weak contradiction
- Neutral overload
- Aspect-level disagreement

**Deduplication is enforced** to prevent signal inflation.

---

## Subclaim Verdict Logic

Each subclaim is classified as:

- `SUPPORT`
- `CONTRADICT`
- `MIXED`
- `INCONCLUSIVE`

Decision rules are **dominance-based**, not threshold-only.

**`MIXED` is a first-class outcome**, not a fallback.

---

## Claim-Level Aggregation

The only public API of the system is:

```python
from app.claim_pipeline import claim_wrapper

result = claim_wrapper(claim: str)
```

### Claim-Level Logic

- Aggregates subclaim signals
- Enforces balance constraints
- Detects hard contradictions
- Scales thresholds with number of subclaims

**Verdicts are soft. Explanations are authoritative.**

---

## Running Claim Verification (Interactive)

Use the provided runner:

```bash
python run_claim_pipeline.py
```

This:

- Prompts for a claim
- Runs the full pipeline
- Pretty-prints verdicts, subclaims, evidence, and scores

**This runner is presentation-only** and does not affect evaluation.

---

## Evaluation & Ablations

Evaluation is treated as a **first-class design tool**, not an afterthought.

### Claim-Level Evaluation

```bash
python -m app.claim_pipeline_eval.eval_claim_wrapper
```

### Metrics

- Final verdict accuracy
- Macro F1 (primary)
- Per-class precision / recall
- Confusion matrices
- Error logs

### Key Findings from Ablations

#### Without Reranker

- `MIXED` collapses to zero
- Verdict space becomes binary
- Macro F1 ≈ 0.23

#### Without NLI

- Polarity disappears entirely
- All claims become `INCONCLUSIVE`
- Macro F1 ≈ 0.06

### Conclusion

- **Reranker is causally necessary** for balanced evidence exposure
- **NLI is strictly necessary** for polarity assignment

---

## PEFT (Deferred by Design)

The `app/peft/` directory contains:

- Decomposer PEFT dataset construction
- LoRA training scripts

### Why PEFT is Intentionally Not Executed

- Evaluation shows decomposer quality is the bottleneck
- Insufficient time for safe bias-targeted tuning
- Pipeline included for reproducibility and future work

---

## Design Philosophy

- **Explanation > Verdict**
- **Disagreement > Forced certainty**
- **Heuristics are explicit, not hidden**
- **Failures must be explainable**

This system is scoped as a **research artifact** for studying adversarial evidence reasoning, not a production fact-checker.