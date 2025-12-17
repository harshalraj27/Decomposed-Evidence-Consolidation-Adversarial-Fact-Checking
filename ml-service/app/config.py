import json
from pathlib import Path

with open(Path(__file__).parent / 'config.json', 'r', encoding='utf-8') as f:
    cfg = json.load(f)

M = 32
efConstruction = 200
efSearch = 64

mpnet_base = cfg['mpnet-base']
e5 = cfg['E5-large']
gte = cfg['gte-large']

metas_file = Path(cfg['metas_path'])
faiss_index = Path(cfg['faiss_index_path'])
local_dir = Path(cfg['local_files_path'])
ingested_dir = Path(cfg['ingested_files_path'])
ingested_meta_dir = Path(cfg['ingested_files_meta_path'])
ingested_pdf_dir = Path(cfg['ingested_pdf_path'])
ingested_cleaned_dir = Path(cfg['ingested_cleaned_path'])
ingested_raw_dir = Path(cfg['ingested_raw_path'])

topk = cfg.get('top_k', 100)

label_eval_dir = Path(cfg['label_eval_path'])
label_test_file = Path(cfg.get('label_test_file', cfg.get('label_test')))

labels = ['science', 'maths', 'technology', 'politics/government', 'health/medicine',
          'economy/finance', 'environment/climate', 'history', 'general knowledge']

threshold = 0.3
device = 0
wiki_language = 'en'