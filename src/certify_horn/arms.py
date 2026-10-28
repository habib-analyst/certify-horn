"""Three decision arms, run on the SAME case (paired design).

CERT: entity-checked links + unification Horn closure; answer only
  from the certificate derivation; else abstain naming open reqs.
CONTROL: entity-checked links + propositional closure (no binding);
  same certificate-answer rule otherwise. Isolates unification.
BASELINE (holistic judge proxy): no entity check, no closure; answer
  iff every required predicate occurs anywhere in the retrieved set
  AND every question entity is mentioned somewhere; answer value =
  the modal country among ALL retrieved capital passages (distractor
  dilution). This is the "holistic judgement" the paper criticises.
"""
from __future__ import annotations

from collections import Counter

from .closure import decide_cert
from .model import Case


def run_arm(case: Case, arm: str):
    if arm == "cert":
        decision, answer, cert, open_reqs = decide_cert(case, use_unification=True)
        return {"arm": arm, "decision": decision, "answer": answer,
                "cert_size": len(cert), "open": open_reqs}
    if arm == "control":
        decision, answer, cert, open_reqs = decide_cert(case, use_unification=False)
        return {"arm": arm, "decision": decision, "answer": answer,
                "cert_size": len(cert), "open": open_reqs}
    if arm == "baseline":
        preds = {p.atom.pred for p in case.passages}
        mentioned = set()
        for p in case.passages:
            mentioned.update(p.atom.args)
            mentioned.update(p.mentions)
        has_all = {"born", "capital"} <= preds
        names_all = {case.person, case.city, case.country} <= mentioned
        if has_all and names_all:
            caps = [p.atom.args[1] for p in case.passages if p.atom.pred == "capital"]
            answer = Counter(caps).most_common(1)[0][0]
            return {"arm": arm, "decision": "answer", "answer": answer,
                    "cert_size": 0, "open": []}
        return {"arm": arm, "decision": "abstain", "answer": "",
                "cert_size": 0, "open": ["requirements not all present"]}
    raise ValueError(arm)


def decision_correct(case: Case, out: dict) -> bool:
    """Decision accuracy: answer on answerable, abstain on unanswerable."""
    return (out["decision"] == "answer") == case.answerable


def answer_correct(case: Case, out: dict) -> bool | None:
    """Answer correctness among answered answerable cases (None if N/A)."""
    if not case.answerable or out["decision"] != "answer":
        return None
    return out["answer"] == case.gold_answer
