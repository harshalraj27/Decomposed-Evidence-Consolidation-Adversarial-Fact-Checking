from .config import *
from .subclaim_pipeline import run_subclaim_pipeline
from .llm_decomposer import llm_decomposer
from .rule_decomposer import rule_decompose

STRONG_THRESHOLD = 0.6
WEAK_THRESHOLD = 0.3
TOP_K_EVIDENCE = 3

def check_hard_contradict(subclaim_results):
    for res in subclaim_results:
        if (
            res["verdict"] == "CONTRADICT"
            and res["strengths"]["contradict"] >= STRONG_THRESHOLD
        ):
            return True
    return False

def aggregate_signals(subclaim_results):
    agg = {
        "support_strong": 0.0,
        "support_weak": 0.0,
        "contradict_strong": 0.0,
        "contradict_weak": 0.0,
        "num_support": 0,
        "num_contradict": 0,
        "num_mixed": 0,
        "num_inconclusive": 0,
        "num_controversial": 0,
        "num_subclaims": len(subclaim_results),
    }

    for res in subclaim_results:
        verdict = res["verdict"]

        if verdict == "SUPPORT":
            agg["num_support"] += 1
        elif verdict == "CONTRADICT":
            agg["num_contradict"] += 1
        elif verdict == "MIXED":
            agg["num_mixed"] += 1
        elif verdict == "INCONCLUSIVE":
            agg["num_inconclusive"] += 1

        if res["controversial"]:
            agg["num_controversial"] += 1

        support = res["strengths"]["support"]
        contradict = res["strengths"]["contradict"]

        if support >= STRONG_THRESHOLD:
            agg["support_strong"] += support
        elif support >= WEAK_THRESHOLD:
            agg["support_weak"] += support

        if contradict >= STRONG_THRESHOLD:
            agg["contradict_strong"] += contradict
        elif contradict >= WEAK_THRESHOLD:
            agg["contradict_weak"] += contradict

    return agg

def rank_and_truncate(evidence_list):
    evidence_list = sorted(
        evidence_list,
        key=lambda x: x["combined_rank_score"],
        reverse=True
    )
    return evidence_list[:TOP_K_EVIDENCE]

def build_subclaim_explanation(res):
    support = res["strengths"]["support"]
    contradict = res["strengths"]["contradict"]

    if support >= STRONG_THRESHOLD:
        support_level = "strong"
    elif support >= WEAK_THRESHOLD:
        support_level = "weak"
    else:
        support_level = "none"

    if contradict >= STRONG_THRESHOLD:
        contradict_level = "strong"
    elif contradict >= WEAK_THRESHOLD:
        contradict_level = "weak"
    else:
        contradict_level = "none"

    return {
        "subclaim": res["subclaim"],
        "verdict": res["verdict"],
        "controversial": res["controversial"],
        "strength_summary": {
            "support": support_level,
            "contradict": contradict_level
        },
        "evidence": {
            "supporting": rank_and_truncate(res["evidence"]["supporting"]),
            "contradicting": rank_and_truncate(res["evidence"]["contradicting"]),
            "neutral": rank_and_truncate(res["evidence"]["neutral"])
        }
    }

def claim_wrapper(claim: str):
    subclaims = []
    subclaims_meta = llm_decomposer(claim)

    if subclaims_meta["verdict"] == "OK":
        for s in subclaims_meta["subclaims"]:
            subclaims.append(s["text"])

    elif subclaims_meta["verdict"] == "NO_DECOMPOSE":
        subclaims = [claim]

    else:
        rule_subclaims = rule_decompose(claim)
        if rule_subclaims:
            for sc in rule_subclaims:
                subclaims.append(sc.text)
        else:
            subclaims = [claim]

    subclaim_results = []
    for sc in subclaims:
        subclaim_results.append(run_subclaim_pipeline(sc))

    hard_contradict = check_hard_contradict(subclaim_results)
    agg = aggregate_signals(subclaim_results)

    n = agg["num_subclaims"]
    if n == 0:
        final_verdict = "INCONCLUSIVE"
    elif hard_contradict:
        final_verdict = "CONTRADICT"
    elif (
        agg["support_strong"] < WEAK_THRESHOLD
        and agg["contradict_strong"] < WEAK_THRESHOLD
        and agg["num_inconclusive"] / n > 0.5
    ):
        final_verdict = "INCONCLUSIVE"
    elif agg["support_strong"] >= STRONG_THRESHOLD and agg["contradict_strong"] < STRONG_THRESHOLD:
        final_verdict = "SUPPORT"
    elif agg["contradict_strong"] >= STRONG_THRESHOLD and agg["support_strong"] < STRONG_THRESHOLD:
        final_verdict = "CONTRADICT"

    elif agg["support_strong"] >= STRONG_THRESHOLD and agg["contradict_strong"] >= STRONG_THRESHOLD:
        final_verdict = "MIXED"

    elif agg["num_support"] / n > 0.5:
        final_verdict = "SUPPORT"

    elif agg["num_contradict"] / n > 0.5:
        final_verdict = "CONTRADICT"

    else:
        final_verdict = "INCONCLUSIVE"

    sections = {
        "SUPPORTED_ASPECTS": [],
        "CONTRADICTED_ASPECTS": [],
        "CONTROVERSIAL_ASPECTS": [],
        "EVIDENCE_LIMITATIONS": []
    }

    for res in subclaim_results:
        exp = build_subclaim_explanation(res)

        if res["verdict"] == "SUPPORT":
            sections["SUPPORTED_ASPECTS"].append(exp)
        elif res["verdict"] == "CONTRADICT":
            sections["CONTRADICTED_ASPECTS"].append(exp)
        elif res["verdict"] == "MIXED" or res["controversial"]:
            sections["CONTROVERSIAL_ASPECTS"].append(exp)
        else:
            sections["EVIDENCE_LIMITATIONS"].append(exp)

    explanation_sections = []
    for k, v in sections.items():
        if v:
            explanation_sections.append({
                "type": k,
                "items": v
            })

    if final_verdict == "SUPPORT":
        summary = "The claim is generally supported by the available evidence, with some limitations."
    elif final_verdict == "CONTRADICT":
        summary = "The claim is contradicted by strong evidence."
    elif final_verdict == "MIXED":
        summary = "The evidence presents mixed conclusions on key aspects of the claim."
    else:
        summary = "There is not enough strong evidence to reach a clear conclusion."

    return {
        "claim": claim,
        "verdict": final_verdict,
        "explanation": {
            "summary": summary,
            "sections": explanation_sections
        },
        "subclaims": subclaim_results
    }
