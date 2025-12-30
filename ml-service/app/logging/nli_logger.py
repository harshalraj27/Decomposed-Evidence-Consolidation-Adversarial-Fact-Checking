import json
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).resolve().parents[1]  # app/
LOG_PATH = BASE_DIR / "peft" / "data" / "nli_train.jsonl"

LOG_PATH.parent.mkdir(parents=True, exist_ok=True)

def log_nli_pair(claim, evidence, probs, pred, category="pipeline_mined"):
    record = {
        "claim": claim,
        "evidence": evidence,
        "pred": pred,
        "probs": probs,
        "category": category,
        "timestamp": datetime.utcnow().isoformat()
    }
    with open(LOG_PATH, "a", encoding="utf8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")
