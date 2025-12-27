import json
from pathlib import Path

import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
from sklearn.preprocessing import normalize

from .config import metas_file, faiss_index, gte, M

model = SentenceTransformer(gte)
index = None


def initialize_faiss_index():
    global index

    texts = []
    ids = []

    with open(metas_file, "r", encoding="utf-8") as f:
        for line in f:
            data = json.loads(line)
            texts.append(data["sentence"])
            ids.append(int(data["id"]))

    if not texts:
        raise ValueError("Metadata file is empty, cannot build FAISS index")

    embeddings = model.encode(texts, show_progress_bar=True)
    embeddings = normalize(embeddings, norm="l2").astype("float32")

    d = embeddings.shape[1]

    base_index = faiss.IndexHNSWFlat(d, M, faiss.METRIC_INNER_PRODUCT)
    index = faiss.IndexIDMap(base_index)

    index.add_with_ids(embeddings, np.array(ids, dtype=np.int64))

    tmp_path = str(faiss_index) + ".tmp"
    faiss.write_index(index, tmp_path)
    Path(tmp_path).replace(faiss_index)


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

    if not metadata:
        return

    index = get_faiss_index()

    texts = [m["sentence"] for m in metadata]
    ids = np.array([int(m["id"]) for m in metadata], dtype=np.int64)

    embeddings = model.encode(texts, show_progress_bar=False)
    embeddings = normalize(embeddings, norm="l2").astype("float32")

    index.add_with_ids(embeddings, ids)

    tmp_path = str(faiss_index) + ".tmp"
    faiss.write_index(index, tmp_path)
    Path(tmp_path).replace(faiss_index)
