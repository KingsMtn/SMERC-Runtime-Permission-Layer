from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, Mapping, Optional

from reference_engine.operator_status import load_json


RUNTIME_HEALTH_VERSION = "smerc.runtime-health-metrics.v1"
OBSERVATIONS_VERSION = "smerc.runtime-health-observations.v1"
POSTURES = ("ALLOW", "THROTTLE", "FREEZE", "DENY", "ESCALATE", "UNAVAILABLE")
INTEGRATION_STATUSES = {"ok", "unavailable", "timeout", "error", "fail_closed"}


def build_runtime_health_metrics(
    *,
    decision_artifacts: Mapping[str, Any],
    observations: Optional[Mapping[str, Any]] = None,
    tenant_id: str = "pilot-review",
    latency_slo_ms: int = 250,
    unavailable_rate_warning: float = 0.01,
    unavailable_rate_blocker: float = 0.05,
) -> Dict[str, Any]:
    records = _decision_records(decision_artifacts)
    observation_records = _observation_records(observations or {})
    posture_counts = Counter(_posture(record) for record in records)
    status_counts = Counter(item["integration_status"] for item in observation_records)
    latencies = [item["evaluation_latency_ms"] for item in observation_records if item.get("evaluation_latency_ms") is not None]
    decision_count = len(records)
    observed_count = len(observation_records)
    unavailable_count = posture_counts.get("UNAVAILABLE", 0) + sum(
        status_counts.get(status, 0) for status in ("unavailable", "timeout", "error")
    )
    fail_closed_count = status_counts.get("fail_closed", 0)
    unavailable_rate = None if max(decision_count, observed_count) == 0 else round(unavailable_count / max(decision_count, observed_count), 4)
    p95 = _percentile(latencies, 95)
    health_status = _health_status(
        unavailable_rate=unavailable_rate,
        unavailable_rate_warning=unavailable_rate_warning,
        unavailable_rate_blocker=unavailable_rate_blocker,
        p95=p95,
        latency_slo_ms=latency_slo_ms,
        observed_count=observed_count,
    )
    return {
        "schema": RUNTIME_HEALTH_VERSION,
        "generated_at": _now(),
        "tenant_id": tenant_id,
        "health_status": health_status,
        "decision_volume": {
            "decision_count": decision_count,
            "observed_evaluation_count": observed_count,
            "posture_counts": {posture: posture_counts.get(posture, 0) for posture in POSTURES},
        },
        "latency": {
            "slo_ms": latency_slo_ms,
            "sample_count": len(latencies),
            "minimum_ms": min(latencies) if latencies else None,
            "average_ms": round(sum(latencies) / len(latencies), 2) if latencies else None,
            "p50_ms": _percentile(latencies, 50),
            "p95_ms": p95,
            "p99_ms": _percentile(latencies, 99),
            "maximum_ms": max(latencies) if latencies else None,
            "slo_met": None if p95 is None else p95 <= latency_slo_ms,
        },
        "resilience": {
            "integration_status_counts": dict(sorted(status_counts.items())),
            "unavailable_count": unavailable_count,
            "unavailable_rate": unavailable_rate,
            "fail_closed_count": fail_closed_count,
            "fail_closed_rate": None if observed_count == 0 else round(fail_closed_count / observed_count, 4),
        },
        "operational_checks": _checks(
            observed_count=observed_count,
            p95=p95,
            latency_slo_ms=latency_slo_ms,
            unavailable_rate=unavailable_rate,
            unavailable_rate_warning=unavailable_rate_warning,
            unavailable_rate_blocker=unavailable_rate_blocker,
            observations=observations,
        ),
        "evidence_boundary": (
            "Runtime health metrics summarize supplied decision artifacts and observation records. Reference/local "
            "observations do not prove customer production latency, availability, incident reduction, or SLA compliance."
        ),
    }


def observations_from_decisions(decision_artifacts: Mapping[str, Any]) -> Dict[str, Any]:
    records: list[Dict[str, Any]] = []
    for record in _decision_records(decision_artifacts):
        observation = _runtime_observation(record)
        if observation is not None:
            records.append(observation)
    return {
        "schema": OBSERVATIONS_VERSION,
        "evidence_status": "api_observed_runtime" if records else "",
        "records": records,
    }


def render_markdown(report: Mapping[str, Any]) -> str:
    volume = report["decision_volume"]
    latency = report["latency"]
    resilience = report["resilience"]
    lines = [
        "# SMERC Runtime Health Metrics",
        "",
        f"Generated: `{report['generated_at']}`",
        "",
        "## Status",
        "",
        f"- Tenant: `{report['tenant_id']}`",
        f"- Health status: `{report['health_status']}`",
        "",
        "## Decision Volume",
        "",
        f"- Decisions: `{volume['decision_count']}`",
        f"- Observed evaluations: `{volume['observed_evaluation_count']}`",
        f"- Posture counts: `{volume['posture_counts']}`",
        "",
        "## Latency",
        "",
        f"- SLO: `{latency['slo_ms']} ms p95`",
        f"- Sample count: `{latency['sample_count']}`",
        f"- Average: `{latency['average_ms']}` ms",
        f"- p50: `{latency['p50_ms']}` ms",
        f"- p95: `{latency['p95_ms']}` ms",
        f"- p99: `{latency['p99_ms']}` ms",
        f"- Maximum: `{latency['maximum_ms']}` ms",
        f"- SLO met: `{latency['slo_met']}`",
        "",
        "## Resilience",
        "",
        f"- Integration status counts: `{resilience['integration_status_counts']}`",
        f"- Unavailable count: `{resilience['unavailable_count']}`",
        f"- Unavailable rate: `{resilience['unavailable_rate']}`",
        f"- Fail-closed count: `{resilience['fail_closed_count']}`",
        f"- Fail-closed rate: `{resilience['fail_closed_rate']}`",
        "",
        "## Operational Checks",
        "",
        "| Check | Status | Detail |",
        "| --- | --- | --- |",
    ]
    for check in report["operational_checks"]:
        lines.append(f"| `{check['name']}` | `{check['status']}` | {check['detail']} |")
    lines.extend(["", "## Evidence Boundary", "", str(report["evidence_boundary"]), ""])
    return "\n".join(lines)


def write_outputs(report: Mapping[str, Any], *, json_path: str | Path, markdown_path: str | Path) -> None:
    Path(json_path).parent.mkdir(parents=True, exist_ok=True)
    Path(json_path).write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    Path(markdown_path).parent.mkdir(parents=True, exist_ok=True)
    Path(markdown_path).write_text(render_markdown(report), encoding="utf-8")


def _decision_records(payload: Mapping[str, Any]) -> list[Mapping[str, Any]]:
    records = payload.get("records")
    if isinstance(records, list):
        return [item for item in records if isinstance(item, Mapping)]
    reports = payload.get("reports")
    if isinstance(reports, list):
        return [item for item in reports if isinstance(item, Mapping)]
    return []


def _observation_records(payload: Mapping[str, Any]) -> list[Dict[str, Any]]:
    if not payload:
        return []
    if payload.get("schema") != OBSERVATIONS_VERSION:
        raise ValueError(f"observations.schema must be {OBSERVATIONS_VERSION}")
    records = payload.get("records")
    if not isinstance(records, list):
        raise TypeError("observations.records must be a list")
    return [_normalize_observation(item, index) for index, item in enumerate(records)]


def _runtime_observation(record: Mapping[str, Any]) -> Optional[Dict[str, Any]]:
    candidates = [record.get("runtime_observation")]
    decision = record.get("decision")
    if isinstance(decision, Mapping):
        candidates.append(decision.get("runtime_observation"))
    for candidate in candidates:
        if isinstance(candidate, Mapping):
            item = dict(candidate)
            item.setdefault("replay_id", str(record.get("replay_id", "")))
            return item
    return None


def _normalize_observation(item: Any, index: int) -> Dict[str, Any]:
    if not isinstance(item, Mapping):
        raise TypeError(f"observation {index} must be an object")
    status = item.get("integration_status")
    if status not in INTEGRATION_STATUSES:
        raise ValueError(f"observation {index}.integration_status must be supported")
    latency = item.get("evaluation_latency_ms")
    if latency is not None:
        if isinstance(latency, bool) or not isinstance(latency, (int, float)) or latency < 0:
            raise ValueError(f"observation {index}.evaluation_latency_ms must be a non-negative number")
        latency = round(float(latency), 3)
    return {
        "replay_id": str(item.get("replay_id", "")),
        "integration_status": status,
        "evaluation_latency_ms": latency,
        "fail_behavior": str(item.get("fail_behavior", "")),
    }


def _posture(record: Mapping[str, Any]) -> str:
    decision = record.get("decision")
    posture = decision.get("posture") if isinstance(decision, Mapping) else record.get("posture")
    return posture if posture in POSTURES else "UNAVAILABLE"


def _percentile(values: Iterable[float], percentile: int) -> Optional[float]:
    ordered = sorted(float(value) for value in values)
    if not ordered:
        return None
    if len(ordered) == 1:
        return round(ordered[0], 3)
    rank = (len(ordered) - 1) * (percentile / 100)
    lower = int(rank)
    upper = min(lower + 1, len(ordered) - 1)
    fraction = rank - lower
    return round(ordered[lower] + (ordered[upper] - ordered[lower]) * fraction, 3)


def _health_status(
    *,
    unavailable_rate: Optional[float],
    unavailable_rate_warning: float,
    unavailable_rate_blocker: float,
    p95: Optional[float],
    latency_slo_ms: int,
    observed_count: int,
) -> str:
    if observed_count == 0:
        return "needs_observations"
    if unavailable_rate is not None and unavailable_rate >= unavailable_rate_blocker:
        return "blocked"
    if p95 is not None and p95 > latency_slo_ms:
        return "degraded"
    if unavailable_rate is not None and unavailable_rate >= unavailable_rate_warning:
        return "degraded"
    return "healthy"


def _checks(
    *,
    observed_count: int,
    p95: Optional[float],
    latency_slo_ms: int,
    unavailable_rate: Optional[float],
    unavailable_rate_warning: float,
    unavailable_rate_blocker: float,
    observations: Optional[Mapping[str, Any]],
) -> list[Dict[str, str]]:
    evidence_status = observations.get("evidence_status") if isinstance(observations, Mapping) else None
    return [
        {
            "name": "observations_present",
            "status": "ready" if observed_count else "warning",
            "detail": "Runtime health requires evaluation observations; without them, latency and availability are unknown.",
        },
        {
            "name": "latency_p95",
            "status": "ready" if p95 is not None and p95 <= latency_slo_ms else "warning",
            "detail": f"p95 evaluation latency should remain at or below {latency_slo_ms} ms for the selected workflow.",
        },
        {
            "name": "unavailable_rate",
            "status": _rate_status(unavailable_rate, unavailable_rate_warning, unavailable_rate_blocker),
            "detail": f"Unavailable rate warning threshold is {unavailable_rate_warning}; blocker threshold is {unavailable_rate_blocker}.",
        },
        {
            "name": "evidence_status_labeled",
            "status": "ready" if evidence_status else "warning",
            "detail": "Observation source must be labeled before using the report externally.",
        },
    ]


def _rate_status(value: Optional[float], warning: float, blocker: float) -> str:
    if value is None:
        return "warning"
    if value >= blocker:
        return "blocker"
    if value >= warning:
        return "warning"
    return "ready"


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate SMERC runtime health and latency metrics.")
    parser.add_argument("--decision-artifacts", default="reports/github_actions_shadow_mode_results.json")
    parser.add_argument("--observations", default="examples/runtime_health_observations.json")
    parser.add_argument("--tenant", default="pilot-review")
    parser.add_argument("--latency-slo-ms", type=int, default=250)
    parser.add_argument("--json-output", default="reports/runtime_health_metrics.json")
    parser.add_argument("--markdown-output", default="reports/Runtime_Health_Metrics.md")
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()

    observations = load_json(args.observations) if args.observations and Path(args.observations).exists() else None
    report = build_runtime_health_metrics(
        decision_artifacts=load_json(args.decision_artifacts),
        observations=observations,
        tenant_id=args.tenant,
        latency_slo_ms=args.latency_slo_ms,
    )
    write_outputs(report, json_path=args.json_output, markdown_path=args.markdown_output)
    print(json.dumps(report, indent=2 if args.pretty else None, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
