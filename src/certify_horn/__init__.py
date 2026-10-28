"""certify-horn: scoped CPU replication of Horn-closure certificates for
RAG sufficiency (arXiv 2610.34684, Zhang & Sun), from the abstract only.

No author code was used (none found as of 2026-10-28); no LLM is used
anywhere; all cases are synthetic and deterministic.
"""
from .model import Atom, Rule, Passage, Case, generate_case
from .closure import horn_closure, propositional_closure, decide_cert
from .arms import run_arm

__all__ = [
    "Atom", "Rule", "Passage", "Case", "generate_case",
    "horn_closure", "propositional_closure", "decide_cert", "run_arm",
]
