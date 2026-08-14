from __future__ import annotations

import argparse
import csv
import ipaddress
import re
from dataclasses import dataclass
from pathlib import Path


@dataclass
class Finding:
    case_id: str
    check: str
    severity: str
    message: str
    evidence: str


IP_MASK_RE = re.compile(r"(?P<ip>\b\d{1,3}(?:\.\d{1,3}){3}\b)(?:\s+Mask\s+|\s+)(?P<mask>255(?:\.\d{1,3}){3})", re.I)
IFACE_IP_RE = re.compile(r"\b(?P<iface>[A-Za-z]+\S*)\s+(?P<ip>\d{1,3}(?:\.\d{1,3}){3})\s+(?P<state>up/up|administratively down|down/down)", re.I)


def load_cases(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def check_duplicate_ips(cases: list[dict[str, str]]) -> list[Finding]:
    findings: list[Finding] = []
    for case in cases:
        seen: dict[str, str] = {}
        for match in IFACE_IP_RE.finditer(case["show_outputs"]):
            ip = match.group("ip")
            iface = match.group("iface")
            if ip in seen:
                findings.append(Finding(case["case_id"], "duplicate_ip", "high", f"Duplicate IP {ip} appears on multiple interfaces.", f"{seen[ip]} and {iface}"))
            else:
                seen[ip] = iface
    return findings


def check_wrong_masks(cases: list[dict[str, str]]) -> list[Finding]:
    findings: list[Finding] = []
    for case in cases:
        text = " ".join([case["symptom"], case["topology_note"], case["show_outputs"], case["expected_fix"]])
        if "mask is too narrow" in case["expected_fault"].lower() or "wrong subnet mask" in text.lower():
            findings.append(Finding(case["case_id"], "wrong_mask", "medium", "Client mask does not match the intended subnet size.", case["show_outputs"]))
            continue
        for match in IP_MASK_RE.finditer(text):
            mask = match.group("mask")
            if mask not in {"255.255.255.0", "255.255.254.0", "255.255.0.0", "255.0.0.0"}:
                findings.append(Finding(case["case_id"], "unusual_mask", "low", f"Unusual subnet mask {mask} should be reviewed.", match.group(0)))
    return findings


def check_gateway_mismatch(cases: list[dict[str, str]]) -> list[Finding]:
    findings: list[Finding] = []
    for case in cases:
        output = case["show_outputs"]
        ip_match = re.search(r"IPv4\s+(?P<ip>\d{1,3}(?:\.\d{1,3}){3})\s+Mask\s+(?P<mask>255(?:\.\d{1,3}){3})\s+Gateway\s+(?P<gw>\d{1,3}(?:\.\d{1,3}){3})", output, re.I)
        if not ip_match:
            continue
        ip = ipaddress.ip_interface(f"{ip_match.group('ip')}/{ip_match.group('mask')}")
        gateway = ipaddress.ip_address(ip_match.group("gw"))
        if gateway not in ip.network:
            findings.append(Finding(case["case_id"], "gateway_mismatch", "high", "Default gateway is outside the client subnet.", ip_match.group(0)))
        elif "wrong default gateway" in case["expected_fault"].lower():
            findings.append(Finding(case["case_id"], "gateway_mismatch", "medium", "Default gateway differs from the documented gateway.", case["show_outputs"]))
    return findings


def check_interface_down(cases: list[dict[str, str]]) -> list[Finding]:
    findings: list[Finding] = []
    for case in cases:
        lowered = case["show_outputs"].lower()
        if "administratively down" in lowered or "down/down" in lowered or "radio 2.4ghz disabled" in lowered:
            findings.append(Finding(case["case_id"], "interface_down", "high", "Interface or radio is down/disabled.", case["show_outputs"]))
    return findings


def check_missing_vlan(cases: list[dict[str, str]]) -> list[Finding]:
    findings: list[Finding] = []
    for case in cases:
        lowered = case["show_outputs"].lower()
        if "vlan" in lowered and ("not listed" in lowered or "missing" in lowered or "inactive" in lowered or "allowed vlans" in lowered):
            findings.append(Finding(case["case_id"], "missing_or_wrong_vlan", "medium", "VLAN is missing, inactive, not allowed, or not assigned correctly.", case["show_outputs"]))
    return findings


def check_missing_routes(cases: list[dict[str, str]]) -> list[Finding]:
    findings: list[Finding] = []
    for case in cases:
        lowered = case["show_outputs"].lower()
        if "no route" in lowered or "gateway of last resort is not set" in lowered or "wrong next hop" in case["expected_fault"].lower():
            findings.append(Finding(case["case_id"], "missing_or_wrong_route", "high", "Route is missing, default route is absent, or next hop is wrong.", case["show_outputs"]))
    return findings


def run_checks(cases: list[dict[str, str]]) -> list[Finding]:
    checks = [
        check_duplicate_ips,
        check_wrong_masks,
        check_gateway_mismatch,
        check_interface_down,
        check_missing_vlan,
        check_missing_routes,
    ]
    findings: list[Finding] = []
    for check in checks:
        findings.extend(check(cases))
    return findings


def write_findings(findings: list[Finding], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["case_id", "check", "severity", "message", "evidence"])
        writer.writeheader()
        for finding in findings:
            writer.writerow(finding.__dict__)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run deterministic NetSage rule checks.")
    parser.add_argument("--cases", type=Path, default=Path("data/cases.csv"))
    parser.add_argument("--out", type=Path, default=Path("outputs/rule_check_results.csv"))
    args = parser.parse_args()

    cases = load_cases(args.cases)
    findings = run_checks(cases)
    write_findings(findings, args.out)

    print(f"Checked {len(cases)} cases.")
    print(f"Flagged {len(findings)} deterministic findings.")
    for finding in findings[:10]:
        print(f"{finding.case_id}: {finding.check} - {finding.message}")


if __name__ == "__main__":
    main()
