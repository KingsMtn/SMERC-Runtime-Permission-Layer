from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict

from reference_engine.audit_store import AuditStore


def build_report(audit_db: str | Path, tenant_id: str) -> Dict[str, Any]:
    database_path = Path(audit_db)
    if str(audit_db) != ":memory:" and not database_path.is_file():
        raise FileNotFoundError(f"Audit database does not exist: {database_path}")
    store = AuditStore(audit_db)
    try:
        report = store.pilot_metrics(tenant_id)
    finally:
        store.close()
    report["generated_at"] = datetime.now(timezone.utc).isoformat()
    report["evidence_status"] = "pilot_observation"
    report["interpretation_warning"] = (
        "Rates describe reviewed pilot records only. They do not establish production accuracy, "
        "causality, or general performance. Read every rate with its denominator."
    )
    return report


def to_markdown(report: Dict[str, Any]) -> str:
    metrics = report["metrics"]
    denominators = report["denominators"]

    def display(value: Any) -> str:
        if value is None:
            return "Not measurable"
        if isinstance(value, float):
            return f"{value:.4f}"
        return str(value)

    lines = [
        "# SMERC Pilot Review Metrics",
        "",
        f"- Tenant: `{report['tenant_id']}`",
        f"- Generated: `{report['generated_at']}`",
        f"- Decisions: {report['decision_count']}",
        f"- Reviewed decisions: {report['reviewed_decision_count']}",
        f"- Reviews: {report['review_count']}",
        "",
        "## Metrics",
        "",
        "| Metric | Value | Denominator |",
        "|---|---:|---:|",
        f"| Decision review coverage | {display(metrics['decision_review_coverage'])} | {denominators['all_decisions']} decisions |",
        f"| Reviewer agreement rate | {display(metrics['reviewer_agreement_rate'])} | {denominators['determinate_reviews']} determinate reviews |",
        f"| Override rate | {display(metrics['override_rate'])} | {denominators['determinate_reviews']} determinate reviews |",
        f"| False release rate | {display(metrics['false_release_rate'])} | {denominators['allow_reviews']} ALLOW reviews |",
        f"| False constraint rate | {display(metrics['false_constraint_rate'])} | {denominators['constrained_reviews']} constrained reviews |",
        f"| Useful constraint rate | {display(metrics['useful_constraint_rate'])} | {denominators['constrained_reviews']} constrained reviews |",
        f"| Average review latency | {display(metrics['average_review_latency_ms'])} ms | {denominators['all_reviews']} reviews |",
        "",
        "## Interpretation Boundary",
        "",
        report["interpretation_warning"],
        "",
    ]
    return "\n".join(lines)


def write_bundle(report: Dict[str, Any], output_dir: str | Path) -> tuple[Path, Path]:
    target = Path(output_dir)
    target.mkdir(parents=True, exist_ok=True)
    json_path = target / "pilot-review-metrics.json"
    markdown_path = target / "pilot-review-metrics.md"
    json_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    markdown_path.write_text(to_markdown(report), encoding="utf-8")
    return json_path, markdown_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Export tenant-scoped SMERC pilot review metrics.")
    parser.add_argument("--audit-db", required=True)
    parser.add_argument("--tenant", required=True)
    parser.add_argument("--output-dir", default="pilot-metrics-output")
    args = parser.parse_args()
    report = build_report(args.audit_db, args.tenant)
    json_path, markdown_path = write_bundle(report, args.output_dir)
    print(f"Wrote {json_path}")
    print(f"Wrote {markdown_path}")


if __name__ == "__main__":
    main()
