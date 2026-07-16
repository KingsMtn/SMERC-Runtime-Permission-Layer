from __future__ import annotations

import argparse
import copy
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Dict, List

from reference_engine.model_fitness import ModelFitnessEngine
from reference_engine.recoverability_engine import RecoverabilityEngine


@dataclass(frozen=True)
class InvariantResult:
    invariant_id: str
    engine: str
    description: str
    passed: bool
    before: Any
    after: Any
    expectation: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "invariant_id": self.invariant_id,
            "engine": self.engine,
            "description": self.description,
            "passed": self.passed,
            "before": self.before,
            "after": self.after,
            "expectation": self.expectation,
        }


RECOVERABILITY_BASE_ACTION: Dict[str, Any] = {
    "action_id": "INVARIANT_BASE_ACTION",
    "description": "AI agent proposes a production configuration change",
    "actor": "ai_deployment_agent",
    "tool": "github_actions",
    "action_type": "deployment_change",
    "base_action_risk": 0.58,
    "reversibility": 0.45,
    "containment_strength": 0.56,
    "rollback_latency": 0.48,
    "evidence_validity": 0.64,
    "anomaly_pressure": 0.36,
    "impact_scope": 0.58,
    "cancel_reliability": 0.57,
    "authorization_confidence": 0.62,
    "external_side_effect": False,
    "sensitive_data": False,
    "context": {"domain_profile": "github_actions"},
}


MODEL_FITNESS_BASE_REQUEST: Dict[str, Any] = {
    "task_id": "INVARIANT_EXECUTOR_SELECTION",
    "description": "Route a production deployment review to a qualified executor",
    "task_type": "cloud_administration",
    "required_capabilities": ["deployment_analysis", "infrastructure_context", "rollback_planning"],
    "risk_level": 0.66,
    "reversibility": 0.48,
    "evidence_validity": 0.68,
    "data_sensitivity": "confidential",
    "required_tool_authority": "execute_external",
    "latency_requirement": "medium",
    "cost_sensitivity": "low",
    "impact_scope": 0.64,
    "anomaly_pressure": 0.30,
    "candidates": [
        {
            "executor_id": "deployment_guardian",
            "display_name": "Deployment Guardian Agent",
            "provider": "internal_agent",
            "capabilities": ["deployment_analysis", "infrastructure_context", "rollback_planning"],
            "allowed_data_classes": ["public", "internal", "confidential"],
            "max_tool_authority": "execute_external",
            "cost_tier": "medium",
            "latency_tier": "medium",
            "reliability_score": 0.82,
            "domain_fit": 0.88,
            "safety_history": 0.78,
            "tool_reliability": 0.80,
            "data_boundary_score": 0.88,
        }
    ],
}


def evaluate_invariants() -> Dict[str, Any]:
    results = recoverability_invariants() + model_fitness_invariants()
    passed = sum(1 for result in results if result.passed)
    failed = len(results) - passed
    return {
        "summary": {
            "total": len(results),
            "passed": passed,
            "failed": failed,
            "status": "PASS" if failed == 0 else "FAIL",
            "claim_boundary": (
                "These invariants test declared score behavior and fail-closed routing properties. "
                "They do not prove production incident reduction or customer-calibrated thresholds."
            ),
        },
        "results": [result.to_dict() for result in results],
    }


def recoverability_invariants() -> List[InvariantResult]:
    engine = RecoverabilityEngine()
    return [
        _score_monotonic(
            invariant_id="RECOVERY_REVERSIBILITY_MONOTONIC",
            engine_name="recoverability",
            description="Higher reversibility must not increase irreversible exposure and must not reduce reversible capacity or authorization score.",
            base=RECOVERABILITY_BASE_ACTION,
            mutate=lambda item: _set(item, "reversibility", 0.80),
            evaluate=lambda item: engine.evaluate(item)["scores"],
            expectations=[
                ("irreversible_exposure_score", "<="),
                ("reversible_capacity_score", ">="),
                ("risk_adjusted_authorization_score", ">="),
            ],
        ),
        _score_monotonic(
            invariant_id="RECOVERY_ROLLBACK_LATENCY_MONOTONIC",
            engine_name="recoverability",
            description="Higher rollback latency must not reduce exposure or stress and must not increase recovery capacity or authorization score.",
            base=RECOVERABILITY_BASE_ACTION,
            mutate=lambda item: _set(item, "rollback_latency", 0.86),
            evaluate=lambda item: engine.evaluate(item)["scores"],
            expectations=[
                ("irreversible_exposure_score", ">="),
                ("operational_stress_score", ">="),
                ("reversible_capacity_score", "<="),
                ("risk_adjusted_authorization_score", "<="),
            ],
        ),
        _score_monotonic(
            invariant_id="RECOVERY_EVIDENCE_VALIDITY_MONOTONIC",
            engine_name="recoverability",
            description="Lower evidence validity must not increase confidence or authorization and must not reduce operational stress.",
            base=RECOVERABILITY_BASE_ACTION,
            mutate=lambda item: _set(item, "evidence_validity", 0.22),
            evaluate=lambda item: engine.evaluate(item)["scores"],
            expectations=[
                ("confidence_score", "<="),
                ("risk_adjusted_authorization_score", "<="),
                ("operational_stress_score", ">="),
            ],
        ),
        _score_monotonic(
            invariant_id="RECOVERY_ANOMALY_PRESSURE_MONOTONIC",
            engine_name="recoverability",
            description="Higher anomaly pressure must not increase confidence and must not reduce operational stress.",
            base=RECOVERABILITY_BASE_ACTION,
            mutate=lambda item: _set(item, "anomaly_pressure", 0.88),
            evaluate=lambda item: engine.evaluate(item)["scores"],
            expectations=[
                ("confidence_score", "<="),
                ("operational_stress_score", ">="),
            ],
        ),
        _score_monotonic(
            invariant_id="RECOVERY_EXTERNAL_AND_SENSITIVE_RISK",
            engine_name="recoverability",
            description="External side effects and sensitive data must not reduce irreversible exposure.",
            base=RECOVERABILITY_BASE_ACTION,
            mutate=lambda item: _set_many(item, {"external_side_effect": True, "sensitive_data": True}),
            evaluate=lambda item: engine.evaluate(item)["scores"],
            expectations=[
                ("irreversible_exposure_score", ">="),
            ],
        ),
    ]


def model_fitness_invariants() -> List[InvariantResult]:
    engine = ModelFitnessEngine()
    return [
        _candidate_blocking(
            invariant_id="FITNESS_DATA_BOUNDARY_FAIL_CLOSED",
            description="A data-boundary violation must block an executor even when capability and reliability scores are strong.",
            base=MODEL_FITNESS_BASE_REQUEST,
            mutate_candidate=lambda candidate: _set_many(
                candidate,
                {
                    "allowed_data_classes": ["public", "internal"],
                    "reliability_score": 1.0,
                    "domain_fit": 1.0,
                    "safety_history": 1.0,
                    "tool_reliability": 1.0,
                },
            ),
            expected_reason="DATA_BOUNDARY_EXCEEDED",
            engine=engine,
        ),
        _candidate_blocking(
            invariant_id="FITNESS_TOOL_AUTHORITY_FAIL_CLOSED",
            description="A tool-authority gap must block an executor even when general capability scores are strong.",
            base=MODEL_FITNESS_BASE_REQUEST,
            mutate_candidate=lambda candidate: _set_many(
                candidate,
                {
                    "max_tool_authority": "read_only",
                    "reliability_score": 1.0,
                    "domain_fit": 1.0,
                    "safety_history": 1.0,
                    "tool_reliability": 1.0,
                },
            ),
            expected_reason="INSUFFICIENT_TOOL_AUTHORITY",
            engine=engine,
        ),
        _candidate_blocking(
            invariant_id="FITNESS_CAPABILITY_GAP_FAIL_CLOSED",
            description="A required-capability gap must block an executor despite low cost and latency.",
            base=MODEL_FITNESS_BASE_REQUEST,
            mutate_candidate=lambda candidate: _set_many(
                candidate,
                {
                    "capabilities": ["summarization"],
                    "cost_tier": "low",
                    "latency_tier": "low",
                },
            ),
            expected_reason="REQUIRED_CAPABILITY_GAP",
            engine=engine,
        ),
        _score_monotonic(
            invariant_id="FITNESS_RISK_PRESSURE_REDUCES_ADJUSTED_SCORE",
            engine_name="model_fitness",
            description="Higher task risk must not increase the risk-adjusted executor score for the same candidate set.",
            base=MODEL_FITNESS_BASE_REQUEST,
            mutate=lambda item: _set(item, "risk_level", 0.92),
            evaluate=lambda item: engine.evaluate(item)["candidate_rankings"][0]["scores"],
            expectations=[
                ("risk_pressure", ">="),
                ("risk_adjusted_executor_score", "<="),
            ],
        ),
        _score_monotonic(
            invariant_id="FITNESS_SAFETY_HISTORY_IMPROVES_FIT",
            engine_name="model_fitness",
            description="Higher safety history must not reduce reliability, recoverability, or model fitness for an otherwise identical qualified executor.",
            base=_with_candidate_value(MODEL_FITNESS_BASE_REQUEST, "safety_history", 0.40),
            mutate=lambda item: _set(item["candidates"][0], "safety_history", 0.90),
            evaluate=lambda item: engine.evaluate(item)["candidate_rankings"][0]["scores"],
            expectations=[
                ("recoverability_fit", ">="),
                ("reliability_fit", ">="),
                ("model_fitness_score", ">="),
            ],
        ),
    ]


def _score_monotonic(
    invariant_id: str,
    engine_name: str,
    description: str,
    base: Dict[str, Any],
    mutate: Callable[[Dict[str, Any]], None],
    evaluate: Callable[[Dict[str, Any]], Dict[str, float]],
    expectations: List[tuple[str, str]],
) -> InvariantResult:
    before_input = copy.deepcopy(base)
    after_input = copy.deepcopy(base)
    mutate(after_input)
    before_scores = evaluate(before_input)
    after_scores = evaluate(after_input)
    comparisons = []
    passed = True
    for key, operator in expectations:
        before = before_scores[key]
        after = after_scores[key]
        ok = after >= before if operator == ">=" else after <= before
        comparisons.append({"score": key, "before": before, "after": after, "expectation": operator, "passed": ok})
        passed = passed and ok
    return InvariantResult(
        invariant_id=invariant_id,
        engine=engine_name,
        description=description,
        passed=passed,
        before={item["score"]: item["before"] for item in comparisons},
        after={item["score"]: item["after"] for item in comparisons},
        expectation="; ".join(f"{item['score']} {item['expectation']} prior value" for item in comparisons),
    )


def _candidate_blocking(
    invariant_id: str,
    description: str,
    base: Dict[str, Any],
    mutate_candidate: Callable[[Dict[str, Any]], None],
    expected_reason: str,
    engine: ModelFitnessEngine,
) -> InvariantResult:
    request = copy.deepcopy(base)
    mutate_candidate(request["candidates"][0])
    result = engine.evaluate(request)
    candidate = result["candidate_rankings"][0]
    blocked = request["candidates"][0]["executor_id"] in result["blocked_executors"]
    reason_present = expected_reason in candidate["blocking_reasons"]
    return InvariantResult(
        invariant_id=invariant_id,
        engine="model_fitness",
        description=description,
        passed=blocked and reason_present,
        before={"executor_id": candidate["executor_id"]},
        after={"blocked_executors": result["blocked_executors"], "blocking_reasons": candidate["blocking_reasons"]},
        expectation=f"candidate is blocked with {expected_reason}",
    )


def write_markdown_report(result: Dict[str, Any], path: Path) -> None:
    lines = [
        "# SMERC Scoring Invariants Report",
        "",
        "This report verifies declared score behavior for the recoverability and Model/Agent Fitness engines.",
        "",
        "It does not prove production incident reduction, customer-calibrated thresholds, or financial-risk prediction.",
        "",
        f"- Total invariants: {result['summary']['total']}",
        f"- Passed: {result['summary']['passed']}",
        f"- Failed: {result['summary']['failed']}",
        f"- Status: {result['summary']['status']}",
        "",
        "## Results",
        "",
    ]
    for item in result["results"]:
        marker = "PASS" if item["passed"] else "FAIL"
        lines.extend(
            [
                f"### {item['invariant_id']} - {marker}",
                "",
                f"- Engine: `{item['engine']}`",
                f"- Description: {item['description']}",
                f"- Expectation: {item['expectation']}",
                f"- Before: `{json.dumps(item['before'], sort_keys=True)}`",
                f"- After: `{json.dumps(item['after'], sort_keys=True)}`",
                "",
            ]
        )
    path.write_text("\n".join(lines), encoding="utf-8")


def _set(payload: Dict[str, Any], key: str, value: Any) -> None:
    payload[key] = value


def _set_many(payload: Dict[str, Any], values: Dict[str, Any]) -> None:
    payload.update(values)


def _with_candidate_value(payload: Dict[str, Any], key: str, value: Any) -> Dict[str, Any]:
    cloned = copy.deepcopy(payload)
    cloned["candidates"][0][key] = value
    return cloned


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate declared SMERC scoring invariants.")
    parser.add_argument("--json-output", type=Path, help="Optional path for JSON report")
    parser.add_argument("--markdown-output", type=Path, help="Optional path for Markdown report")
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON to stdout")
    args = parser.parse_args()

    result = evaluate_invariants()
    if args.json_output:
        args.json_output.parent.mkdir(parents=True, exist_ok=True)
        args.json_output.write_text(json.dumps(result, indent=2), encoding="utf-8")
    if args.markdown_output:
        args.markdown_output.parent.mkdir(parents=True, exist_ok=True)
        write_markdown_report(result, args.markdown_output)
    print(json.dumps(result, indent=2 if args.pretty else None))


if __name__ == "__main__":
    main()
