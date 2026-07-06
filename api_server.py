from __future__ import annotations

import argparse
import hashlib
import hmac
import json
import os
import re
import time
import uuid
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any, Dict, Iterable, Mapping, Optional
from urllib.parse import parse_qs, urlsplit

from reference_engine.audit_store import (
    AuditStore,
    FederatedTokenReplayError,
    IdempotencyConflictError,
    PermitIssuanceConflictError,
    PermitNotIssuedError,
    PermitReplayError,
    ReviewConflictError,
)
from reference_engine.action_language import ACTION_VERSION, DECISION_VERSION, action_hash, evaluate_language_action
from reference_engine.access_token import (
    ACCESS_TOKEN_VERSION,
    AccessTokenError,
    AccessTokenSigner,
    parse_access_token_signer,
)
from reference_engine.api_identity import (
    PRINCIPAL_VERSION,
    APIPrincipal,
    PrincipalRegistry,
    parse_scoped_principals,
)
from reference_engine.authorization_permit import (
    PERMIT_VERSION,
    PermitError,
    PermitSigner,
    parse_permit_signers,
)
from reference_engine.control_evidence import (
    CONTROL_EVIDENCE_VERSION,
    ControlEvidenceError,
    ControlEvidenceSigner,
    parse_control_evidence_signers,
)
from reference_engine.github_oidc import (
    GITHUB_OIDC_VERSION,
    GitHubOIDCError,
    GitHubOIDCVerifier,
    parse_github_oidc_trust,
)
from reference_engine.policy import POLICY_VERSION, PolicyRegistry
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
        api_principals: Iterable[APIPrincipal] = (),
        allow_unauthenticated: bool = False,
        max_body_bytes: int = DEFAULT_MAX_BODY_BYTES,
        max_batch_size: int = DEFAULT_MAX_BATCH_SIZE,
        cors_origins: Iterable[str] = (),
        policy_registry: Optional[PolicyRegistry] = None,
        permit_signers: Optional[Mapping[str, PermitSigner]] = None,
        control_evidence_signers: Optional[Mapping[tuple[str, str], ControlEvidenceSigner]] = None,
        access_token_signer: Optional[AccessTokenSigner] = None,
        github_oidc_verifier: Optional[GitHubOIDCVerifier] = None,
    ) -> None:
        resolved_policy_registry = policy_registry or PolicyRegistry()
        principal_registry = PrincipalRegistry.from_configuration(api_keys, api_principals)
        resolved_permit_signers = dict(permit_signers or {})
        resolved_control_evidence_signers = dict(control_evidence_signers or {})
        if github_oidc_verifier is not None and access_token_signer is None:
            raise ValueError("GitHub OIDC exchange requires an access-token signing key.")
        if access_token_signer is not None and principal_registry.uses_secret_bytes(
            access_token_signer.secret
        ):
            raise ValueError("Access-token signing key must be distinct from API principal secrets.")
        if access_token_signer is not None and any(
            hmac.compare_digest(access_token_signer.secret, signer.secret)
            for signer in resolved_permit_signers.values()
        ):
            raise ValueError("Access-token signing key must be distinct from permit signing keys.")
        if access_token_signer is not None and any(
            hmac.compare_digest(access_token_signer.secret, signer.secret)
            for signer in resolved_control_evidence_signers.values()
        ):
            raise ValueError("Access-token signing key must be distinct from control-evidence signing keys.")
        for binding, signer in resolved_control_evidence_signers.items():
            if binding != (signer.tenant_id, signer.audience):
                raise ValueError("Control-evidence signer mapping must match its tenant and audience.")
        unknown_permit_tenants = sorted(set(resolved_permit_signers) - set(principal_registry.tenant_ids))
        if unknown_permit_tenants and not allow_unauthenticated:
            raise ValueError(
                "Permit signing tenants must also have API credentials: "
                + ", ".join(unknown_permit_tenants)
            )
        unknown_evidence_tenants = sorted(
            {tenant_id for tenant_id, _ in resolved_control_evidence_signers}
            - set(principal_registry.tenant_ids)
        )
        if unknown_evidence_tenants and not allow_unauthenticated:
            raise ValueError(
                "Control-evidence tenants must also have API credentials: "
                + ", ".join(unknown_evidence_tenants)
            )
        evidence_without_permits = sorted(
            {tenant_id for tenant_id, _ in resolved_control_evidence_signers}
            - set(resolved_permit_signers)
        )
        if evidence_without_permits:
            raise ValueError(
                "Control-evidence tenants must also have permit signing keys: "
                + ", ".join(evidence_without_permits)
            )
        for tenant_id in principal_registry.tenant_ids:
            resolved_policy_registry.for_tenant(tenant_id)
        if github_oidc_verifier is not None:
            for tenant_id in github_oidc_verifier.tenant_ids:
                resolved_policy_registry.for_tenant(tenant_id)

        super().__init__(server_address, SMERCRequestHandler)
        self.policy_registry = resolved_policy_registry
        self.audit_store = audit_store
        self.api_keys = dict(api_keys)
        self.principal_registry = principal_registry
        self.allow_unauthenticated = allow_unauthenticated
        self.max_body_bytes = max_body_bytes
        self.max_batch_size = max_batch_size
        self.cors_origins = frozenset(cors_origins)
        self.permit_signers = resolved_permit_signers
        self.control_evidence_signers = resolved_control_evidence_signers
        self.access_token_signer = access_token_signer
        self.github_oidc_verifier = github_oidc_verifier

    def engine_for(self, tenant_id: str) -> RecoverabilityEngine:
        return RecoverabilityEngine(self.policy_registry.for_tenant(tenant_id))

    def signer_for(self, tenant_id: str) -> PermitSigner:
        signer = self.permit_signers.get(tenant_id)
        if signer is None:
            raise APIError(
                HTTPStatus.SERVICE_UNAVAILABLE,
                "permit_signing_unavailable",
                "No permit signing key is configured for this tenant.",
            )
        return signer

    def control_evidence_signer_for(
        self,
        tenant_id: str,
        audience: str,
    ) -> Optional[ControlEvidenceSigner]:
        return self.control_evidence_signers.get((tenant_id, audience))

    def server_close(self) -> None:
        super().server_close()
        self.audit_store.close()


class SMERCRequestHandler(BaseHTTPRequestHandler):
    server: SMERCAPIServer
    server_version = "SMERCRecoverabilityAPI/0.12"

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
                        "version": "0.12",
                        "tenant_policy_count": self.server.policy_registry.count,
                        "permit_signer_count": len(self.server.permit_signers),
                        "api_principal_count": self.server.principal_registry.count,
                        "control_evidence_adapter_count": len(self.server.control_evidence_signers),
                        "short_lived_access_enabled": self.server.access_token_signer is not None,
                        "github_oidc_enabled": self.server.github_oidc_verifier is not None,
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

            if path == "/v1/pilot/metrics":
                required_scope = "metrics.read"
            elif path == "/v1/security-events":
                required_scope = "audit.read"
            elif self._review_replay_id(path) is not None:
                required_scope = "reviews.read"
            else:
                required_scope = "decisions.read"
            principal = self._authenticate(required_scope)
            tenant_id = principal.tenant_id
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
            if path == "/v1/security-events":
                limit = self._parse_limit(query)
                events = self.server.audit_store.list_security_events(tenant_id, limit=limit)
                self._write_json(
                    {
                        "tenant_id": tenant_id,
                        "count": len(events),
                        "events": events,
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
            if path == "/v1/auth/token":
                principal = self._authenticate_static()
                payload = self._read_json()
                if not isinstance(payload, dict):
                    raise APIError(
                        HTTPStatus.BAD_REQUEST,
                        "invalid_access_token_request",
                        "Access-token exchange expects one JSON object.",
                    )
                self._write_json(
                    self._issue_access_token(principal, payload),
                    HTTPStatus.CREATED,
                    request_id=request_id,
                )
                return
            if path == "/v1/auth/github":
                payload = self._read_json()
                if not isinstance(payload, dict):
                    raise APIError(
                        HTTPStatus.BAD_REQUEST,
                        "invalid_github_oidc_request",
                        "GitHub OIDC exchange expects one JSON object.",
                    )
                self._write_json(
                    self._exchange_github_oidc(self._bearer_candidate(), payload),
                    HTTPStatus.CREATED,
                    request_id=request_id,
                )
                return
            principal = self._authenticate(self._post_scope(path))
            tenant_id = principal.tenant_id
            payload = self._read_json()

            if path == "/v1/permits/issue":
                if not isinstance(payload, dict):
                    raise APIError(HTTPStatus.BAD_REQUEST, "invalid_payload", "Permit issuance expects one JSON object.")
                self._write_json(
                    self._issue_permit(principal, payload),
                    HTTPStatus.CREATED,
                    request_id=request_id,
                )
                return
            if path == "/v1/permits/consume":
                if not isinstance(payload, dict):
                    raise APIError(HTTPStatus.BAD_REQUEST, "invalid_payload", "Permit consumption expects one JSON object.")
                self._write_json(self._consume_permit(principal, payload), request_id=request_id)
                return

            review_replay_id = self._review_replay_id(path)
            if review_replay_id is not None:
                if not isinstance(payload, dict):
                    raise APIError(HTTPStatus.BAD_REQUEST, "invalid_payload", "Review expects one JSON object.")
                result, replayed = self._record_review(principal, review_replay_id, payload)
                headers = {"x-smerc-idempotent-replay": "true"} if replayed else None
                self._write_json(
                    result,
                    HTTPStatus.OK if replayed else HTTPStatus.CREATED,
                    request_id=request_id,
                    extra_headers=headers,
                )
                return

            if path not in {"/evaluate", "/batch", "/v1/evaluate", "/v1/batch", "/v1/language/evaluate"}:
                raise APIError(HTTPStatus.NOT_FOUND, "not_found", "Use /evaluate, /batch, or a review endpoint.")

            if path == "/v1/language/evaluate":
                if not isinstance(payload, dict):
                    raise APIError(HTTPStatus.BAD_REQUEST, "invalid_payload", "Language evaluation expects one JSON object.")
                result, replayed = self._evaluate_language_one(principal, payload)
                headers = {"x-smerc-idempotent-replay": "true"} if replayed else None
                self._write_json(result, request_id=request_id, extra_headers=headers)
                return

            if path in {"/evaluate", "/v1/evaluate"}:
                if not isinstance(payload, dict):
                    raise APIError(HTTPStatus.BAD_REQUEST, "invalid_payload", "/evaluate expects one JSON object.")
                result, replayed = self._evaluate_one(principal, payload)
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
            results = [self._evaluate_and_record(principal, item) for item in payload]
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

    def _issue_access_token(
        self,
        principal: APIPrincipal,
        payload: Dict[str, Any],
    ) -> Dict[str, Any]:
        signer = self.server.access_token_signer
        if signer is None:
            raise APIError(
                HTTPStatus.SERVICE_UNAVAILABLE,
                "access_token_exchange_unavailable",
                "Short-lived access-token exchange is not configured.",
            )
        if set(payload) - {"scopes", "ttl_seconds"}:
            raise APIError(
                HTTPStatus.BAD_REQUEST,
                "invalid_access_token_request",
                "Access-token request fields are unknown.",
            )
        scopes = payload.get("scopes")
        if scopes is not None and not isinstance(scopes, list):
            raise APIError(
                HTTPStatus.BAD_REQUEST,
                "invalid_access_token_request",
                "scopes must be a list when supplied.",
            )
        try:
            issued = signer.issue(
                principal,
                requested_scopes=scopes,
                ttl_seconds=payload.get("ttl_seconds", 300),
            )
        except AccessTokenError as exc:
            raise APIError(HTTPStatus.BAD_REQUEST, exc.code, exc.message) from exc
        session = issued["session"]
        self.server.audit_store.record_security_event(
            principal.tenant_id,
            principal.principal_id,
            "access_token.issued",
            session["session_id"],
            {
                "scopes": session["scopes"],
                "issued_at": session["issued_at"],
                "expires_at": session["expires_at"],
                "source_legacy": session["source_legacy"],
                "key_id": signer.key_id,
            },
        )
        return issued

    def _exchange_github_oidc(
        self,
        token: str,
        payload: Dict[str, Any],
    ) -> Dict[str, Any]:
        verifier = self.server.github_oidc_verifier
        signer = self.server.access_token_signer
        if verifier is None or signer is None:
            raise APIError(
                HTTPStatus.SERVICE_UNAVAILABLE,
                "github_oidc_exchange_unavailable",
                "GitHub OIDC exchange is not configured.",
            )
        if set(payload) - {"scopes", "ttl_seconds"}:
            raise APIError(
                HTTPStatus.BAD_REQUEST,
                "invalid_github_oidc_request",
                "GitHub OIDC exchange request fields are unknown.",
            )
        scopes = payload.get("scopes")
        if scopes is not None and not isinstance(scopes, list):
            raise APIError(
                HTTPStatus.BAD_REQUEST,
                "invalid_github_oidc_request",
                "scopes must be a list when supplied.",
            )
        try:
            workload = verifier.verify(token)
        except GitHubOIDCError as exc:
            if exc.code == "github_oidc_trust_denied":
                status = HTTPStatus.FORBIDDEN
            elif exc.code == "github_oidc_jwks_unavailable":
                status = HTTPStatus.SERVICE_UNAVAILABLE
            else:
                status = HTTPStatus.UNAUTHORIZED
            raise APIError(status, exc.code, exc.message) from exc
        requested_ttl = payload.get("ttl_seconds", 300)
        if isinstance(requested_ttl, bool) or not isinstance(requested_ttl, int):
            raise APIError(
                HTTPStatus.BAD_REQUEST,
                "invalid_access_token_ttl",
                "ttl_seconds must be an integer.",
            )
        issued_at = int(time.time())
        remaining_identity_lifetime = workload.expires_at - issued_at
        if remaining_identity_lifetime < 1:
            raise APIError(
                HTTPStatus.UNAUTHORIZED,
                "github_oidc_expired",
                "GitHub OIDC token has no remaining exchange lifetime.",
            )
        try:
            issued = signer.issue(
                workload.principal,
                requested_scopes=scopes,
                ttl_seconds=min(requested_ttl, remaining_identity_lifetime),
                now=issued_at,
            )
        except AccessTokenError as exc:
            raise APIError(HTTPStatus.BAD_REQUEST, exc.code, exc.message) from exc
        session = issued["session"]
        try:
            self.server.audit_store.register_github_oidc_exchange(
                workload.principal.tenant_id,
                workload.principal.principal_id,
                hashlib.sha256(workload.token_id.encode("utf-8")).hexdigest(),
                workload.token_hash,
                session,
                dict(workload.principal.workload_context or {}),
            )
        except FederatedTokenReplayError as exc:
            raise APIError(HTTPStatus.CONFLICT, "github_oidc_replay", str(exc)) from exc
        return issued

    def _issue_permit(self, principal: APIPrincipal, payload: Dict[str, Any]) -> Dict[str, Any]:
        tenant_id = principal.tenant_id
        allowed = {"replay_id", "action", "audience", "ttl_seconds"}
        unknown = sorted(set(payload) - allowed)
        missing = sorted({"replay_id", "action", "audience"} - set(payload))
        if missing or unknown:
            raise APIError(
                HTTPStatus.BAD_REQUEST,
                "invalid_permit_request",
                "Permit request fields are incomplete or unknown.",
            )
        replay_id = payload["replay_id"]
        if not isinstance(replay_id, str):
            raise APIError(HTTPStatus.BAD_REQUEST, "invalid_permit_request", "replay_id must be a string.")
        action = payload["action"]
        if not isinstance(action, dict):
            raise APIError(HTTPStatus.BAD_REQUEST, "invalid_permit_request", "action must be an Action Language object.")
        decision = self.server.audit_store.get(tenant_id, replay_id)
        if decision is None:
            raise APIError(HTTPStatus.NOT_FOUND, "decision_not_found", "Decision was not found.")
        current_policy = self.server.policy_registry.for_tenant(tenant_id)
        if decision.get("policy", {}).get("policy_hash") != current_policy.policy_hash:
            raise APIError(
                HTTPStatus.CONFLICT,
                "policy_superseded",
                "Decision policy is no longer the active tenant policy.",
            )
        try:
            issued = self.server.signer_for(tenant_id).issue(
                decision,
                action,
                tenant_id=tenant_id,
                audience=payload["audience"],
                ttl_seconds=payload.get("ttl_seconds", 60),
            )
        except PermitError as exc:
            raise APIError(HTTPStatus.BAD_REQUEST, exc.code, exc.message) from exc
        try:
            issued["issuance"] = self.server.audit_store.record_permit_issuance(
                tenant_id,
                issued["permit"],
                hashlib.sha256(issued["permit_token"].encode("ascii")).hexdigest(),
            )
        except PermitIssuanceConflictError as exc:
            raise APIError(HTTPStatus.CONFLICT, "permit_already_issued", str(exc)) from exc
        self.server.audit_store.record_security_event(
            tenant_id,
            principal.principal_id,
            "permit.issued",
            issued["permit"]["permit_id"],
            {
                "replay_id": issued["permit"]["replay_id"],
                "audience": issued["permit"]["audience"],
                "posture": issued["permit"]["posture"],
                "policy_hash": issued["permit"]["policy"]["policy_hash"],
                "expires_at": issued["permit"]["expires_at"],
            },
        )
        return issued

    def _consume_permit(self, principal: APIPrincipal, payload: Dict[str, Any]) -> Dict[str, Any]:
        tenant_id = principal.tenant_id
        common_fields = {"permit_token", "action", "audience"}
        if not isinstance(payload.get("audience"), str):
            raise APIError(HTTPStatus.BAD_REQUEST, "invalid_permit_request", "audience must be a string.")
        evidence_signer = self.server.control_evidence_signer_for(tenant_id, payload["audience"])
        evidence_fields = common_fields | {"control_evidence_token"}
        legacy_fields = common_fields | {"enforced_controls"}
        expected_fields = evidence_fields if evidence_signer is not None else legacy_fields
        if set(payload) != expected_fields:
            code = "control_evidence_required" if evidence_signer is not None else "invalid_permit_request"
            raise APIError(
                HTTPStatus.BAD_REQUEST,
                code,
                "Signed control_evidence_token is required for this tenant and executor audience."
                if evidence_signer is not None
                else "Permit consumption fields are incomplete or unknown.",
            )
        if not isinstance(payload["action"], dict):
            raise APIError(
                HTTPStatus.BAD_REQUEST,
                "invalid_permit_request",
                "action must be an object.",
            )
        if evidence_signer is not None:
            if not isinstance(payload["control_evidence_token"], str):
                raise APIError(
                    HTTPStatus.BAD_REQUEST,
                    "invalid_control_evidence",
                    "control_evidence_token must be a string.",
                )
            try:
                evidence = evidence_signer.verify(
                    payload["control_evidence_token"],
                    tenant_id=tenant_id,
                    audience=payload["audience"],
                    action_hash=action_hash(payload["action"]),
                )
            except (ControlEvidenceError, TypeError, ValueError) as exc:
                if isinstance(exc, ControlEvidenceError):
                    raise APIError(HTTPStatus.BAD_REQUEST, exc.code, exc.message) from exc
                raise APIError(HTTPStatus.BAD_REQUEST, "invalid_control_evidence", str(exc)) from exc
            enforced_controls = evidence_signer.applied_controls(evidence)
            evidence_summary = {
                "mode": "signed_adapter_receipt",
                "version": evidence["version"],
                "evidence_id": evidence["evidence_id"],
                "adapter_id": evidence["adapter_id"],
                "key_id": evidence_signer.key_id,
                "controls": enforced_controls,
                "expires_at": evidence["expires_at"],
                "token_sha256": hashlib.sha256(
                    payload["control_evidence_token"].encode("ascii")
                ).hexdigest(),
            }
        else:
            if not isinstance(payload["enforced_controls"], list):
                raise APIError(
                    HTTPStatus.BAD_REQUEST,
                    "invalid_permit_request",
                    "enforced_controls must be a list.",
                )
            enforced_controls = payload["enforced_controls"]
            evidence = None
            evidence_summary = {
                "mode": "legacy_caller_assertion",
                "controls": sorted(enforced_controls),
            }
        try:
            permit = self.server.signer_for(tenant_id).verify(
                payload["permit_token"],
                payload["action"],
                tenant_id=tenant_id,
                audience=payload["audience"],
                enforced_controls=enforced_controls,
            )
        except PermitError as exc:
            raise APIError(HTTPStatus.BAD_REQUEST, exc.code, exc.message) from exc
        if evidence is not None and evidence["permit_id"] != permit["permit_id"]:
            raise APIError(
                HTTPStatus.BAD_REQUEST,
                "control_evidence_permit_mismatch",
                "Control evidence is not bound to this permit.",
            )

        decision = self.server.audit_store.get(tenant_id, permit["replay_id"])
        if decision is None:
            raise APIError(HTTPStatus.NOT_FOUND, "decision_not_found", "Permit decision was not found.")
        if (
            decision.get("action_hash") != permit["action_hash"]
            or decision.get("posture") != permit["posture"]
            or decision.get("policy", {}).get("policy_hash") != permit["policy"]["policy_hash"]
        ):
            raise APIError(
                HTTPStatus.CONFLICT,
                "permit_decision_mismatch",
                "Permit no longer agrees with its stored decision.",
            )
        current_policy = self.server.policy_registry.for_tenant(tenant_id)
        if current_policy.policy_hash != permit["policy"]["policy_hash"]:
            raise APIError(
                HTTPStatus.CONFLICT,
                "policy_superseded",
                "Permit policy is no longer the active tenant policy.",
            )
        try:
            consumption = self.server.audit_store.consume_permit(
                tenant_id,
                permit,
                enforced_controls,
                hashlib.sha256(payload["permit_token"].encode("ascii")).hexdigest(),
            )
        except PermitNotIssuedError as exc:
            raise APIError(HTTPStatus.CONFLICT, "permit_not_issued", str(exc)) from exc
        except PermitReplayError as exc:
            raise APIError(HTTPStatus.CONFLICT, "permit_already_consumed", str(exc)) from exc
        self.server.audit_store.record_security_event(
            tenant_id,
            principal.principal_id,
            "permit.consumed",
            permit["permit_id"],
            {
                "replay_id": permit["replay_id"],
                "audience": permit["audience"],
                "enforced_controls": sorted(enforced_controls),
                "control_evidence": evidence_summary,
            },
        )
        return {
            "valid": True,
            "permit": permit,
            "consumption": consumption,
            "control_evidence": evidence_summary,
        }

    def _record_review(
        self,
        principal: APIPrincipal,
        replay_id: str,
        payload: Dict[str, Any],
    ) -> tuple[Dict[str, Any], bool]:
        tenant_id = principal.tenant_id
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
                stored_principal = stored["review"].get("authenticated_principal", {}).get("principal_id")
                if stored_principal != principal.principal_id:
                    raise APIError(
                        HTTPStatus.CONFLICT,
                        "idempotency_principal_conflict",
                        "Idempotency-Key belongs to a different authenticated principal.",
                    )
                return stored["review"], True

        review = self._validate_review(payload, decision["posture"])
        review.update(
            {
                "review_id": str(uuid.uuid4()),
                "tenant_id": tenant_id,
                "replay_id": replay_id,
                "decision_posture": decision["posture"],
                "authenticated_principal": principal.public_identity(),
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
        self.server.audit_store.record_security_event(
            tenant_id,
            principal.principal_id,
            "review.recorded",
            stored_review["review_id"],
            {
                "replay_id": replay_id,
                "verdict": stored_review["verdict"],
                "reviewer_alias": stored_review["reviewer_id"],
            },
        )
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

    def _evaluate_one(self, principal: APIPrincipal, payload: Dict[str, Any]) -> tuple[Dict[str, Any], bool]:
        tenant_id = principal.tenant_id
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
                self._require_same_principal(stored["decision"], principal)
                return stored["decision"], True
        return self._evaluate_and_record(principal, payload, request_hash, idempotency_key), False

    def _evaluate_language_one(
        self,
        principal: APIPrincipal,
        payload: Dict[str, Any],
    ) -> tuple[Dict[str, Any], bool]:
        tenant_id = principal.tenant_id
        request_hash = payload_hash({"endpoint": "/v1/language/evaluate", "payload": payload})
        idempotency_key = self._idempotency_key()
        if idempotency_key is not None:
            stored = self.server.audit_store.get_by_idempotency_key(tenant_id, idempotency_key)
            if stored is not None:
                if not hmac.compare_digest(stored["request_hash"], request_hash):
                    raise APIError(
                        HTTPStatus.CONFLICT,
                        "idempotency_conflict",
                        "Idempotency-Key was already used with a different request body or endpoint.",
                    )
                self._require_same_principal(stored["decision"], principal)
                return stored["decision"], True
        decision = evaluate_language_action(payload, self.server.engine_for(tenant_id))
        decision["tenant_id"] = tenant_id
        self._bind_principal(decision, principal)
        try:
            stored = self.server.audit_store.record(
                tenant_id, decision, request_hash, idempotency_key=idempotency_key
            )
        except IdempotencyConflictError as exc:
            raise APIError(HTTPStatus.CONFLICT, "idempotency_conflict", str(exc)) from exc
        return stored, False

    def _evaluate_and_record(
        self,
        principal: APIPrincipal,
        payload: Dict[str, Any],
        request_hash: Optional[str] = None,
        idempotency_key: Optional[str] = None,
    ) -> Dict[str, Any]:
        tenant_id = principal.tenant_id
        if not isinstance(payload, dict):
            raise TypeError("Each action must be a JSON object.")
        decision = self.server.engine_for(tenant_id).evaluate(payload)
        decision["tenant_id"] = tenant_id
        self._bind_principal(decision, principal)
        try:
            return self.server.audit_store.record(
                tenant_id,
                decision,
                request_hash or payload_hash(payload),
                idempotency_key=idempotency_key,
            )
        except IdempotencyConflictError as exc:
            raise APIError(HTTPStatus.CONFLICT, "idempotency_conflict", str(exc)) from exc

    @staticmethod
    def _bind_principal(decision: Dict[str, Any], principal: APIPrincipal) -> None:
        identity = principal.public_identity()
        decision["authenticated_principal"] = identity
        decision["replay"]["authenticated_principal"] = identity

    @staticmethod
    def _require_same_principal(decision: Dict[str, Any], principal: APIPrincipal) -> None:
        stored_principal = decision.get("authenticated_principal", {}).get("principal_id")
        if stored_principal != principal.principal_id:
            raise APIError(
                HTTPStatus.CONFLICT,
                "idempotency_principal_conflict",
                "Idempotency-Key belongs to a different authenticated principal.",
            )

    def _authenticate(self, required_scope: Optional[str] = None) -> APIPrincipal:
        if self.server.allow_unauthenticated:
            tenant = self.headers.get("x-smerc-tenant", "local-development").strip()
            tenant = tenant or "local-development"
            return APIPrincipal(
                tenant_id=tenant,
                principal_id="local-development",
                secret="local-development-only-secret",
                scopes=frozenset({"*"}),
                legacy=True,
                credential_type="local_development",
            )

        candidate = self._bearer_candidate()
        principal = self.server.principal_registry.authenticate(candidate)
        if principal is None and self.server.access_token_signer is not None:
            try:
                principal = self.server.access_token_signer.verify(candidate)
            except AccessTokenError as exc:
                raise APIError(HTTPStatus.UNAUTHORIZED, exc.code, exc.message) from exc
        if principal is None:
            raise APIError(HTTPStatus.UNAUTHORIZED, "invalid_api_key", "Bearer credential is invalid.")
        return self._authorize_principal(principal, required_scope)

    def _authenticate_static(self) -> APIPrincipal:
        candidate = self._bearer_candidate()
        principal = self.server.principal_registry.authenticate(candidate)
        if principal is None:
            raise APIError(
                HTTPStatus.UNAUTHORIZED,
                "invalid_bootstrap_credential",
                "A configured static bootstrap credential is required for token exchange.",
            )
        return self._authorize_principal(principal)

    def _bearer_candidate(self) -> str:
        authorization = self.headers.get("authorization", "")
        scheme, separator, candidate = authorization.partition(" ")
        if separator != " " or scheme.lower() != "bearer" or not candidate:
            raise APIError(HTTPStatus.UNAUTHORIZED, "authentication_required", "Bearer authentication is required.")
        return candidate

    def _authorize_principal(
        self,
        principal: APIPrincipal,
        required_scope: Optional[str] = None,
    ) -> APIPrincipal:
        requested_tenant = self.headers.get("x-smerc-tenant")
        if requested_tenant and not hmac.compare_digest(requested_tenant.strip(), principal.tenant_id):
            raise APIError(HTTPStatus.FORBIDDEN, "tenant_mismatch", "Bearer credential is not valid for that tenant.")
        if required_scope is not None and not principal.permits(required_scope):
            raise APIError(
                HTTPStatus.FORBIDDEN,
                "insufficient_scope",
                f"Authenticated principal requires scope {required_scope} for this operation.",
            )
        return principal

    @staticmethod
    def _post_scope(path: str) -> Optional[str]:
        if path == "/v1/permits/issue":
            return "permits.issue"
        if path == "/v1/permits/consume":
            return "permits.consume"
        if re.fullmatch(r"/v1/decisions/[^/]+/reviews", path):
            return "reviews.write"
        if path in {"/evaluate", "/batch", "/v1/evaluate", "/v1/batch", "/v1/language/evaluate"}:
            return "actions.evaluate"
        return None

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
        "language_versions": {
            "action": ACTION_VERSION,
            "decision": DECISION_VERSION,
            "permit": PERMIT_VERSION,
            "control_evidence": CONTROL_EVIDENCE_VERSION,
            "access_token": ACCESS_TOKEN_VERSION,
            "github_oidc": GITHUB_OIDC_VERSION,
        },
        "policy_version": POLICY_VERSION,
        "principal_version": PRINCIPAL_VERSION,
        "security_event_version": "smerc.security-event.v1",
        "authorization": {
            "legacy_keys": "all tenant scopes",
            "scoped_principals_env": "SMERC_API_PRINCIPALS",
            "scopes": [
                "actions.evaluate",
                "decisions.read",
                "permits.issue",
                "permits.consume",
                "reviews.read",
                "reviews.write",
                "metrics.read",
                "audit.read",
            ],
        },
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
            "POST /v1/auth/token": "exchange a static bootstrap credential for a short-lived narrowed token",
            "POST /v1/auth/github": "exchange one verified GitHub Actions OIDC token for a workload-bound session",
            "POST /v1/language/evaluate": "validate, compile, evaluate, and persist one Action Language envelope",
            "POST /v1/permits/issue": "issue a short-lived action-bound permit for an enforceable decision",
            "POST /v1/permits/consume": "verify control evidence and atomically consume an action-bound permit",
            "POST /v1/batch": "evaluate and persist a bounded action list",
            "GET /v1/decisions": "list tenant-scoped decision summaries",
            "GET /v1/decisions/{replay_id}": "retrieve one tenant-scoped decision",
            "POST /v1/decisions/{replay_id}/reviews": "record an immutable pilot review",
            "GET /v1/decisions/{replay_id}/reviews": "list tenant-scoped pilot reviews",
            "GET /v1/pilot/metrics": "calculate review agreement and outcome metrics",
            "GET /v1/review-queue": "list tenant-scoped pending or reviewed decisions",
            "GET /v1/security-events": "list tenant-scoped authenticated security events",
        },
    }


def create_server(
    host: str,
    port: int,
    *,
    audit_db: str,
    api_keys: Mapping[str, str],
    api_principals: Iterable[APIPrincipal] = (),
    allow_unauthenticated: bool = False,
    max_body_bytes: int = DEFAULT_MAX_BODY_BYTES,
    max_batch_size: int = DEFAULT_MAX_BATCH_SIZE,
    cors_origins: Iterable[str] = (),
    policy_registry: Optional[PolicyRegistry] = None,
    permit_signers: Optional[Mapping[str, PermitSigner]] = None,
    control_evidence_signers: Optional[Mapping[tuple[str, str], ControlEvidenceSigner]] = None,
    access_token_signer: Optional[AccessTokenSigner] = None,
    github_oidc_verifier: Optional[GitHubOIDCVerifier] = None,
) -> SMERCAPIServer:
    api_principals = tuple(api_principals)
    if not api_keys and not api_principals and github_oidc_verifier is None and not allow_unauthenticated:
        raise ValueError(
            "At least one API credential or GitHub OIDC trust policy is required unless "
            "--allow-unauthenticated is set."
        )
    audit_store = AuditStore(audit_db)
    try:
        return SMERCAPIServer(
            (host, port),
            audit_store=audit_store,
            api_keys=api_keys,
            api_principals=api_principals,
            allow_unauthenticated=allow_unauthenticated,
            max_body_bytes=max_body_bytes,
            max_batch_size=max_batch_size,
            cors_origins=cors_origins,
            policy_registry=policy_registry,
            permit_signers=permit_signers,
            control_evidence_signers=control_evidence_signers,
            access_token_signer=access_token_signer,
            github_oidc_verifier=github_oidc_verifier,
        )
    except Exception:
        audit_store.close()
        raise


def run(
    host: str,
    port: int,
    *,
    audit_db: str,
    api_keys: Mapping[str, str],
    api_principals: Iterable[APIPrincipal] = (),
    allow_unauthenticated: bool = False,
    max_body_bytes: int = DEFAULT_MAX_BODY_BYTES,
    max_batch_size: int = DEFAULT_MAX_BATCH_SIZE,
    cors_origins: Iterable[str] = (),
    policy_registry: Optional[PolicyRegistry] = None,
    permit_signers: Optional[Mapping[str, PermitSigner]] = None,
    control_evidence_signers: Optional[Mapping[tuple[str, str], ControlEvidenceSigner]] = None,
    access_token_signer: Optional[AccessTokenSigner] = None,
    github_oidc_verifier: Optional[GitHubOIDCVerifier] = None,
) -> None:
    server = create_server(
        host,
        port,
        audit_db=audit_db,
        api_keys=api_keys,
        api_principals=api_principals,
        allow_unauthenticated=allow_unauthenticated,
        max_body_bytes=max_body_bytes,
        max_batch_size=max_batch_size,
        cors_origins=cors_origins,
        policy_registry=policy_registry,
        permit_signers=permit_signers,
        control_evidence_signers=control_evidence_signers,
        access_token_signer=access_token_signer,
        github_oidc_verifier=github_oidc_verifier,
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
    parser.add_argument("--policy-dir", default=os.environ.get("SMERC_POLICY_DIR"))
    parser.add_argument(
        "--allow-unauthenticated",
        action="store_true",
        help="Explicitly allow local requests without a bearer key.",
    )
    args = parser.parse_args()
    api_keys = parse_api_keys(os.environ.get("SMERC_API_KEYS", ""))
    api_principals = parse_scoped_principals(os.environ.get("SMERC_API_PRINCIPALS", ""))
    cors_origins = [item.strip() for item in os.environ.get("SMERC_CORS_ORIGINS", "").split(",") if item.strip()]
    policy_registry = PolicyRegistry.from_directory(args.policy_dir) if args.policy_dir else PolicyRegistry()
    permit_signers = parse_permit_signers(os.environ.get("SMERC_PERMIT_KEYS", ""))
    control_evidence_signers = parse_control_evidence_signers(
        os.environ.get("SMERC_CONTROL_EVIDENCE_KEYS", "")
    )
    access_token_signer = parse_access_token_signer(
        os.environ.get("SMERC_ACCESS_TOKEN_KEY", "")
    )
    github_oidc_policies = parse_github_oidc_trust(
        os.environ.get("SMERC_GITHUB_OIDC_TRUST", "")
    )
    github_oidc_verifier = (
        GitHubOIDCVerifier(github_oidc_policies) if github_oidc_policies else None
    )
    run(
        args.host,
        args.port,
        audit_db=args.audit_db,
        api_keys=api_keys,
        api_principals=api_principals,
        allow_unauthenticated=args.allow_unauthenticated,
        max_body_bytes=int(os.environ.get("SMERC_MAX_BODY_BYTES", str(DEFAULT_MAX_BODY_BYTES))),
        max_batch_size=int(os.environ.get("SMERC_MAX_BATCH_SIZE", str(DEFAULT_MAX_BATCH_SIZE))),
        cors_origins=cors_origins,
        policy_registry=policy_registry,
        permit_signers=permit_signers,
        control_evidence_signers=control_evidence_signers,
        access_token_signer=access_token_signer,
        github_oidc_verifier=github_oidc_verifier,
    )


if __name__ == "__main__":
    main()
