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

from .build_index import add_faiss_index, get_faiss_index
from .config import metas_file, local_dir, ingested_dir
from .schemas import SuccessResponse, ErrorResponse
from .search import load_id_to_meta

nlp = spacy.load("en_core_web_lg")
logger = logging.getLogger(__name__)

_metadata_lock = threading.Lock()

doc_index_file = ingested_dir / "doc_index.json"

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
        if not metas_file.exists():
            return 0
        max_id = 0
        with open(metas_file, "r", encoding="utf-8") as f:
            for line in f:
                data = json.loads(line)
                max_id = max(max_id, data.get("id", 0))
        return max_id + 1

def build_metadata(content, file_name, file_type, source_type,
                    credibility, extra_meta=None, already_split=False):
    content = re.sub(r"\n{3,}", "\n\n", content)
    content = re.sub(r"[ \t]+", " ", content)
    content = re.sub(r"\n•\s*", ". ", content)
    content = re.sub(r"\n-\s*", ". ", content)
    content = re.sub(r"\n\d+\.\s*", ". ", content)
    metadata = []
    current_id = get_new_id()

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

    for pos, sent in enumerate(clean_sentences):
        metadata.append({
            "id": current_id,
            "doc_id": file_name,
            "file_type": file_type,
            "position": pos,
            "sentence": sent,
            "source_type": source_type,
            "credibility": credibility,
            "source_url": extra_meta.get("source_url") if extra_meta else None,
            "primary_category": extra_meta.get("primary_category") if extra_meta else None
        })
        current_id += 1

    try:
        with _metadata_lock:
            with open(metas_file, "a", encoding="utf-8") as f:
                for row in metadata:
                    f.write(json.dumps(row, ensure_ascii=False) + "\n")

        logger.info(f"Successfully processed {file_name}: {len(metadata)} sentences extracted")
        return metadata, None

    except Exception as e:
        logger.error(f"Unexpected error processing {file_name}: {str(e)}")
        return [], ErrorResponse(
            message=f"Failed to process {file_name}: {str(e)}",
            error_type="system"
        )

def initialize_metadata():
    doc_index = _load_doc_index()

    files = list(local_dir.rglob("*.txt")) + list(local_dir.rglob("*.md"))

    for file in files:
        try:
            text = file.read_text(encoding="utf-8")
        except Exception:
            continue

        rel_path = file.relative_to(local_dir).as_posix()
        content_hash = _file_hash(text)

        if rel_path in doc_index and doc_index[rel_path]["hash"] == content_hash:
            continue

        metadata, error = build_metadata(
            content=text,
            file_name=f"local_{rel_path.replace('/', '_')}",
            file_type=file.suffix,
            source_type="local",
            credibility=0.9,
            extra_meta={"source_url": str(file)},
            already_split=False
        )

        if metadata:
            add_faiss_index(metadata)
            load_id_to_meta(force_reload=True)

            doc_index[rel_path] = {
                "hash": content_hash,
                "last_ingested": datetime.utcnow().isoformat()
            }
    _save_doc_index(doc_index)

if not Path(metas_file).exists():
    initialize_metadata()
