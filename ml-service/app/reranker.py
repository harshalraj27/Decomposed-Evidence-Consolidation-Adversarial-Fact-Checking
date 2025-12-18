# Manual dev script to sanity-check dense search + reranker

import numpy as np
import logging
import torch

from sentence_transformers import CrossEncoder
from typing import List, Dict

from .config import *

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
model = CrossEncoder(ms_marco_6, device=DEVICE)


def reranker(query: str, sentences_meta: List[Dict], top_n = 20):
    if not sentences_meta:
        return []
    pairs = [(query, s['sentence']) for s in sentences_meta]
    scores = model.predict(pairs)

    scores = np.asarray(scores)

    for sentence, score in zip(sentences_meta, scores):
        sentence['rerank_score'] = float(score)

    sentences_meta.sort(key=lambda x: x['rerank_score'], reverse=True)

    for rank, sentence in enumerate(sentences_meta):
        sentence['rerank_rank'] = rank+1

    return sentences_meta[:top_n]