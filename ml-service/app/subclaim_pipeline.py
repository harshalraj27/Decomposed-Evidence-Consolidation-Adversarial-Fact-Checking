from .search import search
from .reranker import reranker
from .stance_classifier import stance_score
from .stance_aggregator import aggregate_evidences
from .subclaim_verdict import get_verdict, get_controversy

USE_RERANKER = True
USE_NLI = True

def run_subclaim_pipeline(subclaim, top_k=20, top_n=10):
    subclaim = subclaim.text
    retrieved = search(subclaim, top_k=top_k)

    # Reranker ablation switch
    if USE_RERANKER:
        reranked = reranker(subclaim, retrieved, top_n=top_n)
    else:
        reranked = retrieved

    stance_results = []
    for e in reranked:
        if USE_NLI:
            probs = stance_score(subclaim, e["sentence"])
        else:
            # NLI ablation: neutral-only baseline
            probs = {"support": 0.0, "contradict": 0.0, "neutral": 1.0}

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