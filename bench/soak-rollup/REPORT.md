# Four-setpoint soak evidence — rollup table (final deliverable)

Task (fleet card `meshcore:t_6ece027b`): roll up the four per-setpoint
soak results (+25 C, 0 C, -20 C, -40 C) into one evidence table, backed
by the raw timestamped calshow logs.

Date: 2026-09-14, session 08:07-08:20 local (UTC+2) · Repo: meshcore ·
dispatch run_id `dq05-1789365793` (ownership ledger, this card status
`running`) · artifacts: this directory (`bench/soak-rollup/`).

## RESULT: all four soaks UNVERIFIED. No soak ran at any setpoint.

Zero calshow log lines exist for any setpoint — there is no measured
die-temp value, band, dwell, or timestamped window anywhere in this
campaign. Nothing was fabricated; every cell below reflects exactly
what the per-setpoint reports state.

## Evidence table (exactly four rows, one per setpoint)

| setpoint C | SOAK PASS/FAIL/UNVERIFIED | die-temp band observed (C, peak-to-peak) | dwell time (min) | timestamp range of soaked window | blocking reason (only when not PASS) |
|---|---|---|---|---|---|
| +25 | UNVERIFIED | none — 0 samples exist | 0 | N/A (no in-band samples; no sampling began) | "no calshow access" (gate A) + "parent stability task not PASS" (gate B); root cause: no chamber access |
| 0 | UNVERIFIED | none — 0 samples exist | 0 | N/A (no in-band samples) | "no calshow access" (gate A) + "parent stability task not PASS" (gate B); root cause: no chamber access |
| -20 | UNVERIFIED | none — 0 samples exist | 0 | N/A (no in-band samples; no sampling began) | "no calshow access" (gate A) + "parent stability task not PASS" (gate B); root cause: no chamber access |
| -40 | UNVERIFIED | none — 0 samples exist | 0 | N/A (no in-band samples; sampling never began) | "no calshow access" (gate A) + "parent stability task not PASS" (gate B) + "no chamber access" (root cause, gate C moot) |

Sources, one per row (used exactly as reported, nothing re-derived):

- +25 C — `bench/soak-25c/REPORT.md` (commit `114a397b`, verdict UNVERIFIED, zero samples)
- 0 C — `bench/soak-0c/REPORT.md` (commit `d16a2723`, verdict UNVERIFIED, zero samples)
- -20 C — `bench/soak-20c/REPORT.md` (commit `866d59cd`, verdict UNVERIFIED, zero samples)
- -40 C — `bench/soak-40c/REPORT.md` (commit `76f6a129`, verdict UNVERIFIED, zero samples)
- Harness dry-run note (shared gate-A input) — `bench/dryrun-ambient/REPORT.md` (commit `ea8b9c8e`, verdict DRY RUN FAIL, blocking reason "no calshow access")

## Raw timestamped calshow logs, one delimited block per setpoint

Per task step 3, each setpoint's log block is inlined below. The
harness log format is `iso8601,setpoint,chamber_air_c,die_temp_raw`
(`bench/dryrun-ambient/REPORT.md`, "Log-file format"). The die-temp
raw strings would be preserved byte-for-byte exactly as printed by
calshow. **No log line exists for any setpoint** — the dry run FAILED
(no calshow access), so no sampling loop ever started; each block is
deliberately empty and no log file exists on disk. No placeholder or
fabricated line appears in any block.

### calshow log — setpoint +25 C (fleet card `meshcore:t_3a34bea7`)

```
(no lines — 0 samples; sampling never began. Report: bench/soak-25c/REPORT.md)
```

### calshow log — setpoint 0 C (fleet card `meshcore:t_b0a5312a`)

```
(no lines — 0 samples; sampling never began. Report: bench/soak-0c/REPORT.md)
```

### calshow log — setpoint -20 C (fleet card `meshcore:t_35c19845`)

```
(no lines — 0 samples; sampling never began. Report: bench/soak-20c/REPORT.md)
```

### calshow log — setpoint -40 C (fleet card `meshcore:t_e3bb0dba`)

```
(no lines — 0 samples; sampling never began. Report: bench/soak-40c/REPORT.md)
```

### Chamber-air vs die-temp cross-check

**Not possible — zero samples.** The log format records chamber air
temp alongside die temp precisely so they can be cross-checked, but
no sample exists for any setpoint: no calshow reply was ever received
(no calshow access), and no chamber exists under this host's control
to provide an air-temp reading (chamber-reservation report `7d9227a1`:
NO BOOKING EXISTS; no chamber present, located, or commandable). There
is no measured pair to cross-check.

## Blocking ingredients per setpoint (exact vocabulary from the task)

- **+25 C** — "no calshow access" (gate A: dry-run verdict FAIL —
  calshow reachable NO, serial access operator-denied, zero console
  bytes, log file `calshow_ambient.log` never created) and "parent
  stability task not PASS" (gate B: holds card `t_0e98e408` done with
  no PASS verdict anywhere). Root cause: "no chamber access".
- **0 C** — "no calshow access" (gate A: the dry-run task never
  completed to a pass; ownership status `claimed` at the time of the
  0 C report, then completed to FAIL) and "parent stability task not
  PASS" (gate B: no PASS verdict for 0 C exists). Root cause: "no
  chamber access". Gate C (+25 C not finished) noted moot.
- **-20 C** — "no calshow access" (gate A: dry run FAIL — reachable
  NO, zero console bytes) and "parent stability task not PASS" (gate
  B: no PASS verdict for -20 C exists). Root cause: "no chamber
  access". Gate C (0 C done) noted moot.
- **-40 C** — "no calshow access" (gate A: dry run FAIL), "parent
  stability task not PASS" (gate B: no PASS verdict for -40 C exists),
  root cause "no chamber access"; gate C (-20 C never started) noted
  moot — no chamber exists to release.

## Provenance of every reported value (no re-derivation)

| value | source (verbatim) |
|---|---|
| +25 C verdict/band/dwell/window | bench/soak-25c/REPORT.md: "SOAK verdict for +25 C: **UNVERIFIED**", "die-temp band observed (C, peak-to-peak): **none — 0 samples exist**", "dwell time (min): **0**", "timestamp range of soaked window: **N/A (no in-band samples; no sampling began)**" |
| 0 C verdict/band/dwell/window | bench/soak-0c/REPORT.md: "SOAK verdict for 0 C: **UNVERIFIED**", "die-temp band observed (C, peak-to-peak): **none — 0 samples exist**", "dwell time (min): **0**", "timestamp range of soaked window: **N/A (no in-band samples)**" |
| -20 C verdict/band/dwell/window | bench/soak-20c/REPORT.md: "SOAK verdict for -20 C: **UNVERIFIED**", "die-temp band observed (C, peak-to-peak): **none — 0 samples exist**", "dwell time (min): **0**", "timestamp range of soaked window: **N/A (no in-band samples; no sampling began)**" |
| -40 C verdict/band/dwell/window | bench/soak-40c/REPORT.md: "SOAK verdict for -40 C: **UNVERIFIED**", "die-temp band observed (C, peak-to-peak): **none — 0 samples exist**", "dwell time (min): **0**", "timestamp range of soaked window: **N/A (no in-band samples; sampling never began)**" |
| dry-run gate-A verdict | bench/dryrun-ambient/REPORT.md: "VERDICT: DRY RUN FAIL", "calshow reachable: NO", blocking reason "no calshow access" |

No number in this rollup was re-derived, inferred, or extrapolated.
Every reported value is a verbatim transcription from the per-setpoint
reports; every UNVERIFIED field traces to the absence of timestamped
log lines, which was re-verified this session (filesystem sweep: no
`*calshow*`/`*soak*` log artifact exists anywhere on the host; the
dry-run data log `bench/dryrun-ambient/calshow_ambient.log` does not
exist).

## What this means for the campaign

No PASS row exists, so the campaign-level outcome is: the soak
evidence cannot support any calibration claim at any setpoint. The
complete unblock path (operator bench work, per the fork's bench
README — not agent work) is recorded in each per-setpoint report:
provision/locate a real thermal chamber and prove it holds each
setpoint (parent holds card `t_0e98e408` re-run with logs), sanction
serial access and re-run the dry run (`bench/dryrun-ambient/sample_calshow.py
--samples 3`) to flip the gate-A verdict, attach the LR2021 DUT, then
re-run the four soaks front-to-back (+25 → 0 → -20 → -40 C).