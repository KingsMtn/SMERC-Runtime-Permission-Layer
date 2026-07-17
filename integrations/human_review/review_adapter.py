from __future__ import annotations

import argparse
import hashlib
import hmac
import json
import re
import time
from pathlib import Path
from typing import Any, Dict, Mapping, Optional


REVIEW_REQUEST_VERSION = "smerc.human-review-request.v1"
REVIEW_RESPONSE_VERSION = "smerc.human-review-response.v1"
REVIEW_SIGNATURE_VERSION = "smerc.human-review-signature.v1"
REQUEST_STATES = {"REVIEW_REQUIRED", "BLOCKED_ESCALATION_UNAVAILABLE"}
REVIEW_VERDICTS = {"approve", "deny", "request_changes", "timeout"}


class HumanReviewError(ValueError):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message


def _canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def _digest(value: Any) -> str:
    return hashlib.sha256(_canonical_json(value).encode("utf-8")).hexdigest()


def _identifier(value: Any, path: str, maximum: int = 128) -> str:
    if not isinstance(value, str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._:-]{0,%d}" % (maximum - 1), value):
        raise HumanReviewError("invalid_human_review", f"{path} must be a safe identifier of 1 to {maximum} characters.")
    return value


def _text(value: Any, path: str, maximum: int = 512) -> str:
    if not isinstance(value, str) or not value.strip():
        raise HumanReviewError("invalid_human_review", f"{path} must be a non-empty string.")
    value = value.strip()
    if len(value) > maximum:
        raise HumanReviewError("invalid_human_review", f"{path} must be at most {maximum} characters.")
    return value


def _positive_int(value: Any, path: str, maximum: int = 86_400) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 1 or value > maximum:
        raise HumanReviewError("invalid_human_review", f"{path} must be an integer from 1 through {maximum}.")
    return value


def _object(value: Any, path: str) -> Dict[str, Any]:
    if not isinstance(value, dict):
        raise HumanReviewError("invalid_human_review", f"{path} must be an object.")
    return dict(value)


def _signable(payload: Mapping[str, Any]) -> Dict[str, Any]:
    return {
        key: value
        for key, value in dict(payload).items()
        if key not in {"signature", "signature_verification"}
    }


def _signature(payload: Mapping[str, Any], secret: str, *, key_id: str) -> Dict[str, Any]:
    if not isinstance(secret, str) or len(secret) < 16:
        raise HumanReviewError("invalid_human_review_secret", "review signing secret must be at least 16 characters.")
    key_id = _identifier(key_id, "key_id")
    digest = _digest(_signable(payload))
    return {
        "version": REVIEW_SIGNATURE_VERSION,
        "algorithm": "HMAC-SHA256",
        "key_id": key_id,
        "payload_digest": digest,
        "signature": hmac.new(secret.encode("utf-8"), digest.encode("ascii"), hashlib.sha256).hexdigest(),
    }


def _verify_signature(payload: Mapping[str, Any], secret: str) -> Dict[str, Any]:
    signature = payload.get("signature")
    if not isinstance(signature, dict):
        return {"valid": False, "errors": ["missing signature"]}
    required = {"version", "algorithm", "key_id", "payload_digest", "signature"}
    missing = sorted(required - set(signature))
    if missing:
        return {"valid": False, "errors": [f"signature missing field(s): {', '.join(missing)}"]}
    if signature.get("version") != REVIEW_SIGNATURE_VERSION:
        return {"valid": False, "errors": ["invalid signature version"]}
    if signature.get("algorithm") != "HMAC-SHA256":
        return {"valid": False, "errors": ["invalid signature algorithm"]}
    expected_digest = _digest(_signable(payload))
    if not hmac.compare_digest(str(signature["payload_digest"]), expected_digest):
        return {"valid": False, "errors": ["payload digest mismatch"]}
    expected_signature = hmac.new(
        secret.encode("utf-8"),
        expected_digest.encode("ascii"),
        hashlib.sha256,
    ).hexdigest()
    if not hmac.compare_digest(str(signature["signature"]), expected_signature):
        return {"valid": False, "errors": ["signature mismatch"]}
    return {
        "valid": True,
        "errors": [],
        "key_id": signature["key_id"],
        "payload_digest": expected_digest,
    }


def build_review_request(
    route_report: Mapping[str, Any],
    *,
    requester: str,
    reviewer_group: str,
    callback_ref: str,
    ttl_seconds: int = 1800,
    now: Optional[int] = None,
    secret: Optional[str] = None,
    key_id: str = "human-review-request-key",
) -> Dict[str, Any]:
    route = _object(route_report, "route_report")
    if route.get("route_state") not in REQUEST_STATES:
        raise HumanReviewError("route_not_reviewable", "Only review-required SPARTa routes can create human review requests.")
    issued_at = int(time.time()) if now is None else now
    ttl = _positive_int(ttl_seconds, "ttl_seconds")
    request = {
        "version": REVIEW_REQUEST_VERSION,
        "review_request_id": f"review_request_{_digest({'route_id': route.get('route_id'), 'issued_at': issued_at})[:32]}",
        "route_id": _identifier(route.get("route_id"), "route_report.route_id", 192),
        "decision_replay_id": _identifier(route.get("decision_replay_id"), "route_report.decision_replay_id", 192),
        "route_state": route["route_state"],
        "source_posture": _identifier(route.get("source_posture"), "route_report.source_posture", 32),
        "requested_by": _identifier(requester, "requested_by"),
        "reviewer_group": _identifier(reviewer_group, "reviewer_group"),
        "callback_ref": _text(callback_ref, "callback_ref", 256),
        "reason_codes": _string_list(route.get("reason_codes", []), "route_report.reason_codes"),
        "applied_controls": _string_list(route.get("applied_controls", []), "route_report.applied_controls"),
        "blocked_controls": _string_list(route.get("blocked_controls", []), "route_report.blocked_controls"),
        "plain_english_summary": _text(route.get("plain_english_summary"), "route_report.plain_english_summary", 1024),
        "issued_at": issued_at,
        "expires_at": issued_at + ttl,
        "route_report_digest": _digest(route),
        "evidence_boundary": (
            "Vendor-neutral human review request. Delivery through Slack, Teams, Jira, ServiceNow, "
            "email, or another workflow tool must preserve this signed payload and reviewer response."
        ),
    }
    if secret is not None:
        request["signature"] = _signature(request, secret, key_id=key_id)
    return request


def build_review_response(
    review_request: Mapping[str, Any],
    *,
    reviewer_id: str,
    verdict: str,
    rationale: str,
    final_posture: str,
    now: Optional[int] = None,
    secret: Optional[str] = None,
    key_id: str = "human-review-response-key",
) -> Dict[str, Any]:
    request = validate_review_request(review_request)
    verdict = _identifier(verdict, "verdict", 32)
    if verdict not in REVIEW_VERDICTS:
        raise HumanReviewError("invalid_review_verdict", f"verdict must be one of {', '.join(sorted(REVIEW_VERDICTS))}.")
    reviewed_at = int(time.time()) if now is None else now
    if reviewed_at > request["expires_at"]:
        raise HumanReviewError("review_request_expired", "Review request has expired.")
    response = {
        "version": REVIEW_RESPONSE_VERSION,
        "review_response_id": f"review_response_{_digest({'request': request['review_request_id'], 'reviewer': reviewer_id, 'at': reviewed_at})[:32]}",
        "review_request_id": request["review_request_id"],
        "route_id": request["route_id"],
        "decision_replay_id": request["decision_replay_id"],
        "reviewer_id": _identifier(reviewer_id, "reviewer_id"),
        "reviewer_group": request["reviewer_group"],
        "verdict": verdict,
        "rationale": _text(rationale, "rationale", 1024),
        "source_posture": request["source_posture"],
        "final_posture": _identifier(final_posture, "final_posture", 32),
        "reviewed_at": reviewed_at,
        "request_digest": _digest(_signable(request)),
        "evidence_boundary": "Signed reviewer response package. It records review intent but does not prove external identity provider assurance by itself.",
    }
    if secret is not None:
        response["signature"] = _signature(response, secret, key_id=key_id)
    return response


def validate_review_request(review_request: Mapping[str, Any], *, secret: Optional[str] = None) -> Dict[str, Any]:
    request = _object(review_request, "review_request")
    required = {
        "version",
        "review_request_id",
        "route_id",
        "decision_replay_id",
        "route_state",
        "source_posture",
        "requested_by",
        "reviewer_group",
        "callback_ref",
        "reason_codes",
        "applied_controls",
        "blocked_controls",
        "plain_english_summary",
        "issued_at",
        "expires_at",
        "route_report_digest",
        "evidence_boundary",
    }
    missing = sorted(required - set(request))
    if missing:
        raise HumanReviewError("invalid_review_request", f"review_request missing field(s): {', '.join(missing)}.")
    if request["version"] != REVIEW_REQUEST_VERSION:
        raise HumanReviewError("invalid_review_request", f"review_request.version must be {REVIEW_REQUEST_VERSION}.")
    _identifier(request["review_request_id"], "review_request_id", 192)
    _identifier(request["route_id"], "route_id", 192)
    _identifier(request["decision_replay_id"], "decision_replay_id", 192)
    if request["route_state"] not in REQUEST_STATES:
        raise HumanReviewError("invalid_review_request", "route_state is not review-required.")
    _identifier(request["source_posture"], "source_posture", 32)
    _identifier(request["requested_by"], "requested_by")
    _identifier(request["reviewer_group"], "reviewer_group")
    _text(request["callback_ref"], "callback_ref", 256)
    _string_list(request["reason_codes"], "reason_codes")
    _string_list(request["applied_controls"], "applied_controls")
    _string_list(request["blocked_controls"], "blocked_controls")
    _text(request["plain_english_summary"], "plain_english_summary", 1024)
    _positive_int(request["issued_at"], "issued_at", 4_102_444_800)
    _positive_int(request["expires_at"], "expires_at", 4_102_444_800)
    if request["expires_at"] <= request["issued_at"]:
        raise HumanReviewError("invalid_review_request", "expires_at must be after issued_at.")
    _hex_digest(request["route_report_digest"], "route_report_digest")
    if secret is not None:
        verification = _verify_signature(request, secret)
        if not verification["valid"]:
            raise HumanReviewError("invalid_review_signature", "; ".join(verification["errors"]))
        request["signature_verification"] = verification
    return request


def validate_review_response(
    review_response: Mapping[str, Any],
    review_request: Mapping[str, Any],
    *,
    secret: Optional[str] = None,
) -> Dict[str, Any]:
    request = validate_review_request(review_request)
    response = _object(review_response, "review_response")
    required = {
        "version",
        "review_response_id",
        "review_request_id",
        "route_id",
        "decision_replay_id",
        "reviewer_id",
        "reviewer_group",
        "verdict",
        "rationale",
        "source_posture",
        "final_posture",
        "reviewed_at",
        "request_digest",
        "evidence_boundary",
    }
    missing = sorted(required - set(response))
    if missing:
        raise HumanReviewError("invalid_review_response", f"review_response missing field(s): {', '.join(missing)}.")
    if response["version"] != REVIEW_RESPONSE_VERSION:
        raise HumanReviewError("invalid_review_response", f"review_response.version must be {REVIEW_RESPONSE_VERSION}.")
    for field in ["review_request_id", "route_id", "decision_replay_id", "reviewer_group", "source_posture"]:
        if response[field] != request[field]:
            raise HumanReviewError("review_binding_mismatch", f"review_response.{field} does not match request.")
    _identifier(response["review_response_id"], "review_response_id", 192)
    _identifier(response["reviewer_id"], "reviewer_id")
    verdict = _identifier(response["verdict"], "verdict", 32)
    if verdict not in REVIEW_VERDICTS:
        raise HumanReviewError("invalid_review_verdict", f"verdict must be one of {', '.join(sorted(REVIEW_VERDICTS))}.")
    _text(response["rationale"], "rationale", 1024)
    _identifier(response["final_posture"], "final_posture", 32)
    _positive_int(response["reviewed_at"], "reviewed_at", 4_102_444_800)
    if response["reviewed_at"] > request["expires_at"]:
        raise HumanReviewError("review_request_expired", "Review response arrived after request expiration.")
    if response["request_digest"] != _digest(_signable(request)):
        raise HumanReviewError("review_binding_mismatch", "review_response.request_digest does not match request.")
    if secret is not None:
        verification = _verify_signature(response, secret)
        if not verification["valid"]:
            raise HumanReviewError("invalid_review_signature", "; ".join(verification["errors"]))
        response["signature_verification"] = verification
    return response


def _string_list(value: Any, path: str) -> list[str]:
    if not isinstance(value, list) or any(not isinstance(item, str) or not item for item in value):
        raise HumanReviewError("invalid_human_review", f"{path} must be a list of non-empty strings.")
    return sorted(set(value))


def _hex_digest(value: Any, path: str) -> str:
    if not isinstance(value, str) or not re.fullmatch(r"[0-9a-f]{64}", value):
        raise HumanReviewError("invalid_human_review", f"{path} must be a lowercase SHA-256 digest.")
    return value


def _load_json(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise HumanReviewError("invalid_json", f"{path} must contain a JSON object.")
    return value


def _write_json(path: Path, value: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Build or validate vendor-neutral SMERC human review packages.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    request_parser = subparsers.add_parser("request", help="Create a signed human review request from a SPARTa route.")
    request_parser.add_argument("--route-report", required=True, type=Path)
    request_parser.add_argument("--requested-by", required=True)
    request_parser.add_argument("--reviewer-group", required=True)
    request_parser.add_argument("--callback-ref", required=True)
    request_parser.add_argument("--ttl-seconds", type=int, default=1800)
    request_parser.add_argument("--secret")
    request_parser.add_argument("--key-id", default="human-review-request-key")
    request_parser.add_argument("--output", type=Path)
    request_parser.add_argument("--pretty", action="store_true")

    response_parser = subparsers.add_parser("response", help="Create a signed reviewer response.")
    response_parser.add_argument("--review-request", required=True, type=Path)
    response_parser.add_argument("--reviewer-id", required=True)
    response_parser.add_argument("--verdict", required=True)
    response_parser.add_argument("--rationale", required=True)
    response_parser.add_argument("--final-posture", required=True)
    response_parser.add_argument("--secret")
    response_parser.add_argument("--key-id", default="human-review-response-key")
    response_parser.add_argument("--output", type=Path)
    response_parser.add_argument("--pretty", action="store_true")

    verify_parser = subparsers.add_parser("verify-response", help="Verify response binding against its request.")
    verify_parser.add_argument("--review-request", required=True, type=Path)
    verify_parser.add_argument("--review-response", required=True, type=Path)
    verify_parser.add_argument("--request-secret")
    verify_parser.add_argument("--response-secret")
    verify_parser.add_argument("--pretty", action="store_true")

    args = parser.parse_args()
    if args.command == "request":
        payload = build_review_request(
            _load_json(args.route_report),
            requester=args.requested_by,
            reviewer_group=args.reviewer_group,
            callback_ref=args.callback_ref,
            ttl_seconds=args.ttl_seconds,
            secret=args.secret,
            key_id=args.key_id,
        )
    elif args.command == "response":
        payload = build_review_response(
            _load_json(args.review_request),
            reviewer_id=args.reviewer_id,
            verdict=args.verdict,
            rationale=args.rationale,
            final_posture=args.final_posture,
            secret=args.secret,
            key_id=args.key_id,
        )
    else:
        request = validate_review_request(_load_json(args.review_request), secret=args.request_secret)
        response = validate_review_response(
            _load_json(args.review_response),
            request,
            secret=args.response_secret,
        )
        payload = {"valid": True, "request": request, "response": response}
    if getattr(args, "output", None):
        _write_json(args.output, payload)
    print(json.dumps(payload, indent=2 if getattr(args, "pretty", False) else None, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
