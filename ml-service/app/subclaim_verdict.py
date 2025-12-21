from .config import *

def get_verdict(aggregator_output):
    total_strength = aggregator_output['total_strength']
    support_strength = aggregator_output['support_strength']
    contradict_strength = aggregator_output['contradict_strength']

    support_ratio = support_strength / total_strength
    contradict_ratio = contradict_strength / total_strength

    if(total_strength<0.2):
        label = "INCONCLUSIVE"
    elif (support_ratio > 0.35 and contradict_ratio > 0.35):
        label = "MIXED"
    elif(support_strength>=2 and contradict_strength<0.3):
        label = "SUPPORT"
    elif(support_strength<0.3 and contradict_strength>=2):
        label = "CONTRADICT"
    else:
        label = "INCONCLUSIVE"

    return label, total_strength, support_strength, contradict_strength