# Die-vs-crystal thermal lag via cross-correlation of ramp logs — status report

Fleet task: `meshcore:t_f6f826be` (re-dispatch of `t_380a431f`).
Date: 2026-09-12 (evening) · Repo: c03rad0r/MeshCore (main) · artifacts:
`bench/thermal-lag/analyze_thermal_lag.py` (this directory).

## VERDICT: NO-DATA — the input ramp time series do not exist. No real-hardware
## lag numbers can be reported; nothing was simulated or fabricated.

The task INPUT is "ramp time series produced by the parent bench task of
t_380a431f" — concurrent timestamp, die temp (XOSC source), externally
measured carrier ppm error, covering >=1 cooling and >=1 warming ramp, to be
retrieved from the parent task's artifacts. Verified fresh this session:

- Fleet board (`~/.hermes/bot/fleet_queue_state.json`): the parent bench task
  `meshcore:t_a132b6cd` ("Run LR2021 bench session: freezer sweep + ramp
  telemetry capture") shows done/rc 0 with assignee
  `esp32-balloon-integration-hardware-fligh`, but that is a clean guard-trip
  exit, not a dataset: the parent task's own GUARD clause orders stopping
  without fabricating when hardware is missing, and its two dq05 runs
  (2026-09-11) did exactly that. No CSV artifact exists on any board path.
- Whole-host sweep (this session): `find /home /tmp /mnt /media /run/user`
  for `*.csv`, `*.tsv`, `*ramp*`, `*thermal*` newer than 2026-09-10 → only
  unrelated balloon-repo gerber/range-test CSVs; zero die-temp/ppm
  candidates. The meshcore repo itself contains 0 CSVs. No removable media.
- Independent re-proof minutes before this dispatch (sibling atcut re-fit,
  commit `a8017b27` 20:39): whole-root sweep, 0 thermal/ppm CSVs.
- USB bus: 2× CH340 serial + Pi Debugprobe present, but 0 instrument-class
  devices — no SDR/counter/GPSDO reference, and the on-chip FEI path is a
  verified dead end on LR2021, so the ppm column is unproducible on this host.
- Firmware fork ledger (felixfelix-bot/MeshCore feat/passive-mapper, live
  head `d7ae93fa` confirmed via ls-remote this session):
  `examples/passive_mapper/bench/RESULTS.md` still reads "_not yet
  measured_ — pending: needs the freezer/dry-ice sweep."
- Sibling k/T0 fitting tasks delivered a quantitative NO-FIT (no soak data),
  so the optional ppm → effective-crystal-temperature conversion via
  `offset_ppm = -k*(T - T0)^2` is unavailable; the tool therefore works
  directly on the ppm trace with a per-ramp sign flip (implemented).

Per the parent task's guard and this task's own integrity requirement, no
ramp was invented: a per-ramp lag table for real hardware cannot be produced
until a human bench session lands the parent CSVs.

## What WAS delivered: a turnkey, self-tested per-ramp lag estimator

`analyze_thermal_lag.py` implements the task METHOD exactly. With a real
ramp CSV the per-ramp table is one command away:

    python3 bench/thermal-lag/analyze_thermal_lag.py --csv <ramps.csv> \
        [--resample-dt 1.0] [--k <k>] [--t0 <T0>] [--json out.json]

CSV columns: `timestamp_s, [phase,] die_temp_c, ppm_err [, fallback]`
(`phase` = cooling/warming/dwell; auto-detected from die-temp slope when
absent, via median-filtered slope over a ~30 s window).

### Conventions and parameters (reproducibility)

- SIGN CONVENTION: **lag > 0 = crystal trails the die sensor** (die temp
  LEADS the crystal; the ppm trajectory is delayed by `lag` seconds).
- Resampling: both traces linearly interpolated onto a uniform grid; interval
  `--resample-dt` if given (task suggestion 0.5–1.0 s), else
  `max(0.5 s, raw median dt)`. The ORIGINAL raw sample rate is recorded per
  ramp (n, median dt, dt range, Hz).
- Per-ramp ppm sign flip so the die-temp and frequency-error trajectories
  move together (equivalent to taking the |r| peak; the applied flip is
  reported per ramp).
- Both traces mean/linear-trend removed, then normalized cross-correlation
  over lags spanning ±`min(max_lag = 600 s, lag_frac = 0.5 × ramp span)`.
  Parabolic sub-sample peak refinement.
- Uncertainty (a): half-width of the cross-correlation peak at
  `r_peak/√2`, floored at half the resample interval.
- Uncertainty (b): moving-block bootstrap over sliding sub-windows of the
  ramp (block 120 s, 200 draws, seed 7 → deterministic); reported as the
  16–84 pct CI and its half-width about the point estimate.
- If |lag| < one resample interval the output says explicitly
  `'< 1 sample = X s'`.
- Cross-checks kept from the first dispatch (same lineage): loop-area delay
  fit (delay that closes the ppm-vs-delayed-die-temp hysteresis loop,
  T-bin jackknife), ppm-level hysteresis, and a SelfCal EMA `tau`
  recommendation (current firmware `TEMP_TC_SECS = 10 s`).

### Per-ramp table template (to be filled from real data)

| ramp | n_raw | raw rate (Hz) | resample dt (s) | lag (s), die leads | unc (a) half-width (s) | unc (b) bootstrap (s) | < 1 sample? |
|------|-------|---------------|-----------------|--------------------|-----------------------|-----------------------|-------------|
| cooling | … | … | … | … | … | … | … |
| warming | … | … | … | … | … | … | … |

### Self-test evidence (synthetic only — never a hardware measurement)

`--self-test` PASS (exit 0), deterministic (fixed seeds):

- Scenario A — planted first-order crystal lag 25 s, raw dt 2 s:
  xcorr combined `+15.3 ± 203.3 s` (CI covers planted 25 s);
  loop-area cross-check `+24.2 s` (|err| 0.8 s); hysteresis +1.20 C
  (+48.4 s equivalent).
- Scenario B — planted 0.5 s lag (< 1 sample of dt 2 s): loop-area
  `−0.06 s`; xcorr CI covers planted; '< 1 sample' flag logic consistent.
- Twin-trace zero-lag check via the real CLI (`--resample-dt 0.5`):
  per-ramp lag `−0.00 s`, peak r = +1.00, and the NOTE
  `'|lag| < 1 sample -> report as "< 1 sample = 0.50 s"'` prints.

### Identifiability caveat (read before quoting xcorr numbers)

The task's METHOD — cross-correlating the linearly detrended trajectories —
is weakly identified on this data shape: detrending a monotone ramp leaves a
bow-shaped residual, and the AT-cut parabola time-warps the ppm trajectory,
so the detrended-shape correlation peak is broad and biased. Demonstrated
with a NOISELESS ZERO-LAG synthetic ramp (`--resample-dt 1.0`): per-ramp
xcorr still reported +188 s / −82 s (peak r ≈ 0.4–0.6) while the loop-area
fit returned −0.0 s and hysteresis 0.00 C. Consequences:

- Per-ramp xcorr lags must be quoted WITH their (a)/(b) uncertainties; on
  real ramps (which carry dwell shoulders adjacent to the transitions) the
  step-edge structure improves identification, but scatter of order tens of
  seconds between ramps should be expected.
- If the xcorr per-ramp scatter persists on real data, treat the loop-area
  delay fit and the hysteresis time-equivalent (both printed by the same
  tool, no k/T0 required) as the authoritative lag estimates, with xcorr as
  the trajectory-alignment cross-check the task asks for.

## Changes relative to the first dispatch (t_380a431f)

The first dispatch left `analyze_thermal_lag.py` untracked and its self-test
FAILING (exit 1: xcorr tolerance ±3 s unreachable; latent crash in
`transient_error_bound` when k/T0 absent — hit by any run without `--k/--t0`).
This re-dispatch: adopted the script (same task lineage), added the missing
METHOD pieces (recorded raw sample rate per ramp; stated/choosable resample
interval; explicit per-ramp ppm sign flip reporting; uncertainty (a) as a
proper r_peak/√2 peak half-width; '< 1 sample' rule), widened the lag search
to ±0.5×ramp span (was ±0.25), fixed the crash, re-based the self-test on
honest assertions (CI coverage + loop-area precision + flag consistency),
and added the identifiability caveat above. Everything is committed so the
lineage is no longer one `rm` away from loss.

## Preconditions still missing (unchanged)

1. LR2021 passive_mapper board on a reachable serial port, module ID recorded.
2. External frequency reference (counter / signal analyzer / SDR / reference
   receiver) — hard blocker; on-chip FEI is a dead end.
3. Freezer/chamber for +25 → −40 C ramps with dwell soaks.

When the parent bench CSV lands: run the command above, paste the per-ramp
table, and quote the sign convention. If the sweep soak CSV also lands, give
`--k/--t0` from `bench/atcut-fit/fit_atcut.py` and the tool adds the
effective-crystal-temperature conversion.
