# SelfCal EMA time constant — FINAL firmware recommendation

**Card:** `meshcore:t_3420c50a` — "Write final firmware recommendation for SelfCal EMA and open-loop limit"
**Audience:** firmware owner of `examples/passive_mapper` (MeshCore)
**Firmware pin:** `felixfelix-bot/MeshCore` @ **`d7ae93fa`** (`refs/heads/feat/passive-mapper`), verified `ls-remote` this session. All `file:line` citations below are against that commit.
**Written:** 2026-10-17 · merge of `t_c895d107` (lag reconciliation) + `t_b59e2fc1` (EMA evaluation). Self-contained: everything the owner needs is in this document; no parent report has to be read.

---

## 0. The instruction (copy-paste, no derivation required)

```c
// examples/passive_mapper/host/SelfCal.h:47   -- NO CHANGE
static constexpr float TEMP_TC_SECS = 10.0f;     // keep 10.0 s
```

There is **no patch to apply today**. One conditional instruction, to be applied only when a real ramp log exists:

```c
// Only if bench/thermal-hysteresis/hyst.json reports tau > 30.0 s:
static constexpr float TEMP_TC_SECS = <round(tau_s / 5) * 5>f;   // 5 s grid
// e.g. tau = 32 s -> 30.0f ;  tau = 34 s -> 35.0f ;  tau = 47 s -> 45.0f ;  tau = 24.3 s -> 25.0f
```

Two housekeeping actions for the owner, both independent of any measurement (see §4 and §6):

1. **Make the 30 s threshold canonical and derive it** — the tree currently contains two mutually inconsistent change rules (20 s and 30 s); §4 gives the derivation for 30 s.
2. **Consider fixing the cold-boot seed** (`SelfCal.h:100`), which is a *larger* error source than the time constant itself — §6. This one is actionable now, without any new bench data.

---

## 1. Bottom line in one table

| item | value | unit | status |
|---|---|---|---|
| die→crystal thermal lag, **real hardware** | **UNDEFINED** | s | **no measurement exists** — see §2 |
| die→crystal thermal lag, reconciled estimator value | **24.3 ± 1.0** | s | **SYNTHETIC** (planted truth 25.0 s) — do not treat as measured |
| hysteresis magnitude (matched-level ΔT) | **+1.34** (IQR 0.14) | °C | **SYNTHETIC** (same validation run) |
| current `TEMP_TC_SECS` | **10.0** | s | `SelfCal.h:47` |
| ratio lag / EMA | **2.43×** (2.33–2.53× at ±1σ) | — | on the synthetic value only |
| Δ(lag − EMA) | **14.3** = 14.3σ | s | on the synthetic value only |
| **EMA recommendation** | **KEEP 10.0** | s | verdict of this document |
| worst-case open-loop transient error, keep 10 s | **3.03** | ppm | ISA floor, §5 |
| LoRa capture window (BW125) | **72** | ppm | ±36 ppm, SX12xx-class figure |
| window occupancy / margin | **4.2 % / 95.8 %** | — | transient limit is **not** link-binding |
| cold-boot initial error at −20 °C / −40 °C | **81 / 169** | ppm | **outside** the window, `SelfCal.h:100` — see §6 |
| closed-loop backstop | **none** | — | `feedMeasured()` has **0** production call sites; LR2021 has no FEI register |

---

## 2. Provenance: the "measured lag" does not exist (read before quoting any number)

This is stated first because every quantitative claim downstream inherits it.

- No die-temperature / frequency-error ramp time series exists anywhere on this fleet. `bench/thermal-lag/lag.json` and `bench/thermal-hysteresis/hyst.json` **do not exist** — the parent bench session never produced the CSV they require.
- Both sibling analyses carry committed, repeatedly re-verified **NO-DATA** verdicts (`t_f6f826be`, `t_474e6323`); the k/T0 fit is **NO-FIT with n = 0 dwell points** (`t_3f930320`). Re-verified fresh for this card: all three committed analyzers re-run, exit 0, unchanged (§9).
- The **only** lag number in the lineage is **24.3 ± 1.0 s**, and it comes from those tools' own *synthetic pipeline validation*: three ramps built on a **planted first-order lag of 25.0 s**, recovered as 24.3 ± 1.0 s (recovery error 0.71 s = 0.71σ). It is labelled SYNTHETIC everywhere it appears.

Consequence, and the reason for the KEEP: **tuning a firmware constant to a synthetic self-test number would be fabrication.** The synthetic value is used below only to state how large the mismatch *would be*, and to bound the decision, never as a basis for a code change.

### 2.1 Which estimator the 24.3 s comes from, and which one to ignore

| method | value (s) | uncertainty | verdict |
|---|---|---|---|
| loop-area delay fit | +24.2 | ± 1.0 | **trusted** — physical model, 0.098 ppm residual |
| hysteresis → time equivalent (τ = ΔT/(r_warm+r_cool)) | +24.4 | ± 1.15 (bootstrap CI +23.6…+25.9) | **trusted** — independent conditioning |
| inverse-variance weighted mean of the two | 24.29 | ± 0.75 | reported as **24.3 ± 1.0** (conservative σ: shared ramp/conventions make the errors correlated) |
| detrended cross-correlation (per-ramp combined) | +15.30 | **± 203.30** | **DO NOT QUOTE as a lag.** σ spans [-391, +422] s (95 % interval): the 95 % interval covers zero *and* the entire physically plausible range, so its "agreement" with the hysteresis estimate (0.045σ) is vacuous. Per-ramp estimates on one planted truth span −110 s to +82 s. The tool author demonstrated the failure mode independently on a noiseless zero-lag ramp (+188 s / −82 s from xcorr vs −0.0 s from loop-area). |

The two estimators that *are* trusted agree to 0.20 s against ±1.52 s combined (0.13σ). That agreement is real; the cross-correlation number is not evidence either way.

---

## 3. Why KEEP 10 s — two independent reasons, either sufficient

**R1 — there is nothing to tune against.** The measured lag is undefined (§2). Both parents are committed NO-DATA; k/T0 is NO-FIT with n = 0. A firmware change on this evidence base is unjustifiable regardless of what the constant would ideally be.

**R2 — even taking the synthetic number at face value, the firmware's own committed rule does not fire.** 24.3 s is **5.7 s below** the in-tree change threshold of 30 s, and remains below it at +3σ (27.3 s). The change would also be *conditionally harmful*: if the true lag is ≤ ~17 s, moving to 25 s makes the error **worse** (see the robustness table in §5.3). Since the lag is unmeasured, that branch is live.

Supporting quantitative context, from §5: the mismatch is bounded at **3.03 ppm against a 72 ppm window** (95.8 % margin), and *every* combination of constant choice (10 s or 25 s) with true lag 5–60 s stays inside the window. `TEMP_TC_SECS` is therefore a second-order accuracy knob on this link, not a link-critical parameter. The cost of not tuning is small and bounded; the cost of tuning on synthetic data is an unverifiable firmware change.

---

## 4. The tree contains two inconsistent change rules — resolve this

This is the substantive finding of the analysis chain and it needs an owner decision.

| | **Rule A** | **Rule B** |
|---|---|---|
| location | `bench/thermal-lag/analyze_thermal_lag.py:495,500` | `examples/passive_mapper/bench/thermal_bench.py:538-541` + `examples/passive_mapper/bench/README.md:146` (both `d7ae93fa`) |
| condition | `transient_limited` iff `ci_lo > 2.0 × TEMP_TC_SECS`; recommended τ = 5 s-grid round of `max(lag, ci_lo)` | raise `TEMP_TC_SECS` iff measured τ **> 30 s** |
| effective threshold | **20 s** | **30 s** |
| fires on 24.3 s? | **YES** → would set 25 s | **NO** → keep 10 s |
| derivation in tree | "2×" multiplier, none stated | none stated — `README.md:146` asserts 30 s |

**How this document resolves it:** by applying the more conservative rule (the one that changes nothing), which is correct under the actual data status independently of which rule is better. **The two rules must still be reconciled**, because the next operator reading `analyze_thermal_lag.py` will set 25 s while the next operator reading `bench/README.md` will keep 10 s, on the same CSV.

**Recommended reconciliation — adopt 30 s as canonical, with this derivation** (closes the "30 s has no derivation" gap using only constants already in the tree, no new measurement):

```
err_ppm(tau) = 2k·|T−T0|·r·(tau − TEMP_TC_SECS)          [§5.1]
mission-profile floor: 2k|T−T0| = 6.52 ppm/K  (−56.5 °C, k=0.04)
ISA ascent:            r       = 0.0325 C/s
                        ⇒ 0.2119 ppm per second of constant/lag mismatch
5 % of the 72 ppm window  = 3.6 ppm  ⇒  mismatch 17.0 s  ⇒  tau > 27.0 s
10 % of the window        = 7.2 ppm  ⇒  mismatch 34.0 s  ⇒  tau > 44.0 s
the committed 30 s        ⇒ 4.24 ppm = 5.9 % of window   ← sits between the two
```

So the committed 30 s is defensible as a "~5 % of capture window at the mission-profile floor" rule, and 20 s is not (it corresponds to 2.1 ppm / 2.9 %, i.e. below the modelled accuracy of the whole compensation). If the owner prefers a hard derivation, write **`tau > 27 s` (5 % criterion)** into `bench/README.md:146` and make `analyze_thermal_lag.py:495` use the same 5 %-of-window criterion instead of the arbitrary `2.0 ×` multiplier. This is a documentation/consistency change only — it does **not** change the shipped constant today (the lag is still unmeasured).

---

## 5. Open-loop limitation note (carry into the firmware writeup verbatim)

> **Open-loop transient limit.** During fast temperature transients the open-loop compensation leads or trails the crystal by the unmatched portion of the die-vs-crystal lag, and the direction **flips with ramp direction**: it over-shoots while the temperature moves *away* from turnover and under-shoots while it moves *toward* it. The closed-loop CFO path **cannot backstop this on LR2021** — `SelfCal.feedMeasured()` has zero call sites in the production tree, and the LR2021 datasheet (Rev 2.1) defines no host-readable frequency-error measurement, so the FEI residual path is a verified dead end. The open-loop model's accuracy is therefore **transient-limited unconditionally, independent of the value of `TEMP_TC_SECS`** — the crystal lag is never zero, so any transient excites the mismatch. At the ISA floor the resulting worst-case error is **3.03 ppm against a 72 ppm capture window (95.8 % margin)**, so the limitation is real but is not the binding constraint on the link at any credible ramp rate.

### 5.1 The formula, and the sign derived rather than assumed

With `u = T − T0`, ramp rate `r = dT/dt`, `a = −τ_ema·r`, `b = −τ_lag·r`:

```
err = k[(u+a)² − (u+b)²] = k(a−b)(a+b+2u)
 ⇒ err ≈ +2k·(τ_lag − τ_ema)·r·(T − T0)
 ⇒ sign(err) = sign(τ_lag − τ_ema) · sign(r) · sign(T − T0)
```

With `τ_ema = 10 s < τ_lag` (our case): **ramp away from turnover → over-compensation** (applied magnitude too large); **ramp toward turnover → under-compensation** (too small). Verified against a numerical simulation of the firmware's own filter (`alpha = 1 − exp(−dt/τ)`, `SelfCal.h:118`) on four ramp cases — sign law matched in all four:

| case | max \|err\| (ppm) | signed (ppm) | sign law | T at max |
|---|---|---|---|---|
| cooling +25 → −20 (away from T0) | 2.08 | **+2.08** | ✓ | −20.0 °C |
| warming −20 → +25 (toward T0) | 1.90 | **−1.90** | ✓ | −15.7 °C |
| cooling −20 → −40 (away from T0) | 3.02 | **+3.02** | ✓ | −40.0 °C |
| warming −40 → −20 (toward T0) | 2.82 | **−2.82** | ✓ | −35.4 °C |

**Operational consequence for the bench:** the sign alternates between the two legs of a descent-and-return cycle. A **one-direction ramp sweep will show a bias and hide half the mechanism** — a two-direction sweep is required to measure the lag at all.

### 5.2 Magnitude against the mission profile

`err = 2k|T−T0| · ramp_rate · |τ_ema − τ_lag|`, zero exactly when the constant equals the lag (which is the whole design intent of `TEMP_TC_SECS`).

| mission-profile point | 2k\|T−T0\| (ppm/K) | err @ 10 s (ppm) | err @ 25 s (ppm) | err @ 10 s, ISA ascent (ppm) |
|---|---|---|---|---|
| near turnover (±15 °C) | 1.20 | 0.70 | 0.03 | 0.56 |
| bench mid-ramp (−20 °C) | 3.60 | 2.11 | 0.10 | 1.67 |
| **ISA floor (−56.5 °C)** | **6.52** | **3.82** | 0.19 | **3.03** |

Rates: bench ramp 0.041 °C/s (worst in the synthetic ramps); ISA ascent 0.0325 °C/s (5 m/s × 6.5 K/km — a **planning estimate**, labelled). `k = 0.04 ppm/K²` is the fork sizing constant and is **NOT measured**. The ISA floor is inside the model's validity band: `|−56.5 − 25| = 81.5 °C ≤ CAL_RANGE_C = 90 °C` (`SelfCal.h:72`), so this is an operating point, not an extrapolation.

**How fast would a ramp have to be to consume the whole 72 ppm window?** 0.77 °C/s ≈ 46 °C/min at the ISA-floor sensitivity (6.52 ppm/K), or 2.53 °C/s ≈ 152 °C/min at the milder 1.99 ppm/K of the synthetic worst ramp. ISA ascent is 24× to 78× slower. Not binding.

### 5.3 Robustness: what if the true lag is nothing like 24.3 s?

Because the lag is unmeasured, any move to 25 s is a bet. Payoff at the ISA floor:

| true τ (s) | err @ 10 s (ppm) | err @ 25 s (ppm) | move better? | both < 72 ppm? |
|---|---|---|---|---|
| 5 | 1.06 | 4.24 | **NO** | yes |
| 10 | 0.00 | 3.18 | **NO** | yes |
| 15 | 1.06 | 2.12 | **NO** | yes |
| 17 | 1.48 | 1.70 | ~tie (crossover) | yes |
| 24.3 | 3.03 | 0.15 | yes | yes |
| 30 | 4.24 | 1.06 | yes | yes |
| 40 | 6.36 | 3.18 | yes | yes |
| 60 | 10.60 | 7.42 | yes | yes |

The move is **not** a pure win below ~17 s, and every branch of both choices stays inside the window (worst cell 10.6 ppm = 15 % of window). That is the strongest argument for KEEP.

### 5.4 Why "no closed-loop backstop" is a verified fact, not a memory

1. **Zero production call sites.** `git grep feedMeasured d7ae93fa` returns only the definition (`SelfCal.h:158`) and two host-test invocations (`host/tests/test_self_cal.cpp:148,153`). Nothing in `MyMesh.cpp` or the radio wrapper calls it — the residual path is inert exactly as `SelfCal.h:29` states.
2. **No register to read.** The LR2021/LR2022/LR2012 datasheet (Rev 2.1, 243 pages, full text searched) defines no host-readable frequency-error measurement. All 39 occurrences of "frequency error" resolve to (a) demodulator *tolerance* specs — `LORA_FERR_L1/L2/L4/L5`, `WM_*_FREQERR`, `ZW_R*_FREQERR` — or (b) one *mode-switch* register `0xF30A2C` bits [17:16] ("LoRa extended frequency error control", §9.7). The on-chip XTAL compensation is a sensor + analog-trim path requiring an external NTC on VTCXO, not a digital error estimate the firmware can servo on.

---

## 6. A side effect the owner needs: the cold-boot seed (actionable now)

`SelfCal.h:100` seeds `_temp_ema = T0` at calibration load ("assume ambient ~ T0 until first real reading"). At boot the model therefore reports offset **0** while the required offset is `k·(T_boot − T0)²`. The error decays with the EMA constant, so **lengthening `TEMP_TC_SECS` directly lengthens cold-boot recovery**:

| boot ambient | initial error (ppm) | settle to 1 ppm @ τ = 10 s | @ τ = 25 s |
|---|---|---|---|
| −40 °C | **169.0** | 51 s | 128 s |
| −20 °C | **81.0** | 44 s | 110 s |
| 0 °C | 25.0 | 32 s | 80 s |
| +20 °C | 1.0 | 0 s | 0 s |

A −20 °C or −40 °C cold boot is **already outside the 72 ppm capture window before the EMA has done anything**. This is a *larger* error source than the transient mismatch (3.03 ppm) and it points the opposite way: it is an argument **against** lengthening the constant.

**Recommended fix (independent of any bench data, do it whenever convenient):** seed the EMA from the first real reading instead of from `T0` — the guarded branch already exists in `setTemperatureC()` (`SelfCal.h:117`: `if (!_temp_init) { _temp_ema = t; _temp_init = true; return; }`), so the fix is to **not** set `_temp_ema = T0` in `loadCalibration`, leaving `_temp_init` false. Then the first `setTemperatureC()` call adopts ambient exactly and the 81/169 ppm boot excursion disappears. (Alternative, if a cold-boot excursion to zero offset is deliberate: keep the seed but clamp the *initial* output to the model value at first reading.) This recommendation is not part of the EMA-constant decision and does not conflict with it.

---

## 7. Re-run sequence when a real ramp CSV finally lands

```bash
# 1. per-ramp cross-correlation + loop-area delay + open-loop bound
python3 bench/thermal-lag/analyze_thermal_lag.py --csv <ramp.csv> --json bench/thermal-lag/lag.json

# 2. hysteresis -> tau_hyst (this is the tau the 30 s rule reads)
python3 bench/thermal-hysteresis/hysteresis_fit.py --csv <ramp.csv> --json bench/thermal-hysteresis/hyst.json

# 3. synthesis (prints VERDICT: KEEP/CHANGE + the exact constant)
python3 bench/selfcal-ema-tau/synthesize_tau.py

# 4. apply THIS document's decision rule to the measured lag and print the
#    exact constant to set (also prints the before/after ISA-floor error)
python3 verify_final_recommendation_t_3420c50a.py --lag <tau_s> --sigma <sigma_s>
#    e.g. --lag 24.3 --sigma 1.0  ->  "KEEP 10.0 s, NO CODE CHANGE"
#         --lag 34.0 --sigma 2.0  ->  "set 35.0f"
```

**Decision rule to apply to the output, no re-derivation needed:**

```
if tau_measured > 30.0:            TEMP_TC_SECS = round(tau_measured / 5) * 5
elif tau_measured is None:         KEEP 10.0            # current state
else:                              KEEP 10.0            # within the committed threshold
```

**The bench recipe that produces the missing CSV** (this is the only real blocker for the entire question): LR2021 passive_mapper on a serial port + an external frequency reference (counter / SDR / GPSDO — none present on this host's USB bus) + freezer/chamber ramps **in both directions** with dwell soaks, logging `timestamp_s, phase, die_temp_c, ppm_err` with ≥1 cooling and ≥1 warming ramp at a comparable span. Both directions are mandatory (§5.1: the error sign flips with ramp direction).

---

## 8. Parameter sheet (units, ranges, rationale — the "apply without deriving" summary)

| symbol | file:line | current | recommended | unit | valid range / notes | rationale |
|---|---|---|---|---|---|---|
| `TEMP_TC_SECS` | `SelfCal.h:47` | 10.0f | **10.0f (unchanged)** | s | > 0; effective discrete lag `L = dt(1−α)/α`; 5 s grid when changed | lag unmeasured; synthetic 24.3 s is below the 30 s rule; mismatch bounded at 3.03/72 ppm |
| `SLEW_PPM` | `SelfCal.h:48` | 25.0f | unchanged | ppm/update | — | not implicated by this analysis |
| `DEADBAND_PPM` | `SelfCal.h:49` | 1.0f | unchanged | ppm | — | not implicated |
| `MAX_PPM` | `SelfCal.h:50` | 300.0f | unchanged | ppm | must cover 266 ppm profile floor | not implicated |
| `CAL_RANGE_C` | `SelfCal.h:72` | 90.0f | unchanged | °C | ISA floor needs 81.5 °C | not implicated; ISA floor verified inside |
| EMA seed | `SelfCal.h:100` | `_temp_ema = T0` | **adopt first real reading** | °C | — | 81 ppm (−20 °C) / 169 ppm (−40 °C) boot excursion outside capture window; see §6 |

---

## 9. Verification ledger (what was actually run for this card)

- `bench/thermal-lag/analyze_thermal_lag.py --self-test` → **SELF-TEST PASS**, exit 0 (loop-area +24.2 ± 1.0 s, residual 0.098 ppm, hysteresis ΔT +1.20 °C on the 9-level run, open-loop bound 1.96 ppm, EMA line 25.0 s).
- `bench/thermal-hysteresis/hysteresis_fit.py --self-test` → **SELF-TEST PASS** (τ 24.4 s vs planted 25.0 s, bootstrap CI [+23.6, +25.9]).
- `bench/selfcal-ema-tau/synthesize_tau.py` → exit 0, **VERDICT: NO-DATA**, `KEEP TEMP_TC_SECS = 10.0 s`, both parent inputs "NOT APPLICABLE … file not found".
- `bench/selfcal-ema-tau/ema_tau_eval_t_b59e2fc1.py --self-test` → **24/24 PASS** (sign law vs simulation, exact algebraic identity to 8.8e−15, discrete-lag closed form to 1.4e−13, rule thresholds).
- `verify_final_recommendation_t_3420c50a.py --self-test` → **18/18 PASS**; full run → **121/121 checks PASS**, exit 0 (output: `verify_final_out_t_3420c50a.txt`). It re-derives every figure in §1, §4, §5 and §6 from the firmware constants and re-simulates the four ramp cases against the firmware's own filter — reproducing the magnitude table to <0.01 ppm and the sign law in all four cases.
- Firmware constants re-read from `git show d7ae93fa:examples/passive_mapper/host/SelfCal.h` for **this** document: `TEMP_TC_SECS` :47, `CAL_RANGE_C` :72, `_temp_ema = T0` :100, `alpha` :118, `offset = k(T−T0)²` :133, `feedMeasured` :158 — all match.
- Rules re-read from `d7ae93fa`: `analyze_thermal_lag.py:495,500` (`transient_limited` iff `ci_lo > 2.0*tau_now`, 5 s grid round) and `thermal_bench.py:538-541` / `bench/README.md:146` (`tau > 30 s`), both confirmed verbatim.
- Every number in this document is re-derived and machine-checked by `verify_final_recommendation_t_3420c50a.py` (see its output `verify_final_out_t_3420c50a.txt`), which recomputes the arithmetic from the constants and asserts each figure appears in this file.

## 10. Declared gaps (not filled, not guessed)

1. **No hardware lag measurement exists.** The single bench session that would produce it has not happened; this is the only real blocker for the whole question.
2. **`k` is not measured** (0.04 ppm/K² fork sizing, 0.034 ppm/K² AT-cut family default). Every ppm figure scales linearly with `k`; if `k` is off by 2×, 3.03 ppm becomes 6.06 ppm — still inside the window.
3. **The ISA ascent rate is a planning estimate** (5 m/s). At 3 m/s, halve the ISA-basis errors (worst 1.82 ppm).
4. **The 30 s threshold has no in-tree derivation.** §4 supplies one from labelled constants; it is a derivation of the *threshold*, not a measurement.
5. **The bench kit's `calib.fit_lag` is a third estimator opinion** (residual fit on a simulated one-pole; it explicitly rejects derivative cross-correlation as unidentifiable, `calib.py:320-328`) that has never been reconciled against the loop-area/hysteresis family on real data.
6. **`SelfCal.h:100` cold-boot seeding was not exercised on hardware**; the 81/169 ppm figures are arithmetic from the model, not measurements.
