from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Mapping

from integrations.github_pr_guardian.pr_guardian import build_certificate, render_pr_comment
from reference_engine.agent_permission_layer import RuntimePermissionEngine
from reference_engine.decision_lifecycle_ledger import DecisionLifecycleLedger
from reference_engine.dll_intelligence import analyze_ledgers
from reference_engine.sparta_router import SPARTA_PLAN_VERSION, route_decision, route_report_digest


DEMO_VERSION = "smerc.end-to-end-pr-guardian-demo.v1"


DEFAULT_ACTION = {
    "action_id": "AI_AUTH_MIDDLEWARE_PR",
    "description": "AI coding agent proposes changing authentication middleware and deployment configuration in a pull request.",
    "tool": "github.pull_request",
    "actor": "coding_agent",
    "confidence": 0.61,
    "harm": 0.84,
    "consent": 0.66,
    "reversibility": 0.39,
    "external_effect": True,
    "sensitive_data": True,
    "context": {
        "workflow": "pull_request",
        "touched_area": "authentication",
        "rollback_plan": "partial_git_revert_plus_canary",
        "existing_controls": ["branch_protection", "code_review", "environment_approval"],
    },
}


DEFAULT_TOOL_PLAN = {
    "version": SPARTA_PLAN_VERSION,
    "plan_id": "github-pr-guardian-auth-change",
    "tool": "github_actions",
    "action": "evaluate_and_comment_on_pr",
    "requested_capability": "pull_request_governance",
    "supports_dry_run": True,
    "supports_scope_limit": True,
    "supports_checkpoint": True,
    "supports_rollback": True,
    "supports_human_approval": True,
    "max_scope_units": 100,
    "requested_scope_units": 80,
    "side_effect_level": "external",
    "metadata": {
        "workflow": "smerc-pr-guardian.yml",
        "review_surface": "pull_request_comment",
        "environment": "production-adjacent",
    },
}


def _load_json(path: Path) -> Dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise TypeError(f"{path} must contain a JSON object")
    return payload


def _decision_for_sparta(decision: Mapping[str, Any]) -> Dict[str, Any]:
    controls = decision.get("controls", decision.get("constraints", []))
    if not isinstance(controls, list):
        controls = []
    return {
        "posture": decision.get("posture"),
        "replay_id": decision.get("replay_id"),
        "reason_codes": list(decision.get("reason_codes", [])),
        "controls": [str(item) for item in controls],
        "policy": {"source": "end_to_end_pr_guardian_demo"},
    }


def _build_decision_report(action: Mapping[str, Any]) -> Dict[str, Any]:
    decision = RuntimePermissionEngine().evaluate(action)
    return {
        "mode": "observe",
        "source": "local",
        "integration_status": "evaluated",
        "enforcement": {
            "active": False,
            "would_fail": decision["posture"] in {"DENY", "FREEZE"},
            "fail_on": ["DENY", "FREEZE"],
        },
        "decision": decision,
    }


def _ledger_for_demo(
    *,
    action: Mapping[str, Any],
    decision: Mapping[str, Any],
    route_report: Mapping[str, Any],
    certificate: Mapping[str, Any],
) -> DecisionLifecycleLedger:
    posture = str(decision["posture"])
    controls = [str(item) for item in decision.get("constraints", decision.get("controls", []))]
    reason_codes = [str(item) for item in decision.get("reason_codes", [])]
    route_state = str(route_report["route_state"])
    recoverability_score = max(0.0, min(1.0, float(action.get("reversibility", 0.0))))
    ledger = DecisionLifecycleLedger(
        f"dll_{decision['replay_id']}",
        tenant_id="pr-guardian-demo",
    )
    ledger.append(
        "REQUEST",
        str(action.get("actor", "coding_agent")),
        {
            "initiated_by": str(action.get("actor", "coding_agent")),
            "requested_operation": str(action.get("description", "AI-assisted pull request action")),
            "environment": "github_pull_request",
            "risk_profile": "ai_assisted_code_change",
        },
        recorded_at="2026-07-28T12:00:00+00:00",
    )
    ledger.append(
        "EVIDENCE",
        "smerc-pr-guardian",
        {
            "available_evidence": [
                "pull_request_metadata",
                "declared_action_request",
                "existing_branch_protection",
                "smerc_runtime_decision",
                "sparta_route_report",
            ],
            "confidence_score": float(decision.get("confidence_score", 0.0)),
            "missing_evidence": ["customer_reviewer_label", "live_execution_outcome"],
            "external_dependencies": ["github_actions", "pull_request_review"],
            "model_version": "declared-ai-agent",
            "policy_version": "smerc.pr-guardian.demo.v1",
        },
        recorded_at="2026-07-28T12:00:02+00:00",
    )
    ledger.append(
        "EVALUATION",
        "smerc-engine",
        {
            "structural_state": f"AI-assisted pull request received {posture} before merge or deployment.",
            "entropy_indicators": reason_codes,
            "recoverability_score": recoverability_score,
            "authorization_recommendation": posture,
            "reason_codes": reason_codes,
            "recommended_safeguards": controls,
        },
        recorded_at="2026-07-28T12:00:03+00:00",
    )
    ledger.append(
        "HUMAN_INTERACTION",
        "pilot-reviewer",
        {
            "interaction": "accepted",
            "reviewer_id": "pilot-reviewer",
            "original_recommendation": posture,
            "final_recommendation": posture,
            "rationale": "Demo reviewer accepts the SMERC posture for the end-to-end pilot artifact.",
        },
        recorded_at="2026-07-28T12:03:00+00:00",
    )
    execution_status = "succeeded" if route_report.get("executable") else "blocked"
    ledger.append(
        "EXECUTION",
        "sparta-router",
        {
            "executed_operation": (
                f"Rendered PR Guardian comment and routed posture into {route_state}."
                if route_report.get("executable")
                else f"Rendered PR Guardian comment and preserved blocked route {route_state}."
            ),
            "execution_status": execution_status,
            "started_at": "2026-07-28T12:05:00+00:00",
            "duration_ms": 42000,
            "rollback_performed": False,
            "rollback_success": None,
        },
        recorded_at="2026-07-28T12:06:00+00:00",
    )
    ledger.append(
        "OUTCOME",
        "demo-review-lead",
        {
            "judged_correct": True,
            "unexpected_consequences": False,
            "controls_sufficient": True,
            "cost_incurred": 0,
            "time_to_recover_minutes": 0,
            "customer_impact": "none; synthetic end-to-end demo",
            "security_impact": "none; synthetic end-to-end demo",
            "financial_impact": "none; synthetic end-to-end demo",
        },
        recorded_at="2026-07-29T12:00:00+00:00",
    )
    ledger.append(
        "LEARNING_RECOMMENDATION",
        "smerc-dll",
        {
            "expected_outcome": "PR Guardian makes the runtime decision visible before merge.",
            "actual_outcome": "PR comment, certificate, SPARTa route, DLL, and DLL Intelligence report were generated.",
            "prediction_error": "not measured in synthetic demo",
            "human_override_effectiveness": "no override occurred",
            "recommended_policy_updates": [
                "In a customer pilot, compare PR Guardian posture against reviewer agreement before enforcement."
            ],
            "confidence_calibration_changes": [
                "Do not calibrate from this synthetic demo; collect customer-context PR records."
            ],
            "suggested_rule_modifications": [
                f"Retain certificate digest {certificate['certificate_digest']} with workflow artifacts."
            ],
            "activation_status": "requires_review",
        },
        recorded_at="2026-07-29T12:05:00+00:00",
    )
    return ledger


def build_end_to_end_demo(
    *,
    action: Mapping[str, Any] | None = None,
    tool_plan: Mapping[str, Any] | None = None,
) -> Dict[str, Any]:
    action_payload = dict(action or DEFAULT_ACTION)
    plan_payload = dict(tool_plan or DEFAULT_TOOL_PLAN)
    decision_report = _build_decision_report(action_payload)
    decision = decision_report["decision"]
    pr_certificate = build_certificate(
        decision_report,
        action_request=action_payload,
        event_metadata={
            "repository": "KingsMtn/SMERC-Runtime-Permission-Layer",
            "workflow": "SMERC PR Guardian",
            "event_name": "pull_request",
            "pull_request": {
                "number": 101,
                "title": "AI-assisted authentication middleware change",
                "user": "coding-agent",
                "base_ref": "main",
                "head_sha": "demo-head-sha",
            },
        },
        issued_at="2026-07-28T12:00:05+00:00",
    )
    pr_comment = render_pr_comment(pr_certificate)
    route_report = route_decision(_decision_for_sparta(decision), plan_payload)
    ledger = _ledger_for_demo(
        action=action_payload,
        decision=decision,
        route_report=route_report,
        certificate=pr_certificate,
    )
    ledger_data = ledger.to_dict()
    dll_intelligence = analyze_ledgers([ledger_data])
    return {
        "version": DEMO_VERSION,
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "action_request": action_payload,
        "decision_report": decision_report,
        "pr_guardian": {
            "comment_markdown": pr_comment,
            "certificate": pr_certificate,
        },
        "sparta_route": {
            "route_report": route_report,
            "route_report_digest": route_report_digest(route_report),
        },
        "decision_lifecycle_ledger": ledger_data,
        "dll_intelligence": dll_intelligence,
        "integrated_flow": [
            "AI-assisted PR request declared",
            "SMERC runtime engine evaluated recoverability posture",
            "PR Guardian rendered pull-request comment and certificate",
            "SPARTa routed posture into executable, constrained, paused, blocked, or review-required behavior",
            "Decision Lifecycle Ledger recorded request, evidence, evaluation, review, execution, outcome, and learning",
            "DLL Intelligence summarized the verified lifecycle record",
        ],
        "boundary": [
            "Synthetic end-to-end demo; not customer production evidence.",
            "PR Guardian does not replace branch protection, code review, security review, deployment approvals, or human accountability.",
            "Customer-context pilot records are required before claiming operational risk reduction.",
        ],
    }


def render_markdown(bundle: Mapping[str, Any]) -> str:
    decision = bundle["decision_report"]["decision"]
    route = bundle["sparta_route"]["route_report"]
    certificate = bundle["pr_guardian"]["certificate"]
    ledger = bundle["decision_lifecycle_ledger"]
    intelligence = bundle["dll_intelligence"]
    lines = [
        "# SMERC End-To-End PR Guardian Demo",
        "",
        "## Executive Summary",
        "",
        "This demo proves the current SMERC modules work as one runtime governance loop for an AI-assisted pull request.",
        "",
        "```text",
        "AI-assisted PR request -> SMERC decision -> PR Guardian comment/certificate -> SPARTa route -> Decision Lifecycle Ledger -> DLL Intelligence",
        "```",
        "",
        "## 1. Action Request",
        "",
        f"- Action ID: `{bundle['action_request']['action_id']}`",
        f"- Actor: `{bundle['action_request']['actor']}`",
        f"- Tool: `{bundle['action_request']['tool']}`",
        f"- Description: {bundle['action_request']['description']}",
        "",
        "## 2. SMERC Runtime Decision",
        "",
        f"- Posture: `{decision['posture']}`",
        f"- Risk score: `{decision.get('risk_score')}`",
        f"- Confidence score: `{decision.get('confidence_score')}`",
        f"- Replay ID: `{decision['replay_id']}`",
        f"- Reason codes: `{decision['reason_codes']}`",
        f"- Controls: `{decision.get('constraints', decision.get('controls', []))}`",
        "",
        "## 3. PR Guardian Visible Review Artifact",
        "",
        f"- Certificate digest: `{certificate['certificate_digest']}`",
        f"- Comment posture: `{certificate['posture']}`",
        "",
        "```markdown",
        bundle["pr_guardian"]["comment_markdown"].strip(),
        "```",
        "",
        "## 4. SPARTa Route",
        "",
        f"- Route state: `{route['route_state']}`",
        f"- Executable: `{route['executable']}`",
        f"- Effective scope units: `{route['effective_scope_units']}`",
        f"- Applied controls: `{route['applied_controls']}`",
        f"- Route report digest: `{bundle['sparta_route']['route_report_digest']}`",
        "",
        "## 5. Decision Lifecycle Ledger",
        "",
        f"- Ledger ID: `{ledger['decision_id']}`",
        f"- Record count: `{ledger['record_count']}`",
        f"- Head hash: `{ledger['head_record_hash']}`",
        f"- Verification valid: `{ledger['verification']['valid']}`",
        f"- Event counts: `{ledger['summary']['event_counts']}`",
        "",
        "## 6. DLL Intelligence",
        "",
        f"- Ledger count: `{intelligence['summary']['ledger_count']}`",
        f"- Near-miss count: `{intelligence['summary']['near_miss_count']}`",
        f"- Recovery failure count: `{intelligence['summary']['recovery_failure_count']}`",
        f"- Policy review queue items: `{len(intelligence['policy_review_queue'])}`",
        f"- Recommended next action: {intelligence['recommended_next_action']}",
        "",
        "## Integrated Flow",
        "",
    ]
    lines.extend(f"- {item}" for item in bundle["integrated_flow"])
    lines.extend(["", "## Boundary", ""])
    lines.extend(f"- {item}" for item in bundle["boundary"])
    lines.append("")
    return "\n".join(lines)


def write_outputs(
    bundle: Mapping[str, Any],
    *,
    json_output: Path,
    markdown_output: Path,
    pr_comment_output: Path,
    certificate_output: Path,
    route_output: Path,
    ledger_output: Path,
    intelligence_output: Path,
) -> None:
    for path in [
        json_output,
        markdown_output,
        pr_comment_output,
        certificate_output,
        route_output,
        ledger_output,
        intelligence_output,
    ]:
        path.parent.mkdir(parents=True, exist_ok=True)
    json_output.write_text(json.dumps(bundle, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    markdown_output.write_text(render_markdown(bundle), encoding="utf-8")
    pr_comment_output.write_text(bundle["pr_guardian"]["comment_markdown"], encoding="utf-8")
    certificate_output.write_text(
        json.dumps(bundle["pr_guardian"]["certificate"], indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    route_output.write_text(
        json.dumps(bundle["sparta_route"]["route_report"], indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    ledger_output.write_text(
        json.dumps(bundle["decision_lifecycle_ledger"], indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    intelligence_output.write_text(
        json.dumps(bundle["dll_intelligence"], indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate the end-to-end SMERC PR Guardian demo.")
    parser.add_argument("--action-file", type=Path)
    parser.add_argument("--tool-plan", type=Path)
    parser.add_argument("--json-output", type=Path, default=Path("reports/end_to_end_pr_guardian_demo.json"))
    parser.add_argument("--markdown-output", type=Path, default=Path("reports/End_To_End_PR_Guardian_Demo.md"))
    parser.add_argument("--pr-comment-output", type=Path, default=Path("reports/end_to_end_pr_guardian_comment.md"))
    parser.add_argument("--certificate-output", type=Path, default=Path("reports/end_to_end_pr_guardian_certificate.json"))
    parser.add_argument("--route-output", type=Path, default=Path("reports/end_to_end_pr_guardian_sparta_route.json"))
    parser.add_argument("--ledger-output", type=Path, default=Path("reports/end_to_end_pr_guardian_dll.json"))
    parser.add_argument("--intelligence-output", type=Path, default=Path("reports/end_to_end_pr_guardian_dll_intelligence.json"))
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()
    bundle = build_end_to_end_demo(
        action=_load_json(args.action_file) if args.action_file else None,
        tool_plan=_load_json(args.tool_plan) if args.tool_plan else None,
    )
    write_outputs(
        bundle,
        json_output=args.json_output,
        markdown_output=args.markdown_output,
        pr_comment_output=args.pr_comment_output,
        certificate_output=args.certificate_output,
        route_output=args.route_output,
        ledger_output=args.ledger_output,
        intelligence_output=args.intelligence_output,
    )
    print(json.dumps(bundle, indent=2 if args.pretty else None, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
