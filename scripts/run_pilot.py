"""Pilot: seeds 1000-1039 (n=40). Calibration only -- never used for bars."""
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
    for seed in range(1000, 1040):
        case = generate_case(seed)
        row = {"seed": seed, "kind": case.kind, "answerable": case.answerable}
        for arm in ARMS:
            out = run_arm(case, arm)
            dc = int(decision_correct(case, out))
            per_arm[arm].append(dc)
            ac = answer_correct(case, out)
            if ac is not None:
                ans_corr[arm].append(int(ac))
            row[arm] = {"decision": out["decision"], "answer": out["answer"],
                        "decision_correct": dc, "answer_correct": ac}
        rows.append(row)
    summary = {
        "n": len(rows),
        "decision_accuracy": {a: sum(v) / len(v) for a, v in per_arm.items()},
        "answer_correctness_answered_answerable": {
            a: (sum(v) / len(v) if v else None) for a, v in ans_corr.items()},
        "gaps": {
            "cert_minus_baseline": paired_diff_ci(per_arm["cert"], per_arm["baseline"]),
            "cert_minus_control": paired_diff_ci(per_arm["cert"], per_arm["control"]),
        },
    }
    out_dir = Path(__file__).resolve().parents[1] / "results"
    out_dir.mkdir(exist_ok=True)
    (out_dir / "pilot_rows.jsonl").write_text(
        "".join(json.dumps(r) + "\n" for r in rows))
    (out_dir / "pilot_summary.json").write_text(json.dumps(summary, indent=2))
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
