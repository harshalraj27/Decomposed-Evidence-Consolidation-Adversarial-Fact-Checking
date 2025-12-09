from collections import defaultdict
from transformers import pipeline
import re
from .config import *

classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli", device=0)


health_regex = re.compile(r"\b(virus|covid|infection|antibiotic|cancer|therapy|symptom|vaccine|clinical trial|antiviral|biomarker|diagnostic)\b", re.I)
law_regex = re.compile(r"\b(bill|law|parliament|lawmaker|policy|budget|minister|vote)\b", re.I)
eco_regex = re.compile(r"\b(inflation|gdp|price|stock|market|revenue|tax|unemployment|interest rate)\b", re.I)
history_regex = re.compile(r"\b(1[0-9]{3}|20[0-2][0-9]|[0-9]{1,2}th century|world war|ancient|medieval)\b", re.I)
env_regex = re.compile(r"\b(climate|global warming|carbon|co2|deforestation|pollution|emissions)\b", re.I)
science_regex = re.compile(r"\b(quantum|entanglement|exoplanet|gravitational|orbital|theorem|equation|spectral|astrophysic|particle|neutrino|thermodynamics|differential)\b", re.I)

def classify(sentence, top_label=None, top_score=None, second_label=None,
             second_score=None, THRESHOLD = 0.25):
    if not sentence or not sentence.strip():
        return "general knowledge", 0.0, {
            "first_label": ("general knowledge", 0.0),
            "second_label": ("general knowledge", 0.0)
        }
    if top_label is None or top_score is None:
        result = classifier(sentence, labels)

        label_scores = list(zip(result["labels"], map(float, result["scores"])))

        if science_regex.search(sentence):
            for i, (label, score) in enumerate(label_scores):
                if label == "science/maths":
                    label_scores[i] = (label, score + 0.07)
                    break

        label_scores.sort(key=lambda x: x[1], reverse=True)

        top_label, top_score = label_scores[0]
        top_score = float(top_score)

        if len(label_scores) > 1:
            second_label, second_score = label_scores[1]
            second_score = float(second_score)
        else:
            second_label, second_score = top_label, 0.0

    metadata = {
        "first_label": (top_label, top_score),
        "second_label": (second_label, second_score)
    }

    if health_regex.search(sentence) and not law_regex.search(sentence):
        final_label = "health/medicine"
        final_score = 0.85
        return final_label, final_score, metadata
    if top_score > THRESHOLD:
        final_label = top_label
        final_score = top_score
        return final_label, final_score, metadata
    if eco_regex.search(sentence):
        final_label = "economy/finance"
        final_score = max(top_score, THRESHOLD)
        return final_label, final_score, metadata

    if history_regex.search(sentence):
        final_label = "history"
        final_score = max(top_score, THRESHOLD)
        return final_label, final_score, metadata

    if env_regex.search(sentence):
        final_label = "environment/climate"
        final_score = max(top_score, THRESHOLD)
        return final_label, final_score, metadata

    final_label = "general knowledge"
    final_score = 0.0
    return final_label, final_score, metadata

def label(text, max_chars=500, top_k=2, score_threshold=0.2, batch_size=16, THRESHOLD = 0.25):
    text = (text or "")[:max_chars]
    sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+', text) if s.strip()]

    if not sentences:
        return {
            "primary": ("general knowledge", 0.0),
            "top_k": [("general knowledge", 0.0)],
            "label_distribution": {k: 0.0 for k in labels},
            "sentence_labels": []
        }

    health_matches = [bool(health_regex.search(s)) for s in sentences]
    to_classify_idx = [i for i, is_health in enumerate(health_matches) if not is_health]
    to_classify = [sentences[i] for i in to_classify_idx]

    sentence_classifications = {}

    results = []
    if to_classify:
        results = classifier(to_classify, labels, batch_size=batch_size)
        if isinstance(results, dict):
            results = [results]

    for i, s in enumerate(sentences):
        if health_matches[i]:
            sentence_classifications[i] = ("health/medicine", 0.99)

    for idx, result in zip(to_classify_idx, results):
        top_label = result["labels"][0]
        top_score = float(result["scores"][0])
        second_label = result["labels"][1] if len(result["labels"]) > 1 else top_label
        second_score = float(result["scores"][1]) if len(result["scores"]) > 1 else 0.0

        final_label, final_score, _ = classify(
            sentences[idx],
            top_label=top_label,
            top_score=top_score,
            second_label=second_label,
            second_score=second_score,
            THRESHOLD=THRESHOLD
        )
        sentence_classifications[idx] = (final_label, final_score)

    s_labels = [(sentences[i], sentence_classifications[i][0], sentence_classifications[i][1]) for i in range(len(sentences))]

    score_map = defaultdict(list)
    for _, lbl, score in s_labels:
        score_map[lbl].append(score)

    aggregated = {
        label: (sum(scores) / len(scores)) if scores else 0.0
        for label in labels
        for scores in [score_map.get(label, [])]
    }

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
