import sklearn
import numpy as np
import pandas as pd
from .config import *
from .label_classification import classify

def load_file():
    if not label_test_file.exists():
        return "Error loading test data"
    data = []
    with open(label_test_file, "r", encoding="utf-8") as f:
        for line in f:
            line = json.loads(line)
            data.append(line)
        return data

def x_y_split(data):
    X = []
    y = []
    for line in data:
        X.append(line['sentence'])
        y.append(line['label'])
    return X, y

def tune_model():
    data = load_file()
    if data=="Error loading test data":
        return
    X, y = x_y_split(data)



