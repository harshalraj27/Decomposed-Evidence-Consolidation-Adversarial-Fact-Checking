from .subclaim_pipeline import run_subclaim_pipeline
from .rule_decomposer import rule_decompose

claim = "Transformers are faster and more parallelizable than RNNs"

subclaims = rule_decompose(claim)

for sc in subclaims:
    print("\nSUBCLAIM:")
    print(sc.text,"\n", sc.type)
    out = run_subclaim_pipeline(sc, top_k=20, top_n=10)
    print(out["verdict"])
