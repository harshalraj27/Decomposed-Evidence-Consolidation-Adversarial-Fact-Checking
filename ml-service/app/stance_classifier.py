import torch
import torch.nn.functional as F

from transformers import AutoTokenizer, AutoModelForSequenceClassification

from .config import roberta_large, support_threshold, contradict_threshold, delta

label_mapping = {
    "entailment": "support",
    "contradiction": "contradict",
    "neutral": "neutral"
}

model = AutoModelForSequenceClassification.from_pretrained(roberta_large)
tokenizer = AutoTokenizer.from_pretrained(roberta_large)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)
model.eval()



def stance_score(subclaim, evidence):
    inputs = tokenizer(evidence, subclaim, truncation=True,
                       padding=True, return_tensors="pt").to(device)

    with torch.no_grad():
        outputs = model(**inputs)
        logits = outputs.logits
        probs = F.softmax(logits, dim=-1).squeeze(0)

    id2label = model.config.id2label

    scores = {
        id2label[i].lower(): probs[i].item()
        for i in range(len(probs))
    }
    labels= {label_mapping[k]: v for k, v in scores.items()}
    stance = choose_stance(labels)

    return stance, labels

def choose_stance(labels):
    if(labels["support"]>support_threshold):
        label = "support"
    elif(labels["contradict"]>contradict_threshold):
        label = "contradict"
    else:
        label = "neutral"
        return label

    if(label=='support' and labels['support']>support_threshold):
        if(labels['support']-labels['neutral']<delta):
            label = "neutral"
    if(label=='contradict' and labels['contradict']>contradict_threshold):
        if(labels['contradict']-labels['neutral']<delta):
            label = "neutral"
    return label