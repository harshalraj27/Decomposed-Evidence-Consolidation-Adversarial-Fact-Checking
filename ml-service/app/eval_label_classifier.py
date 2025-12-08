import numpy as np
import os
from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import (
    precision_recall_fscore_support,
    confusion_matrix,
    accuracy_score,
    f1_score,
)
from sklearn.model_selection import KFold

from .config import *
from .label_classification import classify, classifier

def load_file():
    if not label_test_file.exists():
        return "Error loading test data"
    records = []
    with open(label_test_file, "r", encoding="utf-8") as f:
        for line in f:
            records.append(json.loads(line))
    return records

def x_y_split(records):
    sentences = []
    actuals = []
    for rec in records:
        sentences.append(rec["sentence"])
        actuals.append(rec["label"])
    return sentences, actuals

def batch(items, batch_size):
    return [items[i: i + batch_size] for i in range(0, len(items), batch_size)]

def predict_sentence(sentences, actual_labels, threshold, batch_size):
    if not label_eval_dir.exists():
        os.makedirs(label_eval_dir, exist_ok=True)
    sentence_chunks = batch(sentences, batch_size)
    actual_chunks = batch(actual_labels, batch_size)
    predictions_metadata = []
    for chunk_index, chunk in enumerate(sentence_chunks):
        results = classifier(chunk, labels, batch_size=batch_size)
        if isinstance(results, dict):
            results = [results]
        for i, result in enumerate(results):
            top_label = result["labels"][0]
            top_score = float(result["scores"][0])
            second_label = result["labels"][1] if len(result["labels"]) > 1 else top_label
            second_score = float(result["scores"][1]) if len(result["scores"]) > 1 else 0.0
            sentence = chunk[i]
            actual_label = actual_chunks[chunk_index][i]
            final_label, final_score, meta_data = classify(
                sentence,
                top_label=top_label,
                top_score=top_score,
                second_label=second_label,
                second_score=second_score,
                THRESHOLD=threshold
            )
            record = {
                "sentence": sentence,
                "actual_label": actual_label,
                "assigned_label": final_label,
                "assigned_score": final_score,
                "model_top1": (top_label, top_score),
                "model_top2": (second_label, second_score),
                "threshold_used": threshold,
                "top1_score": top_score,
                "top2_score": second_score,
            }
            predictions_metadata.append(record)
    return predictions_metadata

def compute_metrics(predictions_metadata, top2_preds=None, top1_scores=None, threshold=None,
                    general_label="general knowledge", zero_division=0):
    predicted_labels = [rec["assigned_label"] for rec in predictions_metadata]
    actual_labels = [rec["actual_label"] for rec in predictions_metadata]
    p, r, f1, sup = precision_recall_fscore_support(
        actual_labels, predicted_labels, labels=list(labels), zero_division=zero_division
    )
    per_class = {
        label_name: {
            "precision": float(p[i]),
            "recall": float(r[i]),
            "f1": float(f1[i]),
            "support": int(sup[i]),
        }
        for i, label_name in enumerate(labels)
    }
    count = len(predicted_labels)
    macro_f1 = float(f1_score(actual_labels, predicted_labels, average="macro", zero_division=zero_division)) if count else 0.0
    micro_f1 = float(f1_score(actual_labels, predicted_labels, average="micro", zero_division=zero_division)) if count else 0.0
    accuracy = float(accuracy_score(actual_labels, predicted_labels)) if count else 0.0
    coverage = sum((predicted_labels[i] != general_label) for i in range(count)) / count if count else 0.0
    top2_acc = None
    top2_rescue = None
    if top2_preds is not None:
        hits = 0
        rescue_count = 0
        for i in range(count):
            t1, t2 = top2_preds[i]
            if actual_labels[i] in (t1, t2):
                hits += 1
            if top1_scores is not None and threshold is not None:
                if top1_scores[i] < threshold and actual_labels[i] == t2:
                    rescue_count += 1
        top2_acc = hits / count if count else 0.0
        if top1_scores is not None and threshold is not None:
            top2_rescue = rescue_count / count if count else 0.0
    cm = confusion_matrix(actual_labels, predicted_labels, labels=list(labels)).tolist() if count else []
    metrics = {
        "per_class": per_class,
        "macro_f1": macro_f1,
        "micro_f1": micro_f1,
        "accuracy": accuracy,
        "coverage": coverage,
        "confusion_matrix": {"labels": list(labels), "matrix": cm},
    }
    if top2_acc is not None:
        metrics["top2_acc"] = float(top2_acc)
    if top2_rescue is not None:
        metrics["top2_rescue"] = float(top2_rescue)
    return metrics

def _write_jsonl(path_like, items):
    p = Path(path_like)
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("w", encoding="utf8") as f:
        for it in items:
            f.write(json.dumps(it, ensure_ascii=False) + "\n")

def save_errors(predictions_metadata_list, out_dir=None):
    out = Path(out_dir) if out_dir else label_eval_dir
    false_positives = []
    false_negatives = []
    for record in predictions_metadata_list:
        actual_label = record.get("actual_label")
        predicted_label = record.get("assigned_label")
        if predicted_label != actual_label and predicted_label != "general knowledge":
            false_positives.append(record)
        if actual_label != predicted_label and actual_label != "general knowledge":
            false_negatives.append(record)
    _write_jsonl(out / "errors" / "false_positives.jsonl", false_positives)
    _write_jsonl(out / "errors" / "false_negatives.jsonl", false_negatives)

def plot_threshold_vs_metric(sweep_results, metric_name, out_path=None):
    out_path = Path(out_path) if out_path else label_eval_dir / "plots" / f"{metric_name}_vs_threshold.png"
    thresholds = [row["threshold"] for row in sweep_results]
    metrics_vals = [row.get(metric_name, None) for row in sweep_results]
    plt.figure(figsize=(6,4))
    plt.plot(thresholds, metrics_vals, marker="o")
    plt.xlabel("threshold")
    plt.ylabel(metric_name)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(out_path)
    plt.close()

def plot_confusion_matrix(conf_matrix, labels_list, out_path=None):
    out_path = Path(out_path) if out_path else label_eval_dir / "plots" / "confusion_matrix.png"
    cm = np.array(conf_matrix)
    plt.figure(figsize=(max(6, len(labels_list)*0.5), max(4, len(labels_list)*0.35)))
    sns.heatmap(cm, annot=True, fmt="d", xticklabels=labels_list, yticklabels=labels_list, cmap="viridis")
    plt.xlabel("predicted")
    plt.ylabel("actual")
    plt.tight_layout()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(out_path)
    plt.close()

def run_one_threshold(threshold, data_records, batch_size, labels_list):
    sentences, actuals = x_y_split(data_records)
    predictions_metadata = predict_sentence(sentences, actuals, threshold, batch_size)
    metrics = compute_metrics(predictions_metadata)
    return predictions_metadata, metrics

def sweep_thresholds(data_records, labels_list, sweep_from, sweep_to, sweep_step, out_dir=None,
                     batch_size=16, kfold=None, metric_to_opt="macro_f1", ablation_variants=None):
    out = Path(out_dir) if out_dir else label_eval_dir
    sweep_results = []
    best = {"metric": -1.0, "threshold": None, "metrics": None}
    thresholds = list(np.arange(sweep_from, sweep_to + 1e-12, sweep_step))
    for ablation in (ablation_variants or [None]):
        for t in thresholds:
            if kfold and kfold > 1:
                kf = KFold(n_splits=kfold, shuffle=True, random_state=42)
                fold_metrics = []
                for _, val_idx in kf.split(data_records):
                    val_data = [data_records[i] for i in val_idx]
                    _, metrics = run_one_threshold(t, val_data, batch_size, labels_list)
                    fold_metrics.append(metrics[metric_to_opt])
                avg_metric = float(np.mean(fold_metrics))
                row = {"threshold": float(t), "ablation": ablation, f"avg_{metric_to_opt}": avg_metric}
            else:
                preds_meta, metrics = run_one_threshold(t, data_records, batch_size, labels_list)
                row = {"threshold": float(t), "ablation": ablation,
                       **{k: metrics.get(k) for k in ("macro_f1", "micro_f1", "accuracy", "coverage")}}
                _write_jsonl(out / f"sweep_preds_thresh_{t:.3f}_ablation_{ablation}.jsonl", preds_meta)
                if metrics.get(metric_to_opt, -999) > best["metric"]:
                    best = {"metric": metrics.get(metric_to_opt), "threshold": t, "metrics": metrics}
            sweep_results.append(row)
    _write_jsonl(out / "sweep_results.jsonl", sweep_results)
    with (out / "sweep_results.json").open("w", encoding="utf8") as f:
        json.dump(sweep_results, f, indent=2, ensure_ascii=False)
    return best, sweep_results

def run_ablation_set(data_records, labels_list, ablation_flags, out_dir=None, batch_size=16):
    out = Path(out_dir) if out_dir else label_eval_dir
    summaries = {}
    for name, params in ablation_flags.items():
        threshold = params.get("threshold", 0.5)
        preds_meta, metrics = run_one_threshold(threshold, data_records, batch_size, labels_list)
        summaries[name] = metrics
        _write_jsonl(out / f"eval_summary_ablation_{name}.jsonl", preds_meta)
    with (out / "ablation_summaries.json").open("w", encoding="utf8") as f:
        json.dump(summaries, f, indent=2, ensure_ascii=False)
    return summaries

def write_final_outputs(predictions_metadata, metrics, sweep_results=None, out_dir=None):
    out = Path(out_dir) if out_dir else label_eval_dir
    _write_jsonl(out / "predictions.jsonl", predictions_metadata)
    with (out / "eval_summary.json").open("w", encoding="utf8") as f:
        json.dump({"metrics": metrics, "generated_at": datetime.utcnow().isoformat() + "Z"}, f, indent=2, ensure_ascii=False)
    if sweep_results:
        with (out / "sweep_results.json").open("w", encoding="utf8") as f:
            json.dump(sweep_results, f, indent=2, ensure_ascii=False)

    save_errors(predictions_metadata, out)

    cm = metrics.get("confusion_matrix", {}).get("matrix")
    labels_list = metrics.get("confusion_matrix", {}).get("labels")
    if cm and labels_list:
        plot_confusion_matrix(cm, labels_list, out / "plots" / "confusion_matrix.png")

    report_lines = []
    report_lines.append(f"# Evaluation Report\n\n")
    report_lines.append(f"Generated: {datetime.utcnow().isoformat()}Z\n\n")

    chosen_threshold = metrics.get("chosen_threshold", None)
    report_lines.append("## Quick summary\n\n")
    report_lines.append(f"- Chosen threshold: {chosen_threshold}\n")
    report_lines.append(f"- Macro F1: {metrics.get('macro_f1')}\n")
    report_lines.append(f"- Micro F1: {metrics.get('micro_f1')}\n")
    report_lines.append(f"- Accuracy: {metrics.get('accuracy')}\n")
    report_lines.append(f"- Coverage: {metrics.get('coverage')}\n\n")

    report_lines.append("## Top failure labels (false negatives)\n\n")

    fn_path = out / "errors" / "false_negatives.jsonl"
    try:
        if fn_path.exists():
            with fn_path.open("r", encoding="utf8") as f:
                fn_records = [json.loads(l) for l in f]
        else:
            fn_records = []
        if not fn_records:
            report_lines.append("No false negatives recorded.\n\n")
        else:
            label_to_examples = {}
            for rec in fn_records:
                lbl = rec.get("actual_label")
                label_to_examples.setdefault(lbl, []).append(rec)
            top_labels = sorted(label_to_examples.keys(), key=lambda L: -len(label_to_examples[L]))[:10]
            for lbl in top_labels:
                examples = label_to_examples[lbl][:3]
                report_lines.append(f"### {lbl} — {len(label_to_examples[lbl])} cases\n")
                for ex in examples:
                    sent = ex.get("sentence", "")[:300].replace("\n", " ")
                    pred = ex.get("assigned_label")
                    report_lines.append(f"- Predicted: **{pred}** — \"{sent}\"\n")
                report_lines.append("\n")
    except Exception:
        report_lines.append("Could not read false negatives file.\n\n")
    (out / "report.md").write_text("".join(report_lines), encoding="utf8")