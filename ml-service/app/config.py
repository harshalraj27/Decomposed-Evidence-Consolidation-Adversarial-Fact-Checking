import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
CONFIG_DIR = Path(__file__).resolve().parent

with open(CONFIG_DIR / "config.json", "r", encoding="utf-8") as f:
    cfg = json.load(f)

M = 32
efConstruction = 200
efSearch = 64

mpnet_base = cfg["mpnet-base"]
e5 = cfg["E5-large"]
gte = cfg["gte-large"]
ms_marco_6 = cfg["ms-marco-6"]
ms_marco_12 = cfg["ms-marco-12"]
roberta_large = cfg["roberta-large"]

metas_file = BASE_DIR / cfg["metas_path"]
faiss_index = BASE_DIR / cfg["faiss_index_path"]
local_dir = BASE_DIR / cfg["local_files_path"]

ingested_dir = BASE_DIR / cfg["ingested_files_path"]
ingested_meta_dir = BASE_DIR / cfg["ingested_files_meta_path"]
ingested_pdf_dir = BASE_DIR / cfg["ingested_pdf_path"]
ingested_raw_dir = BASE_DIR / cfg["ingested_raw_path"]
ingested_cleaned_dir = BASE_DIR / cfg["ingested_cleaned_path"]

topk = cfg.get("top_k", 100)

label_eval_dir = BASE_DIR / cfg["label_eval_path"]
label_test_file = BASE_DIR / cfg.get("label_test_file", cfg.get("label_test"))
stance_eval_dir = BASE_DIR / cfg["stance_eval_path"]

labels = [
    "science",
    "maths",
    "technology",
    "politics/government",
    "health/medicine",
    "economy/finance",
    "environment/climate",
    "history",
    "general knowledge",
]

threshold = 0.3
device = 0
wiki_language = "en"
support_threshold = 0.6
contradict_threshold = 0.6
delta = 0.2
epsilon = 0.1
