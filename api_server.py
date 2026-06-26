from __future__ import annotations

import argparse
import json
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any, Dict

from reference_engine.recoverability_engine import RecoverabilityEngine, evaluate_batch


ENGINE = RecoverabilityEngine()


class SMERCRequestHandler(BaseHTTPRequestHandler):
    server_version = "SMERCRecoverabilityAPI/0.1"

    def do_GET(self) -> None:
        if self.path == "/health":
            self._write_json({"status": "ok", "service": "smerc-recoverability-api"})
            return
        if self.path == "/schema":
            self._write_json(schema())
            return
        self._write_json({"error": "not_found", "message": "Use /health, /schema, /evaluate, or /batch."}, HTTPStatus.NOT_FOUND)

    def do_POST(self) -> None:
        if self.path not in {"/evaluate", "/batch"}:
            self._write_json({"error": "not_found", "message": "Use /evaluate or /batch."}, HTTPStatus.NOT_FOUND)
            return

        try:
            payload = self._read_json()
            if self.path == "/evaluate":
                if not isinstance(payload, dict):
                    raise TypeError("/evaluate expects one JSON object.")
                result = ENGINE.evaluate(payload)
            else:
                if not isinstance(payload, list):
                    raise TypeError("/batch expects a JSON list.")
                result = evaluate_batch(payload)
            self._write_json(result)
        except (TypeError, ValueError, json.JSONDecodeError) as exc:
            self._write_json({"error": "bad_request", "message": str(exc)}, HTTPStatus.BAD_REQUEST)

    def _read_json(self) -> Any:
        length = int(self.headers.get("content-length", "0"))
        if length <= 0:
            raise ValueError("Request body is required.")
        body = self.rfile.read(length)
        return json.loads(body.decode("utf-8"))

    def _write_json(self, payload: Any, status: HTTPStatus = HTTPStatus.OK) -> None:
        body = json.dumps(payload, indent=2).encode("utf-8")
        self.send_response(status)
        self.send_header("content-type", "application/json; charset=utf-8")
        self.send_header("content-length", str(len(body)))
        self.send_header("access-control-allow-origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format: str, *args: Any) -> None:
        return


def schema() -> Dict[str, Any]:
    return {
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
        "postures": ["ALLOW", "THROTTLE", "FREEZE", "DENY", "ESCALATE"],
        "endpoints": {
            "GET /health": "service health",
            "GET /schema": "input shape",
            "POST /evaluate": "evaluate one action object",
            "POST /batch": "evaluate a list of action objects",
        },
    }


def run(host: str, port: int) -> None:
    server = ThreadingHTTPServer((host, port), SMERCRequestHandler)
    print(f"SMERC recoverability API listening on http://{host}:{port}")
    server.serve_forever()


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the SMERC recoverability API server.")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8788)
    args = parser.parse_args()
    run(args.host, args.port)


if __name__ == "__main__":
    main()
