from __future__ import annotations

from typing import Any, Mapping

from reference_engine.aws_mcp_recovery_proof import run_proof


VERSION = "smerc.iam-runtime-assurance-comparison.v1"


def build_comparison(
    *, iam_authorized: bool = True,
    iam_evidence: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Compare supplied IAM authorization evidence with SMERC recovery decisions."""
    evidence = dict(iam_evidence or {
        "evidence_class": "synthetic_policy_evaluation",
        "principal": "arn:aws:iam::123456789012:role/smerc-pilot",
        "action": "cloudformation:UpdateStack",
        "resource": "arn:aws:cloudformation:us-east-1:123456789012:stack/smerc-pilot/*",
        "decision": "allowed" if iam_authorized else "denied",
    })
    _validate_iam_evidence(evidence, iam_authorized)
    proof = run_proof()
    rows = []
    for recovery_case in ("missing", "stale", "verified"):
        case = proof["cases"][recovery_case]
        boundary = case["recovery_boundary"]
        posture = boundary["max_recommended_posture"]
        route = "NOT_REACHED"
        if case["normal_governance_reached"]:
            proxy = case["transport_response"].get("result", {}).get("smerc_proxy", {})
            posture = proxy.get("posture") or posture
            route = proxy.get("route_state", "UNKNOWN")
        rows.append({
            "scenario": f"iam_{'allowed' if iam_authorized else 'denied'}_recovery_{recovery_case}",
            "iam_authorized": iam_authorized,
            "iam_decision": evidence["decision"],
            "recovery_case": recovery_case,
            "smerc_posture": posture,
            "smerc_route": route,
            "normal_governance_reached": case["normal_governance_reached"],
            "decision_delta": _delta(iam_authorized, posture),
            "authority_effect": boundary["authority_effect"],
        })
    return {
        "version": VERSION,
        "comparison_question": (
            "After an AWS identity is authorized for this action, does current recovery evidence support "
            "executing it now, and under what constraints?"
        ),
        "iam_evidence": evidence,
        "rows": rows,
        "delta_count": sum(1 for row in rows if row["decision_delta"] != "NO_ADDITIONAL_CONSTRAINT"),
        "aws_resources_created_or_modified": False,
        "incremental_aws_cost_usd": 0.0,
        "interpretation": (
            "IAM authorization and SMERC runtime posture answer different questions. This synthetic comparison "
            "does not claim that IAM cannot express conditions or that SMERC replaces AWS authorization."
        ),
        "evidence_boundary": (
            "The IAM decision is supplied synthetic policy-evaluation metadata, not a live IAM Policy Simulator "
            "result or AWS attestation. SMERC outcomes are deterministic local reference-engine evidence."
        ),
    }


def render_markdown(report: Mapping[str, Any]) -> str:
    lines = [
        "# IAM and SMERC Runtime Assurance Decision Comparison", "",
        f"Version: `{report['version']}`", "", "## Comparison Question", "",
        str(report["comparison_question"]), "", "## Decision Deltas", "",
        "| Recovery evidence | IAM | SMERC posture | Route | Delta |",
        "| --- | --- | --- | --- | --- |",
    ]
    for row in report["rows"]:
        lines.append(
            f"| `{row['recovery_case']}` | `{row['iam_decision']}` | `{row['smerc_posture']}` | "
            f"`{row['smerc_route']}` | `{row['decision_delta']}` |"
        )
    lines.extend([
        "", "## Interpretation", "", str(report["interpretation"]), "",
        "## Evidence Boundary", "", str(report["evidence_boundary"]), "",
    ])
    return "\n".join(lines)


def _delta(iam_authorized: bool, posture: str | None) -> str:
    if not iam_authorized:
        return "IAM_DENY_PRESERVED"
    return {
        "DENY": "AUTHORIZED_BUT_RECOVERY_DENIED",
        "FREEZE": "AUTHORIZED_BUT_RECOVERY_REVIEW_REQUIRED",
        "THROTTLE": "AUTHORIZED_BUT_RECOVERY_CONSTRAINED",
        "ESCALATE": "AUTHORIZED_BUT_ESCALATION_REQUIRED",
        "ALLOW": "NO_ADDITIONAL_CONSTRAINT",
    }.get(posture, "AUTHORIZED_BUT_RUNTIME_OUTCOME_UNKNOWN")


def _validate_iam_evidence(evidence: Mapping[str, Any], authorized: bool) -> None:
    required = {"evidence_class", "principal", "action", "resource", "decision"}
    if set(evidence) != required:
        raise ValueError("IAM evidence fields must match the comparison contract")
    for field in required:
        if not isinstance(evidence[field], str) or not evidence[field].strip():
            raise ValueError(f"IAM evidence {field} must be non-empty text")
    expected = "allowed" if authorized else "denied"
    if evidence["decision"] != expected:
        raise ValueError("IAM evidence decision does not match iam_authorized")
