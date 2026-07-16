# SMERC Agent Handshake Integration

This folder shows the smallest safe pattern for connecting an agent runner to SMERC:

1. Build a `smerc.agent_handshake.v1` request.
2. Call the authenticated `POST /v1/agent/handshake` endpoint through the SDK.
3. Convert the SMERC posture into an agent-runner state.
4. Execute only when the posture and required controls allow it.
5. Preserve the replay identifiers.

This integration is deliberately conservative. It does not execute the proposed action. It produces a runner report that an agent framework, workflow runner, or integration partner can wire into its own execution boundary.

## Runner State Mapping

| SMERC posture | Runner state | Execution behavior |
| --- | --- | --- |
| `ALLOW` | `execute` | May proceed while retaining replay evidence. |
| `THROTTLE` | `constrained_execute` | May proceed only after applying required controls. |
| `FREEZE` | `pause` | Must pause automation and obtain review. |
| `DENY` | `block` | Must block automated execution. |
| `ESCALATE` | `escalate` | Must route to review or higher-authority handling. |

## Local Use

Start the SMERC API:

```bash
python api_server.py --host 127.0.0.1 --port 8788 --audit-db :memory: --allow-unauthenticated
```

Run the integration:

```bash
python integrations/agent_handshake/agent_handshake_runner.py \
  --api-url http://127.0.0.1:8788 \
  --handshake-file examples/agent_handshake_request.json \
  --pretty
```

Authenticated pilots should pass `--token` or set `SMERC_API_TOKEN`.

## Boundary

This is not an agent framework, sandbox, IAM system, policy engine, or execution environment. It is a reference adapter pattern showing how an outside agent should treat SMERC output before it acts.
