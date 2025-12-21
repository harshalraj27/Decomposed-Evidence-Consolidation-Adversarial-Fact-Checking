from .search import search
from .reranker import reranker
from .stance_classifier import stance_score
from .stance_aggregator import aggregate_evidences
from .subclaim_verdict import get_verdict, get_controversy

def run_subclaim_pipeline(subclaim, top_k=20, top_n=10):
    retrieved = search(subclaim, top_k=top_k)

    reranked = reranker(subclaim, retrieved, top_n=top_n)

    stance_results = []
    for e in reranked:
        probs = stance_score(subclaim, e["sentence"])
        e["probs"] = probs
        stance_results.append(e)

    aggregated = aggregate_evidences(stance_results)

    verdict, total, support, contradict = get_verdict(aggregated)
    controversial = get_controversy(aggregated, verdict)

    return {
        "subclaim": subclaim,
        "verdict": verdict,
        "controversial": controversial,
        "strengths": {
            "support": support,
            "contradict": contradict,
            "total": total
        },
        "evidence": {
            "supporting": aggregated["supporting"],
            "contradicting": aggregated["contradicting"],
            "neutral": aggregated["neutral"]
        }
    }

if __name__ == "__main__":
    res = run_subclaim_pipeline(
        "Self-attention replaced recurrence in NLP models"
    )

    print("VERDICT:", res["verdict"])
    print("CONTROVERSIAL:", res["controversial"])
    print("STRENGTHS:", res["strengths"])

    print("\nSUPPORTING:")
    for e in res["evidence"]["supporting"][:3]:
        print("-", e["sentence"][:120])

    print("\nCONTRADICTING:")
    for e in res["evidence"]["contradicting"][:3]:
        print("-", e["sentence"][:120])

    print("\nNEUTRAL:")
    for e in res["evidence"]["neutral"][:3]:
        print("-", e["sentence"][:120])