from .config import *

def aggregate_evidences(stance_results):
    seen_sentences = set()
    supporting =[]
    contradicting =[]
    neutral =[]

    support_strength = 0.0
    contradict_strength = 0.0
    for e in stance_results:
        s = e['probs']['support']
        c = e['probs']['contradict']

        sent = e["sentence"].strip()

        if sent not in seen_sentences:
            seen_sentences.add(sent)
        else:
            continue

        stance_score = s-c
        weight = max(0.0, e['rerank_score'])
        evidence_contribution = weight*stance_score
        e['stance_score'] = stance_score
        e['evidence_contribution'] = evidence_contribution

        if(abs(stance_score) < epsilon):
            neutral.append(e)
        elif stance_score>0:
            supporting.append(e)
            support_strength += max(0, evidence_contribution)
        elif stance_score<0:
            contradicting.append(e)
            contradict_strength += max(0, -evidence_contribution)

    supporting = sorted(supporting, key=lambda e: e['evidence_contribution'], reverse=True)
    contradicting = sorted(contradicting, key=lambda e: e['evidence_contribution'])
    neutral = sorted(neutral, key=lambda e: e['rerank_score'], reverse=True)

    total_strength = support_strength + contradict_strength

    return {
        "supporting": supporting,
        "contradicting": contradicting,
        "neutral": neutral[:3],
        "support_strength": support_strength,
        "contradict_strength": contradict_strength,
        "total_strength": total_strength,
        "meta": {
            "num_support": len(supporting),
            "num_contradict": len(contradicting),
            "num_neutral": len(neutral),
            "count": len(supporting) + len(contradicting)
        }
    }
