from .config import *

def get_verdict(aggregator_output):
    total_strength = aggregator_output['total_strength']
    support_strength = aggregator_output['support_strength']
    contradict_strength = aggregator_output['contradict_strength']

    if (total_strength < 0.2):
        return "INCONCLUSIVE", total_strength, support_strength, contradict_strength

    support_ratio = support_strength / total_strength
    contradict_ratio = contradict_strength / total_strength

    if (support_ratio > 0.35 and contradict_ratio > 0.35):
        verdict = "MIXED"
    elif(support_ratio>=0.65):
        verdict = "SUPPORT"
    elif(contradict_ratio>=0.65):
        verdict = "CONTRADICT"
    else:
        verdict = "INCONCLUSIVE"

    return verdict, total_strength, support_strength, contradict_strength

def get_controversy(aggregator_output, verdict):
    total_strength = aggregator_output["total_strength"]
    support_strength = aggregator_output["support_strength"]
    contradict_strength = aggregator_output["contradict_strength"]

    if total_strength <= 0:
        return False

    support_ratio = support_strength / total_strength
    contradict_ratio = contradict_strength / total_strength

    if verdict == "MIXED":
        return True

    if support_ratio > 0.25 and contradict_ratio > 0.25:
        return True

    return False