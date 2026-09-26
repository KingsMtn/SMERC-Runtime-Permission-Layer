from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from reference_engine.consequence_time_reconciliation import reconcile_consequence_time
from reference_engine.delegated_continuance_contract import ContinuanceContractSigner


VERSION = "smerc.authorization-afterlife-scenario-runner.v1"
EVIDENCE_CLASSES = {"PUBLIC_EXAMPLE", "CONTROLLED_AWS_PROOF", "SYNTHETIC", "CUSTOMER_METADATA"}


def _load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def _sha(value: Any) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def build_base_inputs(intent: str) -> dict[str, Any]:
    signer = ContinuanceContractSigner("scenario-key", b"scenario-proof-key-material-00001")
    root = signer.issue_root(
        tenant_id="review-tenant", originating_user_id="review-user", agent_id="coordinator",
        intent_digest=intent, capabilities=["aws:Read", "aws:MutateBounded"],
        resources=["aws:account-summary", "aws:ephemeral-security-group"], max_actions=4,
        max_scope_units=10, max_cost_usd=1, max_delegation_depth=2, issued_at=100,
        expires_at=500, checkpoint_every_actions=2,
        cleanup_obligations=["verify-no-residual-resource"],
    )
    child = signer.delegate(
        root, agent_id="aws-worker", capabilities=["aws:Read", "aws:MutateBounded"],
        resources=["aws:account-summary", "aws:ephemeral-security-group"], max_actions=3,
        max_scope_units=5, max_cost_usd=1, expires_at=450, checkpoint_every_actions=1,
        cleanup_obligations=["verify-no-residual-resource"],
    )
    grant = {
        "contract_id": "authority-aws-proof", "authority_epoch": 7,
        "authority_lineage": ["review-user", "coordinator"], "issued_at": 100,
        "valid_until": 500, "revalidation_triggers": ["policy_changed", "consent_withdrawn"],
        "checkpoint_digest": "aws-checkpoint-7",
        "settlement_requirements": ["outcome_verified", "cleanup_verified"],
        "descendant_contract_ids": ["aws-worker-contract"],
    }
    runtime = {
        "observed_at": 200, "current_authority_epoch": 7, "revoked_contract_ids": [],
        "trigger_events": [], "active_principals": ["review-user", "coordinator"],
        "invalidation_acknowledged_by": ["aws-worker-contract"],
        "checkpoint_digest": "aws-checkpoint-7",
        "satisfied_settlement_requirements": ["outcome_verified", "cleanup_verified"],
    }
    envelope = {
        "envelope_id": "aws-envelope-7", "authority_epoch": 7,
        "allowed_resource_kinds": ["credential", "service"],
        "allowed_capabilities": ["aws:Read", "aws:MutateBounded"],
        "allowed_effects": ["read", "create_ephemeral", "delete_ephemeral"],
        "allowed_providers": ["aws"], "max_delegation_depth": 1,
        "max_persistence_seconds": 900, "max_spend_minor": 100,
    }
    resource = {
        "resource_id": "aws-session-resource", "resource_kind": "credential", "provider": "aws",
        "capabilities": ["aws:Read"], "effects": ["read"], "delegation_depth": 0,
        "persistence_seconds": 300, "spend_minor": 0, "provenance_digest": "aws-proof-digest",
    }
    observation = {
        "current_authority_epoch": 7, "resolved_provenance_digest": "aws-proof-digest",
        "resolver_version": "sanitized-aws-proof-v1", "quarantined_before_evaluation": True,
    }
    return {
        "signer": signer, "delegated_contract": child, "authority_grant": grant,
        "authority_runtime": runtime, "acquired_envelope": envelope,
        "acquired_resource": resource, "acquired_observation": observation,
    }


def build_report(repo_root: str | Path) -> dict[str, Any]:
    root = Path(repo_root)
    read_only = _load(root / "examples" / "aws_mcp_supervised_live_proof.json")
    reversible = _load(root / "reports" / "aws_reversible_mutation_observation.json")
    intent = hashlib.sha256(b"aws-authorization-afterlife-review").hexdigest()
    base = build_base_inputs(intent)

    read_action = {
        "capability": "aws:Read", "resource": "aws:account-summary", "intent_digest": intent,
        "scope_units": 1, "cost_usd": 0, "external_side_effect": False,
        "checkpoint_present": True, "cleanup_plan_present": True,
    }
    normal = reconcile_consequence_time(
        **base, proposed_action=read_action,
        consumption={"actions": 0, "scope_units": 0, "cost_usd": 0}, now=200,
        partial_effects_present=False,
    )

    drift_runtime = dict(base["authority_runtime"])
    drift_runtime.update(current_authority_epoch=8, trigger_events=["policy_changed"])
    drift_observation = dict(base["acquired_observation"])
    drift_observation["current_authority_epoch"] = 8
    expanded = dict(base["acquired_resource"])
    expanded.update(
        capabilities=["aws:Read", "iam:AttachRolePolicy"],
        effects=["read", "change_authority"],
    )
    quarantined = reconcile_consequence_time(
        **{**base, "authority_runtime": drift_runtime, "acquired_observation": drift_observation,
           "acquired_resource": expanded}, proposed_action=read_action,
        consumption={"actions": 0, "scope_units": 0, "cost_usd": 0}, now=210,
        partial_effects_present=False,
    )

    mutation_action = {
        "capability": "aws:MutateBounded", "resource": "aws:ephemeral-security-group",
        "intent_digest": intent, "scope_units": 1, "cost_usd": 0,
        "external_side_effect": True, "checkpoint_present": True, "cleanup_plan_present": True,
    }
    revoked_runtime = dict(base["authority_runtime"])
    revoked_runtime["revoked_contract_ids"] = ["authority-aws-proof"]
    compensated = reconcile_consequence_time(
        **{**base, "authority_runtime": revoked_runtime}, proposed_action=mutation_action,
        consumption={"actions": 1, "scope_units": 1, "cost_usd": 0}, now=220,
        partial_effects_present=True,
    )

    scenarios = [
        {
            "scenario_id": "AWS_AFTERLIFE_READ_ONLY_SETTLE",
            "evidence_source": "CONTROLLED_AWS_PROOF",
            "source_path": "examples/aws_mcp_supervised_live_proof.json",
            "source_sha256": _sha(read_only),
            "source_boundary": read_only.get("boundary", {}),
            "synthetic_extension": "Current authority and settlement metadata are modeled.",
            "result": normal,
        },
        {
            "scenario_id": "AWS_AFTERLIFE_EPOCH_DRIFT_QUARANTINE",
            "evidence_source": "SYNTHETIC",
            "source_path": "examples/aws_mcp_supervised_live_proof.json",
            "source_sha256": _sha(read_only),
            "source_boundary": read_only.get("boundary", {}),
            "synthetic_extension": "Policy epoch change and acquired IAM capability expansion are modeled; AWS did not observe them.",
            "result": quarantined,
        },
        {
            "scenario_id": "AWS_AFTERLIFE_PARTIAL_EFFECT_COMPENSATE",
            "evidence_source": "CONTROLLED_AWS_PROOF",
            "source_path": "reports/aws_reversible_mutation_observation.json",
            "source_sha256": _sha(reversible),
            "source_boundary": reversible.get("boundary", {}),
            "synthetic_extension": "Revocation timing is modeled; creation, deletion, latency, residual count, and cost come from the controlled proof.",
            "observed_recovery": {
                "resource_created": reversible.get("resource_created"),
                "resource_deleted": reversible.get("resource_deleted"),
                "rollback_latency_seconds": reversible.get("rollback_latency_seconds"),
                "residual_count": reversible.get("residual_count"),
                "estimated_incremental_cost_usd": reversible.get("estimated_incremental_cost_usd"),
            },
            "result": compensated,
        },
    ]
    if any(item["evidence_source"] not in EVIDENCE_CLASSES for item in scenarios):
        raise ValueError("unknown evidence source classification")
    return {
        "version": VERSION,
        "title": "AWS Authorization-Afterlife Scenario Report",
        "data_boundary": (
            "Sanitized repository evidence and synthetic authority metadata only. No credentials, "
            "account IDs, ARNs, raw AWS responses, customer records, or live execution are used."
        ),
        "scenario_count": len(scenarios),
        "decision_counts": {
            decision: sum(item["result"]["decision"] == decision for item in scenarios)
            for decision in ("SETTLE", "QUARANTINE", "COMPENSATE")
        },
        "scenarios": scenarios,
        "claim_boundary": (
            "This report demonstrates deterministic reconciliation over labeled evidence. It is not "
            "customer validation, AWS attestation, production enforcement, or proof that all execution paths are mediated."
        ),
    }


def render_markdown(report: dict[str, Any]) -> str:
    lines = [f"# {report['title']}", "", report["data_boundary"], "", "## Outcomes", ""]
    for scenario in report["scenarios"]:
        result = scenario["result"]
        lines.extend([
            f"### {scenario['scenario_id']}", "",
            f"- Evidence source: `{scenario['evidence_source']}`",
            f"- Source: `{scenario['source_path']}`",
            f"- Decision: `{result['decision']}`",
            f"- Should commit: `{str(result['should_commit']).lower()}`",
            f"- Synthetic extension: {scenario['synthetic_extension']}",
            f"- Reasons: {', '.join(result['reasons']) or 'none'}", "",
        ])
    lines.extend(["## Claim Boundary", "", report["claim_boundary"], ""])
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run labeled AWS authorization-afterlife scenarios")
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--output-dir", default="reports/aws_authorization_afterlife")
    args = parser.parse_args()
    report = build_report(args.repo_root)
    output = Path(args.output_dir)
    output.mkdir(parents=True, exist_ok=True)
    (output / "aws_authorization_afterlife.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )
    (output / "AWS_Authorization_Afterlife.md").write_text(render_markdown(report), encoding="utf-8")
    print(json.dumps({"output_dir": str(output), "decision_counts": report["decision_counts"]}, indent=2))


if __name__ == "__main__":
    main()
