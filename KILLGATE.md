# KILLGATE — certify-horn (project #89)

Paper: arXiv 2610.34684, "Knowing When the Evidence Is Enough:
Requirement-Directed Search with Horn-Closure Certificates"
(Xinyu Zhang, Weiwei Sun; submitted 26 Oct 2026). Abstract read live
from arxiv.org/abs/2610.34684 on 2026-10-28.

Live-abstract claims (CONTEXT ONLY, never presented as reproduced):
- Per-query requirement hypergraph: which facts jointly yield another.
- Certify decomposes the question, searches per requirement, accepts
  links only after entity checks; Horn closure over links yields a
  certificate (minimal sufficient passages + derivation) or an
  abstention naming open requirements.
- Given correct retrieval, requirements and links, the decision is
  sound, and complete up to the entity check.
- Pooled over three corpora with unanswerable twins, beats search
  agents, graph retrieval and sufficiency judges in default configs;
  matches a proprietary model's sufficiency label without an extra
  model call on the same evidence.
- Over 21M Wikipedia passages, entity checks add 4-13 points of
  decision accuracy where gold evidence exists.
- Answers from its certificate are 80% correct vs 57% from all
  retrieved passages.
- The abstract page shows NO author-code link (only generic
  arXivLabs/Code-Data toggle placeholders, no repository URL).

Gate order is conjunctive. Any FAIL = KILL (KILLED.md + negative
PAPER.md, no repo/push/draft). Bars are never moved after locking.

## Gate verdicts

- STEP 0 — live abstract read: PASS (2026-10-28; claims above).
- G1 — author-code recheck: PASS (2026-10-28). Searched: arXiv abs
  page code links (none shown), exact-title web search, author-name
  web search ("Xinyu Zhang" + "Weiwei Sun" + Certify/Horn), and
  GitHub API search_repositories ("Certify Horn closure" and
  "2610.34684", both total_count 0). No official author repository
  found. Paper is 2 days old at build time; absence is as of
  2026-10-28 and is re-checked before any future push. This is a
  web-search absence, not an exhaustive GitHub API proof -- stated
  honestly in PAPER.md.
- G0 — harness + tests green: PASS (2026-10-28; pytest 8/8).
- PILOT GATE — disease signal at pilot scale: PASS (2026-10-28;
  seeds 1000-1039, n=40: cert decision accuracy 1.000, control 0.375,
  baseline 0.250; cert-minus-baseline +75.0pp, 95% CI [62.5pp, 87.5pp];
  cert-minus-control +62.5pp, 95% CI [47.5pp, 77.5pp]; cert answer
  correctness 1.000 on answered answerable cases vs baseline 0.000.
  Pilot is calibration only; bars were locked after it, head-to-head
  uses fresh seeds 5000-5199.)
- G2 — disease: PASS (2026-10-28; head-to-head seeds 5000-5199,
  n=200: cert decision accuracy 1.000, baseline 0.250, gap +0.750,
  paired bootstrap 95% CI [0.690, 0.810]; bars were CI excludes 0,
  point >= 0.10, cert accuracy >= 0.80 -- all met, bars unmoved).
- G3 — load-bearing: PASS (2026-10-28; cert 1.000 vs control 0.375,
  gap +0.625, 95% CI [0.555, 0.690]; bars were CI excludes 0,
  point >= 0.05 -- both met, bars unmoved).
- Determinism: PASS (2026-10-28; head-to-head rerun reproduces
  head_to_head_rows.jsonl byte-for-byte, SHA-256
  7d1c899e36e2a35c4eb1ce7be88de305973cc17cc0483455fbab8e05f0a9c8c7).
- OVERALL: PASS -- staged payload, PAPER.md, DRAFT ONLY LinkedIn
  draft; REPO NEEDED via parent's browser flow.
