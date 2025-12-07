from collections import defaultdict
from transformers import pipeline
import re
from .config import *

classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli", device=0)


health_regex = r"\b(vaccine|covid|virus|disease|infection|drug|antibiotic|cancer|therapy|symptom)\b"
eco_regex = r"\b(inflation|gdp|price|stock|market|revenue|tax|unemployment|interest rate)\b"
history_regex = r"\b(1[0-9]{3}|20[0-2][0-9]|[0-9]{1,2}th century|world war|ancient|medieval)\b"
env_regex = r"\b(climate|global warming|carbon|co2|deforestation|pollution|emissions)\b"



def classify(sentence, top_label=None, top_score=None, THRESHOLD = 0.45):
    if not sentence or not sentence.strip():
        return "general knowledge", 0.0

    if top_label is None or top_score is None:
        result = classifier(sentence, labels)
        top_label = result["labels"][0]
        top_score = float(result["scores"][0])

    if re.search(health_regex, sentence, re.I):
        return "health/medicine", 0.99
    if top_score > THRESHOLD:
        return top_label, top_score
    if re.search(eco_regex, sentence, re.I):
        return "economy/finance", top_score
    if re.search(history_regex, sentence, re.I):
        return "history", top_score
    if re.search(env_regex, sentence, re.I):
        return "environment/climate", top_score
    return "general knowledge", top_score


def label(text, max_chars=500, top_k=2, score_threshold=0.2, batch_size=16, THRESHOLD = 0.45):
    text = (text or "")[:max_chars]
    sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+', text) if s.strip()]

    if not sentences:
        return {
            "primary": ("general knowledge", 0.0),
            "top_k": [("general knowledge", 0.0)],
            "label_distribution": {k: 0.0 for k in labels},
            "sentence_labels": []
        }

    hard = [bool(re.search(health_regex, s, re.I)) for s in sentences]
    idx = [i for i, h in enumerate(hard) if not h]
    to_classify = [sentences[i] for i in idx]

    results = []
    if to_classify:
        results = classifier(to_classify, labels, batch_size=batch_size, THRESHOLD = THRESHOLD)
        if isinstance(results, dict):
            results = [results]

    out = {}
    for i, s in enumerate(sentences):
        if hard[i]:
            out[i] = ("health/medicine", 0.99)

    for i, res in zip(idx, results):
        tl = res["labels"][0]
        ts = float(res["scores"][0])
        lbl, sc = classify(sentences[i], top_label=tl, top_score=ts)
        out[i] = (lbl, sc)

    for i in range(len(sentences)):
        if i not in out:
            out[i] = ("general knowledge", 0.0)

    s_labels = [(sentences[i], out[i][0], out[i][1]) for i in range(len(sentences))]

    score_map = defaultdict(list)
    for _, lbl, score in s_labels:
        score_map[lbl].append(score)

    aggregated = {}
    for l in labels:
        lst = score_map.get(l, [])
        aggregated[l] = (sum(lst)/len(lst)) if lst else 0.0

    ranked = sorted(aggregated.items(), key=lambda x: x[1], reverse=True)
    top = [(l, float(s)) for l, s in ranked if s >= score_threshold]
    topk = top[:top_k] if top else [(ranked[0][0], float(ranked[0][1]))]
    primary = topk[0]

    return {
        "primary": (primary[0], float(primary[1])),
        "top_k": topk,
        "label_distribution": {k: float(v) for k, v in aggregated.items()},
        "sentence_labels": s_labels
    }
