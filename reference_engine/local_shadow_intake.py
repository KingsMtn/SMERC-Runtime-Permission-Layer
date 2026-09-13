from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Mapping


VERSION = "smerc.local-shadow-intake.v1"
OUTPUT_VERSION = "smerc.local-shadow-metadata-draft.v1"
SOURCE_NAME = "SMERC Local Shadow Intake"

REQUIRED_FIELDS = {
    "action_id",
    "action_type",
    "tool_system",
    "external_side_effects",
    "reversibility",
    "rollback_latency_seconds",
    "containment_strength",
    "evidence_available",
    "blast_radius_scope",
    "human_approval_existed",
    "schema_contract_match",
    "current_system_handling",
}

PROHIBITED_KEY_FRAGMENTS = {
    "secret",
    "token",
    "password",
    "credential",
    "private_key",
    "wallet_key",
    "api_key",
    "account_id",
    "arn",
    "email",
    "ip_address",
    "customer_name",
    "raw_log",
    "production_log",
    "source_code",
    "prompt",
}

IDENTIFIER_PATTERNS = {
    "AWS_ACCOUNT_ID": re.compile(r"\b\d{12}\b"),
    "AWS_ARN": re.compile(r"\barn:aws[a-zA-Z-]*:[^\s\"']+"),
    "EMAIL": re.compile(r"\b[^@\s]+@[^@\s]+\.[^@\s]+\b"),
    "IP_ADDRESS": re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b"),
}

ALLOWED_HANDLING = {"allow", "block", "review", "log only", "deny", "escalate"}


def load_payload(path: str | Path) -> Dict[str, Any]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise TypeError("local shadow intake input must be a JSON object")
    if payload.get("schema_version") != VERSION:
        raise ValueError(f"schema_version must be {VERSION}")
    actions = payload.get("actions")
    if not isinstance(actions, list) or not actions:
        raise ValueError("actions must be a non-empty list")
    return payload


def build_intake_report(payload: Mapping[str, Any]) -> Dict[str, Any]:
    decisions = [_screen_action(action, index) for index, action in enumerate(payload["actions"], start=1)]
    accepted = [decision["sanitized_record"] for decision in decisions if decision["classification"] == "ACCEPTED_METADATA_ONLY"]
    counts = Counter(decision["classification"] for decision in decisions)
    reason_counts = Counter(reason for decision in decisions for reason in decision["reason_codes"])
    draft = {
        "schema_version": OUTPUT_VERSION,
        "generated_at": _now(),
        "source_name": SOURCE_NAME,
        "data_boundary": (
            "Metadata-only draft produced by local reject-first intake. Human review is required before sharing."
        ),
        "actions": accepted,
    }
    return {
        "version": VERSION,
        "generated_at": _now(),
        "source_name": SOURCE_NAME,
        "input_action_count": len(payload["actions"]),
        "accepted_action_count": len(accepted),
        "classification_counts": dict(sorted(counts.items())),
        "reason_code_counts": dict(sorted(reason_counts.items())),
        "decisions": decisions,
        "sanitized_metadata_draft": draft,
        "share_status": "HUMAN_REVIEW_REQUIRED" if accepted else "NO_SHAREABLE_RECORDS",
        "recommended_next_action": _recommend(accepted, counts),
        "work_result_impact": {
            "work": "Screen local structured action summaries before they become SMERC reviewer-owned metadata.",
            "result": (
                f"Accepted {len(accepted)} of {len(payload['actions'])} action summaries and rejected or flagged the rest."
            ),
            "impact": (
                "Reviewers can prepare 5 to 25 metadata-only actions without sending raw logs, secrets, account "
                "identifiers, private prompts, customer records, ARNs, or production commands into the public repo."
            ),
        },
        "evidence_boundary": (
            "This utility is reject-first intake, not guaranteed anonymization. Hashing is not treated as proof of "
            "privacy. A human must inspect the output before sharing, and raw logs should not be submitted."
        ),
    }


def render_markdown(report: Mapping[str, Any]) -> str:
    lines = [
        "# SMERC Local Shadow Intake Report",
        "",
        f"Generated: `{report['generated_at']}`",
        f"Version: `{report['version']}`",
        "",
        "## Work / Result / Impact",
        "",
        f"- Work: {report['work_result_impact']['work']}",
        f"- Result: {report['work_result_impact']['result']}",
        f"- Impact: {report['work_result_impact']['impact']}",
        "",
        "## Summary",
        "",
        f"- Input actions: `{report['input_action_count']}`",
        f"- Accepted actions: `{report['accepted_action_count']}`",
        f"- Classification counts: `{report['classification_counts']}`",
        f"- Share status: `{report['share_status']}`",
        "",
        "## Evidence Boundary",
        "",
        str(report["evidence_boundary"]),
        "",
        "## Decisions",
        "",
        "| Source row | Classification | Reasons |",
        "| --- | --- | --- |",
    ]
    for decision in report["decisions"]:
        lines.append(
            f"| `{decision['source_index']}` | `{decision['classification']}` | `{decision['reason_codes']}` |"
        )
    lines.extend(["", "## Recommended Next Action", "", str(report["recommended_next_action"]), ""])
    return "\n".join(lines)


def write_outputs(
    report: Mapping[str, Any],
    *,
    sanitized_output: str | Path,
    json_output: str | Path,
    markdown_output: str | Path,
) -> None:
    for path in (sanitized_output, json_output, markdown_output):
        Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(sanitized_output).write_text(
        json.dumps(report["sanitized_metadata_draft"], indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    Path(json_output).write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    Path(markdown_output).write_text(render_markdown(report), encoding="utf-8")


def _screen_action(action: Any, index: int) -> Dict[str, Any]:
    if not isinstance(action, dict):
        return _decision(index, "REJECTED_RAW_LOG", ["ROW_NOT_OBJECT"])

    key_hits = _prohibited_key_hits(action)
    if key_hits:
        return _decision(index, "SKIPPED_PROHIBITED_FIELD", [f"PROHIBITED_KEY:{item}" for item in key_hits])

    text_hits = _identifier_hits(action)
    if text_hits:
        return _decision(index, "REJECTED_IDENTIFIER_RISK", sorted(text_hits))

    if _raw_log_shaped(action):
        return _decision(index, "REJECTED_RAW_LOG", ["RAW_LOG_SHAPED_RECORD"])

    missing = sorted(REQUIRED_FIELDS - set(action))
    if missing:
        return _decision(index, "NEEDS_MANUAL_REVIEW", [f"MISSING:{field}" for field in missing])

    handling = str(action.get("current_system_handling", "")).strip().lower()
    if handling not in ALLOWED_HANDLING:
        return _decision(index, "NEEDS_MANUAL_REVIEW", ["UNKNOWN_CURRENT_SYSTEM_HANDLING"])

    try:
        sanitized = _sanitize_action(action)
    except (TypeError, ValueError) as exc:
        return _decision(index, "NEEDS_MANUAL_REVIEW", [str(exc)])

    return _decision(index, "ACCEPTED_METADATA_ONLY", ["METADATA_ONLY_DRAFT"], sanitized)


def _sanitize_action(action: Mapping[str, Any]) -> Dict[str, Any]:
    rollback = _integer(action["rollback_latency_seconds"], "rollback_latency_seconds")
    return {
        "action_id": _safe_label(action["action_id"], "action_id", 80),
        "action_type": _safe_label(action["action_type"], "action_type", 120),
        "tool_system_class": _tool_class(_safe_label(action["tool_system"], "tool_system", 120)),
        "external_side_effects": _safe_bool_or_unknown(action["external_side_effects"], "external_side_effects"),
        "reversibility": _safe_label(action["reversibility"], "reversibility", 80),
        "rollback_latency_seconds": rollback,
        "containment_strength": _safe_label(action["containment_strength"], "containment_strength", 80),
        "evidence_available": _safe_label(action["evidence_available"], "evidence_available", 160),
        "blast_radius_scope": _safe_label(action["blast_radius_scope"], "blast_radius_scope", 200),
        "human_approval_existed": _boolean(action["human_approval_existed"], "human_approval_existed"),
        "schema_contract_match": _boolean(action["schema_contract_match"], "schema_contract_match"),
        "current_system_posture": str(action["current_system_handling"]).strip().lower(),
        "intake_posture_hint": _posture_hint(action),
    }


def _posture_hint(action: Mapping[str, Any]) -> str:
    reversibility = str(action["reversibility"]).lower()
    containment = str(action["containment_strength"]).lower()
    rollback = int(action["rollback_latency_seconds"])
    schema_match = bool(action["schema_contract_match"])
    if not schema_match:
        return "DENY"
    if "irreversible" in reversibility or rollback < 0 or containment in {"none", "low"}:
        return "FREEZE"
    if rollback > 300:
        return "ESCALATE"
    if rollback > 60 or action["external_side_effects"] is True:
        return "THROTTLE"
    return "ALLOW"


def _prohibited_key_hits(value: Any, prefix: str = "") -> list[str]:
    hits: list[str] = []
    if isinstance(value, dict):
        for key, child in value.items():
            normalized = str(key).lower()
            if any(fragment in normalized for fragment in PROHIBITED_KEY_FRAGMENTS):
                hits.append(f"{prefix}{key}")
            hits.extend(_prohibited_key_hits(child, f"{prefix}{key}."))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            hits.extend(_prohibited_key_hits(child, f"{prefix}{index}."))
    return sorted(set(hits))


def _identifier_hits(value: Any) -> list[str]:
    text = json.dumps(value, sort_keys=True)
    return sorted(name for name, pattern in IDENTIFIER_PATTERNS.items() if pattern.search(text))


def _raw_log_shaped(action: Mapping[str, Any]) -> bool:
    raw_keys = {"timestamp", "message", "level", "stacktrace", "request", "response", "headers", "body"}
    return len(raw_keys & {str(key).lower() for key in action}) >= 2


def _decision(
    index: int,
    classification: str,
    reason_codes: list[str],
    sanitized_record: Mapping[str, Any] | None = None,
) -> Dict[str, Any]:
    result = {
        "source_index": index,
        "classification": classification,
        "reason_codes": sorted(set(reason_codes)),
    }
    if sanitized_record is not None:
        result["sanitized_record"] = dict(sanitized_record)
    return result


def _recommend(accepted: list[Mapping[str, Any]], counts: Mapping[str, int]) -> str:
    if len(accepted) >= 5:
        return "Manually inspect the sanitized draft, then use accepted records for a shadow-mode posture gap matrix."
    if counts.get("SKIPPED_PROHIBITED_FIELD") or counts.get("REJECTED_IDENTIFIER_RISK") or counts.get("REJECTED_RAW_LOG"):
        return "Do not share this output yet; remove prohibited fields, identifiers, and raw-log-shaped records locally."
    return "Collect at least 5 metadata-only action summaries from one workflow before requesting review."


def _safe_label(value: Any, field: str, maximum: int) -> str:
    if not isinstance(value, str) or not value.strip():
        raise TypeError(f"{field} must be a non-empty string")
    text = value.strip()
    if len(text) > maximum:
        raise ValueError(f"{field} must be at most {maximum} characters")
    if _identifier_hits(text):
        raise ValueError(f"{field} contains identifier-shaped text")
    return text


def _tool_class(value: str) -> str:
    return re.split(r"[/.]", value, maxsplit=1)[0]


def _safe_bool_or_unknown(value: Any, field: str) -> bool | str:
    if isinstance(value, bool):
        return value
    if isinstance(value, str) and value.strip().lower() == "unknown":
        return "Unknown"
    raise TypeError(f"{field} must be boolean or Unknown")


def _boolean(value: Any, field: str) -> bool:
    if not isinstance(value, bool):
        raise TypeError(f"{field} must be boolean")
    return value


def _integer(value: Any, field: str) -> int:
    if not isinstance(value, int) or isinstance(value, bool):
        raise TypeError(f"{field} must be an integer")
    return value


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def main() -> int:
    parser = argparse.ArgumentParser(description="Reject-first local intake for SMERC shadow metadata.")
    parser.add_argument("path", nargs="?", default="examples/local_shadow_intake_examples.json")
    parser.add_argument("--sanitized-output", default="reports/smerc_anonymous_contribution.json")
    parser.add_argument("--json-output", default="reports/local_shadow_intake_report.json")
    parser.add_argument("--markdown-output", default="reports/Local_Shadow_Intake_Report.md")
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()
    report = build_intake_report(load_payload(args.path))
    write_outputs(
        report,
        sanitized_output=args.sanitized_output,
        json_output=args.json_output,
        markdown_output=args.markdown_output,
    )
    print(json.dumps(report, indent=2 if args.pretty else None, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
