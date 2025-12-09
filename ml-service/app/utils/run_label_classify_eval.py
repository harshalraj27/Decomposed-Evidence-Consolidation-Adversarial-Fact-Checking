from ..eval_label_classifier import (
    load_file,
    run_one_threshold,
    sweep_thresholds,
    run_ablation_set,
    write_final_outputs
)
from ..config import labels, label_eval_dir

def main():
    data = load_file()
    preds, metrics = run_one_threshold(0.3, data, 16, labels)
    write_final_outputs(preds, metrics, out_dir=label_eval_dir / "simple_optimised")

    best, sweep_results = sweep_thresholds(
        data_records=data,
        labels_list=labels,
        sweep_from=0.25,
        sweep_to=0.70,
        sweep_step=0.025,
        out_dir=label_eval_dir / "sweep_optimised",
        batch_size=16,
        metric_to_opt="macro_f1"
    )

    preds_best, metrics_best = run_one_threshold(best["threshold"], data, 16, labels)
    metrics_best["chosen_threshold"] = best["threshold"]
    write_final_outputs(preds_best, metrics_best, sweep_results, out_dir=label_eval_dir / "sweep_optimised")

    ablations = {
        "low_threshold": {"threshold": 0.15},
        "high_threshold": {"threshold": 0.70}
    }
    run_ablation_set(data, labels, ablations, out_dir=label_eval_dir / "ablation_optimised")

    print("Saved all evaluation outputs to:", label_eval_dir)

if __name__ == "__main__":
    main()
