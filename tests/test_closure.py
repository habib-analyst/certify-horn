import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from certify_horn.arms import answer_correct, decision_correct, run_arm
from certify_horn.closure import decide_cert
from certify_horn.model import generate_case
from certify_horn.stats import paired_diff_ci


def _case_of_kind(kind):
    # kinds cycle seed % 4: 0 answerable, 1 twin_missing, 2 twin_binding, 3 entity_soup
    idx = {"answerable": 0, "twin_missing": 1, "twin_binding": 2, "entity_soup": 3}[kind]
    for seed in range(1000, 1100):
        c = generate_case(seed)
        if seed % 4 == idx and c.kind == kind:
            return c
    raise AssertionError(kind)


def test_answerable_cert_answers_correctly_with_2_passage_certificate():
    c = _case_of_kind("answerable")
    out = run_arm(c, "cert")
    assert out["decision"] == "answer"
    assert out["answer"] == c.gold_answer
    assert out["cert_size"] == 2  # born + capital, the minimal derivation


def test_twin_binding_cert_abstains_control_answers():
    c = _case_of_kind("twin_binding")
    assert not c.answerable
    assert run_arm(c, "cert")["decision"] == "abstain"
    assert run_arm(c, "control")["decision"] == "answer"  # binding-blind


def test_unanswerable_twins_cert_abstains():
    for kind in ("twin_missing", "entity_soup"):
        c = _case_of_kind(kind)
        assert run_arm(c, "cert")["decision"] == "abstain"


def test_baseline_answers_even_on_unanswerable():
    # Holistic predicate-presence + entity-mention judge: the disease.
    for kind in ("twin_missing", "twin_binding", "entity_soup"):
        c = _case_of_kind(kind)
        assert run_arm(c, "baseline")["decision"] == "answer"


def test_generator_deterministic():
    a, b = generate_case(1042), generate_case(1042)
    assert [(p.atom, p.mentions) for p in a.passages] == [(p.atom, p.mentions) for p in b.passages]


def test_decision_correctness_flags():
    c = _case_of_kind("answerable")
    assert decision_correct(c, run_arm(c, "cert"))
    assert answer_correct(c, run_arm(c, "cert")) is True
    assert answer_correct(_case_of_kind("twin_binding"), run_arm(_case_of_kind("twin_binding"), "cert")) is None


def test_paired_ci_excludes_zero_on_known_gap():
    a = [1] * 30 + [0] * 10
    b = [0] * 40
    r = paired_diff_ci(a, b, B=2000, seed=12345)
    assert r["ci95"][0] > 0
    assert abs(r["point"] - 0.75) < 1e-9


def test_open_requirements_named_on_abstention():
    c = _case_of_kind("twin_binding")
    _, _, _, open_reqs = decide_cert(c, use_unification=True)
    assert open_reqs, "abstention must name open requirements"
