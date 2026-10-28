# certify-horn — Horn-closure certificates for RAG sufficiency

Scoped CPU replication of arXiv 2610.34684, "Knowing When the Evidence
Is Enough: Requirement-Directed Search with Horn-Closure Certificates"
(Xinyu Zhang, Weiwei Sun), built from the abstract only. No author code
was used (none found as of 2026-10-28); no LLM is used anywhere.

## The idea in one paragraph

After each search, a RAG system must decide: answer, search again, or
abstain. Holistic model judgement can accept a context that names every
entity yet lacks one required fact. Certify instead states requirements
as a hypergraph — which facts jointly yield another fact — searches per
requirement, accepts links only after entity checks, and runs Horn
closure over the links. Closure reaching the target yields a
certificate: the minimal sufficient passages plus their derivation.
Otherwise the system abstains, naming the open requirements.

## This replication (synthetic, deterministic)

One Horn rule, one question family: "Of which country is person P a
citizen?" — `born(P, C) AND capital(C, K) -> citizen(P, K)`, where the
city `C` is a variable shared across the rule body. Three paired arms
run on the same synthetic case:

- **cert** — entity-checked links + Horn closure with unification;
  answers only from the certificate derivation, else abstains.
- **control** — same entity-checked links, but propositional closure
  with no variable binding (flat predicate coverage dressed as closure).
- **baseline** — holistic-judge proxy: no entity check, no closure;
  answers iff every required predicate occurs anywhere and every
  question entity is mentioned; answer value = modal country among all
  retrieved capital passages (distractor dilution).

Case kinds: answerable, unanswerable twins (missing fact, broken
binding, entity-soup where all entities are named but the relation is
absent).

## Measured results (head-to-head, seeds 5000-5199, n = 200)

| Arm | Decision accuracy | Answer correctness (answered answerable) |
|---|---|---|
| cert | 100.0% (200/200) | 100.0% (50/50) |
| control | 37.5% (75/200) | 16.0% (8/50) |
| baseline | 25.0% (50/200) | 0.0% (0/50) |

- G2 (disease): cert − baseline **+75.0pp, 95% CI [69.0pp, 81.0pp]** —
  bar ≥ +10pp with CI excluding 0: PASS.
- G3 (load-bearing): cert − control **+62.5pp, 95% CI [55.5pp, 69.0pp]** —
  bar ≥ +5pp with CI excluding 0: PASS. The gain is attributable to
  Horn closure with unification, not to entity checks alone.

Determinism: re-running `scripts/run_head_to_head.py` reproduces
`results/head_to_head_rows.jsonl` byte-for-byte, SHA-256
`7d1c899e36e2a35c4eb1ce7be88de305973cc17cc0483455fbab8e05f0a9c8c7`.

## Run it

```bash
python3 -m pytest tests/ -q
python3 scripts/run_pilot.py            # calibration, seeds 1000-1039
python3 scripts/run_head_to_head.py     # prereg-locked, seeds 5000-5199
```

CPU only, $0, no network, no model downloads. Python 3.12, pytest.

## Honest limits

- Synthetic toy: one 2-fact Horn rule, scripted generator, no real
  retrieval, no Wikipedia scale, no LLM. Cert's 100% reflects the
  generator's construction (distractors never break a gold binding),
  not a claim about real RAG systems.
- The paper's figures (+4–13pp from entity checks; certificate answers
  80% vs 57% from all passages) are CONTEXT ONLY and were NOT
  reproduced here. Nothing here is a measurement on the paper's corpora.
- The baseline is a deliberately simple holistic-judge proxy, not the
  paper's search agents, graph retrieval, or sufficiency judges.
- Bars, protocol, and statistics were locked in PREREG.md before the
  head-to-head run and never moved; see KILLGATE.md for gate verdicts.
