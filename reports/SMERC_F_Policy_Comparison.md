# SMERC-F Policy Comparison Report

## Purpose

Compare identical proposed financial actions under conservative, balanced, and permissive reference policies. The profiles demonstrate calibration behavior; they are not institution-approved limits.

## Summary

- Actions evaluated: 5
- Actions with different policy outcomes: 3 (60.0%)
- Actions preserving monotonic restraint: 5 (100.0%)

| Action | Conservative | Balanced | Permissive | Different? |
| --- | --- | --- | --- | --- |
| TREASURY_REBALANCE_ROUTINE | `ALLOW` | `ALLOW` | `ALLOW` | No |
| STABLECOIN_DEPEG_REALLOCATION | `DENY` | `FREEZE` | `FREEZE` | Yes |
| COUNTERPARTY_EXPOSURE_INCREASE | `THROTTLE` | `THROTTLE` | `ALLOW` | Yes |
| UNAUTHORIZED_RESERVE_TRANSFER | `DENY` | `DENY` | `DENY` | No |
| MODEL_DISAGREEMENT_COLLATERAL_POST | `FREEZE` | `FREEZE` | `THROTTLE` | Yes |

## Interpretation

A conservative policy should never be less restrictive than the balanced profile for the same input, and the balanced profile should never be less restrictive than the permissive profile. Differences identify actions that require institution-specific calibration and reviewer testing.

