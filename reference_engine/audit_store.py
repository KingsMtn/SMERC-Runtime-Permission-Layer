from __future__ import annotations

import json
import sqlite3
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


class IdempotencyConflictError(ValueError):
    pass


class ReviewConflictError(ValueError):
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

    def ping(self) -> bool:
        with self._lock:
            row = self._connection.execute("SELECT 1 AS ok").fetchone()
        return row is not None and row["ok"] == 1

    def close(self) -> None:
        with self._lock:
            self._connection.close()
