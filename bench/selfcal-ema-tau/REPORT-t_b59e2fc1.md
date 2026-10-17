# SelfCal EMA time constant vs measured thermal lag — evaluation and recommendation

Fleet card: `meshcore:t_b59e2fc1` — "Evaluate SelfCal EMA time constant against measured lag".
Date: 2026-10-17 · Host: c03rad0r-DQ05proplus · Workspace: `/home/c03rad0r/worktrees/t_e1408991`
Parents: none. Children: `t_307caabf` (root), `t_3420c50a` (final writeup).

---

## ANSWER FIRST

**Recommendation: KEEP `TEMP_TC_SECS = 10.0 s` — do not change the firmware constant.**

Two independent reasons, either of which is sufficient:

1. **The measured lag does not exist.** This card's INPUT is "measured lag (s) with
   uncertainty". No die-temp / ppm ramp time series has ever been recorded on this
   fleet. Both sibling analyses carry committed NO-DATA verdicts and k/T0 is NO-FIT
   (re-verified fresh this session — §5). Changing a firmware constant on synthetic
   self-test numbers would be fabrication.
2. **Even taking the synthetic number at face value, the firmware's own committed
   change rule does not fire.** The value 24.3 s is 5.7 s *below* the in-tree
   threshold of 30 s, and is still below it at +3σ (27.3 s).

**Open-loop limitation: YES, unconditional and unbacked.** The compensation leads or
trails the crystal by the unmatched portion of the lag during any temperature
transient, and there is no closed-loop path to correct it on LR2021 (§4).

**Quantified conditional for the moment a measurement lands:** if a real ramp CSV
yields τ_die→crystal > 30 s, set `TEMP_TC_SECS = round(τ/5)·5 s` (a 24.3 s result → 25 s).

**But the limitation is bounded, not link-breaking:** the worst-case transient
mis-compensation at the ISA floor is **3.03 ppm** against a **72 ppm** BW125 capture
window — a **95.8 % margin**. The mismatch is real; it is not what will lose packets.

---

## 1. STEP 1 — the comparison the card asks for

| quantity | value | source |
|---|---|---|
| lag, die→crystal | **24.3 ± 1.0 s** — SYNTHETIC, not a measurement | reconciled estimator value, `t_c895d107` |
| current EMA constant | **10.0 s** | `SelfCal.h:47` (`TEMP_TC_SECS`), pinned `d7ae93fa` |
| **ratio lag/EMA** | **2.43×** (2.33× … 2.53× at ±1σ) | 24.3 / 10.0 |
| Δ(lag − EMA) | 14.3 s = 14.3σ | |
| hysteresis family alone | 24.4 ± 1.15 s (τ_hyst) | `hysteresis_fit.py --self-test`, re-run |
| loop-area delay fit alone | 24.2 ± 1.0 s | `analyze_thermal_lag.py --self-test`, re-run |

So the lag is **2.43× the EMA constant** — the EMA is *faster* than the crystal, not
slower. On a transient the filtered die temperature moves ahead of the crystal, and
since the compensation is computed from the filtered temperature
(`offset = +k·(T_ema − T0)²`, `SelfCal.h:133`), the applied offset is **ahead of the
truth**. That is the lead/trail direction this card asks about — see §4, where it is
derived and verified rather than assumed.

**Provenance caveat, stated plainly.** 24.3 s is not a measurement. It is the
sibling tools' own synthetic pipeline-validation output: three ramps built on a
**planted first-order lag of 25.0 s**, recovered as 24.3 ± 1.0 s (recovery error
0.71 s = 0.71σ). It is the *only* number that exists in this lineage, and it is
labelled as synthetic everywhere it appears in the deliverable tool.

---

## 2. STEP 2 — the firmware tree's own two decision rules, applied

Rather than invent a threshold, the evaluation applies the two rules that **already
exist in the pinned tree**. They disagree, and that disagreement is the substantive
finding of this card.

| | rule A — thermal-lag tool | rule B — bench kit |
|---|---|---|
| source | `bench/thermal-lag/analyze_thermal_lag.py:495,500` | `thermal_bench.py:538-541` + `bench/README.md:146` (both in `examples/passive_mapper`, `d7ae93fa`) |
| condition | `transient_limited` iff `ci_lo > 2.0 × TEMP_TC_SECS` | raise `TEMP_TC_SECS` iff measured τ **> 30 s** |
| threshold | 20 s | 30 s |
| fires on 24.3 s? | **YES** (ci_lo 23.3 s > 20 s) | **NO** (margin 5.7 s; still no at +3σ = 27.3 s) |
| implied value | 25 s (rounded up to a 5 s grid) | keep 10 s |

> **The two committed rules disagree on this value.** The thermal-lag tool fires
> above ~20 s and would set 25 s; the bench kit fires above 30 s and would keep
> 10 s. The synthetic estimate sits in the gap. This card is what exposes that the
> fleet has two different change thresholds and has never reconciled them.

Both rules are faithfully reported rather than silently picking a winner. The
recommendation (§6) resolves the conflict by taking the **more conservative** rule,
because the number it is being applied to is synthetic — a defensive choice that is
correct under the actual data status regardless of which rule is better.

---

## 3. STEP 3 — how big is the mismatch, physically

Quasi-steady open-loop mis-compensation on a constant-rate ramp:

```
err_ppm ≈ d(offset)/dT · (T_ema − T_x)
        = 2k|T − T0| · ramp_rate · |tau_ema − tau_lag|
```

Zero exactly when the EMA constant equals the lag — which is the entire design
intent of `TEMP_TC_SECS`.

| mission-profile point | 2k\|T−T0\| (ppm/K) | err @ keep 10 s (ppm) | err @ move 25 s (ppm) | err @ 10 s, ISA ascent (ppm) |
|---|---|---|---|---|
| near turnover (±15 C) | 1.20 | 0.70 | 0.03 | 0.56 |
| bench mid-ramp (−20 C) | 3.60 | 2.11 | 0.10 | 1.67 |
| **ISA floor (−56.5 C)** | **6.52** | **3.82** | 0.19 | **3.03** |

Rates: bench ramp 0.041 C/s (worst in the synthetic ramps); ISA ascent 0.0325 C/s
(5 m/s × 6.5 K/km lapse — a planning estimate, labelled). `k = 0.04 ppm/K²` is the
fork sizing constant and is **NOT measured** (t_3f930320 NO-FIT, n = 0 dwell points).

**Worst case 3.03 ppm against the 72 ppm BW125 capture window = 4.2 % occupancy,
95.8 % margin.** The ISA floor is inside the firmware's own validity band
(|−56.5 − 25| = 81.5 C ≤ `CAL_RANGE_C` = 90 C, `SelfCal.h:72`), so this is a point
the model actually operates at, not an extrapolation.

### 3b. Robustness — what if the true lag is nothing like 24.3 s?

Because the lag is unmeasured, the move 10 s → 25 s is a bet on a number. This table
is the bet's payoff at the ISA floor:

| true τ (s) | err @ keep 10 s | err @ move 25 s | move better? | both < 72 ppm? |
|---|---|---|---|---|
| 5 | 1.06 | 4.24 | **NO** | yes |
| 10 | 0.00 | 3.18 | **NO** | yes |
| 15 | 1.06 | 2.12 | **NO** | yes |
| 24.3 | 3.03 | 0.15 | yes | yes |
| 30 | 4.24 | 1.06 | yes | yes |
| 40 | 6.36 | 3.18 | yes | yes |
| 60 | 10.60 | 7.42 | yes | yes |

Two things follow. First, **the move is not a pure win** — if the true lag is ≤ ~17 s
the change makes things worse, and the lag is unmeasured, so that branch is live.
Second, **every branch, both choices, stays inside the 72 ppm capture window** by a
wide margin (worst cell 10.6 ppm = 15 % of window). The constant is therefore not a
link-critical parameter at these ramp rates; it is a second-order accuracy knob. That
is the strongest argument for KEEP: the downside of not tuning is small and bounded,
while the downside of tuning on a synthetic number is an unverifiable firmware change.

---

## 4. STEP 4 — the open-loop limitation, stated explicitly

The card asks for an explicit statement, so here it is, with the sign **derived and
verified** rather than asserted.

**The compensation will lead or trail the crystal — the direction flips with ramp
direction.** With u = T − T0, r = dT/dt, a = −τ_ema·r, b = −τ_lag·r:

```
err = k[(u+a)² − (u+b)²] = k·(a−b)·(a+b+2u)
⇒  err ≈ +2k·(τ_lag − τ_ema)·r·(T − T0)
⇒  sign(err) = sign(τ_lag − τ_ema) · sign(r) · sign(T − T0)
```

So with τ_ema < τ_lag (our case):

- **ramp moving AWAY from turnover → OVER-compensation** (applied magnitude too large)
- **ramp moving TOWARD turnover → UNDER-compensation** (applied magnitude too small)

Verified against the numerical simulation of the firmware's own filter
(`alpha = 1 − exp(−dt/τ)`, `SelfCal.h:118`) on four ramp cases — sign law matches
simulation in all four:

| case | max \|err\| (ppm) | signed (ppm) | sign law | T at max |
|---|---|---|---|---|---|
| cooling +25 → −20 (away from T0) | 2.08 | **+2.08** | ✓ | −20.0 C |
| warming −20 → +25 (toward T0) | 1.90 | **−1.90** | ✓ | −15.7 C |
| cooling −20 → −40 (away from T0) | 3.02 | **+3.02** | ✓ | −40.0 C |
| warming −40 → −20 (toward T0) | 2.82 | **−2.82** | ✓ | −35.4 C |

The alternating sign matters operationally: the same physical mismatch produces a
compensation that is **ahead of the crystal on one leg of a descent and behind it on
the other**, so a symmetric two-direction ramp sweep is required to see it at all.
A one-direction sweep would show a bias and hide half the mechanism.

**There is no closed-loop backstop on LR2021 — verified dead end, not repeated from
memory.** Two independent checks this session:

1. `SelfCal.feedMeasured()` — the only entry point to the closed-loop residual path —
   has **zero call sites** in the production tree at `d7ae93fa`. `git grep
   feedMeasured d7ae93fa` returns only the definition (`SelfCal.h:158`) and two
   invocations inside the host test suite (`host/tests/test_self_cal.cpp:148,153`).
   Nothing in `MyMesh.cpp` or the radio wrapper ever calls it. The residual path is
   inert exactly as `SelfCal.h:28` claims ("INERT on LR2021/LR11x0 (no FEI field)").
2. The LR2021/LR2022/LR2012 datasheet (Rev 2.1, Semtech, 243 pages, full text
   extracted and searched) defines **no host-readable frequency-error measurement**
   — no "frequency error indicator", no `FreqErrInd`, no FEI read command. Every
   occurrence of "frequency error" in the document is one of exactly two things,
   and neither is a readout:
   - **tolerance specifications** — how much transmitter/receiver frequency offset
     the demodulator survives: `LORA_FERR_L1` ±25 %BW (`Table 3-17` sheet 4),
     `LORA_FERR_L2` ±33 %BW, `LORA_FERR_L4` ±100 ppm, `LORA_FERR_L5` ±200 ppm
     (SF12/SF11), plus the WM-Bus `WM_*_FREQERR` and Z-Wave `ZW_R*_FREQERR`
     "Max frequency error tolerated" tables;
   - **one configuration register**, `0xF30A2C` bits [17:16] — "LoRa extended
     frequency error control" (§9.7, *Extended LoRa Rx Bandwidth*), which selects
     the demodulator's offset-*tracking* mode (`0` legacy / `1` extended) to widen
     that tolerance to ±41.25 kHz at BW125. It is a mode switch, not a measurement.

   The datasheet also documents the reason the closed loop is structurally
   unnecessary-but-unavailable here: the on-chip XTAL compensation is a *sensor +
   analog trim* path ("compensates, to some extent, the frequency shift due to XTAL
   heating", §1.9.2, requiring an external NTC on the VTCXO pin), not a digital
   error estimate the firmware can read back and servo on.

Therefore the open-loop model's accuracy is **transient-limited with no recovery
path**. This is a limitation of the architecture, not of the constant's value: it
stands whether `TEMP_TC_SECS` is 10 s, 25 s, or perfectly matched, because the crystal
lag is never zero and any transient excites the mismatch.

**How limiting, quantitatively.** Burning the *entire* 72 ppm capture window with the
current 14.3 s mismatch would require **0.77 C/s ≈ 46 C/min** at the ISA floor
(d(offset)/dT = 6.52 ppm/K there), or **2.53 C/s ≈ 152 C/min** at the much milder
sensitivity of the synthetic worst-ramp window (1.99 ppm/K). ISA ascent is
~0.0325 C/s — **24× (ISA-floor basis) to 78× (mild-window basis) slower**. Either way
the transient limitation is real, is unbacked, and is **not the binding constraint on
this link** at any credible ramp rate.

### 4b. One firmware side effect the card does not ask about but the owner needs

`SelfCal.h:100` seeds `_temp_ema = T0` at calibration load ("assume ambient ~ T0
until first real reading"), so at boot the model reports offset 0 while the required
offset is `k·(T_boot − T0)²`. That error decays with the EMA constant, so **lengthening
`TEMP_TC_SECS` directly lengthens cold-boot recovery**:

| boot ambient | initial error | settle to 1 ppm @ τ=10 s | @ τ=25 s |
|---|---|---|---|
| −40 C | **169.0 ppm** | 51 s | 128 s |
| −20 C | **81.0 ppm** | 44 s | 110 s |
| 0 C | 25.0 ppm | 32 s | 80 s |
| +20 C | 1.0 ppm | 0 s | 0 s |

A −40 C or −20 C cold boot is **already outside the 72 ppm capture window** (169 ppm
and 81 ppm) before the EMA has done anything — and a 25 s constant takes **2.5× longer**
to walk it back in. This is an argument *against* lengthening the constant that does
not appear in either sibling card, and it is why the conditional recommendation (§6)
carries the "> 30 s" gate rather than acting on 24.3 s.

---

## 5. Fresh evidence collected this session (nothing carried from memory)

1. **Data status re-verified, not assumed.**
   - `bench/thermal-lag/lag.json` and `bench/thermal-hysteresis/hyst.json` do not
     exist — the parents' ramp CSV never landed.
   - `find ~ /tmp /mnt /media /run/user -name '*.csv' -newermt 2026-10-16` → **no
     results**. The meshcore repo contains 4 CSVs, none of them a ramp series.
   - `synthesize_tau.py` re-run → exit 0, `VERDICT: NO-DATA`, `KEEP TEMP_TC_SECS =
     10.0 s`, both parent inputs reported "NOT APPLICABLE because … file not found".
2. **All three committed sibling analyzers re-run this session, all exit 0:**
   - `analyze_thermal_lag.py --self-test` → `SELF-TEST PASS` (loop-area +24.2 ± 1.0 s,
     residual 0.098 ppm; hysteresis +1.20 C; open-loop bound 1.96 ppm; EMA
     recommendation line prints 25.0 s and the "transient limit / FEI dead end" note).
   - `hysteresis_fit.py --self-test` → `SELF-TEST PASS` (τ_hyst +24.4 s vs planted
     25.0 s; ΔT +1.34 C; bootstrap CI [+23.6, +25.9] s).
   - `synthesize_tau.py` → NO-DATA, KEEP 10 s (above).
3. **Firmware pinned and line-verified.** `examples/passive_mapper/host/SelfCal.h` at
   `felixfelix-bot/MeshCore @ d7ae93fa` (re-confirmed via `git ls-remote fork`:
   `refs/heads/feat/passive-mapper = d7ae93fa1d0f71fa704d59c801351c28c3d9020a`).
   `TEMP_TC_SECS = 10.0f` at **:47**; `SLEW_PPM` :48; `DEADBAND_PPM` :49; `MAX_PPM`
   :50; `SNR_GATE_DB` :53; `CAL_RANGE_C = 90.0f` :72; EMA alpha :118; `_temp_ema = T0`
   seed :100; `offset = k(T−T0)²` :133; `feedMeasured` definition :158.
   The worktree copy in `$HERMES_KANBAN_WORKSPACE/fw_3fdfbc8e` is an **older** revision
   (`3fdfbc8e`, `SelfCal.h:27`, `CAL_RANGE_C = 60.0f`, `-k` sign convention) — all
   citations in this report use the current `d7ae93fa` tree.
4. **Closed-loop dead end verified two ways** — zero `feedMeasured` call sites in the
   production tree; and the LR2021 datasheet Rev 2.1 (243 pages, `pdftotext`
   full-text searched) defines no host-readable frequency-error measurement — its 39
   "frequency error" hits resolve to demodulator *tolerance* specs (`LORA_FERR_L1/2/4/5`,
   `WM_*_FREQERR`, `ZW_R*_FREQERR`) plus one *mode-switch* register (`0xF30A2C`
   bits [17:16], §9.7). See §4.
5. **Deliverable tool self-tested:** `ema_tau_eval_t_b59e2fc1.py --self-test` →
   **24/24 PASS**, including the sign law against simulation, the exact algebraic
   identity `err = k(a−b)(a+b+2u)` (worst relative deviation 8.8e−15), the settled
   closed form with the discrete effective lag `L = dt(1−α)/α` (worst 1.4e−13),
   reproduction of the sibling tool's own 1.96 ppm bound, and the rule thresholds.

---

## 6. The recommendation, as firmware instructions

```
TEMP_TC_SECS = 10.0f     // NO CHANGE  (examples/passive_mapper/host/SelfCal.h:47)
```

**Rationale (apply as-is, no re-derivation needed):**

1. The die→crystal lag is **unmeasured** on this fleet. Both sibling cards carry
   committed NO-DATA verdicts; k/T0 is NO-FIT with n = 0 dwell points. No ramp time
   series exists. There is nothing to tune against.
2. The only lag number in the lineage is **24.3 ± 1.0 s, synthetic** (planted truth
   25.0 s). It is 2.43× the current constant, but it is **5.7 s below the firmware
   tree's own committed change threshold of 30 s** (`thermal_bench.py:538-541`,
   `bench/README.md:146`) and remains below it at +3σ (27.3 s).
3. The mismatch is **bounded and not link-critical**: worst case 3.03 ppm against a
   72 ppm capture window (95.8 % margin). Every robustness branch — both constant
   choices, true lag 5 s to 60 s — stays inside the window.
4. Lengthening the constant **slows cold-boot recovery** 2.5×, and a −20 C boot
   already starts 81 ppm outside the capture window. Changing it is not free.

**Conditional instruction — act on this the moment a real ramp CSV exists:**

```
if (measured tau_die_to_crystal > 30.0 s)      # thermal_bench.py hyst output
    TEMP_TC_SECS = round(tau / 5) * 5          # 5 s grid, per analyze_thermal_lag.py:489
                                               # e.g. tau = 24.3 s -> 25.0 s
```

**Re-run sequence when the parent CSV lands:**

```bash
python3 bench/thermal-lag/analyze_thermal_lag.py --csv <ramp.csv> --json bench/thermal-lag/lag.json
python3 bench/thermal-hysteresis/hysteresis_fit.py --csv <ramp.csv> --json bench/thermal-hysteresis/hyst.json
python3 bench/selfcal-ema-tau/synthesize_tau.py
python3 ema_tau_eval_t_b59e2fc1.py            # this card's tool: replaces the 24.3 s input
```

**Open-loop limitation note (carry into the firmware writeup verbatim):**

> During fast temperature transients the open-loop compensation leads or trails the
> crystal by the unmatched portion of the die-vs-crystal lag, and the direction
> **flips with ramp direction** — it over-shoots while the temperature moves away
> from turnover and under-shoots while it moves toward it. The closed-loop CFO path
> **cannot backstop this on LR2021**: `SelfCal.feedMeasured()` has zero call sites in
> the tree and the LR2021 datasheet defines no FEI register — the FEI path is a
> verified dead end. The open-loop model's accuracy is therefore transient-limited
> unconditionally, independent of the value of `TEMP_TC_SECS`. At the ISA floor the
> resulting worst-case error is 3.03 ppm against a 72 ppm capture window, so the
> limitation is real but is not the binding constraint on the link at any credible
> ramp rate.

---

## 7. Deliverables

| file | what |
|---|---|
| `ema_tau_eval_t_b59e2fc1.py` | the evaluation tool (stdlib, deterministic, `--self-test` 24/24 PASS, `--json`) |
| `ema_tau_eval_out_t_b59e2fc1.txt` | verbatim stdout of the tool |
| `REPORT-t_b59e2fc1.md` | this report |
| `PROGRESS-t_b59e2fc1.md` | crash-recovery map |

## 8. Declared gaps (not filled, not guessed)

1. **No hardware lag measurement exists.** This is the card's stated INPUT and it is
   absent. Everything quantitative here is either a firmware constant, an in-tree
   rule threshold, or a synthetic estimator-validation value.
2. **k is not measured.** 0.04 ppm/K² (fork sizing) and 0.034 ppm/K² (AT-cut family
   default) are labelled constants. Every ppm figure scales linearly with k.
3. **ISA ascent rate is a planning estimate.** 5 m/s is assumed; 3 m/s would scale
   the ISA errors by 0.6 (worst case 1.82 ppm).
4. **The 30 s threshold has no stated derivation** in the tree — `README.md:146`
   asserts it without justification. It is applied here as the *committed* rule, not
   as a validated one. If the fleet reconciles rules A and B, this recommendation
   should be revisited.
5. **Bench-kit `fit_lag` disagrees with the sibling tools on the estimator.** The
   firmware's own `calib.fit_lag` uses a residual fit on a simulated one-pole and
   explicitly *rejects* the derivative cross-correlation approach as unidentifiable
   (`calib.py:320-328`). This supports the sibling tools' trust decision (loop-area +
   hysteresis over raw xcorr) but is a third opinion that has never been reconciled
   against them on real data.
