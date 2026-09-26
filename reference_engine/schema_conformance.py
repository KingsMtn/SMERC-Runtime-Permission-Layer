"""Optional standards-based validation for SMERC JSON contracts."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SCHEMA_DIR = ROOT / "schemas"


class SchemaConformanceUnavailable(RuntimeError):
    """Raised when the optional JSON Schema dependency is unavailable."""


def _jsonschema_modules():
    try:
        from jsonschema import ValidationError, validators
        from jsonschema.exceptions import SchemaError
    except ImportError as exc:
        raise SchemaConformanceUnavailable(
            "Install requirements-schema-validation.txt to run schema conformance checks."
        ) from exc
    return ValidationError, SchemaError, validators


def _load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"Unable to load JSON from {path}: {exc}") from exc


def validate_schema_document(schema: dict[str, Any]) -> None:
    """Validate a schema against the metaschema declared by its dialect."""
    _, _, validators = _jsonschema_modules()
    validator_class = validators.validator_for(schema)
    validator_class.check_schema(schema)


def validate_instance(instance: Any, schema: dict[str, Any]) -> None:
    """Validate one JSON value against a SMERC schema."""
    _, _, validators = _jsonschema_modules()
    validator_class = validators.validator_for(schema)
    validator_class.check_schema(schema)
    validator_class(schema).validate(instance)


def validate_schema_catalog(schema_dir: Path = DEFAULT_SCHEMA_DIR) -> dict[str, Any]:
    """Validate every JSON Schema document in a directory."""
    files = sorted(schema_dir.glob("*.schema.json"))
    results: list[dict[str, str]] = []
    for path in files:
        try:
            schema = _load_json(path)
            if not isinstance(schema, dict):
                raise ValueError("schema root must be an object")
            validate_schema_document(schema)
            results.append({"path": str(path), "status": "valid"})
        except Exception as exc:  # Report the whole catalog in one run.
            results.append({"path": str(path), "status": "invalid", "error": str(exc)})

    invalid = [item for item in results if item["status"] == "invalid"]
    return {
        "version": "smerc.schema-conformance.v1",
        "schema_directory": str(schema_dir),
        "schema_count": len(files),
        "valid_count": len(files) - len(invalid),
        "invalid_count": len(invalid),
        "status": "PASS" if files and not invalid else "FAIL",
        "results": results,
    }


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Validate SMERC JSON Schema contracts.")
    parser.add_argument("--schema-dir", type=Path, default=DEFAULT_SCHEMA_DIR)
    parser.add_argument("--schema", type=Path)
    parser.add_argument("--instance", type=Path)
    parser.add_argument("--pretty", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    if bool(args.schema) != bool(args.instance):
        raise SystemExit("--schema and --instance must be supplied together")

    if args.schema:
        schema = _load_json(args.schema)
        instance = _load_json(args.instance)
        if not isinstance(schema, dict):
            raise SystemExit("schema root must be an object")
        try:
            validate_instance(instance, schema)
            report = {
                "version": "smerc.schema-conformance.v1",
                "status": "PASS",
                "schema": str(args.schema),
                "instance": str(args.instance),
            }
        except Exception as exc:
            report = {
                "version": "smerc.schema-conformance.v1",
                "status": "FAIL",
                "schema": str(args.schema),
                "instance": str(args.instance),
                "error": str(exc),
            }
    else:
        report = validate_schema_catalog(args.schema_dir)

    print(json.dumps(report, indent=2 if args.pretty else None, sort_keys=True))
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
