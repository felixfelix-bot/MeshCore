# Cooling-vs-warming thermal hysteresis — status report

Task: quantify thermal hysteresis — the die-temperature difference between
cooling and warming ramps at matched frequency-error levels (ppm) — as an
independent cross-check on die-vs-crystal lag.

Date: 2026-09-12 (initial); re-verified 2026-09-14 (third dispatch of
parent t_380a431f — NO-DATA verdict unchanged, tool self-test PASS) ·
re-verified 2026-10-01 (fourth dispatch, task t_474e6323 — verdict
unchanged, fresh evidence below) ·
Repo: c03rad0r/MeshCore (main) · artifacts:
`bench/thermal-hysteresis/hysteresis_fit.py` (this directory).

### Re-verification 2026-10-01 (fourth dispatch, t_474e6323)

Every check re-executed fresh this session; nothing taken on trust from
the 09-14 report:

- Tool: `--self-test` PASS, exit 0 (planted tau = 25.0 s recovered as
  tau_hyst = 24.4 s, |err| 0.56 s; median dT = +1.34 C, 7/7 levels,
  bootstrap CI [23.6, 25.9] s — synthetic validation only, as labeled).
- Availability gate on the parent deliverable:
  `--csv bench/ramp_session_t380a431f.csv` -> `CSV error: file not found`
  (exit 1). 0 cooling / 0 warming ramps => all statistics undefined.
- Filesystem: `find` (2026-09-14 → today, patterns
  ramp|soak|freezer|die_temp|thermal*.csv|session*.csv, /home/c03rad0r,
  caches pruned): ZERO hits — no bench session has run since 09-14.
- Repos: content grep for die_temp|measured_error_ppm|freq_err|xosc over
  meshcore, balloon, balloon-e80bench, e80-bench (*.csv/tsv/log/jsonl/
  parquet/md): zero files. Only CSVs on host remain the e80 PER/RSSI
  sweeps (header `idx,label,pkt_idx,...,rssi_dbm,snr_db,crc_ok,...` — no
  die-temp, no ppm-error column) plus meshcore's 2 mechanical tables
  (penetrations, feedthrough list).
- Kanban DB: the bench-session card (t_03259d94) and the entire prep
  chain (align t_96b58dfc, QC t_34efc124, package t_d05769b5, assemble
  t_e77f6e2d) are archived with ZERO runs/events; capture card t_a132b6cd
  never ran; no task_attachments anywhere in the family; the fleet-offload
  "done" probe card (t_75ddf77a) left no probe_report.json on disk.
- Sibling concurrence unchanged: thermal-lag REPORT (9b9fb897) and
  atcut-fit REPORT re-verified zero soak/ramp rows; parent guard-tripped
  twice 2026-09-11 (no external frequency reference on the USB bus).

VERDICT unchanged: NO DATA. Numeric hysteresis remains UNDEFINED and is
not fabricated.

## VERDICT: NO DATA — hysteresis not measurable. Median ΔT, spread, and
## per-level table are UNDEFINED because the input ramp time series does
## not exist. Nothing was fabricated; the turnkey analyzer is delivered and
## tool-verified.

### Quantitative gate (what the tool prints on the parent task's CSV)

The required input is the parent bench task's ramp CSV (t_380a431f). It does
not exist — running the analyzer against the expected deliverable fails the
availability gate before any statistics exist:

    $ python3 bench/thermal-hysteresis/hysteresis_fit.py --csv bench/ramp_session_t380a431f.csv
    CSV error: file not found: bench/ramp_session_t380a431f.csv   (exit 1)

Levels selectable without both ramp directions: 0 (need ≥1 cooling AND
≥1 warming ramp). With 0 levels, median ΔT, IQR, τ_hyst and the per-level
table are undefined — reported as such, not invented.

### Independent data re-scan (this session, fresh tool evidence)

- Repo-wide `*.csv` search inside meshcore: 0 files (bench/ holds only code,
  reports, and the sibling's uncommitted `analyze_thermal_lag.py`).
- Whole-root `find` for `*.csv|ramp|thermal|soak|freezer` newer than
  2026-09-08 (excluding /proc, /sys, caches, R fixtures): zero thermal
  die-temp/ppm candidates. All CSV hits are the unrelated balloon/e80
  PER/RSSI benches — headers inspected: `per_pct, rssi_avg_dbm, ...` /
  `power_dBm, pkt_count, rssi_avg, ...` — no `die_temp` or ppm-error column
  anywhere.
- Only one meshcore worktree exists (the main repo, this checkout).
- Corroborating committed verdicts: the parent bench task guard-tripped
  twice (sessions 20260911_182734_ad7190, 20260911_214554_f2c910 — no
  external frequency reference on the USB bus; "no CSV was written and no
  commit was made"), and the atcut-fit sibling's REPORT.md (same day)
  independently re-verified zero soak/ramp rows and no frequency-reference
  hardware to produce more.

### What WAS delivered: turnkey hysteresis analyzer

`hysteresis_fit.py` implements the task METHOD exactly, mirroring the
sibling thermal-lag conventions (same CSV column contract/aliases, same
phase-label trust + slope auto-detect segmentation, ≥120 s span / ≥3 °C
range / ≥20 rows per ramp, same linear-interp resampling):

    python3 bench/thermal-hysteresis/hysteresis_fit.py --csv <ramp.csv> [--json out.json]
        [--k 0.034] [--t0 25.0] [--n-levels 7]   (5–10 allowed)
    python3 bench/thermal-hysteresis/hysteresis_fit.py --self-test

1. Ramps loaded and resampled onto a common uniform time base — linear
   interpolation at dt = median sample interval of the whole series
   (interval and method stated in every output).
2. Parametric ppm-vs-die-temp curve per direction (time is the parameter).
3. `--n-levels` (default 7) ppm levels on the interior 80% of the two
   directions' ppm-range overlap; per level, die temp at the crossing on
   each direction via TIME-ORDERED bracketing + linear interpolation,
   median across bracketed crossings (robust to noise re-crossings).
   ΔT = T_warm − T_cool. Every level is reported; UNCOVERED levels are
   printed, never dropped; >2 °C crossing spread flags AMBIGUOUS.
4. Equivalent seconds via each ramp's average die-temp slew rate
   (|OLS slope| of die temp vs time): Δt_warm = ΔT/r_warm,
   Δt_cool = ΔT/r_cool, and the branch-agnostic lag estimate
   τ_hyst = ΔT/(r_warm + r_cool). Because both ramps each lag the crystal
   by τ, τ_hyst ≈ 2× the sibling's single-ramp xcorr lag when slews are
   equal — the explicit cross-check the task asked for.
   Per-ramp slew rates and the medians used are printed explicitly.
5. Optional --k/--t0 (atcut-fit deliverable): ppm levels expressed as
   effective crystal temperatures, T_xtal = T0 − sqrt((ppm − offset)/k),
   static offset from dwell rows. The sibling fit task delivered NO (k, T0)
   (BLOCKED — no soak data), so this path is exercised only in self-test.
   Moving-block bootstrap CI (200 reps) on median ΔT and τ_hyst.

Tool integrity, enforced by execution this session:

- `--self-test` (synthetic ramps with planted first-order crystal lag
  τ = 25 s, cooling 25→−20 °C @ 0.025 °C/s, warming −20→5 °C @ 0.030 °C/s,
  sensor noise 0.15 °C / ppm noise 0.05): PASS, exit 0. Recovered
  median ΔT = +1.34 °C vs expected τ·(r_w+r_c) = 1.38 °C; τ_hyst = 24.4 s
  (|err| 0.56 s); 7/7 levels covered; bootstrap CI [23.6, 25.9] s;
  Δt@warm = 44.8 s, Δt@cool = 53.8 s — slew conversion shown per level.
- Dwell-only CSV (labeled SYNTHETIC, `/tmp/hyst_refusal_demo_SYNTHETIC_dwell_only.csv`):
  quantitative NO-DATA verdict `{'cooling_ramps': 0, 'warming_ramps': 0,
  'dwell_runs': 1, 'usable_rows': 26}`, exit 1 — no statistics emitted.
- Missing CSV path: one-line `CSV error: file not found: ...`, exit 1.

## Unblock (unchanged from the parent task's guard)

A human bench session producing the ramp CSV — columns
`timestamp_s, phase, die_temp_c, ppm_err` (header aliases as in the sibling
contract), ≥1 cooling and ≥1 warming ramp, module ID recorded, external
frequency reference (the on-chip FEI path is a verified dead end on
LR2021). Then the deliverable is one command away:

    python3 bench/thermal-hysteresis/hysteresis_fit.py --csv ramp_session.csv --json hyst.json

## Session notes

- The sibling's untracked `bench/thermal-lag/analyze_thermal_lag.py` was
  left untouched (not this task's artifact; still uncommitted).
- One probe command bundling reads of /tmp e80 worktree files was denied by
  the approval layer; not retried — the data verdict rests on the
  independent scans above, which needed none of those paths.
- No pushes. Commit adds only this task's two files.
