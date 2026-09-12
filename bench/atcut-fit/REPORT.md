# AT-cut (k, T0) fit from freezer-sweep dwell data — status report

Task: fit `offset_ppm = -k*(T - T0)^2` per LR2021 module from the parent bench
task's soak CSV and emit the exact `cal <k> <T0>` serial-CLI line.

Date: 2026-09-12 · Repo: c03rad0r/MeshCore (main @ 07a3ca9e) · artifacts:
`bench/atcut-fit/fit_atcut.py` (this directory).

## VERDICT: BLOCKED — the input data does not exist. No (k, T0) fitted, no
## `cal` command issued. Everything else in the task was delivered.

The parent bench task ("LR2021 bench session: freezer sweep + ramp telemetry
capture") guard-tripped twice and never produced its CSV deliverable:

- Session `20260911_182734_ad7190` (2026-09-11): guard report — no external
  frequency reference on the USB bus (no SDR/counter/GPSDO; on-chip FEI path is
  a verified dead end on LR2021), no chamber control, board identity
  unverified. "no CSV was written and no commit was made."
- Session `20260911_214554_f2c910` (2026-09-11, re-dispatch): same outcome.
  "No CSV was produced, nothing was changed, nothing committed."
- The sibling thermal-lag task (2026-09-12) independently swept this host:
  no thermal die-temp/ppm CSV exists anywhere (all CSV hits are PER/RSSI
  sweeps from the unrelated e80 bench).
- The firmware fork's own calibration ledger,
  `examples/passive_mapper/bench/RESULTS.md` @ d7ae93fa
  (felixfelix-bot/MeshCore feat/passive-mapper), still reads:
  `| _not yet measured_ | SkyMapper Board A (LR2021) | ... pending: needs the
  freezer/dry-ice sweep |` — the fork author has no measurement either.

Per the parent task's guard and this task's step 2, no fit is forced and no
measurement is fabricated. There is nothing to fit: zero soak points exist.

## What WAS delivered

### 1. Firmware-verified `cal` CLI contract (read at the pinned commit)

Firmware: felixfelix-bot/MeshCore, branch `feat/passive-mapper`,
commit `3fdfbc8e` ("BW125 runtime fallback, cal-range predicate, cal-blob
writer"), file `examples/passive_mapper/MyMesh.cpp`, `MyMesh::handleCommand`:

- Command form: `cal <k> <T0>` — **k in ppm/C^2, T0 in C** (comment in the
  handler: "k in ppm/C^2, T0 in C"). k must satisfy **k >= 0** (negative k →
  usage error). k is the parabola MAGNITUDE (positive).
- Number grammar — the handler uses a custom `parseFloat` (avoids ~16 KB of
  scanf float machinery): `[-+]?digits[.digits]`, with
  - a **leading digit REQUIRED** — `cal .034 25` is REJECTED (`.034` fails);
    write `cal 0.034 25`.
  - **no exponent support** — `1e-2` parses as `1` and leaves `e-2` as
    trailing garbage (the T0 parse then fails → usage error).
  - leading spaces/tabs skipped; a trailing dot is fine (`25.` → 25.0).
- Firmware reply on success: `cal k=%.6g T0=%.2fC -> persisted (valid=yes)`
  (or `RAM only, file write failed` if the FS write fails).
- `MyMesh::writeCalBlob(k, t0)` path: `SelfCal::setCalibration(k, t0)` →
  serializes a **15-byte blob** — `2× f32 little-endian (k, T0)` + spare f32
  (0.0) + `u16 magic 0x5343` + `u8 version` — removes then rewrites
  `/selfcal.dat` (`MAP_CAL_FILE`, MyMesh.h:48).
- Model (`host/SelfCal.h` @ 3fdfbc8e): `offset_ppm = -k*(T-T0)^2`, thermal-lag
  EMA `TEMP_TC_SECS = 10 s`, output clamp ±300 ppm, validity band
  `CAL_RANGE_C = 60 C` around T0.

Emission format (what the fitter prints): **`cal %.6g %.2f`** — identical to
the fork's own bench kit (`bench/calib.py::cal_command` at branch head).

Post-pin drift (branch head `d7ae93fa`, 3 commits after `3fdfbc8e`), for
awareness — does NOT change the `cal` command semantics (k stays a positive
magnitude):
- `d83b3660`: the APPLIED compensation sign was corrected
  (`applied_offset_ppm = +k*(T-T0)^2 = -drift_ppm`; the old code doubled the
  error) and `CAL_RANGE_C` widened 60 → 90 C.
- `4a25db04`/`d7ae93fa`: bench calibration kit (soak/edgescan/fit/ramp/hyst)
  and docs — still with zero measured rows.

### 2. Turnkey fitter: `fit_atcut.py`

Implements the task METHOD exactly and refuses unfit data:

    python3 bench/atcut-fit/fit_atcut.py --csv <soak.csv> --module <board-id> [--json out.json]
    python3 bench/atcut-fit/fit_atcut.py --self-test

- OLS quadratic `offset_ppm = a*T^2 + b*T + c` → **k = -a, T0 = -b/(2a)**.
- Sanity gates (each PASS/WARN/FAIL, with numbers): n ≥ 4 soak points; T span
  ≥ 20 C; parabola opens downward (a < 0 ⇔ k > 0 — FAIL refuses); k within
  0.005–0.15 ppm/C² (LR2021-class AT-cut ~0.03–0.04); T0 in a plausible
  room-temperature band (warn outside 15–40 C); T0 bracketed by the sweep
  (single-sided sweep ⇒ (k, T0) not identifiable ⇒ refuse; ≤ 2 C outside the
  swept end counts as bracketed); bias delta `c − (−k·T0²)` reported (static
  reference/initial-tolerance offset the cal cannot correct); R² ≥ 0.95;
  leave-one-out stability of (k, T0).
- Per-point residuals, rms, R², LOO swings printed for every fit.
- On a clean fit it prints the verbatim command `cal %.6g %.2f`, **round-trips
  it through a Python port of the firmware's own `parseFloat`** (incl. the
  k ≥ 0 CLI gate) so the emitted line is verifiably parser-compatible, plus
  the expected firmware reply and the 15-byte blob hex for
  rebuild-after-reflash.
- Exit code 0 only when a fit passed all gates and its command verified.

`--self-test` (synthetic data only — never a hardware measurement) passes
6/6: recovery on a bracketed sweep (k err 2e-5 ppm/C², T0 err 0.05 C);
refusal on upward curvature; refusal on a single-sided (unbracketed) sweep;
refusal on n < 4; firmware-parser grammar quirks (`.5` rejected, `1e-2`
degrades to `1` + garbage, `25.` ok); pure-Python no-numpy solver agrees with
numpy polyfit to 1e-13.

## Ready-to-issue command (TEMPLATE ONLY — cannot be filled without data)

    cal <k_ppm_per_C2> <T0_C>        e.g. format: cal 0.034021 24.95

Rules: k ≥ 0, leading digit before any decimal point, no exponent, 6
significant digits for k and 2 decimals for T0 are plenty for the f32 blob.
When the soak CSV exists, the fitter prints the exact line — copy-paste it to
the module's serial CLI, then confirm with `calshow`
(`valid=yes k=... T0=...C die_temp=... off_hz=...`).

DO NOT copy constants between boards: k/T0 are per-module (per-crystal)
quantities. The illustrative `cal 0.0340211 24.95` above comes from the
SELF-TEST's synthetic generator — it is not a measurement and must never be
issued to real hardware.

## Preconditions still missing (unchanged from the parent task's guard)

1. LR2021 board confirmed running passive_mapper @ feat/passive-mapper on a
   reachable serial port, module ID (board + serial/markings) recorded.
2. External frequency reference (counter / signal analyzer / SDR / reference
   receiver) — the on-chip FEI path is a dead end on LR2021 and must not be
   used.
3. Freezer/chamber able to soak +25 → −40 C with die temp stable to ~0.5 C.

Once a real `soak.csv` (columns: `setpoint_c?, die_temp_c, offset_ppm[, phase]`)
lands in this directory, the fit + command is one command away.

## Session notes

- Fleet-queue state was NOT consulted this session (a read attempt was denied
  by the operator; not retried).
- The sibling's untracked `bench/thermal-lag/analyze_thermal_lag.py` was left
  untouched (not this task's artifact; still uncommitted in the worktree).
- Firmware fork fetched read-only to FETCH_HEAD; no remotes added, no pushes.
