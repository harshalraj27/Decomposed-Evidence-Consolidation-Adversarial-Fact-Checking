from .search import search

query = "Transformers replace recurrence with attention"

results = search(query, top_k=20)

for r in results:
    print(
        f"FAISS #{r['faiss_rank']} ({r['faiss_score']:.3f}) | "
        f"RERANK #{r['rerank_rank']} ({r['rerank_score']:.3f})"
    )
    print(r["sentence"][:120])
    print("-" * 80)
