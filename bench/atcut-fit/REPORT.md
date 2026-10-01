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

> 2026-09-12 follow-up: the full end-to-end argument spec (serial framing,
> parser grammar, precision/ulp analysis, blob byte layout, edge-case
> matrix) now lives in `CAL-CLI-SPEC.md` in this directory, with a
> host-verification harness `cal_cli_harness.cpp` that compiles the
> firmware's own `SelfCal.h` + verbatim `parseFloat` (30/30 checks).

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

## Re-dispatch re-verification (2026-09-12 evening) — verdict unchanged: NO-FIT

The fit task was re-dispatched after this report; every blocker was re-checked
with fresh tool evidence. Quantitative no-fit verdict (per the task FAILURE
PATH — the numbers that demonstrate it):

- Soak dwell points available for fitting: **0** of the ≥ 4 required
  (parent-task acceptance wanted ≥ 4 soaked setpoints spanning +25…−40 C).
  With n = 0 there is nothing to least-square: k, T0, residuals, and R² are
  all undefined. No fit was forced; nothing was fabricated.
- Filesystem re-scan (fresh, this session): whole-root `find` for
  `*.csv|*soak*|*freezer*` newer than 2026-09-10 (excluding /proc, /sys, R
  library test fixtures, and the unrelated balloon/e80 PER-RSSI benches) —
  **zero** thermal die-temp/ppm candidates. Repo-wide `*.csv` search inside
  meshcore: 0 files. Removable media: none mounted (root disk + /boot/efi
  only; the 0 B `sdb` card slot is empty).
- Fork ledger re-read at the live branch head (`git ls-remote` confirms
  feat/passive-mapper is still `d7ae93fa`): `RESULTS.md` still shows
  `_not yet measured_ … pending: needs the freezer/dry-ice sweep`.
- USB re-enumeration: unchanged since the 2026-09-11 guard trips — no
  SDR / counter / GPSDO / usbtmc / gpib device on the bus (only hubs,
  Bluetooth, RTL8152 Ethernet, audio/HID, microSD reader, 2× CH340 serial,
  Pi Debugprobe). The external-frequency-reference precondition is still
  unmet, so no new soak CSV can be produced on this host either.

Tool integrity re-proven this session (so the verdict is enforced by the
tool, not just prose):

- `--self-test`: 6/6 PASS, exit 0.
- Refusal path exercised through the real CLI on a synthetic 3-point CSV
  (`/tmp/atcut_refusal_demo_SYNTHETIC.csv` — labeled synthetic, not a
  measurement): gate `n_points >= 4` FAILed → "VERDICT: DO NOT ISSUE cal",
  exit 1, no command emitted.
- Header-only CSV (the literal zero-rows case): `CSV error: no usable soak
  rows found`, exit 1.

Unblock unchanged: a human bench session producing `soak.csv`
(`die_temp_c` + `offset_ppm` per soaked setpoint, module ID recorded) or an
operator-provisioned frequency reference. Then the deliverable is one
command away:

    python3 bench/atcut-fit/fit_atcut.py --csv soak.csv --module <id>

## Fourth dispatch re-verification (2026-09-14 ~04:00 UTC+2) — verdict unchanged: NO-FIT

Re-dispatched after the sibling thermal-lag / selfcal-ema-tau tasks' third
NO-DATA verdicts (committed same morning, `9b9fb897`). Every blocker was
re-checked with fresh tool evidence; nothing was assumed from prose.

**Why no soak points exist — the root cause is now recorded on the fleet
board itself.** The parent bench-cluster cards in
`~/.hermes/bot/fleet_queue_state.json` (read fresh this session, file mtime
2026-09-14 03:58) carry `decision: skip` / `decision_reason: no-headroom`:

| parent-cluster card (would have produced this task's input) | decision |
|---|---|
| t_ffc911f6 Physically locate thermal chamber | skip (light no-headroom) |
| t_b09424f1 Identify thermal chamber (range/accuracy/ramp) | assigned, no result |
| t_5f6eb893 Command and log 10-min holds +25/0/−20/−40 C | assigned, no result |
| t_db8ffdd6 Capture calshow die-temp soak evidence | assigned, no result |
| t_6a719e4f Identify external frequency reference | assigned, no result |
| t_0e98e408 Run chamber 10-min holds + capture logs | skip (medium no-headroom) |
| t_2eb80aef Inventory bench frequency-reference candidates | skip (medium no-headroom) |
| t_2f5adb53 Inventory RF connectors/adapters/feedthrough | skip (medium no-headroom) |
| t_48e048a1 Survey chamber feedthrough port + mechanical fit | skip |
| t_71af23c2 Audit calibration evidence for every bench instrument | skip |
| t_9d139605 Compile feedthrough+RF feasibility verdict | skip (heavy, waited 232 s) |
| t_de0a0fa5 Assess condensation/frost risk at −20/−40 C | skip |

The scheduler skipped the entire physical-bench prerequisite cluster for
capacity ("no-headroom"), and the cards that were assigned show no result
fields. No CSV was ever captured, on this host or on the fleet queue.

**Fresh evidence (every item re-verified this session, 2026-09-14):**

1. **Filesystem**: repo-wide `*.csv` search inside meshcore → 0 files
   (unchanged). Host-wide walk (whole root, minus /proc /sys /dev /run and
   system trees): **2,249 CSVs seen, 834 newer than 2026-09-12** — every
   thermal-shaped hit (headers `die_temp_c`/`offset_ppm`/`ppm_err`) is one
   of the 5 known SYNTHETIC self-test artifacts from these bench sessions
   (`/tmp/twin_ramp.csv`, `/tmp/zero_lag_ramp.csv`,
   `/tmp/hyst_refusal_demo_SYNTHETIC_dwell_only.csv`,
   `/tmp/atcut_refusal_demo_SYNTHETIC.csv`,
   `/tmp/atcut_empty_header_ONLY_demo.csv`). Everything else is FLRC
   PER/RSSI range-test logs, gerber pick-and-place files, and Go x/arch
   opcode tables. Zero real die-temp/ppm soak candidates, host-wide.
2. **USB bus** (this session): 2× CH340 serial + Pi Debugprobe + RTL8152
   Ethernet + microSD reader + hubs/BT/audio-HID — 0 instrument-class
   devices, no SDR/counter/GPSDO/signal-analyzer. The external
   frequency-reference precondition remains unmet, so the `offset_ppm`
   column is unproducible on this host; the on-chip FEI path is a verified
   dead end on LR2021.
3. **Firmware fork**: `git ls-remote` → feat/passive-mapper still `d7ae93fa`
   (unchanged); ledger `examples/passive_mapper/bench/RESULTS.md` still
   reads "_not yet measured_ — pending: needs the freezer/dry-ice sweep."
4. **Tool integrity**: `fit_atcut.py --self-test` → 6/6 PASS, exit 0.
   Refusal path re-exercised through the real CLI on all 5 synthetic
   thermal-shaped artifacts: every one refused with "VERDICT: DO NOT ISSUE
   cal", exit 1 — upward curvature (a=+0.0047619, k=−0.0047619), upward
   curvature (a=+0.034), T0=−102.5 C unbracketed, n=3, and header-only CSV.
   No command was emitted for any of them.
5. **Parser/domain proof re-run**: `verify_cal_domain.py` → PASS, 0 failures
   over the gate-legal (k, T0) domain; error budget unchanged (worst-case
   `%.6g`/`%.2f` round-trip cost < 0.1 ppm over |T−T0| ≤ 65 C).

**Quantitative NO-FIT (per METHOD step 2):** soak dwell points available:
**0** (need ≥ 4 spanning +25…−40 C). With n=0 there is nothing to
least-square: k, T0, residuals, and R² are undefined. No fit was forced;
no measurement was fabricated; the `cal <k> <T0>` slot stays unfilled.

**What remains ready (unchanged, re-verified this session):** the fitter,
the parser-verified `cal %.6g %.2f` emission contract, the domain-wide
parser proof, and the full argument spec in `CAL-CLI-SPEC.md` /
`CAL-COMMAND.md` — so the moment a real soak CSV lands, the fitted
command is one `fit_atcut.py --csv` invocation away and is
parser-legal by construction.

---

## Dispatch 5 — 2026-10-01 (fleet board `meshcore`, task t_3f930320, run 2)

NO-FIT verdict unchanged; the input CSV still does not exist. Fresh
verification, every item executed this session:

1. **Board state**: the bench-prep chain on the new fleet board is still
   dataless — t_03259d94 ("Run freezer dwell sweep…", the direct parent)
   archived with **0 runs**; t_e80e80cb / t_db8ffdd6 / t_a132b6cd (soak
   capture at +25/0/−20/−40 C) all `blocked` on `fleet-offload:dq05`;
   soak rollup t_6ece027b's ledger commit (c4be4400) states "all four
   UNVERIFIED (no calshow access + parent stability not PASS) — zero
   samples at every setpoint, nothing fabricated".
2. **Filesystem (2026-10-01)**: `find` over /home/c03rad0r/{worktrees,
   repos/meshcore, reports, scratch} (depth 4, .git pruned) for
   `*.csv|*soak*|*sweep*|*measured*|*dwell*|*freezer*` → only unrelated
   projects (hermes-bot sweep scripts, mining partitions, frame audits).
   Content grep for `offset_ppm|freq_err_ppm|drift_ppm` in data files →
   **0 hits**. Sibling thermal-hyst re-verification today (59982540)
   independently confirms ramp CSV absent since 09-14.
3. **Firmware fork**: `git ls-remote fork feat/passive-mapper` → still
   `d7ae93fa` (unchanged); its calibration ledger RESULTS.md still reads
   "_not yet measured_ — pending: needs the freezer/dry-ice sweep".
4. **Tool integrity re-run**: `fit_atcut.py --self-test` → **6/6 PASS**,
   exit 0 (bracketed-sweep recovery k_err 2e-5 ppm/C², T0_err 0.05 C;
   refusals on upward curvature / single-sided sweep / n=3 / parser
   quirks; pure-Python fallback == numpy to 1e-13).
   `verify_cal_domain.py` → **DOMAIN PROOF PASS** (worst-case
   %.6g/%.2f round-trip 2.1e-3 ppm; f32 ulp 1.6e-5 ppm).

**Quantitative NO-FIT (METHOD step 2):** soak dwell points available
**0** (need ≥ 4 spanning +25…−40 C, ≥ 20 C span, T0 bracketed). n = 0 ⇒
k, T0, residuals, R² all undefined; the (T, offset_ppm, residual) table
has zero rows. Root cause (unchanged since dispatch 1): no external
frequency reference on the host (0 instrument-class USB devices) and no
thermal chamber — the `offset_ppm` column is unproducible here. No fit
forced, nothing fabricated, `cal <k> <T0>` stays unfilled. The turnkey
path remains: real soak CSV → `python3 bench/atcut-fit/fit_atcut.py
--csv <file>` → parser-verified `cal %.6g %.2f` line.
