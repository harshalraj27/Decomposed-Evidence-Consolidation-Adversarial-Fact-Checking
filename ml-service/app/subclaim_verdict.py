from .config import *

def get_verdict(aggregator_output):
    total_strength = aggregator_output['total_strength']
    support_strength = aggregator_output['support_strength']
    contradict_strength = aggregator_output['contradict_strength']

    if (total_strength < 0.2):
        label = "INCONCLUSIVE"

    if(total_strength>0):
        support_ratio = support_strength / total_strength
        contradict_ratio = contradict_strength / total_strength

    if (support_ratio > 0.35 and contradict_ratio > 0.35):
        label = "MIXED"
    elif(support_ratio>=0.65):
        label = "SUPPORT"
    elif(contradict_ratio>=0.65):
        label = "CONTRADICT"
    else:
        label = "INCONCLUSIVE"

    return label, total_strength, support_strength, contradict_strength