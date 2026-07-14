from __future__ import annotations

import hmac
import json
import sqlite3
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional
from uuid import uuid4


class IdempotencyConflictError(ValueError):
    pass


class ReviewConflictError(ValueError):
    pass


class PermitReplayError(ValueError):
    pass


class PermitIssuanceConflictError(ValueError):
    pass


class PermitNotIssuedError(ValueError):
    pass


class PermitPreparationConflictError(ValueError):
    pass


class FederatedTokenReplayError(ValueError):
    pass


class LedgerConflictError(ValueError):
    pass


class AuditStore:
    """Tenant-scoped SQLite decision store for controlled pilot deployments."""

    def __init__(self, path: str | Path) -> None:
        self.path = str(path)
        self._lock = threading.RLock()
        self._connection = sqlite3.connect(self.path, check_same_thread=False)
        self._connection.row_factory = sqlite3.Row
        with self._lock:
            self._connection.execute("PRAGMA journal_mode=WAL")
            self._connection.execute("PRAGMA foreign_keys=ON")
            self._connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS decisions (
                    replay_id TEXT PRIMARY KEY,
                    tenant_id TEXT NOT NULL,
                    action_id TEXT NOT NULL,
                    posture TEXT NOT NULL,
                    idempotency_key TEXT,
                    request_hash TEXT NOT NULL,
                    evaluated_at TEXT NOT NULL,
                    decision_json TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    UNIQUE (tenant_id, idempotency_key)
                );
                CREATE INDEX IF NOT EXISTS idx_decisions_tenant_created
                    ON decisions (tenant_id, created_at DESC);
                CREATE INDEX IF NOT EXISTS idx_decisions_tenant_posture
                    ON decisions (tenant_id, posture, created_at DESC);
                CREATE TABLE IF NOT EXISTS decision_reviews (
                    review_id TEXT PRIMARY KEY,
                    tenant_id TEXT NOT NULL,
                    replay_id TEXT NOT NULL,
                    reviewer_id TEXT NOT NULL,
                    verdict TEXT NOT NULL,
                    decision_posture TEXT NOT NULL,
                    recommended_posture TEXT,
                    idempotency_key TEXT,
                    request_hash TEXT NOT NULL,
                    review_json TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY (replay_id) REFERENCES decisions (replay_id) ON DELETE CASCADE,
                    UNIQUE (tenant_id, replay_id, reviewer_id),
                    UNIQUE (tenant_id, idempotency_key)
                );
                CREATE INDEX IF NOT EXISTS idx_reviews_tenant_created
                    ON decision_reviews (tenant_id, created_at DESC);
                CREATE INDEX IF NOT EXISTS idx_reviews_tenant_replay
                    ON decision_reviews (tenant_id, replay_id, created_at ASC);
                CREATE TABLE IF NOT EXISTS permit_issuances (
                    permit_id TEXT PRIMARY KEY,
                    tenant_id TEXT NOT NULL,
                    replay_id TEXT NOT NULL,
                    action_hash TEXT NOT NULL,
                    audience TEXT NOT NULL,
                    token_hash TEXT NOT NULL,
                    issued_at INTEGER NOT NULL,
                    expires_at INTEGER NOT NULL,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY (replay_id) REFERENCES decisions (replay_id) ON DELETE CASCADE,
                    UNIQUE (tenant_id, replay_id, audience)
                );
                CREATE INDEX IF NOT EXISTS idx_permit_issuances_tenant_created
                    ON permit_issuances (tenant_id, created_at DESC);
                CREATE TABLE IF NOT EXISTS permit_consumptions (
                    permit_id TEXT PRIMARY KEY,
                    tenant_id TEXT NOT NULL,
                    replay_id TEXT NOT NULL,
                    action_hash TEXT NOT NULL,
                    audience TEXT NOT NULL,
                    enforced_controls_json TEXT NOT NULL,
                    consumed_at TEXT NOT NULL,
                    FOREIGN KEY (permit_id) REFERENCES permit_issuances (permit_id) ON DELETE CASCADE,
                    FOREIGN KEY (replay_id) REFERENCES decisions (replay_id) ON DELETE CASCADE
                );
                CREATE INDEX IF NOT EXISTS idx_permit_consumptions_tenant_created
                    ON permit_consumptions (tenant_id, consumed_at DESC);
                CREATE TABLE IF NOT EXISTS permit_preparations (
                    preparation_id TEXT PRIMARY KEY,
                    permit_id TEXT NOT NULL UNIQUE,
                    tenant_id TEXT NOT NULL,
                    replay_id TEXT NOT NULL,
                    action_hash TEXT NOT NULL,
                    audience TEXT NOT NULL,
                    principal_id TEXT NOT NULL,
                    execution_id TEXT NOT NULL,
                    prepared_at TEXT NOT NULL,
                    FOREIGN KEY (permit_id) REFERENCES permit_issuances (permit_id) ON DELETE CASCADE,
                    FOREIGN KEY (replay_id) REFERENCES decisions (replay_id) ON DELETE CASCADE
                );
                CREATE TABLE IF NOT EXISTS security_events (
                    event_id TEXT PRIMARY KEY,
                    tenant_id TEXT NOT NULL,
                    principal_id TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    resource_id TEXT NOT NULL,
                    event_json TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );
                CREATE INDEX IF NOT EXISTS idx_security_events_tenant_created
                    ON security_events (tenant_id, created_at DESC);
                CREATE TABLE IF NOT EXISTS federated_token_exchanges (
                    token_id_hash TEXT PRIMARY KEY,
                    token_hash TEXT NOT NULL UNIQUE,
                    tenant_id TEXT NOT NULL,
                    principal_id TEXT NOT NULL,
                    session_id TEXT NOT NULL UNIQUE,
                    repository_id TEXT NOT NULL,
                    run_id TEXT NOT NULL,
                    exchanged_at TEXT NOT NULL
                );
                CREATE INDEX IF NOT EXISTS idx_federated_exchanges_tenant_created
                    ON federated_token_exchanges (tenant_id, exchanged_at DESC);
                CREATE TABLE IF NOT EXISTS decision_lifecycle_ledgers (
                    decision_id TEXT NOT NULL,
                    tenant_id TEXT NOT NULL,
                    record_count INTEGER NOT NULL,
                    head_record_hash TEXT NOT NULL,
                    complete_lifecycle INTEGER NOT NULL,
                    ledger_json TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    PRIMARY KEY (tenant_id, decision_id)
                );
                CREATE INDEX IF NOT EXISTS idx_dll_tenant_updated
                    ON decision_lifecycle_ledgers (tenant_id, updated_at DESC);
                CREATE INDEX IF NOT EXISTS idx_dll_tenant_head
                    ON decision_lifecycle_ledgers (tenant_id, head_record_hash);
                """
            )
            self._connection.commit()

    def record(
        self,
        tenant_id: str,
        decision: Dict[str, Any],
        request_hash: str,
        idempotency_key: Optional[str] = None,
    ) -> Dict[str, Any]:
        now = datetime.now(timezone.utc).isoformat()
        serialized = json.dumps(decision, sort_keys=True, separators=(",", ":"))
        with self._lock:
            try:
                self._connection.execute(
                    """
                    INSERT INTO decisions (
                        replay_id, tenant_id, action_id, posture, idempotency_key,
                        request_hash, evaluated_at, decision_json, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        decision["replay_id"],
                        tenant_id,
                        decision["action_id"],
                        decision["posture"],
                        idempotency_key,
                        request_hash,
                        decision["replay"]["evaluated_at"],
                        serialized,
                        now,
                    ),
                )
                self._connection.commit()
            except sqlite3.IntegrityError:
                self._connection.rollback()
                if idempotency_key is None:
                    raise
                existing = self._connection.execute(
                    """
                    SELECT request_hash, decision_json
                    FROM decisions
                    WHERE tenant_id = ? AND idempotency_key = ?
                    """,
                    (tenant_id, idempotency_key),
                ).fetchone()
                if existing is None:
                    raise
                if existing["request_hash"] != request_hash:
                    raise IdempotencyConflictError(
                        "Idempotency-Key was already used with a different request body."
                    )
                return json.loads(existing["decision_json"])
        return decision

    def get_by_idempotency_key(self, tenant_id: str, key: str) -> Optional[Dict[str, Any]]:
        with self._lock:
            row = self._connection.execute(
                """
                SELECT request_hash, decision_json
                FROM decisions
                WHERE tenant_id = ? AND idempotency_key = ?
                """,
                (tenant_id, key),
            ).fetchone()
        if row is None:
            return None
        return {
            "request_hash": row["request_hash"],
            "decision": json.loads(row["decision_json"]),
        }

    def get(self, tenant_id: str, replay_id: str) -> Optional[Dict[str, Any]]:
        with self._lock:
            row = self._connection.execute(
                """
                SELECT decision_json
                FROM decisions
                WHERE tenant_id = ? AND replay_id = ?
                """,
                (tenant_id, replay_id),
            ).fetchone()
        return None if row is None else json.loads(row["decision_json"])

    def list(
        self,
        tenant_id: str,
        limit: int = 50,
        posture: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        query = """
            SELECT replay_id, action_id, posture, evaluated_at, decision_json
            FROM decisions
            WHERE tenant_id = ?
        """
        parameters: List[Any] = [tenant_id]
        if posture is not None:
            query += " AND posture = ?"
            parameters.append(posture)
        query += " ORDER BY created_at DESC LIMIT ?"
        parameters.append(limit)

        with self._lock:
            rows = self._connection.execute(query, parameters).fetchall()
        return [
            {
                "replay_id": row["replay_id"],
                "action_id": row["action_id"],
                "posture": row["posture"],
                "evaluated_at": row["evaluated_at"],
                "scores": json.loads(row["decision_json"])["scores"],
            }
            for row in rows
        ]

    def count(self, tenant_id: str) -> int:
        with self._lock:
            row = self._connection.execute(
                "SELECT COUNT(*) AS total FROM decisions WHERE tenant_id = ?",
                (tenant_id,),
            ).fetchone()
        return int(row["total"])

    def record_review(
        self,
        tenant_id: str,
        replay_id: str,
        review: Dict[str, Any],
        request_hash: str,
        idempotency_key: Optional[str] = None,
    ) -> Dict[str, Any]:
        now = datetime.now(timezone.utc).isoformat()
        stored_review = dict(review)
        stored_review["created_at"] = now
        serialized = json.dumps(stored_review, sort_keys=True, separators=(",", ":"))
        with self._lock:
            try:
                self._connection.execute(
                    """
                    INSERT INTO decision_reviews (
                        review_id, tenant_id, replay_id, reviewer_id, verdict,
                        decision_posture, recommended_posture, idempotency_key,
                        request_hash, review_json, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        stored_review["review_id"],
                        tenant_id,
                        replay_id,
                        stored_review["reviewer_id"],
                        stored_review["verdict"],
                        stored_review["decision_posture"],
                        stored_review.get("recommended_posture"),
                        idempotency_key,
                        request_hash,
                        serialized,
                        now,
                    ),
                )
                self._connection.commit()
            except sqlite3.IntegrityError as exc:
                self._connection.rollback()
                if idempotency_key is not None:
                    existing = self.get_review_by_idempotency_key(tenant_id, idempotency_key)
                    if existing is not None:
                        if existing["request_hash"] != request_hash:
                            raise IdempotencyConflictError(
                                "Idempotency-Key was already used with a different review body."
                            ) from exc
                        return existing["review"]
                existing = self._connection.execute(
                    """
                    SELECT request_hash, review_json
                    FROM decision_reviews
                    WHERE tenant_id = ? AND replay_id = ? AND reviewer_id = ?
                    """,
                    (tenant_id, replay_id, stored_review["reviewer_id"]),
                ).fetchone()
                if existing is not None:
                    if existing["request_hash"] == request_hash:
                        return json.loads(existing["review_json"])
                    raise ReviewConflictError(
                        "Reviewer already submitted an immutable review for this decision."
                    ) from exc
                raise
        return stored_review

    def get_review_by_idempotency_key(self, tenant_id: str, key: str) -> Optional[Dict[str, Any]]:
        with self._lock:
            row = self._connection.execute(
                """
                SELECT request_hash, review_json
                FROM decision_reviews
                WHERE tenant_id = ? AND idempotency_key = ?
                """,
                (tenant_id, key),
            ).fetchone()
        if row is None:
            return None
        return {"request_hash": row["request_hash"], "review": json.loads(row["review_json"])}

    def list_reviews(self, tenant_id: str, replay_id: str) -> List[Dict[str, Any]]:
        with self._lock:
            rows = self._connection.execute(
                """
                SELECT review_json
                FROM decision_reviews
                WHERE tenant_id = ? AND replay_id = ?
                ORDER BY created_at ASC
                """,
                (tenant_id, replay_id),
            ).fetchall()
        return [json.loads(row["review_json"]) for row in rows]

    def review_queue(
        self,
        tenant_id: str,
        limit: int = 50,
        review_status: str = "all",
        posture: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        query = """
            SELECT
                d.replay_id,
                d.action_id,
                d.posture,
                d.evaluated_at,
                d.decision_json,
                COUNT(r.review_id) AS review_count,
                SUM(CASE WHEN r.verdict = 'agree' THEN 1 ELSE 0 END) AS agree_count,
                SUM(CASE WHEN r.verdict = 'override' THEN 1 ELSE 0 END) AS override_count,
                SUM(CASE WHEN r.verdict = 'uncertain' THEN 1 ELSE 0 END) AS uncertain_count
            FROM decisions d
            LEFT JOIN decision_reviews r
                ON r.tenant_id = d.tenant_id AND r.replay_id = d.replay_id
            WHERE d.tenant_id = ?
        """
        parameters: List[Any] = [tenant_id]
        if posture is not None:
            query += " AND d.posture = ?"
            parameters.append(posture)
        query += " GROUP BY d.replay_id"
        if review_status == "pending":
            query += " HAVING COUNT(r.review_id) = 0"
        elif review_status == "reviewed":
            query += " HAVING COUNT(r.review_id) > 0"
        query += " ORDER BY d.created_at DESC LIMIT ?"
        parameters.append(limit)

        with self._lock:
            rows = self._connection.execute(query, parameters).fetchall()
        queue = []
        for row in rows:
            decision = json.loads(row["decision_json"])
            review_count = int(row["review_count"])
            queue.append(
                {
                    "replay_id": row["replay_id"],
                    "action_id": row["action_id"],
                    "description": decision.get("plain_english_summary", ""),
                    "posture": row["posture"],
                    "evaluated_at": row["evaluated_at"],
                    "scores": decision["scores"],
                    "review_status": "reviewed" if review_count else "pending",
                    "review_count": review_count,
                    "verdict_counts": {
                        "agree": int(row["agree_count"] or 0),
                        "override": int(row["override_count"] or 0),
                        "uncertain": int(row["uncertain_count"] or 0),
                    },
                }
            )
        return queue

    def pilot_metrics(self, tenant_id: str) -> Dict[str, Any]:
        with self._lock:
            rows = self._connection.execute(
                """
                SELECT replay_id, verdict, decision_posture, review_json
                FROM decision_reviews
                WHERE tenant_id = ?
                """,
                (tenant_id,),
            ).fetchall()
            decision_total = self.count(tenant_id)

        reviews = [json.loads(row["review_json"]) for row in rows]
        reviewed_decisions = len({row["replay_id"] for row in rows})
        determinate = [review for review in reviews if review["verdict"] != "uncertain"]
        allowed = [review for review in reviews if review["decision_posture"] == "ALLOW"]
        constrained = [review for review in reviews if review["decision_posture"] != "ALLOW"]
        latencies = [review["review_latency_ms"] for review in reviews]

        def rate(numerator: int, denominator: int) -> Optional[float]:
            return None if denominator == 0 else round(numerator / denominator, 4)

        return {
            "tenant_id": tenant_id,
            "decision_count": decision_total,
            "reviewed_decision_count": reviewed_decisions,
            "review_count": len(reviews),
            "metrics": {
                "decision_review_coverage": rate(reviewed_decisions, decision_total),
                "reviewer_agreement_rate": rate(
                    sum(review["verdict"] == "agree" for review in determinate), len(determinate)
                ),
                "override_rate": rate(
                    sum(review["verdict"] == "override" for review in determinate), len(determinate)
                ),
                "false_release_rate": rate(
                    sum(review["false_release"] for review in allowed), len(allowed)
                ),
                "false_constraint_rate": rate(
                    sum(review["false_constraint"] for review in constrained), len(constrained)
                ),
                "useful_constraint_rate": rate(
                    sum(review["useful_constraint"] for review in constrained), len(constrained)
                ),
                "average_review_latency_ms": (
                    None if not latencies else round(sum(latencies) / len(latencies), 2)
                ),
            },
            "denominators": {
                "all_decisions": decision_total,
                "all_reviews": len(reviews),
                "determinate_reviews": len(determinate),
                "allow_reviews": len(allowed),
                "constrained_reviews": len(constrained),
            },
        }

    def record_permit_issuance(
        self,
        tenant_id: str,
        permit: Dict[str, Any],
        token_hash: str,
    ) -> Dict[str, Any]:
        created_at = datetime.now(timezone.utc).isoformat()
        with self._lock:
            try:
                self._connection.execute(
                    """
                    INSERT INTO permit_issuances (
                        permit_id, tenant_id, replay_id, action_hash, audience,
                        token_hash, issued_at, expires_at, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        permit["permit_id"], tenant_id, permit["replay_id"], permit["action_hash"],
                        permit["audience"], token_hash, permit["issued_at"], permit["expires_at"], created_at,
                    ),
                )
                self._connection.commit()
            except sqlite3.IntegrityError as exc:
                self._connection.rollback()
                existing = self._connection.execute(
                    """
                    SELECT permit_id
                    FROM permit_issuances
                    WHERE tenant_id = ? AND replay_id = ? AND audience = ?
                    """,
                    (tenant_id, permit["replay_id"], permit["audience"]),
                ).fetchone()
                if existing is not None:
                    raise PermitIssuanceConflictError(
                        "A permit was already issued for this decision and audience. A new action decision is required."
                    ) from exc
                raise
        return {
            "permit_id": permit["permit_id"],
            "tenant_id": tenant_id,
            "replay_id": permit["replay_id"],
            "audience": permit["audience"],
            "issued_at": permit["issued_at"],
            "expires_at": permit["expires_at"],
        }

    def consume_permit(
        self,
        tenant_id: str,
        permit: Dict[str, Any],
        enforced_controls: List[str],
        token_hash: str,
        *,
        preparation_id: Optional[str] = None,
        principal_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        consumed_at = datetime.now(timezone.utc).isoformat()
        controls_json = json.dumps(sorted(enforced_controls), separators=(",", ":"))
        with self._lock:
            if preparation_id is not None:
                preparation = self._connection.execute(
                    """
                    SELECT permit_id, tenant_id, replay_id, action_hash, audience, principal_id
                    FROM permit_preparations
                    WHERE preparation_id = ?
                    """,
                    (preparation_id,),
                ).fetchone()
                if preparation is None or principal_id is None or any(
                    (
                        preparation["permit_id"] != permit["permit_id"],
                        preparation["tenant_id"] != tenant_id,
                        preparation["replay_id"] != permit["replay_id"],
                        preparation["action_hash"] != permit["action_hash"],
                        preparation["audience"] != permit["audience"],
                        not hmac.compare_digest(preparation["principal_id"], principal_id),
                    )
                ):
                    raise PermitPreparationConflictError(
                        "Permit preparation does not match this executor and permit."
                    )
            issuance = self._connection.execute(
                """
                SELECT tenant_id, replay_id, action_hash, audience, token_hash
                FROM permit_issuances
                WHERE permit_id = ?
                """,
                (permit["permit_id"],),
            ).fetchone()
            if issuance is None or any(
                (
                    issuance["tenant_id"] != tenant_id,
                    issuance["replay_id"] != permit["replay_id"],
                    issuance["action_hash"] != permit["action_hash"],
                    issuance["audience"] != permit["audience"],
                    issuance["token_hash"] != token_hash,
                )
            ):
                raise PermitNotIssuedError("Permit does not match a registered issuance.")
            try:
                self._connection.execute(
                    """
                    INSERT INTO permit_consumptions (
                        permit_id, tenant_id, replay_id, action_hash, audience,
                        enforced_controls_json, consumed_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        permit["permit_id"],
                        tenant_id,
                        permit["replay_id"],
                        permit["action_hash"],
                        permit["audience"],
                        controls_json,
                        consumed_at,
                    ),
                )
                self._connection.commit()
            except sqlite3.IntegrityError as exc:
                self._connection.rollback()
                existing = self._connection.execute(
                    """
                    SELECT tenant_id, replay_id, action_hash, audience, consumed_at
                    FROM permit_consumptions
                    WHERE permit_id = ?
                    """,
                    (permit["permit_id"],),
                ).fetchone()
                if existing is not None:
                    raise PermitReplayError(
                        f"Permit was already consumed at {existing['consumed_at']}."
                    ) from exc
                raise
        return {
            "permit_id": permit["permit_id"],
            "tenant_id": tenant_id,
            "replay_id": permit["replay_id"],
            "action_hash": permit["action_hash"],
            "audience": permit["audience"],
            "enforced_controls": sorted(enforced_controls),
            "consumed_at": consumed_at,
        }

    def validate_permit_issuance(
        self,
        tenant_id: str,
        permit: Dict[str, Any],
        token_hash: str,
    ) -> Dict[str, Any]:
        """Confirm a permit is registered and unconsumed without reserving it."""
        with self._lock:
            issuance = self._connection.execute(
                """
                SELECT tenant_id, replay_id, action_hash, audience, token_hash
                FROM permit_issuances
                WHERE permit_id = ?
                """,
                (permit["permit_id"],),
            ).fetchone()
            if issuance is None or any(
                (
                    issuance["tenant_id"] != tenant_id,
                    issuance["replay_id"] != permit["replay_id"],
                    issuance["action_hash"] != permit["action_hash"],
                    issuance["audience"] != permit["audience"],
                    not hmac.compare_digest(issuance["token_hash"], token_hash),
                )
            ):
                raise PermitNotIssuedError("Permit does not match a registered issuance.")
            consumed = self._connection.execute(
                "SELECT consumed_at FROM permit_consumptions WHERE permit_id = ?",
                (permit["permit_id"],),
            ).fetchone()
            if consumed is not None:
                raise PermitReplayError(f"Permit was already consumed at {consumed['consumed_at']}.")
        return {
            "permit_id": permit["permit_id"],
            "tenant_id": tenant_id,
            "replay_id": permit["replay_id"],
            "audience": permit["audience"],
            "expires_at": permit["expires_at"],
        }

    def prepare_permit(
        self,
        tenant_id: str,
        permit: Dict[str, Any],
        token_hash: str,
        principal_id: str,
        execution_id: str,
    ) -> Dict[str, Any]:
        """Atomically reserve one issued permit for one executor operation."""
        prepared_at = datetime.now(timezone.utc).isoformat()
        preparation_id = f"preparation_{uuid4().hex}"
        with self._lock:
            self.validate_permit_issuance(tenant_id, permit, token_hash)
            existing = self._connection.execute(
                """
                SELECT preparation_id, principal_id, execution_id, prepared_at
                FROM permit_preparations
                WHERE permit_id = ?
                """,
                (permit["permit_id"],),
            ).fetchone()
            if existing is not None:
                if hmac.compare_digest(existing["principal_id"], principal_id) and hmac.compare_digest(
                    existing["execution_id"], execution_id
                ):
                    return {
                        "preparation_id": existing["preparation_id"],
                        "permit_id": permit["permit_id"],
                        "principal_id": principal_id,
                        "execution_id": execution_id,
                        "prepared_at": existing["prepared_at"],
                        "idempotent_replay": True,
                    }
                raise PermitPreparationConflictError("Permit is already reserved by another execution.")
            try:
                self._connection.execute(
                    """
                    INSERT INTO permit_preparations (
                        preparation_id, permit_id, tenant_id, replay_id, action_hash,
                        audience, principal_id, execution_id, prepared_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        preparation_id, permit["permit_id"], tenant_id, permit["replay_id"],
                        permit["action_hash"], permit["audience"], principal_id, execution_id, prepared_at,
                    ),
                )
                self._connection.commit()
            except sqlite3.IntegrityError as exc:
                self._connection.rollback()
                raise PermitPreparationConflictError("Permit is already reserved by another execution.") from exc
        return {
            "preparation_id": preparation_id,
            "permit_id": permit["permit_id"],
            "principal_id": principal_id,
            "execution_id": execution_id,
            "prepared_at": prepared_at,
            "idempotent_replay": False,
        }

    def record_security_event(
        self,
        tenant_id: str,
        principal_id: str,
        event_type: str,
        resource_id: str,
        metadata: Dict[str, Any],
    ) -> Dict[str, Any]:
        event = {
            "event_version": "smerc.security-event.v1",
            "event_id": f"security_event_{uuid4().hex}",
            "tenant_id": tenant_id,
            "principal_id": principal_id,
            "event_type": event_type,
            "resource_id": resource_id,
            "metadata": metadata,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        serialized = json.dumps(event, sort_keys=True, separators=(",", ":"))
        with self._lock:
            self._connection.execute(
                """
                INSERT INTO security_events (
                    event_id, tenant_id, principal_id, event_type,
                    resource_id, event_json, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    event["event_id"], tenant_id, principal_id, event_type,
                    resource_id, serialized, event["created_at"],
                ),
            )
            self._connection.commit()
        return event

    def register_github_oidc_exchange(
        self,
        tenant_id: str,
        principal_id: str,
        token_id_hash: str,
        token_hash: str,
        session: Dict[str, Any],
        workload_context: Dict[str, str],
    ) -> Dict[str, Any]:
        event = {
            "event_version": "smerc.security-event.v1",
            "event_id": f"security_event_{uuid4().hex}",
            "tenant_id": tenant_id,
            "principal_id": principal_id,
            "event_type": "github_oidc.exchanged",
            "resource_id": session["session_id"],
            "metadata": {
                "token_id_hash": token_id_hash,
                "repository": workload_context["repository"],
                "repository_id": workload_context["repository_id"],
                "workflow_ref": workload_context["workflow_ref"],
                "workflow_sha": workload_context["workflow_sha"],
                "ref": workload_context["ref"],
                "commit_sha": workload_context["commit_sha"],
                "run_id": workload_context["run_id"],
                "run_attempt": workload_context["run_attempt"],
                "actor_id": workload_context["actor_id"],
                "event_name": workload_context["event_name"],
                "environment": workload_context.get("environment"),
                "scopes": session["scopes"],
                "expires_at": session["expires_at"],
            },
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        serialized = json.dumps(event, sort_keys=True, separators=(",", ":"))
        with self._lock:
            try:
                self._connection.execute("BEGIN IMMEDIATE")
                self._connection.execute(
                    """
                    INSERT INTO federated_token_exchanges (
                        token_id_hash, token_hash, tenant_id, principal_id,
                        session_id, repository_id, run_id, exchanged_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        token_id_hash,
                        token_hash,
                        tenant_id,
                        principal_id,
                        session["session_id"],
                        workload_context["repository_id"],
                        workload_context["run_id"],
                        event["created_at"],
                    ),
                )
                self._connection.execute(
                    """
                    INSERT INTO security_events (
                        event_id, tenant_id, principal_id, event_type,
                        resource_id, event_json, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        event["event_id"], tenant_id, principal_id, event["event_type"],
                        event["resource_id"], serialized, event["created_at"],
                    ),
                )
                self._connection.commit()
            except sqlite3.IntegrityError as exc:
                self._connection.rollback()
                raise FederatedTokenReplayError(
                    "GitHub OIDC token was already exchanged."
                ) from exc
            except Exception:
                self._connection.rollback()
                raise
        return event

    def list_security_events(self, tenant_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        with self._lock:
            rows = self._connection.execute(
                """
                SELECT event_json
                FROM security_events
                WHERE tenant_id = ?
                ORDER BY created_at DESC
                LIMIT ?
                """,
                (tenant_id, limit),
            ).fetchall()
        return [json.loads(row["event_json"]) for row in rows]

    def record_decision_lifecycle_ledger(
        self,
        tenant_id: str,
        ledger: Dict[str, Any],
        *,
        principal_id: str,
    ) -> Dict[str, Any]:
        now = datetime.now(timezone.utc).isoformat()
        decision_id = ledger["decision_id"]
        head_record_hash = ledger["head_record_hash"]
        record_count = int(ledger["record_count"])
        summary = ledger.get("summary", {})
        event_counts = summary.get("event_counts", {}) if isinstance(summary, dict) else {}
        complete_lifecycle = int(
            all(
                event_counts.get(event_type, 0) > 0
                for event_type in {
                    "REQUEST",
                    "EVIDENCE",
                    "EVALUATION",
                    "HUMAN_INTERACTION",
                    "EXECUTION",
                    "OUTCOME",
                    "LEARNING_RECOMMENDATION",
                }
            )
        )
        serialized = json.dumps(ledger, sort_keys=True, separators=(",", ":"))
        with self._lock:
            existing = self._connection.execute(
                """
                SELECT head_record_hash, ledger_json, created_at
                FROM decision_lifecycle_ledgers
                WHERE tenant_id = ? AND decision_id = ?
                """,
                (tenant_id, decision_id),
            ).fetchone()
            if existing is not None and existing["head_record_hash"] != head_record_hash:
                raise LedgerConflictError(
                    "A different Decision Lifecycle Ledger already exists for this tenant and decision_id."
                )
            if existing is None:
                self._connection.execute(
                    """
                    INSERT INTO decision_lifecycle_ledgers (
                        decision_id, tenant_id, record_count, head_record_hash,
                        complete_lifecycle, ledger_json, created_at, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        decision_id,
                        tenant_id,
                        record_count,
                        head_record_hash,
                        complete_lifecycle,
                        serialized,
                        now,
                        now,
                    ),
                )
                stored_at = now
            else:
                self._connection.execute(
                    """
                    UPDATE decision_lifecycle_ledgers
                    SET record_count = ?, complete_lifecycle = ?, ledger_json = ?, updated_at = ?
                    WHERE tenant_id = ? AND decision_id = ?
                    """,
                    (record_count, complete_lifecycle, serialized, now, tenant_id, decision_id),
                )
                stored_at = existing["created_at"]
            self._connection.commit()
        return {
            "tenant_id": tenant_id,
            "decision_id": decision_id,
            "record_count": record_count,
            "head_record_hash": head_record_hash,
            "complete_lifecycle": bool(complete_lifecycle),
            "stored_at": stored_at,
            "updated_at": now,
            "stored_by": principal_id,
        }

    def get_decision_lifecycle_ledger(self, tenant_id: str, decision_id: str) -> Optional[Dict[str, Any]]:
        with self._lock:
            row = self._connection.execute(
                """
                SELECT ledger_json, created_at, updated_at
                FROM decision_lifecycle_ledgers
                WHERE tenant_id = ? AND decision_id = ?
                """,
                (tenant_id, decision_id),
            ).fetchone()
        if row is None:
            return None
        ledger = json.loads(row["ledger_json"])
        ledger["stored_at"] = row["created_at"]
        ledger["updated_at"] = row["updated_at"]
        return ledger

    def list_decision_lifecycle_ledgers(self, tenant_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        with self._lock:
            rows = self._connection.execute(
                """
                SELECT decision_id, record_count, head_record_hash, complete_lifecycle, created_at, updated_at
                FROM decision_lifecycle_ledgers
                WHERE tenant_id = ?
                ORDER BY updated_at DESC
                LIMIT ?
                """,
                (tenant_id, limit),
            ).fetchall()
        return [
            {
                "decision_id": row["decision_id"],
                "record_count": int(row["record_count"]),
                "head_record_hash": row["head_record_hash"],
                "complete_lifecycle": bool(row["complete_lifecycle"]),
                "stored_at": row["created_at"],
                "updated_at": row["updated_at"],
            }
            for row in rows
        ]

    def count_decision_lifecycle_ledgers(self, tenant_id: str) -> int:
        with self._lock:
            row = self._connection.execute(
                "SELECT COUNT(*) AS total FROM decision_lifecycle_ledgers WHERE tenant_id = ?",
                (tenant_id,),
            ).fetchone()
        return int(row["total"])

    def ping(self) -> bool:
        with self._lock:
            row = self._connection.execute("SELECT 1 AS ok").fetchone()
        return row is not None and row["ok"] == 1

    def close(self) -> None:
        with self._lock:
            self._connection.close()
