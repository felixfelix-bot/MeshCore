# `cal <k> <T0>` command assembly — verdict & evidence

Task: assemble the final, ready-to-issue `cal <k> <T0>` serial command from
(a) the parabola-fit child task's fitted (k, T0) and (b) the firmware CLI
argument spec; walk the parse path; deliver command + consistency argument +
caveats.

Date: 2026-09-12 · Repo: meshcore (this bench lineage: `bench/atcut-fit/`) ·
inputs: `REPORT.md` (fit task verdict) + `CAL-CLI-SPEC.md` (parser spec,
machine-verified @ felixfelix-bot/MeshCore feat/passive-mapper `3fdfbc8e`).

## VERDICT: NO `cal` COMMAND TO ISSUE — the fit child task returned NO-FIT

Per the task METHOD step 3, the fit task's verdict governs: it is BLOCKED /
NO-FIT (twice re-verified), so no command is fabricated. The command slot
stays unfilled:

    cal <k> <T0>\r        <- NOT FILLED. Do not issue a cal command yet.

### The failed-fit numbers (why no command exists)

| quantity | value | gate required |
|---|---|---|
| soak dwell points available | **0** | ≥ 4 (n_points gate) |
| T span covered | 0 C (no points) | ≥ 20 C |
| fitted k | **undefined** — nothing to least-square | 0.005–0.150 ppm/C², a<0 |
| fitted T0 | **undefined** | bracketed by sweep, ~room band |
| residuals / rms / R² | **undefined** | R² ≥ 0.95 |
| leave-one-out stability | undefined | k < 0.010, T0 < 5 C swings |

Root cause (unchanged since 2026-09-11): the parent bench task guard-tripped
twice — no external frequency reference on the USB bus (on-chip FEI is a
verified dead end on LR2021), no chamber control — so the soak CSV was never
produced. The fork's own ledger (`examples/passive_mapper/bench/RESULTS.md`)
still reads `_not yet measured_ … pending: needs the freezer/dry-ice sweep`.

### Independent re-verification performed THIS session (2026-09-12 ~19:2x UTC)

Every claim above re-checked with fresh tool output, not just report prose:

1. **Repo data scan**: zero `*.csv` anywhere in meshcore. The only CSVs on
   this host (`/tmp`) are labeled synthetic self-test artifacts of the
   sibling tasks; the fitter **refuses every one of them** (exit 1,
   "VERDICT: DO NOT ISSUE cal — No command emitted"):
   - `twin_ramp.csv` (thermal-lag self-test ramp): k = **−0.0047619**,
     T0 = −102.50 C → upward curvature, FAIL gates.
   - `zero_lag_ramp.csv`: k = **−0.034** → FAIL.
   - `atcut_empty_header_ONLY_demo.csv`: "no usable soak rows", exit 1.
   Even the only thermal-shaped files in existence cannot produce an
   issuable command — and being synthetic, must never be used as one.
2. **Fork head unchanged**: `git ls-remote` → feat/passive-mapper still
   `d7ae93fa` (spec pin `3fdfbc8e` + 3 known commits; ledger unchanged).
3. **Parser spec re-proven from source**: firmware clone at /tmp/mc-passive,
   `rev-parse HEAD` = `3fdfbc8e120e13d7543fe224c380e27533e720aa` (exact
   pin); `cal_cli_harness.cpp` rebuilt with g++ from it → all [OK] checks,
   exit 0 (happy path, grammar rejections, sign gate, separators, framing).
4. **Fitter tool integrity**: `fit_atcut.py --self-test` → 6/6 PASS, exit 0
   (recovery on synthetic bracketed sweep; refusals on upward curvature,
   single-sided sweep, n<4; parser grammar quirks; solver cross-check).
5. **NEW domain-wide parser proof** (`verify_cal_domain.py`, this commit):
   481,601 golden-ratio-jittered (k, T0) combinations over the entire
   gate-legal domain (k ∈ [0.005, 0.150] ppm/C², T0 ∈ [−40, +45] C) —
   every rendered `cal %.6g %.2f` line round-trips through the verbatim
   Python port of the firmware `parseFloat` + the k ≥ 0 CLI gate: **0
   failures**. Consequence: any future gate-passing fit emits a
   parser-legal command *by construction*; the only remaining step when
   data arrives is running the fitter.

## What a filled command WILL look like (format contract, parser-walked)

The fitter's emission format is `cal %.6g %.2f` + CR. Walked manually through
the parser path (MyMesh.cpp @ 3fdfbc8e; every step harness-verified), using
the SELF-TEST's synthetic SYNTH-1 values as stand-in — **these are synthetic
and must never be issued to real hardware**:

    cal 0.0340211 24.95\r

| step | chars | parser behavior (citation) |
|---|---|---|
| dispatch | `cal ` | `strncmp(cmd, "cal ", 4) == 0` (MyMesh.cpp:166); byte 4 must be 0x20 — a tab is NOT the cal command |
| k token | `0.0340211` | parseFloat (MyMesh.cpp:128-143): leading digit present → integer `0`, then `.` + fraction `0340211` accumulates `v += d*scale; scale *= 0.1f` in f32 → 0x3D0B59B6; parse stops at the space, `endp` chains to T0 (:168-169) |
| separator | ` ` | one space; second parseFloat skips its own leading ws (MyMesh.cpp:129); comma would FAIL |
| T0 token | `24.95` | integer `24` + fraction `95` → 0x41C79999; parse ends at end-of-string, tail empty (`endp = nullptr`, trailing garbage would be *ignored*, :170) |
| semantic gate | — | `k >= 0.0f` (MyMesh.cpp:170) — 0.0340211 ≥ 0 ✓ |
| terminator | `\r` | completion on `\r` (main.cpp:83), then stripped (:85); LF-only NEVER executes (main.cpp:72-76) |
| effect | — | `writeCalBlob` → `setCalibration` (RAM-first) → 15-byte `/selfcal.dat`; reply `cal k=0.0340211 T0=24.95C -> persisted (valid=yes)` |

Consistency argument (one paragraph): the two arguments are parsed by the
firmware's custom `parseFloat`, whose entire grammar is
`ws* sign? digit+ [ '.' digit* ]` with no exponent and a mandatory leading
digit (MyMesh.cpp:129-139); the fitter's `%.6g` for the gated k band always
renders `0.dddddd` (values 0.005–0.150 never round to an integer, never need
an exponent, always carry the leading `0`), and `%.2f` for any plausible T0
renders `-?dd.dd`, so both tokens are inside the grammar by construction —
verified not just for one example but for 481,601 jittered (k, T0) pairs
across the whole legal domain (0 parser failures), and the round-trip lands
within a half-ULP of the rendered decimals (`verify_command`, fit_atcut.py).
The k ≥ 0 semantic gate is satisfied because the fitter refuses any fit with
k ≤ 0 (a<0 gate) before emitting; the separator is a single space; the line
is ≤ 159 bytes; and the CR terminator matches the serial reader's completion
check. The firmware stores the parsed f32 bit patterns verbatim with no
further scaling (MyMesh.cpp:171 → SelfCal.h:65-73), so what is typed is
exactly what the model and `/selfcal.dat` get.

## Caveats for the moment a REAL fit exists

- **Rounding/quantization budget** (machine-computed, `verify_cal_domain.py`,
  worst case over the sweep |T−T0| ≤ 65 C, i.e. +25…−40 C around a ~25 C T0):
  - `%.6g` k rounding: ≤ **2.11e-3 ppm** worst case (k≈0.1499999);
    ≤ 2.1e-4 ppm for k < 0.1 — negligible vs a typical fit rms ~0.06 ppm.
  - `%.2f` T0 rounding: ≤ **0.096 ppm** at the gate-band edge k=0.15;
    **0.022 ppm** at LR2021-typical k=0.034 — well under the ±300 ppm model
    clamp and typical fit residuals.
  - f32 storage: ~1.6e-5 ppm (k) / 8.4e-6 ppm (T0) — irrelevant.
  Net: the 6-significant-digit / 2-decimal format costs < 0.1 ppm of
  compensation accuracy over the swept range; more digits are accepted by
  the parser but cannot be stored in the f32 blob anyway.
- **Validity band**: firmware applies the cal only for |T_die − T0| ≤ 60 C
  (CAL_RANGE_C, SelfCal.h:36; widened to 90 C in post-pin commit `d83b3660`
  — check the deployed firmware's pin). Outside it: BW125 fallback, last
  offset held. T0 must therefore be the fitted vertex, not a midpoint.
- **Per-module**: k/T0 are per-crystal. Never copy between boards; record
  the module ID when the sweep is finally run (`--module`).
- **Static bias is not correctable**: the c − (−k·T0²) delta (reference /
  initial crystal tolerance) passes through the cal untouched; if > ~10 ppm,
  record it and consider cap trim.
- **Wire details**: terminator CR (LF optional after it; LF-only hangs);
  leading digit before any `.` (`0.034`, never `.034`); no exponent; a lost
  space before a negative T0 silently flips its sign (`0.04-25` → T0=−25);
  a failed FS write still leaves the new cal active in RAM ("RAM only, file
  write failed").
- **Blob rebuild note**: `pack_blob` now defaults `version=0`, matching the
  firmware byte-for-byte (`_ver` starts 0 and `setVersion` is never called
  @ 3fdfbc8e; harness-verified firmware blobs end `43 53 00`). A previous
  default of 1 produced blobs that still loaded (length+magic check only)
  but did not match what the firmware itself writes.

## Unblock (unchanged)

A human bench session with an external frequency reference and a
freezer/chamber producing `soak.csv` (`die_temp_c`, `offset_ppm` per soaked
setpoint, +25 → −40 C, module ID recorded). Then the entire deliverable is
one command:

    python3 bench/atcut-fit/fit_atcut.py --csv soak.csv --module <board-id>

which prints the verbatim, parser-verified `cal %.6g %.2f` line, the
expected firmware reply, and the 15-byte blob hex. Confirm on-target with
`calshow\r` → `cal valid=yes k=... T0=...C ...`.
