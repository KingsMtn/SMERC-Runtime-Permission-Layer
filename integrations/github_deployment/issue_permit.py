from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
from pathlib import Path
from typing import Any, Dict
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit, urlunsplit
from urllib.request import HTTPRedirectHandler, Request, build_opener


MAX_BODY_BYTES = 1024 * 1024


class PermitIssueError(RuntimeError):
    pass


class SameOriginRedirectHandler(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):  # type: ignore[no-untyped-def]
        original = urlsplit(req.full_url)
        redirected = urlsplit(newurl)
        if (original.scheme, original.hostname, original.port) != (
            redirected.scheme,
            redirected.hostname,
            redirected.port,
        ):
            raise HTTPError(newurl, code, "Cross-origin API redirect refused.", headers, fp)
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def endpoint(base_url: str, path: str) -> str:
    parsed = urlsplit(base_url.strip())
    loopback = parsed.hostname in {"localhost", "127.0.0.1", "::1"}
    if (
        not parsed.hostname
        or parsed.username
        or parsed.password
        or parsed.query
        or parsed.fragment
        or (parsed.scheme != "https" and not (parsed.scheme == "http" and loopback))
    ):
        raise PermitIssueError("SMERC API URL must use HTTPS outside loopback and contain no credentials.")
    return urlunsplit((parsed.scheme, parsed.netloc, f"{parsed.path.rstrip('/')}{path}", "", ""))


def post_json(url: str, token: str, payload: Dict[str, Any], *, idempotency_key: str | None = None) -> Dict[str, Any]:
    if not token or "\n" in token or "\r" in token:
        raise PermitIssueError("Required scoped credential is missing or invalid.")
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    if idempotency_key:
        headers["Idempotency-Key"] = idempotency_key
    request = Request(
        url,
        data=json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8"),
        headers=headers,
        method="POST",
    )
    try:
        with build_opener(SameOriginRedirectHandler()).open(request, timeout=15) as response:
            raw = response.read(MAX_BODY_BYTES + 1)
    except (HTTPError, URLError, TimeoutError) as exc:
        raise PermitIssueError("SMERC API rejected or could not complete permit issuance.") from exc
    if len(raw) > MAX_BODY_BYTES:
        raise PermitIssueError("SMERC API response exceeded the permitted size.")
    try:
        value = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise PermitIssueError("SMERC API returned an invalid response.") from exc
    if not isinstance(value, dict):
        raise PermitIssueError("SMERC API returned an invalid response object.")
    return value


def load_action(path: Path) -> Dict[str, Any]:
    try:
        raw = path.read_bytes()
        value = json.loads(raw.decode("utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise PermitIssueError("Action file is unavailable or invalid.") from exc
    if not isinstance(value, dict) or not raw or len(raw) > 128 * 1024:
        raise PermitIssueError("Action file must be one bounded JSON object.")
    return value


def write_private_file(path: Path, token: str) -> None:
    if not re.fullmatch(r"[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+", token):
        raise PermitIssueError("Permit response did not contain a valid token shape.")
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(token)
        os.chmod(path, 0o600)
    except OSError as exc:
        raise PermitIssueError("Permit file could not be created exclusively.") from exc


def main() -> int:
    parser = argparse.ArgumentParser(description="Evaluate one action and issue one action-bound permit.")
    parser.add_argument("--api-url", required=True)
    parser.add_argument("--action-file", required=True)
    parser.add_argument("--audience", required=True)
    parser.add_argument("--output-file", required=True)
    parser.add_argument("--ttl-seconds", type=int, default=120)
    args = parser.parse_args()
    if not 1 <= args.ttl_seconds <= 300:
        raise PermitIssueError("ttl-seconds must be from 1 through 300.")
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._:-]{0,127}", args.audience):
        raise PermitIssueError("Audience is invalid.")
    action = load_action(Path(args.action_file))
    run_identity = os.environ.get("GITHUB_RUN_ID", "local")
    action_digest = hashlib.sha256(
        json.dumps(action, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()[:24]
    decision = post_json(
        endpoint(args.api_url, "/v1/language/evaluate"),
        os.environ.get("SMERC_PROPOSER_TOKEN", ""),
        action,
        idempotency_key=f"deployment-permit-{run_identity}-{args.audience}-{action_digest}"[:192],
    )
    replay_id = decision.get("replay_id")
    if not isinstance(replay_id, str) or not replay_id:
        raise PermitIssueError("Evaluation response omitted replay_id.")
    issued = post_json(
        endpoint(args.api_url, "/v1/permits/issue"),
        os.environ.get("SMERC_ISSUER_TOKEN", ""),
        {
            "replay_id": replay_id,
            "action": action,
            "audience": args.audience,
            "ttl_seconds": args.ttl_seconds,
        },
    )
    token = issued.get("permit_token")
    if not isinstance(token, str):
        raise PermitIssueError("Permit response omitted permit_token.")
    write_private_file(Path(args.output_file), token)
    print(json.dumps({"status": "issued", "replay_id": replay_id, "audience": args.audience}))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except PermitIssueError as exc:
        print(json.dumps({"error": "permit_issue_failed", "message": str(exc)}), file=sys.stderr)
        raise SystemExit(2)
