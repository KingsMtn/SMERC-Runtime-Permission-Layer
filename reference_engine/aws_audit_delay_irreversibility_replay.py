from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, Mapping

from reference_engine.aws_pending_mutation_cache import build_cache_from_map
from reference_engine.customer_evaluation import (
    CUSTOMER_EVALUATION_VERSION,
    build_customer_evaluation,
    write_outputs as write_customer_outputs,
)


VERSION = "smerc.aws-audit-delay-irreversibility-replay.v1"
MAP_VERSION = "smerc.aws_audit_delay_irreversibility_map.v1"
SOURCE_NAME = "AWS Audit Delay And Irreversibility Replay"


def load_map(path: str | Path) -> Dict[str, Any]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise TypeError("AWS audit-delay map must be a JSON object")
    if payload.get("schema_version") != MAP_VERSION:
        raise ValueError(f"schema_version must be {MAP_VERSION}")
    if "no live AWS data" not in _text(payload.get("source_boundary"), "source_boundary"):
        raise ValueError("source_boundary must state that no live AWS data is used")
    rules = payload.get("structural_irreversibility_rules")
    if not isinstance(rules, list) or not rules:
        raise ValueError("structural_irreversibility_rules must be a non-empty list")
    for index, rule in enumerate(rules):
        _validate_rule(rule, index)
    return payload


def normalize_map(payload: Mapping[str, Any]) -> Dict[str, Any]:
    cache = build_cache_from_map(payload)
    cache_effect = cache.next_action_effect(agent_id="aws-agent-runtime")
    actions = [
        _to_customer_action(rule, index, cache_effect)
        for index, rule in enumerate(payload["structural_irreversibility_rules"], start=1)
    ]
    return {
        "version": CUSTOMER_EVALUATION_VERSION,
        "tenant_id": "aws-audit-delay-irreversibility-replay",
        "organization": "AWS Audit Delay And Irreversibility Replay",
        "contact_role": "cloud_agent_runtime_security_reviewer",
        "evaluation_date": datetime.now(timezone.utc).date().isoformat(),
        "data_boundary": (
            "Metadata-only AWS-style replay. The actions are synthesized from public AWS-style documentation and "
            "SMERC rule metadata. They do not call AWS APIs, assume roles, inspect accounts, read CloudTrail, read "
            "customer data, include account identifiers, include ARNs, include raw logs, or execute production commands."
        ),
        "workflow_context": (
            "Replay delayed-audit and structural-irreversibility scenarios through SMERC using an in-memory pending "
            "mutation cache plus SDL-style guardrails for KMS, CloudTrail, IAM boundary, S3 exposure, broad remediation, "
            "and a second mutation while earlier evidence is unreconciled."
        ),
        "initial_autonomy_state": "WATCH",
        "actions": actions,
    }


def build_report(payload: Mapping[str, Any]) -> Dict[str, Any]:
    normalized = normalize_map(payload)
    evaluation = build_customer_evaluation(normalized)
    cache = build_cache_from_map(payload)
    cache_summary = cache.summary(agent_id="aws-agent-runtime")
    cache_effect = cache.next_action_effect(agent_id="aws-agent-runtime")
    rules = payload["structural_irreversibility_rules"]
    deltas = [_classify_delta(rule, record) for rule, record in zip(rules, evaluation["records"])]
    delta_counts = Counter(item["delta"] for item in deltas)
    default_postures = Counter(str(rule["default_smerc_posture"]) for rule in rules)
    rule_reason_codes = Counter(code for rule in rules for code in rule["reason_codes"])

    return {
        "version": VERSION,
        "generated_at": _now(),
        "source_name": SOURCE_NAME,
        "source_boundary": payload["source_boundary"],
        "public_reference_urls": list(payload.get("public_reference_urls", [])),
        "rule_count": len(rules),
        "normalized_action_count": len(normalized["actions"]),
        "pending_mutation_cache": cache_summary,
        "next_action_effect": cache_effect,
        "expected_posture_counts": dict(sorted(default_postures.items())),
        "rule_reason_code_counts": dict(sorted(rule_reason_codes.items())),
        "smerc_posture_counts": evaluation["summary"]["posture_counts"],
        "governance_route_counts": evaluation["summary"]["route_state_counts"],
        "valid_dll_ledgers": evaluation["summary"]["valid_ledgers"],
        "deltas": deltas,
        "delta_counts": dict(sorted(delta_counts.items())),
        "normalized_customer_evaluation": normalized,
        "customer_evaluation": evaluation,
        "work_result_impact": {
            "work": (
                "Combine an in-memory pending mutation cache with structural dead-end guardrails for AWS-style "
                "agent actions."
            ),
            "result": (
                f"Evaluated {len(normalized['actions'])} AWS-style metadata actions through SMERC, SPARTa routing, "
                "autonomy budgeting, and Decision Lifecycle Ledger evidence."
            ),
            "impact": (
                "SMERC now demonstrates a runnable audit-delay loop: it can remember unreconciled mutations, slow "
                "or stop follow-on actions, and show reviewers that recommendations became route controls."
            ),
        },
        "evidence_boundary": (
            "This is a local metadata-only proof. It does not call AWS APIs, inspect live AWS resources, deploy "
            "EventBridge, CloudTrail, Security Lake, SCPs, Lambda, Redis, ElastiCache, or DynamoDB, and it is not AWS "
            "endorsement or production certification."
        ),
    }


def render_markdown(report: Mapping[str, Any]) -> str:
    lines = [
        "# AWS Audit Delay And Irreversibility Replay Report",
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
        "## Pending Mutation Cache",
        "",
        f"- Active unreconciled count: `{report['pending_mutation_cache']['active_unreconciled_count']}`",
        f"- Highest unreconciled risk: `{report['pending_mutation_cache']['highest_unreconciled_risk']}`",
        f"- Status counts: `{report['pending_mutation_cache']['status_counts']}`",
        f"- Next-action posture hint: `{report['next_action_effect']['posture_hint']}`",
        f"- Next-action reason codes: `{report['next_action_effect']['reason_codes']}`",
        "",
        "## SMERC Results",
        "",
        f"- Rules: `{report['rule_count']}`",
        f"- Normalized actions: `{report['normalized_action_count']}`",
        f"- Expected posture counts: `{report['expected_posture_counts']}`",
        f"- SMERC posture counts: `{report['smerc_posture_counts']}`",
        f"- Governance route counts: `{report['governance_route_counts']}`",
        f"- Valid DLL ledgers: `{report['valid_dll_ledgers']}`",
        f"- Delta counts: `{report['delta_counts']}`",
        "",
        "## Evidence Boundary",
        "",
        str(report["evidence_boundary"]),
        "",
        "## Decision Deltas",
        "",
        "| Rule | AWS action family | Expected posture | SMERC posture | Route | Delta |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for item in report["deltas"]:
        lines.append(
            f"| `{item['rule_id']}` | `{item['aws_action_family']}` | `{item['expected_posture']}` | "
            f"`{item['smerc_posture']}` | `{item['governance_route']}` | `{item['delta']}` |"
        )
    lines.extend(["", "## Public Reference URLs", ""])
    for url in report["public_reference_urls"]:
        lines.append(f"- {url}")
    lines.append("")
    return "\n".join(lines)


def write_outputs(
    report: Mapping[str, Any],
    *,
    normalized_output: str | Path,
    json_output: str | Path,
    markdown_output: str | Path,
    customer_json_output: str | Path,
    customer_markdown_output: str | Path,
) -> None:
    Path(normalized_output).parent.mkdir(parents=True, exist_ok=True)
    Path(json_output).parent.mkdir(parents=True, exist_ok=True)
    Path(markdown_output).parent.mkdir(parents=True, exist_ok=True)
    Path(normalized_output).write_text(
        json.dumps(report["normalized_customer_evaluation"], indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    Path(json_output).write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    Path(markdown_output).write_text(render_markdown(report), encoding="utf-8")
    write_customer_outputs(report["customer_evaluation"], customer_json_output, customer_markdown_output)


def _to_customer_action(rule: Mapping[str, Any], index: int, cache_effect: Mapping[str, Any]) -> Dict[str, Any]:
    rule_id = _text(rule.get("rule_id"), "rule_id")
    posture = _text(rule.get("default_smerc_posture"), "default_smerc_posture")
    effect = rule["recoverability_effect"]
    service = _service(rule)
    reason_codes = list(rule["reason_codes"])
    if "AWS_PENDING_MUTATION_UNRECONCILED" not in reason_codes:
        reason_codes.append("AWS_PENDING_MUTATION_UNRECONCILED")
    return {
        "action_id": f"AWS_AUDIT_DELAY_LOOP_{rule_id.replace('-', '_')}",
        "description": f"{SOURCE_NAME} {rule_id}: {_text(rule.get('name'), 'name')}",
        "actor": "aws-agent-runtime",
        "tool": f"aws.{service}.runtime_gate",
        "action_type": f"aws_structural_irreversibility_{rule_id.lower().replace('-', '_')}",
        "base_action_risk": _risk(posture),
        "reversibility": float(effect["reversibility"]),
        "containment_strength": float(effect["containment_strength"]),
        "rollback_latency": float(effect["rollback_latency"]),
        "evidence_validity": float(effect["evidence_validity"]),
        "anomaly_pressure": min(1.0, _risk(posture) + float(cache_effect["anomaly_pressure_delta"])),
        "impact_scope": _impact_scope(posture),
        "cancel_reliability": _cancel_reliability(posture),
        "authorization_confidence": _authorization_confidence(posture),
        "external_side_effect": True,
        "sensitive_data": service in {"kms", "s3", "cloudtrail"},
        "context": {
            "domain_profile": "cloud_admin",
            "source_name": SOURCE_NAME,
            "rule_id": rule_id,
            "aws_action_patterns": list(rule["aws_action_patterns"]),
            "metadata_only": True,
            "source_boundary": "public AWS-style documentation and SMERC rule metadata only",
            "rule_reason_codes": reason_codes,
            "release_evidence_needed": list(rule["required_evidence_before_release"]),
            "cache_posture_hint": cache_effect["posture_hint"],
            "non_claim": _text(rule["non_claim"], "non_claim"),
        },
        "ref_gate": _ref_gate(posture, service),
        "tool_plan": {
            "version": "smerc.sparta-plan.v1",
            "plan_id": f"plan_aws_audit_delay_{rule_id.lower().replace('-', '_')}",
            "tool": f"aws.{service}.runtime_gate",
            "action": f"aws_structural_irreversibility_{rule_id.lower().replace('-', '_')}",
            "requested_capability": "aws_irreversibility_guardrail",
            "supports_dry_run": posture in {"THROTTLE", "ESCALATE"},
            "supports_scope_limit": posture in {"THROTTLE", "ESCALATE"},
            "supports_checkpoint": posture in {"THROTTLE", "ESCALATE", "FREEZE"},
            "supports_rollback": posture == "THROTTLE",
            "supports_human_approval": True,
            "max_scope_units": _scope(posture, index),
            "requested_scope_units": _scope(posture, index),
            "side_effect_level": "destructive" if posture in {"DENY", "FREEZE"} else "external",
            "metadata": {
                "environment": "metadata_only_aws_replay",
                "rule_id": rule_id,
                "posture_hint": cache_effect["posture_hint"],
                "reason_codes": reason_codes,
            },
        },
    }


def _classify_delta(rule: Mapping[str, Any], record: Mapping[str, Any]) -> Dict[str, Any]:
    expected = str(rule["default_smerc_posture"])
    posture = str(record["decision"]["posture"])
    if expected == posture:
        delta = "SMERC_MATCHES_AWS_GUARDRAIL_EXPECTATION"
    elif posture in {"DENY", "FREEZE"} and expected in {"THROTTLE", "ESCALATE", "FREEZE"}:
        delta = "SMERC_RESTRAINS_MORE_STRONGLY_DUE_TO_GATE_EVIDENCE"
    elif posture == "ESCALATE" and expected == "THROTTLE":
        delta = "SMERC_ESCALATES_UNRECONCILED_MUTATION"
    else:
        delta = "NEEDS_REVIEWER_LABEL"
    return {
        "rule_id": str(rule["rule_id"]),
        "aws_action_family": ", ".join(rule["aws_action_patterns"]),
        "expected_posture": expected,
        "smerc_action_id": str(record["action_id"]),
        "smerc_posture": posture,
        "governance_route": str(record["sparta_route"]["route_state"]),
        "delta": delta,
    }


def _validate_rule(rule: Any, index: int) -> None:
    if not isinstance(rule, dict):
        raise TypeError(f"structural_irreversibility_rules[{index}] must be an object")
    for key in (
        "rule_id",
        "name",
        "aws_action_patterns",
        "default_smerc_posture",
        "reason_codes",
        "recoverability_effect",
        "required_evidence_before_release",
        "non_claim",
    ):
        if key not in rule:
            raise ValueError(f"structural_irreversibility_rules[{index}] missing {key}")
    if rule["default_smerc_posture"] not in {"ALLOW", "THROTTLE", "FREEZE", "DENY", "ESCALATE"}:
        raise ValueError(f"{rule['rule_id']} default_smerc_posture is not supported")
    _list(rule["aws_action_patterns"], f"{rule['rule_id']}.aws_action_patterns")
    _list(rule["reason_codes"], f"{rule['rule_id']}.reason_codes")
    _list(rule["required_evidence_before_release"], f"{rule['rule_id']}.required_evidence_before_release")
    effect = rule["recoverability_effect"]
    if not isinstance(effect, dict):
        raise TypeError(f"{rule['rule_id']}.recoverability_effect must be an object")
    for field in ("reversibility", "containment_strength", "rollback_latency", "evidence_validity"):
        if field not in effect:
            raise ValueError(f"{rule['rule_id']}.recoverability_effect missing {field}")


def _service(rule: Mapping[str, Any]) -> str:
    first = str(rule["aws_action_patterns"][0]).split(":", 1)[0].lower()
    if first == "*":
        return "pending"
    if first == "organizations":
        return "remediation"
    return first


def _ref_gate(posture: str, service: str) -> Dict[str, bool]:
    if posture != "DENY":
        return {
            "typed_contract_valid": True,
            "attestation_valid": True,
            "least_privilege_confirmed": True,
            "object_shape_expected": True,
        }
    return {
        "typed_contract_valid": service not in {"pending"},
        "attestation_valid": False,
        "least_privilege_confirmed": False,
        "object_shape_expected": service not in {"cloudtrail"},
    }


def _risk(posture: str) -> float:
    return {"DENY": 0.96, "FREEZE": 0.88, "ESCALATE": 0.78, "THROTTLE": 0.7, "ALLOW": 0.2}[posture]


def _impact_scope(posture: str) -> float:
    return {"DENY": 0.94, "FREEZE": 0.88, "ESCALATE": 0.78, "THROTTLE": 0.7, "ALLOW": 0.2}[posture]


def _cancel_reliability(posture: str) -> float:
    return {"DENY": 0.12, "FREEZE": 0.22, "ESCALATE": 0.42, "THROTTLE": 0.5, "ALLOW": 0.85}[posture]


def _authorization_confidence(posture: str) -> float:
    return {"DENY": 0.26, "FREEZE": 0.34, "ESCALATE": 0.48, "THROTTLE": 0.54, "ALLOW": 0.9}[posture]


def _scope(posture: str, index: int) -> int:
    return {"DENY": 4, "FREEZE": 6, "ESCALATE": 12, "THROTTLE": 8, "ALLOW": 1}[posture] + index


def _text(value: Any, path: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise TypeError(f"{path} must be a non-empty string")
    return value.strip()


def _list(value: Any, path: str) -> list[str]:
    if not isinstance(value, list) or not value:
        raise TypeError(f"{path} must be a non-empty list")
    return [_text(item, f"{path}[]") for item in value]


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def main() -> int:
    parser = argparse.ArgumentParser(description="Replay AWS audit-delay irreversibility map through SMERC.")
    parser.add_argument("path", help="Path to aws_audit_delay_irreversibility_map.json.")
    parser.add_argument(
        "--normalized-output",
        default="examples/aws_audit_delay_irreversibility_normalized_customer_eval_actions.json",
    )
    parser.add_argument("--json-output", default="reports/aws_audit_delay_irreversibility_replay_report.json")
    parser.add_argument("--markdown-output", default="reports/AWS_Audit_Delay_And_Irreversibility_Replay_Report.md")
    parser.add_argument(
        "--customer-json-output",
        default="reports/aws_audit_delay_irreversibility_customer_evaluation/customer_evaluation_report.json",
    )
    parser.add_argument(
        "--customer-markdown-output",
        default="reports/aws_audit_delay_irreversibility_customer_evaluation/Customer_Evaluation_Report.md",
    )
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()

    report = build_report(load_map(args.path))
    write_outputs(
        report,
        normalized_output=args.normalized_output,
        json_output=args.json_output,
        markdown_output=args.markdown_output,
        customer_json_output=args.customer_json_output,
        customer_markdown_output=args.customer_markdown_output,
    )
    print(json.dumps(report, indent=2 if args.pretty else None, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
