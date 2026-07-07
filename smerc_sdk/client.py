from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Mapping, Optional
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


JsonObject = dict[str, Any]


@dataclass
class SMERCAPIError(Exception):
    """Raised when the SMERC API returns a non-2xx response."""

    status: int
    code: str
    message: str
    body: JsonObject

    def __str__(self) -> str:
        return f"SMERC API error {self.status} {self.code}: {self.message}"


class SMERCClient:
    """Small standard-library client for the SMERC Runtime Permission API.

    The SDK intentionally keeps transport behavior explicit: callers pass a base
    URL, an optional bearer token, and ordinary dictionaries matching the public
    SMERC Action Language or recoverability request contracts.
    """

    def __init__(
        self,
        base_url: str,
        *,
        token: Optional[str] = None,
        timeout: float = 10.0,
        user_agent: str = "smerc-python-sdk/0.1",
    ) -> None:
        if not isinstance(base_url, str) or not base_url.startswith(("http://", "https://")):
            raise ValueError("base_url must start with http:// or https://")
        if timeout <= 0:
            raise ValueError("timeout must be greater than zero")
        self.base_url = base_url.rstrip("/")
        self.token = token
        self.timeout = timeout
        self.user_agent = user_agent

    def health(self) -> JsonObject:
        return self._request("GET", "/v1/health")

    def ready(self) -> JsonObject:
        return self._request("GET", "/v1/ready")

    def schema(self) -> JsonObject:
        return self._request("GET", "/v1/schema")

    def evaluate(self, action: Mapping[str, Any], *, idempotency_key: Optional[str] = None) -> JsonObject:
        return self._request("POST", "/v1/evaluate", body=dict(action), idempotency_key=idempotency_key)

    def evaluate_language_action(
        self,
        action_envelope: Mapping[str, Any],
        *,
        idempotency_key: Optional[str] = None,
    ) -> JsonObject:
        return self._request(
            "POST",
            "/v1/language/evaluate",
            body=dict(action_envelope),
            idempotency_key=idempotency_key,
        )

    def batch(self, actions: list[Mapping[str, Any]], *, idempotency_key: Optional[str] = None) -> JsonObject:
        return self._request(
            "POST",
            "/v1/batch",
            body=[dict(action) for action in actions],
            idempotency_key=idempotency_key,
        )

    def list_decisions(
        self,
        *,
        limit: Optional[int] = None,
        posture: Optional[str] = None,
    ) -> JsonObject:
        return self._request("GET", "/v1/decisions", query=_query(limit=limit, posture=posture))

    def get_decision(self, replay_id: str) -> JsonObject:
        return self._request("GET", f"/v1/decisions/{_path_token(replay_id)}")

    def review_decision(
        self,
        replay_id: str,
        review: Mapping[str, Any],
        *,
        idempotency_key: Optional[str] = None,
    ) -> JsonObject:
        return self._request(
            "POST",
            f"/v1/decisions/{_path_token(replay_id)}/reviews",
            body=dict(review),
            idempotency_key=idempotency_key,
        )

    def list_reviews(self, replay_id: str) -> JsonObject:
        return self._request("GET", f"/v1/decisions/{_path_token(replay_id)}/reviews")

    def pilot_metrics(self) -> JsonObject:
        return self._request("GET", "/v1/pilot/metrics")

    def review_queue(
        self,
        *,
        limit: Optional[int] = None,
        posture: Optional[str] = None,
        status: Optional[str] = None,
    ) -> JsonObject:
        return self._request(
            "GET",
            "/v1/review-queue",
            query=_query(limit=limit, posture=posture, status=status),
        )

    def security_events(self, *, limit: Optional[int] = None) -> JsonObject:
        return self._request("GET", "/v1/security-events", query=_query(limit=limit))

    def issue_permit(self, payload: Mapping[str, Any]) -> JsonObject:
        return self._request("POST", "/v1/permits/issue", body=dict(payload))

    def prepare_permit(self, payload: Mapping[str, Any]) -> JsonObject:
        return self._request("POST", "/v1/permits/prepare", body=dict(payload))

    def consume_permit(self, payload: Mapping[str, Any]) -> JsonObject:
        return self._request("POST", "/v1/permits/consume", body=dict(payload))

    def exchange_token(self, payload: Mapping[str, Any]) -> JsonObject:
        return self._request("POST", "/v1/auth/token", body=dict(payload))

    def _request(
        self,
        method: str,
        path: str,
        *,
        body: Optional[Any] = None,
        idempotency_key: Optional[str] = None,
        query: Optional[Mapping[str, Any]] = None,
    ) -> JsonObject:
        url = f"{self.base_url}{path}"
        if query:
            url = f"{url}?{urlencode(query)}"
        headers = {
            "Accept": "application/json",
            "User-Agent": self.user_agent,
        }
        data = None
        if body is not None:
            data = json.dumps(body, separators=(",", ":"), sort_keys=True).encode("utf-8")
            headers["Content-Type"] = "application/json"
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        if idempotency_key:
            headers["Idempotency-Key"] = idempotency_key

        request = Request(url, data=data, headers=headers, method=method)
        try:
            with urlopen(request, timeout=self.timeout) as response:
                return _decode_json_response(response.read())
        except HTTPError as exc:
            body_data = _decode_json_response(exc.read())
            code = str(body_data.get("error") or body_data.get("code") or "http_error")
            message = str(body_data.get("message") or body_data.get("detail") or exc.reason)
            raise SMERCAPIError(exc.code, code, message, body_data) from exc
        except URLError as exc:
            raise ConnectionError(f"Could not reach SMERC API at {self.base_url}: {exc.reason}") from exc


def _decode_json_response(data: bytes) -> JsonObject:
    if not data:
        return {}
    try:
        decoded = json.loads(data.decode("utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError("SMERC API returned invalid JSON") from exc
    if not isinstance(decoded, dict):
        raise ValueError("SMERC API returned a non-object JSON response")
    return decoded


def _query(**values: Any) -> dict[str, Any]:
    return {key: value for key, value in values.items() if value is not None}


def _path_token(value: str) -> str:
    if not value or "/" in value or "?" in value or "#" in value:
        raise ValueError("path identifier must be non-empty and cannot contain path separators")
    return value
