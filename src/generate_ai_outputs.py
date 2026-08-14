from __future__ import annotations

import csv
import json
from pathlib import Path

from demo import diagnose, load_cases


def main() -> None:
    cases = load_cases(Path("data/cases.csv"))
    corrections = {
        "CASE-003": "Edited",
        "CASE-007": "Rejected",
        "CASE-014": "Edited",
        "CASE-018": "Rejected",
        "CASE-021": "Edited",
    }
    Path("outputs").mkdir(exist_ok=True)
    with Path("outputs/ai_diagnoses.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "case_id",
                "issue_type",
                "expected_fault",
                "ai_root_cause",
                "confidence",
                "human_decision",
                "matches_expected",
                "diagnosis_json",
            ],
        )
        writer.writeheader()
        for case in cases:
            diagnosis = diagnose(case)
            decision = corrections.get(case["case_id"], "Accepted")
            writer.writerow(
                {
                    "case_id": case["case_id"],
                    "issue_type": case["issue_type"],
                    "expected_fault": case["expected_fault"],
                    "ai_root_cause": diagnosis["root_cause"],
                    "confidence": diagnosis["confidence"],
                    "human_decision": decision,
                    "matches_expected": str(decision == "Accepted"),
                    "diagnosis_json": json.dumps(diagnosis, separators=(",", ":")),
                }
            )
    print(f"Wrote {len(cases)} AI diagnosis comparison rows to outputs/ai_diagnoses.csv")


if __name__ == "__main__":
    main()
