from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, Mapping


RUNTIME_EVIDENCE_TRUST_VERSION = "smerc.runtime-evidence-trust.v1"
INPUT_VERSION = "smerc.runtime-evidence-trust-input.v1"
TRUSTED_ASSERTION_TYPES = {
    "github_oidc_claims",
    "mcp_proxy_observation",
    "deployment_adapter_receipt",
    "human_review_record",
    "ticketing_system_record",
    "cloud_audit_event",
    "signed_runtime_attestation",
}
HIGH_IMPACT_FIELDS = {
    "actor",
    "authority_basis",
    "environment",
    "operation",
    "resource",
    "impact_scope",
    "reversibility",
    "rollback_method",
    "containment_strength",
}


def evaluate_runtime_evidence_trust(payload: Mapping[str, Any]) -> Dict[str, Any]:
    data = _object(payload, "runtime_evidence")
    if data.get("schema") != INPUT_VERSION:
        raise ValueError(f"schema must be {INPUT_VERSION}")
    action_id = _text(data.get("action_id"), "action_id", 128)
    sources = _sources(data.get("evidence_sources"))
    required_fields = _text_list(data.get("required_fields"), "required_fields", allow_empty=False)
    observed_fields = _observed_fields(data.get("observed_fields"), sources)
    agent_supplied_fields = set(_text_list(data.get("agent_supplied_fields", []), "agent_supplied_fields", allow_empty=True))

    coverage = _coverage(required_fields, observed_fields)
    source_score = _source_score(sources)
    authentication_score = _authentication_score(sources)
    freshness_score = _freshness_score(sources)
    independence_score = _independence_score(sources)
    agent_penalty = _agent_supplied_penalty(agent_supplied_fields)
    high_impact_self_reported = sorted(agent_supplied_fields & HIGH_IMPACT_FIELDS)

    trust_score = _clamp(
        0.24 * coverage
        + 0.22 * authentication_score
        + 0.2 * source_score
        + 0.18 * independence_score
        + 0.16 * freshness_score
        - agent_penalty
    )
    trust_level = _trust_level(trust_score, high_impact_self_reported)
    max_posture = _max_posture(trust_level)
    reason_codes = _reason_codes(
        coverage=coverage,
        sources=sources,
        agent_supplied_fields=agent_supplied_fields,
        high_impact_self_reported=high_impact_self_reported,
        trust_level=trust_level,
    )
    controls = _controls(trust_level, high_impact_self_reported, coverage)
    return {
        "version": RUNTIME_EVIDENCE_TRUST_VERSION,
        "generated_at": _now(),
        "action_id": action_id,
        "trust_level": trust_level,
        "trusted_metadata_score": round(trust_score, 3),
        "field_coverage_score": round(coverage, 3),
        "source_trust_score": round(source_score, 3),
        "authentication_score": round(authentication_score, 3),
        "freshness_score": round(freshness_score, 3),
        "independence_score": round(independence_score, 3),
        "agent_supplied_penalty": round(agent_penalty, 3),
        "admissible_for_runtime_decision": trust_level in {"HIGH", "MEDIUM"},
        "max_recommended_posture": max_posture,
        "trusted_fields": sorted(observed_fields),
        "missing_required_fields": sorted(set(required_fields) - set(observed_fields)),
        "agent_supplied_fields": sorted(agent_supplied_fields),
        "high_impact_self_reported_fields": high_impact_self_reported,
        "reason_codes": reason_codes,
        "required_controls": controls,
        "plain_english_summary": _summary(trust_level, max_posture, high_impact_self_reported),
        "evidence_boundary": (
            "This gate evaluates whether supplied metadata is reliable enough for shadow-mode governance evidence. "
            "It does not prove the action is safe, production-ready, compliant, or customer-validated."
        ),
    }


def build_runtime_evidence_trust_report(payload: Mapping[str, Any]) -> Dict[str, Any]:
    scenarios = payload.get("scenarios")
    if not isinstance(scenarios, list) or not scenarios:
        raise ValueError("payload.scenarios must be a non-empty list")
    results = [evaluate_runtime_evidence_trust(item) for item in scenarios]
    counts: Dict[str, int] = {}
    for result in results:
        counts[result["trust_level"]] = counts.get(result["trust_level"], 0) + 1
    average_score = sum(result["trusted_metadata_score"] for result in results) / len(results)
    report = {
        "version": "smerc.runtime-evidence-trust-report.v1",
        "generated_at": _now(),
        "scenario_count": len(results),
        "trust_level_counts": dict(sorted(counts.items())),
        "average_trusted_metadata_score": round(average_score, 3),
        "admissible_count": sum(1 for result in results if result["admissible_for_runtime_decision"]),
        "capped_posture_count": sum(1 for result in results if result["max_recommended_posture"] != "ALLOW"),
        "results": results,
        "evidence_boundary": (
            "Synthetic examples demonstrate metadata-trust handling. Replace these records with customer-approved "
            "runtime metadata from proxies, OIDC claims, adapters, ticketing systems, or audit logs during a pilot."
        ),
    }
    report["markdown_report"] = render_markdown(report)
    return report


def render_markdown(report: Mapping[str, Any]) -> str:
    lines = [
        "# SMERC Runtime Evidence Trust Gate Report",
        "",
        f"- Generated: `{report['generated_at']}`",
        f"- Scenarios evaluated: `{report['scenario_count']}`",
        f"- Trust level counts: `{report['trust_level_counts']}`",
        f"- Average trusted metadata score: `{report['average_trusted_metadata_score']}`",
        f"- Admissible for runtime decision: `{report['admissible_count']}`",
        f"- Decisions capped below ALLOW: `{report['capped_posture_count']}`",
        "",
        "## Scenario Results",
        "",
        "| Action | Trust | Score | Max Posture | Missing Fields | High-Impact Self-Reported Fields |",
        "|---|---:|---:|---:|---|---|",
    ]
    for result in report["results"]:
        lines.append(
            "| "
            + " | ".join(
                [
                    _escape(result["action_id"]),
                    _escape(result["trust_level"]),
                    str(result["trusted_metadata_score"]),
                    _escape(result["max_recommended_posture"]),
                    _escape(", ".join(result["missing_required_fields"]) or "None"),
                    _escape(", ".join(result["high_impact_self_reported_fields"]) or "None"),
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


def _sources(value: Any) -> list[Dict[str, Any]]:
    if not isinstance(value, list) or not value:
        raise TypeError("evidence_sources must be a non-empty list")
    normalized = []
    names = set()
    for index, item in enumerate(value):
        source = _object(item, f"evidence_sources[{index}]")
        name = _text(source.get("source"), f"evidence_sources[{index}].source", 128)
        if name in names:
            raise ValueError("evidence_sources.source values must be unique")
        names.add(name)
        assertion_type = _text(source.get("assertion_type"), f"evidence_sources[{index}].assertion_type", 128)
        normalized.append(
            {
                "source": name,
                "assertion_type": assertion_type,
                "authenticated": _bool(source.get("authenticated"), f"evidence_sources[{index}].authenticated"),
                "signed": _bool(source.get("signed"), f"evidence_sources[{index}].signed"),
                "agent_supplied": _bool(source.get("agent_supplied"), f"evidence_sources[{index}].agent_supplied"),
                "freshness_seconds": _non_negative_number(
                    source.get("freshness_seconds"), f"evidence_sources[{index}].freshness_seconds"
                ),
            }
        )
    return normalized


def _observed_fields(value: Any, sources: list[Mapping[str, Any]]) -> Dict[str, str]:
    if not isinstance(value, dict) or not value:
        raise TypeError("observed_fields must be a non-empty object")
    source_names = {source["source"] for source in sources}
    fields: Dict[str, str] = {}
    for key, source in value.items():
        field = _text(key, "observed_fields key", 128)
        source_name = _text(source, f"observed_fields.{field}", 128)
        if source_name not in source_names:
            raise ValueError(f"observed_fields.{field} references unknown evidence source {source_name}")
        fields[field] = source_name
    return fields


def _coverage(required_fields: list[str], observed_fields: Mapping[str, str]) -> float:
    return len(set(required_fields) & set(observed_fields)) / len(set(required_fields))


def _source_score(sources: list[Mapping[str, Any]]) -> float:
    trusted = sum(1 for source in sources if source["assertion_type"] in TRUSTED_ASSERTION_TYPES)
    return trusted / len(sources)


def _authentication_score(sources: list[Mapping[str, Any]]) -> float:
    return sum(1 for source in sources if source["authenticated"] and source["signed"]) / len(sources)


def _freshness_score(sources: list[Mapping[str, Any]]) -> float:
    scores = []
    for source in sources:
        seconds = float(source["freshness_seconds"])
        if seconds <= 300:
            scores.append(1.0)
        elif seconds <= 3600:
            scores.append(0.75)
        elif seconds <= 86400:
            scores.append(0.4)
        else:
            scores.append(0.1)
    return sum(scores) / len(scores)


def _independence_score(sources: list[Mapping[str, Any]]) -> float:
    return sum(1 for source in sources if not source["agent_supplied"]) / len(sources)


def _agent_supplied_penalty(fields: set[str]) -> float:
    if not fields:
        return 0.0
    penalty = min(0.22, len(fields) * 0.035)
    if fields & HIGH_IMPACT_FIELDS:
        penalty += 0.18
    return min(0.4, penalty)


def _trust_level(score: float, high_impact_self_reported: list[str]) -> str:
    if high_impact_self_reported and score < 0.9:
        return "LOW"
    if score >= 0.82:
        return "HIGH"
    if score >= 0.64:
        return "MEDIUM"
    if score >= 0.42:
        return "LOW"
    return "UNTRUSTED"


def _max_posture(trust_level: str) -> str:
    return {
        "HIGH": "ALLOW",
        "MEDIUM": "THROTTLE",
        "LOW": "FREEZE",
        "UNTRUSTED": "DENY",
    }[trust_level]


def _reason_codes(
    *,
    coverage: float,
    sources: list[Mapping[str, Any]],
    agent_supplied_fields: set[str],
    high_impact_self_reported: list[str],
    trust_level: str,
) -> list[str]:
    codes = [f"RUNTIME_EVIDENCE_TRUST_{trust_level}"]
    if coverage < 1:
        codes.append("REQUIRED_METADATA_INCOMPLETE")
    if any(source["assertion_type"] not in TRUSTED_ASSERTION_TYPES for source in sources):
        codes.append("UNRECOGNIZED_EVIDENCE_ASSERTION_TYPE")
    if any(not source["authenticated"] or not source["signed"] for source in sources):
        codes.append("UNAUTHENTICATED_OR_UNSIGNED_SOURCE")
    if agent_supplied_fields:
        codes.append("AGENT_SUPPLIED_METADATA_PRESENT")
    if high_impact_self_reported:
        codes.append("HIGH_IMPACT_METADATA_SELF_REPORTED")
    if any(source["freshness_seconds"] > 3600 for source in sources):
        codes.append("STALE_RUNTIME_EVIDENCE")
    return codes


def _controls(trust_level: str, high_impact_self_reported: list[str], coverage: float) -> list[str]:
    controls = []
    if trust_level != "HIGH":
        controls.append("require_trusted_runtime_observation")
    if trust_level in {"LOW", "UNTRUSTED"}:
        controls.append("do_not_allow_based_on_agent_self_description")
    if high_impact_self_reported:
        controls.append("replace_high_impact_fields_with_proxy_or_adapter_evidence")
    if coverage < 1:
        controls.append("collect_missing_required_metadata_before_recommendation")
    if trust_level == "UNTRUSTED":
        controls.append("block_or_hold_until_authenticated_context_exists")
    return controls or ["no_additional_metadata_trust_control_required"]


def _summary(trust_level: str, max_posture: str, high_impact_self_reported: list[str]) -> str:
    if high_impact_self_reported:
        return (
            "The action includes high-impact fields supplied by the proposing agent. SMERC should not treat this "
            f"metadata as sufficient for autonomous release; cap the decision at {max_posture} until trusted runtime "
            "or adapter evidence replaces those fields."
        )
    if trust_level == "HIGH":
        return "The supplied runtime metadata is fresh, authenticated, independently observed, and sufficient for normal shadow-mode decision evidence."
    if trust_level == "MEDIUM":
        return "The supplied metadata is usable for a constrained recommendation, but should not support an unrestricted allow without more trusted evidence."
    if trust_level == "LOW":
        return "The supplied metadata has material trust gaps; preserve the record but freeze or escalate before execution."
    return "The supplied metadata is not reliable enough for a runtime governance decision; deny or hold until authenticated context exists."


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


def _text_list(value: Any, path: str, *, allow_empty: bool) -> list[str]:
    if not isinstance(value, list) or (not value and not allow_empty):
        raise TypeError(f"{path} must be a {'possibly empty' if allow_empty else 'non-empty'} list")
    items = [_text(item, f"{path}[{index}]", 128) for index, item in enumerate(value)]
    if len(set(items)) != len(items):
        raise ValueError(f"{path} must not contain duplicates")
    return items


def _bool(value: Any, path: str) -> bool:
    if not isinstance(value, bool):
        raise TypeError(f"{path} must be a boolean")
    return value


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
    parser = argparse.ArgumentParser(description="Score whether runtime metadata is trustworthy enough for SMERC evidence.")
    parser.add_argument("--input", default="examples/runtime_evidence_trust_examples.json")
    parser.add_argument("--json-output", default="reports/runtime_evidence_trust_report.json")
    parser.add_argument("--markdown-output", default="reports/Runtime_Evidence_Trust_Gate_Report.md")
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()
    payload = json.loads(Path(args.input).read_text(encoding="utf-8"))
    report = build_runtime_evidence_trust_report(payload)
    write_outputs(report, json_path=args.json_output, markdown_path=args.markdown_output)
    print(json.dumps(report, indent=2 if args.pretty else None, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
