#!/usr/bin/env python3
"""
ema_tau_eval_t_b59e2fc1.py
==========================
Kanban meshcore:t_b59e2fc1 -- "Evaluate SelfCal EMA time constant against
measured lag".

DECISION THIS TOOL PRODUCES
---------------------------
Whether SelfCal's thermal-lag EMA constant (TEMP_TC_SECS = 10.0 s) should be
kept or changed, and how bad the open-loop transient limitation actually is.

HONESTY CONTRACT (read before quoting any number)
-------------------------------------------------
This card's INPUT is "measured lag (s) with uncertainty".  THAT INPUT DOES NOT
EXIST.  No die-temp / ppm ramp time series has ever been recorded on this fleet:
both sibling analyses carry committed NO-DATA verdicts and k/T0 is NO-FIT
(re-verified fresh in this session -- see REPORT).  Every lag number in this
lineage is a SYNTHETIC estimator-validation value produced by the sibling tools'
own self-tests against a PLANTED 25.0 s lag.

So the tool keeps three things strictly separate and never blurs them:

  A. DATA STATUS  -- the lag is UNDEFINED.  Nothing here is a measurement.
  B. FIRMWARE ACTION (what to change today) -- driven by (A) plus the firmware's
     OWN committed decision rules, not by the synthetic number.
  C. NUMERIC CONDITIONAL (what to do the moment a measurement lands) -- driven
     by the synthetic estimator value 24.3 s +/- 1.0 s and by the same in-tree
     rules, so the firmware owner can act without re-deriving anything.

PROVENANCE OF EVERY CONSTANT
----------------------------
Firmware constants are read from the pinned tree
felixfelix-bot/MeshCore @ d7ae93fa:examples/passive_mapper/host/SelfCal.h and
:examples/passive_mapper/MyMesh.cpp (fetched, and line-verified, in this
session).  Lag numbers come from the committed sibling tools re-run in this
session.  Decision thresholds come from the firmware's own bench kit.  k/T0 is
NOT measured (t_3f930320 NO-FIT, n=0 dwell points) and is labelled as such
wherever it is used.

Stdlib only.  Deterministic.  `--self-test` verifies the analytic formulas
against the numerical simulation and against the sibling tools' own printed
numbers.

Usage:
    python3 ema_tau_eval_t_b59e2fc1.py
    python3 ema_tau_eval_t_b59e2fc1.py --json
    python3 ema_tau_eval_t_b59e2fc1.py --self-test
"""

import json
import math
import sys

# ------------------------------------------------------------------ inputs
# --- firmware constants: SelfCal.h @ d7ae93fa (line numbers as fetched) -----
TAU_FW = 10.0          # s    TEMP_TC_SECS, SelfCal.h:47
SLEW_PPM = 25.0        # ppm  SLEW_PPM,     SelfCal.h:48
DEADBAND_PPM = 1.0     # ppm  DEADBAND_PPM, SelfCal.h:49
MAX_PPM = 300.0        # ppm  MAX_PPM,      SelfCal.h:50
SNR_GATE_DB = -10.0    # dB   SNR_GATE_DB,  SelfCal.h:53
CAL_RANGE_C = 90.0     # C    CAL_RANGE_C,  SelfCal.h:72
# --- capture window: MyMesh.cpp @ d7ae93fa:23 ("BW125, a +/-72 ppm capture") --
CAPTURE_PPM = 72.0

# --- decision rules that already live IN THE FIRMWARE TREE -------------------
# bench/thermal-lag/analyze_thermal_lag.py:495,500 -- transient_limited iff
# ci_lo > 2.0 * tau_now; recommendation rounded up to a 5 s grid (:489).
RULE_LAG_FACTOR = 2.0
RULE_LAG_ROUND_S = 5.0
# examples/passive_mapper/bench/thermal_bench.py:538-541 and
# examples/passive_mapper/bench/README.md:146 -- "If tau > 30 s, raise
# TEMP_TC_SECS to the measured value".
RULE_BENCH_THRESHOLD_S = 30.0

# --- crystal model constants: NOT MEASURED (t_3f930320 NO-FIT, n=0) ---------
K_FORK = 0.04          # ppm/K^2  fork sizing constant (bench/selfcal-ema-tau)
K_FAMILY = 0.034       # ppm/K^2  AT-cut family default used by sibling self-tests
T0_DEFAULT = 25.0      # C        family default turnover

# --- lag inputs: SYNTHETIC pipeline validation ONLY (planted truth 25.0 s) --
TAU_SYNTH = 24.3       # s   reconciled synthetic estimator value (t_c895d107)
TAU_SYNTH_SIGMA = 1.0  # s   conservative sigma (correlated shared-ramp errors)
TAU_SYNTH_LO = 23.3    # s   = TAU_SYNTH - 1 sigma (the CI low the rule tests)
TAU_PLANTED = 25.0     # s   the truth the synthetic ramps were built on
TAU_SYNTH_HYST = 24.4  # s   hysteresis family alone (tau_hyst, bootstrap CI)
TAU_SYNTH_HYST_SIGMA = 1.15
TAU_SYNTH_LOOPAREA = 24.2   # s  loop-area delay fit alone
TAU_SYNTH_LOOPAREA_SIGMA = 1.0

# --- worst-ramp numbers printed by analyze_thermal_lag.py --self-test -------
RATE_WORST = 0.041     # C/s    worst ramp rate in the synthetic ramps
SENS_WORST = 1.99      # ppm/K  d(offset)/dT in the tool's own worst 30 s window

# --- mission profile: ISA lapse x plausible ascent rate (planning estimate) --
ISA_LAPSE_K_PER_M = 0.0065
ASCENT_RATE_M_PER_S = 5.0
RATE_ISA_C_PER_S = ISA_LAPSE_K_PER_M * ASCENT_RATE_M_PER_S   # 0.0325 C/s cooling
ISA_FLOOR_C = -56.5    # held 11-20 km (bench/README.md, CAL_RANGE_C sizing note)


# --------------------------------------------------------------- physics
def sens_ppm_per_k(temp_c, k=K_FORK, t0=T0_DEFAULT):
    """d(offset)/dT for the AT-cut parabola offset = k*(T-T0)^2 (SelfCal.h:133)."""
    return 2.0 * k * abs(temp_c - t0)


def transient_error_ppm(tau_lag_s, tau_ema_s, sens, rate_c_per_s):
    """Open-loop mis-compensation on a constant-rate ramp, quasi-steady limit:

        err ~= d(offset)/dT * (T_ema - T_x) = sens * r * (tau_ema - tau_lag)

    Zero exactly when the EMA constant matches the die->crystal lag -- which is
    the entire design intent of TEMP_TC_SECS.  Returned as a magnitude in ppm.
    """
    return abs(sens * rate_c_per_s * (tau_ema_s - tau_lag_s))


def sign_law(tau_lag_s, tau_ema_s, rate_c_per_s, temp_c, t0=T0_DEFAULT):
    """Sign of the transient error, derived (not assumed).

    Exact identity when both filters have settled: with u = T-T0, r = dT/dt,
    a = tau_ema*r, b = tau_lag*r,

        err = k[(u-a)^2 - (u-b)^2] = k*(a-b)*(a+b-2u)

    and a-b = -r*(tau_lag-tau_ema).  For |r| small the -2u term dominates, so

        err ~= +2*k*(tau_lag - tau_ema) * r * u

        sign(err) = sign(tau_lag - tau_ema) * sign(r) * sign(T - T0)

    i.e. the compensation OVER-shoots (positive = applied magnitude too large)
    when the ramp drives the temperature AWAY from turnover, and UNDER-shoots
    when it drives the temperature TOWARD turnover.  The lead/trail direction
    therefore flips with ramp direction -- it is not one-signed.
    """
    d = tau_lag_s - tau_ema_s
    s = 1 if d > 0 else (-1 if d < 0 else 0)
    s *= 1 if rate_c_per_s > 0 else (-1 if rate_c_per_s < 0 else 0)
    s *= 1 if (temp_c - t0) > 0 else (-1 if (temp_c - t0) < 0 else 0)
    return s


def offset_ppm(temp_c, k=K_FORK, t0=T0_DEFAULT):
    """Applied compensation, SelfCal.h:133 (k a MAGNITUDE; positive = LO up)."""
    return k * (temp_c - t0) ** 2


def one_pole(series, dt, tau):
    """First-order lag with the exponential-alpha form of SelfCal.h:118."""
    if tau <= 0 or len(series) < 2:
        return list(series)
    alpha = 1.0 - math.exp(-dt / tau)
    out = [series[0]]
    for v in series[1:]:
        out.append(out[-1] + (v - out[-1]) * alpha)
    return out


def _eff_lag(tau, dt):
    """Effective steady-state lag of a DISCRETE one-pole tracking a linear ramp.

    y[i] - x[i] -> -r*L with L = dt*(1-alpha)/alpha, alpha = 1-exp(-dt/tau).
    L -> tau as dt -> 0, with the first-order correction L = tau - dt/2.
    """
    alpha = 1.0 - math.exp(-dt / tau)
    return dt * (1.0 - alpha) / alpha


def ramp_case(k, t0, tau_lag, tau_ema, rate, t_start, t_end, dt=1.0):
    """Simulate a constant-rate slope through a lagging crystal and a lagging
    EMA; return (max|err|, signed err at max, tail-window mean err, tail temps).

    Both filters are seeded at t_start, mirroring a soak-then-ramp bench run.
    """
    span = abs((t_end - t_start) / rate)
    n = max(2, int(round(span / dt)))
    die = [t_start + rate * i * dt for i in range(n + 1)]
    xtal = one_pole(die, dt, tau_lag)
    ema = one_pole(die, dt, tau_ema)
    errs = [offset_ppm(e, k, t0) - offset_ppm(x, k, t0) for e, x in zip(ema, xtal)]
    imax = max(range(len(errs)), key=lambda i: abs(errs[i]))
    tail = slice(2 * len(errs) // 3, len(errs))
    mean_tail = sum(errs[tail]) / len(errs[tail])
    return (abs(errs[imax]), errs[imax], mean_tail,
            die, xtal, ema, errs)


def cold_start_settle_s(tau, seed_temp, actual_temp, k, target_ppm=1.0):
    """Seconds for a boot-time EMA seeded at `seed_temp` (SelfCal.h:100 sets
    _temp_ema = T0) to converge on `actual_temp` to within `target_ppm`."""
    e0 = abs(offset_ppm(seed_temp, k) - offset_ppm(actual_temp, k))
    if e0 <= target_ppm:
        return 0.0
    return tau * math.log(e0 / target_ppm)


# ----------------------------------------------------------------- report
def build():
    r = {}

    # ---- 0. data status ------------------------------------------------
    r["data_status"] = {
        "hardware_lag": "UNDEFINED -- no die-temp/ppm ramp time series exists",
        "lag_value_used": TAU_SYNTH,
        "lag_provenance": ("SYNTHETIC estimator validation from the sibling tools' "
                           "own --self-test runs (planted truth %.1f s); NOT a "
                           "measurement" % TAU_PLANTED),
        "k_t0_status": "NO-FIT (n=0 dwell points, t_3f930320) -- k is a labelled "
                       "sizing constant, not a measurement",
    }

    # ---- 1. the comparison the card asks for ---------------------------
    r["comparison"] = {
        "lag_s": TAU_SYNTH,
        "lag_sigma_s": TAU_SYNTH_SIGMA,
        "ema_s": TAU_FW,
        "ratio": TAU_SYNTH / TAU_FW,
        "ratio_lo": (TAU_SYNTH - TAU_SYNTH_SIGMA) / TAU_FW,
        "ratio_hi": (TAU_SYNTH + TAU_SYNTH_SIGMA) / TAU_FW,
        "delta_s": abs(TAU_SYNTH - TAU_FW),
        "delta_sigma": abs(TAU_SYNTH - TAU_FW) / TAU_SYNTH_SIGMA,
        "families": {
            "hysteresis_tau_hyst_s": TAU_SYNTH_HYST,
            "hysteresis_sigma_s": TAU_SYNTH_HYST_SIGMA,
            "loop_area_s": TAU_SYNTH_LOOPAREA,
            "loop_area_sigma_s": TAU_SYNTH_LOOPAREA_SIGMA,
        },
    }

    # ---- 2. the two committed in-tree decision rules, applied ----------
    ci_lo = TAU_SYNTH_LO
    lag_rule_fires = ci_lo > RULE_LAG_FACTOR * TAU_FW
    bench_rule_fires = TAU_SYNTH > RULE_BENCH_THRESHOLD_S
    bench_rule_fires_3sig = (TAU_SYNTH + 3 * TAU_SYNTH_SIGMA) > RULE_BENCH_THRESHOLD_S
    rec_round = RULE_LAG_ROUND_S * round(max(TAU_SYNTH, ci_lo) / RULE_LAG_ROUND_S)
    r["rules"] = {
        "rule_lag": {
            "source": "bench/thermal-lag/analyze_thermal_lag.py:495,500",
            "condition": "transient_limited iff ci_lo > %.1f * TEMP_TC_SECS" % RULE_LAG_FACTOR,
            "ci_lo_s": ci_lo,
            "threshold_s": RULE_LAG_FACTOR * TAU_FW,
            "fires": lag_rule_fires,
            "implied_value_s": rec_round,
        },
        "rule_bench": {
            "source": ("bench/thermal_bench.py:538-541 + bench/README.md:146 "
                       "(examples/passive_mapper, d7ae93fa)"),
            "condition": "raise TEMP_TC_SECS iff measured tau > %.0f s" % RULE_BENCH_THRESHOLD_S,
            "value_s": TAU_SYNTH,
            "threshold_s": RULE_BENCH_THRESHOLD_S,
            "margin_s": RULE_BENCH_THRESHOLD_S - TAU_SYNTH,
            "fires": bench_rule_fires,
            "fires_at_plus_3_sigma": bench_rule_fires_3sig,
        },
        "agree": lag_rule_fires == bench_rule_fires,
        "note": ("the two committed rules DISAGREE on this value: the thermal-lag "
                 "tool fires above ~%.0f s and would set 25 s; the bench kit fires "
                 "above %.0f s and would keep 10 s.  The synthetic estimate sits in "
                 "the gap."
                 % (RULE_LAG_FACTOR * TAU_FW, RULE_BENCH_THRESHOLD_S)),
    }

    # ---- 3. transient error at mission-profile temperature extremes ----
    prof = []
    for label, temp_c in (("at turnover+/-15 C", 40.0),
                          ("bench mid-ramp (-20 C)", -20.0),
                          ("ISA floor (-56.5 C)", ISA_FLOOR_C)):
        s = sens_ppm_per_k(temp_c)
        e10 = transient_error_ppm(TAU_SYNTH, TAU_FW, s, RATE_WORST)
        e25 = transient_error_ppm(TAU_SYNTH, 25.0, s, RATE_WORST)
        e10_isa = transient_error_ppm(TAU_SYNTH, TAU_FW, s, RATE_ISA_C_PER_S)
        prof.append({
            "label": label,
            "temp_c": temp_c,
            "sens_ppm_per_k": s,
            "err_tau10_bench_ppm": e10,
            "err_tau25_bench_ppm": e25,
            "err_tau10_isa_ppm": e10_isa,
            "pct_capture_tau10_bench": 100.0 * e10 / CAPTURE_PPM,
            "pct_capture_tau10_isa": 100.0 * e10_isa / CAPTURE_PPM,
            "in_cal_range": abs(temp_c - T0_DEFAULT) <= CAL_RANGE_C,
        })
    r["profile_errors"] = prof

    # ---- 3b. capture-window crossover, at two sensitivities ------------
    mismatch_now = abs(TAU_SYNTH - TAU_FW)
    sens_isa = sens_ppm_per_k(ISA_FLOOR_C)
    r["crossover"] = {
        "mismatch_s": mismatch_now,
        "sens_worst_ppm_per_k": SENS_WORST,
        "sens_isa_floor_ppm_per_k": sens_isa,
        "rate_worst_basis_C_per_s": CAPTURE_PPM / (SENS_WORST * mismatch_now),
        "rate_isa_basis_C_per_s": CAPTURE_PPM / (sens_isa * mismatch_now),
        "rate_isa_basis_C_per_min": 60.0 * CAPTURE_PPM / (sens_isa * mismatch_now),
        "isa_ascent_C_per_s": RATE_ISA_C_PER_S,
        "isa_headroom_isa_basis": (CAPTURE_PPM / (sens_isa * mismatch_now))
                                  / RATE_ISA_C_PER_S,
        "isa_headroom_worst_basis": (CAPTURE_PPM / (SENS_WORST * mismatch_now))
                                    / RATE_ISA_C_PER_S,
    }

    # ---- 4. sign law, verified against simulation ----------------------
    sign_rows = []
    for label, (t0c, t1c, rate) in {
        "cooling +25 -> -20 (away from T0)": (25.0, -20.0, -RATE_WORST),
        "warming -20 -> +25 (toward T0)": (-20.0, 25.0, +RATE_WORST),
        "cooling -20 -> -40 (away from T0)": (-20.0, -40.0, -RATE_WORST),
        "warming -40 -> -20 (toward T0)": (-40.0, -20.0, +RATE_WORST),
    }.items():
        mx, signed, mean_tail, die, xtal, ema, errs = ramp_case(
            K_FORK, T0_DEFAULT, TAU_SYNTH, TAU_FW, rate, t0c, t1c)
        t_at_max = die[errs.index(max(errs, key=abs))]
        predicted = sign_law(TAU_SYNTH, TAU_FW, rate, t_at_max)
        sign_rows.append({
            "case": label,
            "max_abs_ppm": mx,
            "signed_ppm_at_max": signed,
            "temp_at_max_c": t_at_max,
            "predicted_sign": predicted,
            "sign_matches": (predicted > 0) == (signed > 0),
            "mean_tail_ppm": mean_tail,
        })
    r["sign_law"] = sign_rows

    # ---- 5. robustness of a move if the true lag is unknown ------------
    robust = []
    for tau_true in (5.0, 10.0, 15.0, 24.3, 30.0, 40.0, 60.0):
        e_keep = transient_error_ppm(tau_true, TAU_FW, sens_ppm_per_k(ISA_FLOOR_C),
                                     RATE_ISA_C_PER_S)
        e_move = transient_error_ppm(tau_true, 25.0, sens_ppm_per_k(ISA_FLOOR_C),
                                     RATE_ISA_C_PER_S)
        robust.append({
            "tau_true_s": tau_true,
            "err_keep_10s_ppm": e_keep,
            "err_move_25s_ppm": e_move,
            "move_is_better": e_move < e_keep,
            "both_under_capture": max(e_keep, e_move) < CAPTURE_PPM,
        })
    r["robustness"] = robust

    # ---- 6. cold-start side effect of a longer EMA --------------------
    boot = []
    for ambient in (-40.0, -20.0, 0.0, 20.0):
        boot.append({
            "ambient_c": ambient,
            "initial_error_ppm": abs(offset_ppm(T0_DEFAULT, K_FORK)
                                     - offset_ppm(ambient, K_FORK)),
            "settle_1ppm_s_tau10": cold_start_settle_s(TAU_FW, T0_DEFAULT, ambient, K_FORK),
            "settle_1ppm_s_tau25": cold_start_settle_s(25.0, T0_DEFAULT, ambient, K_FORK),
        })
    r["cold_start"] = boot

    # ---- 7. the recommendation ----------------------------------------
    worst_err = max(p["err_tau10_isa_ppm"] for p in prof)
    r["recommendation"] = {
        "action_today": "KEEP TEMP_TC_SECS = 10.0 s (no firmware change)",
        "action_today_reasons": [
            "the lag is UNMEASURED (both sibling cards committed NO-DATA; k/T0 "
            "NO-FIT); moving a firmware constant on synthetic self-test numbers "
            "would be fabrication",
            "even the synthetic estimator value %.1f +/- %.1f s is BELOW the "
            "firmware's own committed change threshold of %.0f s "
            "(thermal_bench.py:538-541, bench/README.md:146) -- margin %.1f s, "
            "and still not crossed at +3 sigma"
            % (TAU_SYNTH, TAU_SYNTH_SIGMA, RULE_BENCH_THRESHOLD_S,
               RULE_BENCH_THRESHOLD_S - TAU_SYNTH),
        ],
        "conditional_action": (
            "if a real ramp CSV yields tau_die_to_crystal > %.0f s, set "
            "TEMP_TC_SECS = round(tau/%.0f)*%.0f s (a %.1f s result -> 25 s)"
            % (RULE_BENCH_THRESHOLD_S, RULE_LAG_ROUND_S, RULE_LAG_ROUND_S, TAU_SYNTH)),
        "open_loop_limited": True,
        "transient_is_binding": worst_err > CAPTURE_PPM,
        "worst_transient_err_ppm": worst_err,
        "capture_ppm": CAPTURE_PPM,
        "capture_margin_pct": 100.0 * (1.0 - worst_err / CAPTURE_PPM),
    }
    return r


def emit(r):
    w = print
    w("=" * 78)
    w("SELFCAL EMA TIME-CONSTANT EVALUATION -- meshcore:t_b59e2fc1")
    w("=" * 78)
    d = r["data_status"]
    w("DATA STATUS: %s" % d["hardware_lag"])
    w("  lag used below      : %.1f s -- %s" % (d["lag_value_used"], d["lag_provenance"]))
    w("  k/T0                : %s" % d["k_t0_status"])
    w("")
    w("--- STEP 1  lag vs EMA constant")
    c = r["comparison"]
    w("  lag (SYNTHETIC)     = %.1f +/- %.1f s" % (c["lag_s"], c["lag_sigma_s"]))
    w("  EMA constant        = %.1f s   [SelfCal.h:47]" % c["ema_s"])
    w("  ratio lag/EMA       = %.2f x   (%.2fx .. %.2fx at +/-1 sigma)"
      % (c["ratio"], c["ratio_lo"], c["ratio_hi"]))
    w("  delta lag-EMA       = %.1f s = %.1f sigma" % (c["delta_s"], c["delta_sigma"]))
    w("  independent families: hysteresis tau_hyst %.1f +/- %.2f s; loop-area %.1f +/- %.1f s"
      % (c["families"]["hysteresis_tau_hyst_s"], c["families"]["hysteresis_sigma_s"],
         c["families"]["loop_area_s"], c["families"]["loop_area_sigma_s"]))
    w("")
    w("--- STEP 2/3  the firmware tree's OWN two decision rules")
    rl, rb = r["rules"]["rule_lag"], r["rules"]["rule_bench"]
    w("  rule A  %s" % rl["source"])
    w("          %s -> fires=%s; implied value %.0f s"
      % (rl["condition"], rl["fires"], rl["implied_value_s"]))
    w("  rule B  %s" % rb["source"])
    w("          %s -> fires=%s (at +3 sigma: %s); margin %.1f s"
      % (rb["condition"], rb["fires"], rb["fires_at_plus_3_sigma"], rb["margin_s"]))
    w("  rules agree: %s" % r["rules"]["agree"])
    w("  NOTE: %s" % r["rules"]["note"])
    w("")
    w("--- STEP 4  open-loop transient error vs mission-profile temperature")
    w("  err_ppm = 2k|T-T0| * ramp_rate * |tau_ema - tau_lag|   (k=%.3f ppm/K^2,"
      " labelled: NOT measured)" % K_FORK)
    w("  %-24s %-10s %-10s %-11s %s"
      % ("point", "2k|T-T0|", "err@10s", "err@25s", "err@10s ISA"))
    for p in r["profile_errors"]:
        w("  %-24s %-10.2f %-10.2f %-11.2f %.2f%s"
          % (p["label"], p["sens_ppm_per_k"], p["err_tau10_bench_ppm"],
             p["err_tau25_bench_ppm"], p["err_tau10_isa_ppm"],
             "" if p["in_cal_range"] else "  [OUT OF CAL RANGE]"))
    w("  bench ramp %.3f C/s; ISA ascent %.4f C/s; BW125 capture window %.0f ppm"
      % (RATE_WORST, RATE_ISA_C_PER_S, CAPTURE_PPM))
    w("  worst tau=10 error is %.2f ppm = %.1f%% of the capture window -> margin %.1f%%"
      % (r["recommendation"]["worst_transient_err_ppm"],
         r["recommendation"]["worst_transient_err_ppm"] / CAPTURE_PPM * 100.0,
         r["recommendation"]["capture_margin_pct"]))
    cx = r["crossover"]
    w("  burning the ENTIRE %.0f ppm window with the current %.1f s mismatch needs"
      % (CAPTURE_PPM, cx["mismatch_s"]))
    w("    %.2f C/s (%.0f C/min) at the ISA-floor sensitivity %.2f ppm/K, or"
      % (cx["rate_isa_basis_C_per_s"], cx["rate_isa_basis_C_per_min"],
         cx["sens_isa_floor_ppm_per_k"]))
    w("    %.2f C/s (%.0f C/min) at the synthetic worst-window %.2f ppm/K"
      % (cx["rate_worst_basis_C_per_s"], 60.0 * cx["rate_worst_basis_C_per_s"],
         cx["sens_worst_ppm_per_k"]))
    w("  ISA ascent %.4f C/s is %.0fx (ISA basis) to %.0fx (mild basis) slower -> not binding"
      % (cx["isa_ascent_C_per_s"], cx["isa_headroom_isa_basis"],
         cx["isa_headroom_worst_basis"]))
    w("")
    w("--- STEP 4b  sign of the error, derived AND simulated")
    w("  err ~= +2k(tau_lag - tau_ema) * (dT/dt) * (T - T0)")
    w("  => OVER-shoots when the ramp moves AWAY from turnover, UNDER-shoots TOWARD.")
    w("  %-34s %-10s %-10s %-9s %s"
      % ("case", "max|err|", "signed", "sign ok?", "T at max"))
    for s in r["sign_law"]:
        w("  %-34s %-10.2f %+-10.2f %-9s %+.1f C"
          % (s["case"], s["max_abs_ppm"], s["signed_ppm_at_max"],
             "yes" if s["sign_matches"] else "NO", s["temp_at_max_c"]))
    w("")
    w("--- STEP 3b  robustness if the true lag turns out different (ISA floor)")
    w("  %-10s %-16s %-16s %-12s %s"
      % ("tau_true", "err @ keep 10s", "err @ move 25s", "move better?", "both < 72ppm"))
    for row in r["robustness"]:
        w("  %-10.1f %-16.2f %-16.2f %-12s %s"
          % (row["tau_true_s"], row["err_keep_10s_ppm"], row["err_move_25s_ppm"],
             "yes" if row["move_is_better"] else "NO",
             "yes" if row["both_under_capture"] else "NO"))
    w("")
    w("--- STEP 5  cost of a longer EMA at boot (SelfCal.h:100 seeds _temp_ema = T0)")
    w("  %-10s %-14s %-18s %s" % ("ambient", "initial err", "settle to 1ppm", "settle to 1ppm"))
    w("  %-10s %-14s %-18s %s" % ("(C)", "(ppm)", "@ tau=10 s", "@ tau=25 s"))
    for row in r["cold_start"]:
        w("  %-10.1f %-14.1f %-18.0f %.0f s"
          % (row["ambient_c"], row["initial_error_ppm"],
             row["settle_1ppm_s_tau10"], row["settle_1ppm_s_tau25"]))
    w("")
    w("-" * 78)
    w("VERDICT")
    w("-" * 78)
    rec = r["recommendation"]
    w("  firmware action : %s" % rec["action_today"])
    for i, reason in enumerate(rec["action_today_reasons"], 1):
        w("    %d. %s" % (i, reason))
    w("  conditional     : %s" % rec["conditional_action"])
    w("  open-loop limit : LIMITED (unconditional).  The compensation leads or")
    w("                    trails the crystal by the unmatched part of the lag and")
    w("                    there is NO closed-loop backstop: SelfCal.feedMeasured()")
    w("                    has zero call sites in the pinned tree, and the LR2021")
    w("                    datasheet (Rev 2.1) contains no FEI register -- the FEI")
    w("                    path is a verified dead end.")
    w("  binding on link?: %s -- worst case %.2f ppm against %.0f ppm of capture"
      % (rec["transient_is_binding"], rec["worst_transient_err_ppm"], rec["capture_ppm"]))
    w("=" * 78)


# --------------------------------------------------------------- self-test
def self_test():
    """Verify every analytic claim against simulation and against the sibling
    tools' own printed numbers.  Nothing is asserted that is not derived."""
    checks = []

    def chk(name, cond, detail=""):
        checks.append((name, bool(cond), detail))

    # 1. err is zero exactly when the EMA matches the lag (the design intent).
    chk("err == 0 at matched tau",
        transient_error_ppm(24.3, 24.3, SENS_WORST, RATE_WORST) == 0.0)

    # 2. reproduces analyze_thermal_lag.py's own printed 1.96 ppm bound
    #    (lead 24.2 s, sens 1.99 ppm/K, rate 0.041 C/s).
    got = transient_error_ppm(24.2, 0.0, SENS_WORST, RATE_WORST)
    chk("reproduces sibling 1.96 ppm bound", abs(got - 1.96) < 0.05, "%.3f" % got)

    # 3. the derived sign law matches simulation on all four ramp cases.
    for label, (t0c, t1c, rate) in {
        "cooling away": (25.0, -20.0, -RATE_WORST),
        "warming toward": (-20.0, 25.0, +RATE_WORST),
        "cooling away deep": (-20.0, -40.0, -RATE_WORST),
        "warming toward deep": (-40.0, -20.0, +RATE_WORST),
    }.items():
        _, signed, _, die, _, _, errs = ramp_case(
            K_FORK, T0_DEFAULT, TAU_SYNTH, TAU_FW, rate, t0c, t1c)
        t_at_max = die[errs.index(max(errs, key=abs))]
        pred = sign_law(TAU_SYNTH, TAU_FW, rate, t_at_max)
        chk("sign law matches sim (%s)" % label,
            (pred > 0) == (signed > 0),
            "predicted %+d, simulated %+.3f" % (pred, signed))

    # 4. the EXACT algebraic identity holds on a settled tail.  With
    #    u = T_die - T0, a = u_ema - u, b = u_x - u:
    #        err = k(u_ema^2 - u_x^2) = k*(a-b)*(a+b+2u)
    _, _, _, die, xtal, ema, errs = ramp_case(
        K_FORK, T0_DEFAULT, TAU_SYNTH, TAU_FW, -RATE_WORST, 25.0, -20.0)
    worst_rel = 0.0
    for i in range(2 * len(errs) // 3, len(errs)):
        u_die = die[i] - T0_DEFAULT
        a = ema[i] - T0_DEFAULT - u_die
        b = xtal[i] - T0_DEFAULT - u_die
        ident = K_FORK * (a - b) * (a + b + 2.0 * u_die)
        denom = max(1e-9, abs(errs[i]))
        worst_rel = max(worst_rel, abs(ident - errs[i]) / denom)
    chk("exact identity err=k(a-b)(a+b+2u) on settled tail",
        worst_rel < 1e-9, "worst rel dev %.2e" % worst_rel)

    # 4b. the settled closed form reproduces the simulated error at EVERY point
    #     of the tail.  A discrete one-pole driven by a linear ramp settles to a
    #     temperature offset of exactly |r|*L(tau) with the DISCRETE effective lag
    #         L(tau) = dt*(1-alpha)/alpha,  alpha = 1-exp(-dt/tau)
    #     (L -> tau as dt -> 0), so with a = -r*L_ema, b = -r*L_xtal:
    #         err = k*r*(L_ema - L_xtal)*(r*(L_ema + L_xtal) - 2u)
    dt = 1.0
    r_rate = -RATE_WORST
    L_ema = _eff_lag(TAU_FW, dt)
    L_xtal = _eff_lag(TAU_SYNTH, dt)
    worst_cf = 0.0
    for i in range(2 * len(errs) // 3, len(errs)):
        u_die = die[i] - T0_DEFAULT
        cf = K_FORK * r_rate * (L_ema - L_xtal) * (r_rate * (L_ema + L_xtal) - 2.0 * u_die)
        worst_cf = max(worst_cf, abs(cf - errs[i]) / max(1e-9, abs(errs[i])))
    chk("settled closed form matches sim at every tail point",
        worst_cf < 1e-4, "worst rel dev %.2e (L_ema %.4f, L_xtal %.4f)"
        % (worst_cf, L_ema, L_xtal))
    chk("discrete effective lag -> tau as dt -> 0",
        abs(_eff_lag(TAU_FW, 1e-4) - TAU_FW) < 1e-4,
        "L(1e-4 s) = %.6f vs tau %.1f" % (_eff_lag(TAU_FW, 1e-4), TAU_FW))
    chk("first-order correction is dt/2",
        abs((TAU_FW - _eff_lag(TAU_FW, 1.0)) - 0.5) < 0.02,
        "tau - L = %.4f" % (TAU_FW - _eff_lag(TAU_FW, 1.0)))

    # 5. matching the EMA collapses the simulated error by >10x.
    mx10 = ramp_case(K_FORK, T0_DEFAULT, TAU_SYNTH, TAU_FW, -RATE_WORST, 25.0, -20.0)[0]
    mx25 = ramp_case(K_FORK, T0_DEFAULT, TAU_SYNTH, 25.0, -RATE_WORST, 25.0, -20.0)[0]
    chk("matched EMA beats 10 s by >10x", mx10 / mx25 > 10.0,
        "%.2f / %.2f = %.1fx" % (mx10, mx25, mx10 / mx25))

    # 6. simulated max|err| matches the closed form at the temperature of max.
    pred_max = transient_error_ppm(TAU_SYNTH, TAU_FW, sens_ppm_per_k(-20.0), RATE_WORST)
    chk("closed form reproduces simulated max (cool 25->-20)",
        abs(mx10 - pred_max) <= 0.06 * pred_max,
        "sim %.3f vs closed form %.3f" % (mx10, pred_max))

    # 7. cold-start: a -20 C boot is already outside the capture window, and a
    #    25 s EMA converges exactly 2.5x slower.
    e0 = abs(offset_ppm(T0_DEFAULT, K_FORK) - offset_ppm(-20.0, K_FORK))
    chk("cold boot error exceeds capture window", e0 > CAPTURE_PPM, "%.1f ppm" % e0)
    s10 = cold_start_settle_s(TAU_FW, T0_DEFAULT, -20.0, K_FORK)
    s25 = cold_start_settle_s(25.0, T0_DEFAULT, -20.0, K_FORK)
    chk("tau=25 settles 2.5x slower", abs(s25 / s10 - 2.5) < 1e-9,
        "%.1f / %.1f" % (s25, s10))

    # 8. ratio arithmetic against the sibling card's reported 2.43x.
    chk("ratio 24.3/10 = 2.43", abs(TAU_SYNTH / TAU_FW - 2.43) < 0.005,
        "%.3f" % (TAU_SYNTH / TAU_FW))

    # 9. rule thresholds, as stated in the tree, reproduce the intended verdicts.
    chk("bench rule does NOT fire at 24.3 s", not (TAU_SYNTH > RULE_BENCH_THRESHOLD_S))
    chk("bench rule does NOT fire at +3 sigma either",
        not ((TAU_SYNTH + 3 * TAU_SYNTH_SIGMA) > RULE_BENCH_THRESHOLD_S),
        "%.1f s" % (TAU_SYNTH + 3 * TAU_SYNTH_SIGMA))
    chk("thermal-lag rule DOES fire (2x10=20 s < ci_lo %.1f s)" % TAU_SYNTH_LO,
        TAU_SYNTH_LO > RULE_LAG_FACTOR * TAU_FW)

    # 10. ISA rate arithmetic and both crossover bases.
    chk("ISA rate = 5 m/s x 6.5 K/km = 0.0325 C/s",
        abs(RATE_ISA_C_PER_S - 0.0325) < 1e-12, "%.4f" % RATE_ISA_C_PER_S)
    cx = build()["crossover"]
    chk("crossover at the ISA floor = 0.77 C/s",
        abs(cx["rate_isa_basis_C_per_s"] - 0.772) < 0.002,
        "%.4f C/s" % cx["rate_isa_basis_C_per_s"])
    chk("crossover at the 1.99 ppm/K window = 2.53 C/s",
        abs(cx["rate_worst_basis_C_per_s"] - 2.53) < 0.01,
        "%.4f C/s" % cx["rate_worst_basis_C_per_s"])
    chk("ISA headroom is 24x .. 78x",
        23.0 < cx["isa_headroom_isa_basis"] < 25.0
        and 77.0 < cx["isa_headroom_worst_basis"] < 79.0,
        "%.1fx .. %.1fx" % (cx["isa_headroom_isa_basis"],
                            cx["isa_headroom_worst_basis"]))

    # 11. the ISA floor is inside the firmware's own validity band.
    chk("ISA floor inside CAL_RANGE_C",
        abs(ISA_FLOOR_C - T0_DEFAULT) <= CAL_RANGE_C,
        "|%.1f - %.0f| = %.1f <= %.0f" % (ISA_FLOOR_C, T0_DEFAULT,
                                          abs(ISA_FLOOR_C - T0_DEFAULT), CAL_RANGE_C))

    # 12. even at the very worst case the transient does NOT bind the link.
    worst = max(p["err_tau10_isa_ppm"] for p in build()["profile_errors"])
    chk("transient not binding (worst < capture window)", worst < CAPTURE_PPM,
        "%.2f ppm vs %.0f ppm" % (worst, CAPTURE_PPM))

    ok = all(c[1] for c in checks)
    print("SELF-TEST (%d checks)" % len(checks))
    for name, passed, detail in checks:
        print("  [%s] %-52s %s" % ("PASS" if passed else "FAIL", name, detail))
    print("SELF-TEST %s" % ("PASS" if ok else "FAIL"))
    return 0 if ok else 1


def main(argv):
    if "--self-test" in argv:
        return self_test()
    if "--json" in argv:
        print(json.dumps(build(), indent=2))
        return 0
    emit(build())
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
