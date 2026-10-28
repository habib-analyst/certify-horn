"""Head-to-head: seeds 5000-5199 (n=200). PREREG-locked; run once, then
a determinism rerun must reproduce results_head_to_head.json exactly.
"""
import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from certify_horn.arms import answer_correct, decision_correct, run_arm
from certify_horn.model import generate_case
from certify_horn.stats import paired_diff_ci

ARMS = ("cert", "control", "baseline")


def main():
    rows = []
    per_arm = {a: [] for a in ARMS}
    ans_corr = {a: [] for a in ARMS}
    kinds = {}
    for seed in range(5000, 5200):
        case = generate_case(seed)
        kinds[case.kind] = kinds.get(case.kind, 0) + 1
        row = {"seed": seed, "kind": case.kind, "answerable": case.answerable}
        for arm in ARMS:
            out = run_arm(case, arm)
            dc = int(decision_correct(case, out))
            per_arm[arm].append(dc)
            ac = answer_correct(case, out)
            if ac is not None:
                ans_corr[arm].append(int(ac))
            row[arm] = {"decision": out["decision"], "answer": out["answer"],
                        "decision_correct": dc, "answer_correct": ac,
                        "cert_size": out["cert_size"], "open": out["open"]}
        rows.append(row)
    summary = {
        "n": len(rows), "seeds": "5000-5199", "kind_mix": kinds,
        "decision_accuracy": {a: sum(v) / len(v) for a, v in per_arm.items()},
        "answer_correctness_answered_answerable": {
            a: {"rate": (sum(v) / len(v) if v else None), "n": len(v)}
            for a, v in ans_corr.items()},
        "gaps": {
            "cert_minus_baseline": paired_diff_ci(per_arm["cert"], per_arm["baseline"]),
            "cert_minus_control": paired_diff_ci(per_arm["cert"], per_arm["control"]),
        },
    }
    out_dir = Path(__file__).resolve().parents[1] / "results"
    out_dir.mkdir(exist_ok=True)
    rows_text = "".join(json.dumps(r, sort_keys=True) + "\n" for r in rows)
    (out_dir / "head_to_head_rows.jsonl").write_text(rows_text)
    (out_dir / "head_to_head_summary.json").write_text(json.dumps(summary, indent=2))
    digest = hashlib.sha256(rows_text.encode()).hexdigest()
    print(json.dumps(summary, indent=2))
    print("rows_sha256:", digest)


if __name__ == "__main__":
    main()
