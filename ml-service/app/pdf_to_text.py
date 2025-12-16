from pathlib import Path
import json
import re
import logging

import spacy
from pdfminer.high_level import extract_text

from .build_metadata import build_metadata
from .config import ingested_pdf_dir, ingested_meta_dir

logger = logging.getLogger(__name__)
nlp = spacy.load("en_core_web_sm")

def pdf_to_text_and_metadata(arxiv_id: str):
    pdf_path = ingested_pdf_dir / f"arxiv_{arxiv_id}.pdf"
    meta_path = ingested_meta_dir / f"arxiv_{arxiv_id}.meta.json"

    if not pdf_path.exists() or not meta_path.exists():
        logger.warning(f"Missing files for {arxiv_id}")
        return
    with open(meta_path, "r", encoding="utf-8") as f:
        doc_meta = json.load(f)

    try:
        raw_text = extract_text(pdf_path)
    except Exception as e:
        logger.error(f"PDF extraction failed for {arxiv_id}: {e}")
        return

    if not raw_text or len(raw_text.strip()) < 500:
        logger.warning(f"Too little text extracted for {arxiv_id}")
        return

    text = raw_text

    # normalize whitespace
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"[ \t]+", " ", text)

    # remove page numbers
    text = re.sub(r"\n\d+\n", "\n", text)

    # merge broken lines
    text = re.sub(r"(?<!\n)\n(?!\n)", " ", text)

    PRUNE_MARKERS = [
        "references",
        "bibliography",
        "acknowledgements",
        "appendix"
    ]

    lower = text.lower()
    for marker in PRUNE_MARKERS:
        idx = lower.find("\n" + marker)
        if idx != -1:
            text = text[:idx]
            break

    doc = nlp(text)
    sentences = [sent.text.strip() for sent in doc.sents]

    clean_sentences = []

    for s in sentences:
        # basic normalization
        s = re.sub(r"\s+", " ", s).strip()

        # filters
        if len(s.split()) < 5 or len(s.split()) > 60:
            continue
        if not re.search(r"[a-zA-Z]", s):
            continue
        if s.isupper():
            continue
        if re.match(r"^\(?\d+[\]\)]?$", s):
            continue

    clean_sentences.append(s)

    if not clean_sentences:
        logger.warning(f"No usable sentences for {arxiv_id}")
        return

    build_metadata(
        content=clean_sentences,
        file_name=f"arxiv_{arxiv_id}",
        file_type=".pdf",
        source_type=doc_meta["source_type"],
        credibility=doc_meta["credibility"],
        extra_meta=doc_meta
    )

