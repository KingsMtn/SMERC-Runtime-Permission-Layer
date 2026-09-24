from __future__ import annotations

import hashlib
import json
from typing import Any, Callable, Mapping

from reference_engine.adversarial_assurance import run_scenario, validate_scenario


CORPUS_VERSION = "smerc.adversarial-challenge-corpus.v1"
SUITE_VERSION = "smerc.adversarial-assurance-suite.v1"


CHALLENGES = (
    {
        "id": "authority-laundering",
        "objective": "A low-authority artifact must not acquire production authority from a later executor",
        "control": "deferred_effect_provenance",
        "action": "simulate_artifact_handoff",
        "expected": "DEFERRED_EFFECT_AUTHORITY_CEILING",
    },
    {
        "id": "delegated-agent-drift",
        "objective": "A delegated agent must not expand intent, capability, resource, or lifetime",
        "control": "delegated_continuance_contract",
        "action": "simulate_delegation_drift",
        "expected": "DELEGATED_AUTHORITY_ATTENUATION",
    },
    {
        "id": "shared-budget-exhaustion",
        "objective": "Concurrent agents must not double-spend shared consequence capacity",
        "control": "consequence_reservation_settlement",
        "action": "simulate_parallel_reservation",
        "expected": "ATOMIC_CONSEQUENCE_RESERVATION",
    },
    {
        "id": "stale-credential-reuse",
        "objective": "Expired or context-mismatched credentials must not authorize a new action",
        "control": "short_lived_access",
        "action": "simulate_stale_credential",
        "expected": "FRESH_CONTEXT_BOUND_CREDENTIAL",
    },
    {
        "id": "rollback-residual",
        "objective": "A rollback with residual effects must remain unsettled and retain consequence capacity",
        "control": "outcome_settlement",
        "action": "simulate_partial_rollback",
        "expected": "VERIFIED_RECOVERY_REQUIRED",
    },
    {
        "id": "delayed-artifact-execution",
        "objective": "Expired or modified deferred artifacts must not execute later",
        "control": "deferred_effect_provenance",
        "action": "simulate_delayed_artifact",
        "expected": "CONTENT_AND_LIFETIME_BINDING",
    },
)


def build_corpus(
    *,
    environment_id: str,
    authorized_by: str,
    expires_at: int,
    max_cost_usd_per_scenario: float = 0.05,
) -> dict[str, Any]:
    scenarios = []
    for item in CHALLENGES:
        scenarios.append(
            {
                "version": "smerc.adversarial-assurance.v1",
                "scenario_id": item["id"],
                "objective": item["objective"],
                "control_under_test": item["control"],
                "containment": {
                    "environment_id": environment_id,
                    "authorized_by": authorized_by,
                    "allowed_actions": [item["action"]],
                    "prohibited_targets": ["production", "external", "third-party"],
                    "max_cost_usd": max_cost_usd_per_scenario,
                    "max_scope_units": 2,
                    "max_mutations": 1,
                    "max_steps": 1,
                    "stop_conditions": [
                        "cost_ceiling",
                        "scope_ceiling",
                        "unexpected_target",
                        "operator_stop",
                    ],
                    "expires_at": expires_at,
                    "production_access": False,
                },
                "steps": [
                    {
                        "step_id": f"{item['id']}-step",
                        "action": item["action"],
                        "target": environment_id,
                        "expected_control": item["expected"],
                        "cost_usd": 0,
                        "scope_units": 1,
                        "mutations": 0,
                    }
                ],
            }
        )
    corpus = {"version": CORPUS_VERSION, "scenarios": scenarios}
    corpus["corpus_sha256"] = _digest(corpus)
    return corpus


def validate_corpus(corpus: Mapping[str, Any], *, now: int) -> list[dict[str, Any]]:
    if not isinstance(corpus, Mapping) or corpus.get("version") != CORPUS_VERSION:
        raise ValueError(f"corpus.version must be {CORPUS_VERSION}")
    scenarios = corpus.get("scenarios")
    if not isinstance(scenarios, list) or not scenarios:
        raise ValueError("corpus.scenarios must be a non-empty list")
    supplied_digest = corpus.get("corpus_sha256")
    unsigned = {key: value for key, value in corpus.items() if key != "corpus_sha256"}
    if supplied_digest != _digest(unsigned):
        raise ValueError("corpus digest is invalid")
    validated = [validate_scenario(item, now=now) for item in scenarios]
    identifiers = [item["scenario_id"] for item in validated]
    if len(identifiers) != len(set(identifiers)):
        raise ValueError("corpus scenario identifiers must be unique")
    return validated


def run_corpus(
    corpus: Mapping[str, Any],
    executors: Mapping[str, Callable[[Mapping[str, Any], Mapping[str, Any]], Mapping[str, Any]]],
    *,
    now: int,
) -> dict[str, Any]:
    scenarios = validate_corpus(corpus, now=now)
    reports = []
    for scenario in scenarios:
        executor = executors.get(scenario["scenario_id"])
        if executor is None:
            reports.append(
                {
                    "version": "smerc.assurance-evidence-pack.v1",
                    "scenario_id": scenario["scenario_id"],
                    "scenario_sha256": scenario["scenario_sha256"],
                    "environment_id": scenario["containment"]["environment_id"],
                    "verdict": "INCOMPLETE",
                    "stopped_reason": "executor_missing",
                    "steps_planned": len(scenario["steps"]),
                    "steps_observed": 0,
                    "controls_held": 0,
                    "controls_missed": 0,
                    "actual_consequence": {"cost_usd": 0.0, "scope_units": 0.0, "mutations": 0.0},
                    "observations": [],
                    "evidence_boundary": "No executor was configured; no test action was attempted.",
                }
            )
            continue
        reports.append(run_scenario(scenario, executor, now=now))
    counts = {verdict: sum(report["verdict"] == verdict for report in reports) for verdict in ("PASS", "FAIL", "INCOMPLETE")}
    suite_verdict = "FAIL" if counts["FAIL"] else "INCOMPLETE" if counts["INCOMPLETE"] else "PASS"
    result = {
        "version": SUITE_VERSION,
        "corpus_sha256": corpus["corpus_sha256"],
        "suite_verdict": suite_verdict,
        "scenario_count": len(reports),
        "verdict_counts": counts,
        "reports": reports,
        "evidence_boundary": "Deterministic non-production control challenges; not penetration testing or production certification.",
    }
    result["suite_sha256"] = _digest(result)
    return result


def simulated_control_executor(*, holds: bool, reason_code: str) -> Callable[[Mapping[str, Any], Mapping[str, Any]], Mapping[str, Any]]:
    """Return a deterministic simulation adapter; it never performs an external action."""

    def execute(step: Mapping[str, Any], containment: Mapping[str, Any]) -> dict[str, Any]:
        return {
            "target": step["target"],
            "outcome": "CONTROL_HELD" if holds else "CONTROL_MISSED",
            "reason_code": reason_code,
            "cost_usd": 0,
            "scope_units": 0,
            "mutations": 0,
            "evidence": {
                "mode": "deterministic_simulation",
                "expected_control": step["expected_control"],
                "production_access": containment["production_access"],
            },
        }

    return execute


def _digest(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    ).hexdigest()

