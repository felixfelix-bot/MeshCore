# SelfCal EMA time-constant (TEMP_TC_SECS) — synthesis recommendation

Fleet task: synthesize the two committed parent analyses —
`bench/thermal-lag` (per-ramp cross-correlation lag) and
`bench/thermal-hysteresis` (matched-level hysteresis) — into one
firmware-actionable keep-or-change recommendation for SelfCal's EMA time
constant, plus an honest statement of open-loop transient limits.

Date: 2026-09-12 (evening) · Repo: c03rad0r/MeshCore (main) ·
artifacts: `bench/selfcal-ema-tau/synthesize_tau.py` (this directory).
Body below is the VERBATIM stdout of:

    python3 bench/selfcal-ema-tau/synthesize_tau.py

Both parent deliverables carry committed NO-DATA verdicts (their ramp CSV
never existed; re-verified fresh this session: repo has 0 CSVs, 0 parent
JSON artifacts; /tmp holds only the parents' SYNTHETIC self-test leftovers
and unrelated FLRC PER benches). The synthesis therefore runs its NO-DATA
path: every field is either a concrete number (firmware constants, formula
rows — labeled NOT-measured where applicable) or a definitive
"NOT APPLICABLE because …". No number below is a hardware measurement.

Cross-check convention (documented in the tool): the hysteresis tool's
tau_hyst = dT/(r_warm+r_cool) recovers the SINGLE die→crystal lag (its own
self-test: planted 25 s → recovered 24.4 s); the "~2× the sibling's xcorr
lag" note in hysteresis_fit.py output is an erratum — the two methods are
compared 1:1. Derivation in the tool docstring.

----------------------------------------------------------------------------

SELFCAL EMA TIME-CONSTANT RECOMMENDATION - synthesis of thermal-lag + hysteresis parents
========================================================================================
VERDICT: NO-DATA   |   firmware constant: TEMP_TC_SECS = 10.0 s (now)
firmware: examples/passive_mapper/host/SelfCal.h:47 (felixfelix-bot/MeshCore feat/passive-mapper @ d7ae93fa, verified by fresh ls-remote+fetch this session)

INPUTS (parent deliverables)
  (a) per-ramp cross-correlation lag, seconds +/- uncertainty:
      NOT APPLICABLE because lag: file not found: /home/c03rad0r/repos/meshcore/bench/selfcal-ema-tau/../thermal-lag/lag.json - parent bench ramp CSV never existed (committed NO-DATA verdict)
  (b) hysteresis magnitude, C and equivalent seconds:
      NOT APPLICABLE because hyst: file not found: /home/c03rad0r/repos/meshcore/bench/selfcal-ema-tau/../thermal-hysteresis/hyst.json - parent bench ramp CSV never existed (committed NO-DATA verdict)

CROSS-METHOD CHECK (lag vs hysteresis-in-seconds)
  NOT APPLICABLE because at least one parent estimate is absent (no two numbers exist to compare)

RECOMMENDATION (directly translatable: SelfCal.h TEMP_TC_SECS)
  KEEP TEMP_TC_SECS = 10.0 s
  rule: no measured lag exists -> keep current constant; changing it on synthetic/self-test numbers would be fabrication
  rationale: the EMA tau should make the FILTERED die temperature track
  the crystal's effective temperature through transients, i.e. tau_ema ~
  measured die->crystal lag; compensation is computed from T_ema
  (SelfCal.h:133), so a mismatched tau biases every transient ppm directly.

LIMITATION NOTE (open-loop, unconditional)
  During fast temperature transients the open-loop compensation will lead or trail the crystal by the (un)matched portion of the die-vs-crystal lag: open-loop error ~ 2k|T-T0| * dT/dt * |lag - TEMP_TC_SECS|.
  The closed-loop CFO path cannot backstop this on LR2021 - the FEI residual path is inert there (verified dead end) - so the open-loop model's accuracy is transient-limited.
  With no measured lag, the current 10 s EMA's transient tracking error is UNQUANTIFIED; the illustrative rows bound the scale.
  update path: first-order EMA, alpha = 1 - exp(-dt/TEMP_TC_SECS) (SelfCal.h:118); compensation computed from the FILTERED temp: offset = +k*(T_ema - T0)^2 (SelfCal.h:133); output clamps: SLEW_PPM 25 / DEADBAND_PPM 1 / MAX_PPM 300 (SelfCal.h:48-50)
  closed loop: FEI residual path (SelfCal.feedMeasured) is inert on LR2021 (never called; on-chip frequency-error estimate is a verified dead end there) - open-loop has no backstop

ILLUSTRATIVE transient mis-compensation scale (formula rows from the
firmware's own sizing constants; k is UNMEASURED - atcut-fit NO-FIT;)
error_ppm = 2k|T-T0| * ramp_rate * mismatch_s:
  k (ppm/C^2)                                    ramp rate                              mismatch  -> ppm
  k=0.04 (fork sizing constant, NOT measured)    0.017 C/s = 1 C/min (bench-style ramp)     10s    0.53
  k=0.04 (fork sizing constant, NOT measured)    0.017 C/s = 1 C/min (bench-style ramp)     25s    1.34
  k=0.04 (fork sizing constant, NOT measured)    0.03 C/s ~ 1.8 C/min (ISA-ascent order)     10s    0.96
  k=0.04 (fork sizing constant, NOT measured)    0.03 C/s ~ 1.8 C/min (ISA-ascent order)     25s    2.40
  k=0.034 (AT-cut family default, NOT measured)  0.017 C/s = 1 C/min (bench-style ramp)     10s    0.45
  k=0.034 (AT-cut family default, NOT measured)  0.017 C/s = 1 C/min (bench-style ramp)     25s    1.14
  k=0.034 (AT-cut family default, NOT measured)  0.03 C/s ~ 1.8 C/min (ISA-ascent order)     10s    0.82
  k=0.034 (AT-cut family default, NOT measured)  0.03 C/s ~ 1.8 C/min (ISA-ascent order)     25s    2.04

RE-RUN WHEN PARENT CSV LANDS:
  python3 bench/thermal-lag/analyze_thermal_lag.py --csv <ramp.csv> --json bench/thermal-lag/lag.json && python3 bench/thermal-hysteresis/hysteresis_fit.py --csv <ramp.csv> --json bench/thermal-hysteresis/hyst.json && python3 bench/selfcal-ema-tau/synthesize_tau.py
