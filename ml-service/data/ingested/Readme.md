# Ingested Data Directory

This directory stores content fetched from online sources via the ingestion pipeline.

## Purpose

The ingestion system downloads and processes content from curated sources:
- **arXiv:** Research papers (PDF → text)
- **Wikipedia:** Article content (HTML → text)
- **PubMed:** Biomedical abstracts and full text
- **OpenReview:** Conference submissions and reviews

All ingested content is converted to sentence-level metadata and indexed in `data/metas.jsonl` and `data/index.faiss`.

---

## Directory Structure
```
data/ingested/
├── README.md                   # This file
├── pdf/                        # Raw PDFs from arXiv
├── raw/                        # Raw text/HTML from sources
├── cleaned/                    # Cleaned and filtered text
├── meta/                       # Source metadata (.meta.json files)
└── .gitkeep                    # Keeps directory in git
```

---

## Subdirectories

### `pdf/`
Contains raw PDF files downloaded from arXiv.

**Format:** `{arxiv_id}.pdf`  
**Example:** `2312.00123v1.pdf`

**Processing:**
1. Download PDF from arXiv
2. Extract text using `pdf_to_text.py`
3. Clean and filter sentences
4. Generate metadata
5. Add to `metas.jsonl`

---

### `raw/`
Contains raw unprocessed text from all sources.

**Format:** `{source}_{identifier}.txt`  
**Examples:**
- `wiki_Machine_Learning.txt`
- `pubmed_38234567.txt`
- `openreview_iclr2024_xyz123.txt`

**Processing:** Raw text is cleaned, split into sentences, and filtered before indexing.

---

### `cleaned/`
Contains cleaned and sentence-filtered text ready for indexing.

**Format:** `{source}_{identifier}_cleaned.txt`  
**Processing:**
- Removed noisy characters
- Filtered short sentences (<10 chars)
- Removed references/citations (arXiv)
- Removed equations/math fragments
- Deduplicated sentences

---

### `meta/`
Contains source metadata for each ingested document.

**Format:** `{source}_{identifier}.meta.json`  
**Example structure:**
```json
{
  "source": "arxiv",
  "arxiv_id": "2312.00123v1",
  "title": "Attention Is All You Need",
  "authors": ["Vaswani et al."],
  "abstract": "...",
  "pdf_url": "https://arxiv.org/pdf/2312.00123v1.pdf",
  "categories": ["cs.LG", "cs.AI"],
  "published": "2023-12-01",
  "credibility": 0.85,
  "ingested_at": "2024-01-04T10:23:45Z"
}
```

---

## Ingestion Workflow

### Running Ingestion
```bash
python run_online_ingestion.py
```

**Interactive prompts:**
1. Select source (arxiv/wikipedia/pubmed/openreview)
2. Provide source-specific parameters
3. System automatically:
   - Downloads content
   - Processes and cleans text
   - Generates metadata
   - Updates `metas.jsonl`
   - Rebuilds FAISS index

---

### Source-Specific Parameters

#### arXiv
- **Input:** Category (e.g., `cs.AI`, `cs.LG`, `stat.ML`)
- **Output:** PDFs in `pdf/`, text in `cleaned/`, metadata in `meta/`
- **Credibility:** 0.85 (peer-reviewed preprints)

#### Wikipedia
- **Input:** Article title or search query
- **Output:** Text in `raw/` and `cleaned/`, metadata in `meta/`
- **Credibility:** 0.6-0.8 (varies by article quality)

#### PubMed
- **Input:** Search query or PMID
- **Output:** Abstracts in `raw/` and `cleaned/`, metadata in `meta/`
- **Credibility:** 0.9 (peer-reviewed journals)

#### OpenReview
- **Input:** Venue invitation (e.g., `ICLR.cc/2024/Conference`)
- **Output:** Submissions in `raw/` and `cleaned/`, metadata in `meta/`
- **Credibility:** 0.75 (under-review papers)

---

## Data Flow
```
Online Source
    ↓
Download (PDF/HTML/API)
    ↓
data/ingested/pdf/ or data/ingested/raw/
    ↓
Clean & Filter
    ↓
data/ingested/cleaned/
    ↓
Extract Metadata
    ↓
data/ingested/meta/*.meta.json
    ↓
Build Sentence Metadata
    ↓
data/metas.jsonl
    ↓
Rebuild FAISS Index
    ↓
data/index.faiss
```

---

## File Naming Conventions

### arXiv
- **PDF:** `{arxiv_id}.pdf` (e.g., `2312.00123v1.pdf`)
- **Raw:** `arxiv_{arxiv_id}.txt`
- **Cleaned:** `arxiv_{arxiv_id}_cleaned.txt`
- **Meta:** `arxiv_{arxiv_id}.meta.json`

### Wikipedia
- **Raw:** `wiki_{article_title}.txt` (underscores for spaces)
- **Cleaned:** `wiki_{article_title}_cleaned.txt`
- **Meta:** `wiki_{article_title}.meta.json`

### PubMed
- **Raw:** `pubmed_{pmid}.txt`
- **Cleaned:** `pubmed_{pmid}_cleaned.txt`
- **Meta:** `pubmed_{pmid}.meta.json`

### OpenReview
- **Raw:** `openreview_{venue}_{submission_id}.txt`
- **Cleaned:** `openreview_{venue}_{submission_id}_cleaned.txt`
- **Meta:** `openreview_{venue}_{submission_id}.meta.json`

---

## Metadata Schema

All `.meta.json` files follow this structure:
```json
{
  "source": "string",           // arxiv|wikipedia|pubmed|openreview
  "identifier": "string",       // Source-specific ID
  "title": "string",
  "authors": ["string"],        // Optional
  "abstract": "string",         // Optional
  "url": "string",
  "credibility": float,         // 0.0-1.0
  "published": "ISO8601",       // Optional
  "ingested_at": "ISO8601",
  "category": "string",         // Source-specific
  "sentence_count": int,
  "file_paths": {
    "raw": "string",
    "cleaned": "string",
    "pdf": "string"             // arXiv only
  }
}
```

---

## Storage Considerations

### Disk Usage (Typical)

- **arXiv papers:** ~5-10MB per paper (PDF + text)
- **Wikipedia articles:** ~50-500KB per article
- **PubMed abstracts:** ~5-20KB per abstract
- **OpenReview submissions:** ~100-500KB per submission

**Estimate for 100 documents:**
- arXiv: ~500-1000MB
- Wikipedia: ~5-50MB
- PubMed: ~0.5-2MB
- OpenReview: ~10-50MB

### Cleanup

To free up space while preserving metadata:
```bash
# Remove raw PDFs (keep processed text)
rm -rf data/ingested/pdf/

# Remove raw text (keep cleaned versions)
rm -rf data/ingested/raw/

# Remove all ingested files (keep metadata)
rm -rf data/ingested/pdf/ data/ingested/raw/ data/ingested/cleaned/
# Metadata in meta/ and metas.jsonl remains intact
```

To completely reset ingestion:
```bash
# WARNING: This removes all ingested content
rm -rf data/ingested/*
# Rebuild metadata and index from local_curated only
python -m app.build_metadata
python -m app.build_index
```

---

## Troubleshooting

### Permission Errors
```
PermissionError: [Errno 13] Permission denied: 'data/ingested/pdf/'
```

**Solution:**
```bash
chmod -R 755 data/ingested/
```

---

### Disk Space Issues
```
OSError: [Errno 28] No space left on device
```

**Solution:**
1. Check disk usage: `du -sh data/ingested/*`
2. Remove raw files (PDFs, raw text)
3. Keep only `cleaned/` and `meta/`

---

### Missing Subdirectories
```
FileNotFoundError: [Errno 2] No such file or directory: 'data/ingested/pdf/'
```

**Solution:**
```bash
mkdir -p data/ingested/{pdf,raw,cleaned,meta}
```

---

## Best Practices

### Incremental Ingestion

1. **Start small:** Ingest 10-20 documents to test pipeline
2. **Verify metadata:** Check `.meta.json` files are created
3. **Check index:** Run search to verify sentences are indexed
4. **Scale up:** Ingest larger batches once verified

### Source Credibility

Credibility scores are heuristic estimates:
- **PubMed:** 0.9 (peer-reviewed journals)
- **arXiv:** 0.85 (preprints, not peer-reviewed)
- **OpenReview:** 0.75 (under review)
- **Wikipedia:** 0.6-0.8 (varies by article quality)

These affect evidence weighting in the aggregation pipeline.

### Corpus Management

**Regular maintenance:**
- Remove duplicate papers (same arXiv ID, different versions)
- Update Wikipedia articles periodically
- Archive old OpenReview submissions after conference

**Version control:**
- Metadata files (`.meta.json`) should be backed up
- Raw/cleaned text can be regenerated from sources
- PDFs can be re-downloaded from arXiv

---

## Git Tracking

**This directory is excluded from git** (see `.gitignore`).

**What's tracked:**
- ✓ `data/ingested/README.md` (this file)
- ✓ `data/ingested/.gitkeep` (preserves directory)

**What's ignored:**
- ✗ All ingested content (`pdf/`, `raw/`, `cleaned/`, `meta/`)

**Rationale:**
- Ingested data is reproducible (can be re-downloaded)
- Large files would bloat repository
- Sources may have licensing restrictions

---

## Reproducibility

To reproduce the corpus from scratch:

1. **Clone repository** (gets README and structure)
2. **Run ingestion:**
```bash
   python run_online_ingestion.py
   # Select sources and parameters
```
3. **Rebuild index:**
```bash
   python -m app.build_metadata
   python -m app.build_index
```

**Note:** Exact reproduction depends on:
- Source availability (papers may be removed)
- Wikipedia content changes over time
- OpenReview submissions (conference-specific)

For exact reproducibility, preserve `.meta.json` files and `metas.jsonl`.

---

## Support

For ingestion issues:
1. Check source is accessible (network, API limits)
2. Verify credentials (if required)
3. Check disk space (`df -h`)
4. Review logs in `run_online_ingestion.py` output

For source-specific issues:
- **arXiv:** Check category code validity
- **Wikipedia:** Verify article title spelling
- **PubMed:** Check PMID or search query
- **OpenReview:** Verify venue invitation format