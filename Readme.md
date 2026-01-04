# Decomposed Evidence Consolidation Adversarial Fact-Checking

## Overview

This project implements a decomposed, evidence-driven, adversarial fact-checking system for verifying complex factual claims.

Instead of treating fact-checking as a single retrieval or classification task, the system explicitly models **supporting and contradicting evidence as competing signals**. Claims are decomposed into atomic subclaims, each subclaim is independently verified, and final claim-level decisions are made only after aggregating opposing evidence across all subclaims.

This system is **research-oriented by design**. It prioritizes interpretability, error analysis, and architectural clarity over raw accuracy or production readiness.

> **Note:** This is not a production QA system.

---

## Quick Start

### Verify Your First Claim

**Prerequisites:**
- GPU with 8GB+ VRAM
- Python 3.8+

#### 1. Setup Environment

```bash
python -m venv .venv
source .venv/bin/activate          # Linux / Mac
# .venv\Scripts\activate           # Windows

pip install -r requirements.txt
python -m spacy download en_core_web_lg
```

#### 2. Build Knowledge Base

```bash
python -m app.build_metadata
python -m app.build_index
```

#### 3. Run Verification

```bash
python run_claim_pipeline.py
```

**Example:**
```
Enter claim: Scaling model size and training data has led to improved performance in large language models.

FINAL VERDICT: SUPPORT
```

---

## Example Verification Cases

### Case 1: Fully Supported Claim

**Claim:** *"Scaling model size and training data has led to improved performance in large language models."*

**Verdict:** `SUPPORT`

**Decomposition:**
1. "Scaling model size has led to improved performance in large language models" → **SUPPORT**
2. "Training data has led to improved performance in large language models" → **SUPPORT**

**Top Evidence:**
- Source: `arxiv.org/abs/2512.25070v1`
  - Scores → FAISS: 0.8933 | Rerank: 3.9703 | Combined: 4.8636

- Source: `ml_llms.txt`
  - Scores → FAISS: 0.8985 | Rerank: 1.8251 | Combined: 2.7236

---

### Case 2: Partially Supported Claim

**Claim:** *"Transformer-based language models significantly improve performance on NLP tasks but introduce high computational and energy costs."*

**Verdict:** `SUPPORT` (with limitations)

**Decomposition:**
1. "Transformer-based language models significantly improve performance on NLP tasks" → **SUPPORT**
2. "Transformer-based language models introduce high computational costs" → **INCONCLUSIVE**
3. "Transformer-based language models introduce high energy costs" → **INCONCLUSIVE**

**Evidence Breakdown:**

**✓ Supported: Performance Improvements**
- Source: `ml_transformers.txt`
- Scores → FAISS: 0.9092 | Rerank: 2.3207 | Combined: 3.2298

**⚠ Inconclusive: Computational Costs**
- Contradicting evidence present (score: -3.6436)
- Neutral evidence dominates (score: 5.9213)
- No strong supporting evidence found

**⚠ Inconclusive: Energy Costs**
- Contradicting evidence present (score: -1.9597)
- Neutral evidence present (score: 1.4848)
- No supporting evidence found

---

## Understanding the Output

### Verdict Types

- **`SUPPORT`**: Strong evidence supports the claim, minimal contradiction
- **`CONTRADICT`**: Strong evidence contradicts the claim, minimal support
- **`MIXED`**: Significant evidence on both sides, unresolved disagreement
- **`INCONCLUSIVE`**: Insufficient evidence, high neutral signal, or corpus gap

### Evidence Scoring

```
Scores → FAISS: 0.9033 | Rerank: 2.2963 | NLI: 0.0 | Cred: 0.0 | Combined: 3.1996
```

- **FAISS**: Semantic similarity to subclaim
- **Rerank**: Cross-encoder relevance score
- **NLI**: Natural Language Inference stance score
- **Cred**: Source credibility weight
- **Combined**: Weighted aggregate score

### Subclaim Strength Indicators

```
Strength → Support: strong, Contradict: none
```

- **strong**: Multiple high-scoring evidence pieces
- **weak**: Few or low-scoring evidence pieces
- **none**: No evidence above threshold

---

## Research-Oriented Design Principles

The system is intentionally built around the following principles:

- **Explanation > Verdict**
- **Disagreement is surfaced, not hidden**
- **Uncertainty is a valid and expected outcome**
- **Every major component can be ablated and inspected**
- **Failures should be explainable, not silent**

The goal is not to maximize decisiveness, but to **understand how evidence supports or contradicts a claim and where the system fails**.

---

## Core Idea: Adversarial Evidence Consolidation

Fact-checking is framed as an **adversarial process**.

For each subclaim:

- Evidence is evaluated for both support and contradiction
- Opposing signals are accumulated instead of filtered
- Weak and neutral evidence is preserved as context
- Disagreement is explicitly represented (via `MIXED` and `INCONCLUSIVE`)

**Final decisions depend on relative dominance of evidence**, not the presence of a single strong sentence.

---

## High-Level Architecture

```
Claim
  → Decomposer
      → Subclaims
          → Subclaim Pipeline
              → Dense Retrieval (FAISS)
              → Cross-Encoder Reranking
              → Sentence-Level NLI
              → Evidence Aggregation
              → Subclaim Verdict
          → Claim-Level Aggregation
              → Final Claim Verdict + Explanation
```

Each stage has a **single, explicit responsibility** and is designed to be independently testable and ablatable.

---

## Repository Structure

```
ml-service/
├── app/
│   ├── claim_pipeline.py           # Claim-level wrapper (main API)
│   ├── subclaim_pipeline.py        # Per-subclaim verification pipeline
│   ├── llm_decomposer.py           # LLM-based claim decomposition
│   ├── rule_decomposer.py          # Heuristic decomposer gate
│   ├── search.py                   # FAISS dense retrieval
│   ├── reranker.py                 # Cross-encoder reranking
│   ├── stance_classifier.py        # MNLI stance scoring
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
│   ├── ingested/
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

## Environment & Hardware Requirements

### GPU Requirement

**This project assumes GPU usage.**

The following components are GPU-heavy by design:

- SentenceTransformer encoders
- Cross-encoder reranker
- MNLI stance classifier
- LLM-based decomposer (llama.cpp)

**CPU execution is technically possible but not a supported or optimized path.**

### Environment Setup

```bash
python -m venv .venv
source .venv/bin/activate          # Linux / Mac
# .venv\Scripts\activate           # Windows

pip install -r requirements.txt
```

### Download Decomposer Model

The system uses a local LLM for claim decomposition. Download the quantized Llama-3 model:
```bash
# Create models directory if it doesn't exist
mkdir -p models

# Download Meta-Llama-3-8B-Instruct (Q5_K_M quantization)
# Visit: https://huggingface.co/QuantFactory/Meta-Llama-3-8B-Instruct-GGUF
# Download: Meta-Llama-3-8B-Instruct-Q5_K_M.gguf
# Place in: models/Meta-Llama-3-8B-Instruct-Q5_K_M.gguf
```

**Direct download link:** [Meta-Llama-3-8B-Instruct-Q5_K_M.gguf](https://huggingface.co/QuantFactory/Meta-Llama-3-8B-Instruct-GGUF/blob/main/Meta-Llama-3-8B-Instruct-Q5_K_M.gguf)

**Model specs:**
- Size: ~5.7GB
- Quantization: Q5_K_M (balanced quality/size)
- Context length: 8192 tokens

**Alternative (CLI download with huggingface-cli):**
```bash
pip install huggingface-hub
huggingface-cli download QuantFactory/Meta-Llama-3-8B-Instruct-GGUF \
  Meta-Llama-3-8B-Instruct-Q5_K_M.gguf \
  --local-dir models/ \
  --local-dir-use-symlinks False
```

**Verify model location:**
```bash
ls -lh models/Meta-Llama-3-8B-Instruct-Q5_K_M.gguf
# Should show ~5.7GB file
```



### Additional Required Model

```bash
python -m spacy download en_core_web_lg
```

---

## Data & Corpus Design (Intentional Constraint)

**The system does not accept arbitrary user uploads.**

All evidence must come from:

- `data/local_curated/` (manual, reproducible sources)
- Admin-controlled online ingestion

### Why This Constraint Exists

- Ensures reproducibility
- Prevents noisy or adversarial inputs
- Keeps evaluation controlled and interpretable
- Avoids "LLM-style" free-form answering

**Downstream components do not distinguish between local and online sources.**

---

## Metadata Construction (Core Data Layer)

All documents are converted into **sentence-level metadata**, stored in:

```
data/metas.jsonl
```

Each sentence includes:

- Stable sentence ID
- Source type
- Document metadata
- Credibility score
- Provenance information

### Local Curated Ingestion

1. Place files in:
   ```
   data/local_curated/
   ```

2. Run:
   ```bash
   python -m app.build_metadata
   ```

This step:

- Recursively scans directories
- Splits text into sentences
- Filters noisy or malformed sentences
- Assigns stable IDs
- Writes metadata to `metas.jsonl`

---

## Online Ingestion (Admin / Research Use)

Online ingestion is interactive and controlled via:

```bash
python run_online_ingestion.py
```

You select a source and provide inputs interactively.

### arXiv Ingestion

- Fetches papers by category
- Downloads PDFs
- Writes metadata
- Automatically runs:
  - PDF → text
  - Sentence filtering
  - Metadata construction
- **No manual post-processing is required**

### Wikipedia Ingestion

- Fetches full article text
- Drops non-content sections
- Assigns heuristic credibility
- Passes text directly to metadata builder

### PubMed Ingestion

- Fetches abstracts (or PMC full text optionally)
- Applies length and quality filters
- Stores biomedical metadata

### OpenReview Ingestion

- Fetches submissions from a venue
- Optionally includes reviews
- Stores structured metadata

**All ingestion paths end by calling `build_metadata`.**

---

## FAISS Index Construction

After ingestion:

```bash
python -m app.build_index
```

This:

- Encodes all sentences in `metas.jsonl`
- Normalizes embeddings
- Builds a FAISS `IndexIDMap`
- Persists to `data/index.faiss`

**Index rebuilds are manual by design to keep experiments controlled.**

---

## Claim Decomposition

### Purpose

The decomposer converts a claim into **atomic, independently verifiable subclaims**. This defines the reasoning granularity of the entire system.

### Hybrid Design

- **`rule_decomposer`**: cheap, conservative gate
- **`llm_decomposer`**: semantic decomposition for complex claims

Rules catch obvious atomic cases early. The LLM handles semantic splits that rules cannot.

### Design Constraints

- No external facts are added
- No paraphrasing
- Output may be:
  - `OK`
  - `NO_DECOMPOSE`
  - `UNCERTAIN`

**Failures at this stage propagate downstream** by producing weak or background subclaims, which is explicitly acknowledged.

---

## Subclaim Verification Pipeline

Each subclaim is verified independently:

```
Subclaim
  → FAISS Retrieval
  → Cross-Encoder Reranking
  → MNLI Stance Scoring
  → Evidence Aggregation
  → Subclaim Verdict
```

**No early collapse is allowed.**

---

## Sentence-Level NLI (Stance Scoring)

### Model

- **RoBERTa MNLI**

### Input

- `(evidence_sentence, subclaim)`

### Output

- Soft probabilities

### Mapping

- `entailment` → **SUPPORT**
- `contradiction` → **CONTRADICT**
- `neutral` → **NEUTRAL**

**No hard labels are assigned here.** All downstream reasoning uses soft scores.

---

## Adversarial Evidence Aggregation (Core Contribution)

Each sentence contributes a **signed signal**:

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

This layer evolved heavily through evaluation and is frozen.

---

## Subclaim Verdict Logic

Each subclaim is classified as:

- `SUPPORT`
- `CONTRADICT`
- `MIXED`
- `INCONCLUSIVE`

### Key Principles

- `MIXED` is detected before binary verdicts
- Neutral evidence increases uncertainty, not contradiction
- Dominance matters more than raw counts

---

## Claim-Level Aggregation (Main API)

The only public API:

```python
from app.claim_pipeline import claim_wrapper

result = claim_wrapper(claim: str)
```

### Claim-Level Logic

- Aggregates subclaim signals
- Enforces balance constraints
- Detects hard contradictions
- Scales thresholds with subclaim count

**Verdicts are soft. Explanations are authoritative.**

---

## Running Claim Verification (Interactive)

```bash
python run_claim_pipeline.py
```

This:

- Prompts for a claim
- Runs the full pipeline
- Pretty-prints verdicts, subclaims, evidence, and scores

**This runner is presentation-only.**

---

## Evaluation & Ablations (First-Class Design Tool)

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

### Confusion Matrix

![Claim Wrapper Confusion Matrix](assets/confusion_matrix.png)

The confusion matrix shows:
- **SUPPORT**: 5/6 correctly classified (83% precision)
- **CONTRADICT**: 5/6 correctly classified (83% precision)
- **MIXED**: 4/11 correctly classified (36% recall)
- **INCONCLUSIVE**: 2/4 correctly classified (50% precision)

**Key observations:**
- Strong diagonal (correct predictions)
- MIXED class shows confusion with CONTRADICT (6 cases)
- System tends to under-predict MIXED verdicts

### Ablation Study Results

| Run | Alpha | Logic Version | Accuracy | Macro F1 | MIXED Precision | MIXED Recall | Key Observation |
|-----|-------|---------------|----------|----------|-----------------|--------------|-----------------|
| 1 | 0.3 | Old logic (no polarity) | ~0.48 | ~0.49 | 0.0 | 0.0 | MIXED not detected at all |
| 2 | 0.3 | Polarity-aware logic | ~0.59 | ~0.62 | 1.0 | ~0.36 | Best balance so far |
| 3 | 0.4 | Polarity-aware logic | ~0.56 | ~0.58 | 1.0 | ~0.27 | MIXED appears, conservative |
| 4 | 0.5 | Polarity-aware logic | ~0.52 | ~0.54 | 1.0 | ~0.18 | Over-penalizes → MIXED collapses again |

### Key Ablation Results

#### Without Reranker

- `MIXED` collapses to zero
- Verdicts become binary
- Macro F1 ≈ 0.23

**Explanation:** Without reranking, the system cannot distinguish between strongly relevant and weakly relevant evidence. All retrieved sentences are treated equally, leading to signal noise and inability to detect nuanced disagreement.

#### Without NLI

- Polarity disappears
- All claims → `INCONCLUSIVE`
- Macro F1 ≈ 0.06

**Explanation:** Without stance classification, the system cannot determine whether evidence supports or contradicts a claim. It becomes a pure retrieval system with no reasoning capability.

#### Impact of Alpha (Threshold Parameter)

- **Alpha = 0.3**: Best overall balance (Macro F1 = 0.62), but MIXED recall is moderate (~0.36)
- **Alpha = 0.4**: More conservative, MIXED recall drops to ~0.27
- **Alpha = 0.5**: Over-penalizes weak signals, MIXED collapses again (recall ~0.18)

**Conclusion:** The alpha parameter controls the sensitivity threshold. Too low causes false positives in MIXED detection; too high causes the system to collapse back to binary verdicts.

**These ablations validate architectural necessity, not tuning.**

---


## Technical Decisions & Evolution

This section documents key architectural decisions, failures, and pivots during development.

### Why Polarity-Aware Aggregation?

**Initial approach (before Dec 27):** Simple verdict counting across subclaims.

**Problem identified:** MIXED verdicts collapsed entirely. Single weak contradiction would overpower multiple support signals.

**Solution:** Moved to **signal accumulation** with explicit polarity tracking:

```python
support_signal = Σ(support_strength × reranker_score)
contradict_signal = Σ(contradict_strength × reranker_score)
```

**Impact:** Macro F1 improved from ~0.49 → ~0.62, MIXED precision reached 1.0

---

### Why Hybrid Decomposer (Rule + LLM)?

**Initial approach:** Pure LLM decomposition using Llama-3.1-8B.

**Problems observed:**
- Model sometimes marked atomic claims as decomposable
- Generated weak or redundant subclaims
- Slow for obvious cases

**Solution:** Two-stage hybrid:
1. **Rule-based gate** catches obvious atomic/compound patterns (fast, conservative)
2. **LLM decomposer** handles complex semantic splits

**Trade-off accepted:** Some borderline failures remain. Fixing requires fine-tuning (see PEFT section).

---

### Why Two Ablations (No Reranker, No NLI)?

#### Ablation 1: No Reranker

- Macro F1 dropped to ~0.23
- MIXED recall → 0.0
- **Finding:** FAISS-only retrieval surfaces imbalanced evidence. Reranker is causally necessary for exposing counter-evidence.

#### Ablation 2: No NLI

- Macro F1 dropped to ~0.06
- All verdicts collapsed to INCONCLUSIVE
- **Finding:** NLI is the only component that assigns semantic polarity. Without it, system cannot distinguish support from contradiction.

**Architectural conclusion:** Reranker enables balanced retrieval, NLI enables polarity discrimination. Both are strictly necessary.

---

### Threshold Calibration

Thresholds were tuned via systematic evaluation, not intuition:

| Parameter | Initial | Final | Rationale |
|-----------|---------|-------|-----------|
| `alpha` | 0.5 | 0.3 | Lower α prevents MIXED collapse |
| `STRONG_THRESHOLD` | 0.6 | 0.7 | Stricter bar for "strong" evidence |
| `WEAK_THRESHOLD` | 0.3 | 0.3 | Unchanged (balanced) |
| `MIXED_SUPPORT_MIN` | 0.35 | 0.30 | Allow MIXED with moderate support |
| `MIXED_NEGATIVE_MIN` | 0.35 | 0.30 | Symmetric constraint |

**Alpha sweep results:**
- α=0.5: MIXED recall ~0.18 (too conservative)
- α=0.3: MIXED recall ~0.36 (best balance)
- α<0.3: False positives increase

---

### Why PEFT Was Deferred

**Observation:** Evaluation showed decomposer quality is the primary bottleneck (~34% of errors trace to weak subclaim generation).

**Attempted:** LoRA fine-tuning on Llama-3.1-8B using pipeline-logged failure cases.

**Blockers:**
1. Model gating/authentication issues on HuggingFace
2. Switching to smaller model would invalidate existing baselines
3. Insufficient time for proper bias validation

**Decision:** Defer PEFT rather than rush incomplete fine-tuning. Pipeline is implemented and documented for reproducibility.

**Alternative considered:** Fine-tune on generic decomposition dataset (rejected—doesn't address system-specific failures).

---

## Known Limitations

### Decomposer Brittleness

- Generates weak/background subclaims for vague input claims
- Example: "These models improve performance" → subclaim lacks specificity
- Downstream NLI sees high neutral scores (not a bug, input is genuinely underspecified)
- **Impact:** Reduces MIXED recall, increases INCONCLUSIVE false positives

### Neutral Evidence Overload

- When decomposer produces generic subclaims, retrieval returns topically related but stance-neutral evidence
- Aggregation correctly treats this as insufficient evidence
- **Not an NLI failure**—the subclaim itself carries no polarity
- **Fix:** Improve decomposer via PEFT or better prompting

### MIXED Recall Trade-off

- Current system prioritizes MIXED precision (1.0) over recall (~0.36)
- This is intentional—false MIXED verdicts are worse than missing some
- Lowering α improves recall but increases false positives
- **Design choice:** Conservative disagreement detection

### Corpus Coverage Gaps

- System is constrained to curated sources (no arbitrary uploads)
- Recent events or niche domains may return INCONCLUSIVE due to corpus gaps
- **Mitigation:** Periodic online ingestion (arXiv, Wikipedia, PubMed)

---

## Error Analysis (Sample Cases)

### Case 1: Decomposer Failure

**Claim:** "Einstein won a Nobel Prize for relativity"

**Expected:** Decompose into "Einstein won Nobel Prize" + "Prize was for relativity"

**Actual:** Not decomposed (treated as atomic)

**Impact:** Prize was for photoelectric effect → incorrect SUPPORT verdict

**Root cause:** Rule decomposer missed this, LLM treated as single fact

---

### Case 2: Corpus Gap

**Claim:** "The Riemann Hypothesis was proven in 2024"

**Expected:** CONTRADICT or INCONCLUSIVE

**Actual:** INCONCLUSIVE (corpus ends Jan 2025, no coverage)

**Impact:** Cannot verify recent mathematical claims

**Mitigation:** Requires domain-specific corpus expansion

---

### Case 3: NLI Lexical Bias

**Claim:** "Transformers require high computational resources"

**Evidence:** "Transformers use self-attention mechanisms"

**NLI Output:** Neutral (correct—evidence is topically related but doesn't address "high resources")

**System Behavior:** INCONCLUSIVE (no strong evidence found)

**Not a failure:** Evidence genuinely doesn't support the claim

---

## Reproducibility Notes

### Evaluation Dataset

- 27 hand-curated claims spanning:
  - Simple factual claims (5 claims)
  - Multi-aspect claims with 5–7 subclaims (11 claims)
  - Controversial/mixed claims (6 claims)
  - Out-of-domain claims (5 claims)
- Dataset includes expected verdicts and subclaim decompositions
- Located in: `app/claim_pipeline_eval/test_claims.jsonl`

### Hardware Used During Development

- **GPU:** NVIDIA RTX 4070 (8GB VRAM)
- **RAM:** 32GB
- **CPU:** Intel i9-13900H
- **OS:** Windows 11

### Model Versions

- **SentenceTransformer (FAISS encoding):** `all-MiniLM-L6-v2`
- **Cross-encoder (reranker):** `cross-encoder/ms-marco-MiniLM-L-6-v2`
- **NLI stance classifier:** `roberta-large-mnli`
- **Decomposer LLM:** `Meta-Llama-3-8B-Instruct-Q5_K_M.gguf` (via llama.cpp)
  - Source: [QuantFactory/Meta-Llama-3-8B-Instruct-GGUF](https://huggingface.co/QuantFactory/Meta-Llama-3-8B-Instruct-GGUF)
  - Quantization: Q5_K_M (5.7GB)
- **Sentence splitting:** spaCy `en_core_web_lg`

### Corpus Statistics (Post-Ingestion)

- **Total sentences:** ~12,847
- **Sources:**
  - Local curated: ~3,200 sentences (ML scaling, transformers, LLMs, datasets)
  - arXiv papers: ~5,400 sentences (cs.AI, cs.LG categories)
  - Wikipedia: ~2,800 sentences (ML/NLP articles)
  - PubMed: ~1,200 sentences (computational biology abstracts)
  - OpenReview: ~247 sentences (ICLR 2024 submissions)

---

## Future Work

### High-Priority Improvements

1. **Decomposer PEFT fine-tuning**
   - Target: Reduce weak subclaim generation by 50%
   - Method: LoRA on pipeline-logged failure cases
   - Expected impact: +0.10 macro F1, +0.15 MIXED recall

2. **Corpus expansion**
   - Add domain-specific sources (legal, medical, financial)
   - Implement incremental online ingestion (daily Wikipedia/arXiv updates)
   - Expected impact: Reduce INCONCLUSIVE false positives by 30%

3. **Subclaim importance weighting**
   - Current limitation: All subclaims treated equally
   - Proposed: Core vs peripheral subclaim classification
   - Expected impact: Reduce penalty for irrelevant subclaim failures

### Lower-Priority Enhancements

- Multi-hop reasoning support (claims requiring 2+ evidence chains)
- Temporal reasoning (claims with time-sensitive conditions)
- Source credibility learning (move from heuristic to learned scores)
- Explanation quality metrics (human eval of generated explanations)

---

## Citation

If you use this system or methodology in your research:

```bibtex
@misc{adversarial-fact-checking-2025,
  title={Decomposed Evidence Consolidation for Adversarial Fact-Checking},
  author={Your Name},
  year={2025},
  url={https://github.com/yourusername/fact-checking}
}
```


## PEFT (Deferred Intentionally)

The `app/peft/` directory contains:

- Dataset construction
- LoRA scripts

### Why PEFT Was Intentionally Not Completed

- Evaluation showed decomposer quality is the bottleneck
- Insufficient time for safe bias-targeted tuning
- Running PEFT without proper validation would be misleading

**The pipeline is included for reproducibility and future work.**

---

## Design Philosophy (Explicit)

- **Explanation > Verdict**
- **Disagreement > Forced certainty**
- **Heuristics are explicit**
- **Failures must be explainable**

This system is a **research artifact** for studying adversarial evidence reasoning — not a production fact-checker.