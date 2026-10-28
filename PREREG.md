# PREREGISTRATION — certify-horn (locked BEFORE the head-to-head run)

Locked: 2026-10-28, after G0 + G1 + PILOT GATE passed, before any
head-to-head number exists. Head-to-head seeds 5000-5199 were chosen
precisely because no pilot run, test, or exploratory run touched
them (pilot used 1000-1039; tests used 1000-1099 lookups only for
kind fixtures, never 5000+). No head-to-head row exists at lock time.

## Protocol (frozen)

- Paired design: the SAME generated case is run through all three
  arms (cert, control, baseline). One decision outcome per case per arm.
- n = 200 cases (seeds 5000-5199). Kind cycles seed % 4: answerable,
  twin_missing, twin_binding, entity_soup (50 each in expectation;
  exact mix is whatever the generator yields -- reported, not adjusted).
- Oracle (frozen): decision correct = answer on answerable cases,
  abstain on unanswerable twins. Answer correctness (secondary) =
  answered value equals gold country, among answered answerable cases.
- Statistics: paired bootstrap 95% CI, B = 10,000 resamples,
  RNG seed 12345, percentile method, computed over case indices.
- No LLMs anywhere. No local model anywhere. CPU only, $0.
- Determinism check: re-running the head-to-head script must
  reproduce the results file byte-for-byte (SHA-256 recorded).

## Disease (G2) — PASS bars, all required

- G2a: paired bootstrap 95% CI for (cert decision accuracy minus
  baseline decision accuracy) EXCLUDES 0.
- G2b: point estimate of that gap is >= 0.10 (10pp; paper-calibrated:
  the paper's entity checks add 4-13pp of decision accuracy, so a
  10pp bar sits inside the paper's reported range, not above it).
- G2c: cert decision accuracy itself is >= 0.80 (the disease must be a
  real effect, not a both-arms-bad relative gap).
- If any fails, G2 FAILS and the project is KILLED (no bar-moving).

## Load-bearing (G3) — PASS bars, all required

- G3a: paired bootstrap 95% CI for (cert minus control decision
  accuracy) EXCLUDES 0.
- G3b: point estimate of that gap is >= 0.05 (5pp).
- The control uses the SAME entity-checked links and the SAME
  certificate-answer rule, minus unification binding only, so a pass
  attributes the gain to Horn closure with unification, not to entity
  checks or to the answer rule alone.
- If any fails, G3 FAILS and the project is KILLED.

## Reporting

- Report all three arms' decision accuracy and answer correctness,
  both gaps with CIs, n, seeds, and the determinism hash -- whether or
  not bars pass.
- Paper figures from arXiv 2610.34684 (entity checks +4-13pp,
  certificate answers 80% vs 57% from all passages) are context only
  and are NEVER reported as reproduced results.
- All results are scripted/synthetic (deterministic rule-based
  generator, toy 2-fact Horn rule), never real-model measurements. Say
  so plainly in PAPER.md and any draft.
