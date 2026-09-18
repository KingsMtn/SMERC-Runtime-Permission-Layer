# AWS Execution-Boundary Contrast Report

- Source action families: **2**
- Evaluated variants: **4**
- Postures: `{'FREEZE': 2, 'THROTTLE': 2}`
- Every broad variant stricter: **true**

## Comparisons

### aws-open-agentcore-create-runtime-002

- Bounded: `THROTTLE` / `REVIEW_REQUIRED`
- Broad: `FREEZE` / `PAUSE`
- Broad is stricter: **true**
- Bounded reasons: `['EXTERNAL_SIDE_EFFECT']`
- Broad reasons: `['IRREVERSIBLE_EXPOSURE_ELEVATED', 'EXTERNAL_SIDE_EFFECT', 'HOST_ISOLATION_WEAK', 'PRODUCTION_NETWORK_REACHABLE', 'TOOLING_AUTHORITY_BROAD', 'SANDBOX_ESCAPE_OR_CREDENTIAL_SURFACE']`

### aws-open-bedrock-invoke-004

- Bounded: `THROTTLE` / `REVIEW_REQUIRED`
- Broad: `FREEZE` / `PAUSE`
- Broad is stricter: **true**
- Bounded reasons: `['EXTERNAL_SIDE_EFFECT']`
- Broad reasons: `['EXTERNAL_SIDE_EFFECT', 'HOST_ISOLATION_WEAK', 'PRODUCTION_NETWORK_REACHABLE', 'TOOLING_AUTHORITY_BROAD', 'SANDBOX_ESCAPE_OR_CREDENTIAL_SURFACE']`

## Evidence Boundary

Boundary variants are controlled SMERC fixtures derived from public AWS action descriptions. They are not observed AWS configurations, customer outcomes, or proof of deployed enforcement.
