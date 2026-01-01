import pandas as pd
import spacy
import json
from pathlib import Path
from io import StringIO
import threading
import logging
import hashlib
from datetime import datetime
import re

from .build_index import add_faiss_index
from .config import metas_file, local_dir, ingested_dir
from .schemas import SuccessResponse, ErrorResponse
from .search import load_id_to_meta

nlp = spacy.blank("en")
nlp.add_pipe("sentencizer")

logger = logging.getLogger(__name__)

_metadata_lock = threading.Lock()

doc_index_file = ingested_dir / "doc_index.json"
next_id_file = ingested_dir / "next_id.txt"

def _load_doc_index():
    if doc_index_file.exists():
        with open(doc_index_file, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def _save_doc_index(data):
    with open(doc_index_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def _file_hash(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()

def get_new_id():
    with _metadata_lock:
        if not next_id_file.exists():
            next_id_file.parent.mkdir(parents=True, exist_ok=True)
            next_id_file.write_text("1")
            return 0
        curr = int(next_id_file.read_text())
        next_id_file.write_text(str(curr + 1))
        return curr

def build_metadata(content, file_name, file_type, source_type,
                    credibility, extra_meta=None, already_split=False):

    if not already_split:
        content = re.sub(r"\n{3,}", "\n\n", content)
        content = re.sub(r"[ \t]+", " ", content)
        content = re.sub(r"\n•\s*", ". ", content)
        content = re.sub(r"\n-\s*", ". ", content)
        content = re.sub(r"\n\d+\.\s*", ". ", content)

    if already_split:
        sentences = content
    else:
        doc = nlp(content)
        sentences = [s.text.strip() for s in doc.sents]

    clean_sentences = []
    for s in sentences:
        s = s.strip()
        s = re.sub(r"\s+", " ", s)

        if len(s.split()) < 5 or len(s.split()) > 100:
            continue
        if not re.search(r"[a-zA-Z]", s):
            continue
        if s.isupper():
            continue
        if "{" in s or "\\" in s:
            continue
        if s.count("(") > 4 or s.count(")") > 4:
            continue

        clean_sentences.append(s)

    metadata = []
    for pos, sent in enumerate(clean_sentences):
        metadata.append({
            "id": get_new_id(),
            "doc_id": file_name,
            "file_type": file_type,
            "position": pos,
            "sentence": sent,
            "source_type": source_type,
            "credibility": credibility,
            "source_url": extra_meta.get("source_url") if extra_meta else None,
            "primary_category": extra_meta.get("primary_category") if extra_meta else None
        })

    try:
        if metadata:
            metas_file.parent.mkdir(parents=True, exist_ok=True)
            with _metadata_lock:
                with open(metas_file, "a", encoding="utf-8") as f:
                    for row in metadata:
                        f.write(json.dumps(row, ensure_ascii=False) + "\n")

            add_faiss_index(metadata)
            load_id_to_meta(force_reload=True)

        logger.info(f"Successfully processed {file_name}: {len(metadata)} sentences extracted")
        return metadata, None

    except Exception as e:
        logger.error(f"Unexpected error processing {file_name}: {str(e)}")
        return [], ErrorResponse(
            message=f"Failed to process {file_name}: {str(e)}",
            error_type="system"
        )
