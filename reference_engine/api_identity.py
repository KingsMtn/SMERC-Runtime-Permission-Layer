from __future__ import annotations

import hmac
import re
from dataclasses import dataclass, field
from typing import Dict, Iterable, Mapping, Optional


SCOPES = frozenset(
    {
        "actions.evaluate",
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
