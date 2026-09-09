# NetSage AI

AI-assisted troubleshooting helper for Cisco-style Packet Tracer labs.

NetSage reads symptoms, topology notes, and show-command evidence, then produces a structured diagnosis that must be reviewed by a human before any fix is accepted.

## What is included

- `data/cases.csv`: 32 troubleshooting cases covering VLAN, gateway, DHCP, DNS, routing, ACL, NAT, and wireless issues.
- `prompts/diagnose_prompt.md`: JSON-only diagnosis prompt with worked examples.
- `prompts/review_prompt.md`: human review checklist prompt.
- `src/rule_checker.py`: deterministic checks for duplicate IPs, wrong masks, gateway mismatch, interface down, missing VLAN, and missing routes.
- `src/demo.py`: runs one broken-lab diagnosis flow and writes sample outputs.
- `src/generate_ai_outputs.py`: creates a saved diagnosis/comparison row for every case.
- `dashboard/index.html`: local dashboard summarizing issue types, severity, AI vs human agreement, and a reviewed demo case.
- `outputs/responsible_ai_log.csv`: examples where human reviewers corrected AI outputs.
## How it works

NetSage AI analyzes network symptoms, topology details, and show-command evidence using rule-based checks and AI-generated diagnosis. The diagnosis is then reviewed by a human and marked as `Accepted`, `Edited`, or `Rejected` before any fix is applied.
## Quick start

```powershell
python src\rule_checker.py --cases data\cases.csv --out outputs\rule_check_results.csv
python src\generate_ai_outputs.py
python src\demo.py --case-id CASE-001
```

Open `dashboard\index.html` in a browser to view the dashboard.

## Review policy

Every AI diagnosis is provisional. A reviewer must mark it as `Accepted`, `Edited`, or `Rejected` before a fix is used in the lab.
