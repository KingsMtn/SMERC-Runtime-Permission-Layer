from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import time
from pathlib import Path
from typing import Any, Dict, Iterable, Optional
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit, urlunsplit
from urllib.request import HTTPRedirectHandler, Request, build_opener


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from reference_engine.agent_permission_layer import RuntimePermissionEngine  # noqa: E402


VALID_MODES = {"observe", "recommend", "enforce"}
VALID_POSTURES = {"ALLOW", "THROTTLE", "FREEZE", "DENY", "ESCALATE"}
TRANSIENT_HTTP_CODES = {429, 500, 502, 503, 504}
MAX_RESPONSE_BYTES = 1024 * 1024


class IntegrationError(Exception):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message


class SameOriginRedirectHandler(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):  # type: ignore[no-untyped-def]
        original = urlsplit(req.full_url)
        redirected = urlsplit(newurl)
        original_origin = (original.scheme.lower(), original.hostname, original.port)
        redirected_origin = (redirected.scheme.lower(), redirected.hostname, redirected.port)
        if redirected_origin != original_origin:
            raise HTTPError(newurl, code, "Cross-origin API redirect refused.", headers, fp)
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def _load_action(path: Path) -> Dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Action request file not found: {path}")
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise TypeError("GitHub Action integration expects one JSON action request object.")
    return payload


def _api_endpoint(api_url: str) -> str:
    parsed = urlsplit(api_url.strip())
    if not parsed.scheme or not parsed.hostname:
        raise IntegrationError("invalid_api_url", "SMERC API URL must include a scheme and hostname.")
    if parsed.username or parsed.password or parsed.query or parsed.fragment:
        raise IntegrationError("invalid_api_url", "SMERC API URL cannot contain credentials, query, or fragment.")
    try:
        parsed.port
    except ValueError as exc:
        raise IntegrationError("invalid_api_url", "SMERC API URL contains an invalid port.") from exc

    scheme = parsed.scheme.lower()
    loopback = parsed.hostname in {"localhost", "127.0.0.1", "::1"}
    if scheme != "https" and not (scheme == "http" and loopback):
        raise IntegrationError("insecure_api_url", "Remote SMERC API requires HTTPS outside loopback testing.")

    path = parsed.path.rstrip("/")
    if not path.endswith("/v1/evaluate"):
        path = f"{path}/v1/evaluate" if path else "/v1/evaluate"
    return urlunsplit((scheme, parsed.netloc, path, "", ""))


def _default_idempotency_key(payload: Dict[str, Any]) -> str:
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    digest = hashlib.sha256(canonical.encode("utf-8")).hexdigest()[:16]
    action_id = re.sub(r"[^A-Za-z0-9._-]+", "-", str(payload.get("action_id", "action"))).strip("-")
    parts = [
        os.environ.get("GITHUB_RUN_ID", "local"),
        os.environ.get("GITHUB_RUN_ATTEMPT", "1"),
        os.environ.get("GITHUB_JOB", "smerc"),
        action_id[:40] or "action",
        digest,
    ]
    return "-".join(parts)[:128]


def _validate_remote_decision(payload: Any) -> Dict[str, Any]:
    if not isinstance(payload, dict):
        raise IntegrationError("invalid_api_response", "SMERC API response must be a JSON object.")
    posture = payload.get("posture")
    if posture not in VALID_POSTURES:
        raise IntegrationError("invalid_api_response", "SMERC API response contains an invalid posture.")
    required = {
        "replay_id": str,
        "scores": dict,
        "reason_codes": list,
        "controls": list,
        "plain_english_summary": str,
    }
    for field, expected_type in required.items():
        if not isinstance(payload.get(field), expected_type):
            raise IntegrationError("invalid_api_response", f"SMERC API response is missing valid {field}.")
    if not payload["replay_id"] or not payload["plain_english_summary"]:
        raise IntegrationError("invalid_api_response", "SMERC API response contains an empty identifier or summary.")
    if not all(isinstance(item, str) for item in payload["reason_codes"] + payload["controls"]):
        raise IntegrationError("invalid_api_response", "SMERC API reasons and controls must be strings.")
    for field in ("irreversible_exposure_score", "confidence_score"):
        value = payload["scores"].get(field)
        if not isinstance(value, (int, float)) or isinstance(value, bool) or not 0 <= value <= 1:
            raise IntegrationError("invalid_api_response", f"SMERC API response contains an invalid {field}.")
    return payload


def _remote_evaluate(
    payload: Dict[str, Any],
    *,
    api_url: str,
    api_key: str,
    tenant: Optional[str],
    idempotency_key: str,
    timeout: float,
    max_retries: int,
) -> Dict[str, Any]:
    endpoint = _api_endpoint(api_url)
    body = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "Idempotency-Key": idempotency_key,
        "User-Agent": "SMERC-GitHub-Action/0.2",
    }
    if tenant:
        headers["X-SMERC-Tenant"] = tenant
    opener = build_opener(SameOriginRedirectHandler())

    for attempt in range(max_retries + 1):
        request = Request(endpoint, data=body, headers=headers, method="POST")
        try:
            with opener.open(request, timeout=timeout) as response:
                content_type = response.headers.get_content_type()
                if content_type != "application/json":
                    raise IntegrationError("invalid_api_response", "SMERC API response must use application/json.")
                raw = response.read(MAX_RESPONSE_BYTES + 1)
                if len(raw) > MAX_RESPONSE_BYTES:
                    raise IntegrationError("api_response_too_large", "SMERC API response exceeded 1 MiB.")
                try:
                    return _validate_remote_decision(json.loads(raw.decode("utf-8")))
                except (UnicodeDecodeError, json.JSONDecodeError) as exc:
                    raise IntegrationError("invalid_api_response", "SMERC API returned invalid JSON.") from exc
        except HTTPError as exc:
            if exc.code in TRANSIENT_HTTP_CODES and attempt < max_retries:
                time.sleep(0.25 * (attempt + 1))
                continue
            raise IntegrationError("api_http_error", f"SMERC API returned HTTP {exc.code}.") from exc
        except (URLError, TimeoutError, OSError) as exc:
            if attempt < max_retries:
                time.sleep(0.25 * (attempt + 1))
                continue
            raise IntegrationError("api_unavailable", "SMERC API could not be reached within the retry budget.") from exc
    raise IntegrationError("api_unavailable", "SMERC API retry budget was exhausted.")


def _decision_risk(decision: Dict[str, Any]) -> Any:
    return decision.get("risk_score", decision.get("scores", {}).get("irreversible_exposure_score", ""))


def _decision_confidence(decision: Dict[str, Any]) -> Any:
    return decision.get("confidence_score", decision.get("scores", {}).get("confidence_score", ""))


def _decision_controls(decision: Dict[str, Any]) -> Iterable[str]:
    return decision.get("constraints", decision.get("controls", []))


def _summary_lines(report: Dict[str, Any]) -> Iterable[str]:
    yield "# SMERC Runtime Permission Decision"
    yield ""
    yield f"- Mode: `{report['mode']}`"
    yield f"- Source: `{report['source']}`"
    yield f"- Integration status: `{report['integration_status']}`"
    decision = report.get("decision")
    if decision is None:
        yield ""
        yield "## Evaluation Unavailable"
        yield report["error"]["message"]
        yield ""
        yield "No authorization posture was produced. Enforce mode fails closed on this condition."
        return

    yield f"- Posture: `{decision['posture']}`"
    yield f"- Risk score: `{_decision_risk(decision)}`"
    yield f"- Confidence score: `{_decision_confidence(decision)}`"
    yield f"- Replay ID: `{decision['replay_id']}`"
    yield ""
    yield "## Controls"
    for control in _decision_controls(decision):
        yield f"- `{control}`"
    yield ""
    yield "## Reason Codes"
    for reason in decision["reason_codes"]:
        yield f"- `{reason}`"
    yield ""
    yield "## Summary"
    yield decision["plain_english_summary"]


def _write_github_output(values: Dict[str, str]) -> None:
    output_path = os.environ.get("GITHUB_OUTPUT")
    if not output_path:
        return
    with Path(output_path).open("a", encoding="utf-8") as handle:
        for key, value in values.items():
            handle.write(f"{key}={value}\n")


def _write_step_summary(report: Dict[str, Any]) -> None:
    summary_path = os.environ.get("GITHUB_STEP_SUMMARY")
    if not summary_path:
        return
    Path(summary_path).write_text("\n".join(_summary_lines(report)) + "\n", encoding="utf-8")


def _write_report(path: Path, report: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    serialized = json.dumps(report, indent=2)
    temporary.write_text(serialized, encoding="utf-8")
    try:
        temporary.replace(path)
    except PermissionError:
        # Some synchronized Windows filesystems refuse an otherwise valid atomic rename.
        path.write_text(serialized, encoding="utf-8")
        try:
            temporary.unlink()
        except OSError:
            pass


def _publish_outputs(report: Dict[str, Any]) -> None:
    decision = report.get("decision")
    _write_github_output(
        {
            "posture": decision["posture"] if decision else "UNAVAILABLE",
            "risk-score": str(_decision_risk(decision)) if decision else "",
            "replay-id": decision["replay_id"] if decision else "",
            "integration-status": report["integration_status"],
            "source": report["source"],
        }
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Run SMERC as a GitHub Actions permission gate.")
    parser.add_argument("--action-file", required=True, help="Path to a JSON action request.")
    parser.add_argument("--mode", default="observe", choices=sorted(VALID_MODES))
    parser.add_argument("--source", default="local", choices=["local", "remote"])
    parser.add_argument("--api-url", default=os.environ.get("SMERC_API_URL", ""))
    parser.add_argument("--tenant", default=os.environ.get("SMERC_TENANT"))
    parser.add_argument("--idempotency-key", default=os.environ.get("SMERC_IDEMPOTENCY_KEY"))
    parser.add_argument("--api-failure-policy", default="report", choices=["report", "fail"])
    parser.add_argument("--request-timeout", type=float, default=10.0)
    parser.add_argument("--max-retries", type=int, default=1)
    parser.add_argument("--output-file", default="smerc-decision.json")
    parser.add_argument("--fail-on", default="DENY,FREEZE")
    args = parser.parse_args()

    if not 1 <= args.request_timeout <= 30:
        parser.error("--request-timeout must be between 1 and 30 seconds")
    if not 0 <= args.max_retries <= 3:
        parser.error("--max-retries must be between 0 and 3")

    action = _load_action(Path(args.action_file))
    output_path = Path(args.output_file)
    fail_on = {item.strip().upper() for item in args.fail_on.split(",") if item.strip()}

    try:
        if args.source == "local":
            decision = RuntimePermissionEngine().evaluate(action)
        else:
            api_key = os.environ.get("SMERC_API_KEY", "").strip()
            if not api_key:
                raise IntegrationError("missing_api_key", "SMERC_API_KEY is required for remote evaluation.")
            if not args.api_url:
                raise IntegrationError("missing_api_url", "SMERC API URL is required for remote evaluation.")
            if "\r" in api_key or "\n" in api_key:
                raise IntegrationError("invalid_api_key", "SMERC_API_KEY contains invalid control characters.")
            if args.tenant and not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]{0,63}", args.tenant):
                raise IntegrationError("invalid_tenant", "Tenant must be a safe identifier of 1 to 64 characters.")
            idempotency_key = args.idempotency_key or _default_idempotency_key(action)
            if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._:-]{0,127}", idempotency_key):
                raise IntegrationError(
                    "invalid_idempotency_key",
                    "Idempotency key must be a safe identifier of 1 to 128 characters.",
                )
            decision = _remote_evaluate(
                action,
                api_url=args.api_url,
                api_key=api_key,
                tenant=args.tenant,
                idempotency_key=idempotency_key,
                timeout=args.request_timeout,
                max_retries=args.max_retries,
            )
        report: Dict[str, Any] = {
            "mode": args.mode,
            "source": args.source,
            "integration_status": "evaluated",
            "enforcement": {
                "fail_on": sorted(fail_on),
                "would_fail": decision["posture"] in fail_on,
                "active": args.mode == "enforce",
            },
            "decision": decision,
        }
    except IntegrationError as exc:
        report = {
            "mode": args.mode,
            "source": args.source,
            "integration_status": "unavailable",
            "enforcement": {
                "fail_on": sorted(fail_on),
                "would_fail": True,
                "active": args.mode == "enforce",
            },
            "decision": None,
            "error": {"code": exc.code, "message": exc.message},
        }
        _write_report(output_path, report)
        _write_step_summary(report)
        _publish_outputs(report)
        print(json.dumps(report, indent=2))
        if args.mode == "enforce" or args.api_failure_policy == "fail":
            print("SMERC remote evaluation unavailable; workflow stopped by failure policy.", file=sys.stderr)
            return 2
        return 0

    _write_report(output_path, report)
    _write_step_summary(report)
    _publish_outputs(report)
    print(json.dumps(report, indent=2))

    if args.mode == "enforce" and decision["posture"] in fail_on:
        print(f"SMERC enforce mode failed on posture {decision['posture']}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
