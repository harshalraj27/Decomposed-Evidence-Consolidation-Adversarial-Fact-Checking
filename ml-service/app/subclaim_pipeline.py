from .config import *
from .search import search
from .reranker import reranker
from .stance_classifier import stance_score

subclaim = "Self-attention replaced recurrence in NLP models"

retrieved = search(subclaim, top_k=20)
print("RETRIEVED:", len(retrieved))

for e in retrieved[:5]:
    print("----")
    print("Keys in retrieved item:", retrieved[0].keys())
    print("Sentence:", e["sentence"])
    print("FAISS score:", e["faiss_score"])
    print("Source:", e["source_type"])

reranked = reranker(subclaim, retrieved, top_n=10)
print("\nRERANKED:")

for e in reranked:
    print("----")
    print("Sentence:", e["sentence"])
    print("FAISS:", e["faiss_score"])
    print("Rerank:", e["rerank_score"])

print("\nSTANCE RESULTS:")
for e in reranked:
    stance, probs = stance_score(subclaim, e["sentence"])
    print("----")
    print("Sentence:", e["sentence"])
    print("Stance:", stance)
    print("Probs:", probs)
