from __future__ import annotations

from typing import Any, Mapping

from reference_engine.ephemeral_execution_envelope import (
    _identifier,
    _sha256,
    _timestamp,
    canonical_digest,
    verify_envelope,
)


VERSION = "smerc.trace-export-candidate.v1"
TRACE_PROFILE = "tag:agentrust-io.com,2026:trace-v0.2"


def export_trace_candidate(
    envelope: Mapping[str, Any], *, issued_at: int, subject: str,
    model_provider: str, model_id: str, runtime_platform: str,
    runtime_measurement: str, data_class: str,
    tool_transcript_sha256: str, tool_call_count: int,
) -> dict[str, Any]:
    issued_at = _timestamp(issued_at, "issued_at")
    verified = verify_envelope(envelope, now=issued_at, allow_expired=True)
    if isinstance(tool_call_count, bool) or not isinstance(tool_call_count, int) or tool_call_count < 0:
        raise ValueError("tool_call_count must be a non-negative integer")
    subject = _identifier(subject, "subject")
    model_provider = _identifier(model_provider, "model_provider")
    model_id = _identifier(model_id, "model_id")
    runtime_platform = _identifier(runtime_platform, "runtime_platform")
    runtime_measurement = _identifier(runtime_measurement, "runtime_measurement")
    data_class = _identifier(data_class, "data_class")
    tool_transcript_sha256 = _sha256(tool_transcript_sha256, "tool_transcript_sha256")
    claim = {
        "eat_profile": TRACE_PROFILE,
        "iat": issued_at,
        "subject": subject,
        "model": {"provider": model_provider, "model_id": model_id},
        "runtime": {"platform": runtime_platform, "measurement": runtime_measurement},
        "policy": {"bundle_hash": "sha256:" + verified["policy_bundle_sha256"], "enforcement_mode": "enforce"},
        "data_class": data_class,
        "tool_transcript": {"hash": "sha256:" + tool_transcript_sha256, "call_count": tool_call_count},
        "smerc_extension": {
            "envelope_id": verified["envelope_id"],
            "envelope_sha256": verified["envelope_sha256"],
            "state": verified["state"],
            "execution_target_sha256": verified["execution_target_sha256"],
            "permit_id": verified["permit_id"],
            "replay_id": verified["replay_id"],
            "ephemeral_ref": verified["ephemeral_ref"],
        },
    }
    return {
        "version": VERSION,
        "conformance_status": "unverified",
        "signed": False,
        "hardware_attested": False,
        "claim_sha256": canonical_digest(claim),
        "claim": claim,
        "boundary": (
            "This is an unsigned TRACE-shaped export candidate. It is not a conformant TRACE Trust Record, "
            "does not establish issuer trust, and does not provide hardware attestation or transparency anchoring."
        ),
    }
