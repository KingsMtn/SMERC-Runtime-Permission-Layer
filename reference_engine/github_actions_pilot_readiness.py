from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping

from reference_engine.first_pilot_packet import load_json, validate_manifest


VERSION = "smerc.github-actions-pilot-readiness.v1"


REQUIRED_SETUP_ITEMS = [
    "one selected repository or workflow family",
    "security owner",
    "platform owner",
    "pilot reviewer group",
    "metadata-only action request file",
    "observe-mode workflow configuration",
    "artifact retention period",
    "weekly review cadence",
    "stop conditions",
    "day-30 go/no-go criteria",
]


def build_readiness(manifest_payload: Mapping[str, Any], *, repo_root: Path) -> Dict[str, Any]:
    manifest = validate_manifest(manifest_payload)
    evidence_checks = _evidence_checks(manifest["required_repository_evidence"], repo_root=repo_root)
    setup_checks = _setup_checks(manifest)
    blockers = [
        check["item"]
        for check in evidence_checks + setup_checks
        if check["status"] == "blocker"
    ]
    warnings = [
        check["item"]
        for check in evidence_checks + setup_checks
        if check["status"] == "warning"
    ]
    ready_for_week_zero = not blockers
    ready_for_customer_observe = ready_for_week_zero and not warnings
    return {
        "schema": VERSION,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "pilot_name": manifest["pilot_name"],
        "mode": manifest["pilot_boundary"]["mode"],
        "ready_for_week_zero": ready_for_week_zero,
        "ready_for_customer_observe": ready_for_customer_observe,
        "blockers": blockers,
        "warnings": warnings,
        "required_setup_items": REQUIRED_SETUP_ITEMS,
        "evidence_checks": evidence_checks,
        "setup_checks": setup_checks,
        "first_customer_question": (
            "Can we run SMERC in observe mode against one GitHub Actions workflow using metadata-only "
            "action descriptions and compare the output with reviewer judgment for 30 days?"
        ),
        "evidence_boundary": (
            "Readiness only. This does not prove production suitability, incident reduction, "
            "customer demand, or regulatory compliance."
        ),
    }


def _evidence_checks(paths: Iterable[str], *, repo_root: Path) -> List[Dict[str, str]]:
    checks: List[Dict[str, str]] = []
    for relative_path in paths:
        path = repo_root / relative_path
        checks.append(
            {
                "item": relative_path,
                "status": "ready" if path.exists() else "blocker",
                "detail": "repository evidence exists" if path.exists() else "required repository evidence is missing",
            }
        )
    return checks


def _setup_checks(manifest: Mapping[str, Any]) -> List[Dict[str, str]]:
    checks = [
        _check(
            "pilot starts in observe mode",
            manifest["pilot_boundary"]["mode"] == "observe",
            "first customer test must not block workflow execution",
        ),
        _check(
            "pilot explicitly excludes production certification claims",
            manifest["pilot_boundary"]["not_production_certified"] is True,
            "public and customer language must stay inside evidence boundaries",
        ),
        _check(
            "metadata-only approved data is defined",
            bool(manifest["pilot_boundary"]["approved_data"]),
            "pilot should score workflow metadata, not sensitive payloads",
        ),
        _check(
            "sensitive and regulated data exclusions are defined",
            bool(manifest["pilot_boundary"]["excluded_data"]),
            "first pilot must state what not to send",
        ),
        _check(
            "GitHub OIDC is the preferred authentication path",
            manifest["authentication_options"]["preferred"] == "github-oidc",
            "OIDC reduces static secret handling in a real workflow",
            warning=True,
        ),
        _check(
            "at least one target workflow is declared",
            bool(manifest["target_workflows"]),
            "a pilot must start with a concrete workflow",
        ),
        _check(
            "weekly metrics include reviewer agreement",
            "reviewer_agreement_rate" in manifest["weekly_metrics"],
            "commercial evidence requires human comparison labels",
        ),
        _check(
            "weekly metrics include unavailable evaluation count",
            "integration_unavailable_count" in manifest["weekly_metrics"],
            "operators need to know whether integration reliability is noisy",
        ),
        _check(
            "stop conditions are declared",
            bool(manifest["stop_conditions"]),
            "a bounded pilot needs explicit halt rules",
        ),
        _check(
            "go/no-go options are declared",
            {"stop", "narrow", "continue_observe", "move_to_recommend"}.issubset(set(manifest["go_no_go_options"])),
            "day-30 decision should not drift into unapproved enforcement",
        ),
    ]
    return checks


def _check(item: str, passed: bool, detail: str, *, warning: bool = False) -> Dict[str, str]:
    if passed:
        status = "ready"
    elif warning:
        status = "warning"
    else:
        status = "blocker"
    return {"item": item, "status": status, "detail": detail}


def markdown(report: Mapping[str, Any]) -> str:
    lines = [
        "# GitHub Actions Pilot Operator Readiness",
        "",
        f"Generated: `{report['generated_at']}`",
        "",
        "## Decision",
        "",
        f"- Ready for week-zero qualification: `{str(report['ready_for_week_zero']).lower()}`",
        f"- Ready for customer observe mode: `{str(report['ready_for_customer_observe']).lower()}`",
        f"- Pilot mode: `{report['mode']}`",
        "",
        "## First Customer Question",
        "",
        str(report["first_customer_question"]),
        "",
        "## Required Setup Items",
        "",
    ]
    lines.extend(f"- {item}" for item in report["required_setup_items"])
    lines.extend(["", "## Blockers", ""])
    if report["blockers"]:
        lines.extend(f"- {item}" for item in report["blockers"])
    else:
        lines.append("- None.")
    lines.extend(["", "## Warnings", ""])
    if report["warnings"]:
        lines.extend(f"- {item}" for item in report["warnings"])
    else:
        lines.append("- None.")
    lines.extend(["", "## Repository Evidence Checks", "", "| Item | Status | Detail |", "| --- | --- | --- |"])
    for check in report["evidence_checks"]:
        lines.append(f"| `{safe(check['item'])}` | `{check['status']}` | {safe(check['detail'])} |")
    lines.extend(["", "## Setup Checks", "", "| Item | Status | Detail |", "| --- | --- | --- |"])
    for check in report["setup_checks"]:
        lines.append(f"| {safe(check['item'])} | `{check['status']}` | {safe(check['detail'])} |")
    lines.extend(["", "## Evidence Boundary", "", str(report["evidence_boundary"])])
    return "\n".join(lines) + "\n"


def safe(value: Any) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ")


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a GitHub Actions pilot operator-readiness report.")
    parser.add_argument("--manifest", type=Path, default=Path("examples/github_actions_pilot_manifest.json"))
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    parser.add_argument("--json-output", type=Path, default=Path("reports/github_actions_pilot_readiness.json"))
    parser.add_argument("--markdown-output", type=Path, default=Path("reports/GitHub_Actions_Pilot_Readiness.md"))
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()

    report = build_readiness(load_json(args.manifest), repo_root=args.repo_root)
    args.json_output.parent.mkdir(parents=True, exist_ok=True)
    args.markdown_output.parent.mkdir(parents=True, exist_ok=True)
    args.json_output.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    args.markdown_output.write_text(markdown(report), encoding="utf-8")
    print(json.dumps(report, indent=2 if args.pretty else None, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
