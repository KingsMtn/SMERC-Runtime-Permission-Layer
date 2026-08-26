from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Mapping


CONTENT_EVIDENCE_INPUT_VERSION = "smerc.content-evidence-input.v1"
CONTENT_EVIDENCE_VERSION = "smerc.content-evidence.v1"
CONTENT_EVIDENCE_REPORT_VERSION = "smerc.content-evidence-report.v1"

TRUSTED_SCANNER_TYPES = {
    "sast",
    "sql_analyzer",
    "dlp",
    "email_security",
    "prompt_injection_detector",
    "malware_scanner",
    "secrets_scanner",
    "policy_engine",
    "ai_eval_platform",
    "human_review",
}
HIGH_RISK_FINDINGS = {
    "destructive_database_operation",
    "secret_exposure",
    "credential_exposure",
    "regulated_data_exposure",
    "external_legal_commitment",
    "privilege_escalation",
    "prompt_injection",
    "malware_or_suspicious_payload",
    "funds_or_asset_transfer",
    "customer_data_deletion",
}


def evaluate_content_evidence(payload: Mapping[str, Any]) -> Dict[str, Any]:
    data = _object(payload, "content_evidence")
    if data.get("schema") != CONTENT_EVIDENCE_INPUT_VERSION:
        raise ValueError(f"schema must be {CONTENT_EVIDENCE_INPUT_VERSION}")
    action_id = _text(data.get("action_id"), "action_id", 128)
    content_target = _text(data.get("content_target"), "content_target", 128)
    content_available = _bool(data.get("content_available"), "content_available")
    assessments = _assessments(data.get("assessments"))

    unavailable = [item for item in assessments if item["status"] != "available"]
    available = [item for item in assessments if item["status"] == "available"]
    high_findings = sorted({item["finding_type"] for item in available if item["finding_type"] in HIGH_RISK_FINDINGS})

    if available:
        weighted_risk = sum(item["severity"] * item["confidence"] for item in available) / sum(
            max(item["confidence"], 0.001) for item in available
        )
        reliability = sum(_assessment_reliability(item) for item in assessments) / len(assessments)
    else:
        weighted_risk = 0.0
        reliability = 0.0

    if not content_available:
        weighted_risk = max(weighted_risk, 0.62)

    content_risk_score = _clamp(weighted_risk)
    evidence_reliability_score = _clamp(reliability)
    content_trust_level = _trust_level(evidence_reliability_score, unavailable, content_available)
    max_posture = _max_posture(content_risk_score, content_trust_level, high_findings, unavailable)
    reason_codes = _reason_codes(
        content_risk_score=content_risk_score,
        evidence_reliability_score=evidence_reliability_score,
        high_findings=high_findings,
        unavailable=unavailable,
        content_available=content_available,
        assessments=assessments,
    )
    controls = _controls(max_posture, high_findings, unavailable, content_available)
    return {
        "version": CONTENT_EVIDENCE_VERSION,
        "generated_at": _now(),
        "action_id": action_id,
        "content_target": content_target,
        "content_available": content_available,
        "content_risk_score": round(content_risk_score, 3),
        "evidence_reliability_score": round(evidence_reliability_score, 3),
        "content_trust_level": content_trust_level,
        "max_recommended_posture": max_posture,
        "high_risk_findings": high_findings,
        "unavailable_assessments": [
            {"source": item["source"], "scanner_type": item["scanner_type"], "status": item["status"]}
            for item in unavailable
        ],
        "reason_codes": reason_codes,
        "required_controls": controls,
        "plain_english_summary": _summary(action_id, content_risk_score, content_trust_level, max_posture),
        "evidence_boundary": (
            "SMERC does not classify raw content in this module. It normalizes trusted content-risk signals from "
            "scanners, eval platforms, policy engines, or reviewers so those signals can influence runtime posture."
        ),
    }


def build_content_evidence_report(payload: Mapping[str, Any]) -> Dict[str, Any]:
    scenarios = payload.get("scenarios")
    if not isinstance(scenarios, list) or not scenarios:
        raise ValueError("payload.scenarios must be a non-empty list")
    results = [evaluate_content_evidence(item) for item in scenarios]
    posture_counts: Dict[str, int] = {}
    for result in results:
        posture_counts[result["max_recommended_posture"]] = posture_counts.get(result["max_recommended_posture"], 0) + 1
    report = {
        "version": CONTENT_EVIDENCE_REPORT_VERSION,
        "generated_at": _now(),
        "scenario_count": len(results),
        "average_content_risk_score": round(sum(item["content_risk_score"] for item in results) / len(results), 3),
        "average_evidence_reliability_score": round(
            sum(item["evidence_reliability_score"] for item in results) / len(results), 3
        ),
        "max_posture_counts": dict(sorted(posture_counts.items())),
        "results": results,
        "evidence_boundary": (
            "Synthetic examples demonstrate content-evidence ingestion. Replace these with customer-approved scanner "
            "or reviewer signals during a pilot; do not send raw source code, customer data, secrets, or private prompts."
        ),
    }
    report["markdown_report"] = render_markdown(report)
    return report


def render_markdown(report: Mapping[str, Any]) -> str:
    lines = [
        "# SMERC Content Evidence Adapter Report",
        "",
        f"- Generated: `{report['generated_at']}`",
        f"- Scenarios evaluated: `{report['scenario_count']}`",
        f"- Average content risk score: `{report['average_content_risk_score']}`",
        f"- Average evidence reliability score: `{report['average_evidence_reliability_score']}`",
        f"- Max posture counts: `{report['max_posture_counts']}`",
        "",
        "| Action | Target | Risk | Reliability | Trust | Max Posture | Findings |",
        "| --- | --- | ---: | ---: | --- | --- | --- |",
    ]
    for result in report["results"]:
        lines.append(
            "| "
            + " | ".join(
                [
                    _escape(result["action_id"]),
                    _escape(result["content_target"]),
                    str(result["content_risk_score"]),
                    str(result["evidence_reliability_score"]),
                    _escape(result["content_trust_level"]),
                    _escape(result["max_recommended_posture"]),
                    _escape(", ".join(result["high_risk_findings"]) or "None"),
                ]
            )
            + " |"
        )
    lines.extend(["", "## Evidence Boundary", "", str(report["evidence_boundary"]), ""])
    return "\n".join(lines)


def write_outputs(report: Mapping[str, Any], *, json_path: str | Path, markdown_path: str | Path) -> None:
    Path(json_path).parent.mkdir(parents=True, exist_ok=True)
    Path(markdown_path).parent.mkdir(parents=True, exist_ok=True)
    Path(json_path).write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    Path(markdown_path).write_text(str(report["markdown_report"]) + "\n", encoding="utf-8")


def _assessments(value: Any) -> list[Dict[str, Any]]:
    if not isinstance(value, list) or not value:
        raise TypeError("assessments must be a non-empty list")
    parsed = []
    names = set()
    for index, item in enumerate(value):
        data = _object(item, f"assessments[{index}]")
        source = _text(data.get("source"), f"assessments[{index}].source", 128)
        if source in names:
            raise ValueError("assessment sources must be unique")
        names.add(source)
        status = _text(data.get("status"), f"assessments[{index}].status", 32)
        if status not in {"available", "unavailable", "error", "timeout", "stale"}:
            raise ValueError(f"assessments[{index}].status is unsupported")
        parsed.append(
            {
                "source": source,
                "scanner_type": _scanner_type(data.get("scanner_type"), f"assessments[{index}].scanner_type"),
                "status": status,
                "finding_type": _text(data.get("finding_type"), f"assessments[{index}].finding_type", 128),
                "severity": _score(data.get("severity"), f"assessments[{index}].severity"),
                "confidence": _score(data.get("confidence"), f"assessments[{index}].confidence"),
                "authenticated": _bool(data.get("authenticated"), f"assessments[{index}].authenticated"),
                "signed": _bool(data.get("signed"), f"assessments[{index}].signed"),
                "agent_supplied": _bool(data.get("agent_supplied"), f"assessments[{index}].agent_supplied"),
                "freshness_seconds": _non_negative_number(
                    data.get("freshness_seconds"), f"assessments[{index}].freshness_seconds"
                ),
            }
        )
    return parsed


def _assessment_reliability(item: Mapping[str, Any]) -> float:
    if item["status"] != "available":
        return 0.05
    score = 0.0
    score += 0.28 if item["scanner_type"] in TRUSTED_SCANNER_TYPES else 0.08
    score += 0.24 if item["authenticated"] else 0.0
    score += 0.18 if item["signed"] else 0.0
    score += 0.18 if not item["agent_supplied"] else -0.18
    score += 0.12 if item["freshness_seconds"] <= 600 else 0.05 if item["freshness_seconds"] <= 3600 else 0.0
    return _clamp(score)


def _trust_level(reliability: float, unavailable: list[Mapping[str, Any]], content_available: bool) -> str:
    if not content_available:
        return "MISSING_CONTENT"
    if len(unavailable) >= 2:
        return "DEGRADED"
    if reliability >= 0.82:
        return "HIGH"
    if reliability >= 0.62:
        return "MEDIUM"
    if reliability >= 0.42:
        return "LOW"
    return "DEGRADED"


def _max_posture(
    risk: float,
    trust_level: str,
    high_findings: list[str],
    unavailable: list[Mapping[str, Any]],
) -> str:
    if trust_level in {"MISSING_CONTENT", "DEGRADED"} and (risk >= 0.55 or unavailable):
        return "FREEZE"
    if risk >= 0.86 or {"secret_exposure", "credential_exposure", "malware_or_suspicious_payload"} & set(high_findings):
        return "DENY"
    if risk >= 0.70 or high_findings:
        return "ESCALATE"
    if risk >= 0.42 or trust_level in {"MEDIUM", "LOW"}:
        return "THROTTLE"
    return "ALLOW"


def _reason_codes(
    *,
    content_risk_score: float,
    evidence_reliability_score: float,
    high_findings: list[str],
    unavailable: list[Mapping[str, Any]],
    content_available: bool,
    assessments: list[Mapping[str, Any]],
) -> list[str]:
    codes = []
    if not content_available:
        codes.append("CONTENT_NOT_AVAILABLE")
    if unavailable:
        codes.append("CONTENT_SCANNER_UNAVAILABLE")
    if content_risk_score >= 0.70:
        codes.append("CONTENT_RISK_HIGH")
    elif content_risk_score >= 0.42:
        codes.append("CONTENT_RISK_ELEVATED")
    if evidence_reliability_score < 0.62:
        codes.append("CONTENT_EVIDENCE_RELIABILITY_LOW")
    if high_findings:
        codes.extend(f"CONTENT_FINDING_{finding.upper()}" for finding in high_findings)
    if any(item["agent_supplied"] for item in assessments):
        codes.append("AGENT_SUPPLIED_CONTENT_EVIDENCE")
    if any(item["freshness_seconds"] > 3600 for item in assessments):
        codes.append("STALE_CONTENT_EVIDENCE")
    return sorted(set(codes)) or ["CONTENT_EVIDENCE_ACCEPTABLE"]


def _controls(
    max_posture: str,
    high_findings: list[str],
    unavailable: list[Mapping[str, Any]],
    content_available: bool,
) -> list[str]:
    controls = []
    if not content_available:
        controls.append("collect_content_or_trusted_summary_before_release")
    if unavailable:
        controls.append("retry_or_replace_unavailable_scanners")
    if high_findings:
        controls.append("route_high_risk_content_to_accountable_reviewer")
    if max_posture in {"FREEZE", "DENY", "ESCALATE"}:
        controls.append("preserve_content_evidence_trace")
    if max_posture == "DENY":
        controls.append("block_execution_until_content_risk_is_resolved")
    if max_posture == "THROTTLE":
        controls.append("limit_scope_and_require_preview")
    return controls or ["no_additional_content_control_required"]


def _summary(action_id: str, risk: float, trust_level: str, posture: str) -> str:
    return (
        f"Content evidence for action '{action_id}' produced risk {risk:.3f} with trust level {trust_level}. "
        f"The content evidence adapter caps unrestricted release at {posture}."
    )


def _object(value: Any, path: str) -> Dict[str, Any]:
    if not isinstance(value, dict):
        raise TypeError(f"{path} must be an object")
    return dict(value)


def _text(value: Any, path: str, maximum: int) -> str:
    if not isinstance(value, str) or not value.strip():
        raise TypeError(f"{path} must be a non-empty string")
    value = value.strip()
    if len(value) > maximum:
        raise ValueError(f"{path} must be at most {maximum} characters")
    return value


def _scanner_type(value: Any, path: str) -> str:
    scanner_type = _text(value, path, 128)
    if not scanner_type.replace("_", "").replace("-", "").isalnum():
        raise ValueError(f"{path} must be a safe scanner identifier")
    return scanner_type


def _bool(value: Any, path: str) -> bool:
    if not isinstance(value, bool):
        raise TypeError(f"{path} must be a boolean")
    return value


def _score(value: Any, path: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeError(f"{path} must be a number between 0.0 and 1.0")
    if not 0 <= value <= 1:
        raise ValueError(f"{path} must be between 0.0 and 1.0")
    return float(value)


def _non_negative_number(value: Any, path: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeError(f"{path} must be a non-negative number")
    if value < 0:
        raise ValueError(f"{path} must be non-negative")
    return float(value)


def _clamp(value: float) -> float:
    return max(0.0, min(1.0, value))


def _escape(value: str) -> str:
    return str(value).replace("|", "\\|")


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def main() -> int:
    parser = argparse.ArgumentParser(description="Normalize trusted content-risk evidence for SMERC runtime decisions.")
    parser.add_argument("--input", default="examples/content_evidence_examples.json")
    parser.add_argument("--json-output", default="reports/content_evidence_report.json")
    parser.add_argument("--markdown-output", default="reports/Content_Evidence_Adapter_Report.md")
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()
    payload = json.loads(Path(args.input).read_text(encoding="utf-8"))
    report = build_content_evidence_report(payload)
    write_outputs(report, json_path=args.json_output, markdown_path=args.markdown_output)
    print(json.dumps(report, indent=2 if args.pretty else None, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
