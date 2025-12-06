import json
import faiss
from sklearn.preprocessing import normalize
from sentence_transformers import SentenceTransformer
import logging
from pathlib import Path

from .config import model_name, metas_file, faiss_index, top_k
from .schemas import ErrorResponse
from .build_index import get_faiss_index

logger = logging.getLogger(__name__)
model = SentenceTransformer(model_name)

id_to_meta = {}

def load_id_to_meta():
    global id_to_meta
    id_to_meta = {}
    with open(str(metas_file), 'r', encoding='utf8') as f:
        for line in f:
            obj = json.loads(line)
            id_to_meta[obj['id']] = obj

index = get_faiss_index()

def search_query(query, top_k=top_k):
    load_id_to_meta()
    if not query or not query.strip():
        ErrorResponse(message="NO QUERY FOUND!!, QUERY IS REQUIRED", error_type="validation").to_http_exception()
    if top_k < 1 or top_k > 100:
        ErrorResponse(message="top_k must be between 1 and 100", error_type="validation").to_http_exception()
    try:
        query_embeddings = model.encode(query, convert_to_numpy=True)
        query_embeddings = normalize(query_embeddings.reshape(1, -1), norm='l2')
        D, I = index.search(query_embeddings, top_k)
        results = []
        for idx, score in zip(I[0], D[0]):
            results.append({
                "id": int(idx),
                "score": float(score),
                **id_to_meta.get(int(idx), {"sentence": "Not found"})
            })
        return results
    except Exception as e:
        logger.error(f"Search query failed: {e}")
        ErrorResponse(message="Search failed", error_type="system").to_http_exception()
