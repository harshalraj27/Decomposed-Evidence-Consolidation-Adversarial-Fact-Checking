import json
from pathlib import Path

with open(Path(__file__).parent / 'config.json', 'r', encoding='utf-8') as f:
    cfg = json.load(f)

model_name = cfg['model_name']
metas_file = Path(cfg['metas_path'])
faiss_index = Path(cfg['faiss_index_path'])
raw_dir = Path(cfg['raw_data_path'])
top_k = cfg.get('top_k', 5)