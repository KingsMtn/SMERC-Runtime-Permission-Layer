from __future__ import annotations

import hmac
import re
from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Dict, Iterable, Mapping, Optional


SCOPES = frozenset(
    {
        "actions.evaluate",
        "routes.write",
        "decisions.read",
        "permits.issue",
        "permits.consume",
        "reviews.read",
        "reviews.write",
        "metrics.read",
        "audit.read",
    }
)
ALL_SCOPES = "*"
PRINCIPAL_VERSION = "smerc.principal.v1"
WORKLOAD_CONTEXT_FIELDS = frozenset(
    {
        "provider", "subject", "repository", "repository_id",
        "repository_owner_id", "workflow_ref", "workflow_sha", "ref",
        "commit_sha", "run_id", "run_attempt", "actor_id", "event_name",
        "runner_environment", "environment", "job_workflow_ref", "token_id",
    }
)
REQUIRED_WORKLOAD_CONTEXT_FIELDS = frozenset(
    {
        "provider", "subject", "repository", "repository_id",
        "repository_owner_id", "workflow_ref", "workflow_sha", "ref",
        "commit_sha", "run_id", "run_attempt", "actor_id", "event_name",
        "runner_environment", "token_id",
    }
)


def _identifier(value: str, path: str) -> str:
    if not isinstance(value, str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]{0,63}", value):
        raise ValueError(f"{path} must be a safe identifier of 1 to 64 characters.")
    return value


@dataclass(frozen=True)
class APIPrincipal:
    tenant_id: str
    principal_id: str
    secret: str = field(repr=False)
    scopes: frozenset[str]
    legacy: bool = False
    credential_type: str = "static_bearer"
    session_id: Optional[str] = None
    expires_at: Optional[int] = None
    workload_context: Optional[Mapping[str, str]] = None

    def __post_init__(self) -> None:
        _identifier(self.tenant_id, "principal tenant")
        _identifier(self.principal_id, "principal ID")
        if not isinstance(self.secret, str) or len(self.secret) < 8:
            raise ValueError("Programmatic principal secrets must contain at least 8 characters.")
        if not self.scopes:
            raise ValueError("Principal must have at least one scope.")
        unknown = set(self.scopes) - SCOPES - {ALL_SCOPES}
        if unknown or (ALL_SCOPES in self.scopes and len(self.scopes) != 1):
            raise ValueError("Principal contains an unknown or incoherent scope set.")
        if self.credential_type not in {
            "static_bearer", "short_lived_access_token", "local_development"
        }:
            raise ValueError("Principal credential_type is not recognized.")
        is_session = self.credential_type == "short_lived_access_token"
        if is_session and (self.session_id is None or self.expires_at is None):
            raise ValueError("Short-lived principal session metadata is incomplete or incoherent.")
        if not is_session and (self.session_id is not None or self.expires_at is not None):
            raise ValueError("Non-session principals cannot carry session metadata.")
        if self.session_id is not None and not re.fullmatch(r"session_[0-9a-f]{32}", self.session_id):
            raise ValueError("Principal session_id is invalid.")
        if self.expires_at is not None and (
            isinstance(self.expires_at, bool) or not isinstance(self.expires_at, int) or self.expires_at < 0
        ):
            raise ValueError("Principal expires_at must be a non-negative integer.")
        if self.workload_context is not None:
            context = dict(self.workload_context)
            if set(context) - WORKLOAD_CONTEXT_FIELDS:
                raise ValueError("Principal workload_context contains unknown fields.")
            if REQUIRED_WORKLOAD_CONTEXT_FIELDS - set(context):
                raise ValueError("Principal workload_context is missing required fields.")
            if context.get("provider") != "github_actions_oidc":
                raise ValueError("Principal workload_context provider is not recognized.")
            if any(
                not isinstance(value, str) or not value or len(value) > 512
                for value in context.values()
            ):
                raise ValueError("Principal workload_context values must be bounded non-empty strings.")
            if not context["repository_id"].isdigit() or not context["repository_owner_id"].isdigit():
                raise ValueError("Principal workload_context repository IDs must be decimal strings.")
            if any(
                not re.fullmatch(r"(?:[0-9a-f]{40}|[0-9a-f]{64})", context[field])
                for field in ("workflow_sha", "commit_sha")
            ):
                raise ValueError("Principal workload_context Git object IDs are invalid.")
            object.__setattr__(self, "workload_context", MappingProxyType(context))

    def permits(self, scope: str) -> bool:
        if scope not in SCOPES:
            raise ValueError(f"Unknown API scope: {scope}")
        return ALL_SCOPES in self.scopes or scope in self.scopes

    def public_identity(self) -> Dict[str, object]:
        return {
            "identity_version": PRINCIPAL_VERSION,
            "tenant_id": self.tenant_id,
            "principal_id": self.principal_id,
            "scopes": sorted(self.scopes),
            "legacy": self.legacy,
            "credential_type": self.credential_type,
            "session_id": self.session_id,
            "expires_at": self.expires_at,
            "workload_context": None if self.workload_context is None else dict(self.workload_context),
        }


class PrincipalRegistry:
    def __init__(self, principals: Iterable[APIPrincipal]) -> None:
        self._principals = list(principals)
        identities = set()
        secrets = set()
        for principal in self._principals:
            identity = (principal.tenant_id, principal.principal_id)
            if identity in identities:
                raise ValueError(f"Duplicate API principal: {principal.tenant_id}/{principal.principal_id}")
            if principal.secret in secrets:
                raise ValueError("Each API principal must use a distinct secret.")
            identities.add(identity)
            secrets.add(principal.secret)

    @property
    def count(self) -> int:
        return len(self._principals)

    @property
    def tenant_ids(self) -> frozenset[str]:
        return frozenset(item.tenant_id for item in self._principals)

    def authenticate(self, candidate: str) -> Optional[APIPrincipal]:
        match = None
        for principal in self._principals:
            if hmac.compare_digest(candidate, principal.secret):
                match = principal
        return match

    def uses_secret_bytes(self, candidate: bytes) -> bool:
        return any(
            hmac.compare_digest(principal.secret.encode("utf-8"), candidate)
            for principal in self._principals
        )

    @classmethod
    def from_configuration(
        cls,
        legacy_keys: Mapping[str, str],
        scoped_principals: Iterable[APIPrincipal] = (),
    ) -> "PrincipalRegistry":
        legacy = [
            APIPrincipal(
                tenant_id=tenant_id,
                principal_id=f"legacy-{tenant_id}",
                secret=secret,
                scopes=frozenset({ALL_SCOPES}),
                legacy=True,
            )
            for tenant_id, secret in legacy_keys.items()
        ]
        return cls([*legacy, *scoped_principals])


def parse_scoped_principals(value: str) -> list[APIPrincipal]:
    """Parse tenant:principal:scope+scope=secret entries."""
    principals = []
    if not value.strip():
        return principals
    for entry in value.split(","):
        identity, separator, secret = entry.strip().partition("=")
        parts = identity.split(":")
        if separator != "=" or len(parts) != 3 or not secret:
            raise ValueError(
                "SMERC_API_PRINCIPALS entries must use tenant:principal:scope+scope=secret format."
            )
        tenant_id, principal_id, raw_scopes = parts
        scopes = raw_scopes.split("+")
        if not raw_scopes or any(not scope for scope in scopes):
            raise ValueError("Scoped principal must declare one or more scopes.")
        if len(scopes) != len(set(scopes)):
            raise ValueError("Scoped principal cannot repeat a scope.")
        if ALL_SCOPES in scopes:
            raise ValueError("SMERC_API_PRINCIPALS cannot use the wildcard scope.")
        if len(secret) < 24:
            raise ValueError("SMERC_API_PRINCIPALS secrets must contain at least 24 characters.")
        principal = APIPrincipal(
            tenant_id=tenant_id,
            principal_id=principal_id,
            secret=secret,
            scopes=frozenset(scopes),
        )
        principals.append(principal)
    return principals
