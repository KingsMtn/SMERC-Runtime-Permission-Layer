from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Mapping

from reference_engine.recoverability_engine import RecoverabilityEngine


SELF_GOVERNANCE_SANDBOX_VERSION = "smerc.self-governance-sandbox.v1"
SELF_GOVERNANCE_INPUT_VERSION = "smerc.self-governance-change.v1"
REPORT_VERSION = "smerc.self-governance-sandbox-report.v1"
SELF_CHANGE_MAX_POSTURE = {
    "ALLOW": "THROTTLE",
    "THROTTLE": "THROTTLE",
    "FREEZE": "FREEZE",
    "DENY": "DENY",
    "ESCALATE": "ESCALATE",
}
SELF_CHANGE_ACTION_TYPES = {
    "policy_threshold_change",
    "scoring_weight_change",
    "governance_engine_change",
    "adapter_enforcement_change",
    "runtime_metadata_trust_change",
    "autonomous_policy_update",
}


def evaluate_self_governance_change(payload: Mapping[str, Any]) -> Dict[str, Any]:
    data = _object(payload, "self_governance_change")
    if data.get("schema") != SELF_GOVERNANCE_INPUT_VERSION:
        raise ValueError(f"schema must be {SELF_GOVERNANCE_INPUT_VERSION}")
    proposal_id = _text(data.get("proposal_id"), "proposal_id", 128)
    change_type = _text(data.get("change_type"), "change_type", 128)
    proposed_action = _object(data.get("proposed_action"), "proposed_action")
    reviewer_evidence = _object(data.get("reviewer_evidence"), "reviewer_evidence")
    rollback_plan = _object(data.get("rollback_plan"), "rollback_plan")
    benchmark_evidence = _object(data.get("benchmark_evidence"), "benchmark_evidence")
    activation = _object(data.get("activation"), "activation")

    if proposed_action.get("action_type") not in SELF_CHANGE_ACTION_TYPES:
        raise ValueError("proposed_action.action_type must be a recognized SMERC self-change action type")

    base_decision = RecoverabilityEngine(domain_profile="github_actions").evaluate(dict(proposed_action))
    self_posture = SELF_CHANGE_MAX_POSTURE[base_decision["posture"]]
    evidence_controls = _evidence_controls(
        reviewer_evidence=reviewer_evidence,
        rollback_plan=rollback_plan,
        benchmark_evidence=benchmark_evidence,
        activation=activation,
    )
    if evidence_controls:
        self_posture = _stricter(self_posture, "FREEZE")
    if _bool(activation.get("automatic_activation"), "activation.automatic_activation"):
        self_posture = _stricter(self_posture, "DENY")
    if _bool(activation.get("affects_production_policy"), "activation.affects_production_policy") and not _bool(
        reviewer_evidence.get("human_reviewer_required"), "reviewer_evidence.human_reviewer_required"
    ):
        self_posture = _stricter(self_posture, "DENY")

    reason_codes = _reason_codes(base_decision, evidence_controls, activation)
    controls = _controls(self_posture, base_decision, evidence_controls)
    return {
        "version": SELF_GOVERNANCE_SANDBOX_VERSION,
        "generated_at": _now(),
        "proposal_id": proposal_id,
        "change_type": change_type,
        "base_smerc_posture": base_decision["posture"],
        "self_governed_posture": self_posture,
        "self_change_ceiling_applied": self_posture != base_decision["posture"],
        "scores": base_decision["scores"],
        "base_reason_codes": base_decision["reason_codes"],
        "self_governance_reason_codes": reason_codes,
        "required_controls": controls,
        "activation_allowed": self_posture == "ALLOW",
        "test_only_allowed": self_posture == "THROTTLE" and not evidence_controls,
        "policy_update_requires_review": True,
        "plain_english_summary": _summary(proposal_id, base_decision["posture"], self_posture),
        "evidence_boundary": (
            "This sandbox governs proposed changes to SMERC itself. It does not authorize silent self-training, "
            "autonomous production policy mutation, or deployment without human-owned review and outcome evidence."
        ),
    }


def build_self_governance_report(payload: Mapping[str, Any]) -> Dict[str, Any]:
    proposals = payload.get("proposals")
    if not isinstance(proposals, list) or not proposals:
        raise ValueError("payload.proposals must be a non-empty list")
    results = [evaluate_self_governance_change(item) for item in proposals]
    counts: Dict[str, int] = {}
    for result in results:
        counts[result["self_governed_posture"]] = counts.get(result["self_governed_posture"], 0) + 1
    report = {
        "version": REPORT_VERSION,
        "generated_at": _now(),
        "proposal_count": len(results),
        "self_governed_posture_counts": dict(sorted(counts.items())),
        "ceiling_applied_count": sum(1 for result in results if result["self_change_ceiling_applied"]),
        "test_only_count": sum(1 for result in results if result["test_only_allowed"]),
        "activation_allowed_count": sum(1 for result in results if result["activation_allowed"]),
        "results": results,
        "recommended_next_action": (
            "Use self-governance outputs for local policy-change review only. Publish externally only after the "
            "workflow is tied to real pull requests, reviewer labels, and before/after benchmark evidence."
        ),
        "evidence_boundary": (
            "Synthetic SMERC self-change examples. This is not proof that SMERC can autonomously improve itself."
        ),
    }
    report["markdown_report"] = render_markdown(report)
    return report


def render_markdown(report: Mapping[str, Any]) -> str:
    lines = [
        "# SMERC Self-Governance Sandbox Report",
        "",
        f"- Generated: `{report['generated_at']}`",
        f"- Proposals evaluated: `{report['proposal_count']}`",
        f"- Self-governed posture counts: `{report['self_governed_posture_counts']}`",
        f"- Self-change ceiling applied: `{report['ceiling_applied_count']}`",
        f"- Test-only proposals: `{report['test_only_count']}`",
        f"- Activation allowed: `{report['activation_allowed_count']}`",
        "",
        "## Proposal Results",
        "",
        "| Proposal | Base Posture | Self-Governed Posture | Test Only | Activation Allowed |",
        "|---|---:|---:|---:|---:|",
    ]
    for result in report["results"]:
        lines.append(
            "| "
            + " | ".join(
                [
                    _escape(result["proposal_id"]),
                    _escape(result["base_smerc_posture"]),
                    _escape(result["self_governed_posture"]),
                    str(result["test_only_allowed"]).lower(),
                    str(result["activation_allowed"]).lower(),
                ]
            )
            + " |"
        )
    lines.extend(
        [
            "",
            "## Recommended Next Action",
            "",
            str(report["recommended_next_action"]),
            "",
            "## Evidence Boundary",
            "",
            str(report["evidence_boundary"]),
            "",
        ]
    )
    return "\n".join(lines)


def write_outputs(report: Mapping[str, Any], *, json_path: str | Path, markdown_path: str | Path) -> None:
    Path(json_path).parent.mkdir(parents=True, exist_ok=True)
    Path(markdown_path).parent.mkdir(parents=True, exist_ok=True)
    Path(json_path).write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    Path(markdown_path).write_text(str(report["markdown_report"]) + "\n", encoding="utf-8")


def _evidence_controls(
    *,
    reviewer_evidence: Mapping[str, Any],
    rollback_plan: Mapping[str, Any],
    benchmark_evidence: Mapping[str, Any],
    activation: Mapping[str, Any],
) -> list[str]:
    controls = []
    if not _bool(reviewer_evidence.get("human_reviewer_required"), "reviewer_evidence.human_reviewer_required"):
        controls.append("require_human_reviewer")
    if not _bool(reviewer_evidence.get("review_record_required"), "reviewer_evidence.review_record_required"):
        controls.append("require_review_record")
    if not _bool(rollback_plan.get("rollback_defined"), "rollback_plan.rollback_defined"):
        controls.append("define_policy_rollback_plan")
    if not _bool(rollback_plan.get("previous_policy_retained"), "rollback_plan.previous_policy_retained"):
        controls.append("retain_previous_policy_version")
    if not _bool(benchmark_evidence.get("before_after_required"), "benchmark_evidence.before_after_required"):
        controls.append("require_before_after_benchmark")
    if not _bool(benchmark_evidence.get("regression_suite_required"), "benchmark_evidence.regression_suite_required"):
        controls.append("require_regression_suite")
    if _bool(activation.get("affects_production_policy"), "activation.affects_production_policy") and not _bool(
        activation.get("shadow_mode_first"), "activation.shadow_mode_first"
    ):
        controls.append("start_in_shadow_mode")
    return controls


def _reason_codes(
    base_decision: Mapping[str, Any],
    evidence_controls: list[str],
    activation: Mapping[str, Any],
) -> list[str]:
    codes = ["SMERC_SELF_CHANGE_REVIEW_REQUIRED"]
    if base_decision["posture"] == "ALLOW":
        codes.append("ALLOW_CAPPED_FOR_GOVERNANCE_LAYER_CHANGE")
    if evidence_controls:
        codes.append("SELF_CHANGE_EVIDENCE_INCOMPLETE")
    if _bool(activation.get("automatic_activation"), "activation.automatic_activation"):
        codes.append("AUTONOMOUS_POLICY_MUTATION_PROHIBITED")
    if _bool(activation.get("affects_production_policy"), "activation.affects_production_policy"):
        codes.append("PRODUCTION_POLICY_CHANGE")
    return codes


def _controls(self_posture: str, base_decision: Mapping[str, Any], evidence_controls: list[str]) -> list[str]:
    controls = set(base_decision.get("controls", []))
    controls.update(
        {
            "record_policy_change_dll",
            "compare_before_after_benchmark",
            "require_reviewer_approval",
        }
    )
    if self_posture == "THROTTLE":
        controls.add("test_only")
        controls.add("shadow_mode_before_activation")
    if self_posture in {"FREEZE", "DENY", "ESCALATE"}:
        controls.add("do_not_activate_policy_change")
        controls.add("require_design_review")
    controls.update(evidence_controls)
    return sorted(controls)


POSTURE_ORDER = {"ALLOW": 0, "THROTTLE": 1, "FREEZE": 2, "ESCALATE": 2, "DENY": 3}


def _stricter(left: str, right: str) -> str:
    return left if POSTURE_ORDER[left] >= POSTURE_ORDER[right] else right


def _summary(proposal_id: str, base_posture: str, self_posture: str) -> str:
    if base_posture == "ALLOW" and self_posture == "THROTTLE":
        return (
            f"{proposal_id} looks recoverable enough to test, but SMERC self-changes are capped at test-only "
            "until human review, benchmark comparison, rollback evidence, and DLL recording are complete."
        )
    if self_posture == "DENY":
        return f"{proposal_id} should not be activated because the proposed governance-layer change is not structurally defensible."
    if self_posture == "FREEZE":
        return f"{proposal_id} should pause for design review before any activation path is considered."
    return f"{proposal_id} may proceed only under constrained self-governance controls."


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


def _bool(value: Any, path: str) -> bool:
    if not isinstance(value, bool):
        raise TypeError(f"{path} must be a boolean")
    return value


def _escape(value: str) -> str:
    return str(value).replace("|", "\\|")


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def main() -> int:
    parser = argparse.ArgumentParser(description="Evaluate proposed SMERC changes through the SMERC self-governance sandbox.")
    parser.add_argument("--input", default="examples/self_governance_change_proposals.json")
    parser.add_argument("--json-output", default="reports/self_governance_sandbox_report.json")
    parser.add_argument("--markdown-output", default="reports/Self_Governance_Sandbox_Report.md")
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()
    payload = json.loads(Path(args.input).read_text(encoding="utf-8"))
    report = build_self_governance_report(payload)
    write_outputs(report, json_path=args.json_output, markdown_path=args.markdown_output)
    print(json.dumps(report, indent=2 if args.pretty else None, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
