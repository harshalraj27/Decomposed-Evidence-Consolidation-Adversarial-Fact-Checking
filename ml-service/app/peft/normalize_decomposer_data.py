import json

inp = "app/peft/decomposer_peft_data/decomposer_train_raw.json"
out = "app/peft/decomposer_peft_data/decomposer_train.jsonl"

cleaned = []

with open(inp, "r", encoding="utf-8") as f:
    data = json.load(f)
    for ex in data:

        verdict = ex["output"]["verdict"]
        if verdict not in ["OK", "NO_DECOMPOSE"]:
            continue

        if verdict == "NO_DECOMPOSE":
            ex["output"]["subclaims"] = []

        ex = {
            "input": ex["input"],
            "output": {
                "verdict": verdict,
                "subclaims": ex["output"]["subclaims"]
            }
        }

        cleaned.append(ex)

with open(out, "w", encoding="utf-8") as f:
    for ex in cleaned:
        f.write(json.dumps(ex, ensure_ascii=False) + "\n")

print("Saved", len(cleaned), "examples")
