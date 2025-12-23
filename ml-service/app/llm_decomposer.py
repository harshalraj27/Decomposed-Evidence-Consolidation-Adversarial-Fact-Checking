import json
import re

from llama_cpp import Llama
from dataclasses import dataclass

from .config import llama_8B

@dataclass
class Subclaim:
    id: int
    text: str
    type: str
    source_claim: str

llm = Llama(
    model_path=llama_8B,
    n_ctx=4096,
    n_gpu_layers=35,
    n_threads=8,
    n_batch=512,
    verbose=False
)

PROMPT_TEMPLATE = """You are a claim decomposition module.

CORE PRINCIPLE: Only decompose if the claim contains multiple INDEPENDENT facts that can be verified separately. Each subclaim must be self-contained with complete context.

WHEN TO DECOMPOSE (verdict: "OK"):
- Claim explicitly joins multiple independent factual statements
- Each part can be fact-checked independently
- Each subclaim remains fully understandable on its own

WHEN NOT TO DECOMPOSE (verdict: "NO_DECOMPOSE"):
- Single factual statement
- Comparative/evaluative claims (better, worse, more effective)
- Opinions or subjective judgments
- Claims where splitting loses essential meaning

OUTPUT FORMAT:
{{
  "verdict": "OK",
  "subclaims": [
    {{"text": "complete self-contained statement", "type": "FACTUAL"}}
  ]
}}

OR

{{
  "verdict": "NO_DECOMPOSE",
  "subclaims": []
}}

INPUT CLAIM: "{CLAIM}"

JSON OUTPUT:"""

def build_decomposer_prompt(claim: str) -> str:
    return PROMPT_TEMPLATE.replace("{CLAIM}", claim)

def extract_json(text: str):
    text = text.strip()
    text = re.sub(r'\s*\([^)]*\)\s*$', '', text)

    start = text.find('{')
    end = text.rfind('}')

    if start == -1 or end == -1:
        return None

    json_str = text[start:end + 1]
    json_str = json_str.replace('{{', '{').replace('}}', '}')

    try:
        return json.loads(json_str)
    except json.JSONDecodeError:
        try:
            cleaned = re.sub(r'[^\{\}\[\]":,\w\s-]', '', json_str)
            return json.loads(cleaned)
        except:
            return None

def llm_decomposer(claim: str):
    prompt = build_decomposer_prompt(claim)

    output = llm(
        prompt=prompt,
        max_tokens=512,
        temperature=0.0,
        stop=["\n\n", "Example", "Note:", "Replace", "#", "(", "because"]
    )

    text = output["choices"][0]["text"].strip()

    print("RAW LLM OUTPUT:\n", text)

    data = extract_json(text)

    if data is None:
        return {"verdict": "ERROR", "subclaims": []}

    if "verdict" not in data or "subclaims" not in data:
        return {"verdict": "ERROR", "subclaims": []}

    if data["verdict"] not in {"OK", "NO_DECOMPOSE", "ERROR"}:
        return {"verdict": "ERROR", "subclaims": []}

    if not isinstance(data["subclaims"], list):
        return {"verdict": "ERROR", "subclaims": []}

    if data["verdict"] == "OK" and not data["subclaims"]:
        return {"verdict": "ERROR", "subclaims": []}

    return data
