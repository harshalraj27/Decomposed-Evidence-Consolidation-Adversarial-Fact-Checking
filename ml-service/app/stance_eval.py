import json
from pathlib import Path

import matplotlib.pyplot as plt
from sklearn.metrics import accuracy_score, precision_recall_fscore_support, confusion_matrix

from .stance_classifier import stance_score
from .stance_eval_examples import curated_examples
from .config import stance_eval_dir


out = Path(stance_eval_dir)


def _write_jsonl(path_like, items):
    p = Path(path_like)
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("w", encoding="utf8") as f:
        for it in items:
            f.write(json.dumps(it, ensure_ascii=False) + "\n")


def save_errors(examples, out_dir):
    false_positives = []
    false_negatives = []

    for example in examples:
        actual_stance = example["gold"]
        predicted_stance = example["pred"]

        if predicted_stance != actual_stance and predicted_stance != "neutral":
            false_positives.append(example)

        if actual_stance != predicted_stance and actual_stance != "neutral":
            false_negatives.append(example)

    _write_jsonl(out_dir / "errors" / "false_positives.jsonl", false_positives)
    _write_jsonl(out_dir / "errors" / "false_negatives.jsonl", false_negatives)


results = []
gold_labels = []
pred_labels = []

for example in curated_examples:
    stance, stance_scores = stance_score(
        example["claim"],
        example["evidence"]
    )

    example["pred"] = stance
    example["probs"] = stance_scores

    gold_labels.append(example["gold"])
    pred_labels.append(stance)

    results.append(example)


acc = accuracy_score(gold_labels, pred_labels)
precision, recall, f1, _ = precision_recall_fscore_support(
    gold_labels,
    pred_labels,
    labels=["support", "contradict", "neutral"],
    average="macro",
    zero_division=0
)

cm = confusion_matrix(
    gold_labels,
    pred_labels,
    labels=["support", "contradict", "neutral"]
)

metrics = {
    "primary_metric": "f1_macro",
    "f1_macro": f1,
    "precision_macro": precision,
    "recall_macro": recall,
    "accuracy": acc,
    "confusion_matrix": cm.tolist(),
    "labels": ["support", "contradict", "neutral"]
}


_write_jsonl(out / "metrics.jsonl", [metrics])
_write_jsonl(out / "all_results.jsonl", results)

save_errors(results, out)


labels = ["support", "contradict", "neutral"]
plt.figure(figsize=(5, 4))
plt.imshow(cm)
plt.xticks(range(len(labels)), labels)
plt.yticks(range(len(labels)), labels)
plt.xlabel("Predicted")
plt.ylabel("Actual")

for i in range(len(labels)):
    for j in range(len(labels)):
        plt.text(j, i, cm[i, j], ha="center", va="center")

(out / "plots").mkdir(parents=True, exist_ok=True)
plt.tight_layout()
plt.savefig(out / "plots" / "confusion_matrix.png")
plt.close()
