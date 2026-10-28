"""Paired bootstrap 95% CI for a difference of per-case 0/1 outcomes.

Percentile method, B resamples, fixed RNG seed. Operates on paired
differences so the CI is for the within-case gap, not two independent
rates.
"""
from __future__ import annotations

import random


def paired_diff_ci(a: list[int], b: list[int], B: int = 10000, seed: int = 12345):
    """CI for mean(a) - mean(b) over paired cases."""
    assert len(a) == len(b) and len(a) > 0
    diffs = [x - y for x, y in zip(a, b)]
    rng = random.Random(seed)
    n = len(diffs)
    boots = []
    for _ in range(B):
        boots.append(sum(rng.choice(diffs) for _ in range(n)) / n)
    boots.sort()
    lo = boots[int(0.025 * B)]
    hi = boots[int(0.975 * B) - 1]
    return {"point": sum(diffs) / n, "ci95": [lo, hi], "B": B, "seed": seed}
