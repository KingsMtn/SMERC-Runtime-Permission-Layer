from __future__ import annotations

import hashlib
import json
import sqlite3
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping
from uuid import uuid4

from reference_engine.delegated_continuance_contract import ContinuanceContractSigner


VERSION = "smerc.consequence-reservation-settlement.v1"
SETTLEMENT_STATES = {"RELEASED", "CONSUMED", "RECOVERED", "UNSETTLED", "ESCALATED"}


class ConsequenceReservationError(ValueError):
    pass


class ConsequenceSettlementError(ValueError):
    pass


def _canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def _digest(value: Any) -> str:
    return hashlib.sha256(_canonical(value).encode("utf-8")).hexdigest()


def _amount(value: Any, path: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)) or value < 0:
        raise ValueError(f"{path} must be a non-negative number")
    return float(value)


class ConsequenceLedger:
    """Atomic SQLite ledger for shared delegated consequence capacity."""

    def __init__(self, path: str | Path) -> None:
        self.path = str(path)
        self._lock = threading.RLock()
        self._connection = sqlite3.connect(self.path, check_same_thread=False, timeout=30)
        self._connection.row_factory = sqlite3.Row
        with self._lock:
            self._connection.execute("PRAGMA journal_mode=WAL")
            self._connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS consequence_budgets (
                    budget_id TEXT PRIMARY KEY,
                    tenant_id TEXT NOT NULL,
                    intent_digest TEXT NOT NULL,
                    max_cost_usd REAL NOT NULL,
                    max_scope_units REAL NOT NULL,
                    max_mutations REAL NOT NULL,
                    created_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS consequence_reservations (
                    reservation_id TEXT PRIMARY KEY,
                    budget_id TEXT NOT NULL,
                    operation_key TEXT NOT NULL,
                    request_sha256 TEXT NOT NULL,
                    contract_sha256 TEXT NOT NULL,
                    task_id TEXT NOT NULL,
                    requested_cost_usd REAL NOT NULL,
                    requested_scope_units REAL NOT NULL,
                    requested_mutations REAL NOT NULL,
                    actual_cost_usd REAL,
                    actual_scope_units REAL,
                    actual_mutations REAL,
                    status TEXT NOT NULL,
                    cleanup_verified INTEGER,
                    evidence_json TEXT,
                    created_at TEXT NOT NULL,
                    settled_at TEXT,
                    FOREIGN KEY (budget_id) REFERENCES consequence_budgets (budget_id),
                    UNIQUE (budget_id, operation_key)
                );
                CREATE INDEX IF NOT EXISTS idx_consequence_reservations_budget
                    ON consequence_reservations (budget_id, status);
                """
            )
            self._connection.commit()

    def close(self) -> None:
        with self._lock:
            self._connection.close()

    def create_budget(
        self,
        *,
        budget_id: str,
        tenant_id: str,
        intent_digest: str,
        max_cost_usd: float,
        max_scope_units: float,
        max_mutations: float,
    ) -> dict[str, Any]:
        values = (
            budget_id,
            tenant_id,
            intent_digest,
            _amount(max_cost_usd, "max_cost_usd"),
            _amount(max_scope_units, "max_scope_units"),
            _amount(max_mutations, "max_mutations"),
            _now(),
        )
        with self._lock:
            try:
                self._connection.execute(
                    "INSERT INTO consequence_budgets VALUES (?, ?, ?, ?, ?, ?, ?)", values
                )
                self._connection.commit()
            except sqlite3.IntegrityError as exc:
                raise ConsequenceReservationError("budget_id already exists") from exc
        return self.budget_status(budget_id)

    def reserve(
        self,
        *,
        budget_id: str,
        signer: ContinuanceContractSigner,
        contract: Mapping[str, Any],
        operation_key: str,
        task_id: str,
        request: Mapping[str, Any],
        now: int,
    ) -> dict[str, Any]:
        contract_body = signer.verify(contract)
        if isinstance(now, bool) or not isinstance(now, int) or now < 0:
            raise ConsequenceReservationError("now must be a non-negative integer")
        if now >= contract_body["expires_at"]:
            raise ConsequenceReservationError("delegated continuance contract has expired")
        if request.get("intent_digest") != contract_body["intent_digest"]:
            raise ConsequenceReservationError("request intent does not match delegated contract")
        requested = {
            "cost_usd": _amount(request.get("cost_usd", 0), "request.cost_usd"),
            "scope_units": _amount(request.get("scope_units", 0), "request.scope_units"),
            "mutations": _amount(request.get("mutations", 0), "request.mutations"),
        }
        if requested["cost_usd"] > contract_body["budget"]["max_cost_usd"]:
            raise ConsequenceReservationError("request cost exceeds delegated contract budget")
        if requested["scope_units"] > contract_body["budget"]["max_scope_units"]:
            raise ConsequenceReservationError("request scope exceeds delegated contract budget")
        request_sha256 = _digest(request)
        contract_sha256 = _digest(contract)
        with self._lock:
            self._connection.execute("BEGIN IMMEDIATE")
            try:
                budget = self._connection.execute(
                    "SELECT * FROM consequence_budgets WHERE budget_id = ?", (budget_id,)
                ).fetchone()
                if budget is None:
                    raise ConsequenceReservationError("budget does not exist")
                if budget["tenant_id"] != contract_body["tenant_id"]:
                    raise ConsequenceReservationError("contract tenant does not match budget")
                if budget["intent_digest"] != contract_body["intent_digest"]:
                    raise ConsequenceReservationError("contract intent does not match budget")
                existing = self._connection.execute(
                    "SELECT * FROM consequence_reservations WHERE budget_id = ? AND operation_key = ?",
                    (budget_id, operation_key),
                ).fetchone()
                if existing is not None:
                    if existing["request_sha256"] != request_sha256 or existing["contract_sha256"] != contract_sha256:
                        raise ConsequenceReservationError("operation_key reuse conflicts with the original reservation")
                    self._connection.commit()
                    return self._reservation(existing, idempotent=True)
                usage = self._usage_locked(budget_id)
                exceeded = []
                if usage["cost_usd"] + requested["cost_usd"] > budget["max_cost_usd"]:
                    exceeded.append("cost")
                if usage["scope_units"] + requested["scope_units"] > budget["max_scope_units"]:
                    exceeded.append("scope")
                if usage["mutations"] + requested["mutations"] > budget["max_mutations"]:
                    exceeded.append("mutations")
                if exceeded:
                    raise ConsequenceReservationError(
                        "shared consequence capacity exceeded: " + ", ".join(exceeded)
                    )
                reservation_id = f"csr_{uuid4().hex}"
                self._connection.execute(
                    """
                    INSERT INTO consequence_reservations (
                        reservation_id, budget_id, operation_key, request_sha256, contract_sha256,
                        task_id, requested_cost_usd, requested_scope_units, requested_mutations,
                        status, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'RESERVED', ?)
                    """,
                    (
                        reservation_id, budget_id, operation_key, request_sha256, contract_sha256,
                        task_id, requested["cost_usd"], requested["scope_units"], requested["mutations"], _now(),
                    ),
                )
                row = self._connection.execute(
                    "SELECT * FROM consequence_reservations WHERE reservation_id = ?", (reservation_id,)
                ).fetchone()
                self._connection.commit()
                return self._reservation(row, idempotent=False)
            except Exception:
                self._connection.rollback()
                raise

    def settle(
        self,
        reservation_id: str,
        *,
        outcome: str,
        actual_cost_usd: float,
        actual_scope_units: float,
        actual_mutations: float,
        cleanup_verified: bool,
        evidence: Mapping[str, Any],
    ) -> dict[str, Any]:
        if outcome not in SETTLEMENT_STATES:
            raise ConsequenceSettlementError("settlement outcome is invalid")
        actual = {
            "cost_usd": _amount(actual_cost_usd, "actual_cost_usd"),
            "scope_units": _amount(actual_scope_units, "actual_scope_units"),
            "mutations": _amount(actual_mutations, "actual_mutations"),
        }
        if outcome == "RECOVERED" and not cleanup_verified:
            raise ConsequenceSettlementError("RECOVERED requires verified cleanup")
        if outcome == "RELEASED" and any(actual.values()):
            raise ConsequenceSettlementError("RELEASED requires zero actual consequence")
        if outcome == "UNSETTLED" and cleanup_verified:
            raise ConsequenceSettlementError("UNSETTLED cannot claim verified cleanup")
        with self._lock:
            self._connection.execute("BEGIN IMMEDIATE")
            try:
                row = self._connection.execute(
                    "SELECT * FROM consequence_reservations WHERE reservation_id = ?", (reservation_id,)
                ).fetchone()
                if row is None:
                    raise ConsequenceSettlementError("reservation does not exist")
                if row["status"] != "RESERVED":
                    same = (
                        row["status"] == outcome
                        and row["actual_cost_usd"] == actual["cost_usd"]
                        and row["actual_scope_units"] == actual["scope_units"]
                        and row["actual_mutations"] == actual["mutations"]
                        and bool(row["cleanup_verified"]) == cleanup_verified
                    )
                    if not same:
                        raise ConsequenceSettlementError("reservation has already been settled differently")
                    self._connection.commit()
                    return self._reservation(row, idempotent=True)
                requested = (row["requested_cost_usd"], row["requested_scope_units"], row["requested_mutations"])
                if outcome not in {"ESCALATED", "UNSETTLED"} and any(
                    value > limit for value, limit in zip(actual.values(), requested)
                ):
                    raise ConsequenceSettlementError("actual consequence exceeds reservation")
                self._connection.execute(
                    """
                    UPDATE consequence_reservations
                    SET status = ?, actual_cost_usd = ?, actual_scope_units = ?, actual_mutations = ?,
                        cleanup_verified = ?, evidence_json = ?, settled_at = ?
                    WHERE reservation_id = ?
                    """,
                    (
                        outcome, actual["cost_usd"], actual["scope_units"], actual["mutations"],
                        int(cleanup_verified), _canonical(evidence), _now(), reservation_id,
                    ),
                )
                updated = self._connection.execute(
                    "SELECT * FROM consequence_reservations WHERE reservation_id = ?", (reservation_id,)
                ).fetchone()
                self._connection.commit()
                return self._reservation(updated, idempotent=False)
            except Exception:
                self._connection.rollback()
                raise

    def budget_status(self, budget_id: str) -> dict[str, Any]:
        with self._lock:
            budget = self._connection.execute(
                "SELECT * FROM consequence_budgets WHERE budget_id = ?", (budget_id,)
            ).fetchone()
            if budget is None:
                raise ConsequenceReservationError("budget does not exist")
            usage = self._usage_locked(budget_id)
        maximum = {
            "cost_usd": budget["max_cost_usd"],
            "scope_units": budget["max_scope_units"],
            "mutations": budget["max_mutations"],
        }
        return {
            "version": VERSION,
            "budget_id": budget_id,
            "tenant_id": budget["tenant_id"],
            "intent_digest": budget["intent_digest"],
            "maximum": maximum,
            "committed": usage,
            "available": {key: max(0.0, maximum[key] - usage[key]) for key in maximum},
        }

    def _usage_locked(self, budget_id: str) -> dict[str, float]:
        rows = self._connection.execute(
            "SELECT * FROM consequence_reservations WHERE budget_id = ?", (budget_id,)
        ).fetchall()
        totals = {"cost_usd": 0.0, "scope_units": 0.0, "mutations": 0.0}
        for row in rows:
            status = row["status"]
            if status == "RELEASED":
                continue
            if status == "RECOVERED":
                totals["cost_usd"] += row["actual_cost_usd"] or 0.0
                continue
            if status == "CONSUMED":
                totals["cost_usd"] += row["actual_cost_usd"] or 0.0
                totals["scope_units"] += row["actual_scope_units"] or 0.0
                totals["mutations"] += row["actual_mutations"] or 0.0
                continue
            actual_or_requested = status == "ESCALATED"
            for name, column in (
                ("cost_usd", "cost_usd"), ("scope_units", "scope_units"), ("mutations", "mutations")
            ):
                requested = row[f"requested_{column}"]
                actual = row[f"actual_{column}"] or 0.0
                totals[name] += max(requested, actual) if actual_or_requested else requested
        return {key: round(value, 6) for key, value in totals.items()}

    @staticmethod
    def _reservation(row: sqlite3.Row, *, idempotent: bool) -> dict[str, Any]:
        return {
            "version": VERSION,
            "reservation_id": row["reservation_id"],
            "budget_id": row["budget_id"],
            "operation_key": row["operation_key"],
            "task_id": row["task_id"],
            "status": row["status"],
            "requested": {
                "cost_usd": row["requested_cost_usd"],
                "scope_units": row["requested_scope_units"],
                "mutations": row["requested_mutations"],
            },
            "actual": None if row["actual_cost_usd"] is None else {
                "cost_usd": row["actual_cost_usd"],
                "scope_units": row["actual_scope_units"],
                "mutations": row["actual_mutations"],
            },
            "cleanup_verified": None if row["cleanup_verified"] is None else bool(row["cleanup_verified"]),
            "idempotent_replay": idempotent,
        }


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()
