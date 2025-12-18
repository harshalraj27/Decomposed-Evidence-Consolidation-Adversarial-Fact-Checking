import json
import logging

import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.preprocessing import normalize

from .reranker import reranker
from .build_index import get_faiss_index
from .config import gte, metas_file, topk
from .schemas import ErrorResponse

logger = logging.getLogger(__name__)
model = SentenceTransformer(gte)

id_to_meta = {}

def load_id_to_meta(force_reload: bool = False):
    global id_to_meta
    if id_to_meta and not force_reload:
        return
    id_to_meta = {}
    with open(str(metas_file), 'r', encoding='utf8') as f:
        for line in f:
            obj = json.loads(line)
            id_to_meta[obj['id']] = obj

def search(subclaim: str, top_k: int = None):
    index = get_faiss_index()
    if not id_to_meta:
        load_id_to_meta()

    if not subclaim or not subclaim.strip():
        raise ErrorResponse(
            message="NO QUERY FOUND!!, QUERY IS REQUIRED",
            error_type="validation"
        ).to_http_exception()

    if top_k is None:
        top_k = topk

    try:
        top_k = int(top_k)
    except Exception:
        raise ErrorResponse(
            message="top_k must be an integer",
            error_type="validation"
        ).to_http_exception()

    if top_k < 1 or top_k > 100:
        raise ErrorResponse(
            message="top_k must be between 1 and 100",
            error_type="validation"
        ).to_http_exception()

    try:
        query_embeddings = model.encode(
            [subclaim],
            convert_to_numpy=True,
            normalize_embeddings=True
        )

        D, I = index.search(query_embeddings, top_k)
        results = []

        for rank, (idx, score) in enumerate(zip(I[0], D[0]), start=1):
            if idx == -1:
                continue
            meta = id_to_meta.get(int(idx))
            if meta is None:
                meta = {"sentence": "Not found", "doc_id": None, "position": None}
            faiss_rank = rank
            results.append({
                "id": int(idx),
                "faiss_score": float(score),
                "faiss_rank": faiss_rank,
                **meta
            })

        re_ranked_results = reranker(subclaim, results)
        return re_ranked_results

    except Exception as e:
        logger.error(f"Search query failed: {e}")
        raise ErrorResponse(
            message="Search failed",
            error_type="system"
        ).to_http_exception()
