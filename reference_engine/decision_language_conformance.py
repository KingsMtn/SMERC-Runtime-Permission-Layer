from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any, Dict, Iterable, List


VERSION = "smerc.decision-language-conformance.v1"
DECISION_VERSION = "smerc.decision.v1"
ACTION_VERSION = "smerc.action.v1"
POSTURE_TO_ENFORCEMENT = {
    "ALLOW": "release",
    "THROTTLE": "constrain",
    "FREEZE": "pause",
    "DENY": "block",
    "ESCALATE": "review",
}
POSTURE_TO_ROUTE = {
    "ALLOW": "EXECUTE",
    "THROTTLE": "CONSTRAINED_EXECUTE",
    "FREEZE": "PAUSE",
    "DENY": "BLOCK",
    "ESCALATE": "REVIEW_REQUIRED",
}
REQUIRED_FIELDS = {
    "language_version",
    "action_language_version",
    "action_hash",
    "action_id",
    "posture",
    "enforcement_state",
    "route_state",
    "required_controls",
    "recoverability",
    "scores",
    "reasons",
    "structured_controls",
    "evidence_expectation",
    "postcondition_expectation",
    "transition",
    "replay_id",
    "replay",
}
RECOVERABILITY_FIELDS = {"rollback_ready", "blast_radius_bounded", "evidence_sufficient", "containment_strength"}
EVIDENCE_EXPECTATION_FIELDS = {"pre_execution", "postcondition", "review"}
POSTCONDITION_EXPECTATION_FIELDS = {
    "must_preserve_replay",
    "must_record_execution",
    "must_report_missing_controls",
}
TRANSITION_FIELDS = {"mode", "eligible_target_posture", "requires_new_request", "conditions"}


def load_decision(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def check_decision(payload: Dict[str, Any], source: str = "<memory>") -> Dict[str, Any]:
    findings: List[Dict[str, str]] = []
    if not isinstance(payload, dict):
        return _result(source, None, ["payload must be an object"], findings)

    missing = sorted(REQUIRED_FIELDS - set(payload))
    extra_required_message = [f"missing required field: {field}" for field in missing]
    errors = list(extra_required_message)

    posture = payload.get("posture")
    if posture not in POSTURE_TO_ROUTE:
        errors.append("posture must be one of ALLOW, THROTTLE, FREEZE, DENY, ESCALATE")
    else:
        _expect(payload.get("enforcement_state") == POSTURE_TO_ENFORCEMENT[posture], errors, "enforcement_state does not match posture")
        _expect(payload.get("route_state") == POSTURE_TO_ROUTE[posture], errors, "route_state does not match posture")

    _expect(payload.get("language_version") == DECISION_VERSION, errors, f"language_version must be {DECISION_VERSION}")
    _expect(payload.get("action_language_version") == ACTION_VERSION, errors, f"action_language_version must be {ACTION_VERSION}")
    _expect(_is_hash(payload.get("action_hash")), errors, "action_hash must be a 64-character lowercase hex string")
    _expect(_non_empty_text(payload.get("action_id")), errors, "action_id must be a non-empty string")
    _expect(_non_empty_text(payload.get("replay_id")), errors, "replay_id must be a non-empty string")
    _expect(isinstance(payload.get("replay"), dict), errors, "replay must be an object")
    _expect(_non_empty_string_list(payload.get("required_controls")), errors, "required_controls must be a non-empty string array")
    _expect(_terms(payload.get("reasons")), errors, "reasons must be an array of {code,title} terms")
    _expect(_terms(payload.get("structured_controls")), errors, "structured_controls must be an array of {code,title} terms")
    _expect(_scores(payload.get("scores")), errors, "scores must be numeric values between 0.0 and 1.0")

    _check_object_fields(payload.get("recoverability"), RECOVERABILITY_FIELDS, "recoverability", errors)
    if isinstance(payload.get("recoverability"), dict):
        _expect(isinstance(payload["recoverability"].get("rollback_ready"), bool), errors, "recoverability.rollback_ready must be boolean")
        _expect(isinstance(payload["recoverability"].get("blast_radius_bounded"), bool), errors, "recoverability.blast_radius_bounded must be boolean")
        _expect(isinstance(payload["recoverability"].get("evidence_sufficient"), bool), errors, "recoverability.evidence_sufficient must be boolean")
        _expect(_unit_number(payload["recoverability"].get("containment_strength")), errors, "recoverability.containment_strength must be 0.0 through 1.0")

    _check_object_fields(payload.get("evidence_expectation"), EVIDENCE_EXPECTATION_FIELDS, "evidence_expectation", errors)
    if isinstance(payload.get("evidence_expectation"), dict):
        for field in EVIDENCE_EXPECTATION_FIELDS:
            _expect(_string_list(payload["evidence_expectation"].get(field)), errors, f"evidence_expectation.{field} must be a string array")

    _check_object_fields(payload.get("postcondition_expectation"), POSTCONDITION_EXPECTATION_FIELDS, "postcondition_expectation", errors)
    if isinstance(payload.get("postcondition_expectation"), dict):
        for field in POSTCONDITION_EXPECTATION_FIELDS:
            _expect(isinstance(payload["postcondition_expectation"].get(field), bool), errors, f"postcondition_expectation.{field} must be boolean")
        if payload["postcondition_expectation"].get("must_preserve_replay") is not True:
            findings.append({"severity": "warning", "message": "SMERC-compatible decisions should preserve replay evidence."})

    _check_object_fields(payload.get("transition"), TRANSITION_FIELDS, "transition", errors)
    if isinstance(payload.get("transition"), dict):
        _expect(payload["transition"].get("mode") in {"maintain", "conditional"}, errors, "transition.mode must be maintain or conditional")
        _expect(isinstance(payload["transition"].get("requires_new_request"), bool), errors, "transition.requires_new_request must be boolean")
        _expect(isinstance(payload["transition"].get("conditions"), list), errors, "transition.conditions must be an array")
        target = payload["transition"].get("eligible_target_posture")
        _expect(target in {"ALLOW", "THROTTLE", None}, errors, "transition.eligible_target_posture must be ALLOW, THROTTLE, or null")
        if posture == "DENY":
            _expect(payload["transition"].get("requires_new_request") is True, errors, "DENY must require a new request")
            _expect(target is None, errors, "DENY must not have an automatic target posture")

    return _result(source, posture if isinstance(posture, str) else None, errors, findings)


def build_conformance_report(paths: Iterable[Path]) -> Dict[str, Any]:
    records = [check_decision(load_decision(path), source=str(path)) for path in paths]
    status_counts = Counter(record["status"] for record in records)
    posture_counts = Counter(record.get("posture") or "UNKNOWN" for record in records)
    return {
        "version": VERSION,
        "status": "pass" if status_counts.get("fail", 0) == 0 else "fail",
        "decision_count": len(records),
        "status_counts": dict(sorted(status_counts.items())),
        "posture_counts": dict(sorted(posture_counts.items())),
        "records": records,
        "evidence_boundary": (
            "This conformance check validates the portable SMERC decision-language shape. "
            "It does not prove the underlying risk scores, production enforcement, customer calibration, "
            "or that route controls actually happened."
        ),
        "work_result_impact": {
            "work": "Check emitted decision JSON against the SMERC decision-language contract.",
            "result": f"Checked {len(records)} decision artifact(s) with {status_counts.get('fail', 0)} failure(s).",
            "impact": (
                "Frameworks can adopt the SMERC posture vocabulary and evidence fields without adopting "
                "the full reference engine, while reviewers can still detect malformed or incomplete decisions."
            ),
        },
    }


def render_markdown(report: Dict[str, Any]) -> str:
    lines = [
        "# SMERC Decision Language Conformance Report",
        "",
        f"Version: `{report['version']}`",
        f"Status: `{report['status']}`",
        f"Decision count: `{report['decision_count']}`",
        "",
        "## Work / Result / Impact",
        "",
        f"- Work: {report['work_result_impact']['work']}",
        f"- Result: {report['work_result_impact']['result']}",
        f"- Impact: {report['work_result_impact']['impact']}",
        "",
        "## Summary",
        "",
        f"- Status counts: `{report['status_counts']}`",
        f"- Posture counts: `{report['posture_counts']}`",
        "",
        "## Decisions",
        "",
        "| Source | Posture | Status | Errors | Warnings |",
        "| --- | --- | --- | --- | --- |",
    ]
    for record in report["records"]:
        warnings = [item["message"] for item in record["findings"] if item["severity"] == "warning"]
        lines.append(
            f"| `{record['source']}` | `{record.get('posture')}` | `{record['status']}` | "
            f"`{record['errors']}` | `{warnings}` |"
        )
    lines.extend(["", "## Evidence Boundary", "", report["evidence_boundary"], ""])
    return "\n".join(lines)


def write_outputs(report: Dict[str, Any], json_output: Path | None = None, markdown_output: Path | None = None) -> None:
    if json_output:
        json_output.parent.mkdir(parents=True, exist_ok=True)
        json_output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if markdown_output:
        markdown_output.parent.mkdir(parents=True, exist_ok=True)
        markdown_output.write_text(render_markdown(report), encoding="utf-8")


def _result(source: str, posture: str | None, errors: List[str], findings: List[Dict[str, str]]) -> Dict[str, Any]:
    return {
        "source": source,
        "posture": posture,
        "status": "fail" if errors else "pass",
        "errors": errors,
        "findings": findings,
    }


def _expect(condition: bool, errors: List[str], message: str) -> None:
    if not condition:
        errors.append(message)


def _is_hash(value: Any) -> bool:
    return isinstance(value, str) and len(value) == 64 and all(char in "0123456789abcdef" for char in value)


def _non_empty_text(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _string_list(value: Any) -> bool:
    return isinstance(value, list) and all(_non_empty_text(item) for item in value)


def _non_empty_string_list(value: Any) -> bool:
    return _string_list(value) and bool(value)


def _terms(value: Any) -> bool:
    if not isinstance(value, list) or not value:
        return False
    for item in value:
        if not isinstance(item, dict):
            return False
        if set(item) - {"code", "title"}:
            return False
        if not _non_empty_text(item.get("code")) or not _non_empty_text(item.get("title")):
            return False
    return True


def _scores(value: Any) -> bool:
    return isinstance(value, dict) and bool(value) and all(_unit_number(item) for item in value.values())


def _unit_number(value: Any) -> bool:
    return not isinstance(value, bool) and isinstance(value, (int, float)) and 0 <= value <= 1


def _check_object_fields(value: Any, required: set[str], path: str, errors: List[str]) -> None:
    if not isinstance(value, dict):
        errors.append(f"{path} must be an object")
        return
    for field in sorted(required - set(value)):
        errors.append(f"{path} missing required field: {field}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Check SMERC Decision Language conformance.")
    parser.add_argument("decisions", nargs="+", type=Path)
    parser.add_argument("--json-output", type=Path)
    parser.add_argument("--markdown-output", type=Path)
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()

    report = build_conformance_report(args.decisions)
    write_outputs(report, args.json_output, args.markdown_output)
    print(json.dumps(report, indent=2 if args.pretty else None, sort_keys=True))


if __name__ == "__main__":
    main()

