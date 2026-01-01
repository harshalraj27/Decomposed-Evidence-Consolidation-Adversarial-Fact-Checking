import json
import torch

from datasets import load_dataset
from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
    TrainingArguments,
    Trainer,
    DataCollatorForLanguageModeling,
)
from peft import LoraConfig, get_peft_model

MODEL_ID = "meta-llama/Llama-3.1-8b-hf"
DATA_PATH = "app/peft/decomposer_peft_data/decomposer_train.jsonl"
OUT_DIR = "app/peft/decomposer_lora"
MAX_LEN = 2048

PROMPT = """You are a claim decomposition module.

Given a claim, decide whether it can be decomposed into factual subclaims.

Rules:
- If decomposable, output verdict = OK and list factual subclaims.
- If not decomposable, output verdict = NO_DECOMPOSE.
- Do NOT add external knowledge.
- Do NOT infer unstated facts.

Claim:
{input}
"""

dataset = load_dataset(
    "json",
    data_files=DATA_PATH
)["train"]

tokenizer = AutoTokenizer.from_pretrained(MODEL_ID)
tokenizer.pad_token = tokenizer.eos_token

model = AutoModelForCausalLM.from_pretrained(
    MODEL_ID,
    torch_dtype=torch.bfloat16,
    device_map="auto",
)

def format_example(example):
    instruction = PROMPT.format(input=example["input"])
    response = json.dumps(example["output"], ensure_ascii=False)
    return {"text": instruction + "\n" + response}

dataset = dataset.map(format_example)

def tokenize(example):
    tokens = tokenizer(
        example["text"],
        truncation=True,
        max_length=MAX_LEN,
        padding="max_length",
    )
    tokens["labels"] = tokens["input_ids"].copy()
    return tokens

dataset = dataset.map(tokenize, remove_columns=dataset.column_names)

lora_config = LoraConfig(
    r=8,
    lora_alpha=16,
    lora_dropout=0.05,
    bias="none",
    task_type="CAUSAL_LM",
    target_modules=[
        "q_proj",
        "k_proj",
        "v_proj",
        "o_proj",
    ],
)

model = get_peft_model(model, lora_config)
model.print_trainable_parameters()

training_args = TrainingArguments(
    output_dir=OUT_DIR,
    per_device_train_batch_size=1,
    gradient_accumulation_steps=8,
    num_train_epochs=3,
    learning_rate=2e-4,
    fp16=True,
    logging_steps=10,
    save_steps=500,
    save_total_limit=2,
    optim="paged_adamw_8bit",
    report_to="none",
    remove_unused_columns=False,
)

data_collator = DataCollatorForLanguageModeling(
    tokenizer=tokenizer,
    mlm=False,
)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=dataset,
    tokenizer=tokenizer,
    data_collator=data_collator,
)

trainer.train()

trainer.save_model(OUT_DIR)
tokenizer.save_pretrained(OUT_DIR)
