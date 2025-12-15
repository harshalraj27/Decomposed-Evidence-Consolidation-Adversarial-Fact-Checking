from sentence_transformers import SentenceTransformer
import json
from sklearn.preprocessing import normalize
import numpy as np
import faiss
from pathlib import Path

from .config import gte, metas_file, faiss_index

model = SentenceTransformer(gte)

index = None


def initialize_faiss_index():
    global index

    json_data = []
    with open(metas_file, "r", encoding="utf-8") as f:
        for line in f:
            json_data.append(json.loads(line))

    if not json_data:
        raise ValueError("Metadata file is empty, cannot build FAISS index")

    text = [s["sentence"] for s in json_data]
    ids = np.array([int(s["id"]) for s in json_data], dtype=np.int64)

    embeddings = model.encode(text, show_progress_bar=False)
    embeddings = normalize(embeddings, norm="l2").astype("float32")

    d = embeddings.shape[1]
    base_index = faiss.IndexFlatIP(d)
    index = faiss.IndexIDMap(base_index)

    index.add_with_ids(embeddings, ids)
    faiss.write_index(index, str(faiss_index))


def get_faiss_index():
    global index

    if index is not None:
        return index

    if Path(faiss_index).exists():
        index = faiss.read_index(str(faiss_index))
    else:
        initialize_faiss_index()

    return index


def add_faiss_index(metadata):
    global index

    index = get_faiss_index()

    text = [s["sentence"] for s in metadata]
    ids = np.array([int(s["id"]) for s in metadata], dtype=np.int64)

    embeddings = model.encode(text, show_progress_bar=False)
    embeddings = normalize(embeddings, norm="l2").astype("float32")

    index.add_with_ids(embeddings, ids)
    faiss.write_index(index, str(faiss_index))
