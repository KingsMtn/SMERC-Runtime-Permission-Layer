from __future__ import annotations

import argparse
import hashlib
import hmac
import json
import os
import re
import uuid
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any, Dict, Iterable, Mapping, Optional
from urllib.parse import parse_qs, urlsplit

from reference_engine.audit_store import AuditStore, IdempotencyConflictError, ReviewConflictError
from reference_engine.recoverability_engine import RecoverabilityEngine, RuntimePosture


DEFAULT_MAX_BODY_BYTES = 256 * 1024
DEFAULT_MAX_BATCH_SIZE = 100


class APIError(Exception):
    def __init__(self, status: HTTPStatus, code: str, message: str) -> None:
        super().__init__(message)
        self.status = status
        self.code = code
        self.message = message


class SMERCAPIServer(ThreadingHTTPServer):
    def __init__(
        self,
        server_address: tuple[str, int],
        *,
        audit_store: AuditStore,
        api_keys: Mapping[str, str],
        allow_unauthenticated: bool = False,
        max_body_bytes: int = DEFAULT_MAX_BODY_BYTES,
        max_batch_size: int = DEFAULT_MAX_BATCH_SIZE,
        cors_origins: Iterable[str] = (),
    ) -> None:
        super().__init__(server_address, SMERCRequestHandler)
        self.engine = RecoverabilityEngine()
        self.audit_store = audit_store
        self.api_keys = dict(api_keys)
        self.allow_unauthenticated = allow_unauthenticated
        self.max_body_bytes = max_body_bytes
        self.max_batch_size = max_batch_size
        self.cors_origins = frozenset(cors_origins)

    def server_close(self) -> None:
        super().server_close()
        self.audit_store.close()


class SMERCRequestHandler(BaseHTTPRequestHandler):
    server: SMERCAPIServer
    server_version = "SMERCRecoverabilityAPI/0.4"

    def do_OPTIONS(self) -> None:
        origin = self.headers.get("origin")
        if origin and origin in self.server.cors_origins:
            self.send_response(HTTPStatus.NO_CONTENT)
            self.send_header("access-control-allow-origin", origin)
            self.send_header("access-control-allow-methods", "GET, POST, OPTIONS")
            self.send_header(
                "access-control-allow-headers",
                "Authorization, Content-Type, Idempotency-Key, X-SMERC-Tenant, X-Request-ID",
            )
            self.send_header("vary", "Origin")
            self.end_headers()
            return
        self._write_error(APIError(HTTPStatus.FORBIDDEN, "origin_not_allowed", "Origin is not allowed."))

    def do_GET(self) -> None:
        request_id = self._request_id()
        try:
            path, query = self._path_and_query()
            if path in {"/health", "/v1/health"}:
                self._write_json(
                    {
                        "status": "ok",
                        "service": "smerc-recoverability-api",
                        "version": "0.4",
                        "request_id": request_id,
                    },
                    request_id=request_id,
                )
                return
            if path in {"/ready", "/v1/ready"}:
                ready = self.server.audit_store.ping()
                self._write_json(
                    {"status": "ready" if ready else "not_ready", "request_id": request_id},
                    HTTPStatus.OK if ready else HTTPStatus.SERVICE_UNAVAILABLE,
                    request_id=request_id,
                )
                return
            if path in {"/schema", "/v1/schema"}:
                self._write_json(schema(), request_id=request_id)
                return

            tenant_id = self._authenticate()
            if path == "/v1/pilot/metrics":
                metrics = self.server.audit_store.pilot_metrics(tenant_id)
                metrics["request_id"] = request_id
                self._write_json(metrics, request_id=request_id)
                return
            if path == "/v1/review-queue":
                limit = self._parse_limit(query)
                posture = self._parse_posture(query)
                review_status = self._parse_review_status(query)
                queue = self.server.audit_store.review_queue(
                    tenant_id,
                    limit=limit,
                    review_status=review_status,
                    posture=posture,
                )
                self._write_json(
                    {
                        "tenant_id": tenant_id,
                        "count": len(queue),
                        "status": review_status,
                        "posture": posture,
                        "decisions": queue,
                        "request_id": request_id,
                    },
                    request_id=request_id,
                )
                return
            if path == "/v1/decisions":
                limit = self._parse_limit(query)
                posture = self._parse_posture(query)
                decisions = self.server.audit_store.list(tenant_id, limit=limit, posture=posture)
                self._write_json(
                    {
                        "tenant_id": tenant_id,
                        "count": len(decisions),
                        "total": self.server.audit_store.count(tenant_id),
                        "decisions": decisions,
                        "request_id": request_id,
                    },
                    request_id=request_id,
                )
                return
            review_replay_id = self._review_replay_id(path)
            if review_replay_id is not None:
                decision = self.server.audit_store.get(tenant_id, review_replay_id)
                if decision is None:
                    raise APIError(HTTPStatus.NOT_FOUND, "decision_not_found", "Decision was not found.")
                reviews = self.server.audit_store.list_reviews(tenant_id, review_replay_id)
                self._write_json(
                    {
                        "tenant_id": tenant_id,
                        "replay_id": review_replay_id,
                        "count": len(reviews),
                        "reviews": reviews,
                        "request_id": request_id,
                    },
                    request_id=request_id,
                )
                return
            prefix = "/v1/decisions/"
            if path.startswith(prefix) and len(path) > len(prefix):
                replay_id = path[len(prefix) :]
                decision = self.server.audit_store.get(tenant_id, replay_id)
                if decision is None:
                    raise APIError(HTTPStatus.NOT_FOUND, "decision_not_found", "Decision was not found.")
                self._write_json(decision, request_id=request_id)
                return
            raise APIError(
                HTTPStatus.NOT_FOUND,
                "not_found",
                "Use /health, /ready, /schema, /v1/evaluate, /v1/decisions, /v1/review-queue, or /v1/pilot/metrics.",
            )
        except APIError as exc:
            self._write_error(exc, request_id)

    def do_POST(self) -> None:
        request_id = self._request_id()
        try:
            path, _ = self._path_and_query()
            tenant_id = self._authenticate()
            payload = self._read_json()

            review_replay_id = self._review_replay_id(path)
            if review_replay_id is not None:
                if not isinstance(payload, dict):
                    raise APIError(HTTPStatus.BAD_REQUEST, "invalid_payload", "Review expects one JSON object.")
                result, replayed = self._record_review(tenant_id, review_replay_id, payload)
                headers = {"x-smerc-idempotent-replay": "true"} if replayed else None
                self._write_json(
                    result,
                    HTTPStatus.OK if replayed else HTTPStatus.CREATED,
                    request_id=request_id,
                    extra_headers=headers,
                )
                return

            if path not in {"/evaluate", "/batch", "/v1/evaluate", "/v1/batch"}:
                raise APIError(HTTPStatus.NOT_FOUND, "not_found", "Use /evaluate, /batch, or a review endpoint.")

            if path in {"/evaluate", "/v1/evaluate"}:
                if not isinstance(payload, dict):
                    raise APIError(HTTPStatus.BAD_REQUEST, "invalid_payload", "/evaluate expects one JSON object.")
                result, replayed = self._evaluate_one(tenant_id, payload)
                headers = {"x-smerc-idempotent-replay": "true"} if replayed else None
                self._write_json(result, request_id=request_id, extra_headers=headers)
                return

            if not isinstance(payload, list):
                raise APIError(HTTPStatus.BAD_REQUEST, "invalid_payload", "/batch expects a JSON list.")
            if not payload:
                raise APIError(HTTPStatus.BAD_REQUEST, "invalid_payload", "/batch requires at least one action.")
            if len(payload) > self.server.max_batch_size:
                raise APIError(
                    HTTPStatus.REQUEST_ENTITY_TOO_LARGE,
                    "batch_too_large",
                    f"Batch exceeds the {self.server.max_batch_size}-action limit.",
                )
            results = [self._evaluate_and_record(tenant_id, item) for item in payload]
            response: Any = results
            if path == "/v1/batch":
                response = {
                    "tenant_id": tenant_id,
                    "count": len(results),
                    "decisions": results,
                    "request_id": request_id,
                }
            self._write_json(response, request_id=request_id)
        except APIError as exc:
            self._write_error(exc, request_id)
        except (TypeError, ValueError, json.JSONDecodeError) as exc:
            self._write_error(APIError(HTTPStatus.BAD_REQUEST, "bad_request", str(exc)), request_id)

    def _record_review(
        self,
        tenant_id: str,
        replay_id: str,
        payload: Dict[str, Any],
    ) -> tuple[Dict[str, Any], bool]:
        decision = self.server.audit_store.get(tenant_id, replay_id)
        if decision is None:
            raise APIError(HTTPStatus.NOT_FOUND, "decision_not_found", "Decision was not found.")

        request_hash = payload_hash({"replay_id": replay_id, "review": payload})
        idempotency_key = self._idempotency_key()
        if idempotency_key is not None:
            stored = self.server.audit_store.get_review_by_idempotency_key(tenant_id, idempotency_key)
            if stored is not None:
                if not hmac.compare_digest(stored["request_hash"], request_hash):
                    raise APIError(
                        HTTPStatus.CONFLICT,
                        "idempotency_conflict",
                        "Idempotency-Key was already used with a different review body.",
                    )
                return stored["review"], True

        review = self._validate_review(payload, decision["posture"])
        review.update(
            {
                "review_id": str(uuid.uuid4()),
                "tenant_id": tenant_id,
                "replay_id": replay_id,
                "decision_posture": decision["posture"],
            }
        )
        try:
            stored_review = self.server.audit_store.record_review(
                tenant_id,
                replay_id,
                review,
                request_hash,
                idempotency_key=idempotency_key,
            )
        except IdempotencyConflictError as exc:
            raise APIError(HTTPStatus.CONFLICT, "idempotency_conflict", str(exc)) from exc
        except ReviewConflictError as exc:
            raise APIError(HTTPStatus.CONFLICT, "review_conflict", str(exc)) from exc
        return stored_review, False

    @staticmethod
    def _validate_review(payload: Dict[str, Any], decision_posture: str) -> Dict[str, Any]:
        allowed_fields = {
            "reviewer_id",
            "verdict",
            "recommended_posture",
            "false_release",
            "false_constraint",
            "useful_constraint",
            "review_latency_ms",
            "comment",
        }
        unknown = sorted(set(payload) - allowed_fields)
        if unknown:
            raise APIError(
                HTTPStatus.BAD_REQUEST,
                "unknown_review_fields",
                f"Unknown review fields: {', '.join(unknown)}.",
            )

        reviewer_id = payload.get("reviewer_id")
        if not isinstance(reviewer_id, str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]{0,63}", reviewer_id):
            raise APIError(
                HTTPStatus.BAD_REQUEST,
                "invalid_reviewer_id",
                "reviewer_id must be a pseudonymous 1-64 character safe identifier.",
            )
        verdict = payload.get("verdict")
        if verdict not in {"agree", "override", "uncertain"}:
            raise APIError(
                HTTPStatus.BAD_REQUEST,
                "invalid_verdict",
                "verdict must be agree, override, or uncertain.",
            )
        postures = {item.value for item in RuntimePosture}
        recommended = payload.get("recommended_posture")
        if recommended is not None:
            if not isinstance(recommended, str) or recommended.upper() not in postures:
                raise APIError(
                    HTTPStatus.BAD_REQUEST,
                    "invalid_recommended_posture",
                    "recommended_posture is not recognized.",
                )
            recommended = recommended.upper()
        if verdict == "override" and (recommended is None or recommended == decision_posture):
            raise APIError(
                HTTPStatus.BAD_REQUEST,
                "invalid_override",
                "override requires a recommended_posture different from the decision posture.",
            )
        if verdict == "agree" and recommended not in {None, decision_posture}:
            raise APIError(
                HTTPStatus.BAD_REQUEST,
                "invalid_agreement",
                "agree cannot recommend a different posture.",
            )

        flags: Dict[str, bool] = {}
        for name in ("false_release", "false_constraint", "useful_constraint"):
            value = payload.get(name, False)
            if not isinstance(value, bool):
                raise APIError(HTTPStatus.BAD_REQUEST, "invalid_review_flag", f"{name} must be boolean.")
            flags[name] = value
        if flags["false_release"] and decision_posture != "ALLOW":
            raise APIError(
                HTTPStatus.BAD_REQUEST,
                "invalid_false_release",
                "false_release applies only to an ALLOW decision.",
            )
        if (flags["false_constraint"] or flags["useful_constraint"]) and decision_posture == "ALLOW":
            raise APIError(
                HTTPStatus.BAD_REQUEST,
                "invalid_constraint_label",
                "constraint labels do not apply to an ALLOW decision.",
            )
        if flags["false_constraint"] and flags["useful_constraint"]:
            raise APIError(
                HTTPStatus.BAD_REQUEST,
                "conflicting_constraint_labels",
                "A constraint cannot be both false and useful in one review.",
            )

        latency = payload.get("review_latency_ms")
        if isinstance(latency, bool) or not isinstance(latency, int) or latency < 0 or latency > 604_800_000:
            raise APIError(
                HTTPStatus.BAD_REQUEST,
                "invalid_review_latency",
                "review_latency_ms must be an integer from 0 through 604800000.",
            )
        comment = payload.get("comment")
        if comment is not None and (not isinstance(comment, str) or len(comment.strip()) > 500):
            raise APIError(
                HTTPStatus.BAD_REQUEST,
                "invalid_review_comment",
                "comment must be a string of at most 500 characters.",
            )

        return {
            "reviewer_id": reviewer_id,
            "verdict": verdict,
            "recommended_posture": recommended,
            **flags,
            "review_latency_ms": latency,
            "comment": comment.strip() if isinstance(comment, str) and comment.strip() else None,
        }

    @staticmethod
    def _review_replay_id(path: str) -> Optional[str]:
        match = re.fullmatch(r"/v1/decisions/([^/]+)/reviews", path)
        return None if match is None else match.group(1)

    def _idempotency_key(self) -> Optional[str]:
        value = self.headers.get("idempotency-key")
        if value is None:
            return None
        value = value.strip()
        if not value or len(value) > 128:
            raise APIError(
                HTTPStatus.BAD_REQUEST,
                "invalid_idempotency_key",
                "Idempotency-Key must contain 1 to 128 characters.",
            )
        return value

    def _evaluate_one(self, tenant_id: str, payload: Dict[str, Any]) -> tuple[Dict[str, Any], bool]:
        request_hash = payload_hash(payload)
        idempotency_key = self._idempotency_key()
        if idempotency_key is not None:
            stored = self.server.audit_store.get_by_idempotency_key(tenant_id, idempotency_key)
            if stored is not None:
                if not hmac.compare_digest(stored["request_hash"], request_hash):
                    raise APIError(
                        HTTPStatus.CONFLICT,
                        "idempotency_conflict",
                        "Idempotency-Key was already used with a different request body.",
                    )
                return stored["decision"], True
        return self._evaluate_and_record(tenant_id, payload, request_hash, idempotency_key), False

    def _evaluate_and_record(
        self,
        tenant_id: str,
        payload: Dict[str, Any],
        request_hash: Optional[str] = None,
        idempotency_key: Optional[str] = None,
    ) -> Dict[str, Any]:
        if not isinstance(payload, dict):
            raise TypeError("Each action must be a JSON object.")
        decision = self.server.engine.evaluate(payload)
        decision["tenant_id"] = tenant_id
        try:
            return self.server.audit_store.record(
                tenant_id,
                decision,
                request_hash or payload_hash(payload),
                idempotency_key=idempotency_key,
            )
        except IdempotencyConflictError as exc:
            raise APIError(HTTPStatus.CONFLICT, "idempotency_conflict", str(exc)) from exc

    def _authenticate(self) -> str:
        if self.server.allow_unauthenticated:
            tenant = self.headers.get("x-smerc-tenant", "local-development").strip()
            return tenant or "local-development"

        authorization = self.headers.get("authorization", "")
        scheme, separator, candidate = authorization.partition(" ")
        if separator != " " or scheme.lower() != "bearer" or not candidate:
            raise APIError(HTTPStatus.UNAUTHORIZED, "authentication_required", "Bearer authentication is required.")
        for tenant_id, expected_key in self.server.api_keys.items():
            if hmac.compare_digest(candidate, expected_key):
                requested_tenant = self.headers.get("x-smerc-tenant")
                if requested_tenant and not hmac.compare_digest(requested_tenant.strip(), tenant_id):
                    raise APIError(HTTPStatus.FORBIDDEN, "tenant_mismatch", "API key is not valid for that tenant.")
                return tenant_id
        raise APIError(HTTPStatus.UNAUTHORIZED, "invalid_api_key", "Bearer credential is invalid.")

    def _read_json(self) -> Any:
        content_type = self.headers.get("content-type", "").split(";", 1)[0].strip().lower()
        if content_type != "application/json":
            raise APIError(HTTPStatus.UNSUPPORTED_MEDIA_TYPE, "unsupported_media_type", "Use application/json.")
        try:
            length = int(self.headers.get("content-length", "0"))
        except ValueError as exc:
            raise APIError(HTTPStatus.BAD_REQUEST, "invalid_content_length", "Content-Length is invalid.") from exc
        if length <= 0:
            raise APIError(HTTPStatus.BAD_REQUEST, "empty_body", "Request body is required.")
        if length > self.server.max_body_bytes:
            raise APIError(
                HTTPStatus.REQUEST_ENTITY_TOO_LARGE,
                "body_too_large",
                f"Request body exceeds {self.server.max_body_bytes} bytes.",
            )
        body = self.rfile.read(length)
        return json.loads(body.decode("utf-8"))

    @staticmethod
    def _request_id() -> str:
        candidate = str(uuid.uuid4())
        return candidate

    def _path_and_query(self) -> tuple[str, Dict[str, list[str]]]:
        parsed = urlsplit(self.path)
        return parsed.path.rstrip("/") or "/", parse_qs(parsed.query)

    @staticmethod
    def _parse_limit(query: Dict[str, list[str]]) -> int:
        raw = query.get("limit", ["50"])[0]
        try:
            limit = int(raw)
        except ValueError as exc:
            raise APIError(HTTPStatus.BAD_REQUEST, "invalid_limit", "limit must be an integer.") from exc
        if limit < 1 or limit > 200:
            raise APIError(HTTPStatus.BAD_REQUEST, "invalid_limit", "limit must be between 1 and 200.")
        return limit

    @staticmethod
    def _parse_posture(query: Dict[str, list[str]]) -> Optional[str]:
        posture = query.get("posture", [None])[0]
        if posture is None:
            return None
        posture = posture.upper()
        if posture not in {item.value for item in RuntimePosture}:
            raise APIError(HTTPStatus.BAD_REQUEST, "invalid_posture", "posture is not recognized.")
        return posture

    @staticmethod
    def _parse_review_status(query: Dict[str, list[str]]) -> str:
        status = query.get("status", ["all"])[0].lower()
        if status not in {"all", "pending", "reviewed"}:
            raise APIError(
                HTTPStatus.BAD_REQUEST,
                "invalid_review_status",
                "status must be all, pending, or reviewed.",
            )
        return status

    def _write_error(self, error: APIError, request_id: Optional[str] = None) -> None:
        request_id = request_id or self._request_id()
        self._write_json(
            {"error": error.code, "message": error.message, "request_id": request_id},
            error.status,
            request_id=request_id,
        )

    def _write_json(
        self,
        payload: Any,
        status: HTTPStatus = HTTPStatus.OK,
        *,
        request_id: Optional[str] = None,
        extra_headers: Optional[Mapping[str, str]] = None,
    ) -> None:
        body = json.dumps(payload, indent=2).encode("utf-8")
        self.send_response(status)
        self.send_header("content-type", "application/json; charset=utf-8")
        self.send_header("content-length", str(len(body)))
        self.send_header("cache-control", "no-store")
        self.send_header("x-content-type-options", "nosniff")
        self.send_header("x-request-id", request_id or self._request_id())
        origin = self.headers.get("origin")
        if origin and origin in self.server.cors_origins:
            self.send_header("access-control-allow-origin", origin)
            self.send_header("vary", "Origin")
        for name, value in (extra_headers or {}).items():
            self.send_header(name, value)
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format: str, *args: Any) -> None:
        return


def payload_hash(payload: Any) -> str:
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def parse_api_keys(value: str) -> Dict[str, str]:
    mappings: Dict[str, str] = {}
    if not value.strip():
        return mappings
    for entry in value.split(","):
        tenant, separator, key = entry.strip().partition("=")
        if separator != "=" or not tenant.strip() or not key.strip():
            raise ValueError("SMERC_API_KEYS entries must use tenant=secret format.")
        tenant = tenant.strip()
        key = key.strip()
        if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]{0,63}", tenant):
            raise ValueError("SMERC_API_KEYS tenant IDs must be 1-64 safe identifier characters.")
        if len(key) < 24:
            raise ValueError(f"SMERC_API_KEYS secret for {tenant} must contain at least 24 characters.")
        if tenant in mappings:
            raise ValueError(f"Duplicate tenant in SMERC_API_KEYS: {tenant}")
        if key in mappings.values():
            raise ValueError("Each SMERC_API_KEYS tenant must use a distinct secret.")
        mappings[tenant] = key
    return mappings


def schema() -> Dict[str, Any]:
    return {
        "api_version": "v1",
        "required_fields": [
            "action_id",
            "description",
            "actor",
            "tool",
            "action_type",
            "base_action_risk",
            "reversibility",
            "containment_strength",
            "rollback_latency",
            "evidence_validity",
            "anomaly_pressure",
            "impact_scope",
            "cancel_reliability",
            "authorization_confidence",
            "external_side_effect",
            "sensitive_data",
        ],
        "numeric_range": "0.0 to 1.0",
        "postures": [item.value for item in RuntimePosture],
        "endpoints": {
            "GET /health": "unauthenticated liveness",
            "GET /ready": "unauthenticated persistence readiness",
            "GET /schema": "input and endpoint shape",
            "POST /v1/evaluate": "evaluate and persist one action",
            "POST /v1/batch": "evaluate and persist a bounded action list",
            "GET /v1/decisions": "list tenant-scoped decision summaries",
            "GET /v1/decisions/{replay_id}": "retrieve one tenant-scoped decision",
            "POST /v1/decisions/{replay_id}/reviews": "record an immutable pilot review",
            "GET /v1/decisions/{replay_id}/reviews": "list tenant-scoped pilot reviews",
            "GET /v1/pilot/metrics": "calculate review agreement and outcome metrics",
            "GET /v1/review-queue": "list tenant-scoped pending or reviewed decisions",
        },
    }


def create_server(
    host: str,
    port: int,
    *,
    audit_db: str,
    api_keys: Mapping[str, str],
    allow_unauthenticated: bool = False,
    max_body_bytes: int = DEFAULT_MAX_BODY_BYTES,
    max_batch_size: int = DEFAULT_MAX_BATCH_SIZE,
    cors_origins: Iterable[str] = (),
) -> SMERCAPIServer:
    if not api_keys and not allow_unauthenticated:
        raise ValueError("At least one API key is required unless --allow-unauthenticated is set.")
    return SMERCAPIServer(
        (host, port),
        audit_store=AuditStore(audit_db),
        api_keys=api_keys,
        allow_unauthenticated=allow_unauthenticated,
        max_body_bytes=max_body_bytes,
        max_batch_size=max_batch_size,
        cors_origins=cors_origins,
    )


def run(
    host: str,
    port: int,
    *,
    audit_db: str,
    api_keys: Mapping[str, str],
    allow_unauthenticated: bool = False,
    max_body_bytes: int = DEFAULT_MAX_BODY_BYTES,
    max_batch_size: int = DEFAULT_MAX_BATCH_SIZE,
    cors_origins: Iterable[str] = (),
) -> None:
    server = create_server(
        host,
        port,
        audit_db=audit_db,
        api_keys=api_keys,
        allow_unauthenticated=allow_unauthenticated,
        max_body_bytes=max_body_bytes,
        max_batch_size=max_batch_size,
        cors_origins=cors_origins,
    )
    print(f"SMERC recoverability API listening on http://{host}:{server.server_address[1]}")
    try:
        server.serve_forever()
    finally:
        server.server_close()


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the SMERC recoverability API server.")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=int(os.environ.get("PORT", "8788")))
    parser.add_argument("--audit-db", default=os.environ.get("SMERC_AUDIT_DB", "smerc_audit.sqlite3"))
    parser.add_argument(
        "--allow-unauthenticated",
        action="store_true",
        help="Explicitly allow local requests without a bearer key.",
    )
    args = parser.parse_args()
    api_keys = parse_api_keys(os.environ.get("SMERC_API_KEYS", ""))
    cors_origins = [item.strip() for item in os.environ.get("SMERC_CORS_ORIGINS", "").split(",") if item.strip()]
    run(
        args.host,
        args.port,
        audit_db=args.audit_db,
        api_keys=api_keys,
        allow_unauthenticated=args.allow_unauthenticated,
        max_body_bytes=int(os.environ.get("SMERC_MAX_BODY_BYTES", str(DEFAULT_MAX_BODY_BYTES))),
        max_batch_size=int(os.environ.get("SMERC_MAX_BATCH_SIZE", str(DEFAULT_MAX_BATCH_SIZE))),
        cors_origins=cors_origins,
    )


if __name__ == "__main__":
    main()
