from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Mapping

from reference_engine.ciso_review_seed import (
    load_actions,
    seed_ciso_review,
    write_report as write_ciso_seed_report,
)
from reference_engine.end_to_end_pr_guardian_demo import (
    build_end_to_end_demo,
    write_outputs as write_pr_guardian_outputs,
)
from reference_engine.runtime_benchmark_suite import (
    build_runtime_benchmark,
    write_outputs as write_benchmark_outputs,
)


REVIEWER_QUICKSTART_VERSION = "smerc.reviewer-quickstart.v1"


def _relative(path: Path) -> str:
    return path.as_posix()


def build_reviewer_quickstart(
    *,
    output_dir: str | Path = "reports/reviewer_quickstart",
    audit_db: str | Path = "./smerc_reviewer_quickstart.sqlite3",
    ciso_actions: str | Path = "examples/ciso_review_seed_actions.json",
    benchmark_seed: str | Path = "examples/proxy_incident_replay_scenarios.json",
) -> Dict[str, Any]:
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)

    pr_json = output / "end_to_end_pr_guardian_demo.json"
    pr_markdown = output / "End_To_End_PR_Guardian_Demo.md"
    pr_comment = output / "end_to_end_pr_guardian_comment.md"
    pr_certificate = output / "end_to_end_pr_guardian_certificate.json"
    pr_route = output / "end_to_end_pr_guardian_sparta_route.json"
    pr_ledger = output / "end_to_end_pr_guardian_dll.json"
    pr_intelligence = output / "end_to_end_pr_guardian_dll_intelligence.json"

    pr_bundle = build_end_to_end_demo()
    write_pr_guardian_outputs(
        pr_bundle,
        json_output=pr_json,
        markdown_output=pr_markdown,
        pr_comment_output=pr_comment,
        certificate_output=pr_certificate,
        route_output=pr_route,
        ledger_output=pr_ledger,
        intelligence_output=pr_intelligence,
    )

    ciso_json = output / "ciso_evidence_walkthrough_seed.json"
    ciso_markdown = output / "CISO_Evidence_Walkthrough_Seed_Report.md"
    ciso_report = seed_ciso_review(load_actions(ciso_actions), audit_db=audit_db)
    write_ciso_seed_report(ciso_report, ciso_json, ciso_markdown)

    benchmark_json = output / "runtime_governance_benchmark.json"
    benchmark_markdown = output / "Runtime_Governance_Benchmark.md"
    benchmark_payload = build_runtime_benchmark(benchmark_seed)
    write_benchmark_outputs(benchmark_payload, benchmark_json, benchmark_markdown)

    pr_decision = pr_bundle["decision_report"]["decision"]
    pr_route_report = pr_bundle["sparta_route"]["route_report"]
    benchmark_summary = benchmark_payload["summary"]

    return {
        "version": REVIEWER_QUICKSTART_VERSION,
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "review_question": "Is SMERC credible enough to test in a bounded shadow-mode pilot?",
        "not_a_claim": [
            "not production certification",
            "not compliance attestation",
            "not customer validation",
            "not proof of incident reduction",
        ],
        "one_command": "python -m reference_engine.reviewer_quickstart --pretty",
        "artifacts": {
            "summary_markdown": _relative(output / "Reviewer_Quickstart_Report.md"),
            "summary_json": _relative(output / "reviewer_quickstart.json"),
            "pr_guardian_demo": _relative(pr_markdown),
            "pr_guardian_json": _relative(pr_json),
            "pr_guardian_comment": _relative(pr_comment),
            "pr_guardian_certificate": _relative(pr_certificate),
            "sparta_route": _relative(pr_route),
            "decision_lifecycle_ledger": _relative(pr_ledger),
            "dll_intelligence": _relative(pr_intelligence),
            "ciso_seed_report": _relative(ciso_markdown),
            "ciso_seed_json": _relative(ciso_json),
            "runtime_benchmark": _relative(benchmark_markdown),
            "runtime_benchmark_json": _relative(benchmark_json),
            "audit_database": str(audit_db),
        },
        "proof_highlights": {
            "pr_guardian_posture": pr_decision["posture"],
            "pr_guardian_replay_id": pr_decision["replay_id"],
            "sparta_route_state": pr_route_report["route_state"],
            "sparta_executable": pr_route_report["executable"],
            "dll_record_count": pr_bundle["decision_lifecycle_ledger"]["record_count"],
            "dll_verification_valid": pr_bundle["decision_lifecycle_ledger"]["verification"]["valid"],
            "benchmark_total_scenarios": benchmark_summary["total_scenarios"],
            "benchmark_decision_difference_rate": benchmark_summary["decision_difference_rate"],
            "benchmark_evidence_limit": benchmark_summary["evidence_limit"],
            "seeded_ciso_decisions": ciso_report["seeded_decision_count"],
            "stored_ciso_ledgers": ciso_report["stored_ledger_count"],
        },
        "reviewer_path": [
            "Read the summary report.",
            "Open the PR Guardian demo and confirm the action, posture, route, DLL, and DLL Intelligence are linked.",
            "Open the CISO seed report and confirm the review queue has replayable seeded decisions.",
            "Open the runtime benchmark and inspect where SMERC differs from simple allow/deny.",
            "Decide whether one real GitHub Actions workflow is worth testing in observe mode.",
        ],
        "pilot_gate": [
            "Proceed only if a reviewer can name one side-effecting workflow.",
            "Proceed only if reviewer labels can be collected.",
            "Proceed only if the organization accepts observe mode before enforcement.",
            "Do not proceed if current controls already cover recoverability scoring and replay well enough.",
        ],
    }


def render_markdown(report: Mapping[str, Any]) -> str:
    highlights = report["proof_highlights"]
    artifacts = report["artifacts"]
    lines = [
        "# SMERC Reviewer Quickstart Report",
        "",
        f"Version: `{report['version']}`",
        f"Generated at: `{report['generated_at']}`",
        "",
        "## Review Question",
        "",
        str(report["review_question"]),
        "",
        "## Evidence Boundary",
        "",
    ]
    lines.extend(f"- {item}" for item in report["not_a_claim"])
    lines.extend(
        [
            "",
            "## One Command",
            "",
            "```bash",
            str(report["one_command"]),
            "```",
            "",
            "## Proof Highlights",
            "",
            f"- PR Guardian posture: `{highlights['pr_guardian_posture']}`",
            f"- PR Guardian replay ID: `{highlights['pr_guardian_replay_id']}`",
            f"- SPARTa route state: `{highlights['sparta_route_state']}`",
            f"- SPARTa executable: `{highlights['sparta_executable']}`",
            f"- DLL record count: `{highlights['dll_record_count']}`",
            f"- DLL verification valid: `{highlights['dll_verification_valid']}`",
            f"- CISO seeded decisions: `{highlights['seeded_ciso_decisions']}`",
            f"- CISO stored ledgers: `{highlights['stored_ciso_ledgers']}`",
            f"- Benchmark scenarios: `{highlights['benchmark_total_scenarios']}`",
            f"- Benchmark decision difference rate: `{highlights['benchmark_decision_difference_rate']}`",
            "",
            "## Generated Artifacts",
            "",
        ]
    )
    for label, path in artifacts.items():
        lines.append(f"- {label}: `{path}`")
    lines.extend(["", "## Reviewer Path", ""])
    lines.extend(f"{index}. {step}" for index, step in enumerate(report["reviewer_path"], start=1))
    lines.extend(["", "## Pilot Gate", ""])
    lines.extend(f"- {step}" for step in report["pilot_gate"])
    lines.extend(
        [
            "",
            "## What This Proves",
            "",
            "This proves that SMERC can generate a coherent local review package connecting a proposed AI-agent action, runtime posture, visible PR review artifact, SPARTa route, Decision Lifecycle Ledger, DLL Intelligence, seeded CISO review evidence, and benchmark comparison.",
            "",
            "## What This Does Not Prove",
            "",
            "This does not prove customer demand, production safety, compliance readiness, or incident reduction. Those require external review, shadow-mode pilot evidence, and customer-specific calibration.",
            "",
        ]
    )
    return "\n".join(lines)


def write_report(report: Mapping[str, Any], *, output_dir: str | Path = "reports/reviewer_quickstart") -> None:
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    (output / "reviewer_quickstart.json").write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (output / "Reviewer_Quickstart_Report.md").write_text(render_markdown(report), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate the SMERC one-command reviewer quickstart package.")
    parser.add_argument("--output-dir", default="reports/reviewer_quickstart")
    parser.add_argument("--audit-db", default="./smerc_reviewer_quickstart.sqlite3")
    parser.add_argument("--ciso-actions", default="examples/ciso_review_seed_actions.json")
    parser.add_argument("--benchmark-seed", default="examples/proxy_incident_replay_scenarios.json")
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()

    report = build_reviewer_quickstart(
        output_dir=args.output_dir,
        audit_db=args.audit_db,
        ciso_actions=args.ciso_actions,
        benchmark_seed=args.benchmark_seed,
    )
    write_report(report, output_dir=args.output_dir)
    print(json.dumps(report, indent=2 if args.pretty else None, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
