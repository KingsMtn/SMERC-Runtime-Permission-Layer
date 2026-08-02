from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Mapping

from smerc_sdk import SMERCAPIError, SMERCClient


SMOKE_TEST_VERSION = "smerc.api-smoke-test.v1"


def load_json(path: str | Path) -> Dict[str, Any]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise TypeError(f"{path} must contain a JSON object")
    return payload


def run_api_smoke_test(
    *,
    base_url: str,
    token: str,
    action: Mapping[str, Any],
    latency_slo_ms: int = 500,
    timeout: float = 10.0,
) -> Dict[str, Any]:
    client = SMERCClient(base_url, token=token, timeout=timeout)
    checks: list[Dict[str, Any]] = []
    artifacts: Dict[str, Any] = {}

    health = _capture(checks, "health", lambda: client.health())
    if health is not None:
        artifacts["health"] = health
        _expect(checks, "health_status_ok", health.get("status") == "ok", "Runtime liveness endpoint returned ok.")

    ready = _capture(checks, "ready", lambda: client.ready())
    if ready is not None:
        artifacts["ready"] = ready
        _expect(checks, "ready_status_ready", ready.get("status") == "ready", "Persistence readiness endpoint returned ready.")

    schema = _capture(checks, "schema", lambda: client.schema())
    if schema is not None:
        artifacts["schema"] = {
            "api_version": schema.get("api_version"),
            "operator_status_version": schema.get("language_versions", {}).get("operator_status"),
            "has_operator_status_endpoint": "GET /v1/operator/status" in schema.get("endpoints", {}),
        }
        _expect(
            checks,
            "operator_status_discoverable",
            artifacts["schema"]["has_operator_status_endpoint"],
            "Schema advertises GET /v1/operator/status.",
        )

    decision = _capture(checks, "evaluate", lambda: client.evaluate(action))
    if decision is not None:
        artifacts["decision"] = {
            "replay_id": decision.get("replay_id"),
            "posture": decision.get("posture"),
            "runtime_observation": decision.get("runtime_observation"),
        }
        _expect(checks, "decision_has_replay_id", bool(decision.get("replay_id")), "Evaluation returned a replay ID.")
        _expect(
            checks,
            "decision_has_runtime_observation",
            isinstance(decision.get("runtime_observation"), dict),
            "Evaluation persisted a runtime observation.",
        )

    runtime_health = _capture(
        checks,
        "runtime_health_metrics",
        lambda: client.runtime_health_metrics(limit=25, latency_slo_ms=latency_slo_ms),
    )
    if runtime_health is not None:
        artifacts["runtime_health"] = runtime_health
        _expect(
            checks,
            "runtime_health_has_latency",
            runtime_health.get("latency", {}).get("p95_ms") is not None,
            "Runtime health reports p95 latency after a live evaluation.",
        )
        _expect(
            checks,
            "runtime_health_slo_met",
            runtime_health.get("latency", {}).get("slo_met") is True,
            f"Runtime health p95 latency meets the configured {latency_slo_ms} ms SLO.",
        )

    operator_status = _capture(
        checks,
        "operator_status",
        lambda: client.operator_status(limit=25, latency_slo_ms=latency_slo_ms),
    )
    if operator_status is not None:
        artifacts["operator_status"] = operator_status
        _expect(
            checks,
            "operator_status_has_runtime_health",
            operator_status.get("runtime_health", {}).get("present") is True,
            "Operator status includes runtime health.",
        )
        _expect(
            checks,
            "operator_status_not_blocked",
            operator_status.get("operator_status") != "blocked",
            "Operator status is not blocked for this smoke test.",
        )

    passed = all(check["status"] == "pass" for check in checks)
    return {
        "schema": SMOKE_TEST_VERSION,
        "generated_at": _now(),
        "base_url": base_url.rstrip("/"),
        "passed": passed,
        "check_count": len(checks),
        "failed_checks": [check["name"] for check in checks if check["status"] == "fail"],
        "checks": checks,
        "artifacts": artifacts,
        "evidence_boundary": (
            "This smoke test proves that the selected SMERC API responded to basic pilot-readiness calls. "
            "It does not prove production availability, security certification, incident reduction, customer "
            "calibration, or enforcement safety."
        ),
    }


def render_markdown(report: Mapping[str, Any]) -> str:
    lines = [
        "# SMERC API Smoke Test Report",
        "",
        f"Generated: `{report['generated_at']}`",
        "",
        "## Summary",
        "",
        f"- Base URL: `{report['base_url']}`",
        f"- Passed: `{str(report['passed']).lower()}`",
        f"- Checks: `{report['check_count']}`",
        f"- Failed checks: `{report['failed_checks']}`",
        "",
        "## Checks",
        "",
        "| Check | Status | Detail |",
        "| --- | --- | --- |",
    ]
    for check in report["checks"]:
        lines.append(f"| `{check['name']}` | `{check['status']}` | {check['detail']} |")
    lines.extend(["", "## Evidence Boundary", "", str(report["evidence_boundary"]), ""])
    return "\n".join(lines)


def write_outputs(report: Mapping[str, Any], *, json_path: str | Path, markdown_path: str | Path) -> None:
    Path(json_path).parent.mkdir(parents=True, exist_ok=True)
    Path(json_path).write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    Path(markdown_path).parent.mkdir(parents=True, exist_ok=True)
    Path(markdown_path).write_text(render_markdown(report), encoding="utf-8")


def _capture(checks: list[Dict[str, Any]], name: str, call: Any) -> Dict[str, Any] | None:
    try:
        result = call()
    except (ConnectionError, SMERCAPIError, ValueError, TimeoutError) as exc:
        checks.append({"name": name, "status": "fail", "detail": str(exc)})
        return None
    checks.append({"name": name, "status": "pass", "detail": "Endpoint returned a structured response."})
    return result


def _expect(checks: list[Dict[str, Any]], name: str, condition: bool, detail: str) -> None:
    checks.append({"name": name, "status": "pass" if condition else "fail", "detail": detail})


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def main() -> int:
    parser = argparse.ArgumentParser(description="Run a SMERC Runtime API smoke test.")
    parser.add_argument("--base-url", required=True, help="SMERC API base URL, for example http://127.0.0.1:8000")
    parser.add_argument("--token", required=True, help="Bearer token or pilot API key.")
    parser.add_argument("--action", default="examples/recoverability_single_action.json")
    parser.add_argument("--latency-slo-ms", type=int, default=500)
    parser.add_argument("--timeout", type=float, default=10.0)
    parser.add_argument("--json-output", default="reports/api_smoke_test.json")
    parser.add_argument("--markdown-output", default="reports/API_Smoke_Test_Report.md")
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()

    report = run_api_smoke_test(
        base_url=args.base_url,
        token=args.token,
        action=load_json(args.action),
        latency_slo_ms=args.latency_slo_ms,
        timeout=args.timeout,
    )
    write_outputs(report, json_path=args.json_output, markdown_path=args.markdown_output)
    print(json.dumps(report, indent=2 if args.pretty else None, sort_keys=True))
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
