# ILION-Bench v2 Replay

SMERC can replay public ILION-Bench v2 execution-safety scenarios through the recoverability engine.

ILION-Bench v2 is an external benchmark for agentic AI execution-safety gates. Its scenarios include an agent role, trigger text, proposed action, binary `ALLOW` / `BLOCK` ground truth, difficulty, and rationale.

Source: `https://zenodo.org/records/18929841`

## Why This Matters

ILION tests whether proposed agent actions should be allowed or blocked.

SMERC tests a related but different governance question:

> Is the proposed action recoverable enough to execute now, and if not, should it be throttled, frozen, denied, or escalated?

This makes ILION useful as an external benchmark for SMERC's runtime permission layer.

## Evidence Boundary

This replay does not use customer telemetry.

This replay does not prove production incident reduction.

This replay does not claim that ILION endorses SMERC.

The adapter maps ILION rows into SMERC recoverability signals using documented heuristics. Results should be treated as calibration evidence and benchmark alignment evidence, not market validation.

## Local Usage

Download `benchmark_v2.csv` from Zenodo into a local ignored path:

```bash
mkdir -p external_benchmarks/ilion_bench_v2
curl -L -o external_benchmarks/ilion_bench_v2/benchmark_v2.csv "https://zenodo.org/records/18929841/files/benchmark_v2.csv?download=1"
```

Run the replay:

```bash
python -m reference_engine.ilion_bench_replay external_benchmarks/ilion_bench_v2/benchmark_v2.csv --pretty
```

By default this writes:

- `reports/ilion_bench_v2_replay_report.json`
- `reports/ILION_Bench_v2_Replay_Report.md`

## Metrics

The replay reports:

- scenario count
- ILION expected verdict counts
- SMERC posture counts
- strict binary match rate
- governance-aligned rate
- middle-state rate
- average irreversible exposure by category
- conformance type counts

## Interpretation

The most important metric is not simple agreement with binary `ALLOW` / `BLOCK`.

The commercial question is whether SMERC adds useful runtime detail:

- `THROTTLE` when an action may be valid but should be constrained
- `ESCALATE` when evidence is incomplete or consequence is material
- `FREEZE` when execution should pause before irreversible harm
- `DENY` when the action is not structurally defensible

If external and customer datasets repeatedly show that SMERC middle states identify practical action paths, SMERC becomes easier to explain as a recoverability checkpoint rather than a generic AI safety filter.
