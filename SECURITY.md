# Security Policy

## Current Status

SMERC is an MVP/reference implementation intended for controlled technical review and shadow-mode pilots. It is not currently represented as production-certified security infrastructure.

## Reporting Security Issues

Do not publish suspected vulnerabilities, secrets, or sensitive customer information in a public issue.

Use the repository owner's private GitHub contact path to report a suspected security issue and include:

- affected component
- reproduction steps
- potential impact
- suggested mitigation, if available

## Pilot Data Handling

A first pilot should provide action metadata rather than raw sensitive payloads. SMERC should not require production secrets, customer PII, private keys, raw credentials, full source-code contents, or privileged cloud credentials.

## Enforcement Warning

Do not use the reference thresholds for production blocking without threat modeling, calibration, accountable approval, override procedures, and an explicit fail-open/fail-closed decision.
