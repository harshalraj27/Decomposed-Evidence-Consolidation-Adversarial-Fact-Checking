import json

from pathlib import Path
from collections import defaultdict

import matplotlib.pyplot as plt

from app.claim_pipeline import claim_wrapper

LABELS = ["SUPPORT", "CONTRADICT", "MIXED", "INCONCLUSIVE"]

def load_eval_claims(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def run_eval(claims):
    results = []

    for item in claims:
        claim = item["claim"]
        expected = item["expected_final_verdict"]

        output = claim_wrapper(claim)

        results.append({
            "claim": claim,
            "expected_verdict": expected,
            "predicted_verdict": output["verdict"],
            "subclaims": output["subclaims"],
            "explanation": output["explanation"]
        })

        print("=" * 80)
        print("CLAIM:", claim)
        print("EXPECTED:", expected)
        print("PREDICTED:", output["verdict"])

    return results

def compute_final_accuracy(results):
    correct = sum(
        1 for r in results
        if r["expected_verdict"] == r["predicted_verdict"]
    )
    return correct / len(results)

def compute_confusion_matrix(results):
    matrix = {l: {k: 0 for k in LABELS} for l in LABELS}

    for r in results:
        matrix[r["expected_verdict"]][r["predicted_verdict"]] += 1

    return matrix

def compute_precision_recall_f1(confusion):
    metrics = {}

    for label in LABELS:
        tp = confusion[label][label]
        fp = sum(confusion[other][label] for other in LABELS if other != label)
        fn = sum(confusion[label][other] for other in LABELS if other != label)

        precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        f1 = (2 * precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0

        metrics[label] = {
            "precision": precision,
            "recall": recall,
            "f1": f1
        }

    macro_f1 = sum(m["f1"] for m in metrics.values()) / len(metrics)

    return {
        "per_class": metrics,
        "macro_f1": macro_f1
    }

def compute_subclaim_accuracy(results):
    total = 0
    correct = 0

    for r in results:
        for sc in r["subclaims"]:
            if "expected_verdict" not in sc:
                continue
            total += 1
            if sc["verdict"] == sc["expected_verdict"]:
                correct += 1

    if total == 0:
        return None

    return correct / total

def compute_decomposition_stats(results):
    counts = [len(r["subclaims"]) for r in results]
    return {
        "avg_subclaims_per_claim": sum(counts) / len(counts),
        "min_subclaims": min(counts),
        "max_subclaims": max(counts)
    }

def save_confusion_matrix_png(confusion, out_path):
    matrix = [[confusion[r][c] for c in LABELS] for r in LABELS]

    fig, ax = plt.subplots(figsize=(6, 6))
    im = ax.imshow(matrix)

    ax.set_xticks(range(len(LABELS)))
    ax.set_yticks(range(len(LABELS)))
    ax.set_xticklabels(LABELS)
    ax.set_yticklabels(LABELS)

    for i in range(len(LABELS)):
        for j in range(len(LABELS)):
            ax.text(j, i, matrix[i][j], ha="center", va="center")

    ax.set_xlabel("Predicted")
    ax.set_ylabel("Expected")
    ax.set_title("Claim Wrapper Confusion Matrix")

    plt.tight_layout()
    plt.savefig(out_path)
    plt.close()

if __name__ == "__main__":
    BASE_DIR = Path(__file__).parent

    claims = load_eval_claims(BASE_DIR / "claims_eval.json")
    results = run_eval(claims)

    final_acc = compute_final_accuracy(results)
    confusion = compute_confusion_matrix(results)
    prf = compute_precision_recall_f1(confusion)
    subclaim_acc = compute_subclaim_accuracy(results)
    decomp_stats = compute_decomposition_stats(results)

    print("\nFINAL VERDICT ACCURACY:", final_acc)
    print("\nCONFUSION MATRIX:")
    for k, v in confusion.items():
        print(k, v)

    print("\nMACRO F1:", prf["macro_f1"])
    print("\nPER-CLASS METRICS:")
    for k, v in prf["per_class"].items():
        print(k, v)

    print("\nSUBCLAIM ACCURACY:", subclaim_acc)
    print("\nDECOMPOSITION STATS:", decomp_stats)

    save_confusion_matrix_png(
        confusion,
        BASE_DIR / "claim_confusion_matrix.png"
    )

    with open(BASE_DIR / "claim_eval_results.json", "w", encoding="utf-8") as f:
        json.dump({
            "results": results,
            "metrics": {
                "final_accuracy": final_acc,
                "confusion_matrix": confusion,
                "precision_recall_f1": prf,
                "subclaim_accuracy": subclaim_acc,
                "decomposition_stats": decomp_stats
            }
        }, f, indent=2)
