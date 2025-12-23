import json
import pytest
import os

from app.llm_decomposer import llm_decomposer

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SANITY_PATH = os.path.join(PROJECT_ROOT, "data", "checking", "decomposer_sanity_test.json")

def load_sanity_set():
    with open(SANITY_PATH, "r", encoding="utf-8") as f:
        return json.load(f)["decomposer_sanity_set"]

@pytest.mark.parametrize("case", load_sanity_set())
def test_llm_decomposer_sanity_set(case):
    claim = case["claim"]
    expected = case["expected_verdict"]

    print(f"\nClaim: {claim}")
    print(f"Expected: {expected}")

    res = llm_decomposer(claim)

    print(f"Got verdict: {res['verdict']}")
    print(f"Got subclaims: {res['subclaims']}")

    assert isinstance(res, dict)
    assert "verdict" in res
    assert "subclaims" in res
    assert res["verdict"] in {"OK", "NO_DECOMPOSE", "ERROR"}
    assert isinstance(res["subclaims"], list)

    if expected == "DECOMPOSE":
        assert res["verdict"] == "OK"
        assert len(res["subclaims"]) > 0

        for sc in res["subclaims"]:
            assert isinstance(sc, dict)
            assert "text" in sc
            assert "type" in sc
            assert isinstance(sc["text"], str)
            assert len(sc["text"].strip()) >= 5

    elif expected == "UNCERTAIN":
        assert res["verdict"] == "NO_DECOMPOSE"
        assert res["subclaims"] == []