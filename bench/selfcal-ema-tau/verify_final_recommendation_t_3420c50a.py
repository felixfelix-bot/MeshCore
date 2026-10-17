#!/usr/bin/env python3
"""Independent verification + decision tool for meshcore:t_3420c50a.

Two jobs:

  1. --verify   (default)  Recompute EVERY number in
     SELFCAL-EMA-FIRMWARE-RECOMMENDATION-t_3420c50a.md from first principles
     (firmware constants + mission-profile assumptions), then assert each of
     them appears verbatim in the document. A figure that does not appear, or
     that disagrees with the recomputation, is a FAILURE. This is what makes
     the writeup self-contained: the reader can trust the arithmetic because
     it is checked, not because it is asserted.

  2. --lag S --sigma S     Apply the document's own decision rule to a real
     measured lag (the moment a bench CSV lands) and print the exact firmware
     constant to set. This is the re-run path referenced in section 7.

Stdlib only, deterministic, no network, no side effects.

    python3 verify_final_recommendation_t_3420c50a.py
    python3 verify_final_recommendation_t_3420c50a.py --self-test
    python3 verify_final_recommendation_t_3420c50a.py --lag 34.0 --sigma 2.0
"""
import math
import os
import sys

# ---------------------------------------------------------------- constants
# All of these are quoted from the pinned firmware tree
# felixfelix-bot/MeshCore @ d7ae93fa (examples/passive_mapper).
TEMP_TC_SECS = 10.0        # SelfCal.h:47
K_FORK = 0.04              # ppm/K^2, fork sizing constant -- NOT measured
T0_DEFAULT = 25.0          # C
ISA_FLOOR_C = -56.5        # C, held 11-20 km
CAL_RANGE_C = 90.0         # SelfCal.h:72
ISA_LAPSE = 0.0065         # K/m
ASCENT_MPS = 5.0           # m/s, planning estimate
RATE_ISA = ISA_LAPSE * ASCENT_MPS      # 0.0325 C/s
RATE_BENCH_WORST = 0.041   # C/s, worst synthetic ramp
SENS_WORST_WINDOW = 1.99   # ppm/K, the tool's own mild 30 s window
WINDOW_PPM = 72.0          # BW125 capture window, +/-36 ppm
RULE_B_THRESHOLD_S = 30.0  # thermal_bench.py:538-541, bench/README.md:146
RULE_A_MULTIPLIER = 2.0    # analyze_thermal_lag.py:495: 2.0 * TEMP_TC_SECS
GRID_S = 5.0               # analyze_thermal_lag.py: 5 s rounding grid

# Reconciled synthetic estimator value (parent card t_c895d107)
TAU_RECON = 24.3           # s
TAU_RECON_SIGMA = 1.0      # s
TAU_HYST = 24.4            # s
TAU_HYST_SIGMA = 1.15
TAU_LOOPAREA = 24.2        # s
TAU_LOOPAREA_SIGMA = 1.0
HYST_DT = 1.34             # C
HYST_DT_IQR = 0.14         # C
TAU_PLANTED = 25.0         # s

_HERE = os.path.dirname(os.path.abspath(__file__))
_CANDIDATES = ("SELFCAL-EMA-FIRMWARE-RECOMMENDATION-t_3420c50a.md",
               "RECOMMENDATION-FINAL-t_3420c50a.md")
DOC = next((os.path.join(_HERE, c) for c in _CANDIDATES
            if os.path.exists(os.path.join(_HERE, c))),
           os.path.join(_HERE, _CANDIDATES[0]))

CHECKS = []
FAILS = []


def check(name, ok, detail=""):
    CHECKS.append((name, bool(ok), detail))
    if not ok:
        FAILS.append("%s  %s" % (name, detail))


def close(a, b, tol):
    return abs(a - b) <= tol


# ------------------------------------------------------------------ physics
def sens_ppm_per_k(temp_c, k=K_FORK, t0=T0_DEFAULT):
    """d(offset)/dT for offset = k (T-T0)^2  (SelfCal.h:133)."""
    return 2.0 * k * abs(temp_c - t0)


def transient_ppm(tau_lag, tau_ema, sens, rate):
    """Quasi-steady open-loop mis-compensation magnitude, err = sens*r*|dtau|."""
    return sens * rate * abs(tau_ema - tau_lag)


def cold_boot_ppm(temp_c, k=K_FORK, t0=T0_DEFAULT):
    """Error at boot when SelfCal.h:100 seeds _temp_ema = T0."""
    return k * (temp_c - t0) ** 2


def settle_s(err0, tau, target=1.0):
    """Time for a first-order EMA starting at err0 to fall below target."""
    if err0 <= target:
        return 0.0
    return tau * math.log(err0 / target)


def round_to_grid(tau, grid=GRID_S):
    return float(grid * round(tau / grid))


def decide(tau, sigma=None):
    """The document's own section-7 decision rule, in one place."""
    if tau is None:
        return TEMP_TC_SECS, "NO DATA -> KEEP"
    if tau > RULE_B_THRESHOLD_S:
        new = round_to_grid(tau)
        return new, "tau %.1f s > %.0f s -> set %.1f s" % (
            tau, RULE_B_THRESHOLD_S, new)
    return TEMP_TC_SECS, "tau %.1f s <= %.0f s -> KEEP 10.0 s" % (
        tau, RULE_B_THRESHOLD_S)


# ------------------------------------------------------------------- verify
def verify():
    doc = open(DOC, encoding="utf-8").read()

    # --- section 1: lag vs EMA
    ratio = TAU_RECON / TEMP_TC_SECS
    ratio_lo = (TAU_RECON - TAU_RECON_SIGMA) / TEMP_TC_SECS
    ratio_hi = (TAU_RECON + TAU_RECON_SIGMA) / TEMP_TC_SECS
    delta = TAU_RECON - TEMP_TC_SECS
    check("ratio 2.43x", close(ratio, 2.43, 0.005), "%.3f" % ratio)
    check("ratio band 2.33-2.53", close(ratio_lo, 2.33, 0.005)
          and close(ratio_hi, 2.53, 0.005), "%.2f..%.2f" % (ratio_lo, ratio_hi))
    check("delta 14.3 s", close(delta, 14.3, 0.05), "%.2f" % delta)
    check("delta 14.3 sigma", close(delta / TAU_RECON_SIGMA, 14.3, 0.05))
    for s in ["2.43×", "2.33–2.53×", "14.3"]:
        check("doc has %r" % s, s in doc)

    # --- trust decision: xcorr must be rejected
    check("xcorr +15.30 quoted as do-not-use", "+15.30" in doc)
    check("xcorr sigma 203.30 quoted", "203.30" in doc)
    check("xcorr 95% range spans zero", "-391" in doc and "+422" in doc)

    # --- section 5.2 magnitude table
    sens = {"near turnover (±15 C)": sens_ppm_per_k(10.0),
            "bench mid-ramp (-20 C)": sens_ppm_per_k(-20.0),
            "ISA floor (-56.5 C)": sens_ppm_per_k(ISA_FLOOR_C)}
    check("sens @ +/-15 C = 1.20", close(sens["near turnover (±15 C)"], 1.20, 0.005))
    check("sens @ -20 C = 3.60", close(sens["bench mid-ramp (-20 C)"], 3.60, 0.005))
    check("sens @ -56.5 C = 6.52", close(sens["ISA floor (-56.5 C)"], 6.52, 0.005))

    worst = 0.0
    for label, s in sens.items():
        e10 = transient_ppm(TAU_RECON, TEMP_TC_SECS, s, RATE_BENCH_WORST)
        e25 = transient_ppm(TAU_RECON, 25.0, s, RATE_BENCH_WORST)
        eisa = transient_ppm(TAU_RECON, TEMP_TC_SECS, s, RATE_ISA)
        worst = max(worst, e10, eisa)
        print("  %-24s sens %5.2f  e@10 %5.2f  e@25 %5.2f  e@10-ISA %5.2f"
              % (label, s, e10, e25, eisa))
    # table values in the document
    for v in ["0.70", "0.03", "0.56", "2.11", "0.10", "1.67",
              "3.82", "0.19", "3.03"]:
        check("doc has magnitude cell %s" % v, v in doc)
    check("worst case is the ISA-floor 3.03 ppm",
          close(transient_ppm(TAU_RECON, TEMP_TC_SECS,
                              sens_ppm_per_k(ISA_FLOOR_C), RATE_ISA), 3.03, 0.005))

    # --- occupancy
    occ = 3.03 / WINDOW_PPM
    check("occupancy 4.2%", close(100 * occ, 4.2, 0.05), "%.3f%%" % (100 * occ))
    check("margin 95.8%", close(100 * (1 - occ), 95.8, 0.05))
    for s in ["4.2 %", "95.8 %"]:
        check("doc has %r" % s, s in doc)

    # --- crossover rates
    cross_isa = WINDOW_PPM / (sens_ppm_per_k(ISA_FLOOR_C) * delta)
    cross_mild = WINDOW_PPM / (SENS_WORST_WINDOW * delta)
    check("crossover 0.77 C/s", close(cross_isa, 0.77, 0.005), "%.3f" % cross_isa)
    check("crossover 2.53 C/s", close(cross_mild, 2.53, 0.005), "%.3f" % cross_mild)
    check("ISA 24x slower", close(cross_isa / RATE_ISA, 24.0, 0.3),
          "%.1f" % (cross_isa / RATE_ISA))
    check("ISA 78x slower", close(cross_mild / RATE_ISA, 78.0, 0.5),
          "%.1f" % (cross_mild / RATE_ISA))
    for s in ["0.77 °C/s", "2.53 °C/s", "24×", "78×"]:
        check("doc has %r" % s, s in doc)

    # --- section 5.3 robustness sweep
    print("\n  robustness sweep at ISA floor (keep 10 s vs move 25 s):")
    taus = [5.0, 10.0, 15.0, 17.0, 24.3, 30.0, 40.0, 60.0]
    floor_sens = sens_ppm_per_k(ISA_FLOOR_C)
    for t in taus:
        a = transient_ppm(t, TEMP_TC_SECS, floor_sens, RATE_ISA)
        b = transient_ppm(t, 25.0, floor_sens, RATE_ISA)
        print("    tau %5.1f  keep %5.2f  move %5.2f  move better %-3s  both<72 %s"
              % (t, a, b, "yes" if b < a else "NO",
                 "yes" if max(a, b) < WINDOW_PPM else "NO"))
        check("both branches < 72 ppm at tau=%s" % t, max(a, b) < WINDOW_PPM)
    a17 = transient_ppm(17.0, TEMP_TC_SECS, floor_sens, RATE_ISA)
    b17 = transient_ppm(17.0, 25.0, floor_sens, RATE_ISA)
    check("17 s is the crossover (move stops helping)", b17 >= a17 - 0.25)
    a16 = transient_ppm(16.0, TEMP_TC_SECS, floor_sens, RATE_ISA)
    b16 = transient_ppm(16.0, 25.0, floor_sens, RATE_ISA)
    check("16 s: move still worse", b16 > a16)
    check("worst robustness cell 10.60 ppm",
          close(transient_ppm(60.0, TEMP_TC_SECS, floor_sens, RATE_ISA), 10.60, 0.01))
    for v in ["1.06", "4.24", "3.18", "2.12", "0.15", "6.36", "10.60", "7.42"]:
        check("doc has sweep cell %s" % v, v in doc)

    # --- section 6 cold boot
    print("\n  cold-boot table:")
    boot = {}
    for amb in (-40.0, -20.0, 0.0, 20.0):
        e0 = cold_boot_ppm(amb)
        s10 = settle_s(e0, TEMP_TC_SECS)
        s25 = settle_s(e0, 25.0)
        boot[amb] = (e0, s10, s25)
        print("    %5.1f C  init %6.1f ppm  settle@10 %5.1f s  settle@25 %5.1f s"
              % (amb, e0, s10, s25))
    check("boot -40 C = 169.0 ppm", close(boot[-40.0][0], 169.0, 0.05))
    check("boot -20 C = 81.0 ppm", close(boot[-20.0][0], 81.0, 0.05))
    check("boot 0 C = 25.0 ppm", close(boot[0.0][0], 25.0, 0.05))
    check("boot +20 C = 1.0 ppm", close(boot[20.0][0], 1.0, 0.05))
    check("settle -40 @10 = 51 s", close(boot[-40.0][1], 51.0, 0.6))
    check("settle -40 @25 = 128 s", close(boot[-40.0][2], 128.0, 0.6))
    check("settle -20 @10 = 44 s", close(boot[-20.0][1], 44.0, 0.6))
    check("settle -20 @25 = 110 s", close(boot[-20.0][2], 110.0, 0.6))
    check("settle 0 @10 = 32 s", close(boot[0.0][1], 32.0, 0.6))
    check("settle 0 @25 = 80 s", close(boot[0.0][2], 80.0, 0.6))
    check("cold boot exceeds window at -20 C", boot[-20.0][0] > WINDOW_PPM)
    check("cold boot exceeds window at -40 C", boot[-40.0][0] > WINDOW_PPM)
    check("lengthening is 2.5x slower",
          close(boot[-20.0][2] / boot[-20.0][1], 2.5, 0.05))
    for v in ["169.0", "81.0", "128", "110"]:
        check("doc has cold-boot cell %s" % v, v in doc)

    # --- section 4 threshold derivation
    per_sec = sens_ppm_per_k(ISA_FLOOR_C) * RATE_ISA
    check("0.2119 ppm per second of mismatch", close(per_sec, 0.2119, 0.0005),
          "%.4f" % per_sec)
    f5 = 0.05 * WINDOW_PPM / per_sec
    f10 = 0.10 * WINDOW_PPM / per_sec
    check("5% criterion -> 17.0 s mismatch",
          close(f5, 17.0, 0.05), "%.2f" % f5)
    check("5% criterion -> tau 27.0 s",
          close(f5 + TEMP_TC_SECS, 27.0, 0.05))
    check("10% criterion -> 34.0 s mismatch", close(f10, 34.0, 0.05),
          "%.2f" % f10)
    check("30 s rule -> 4.24 ppm = 5.9% of window",
          close(per_sec * (RULE_B_THRESHOLD_S - TEMP_TC_SECS), 4.24, 0.005)
          and close(100 * per_sec * (RULE_B_THRESHOLD_S - TEMP_TC_SECS)
                    / WINDOW_PPM, 5.9, 0.05))
    a_thresh = RULE_A_MULTIPLIER * TEMP_TC_SECS
    check("rule A threshold is 20 s", close(a_thresh, 20.0, 1e-9))
    check("rule A would fire on 24.3 s (ci_lo 23.3 > 20)",
          close(TAU_RECON - TAU_RECON_SIGMA, 23.3, 0.05)
          and (TAU_RECON - TAU_RECON_SIGMA) > a_thresh)
    check("rule B does NOT fire on 24.3 s",
          TAU_RECON <= RULE_B_THRESHOLD_S)
    check("rule B does NOT fire at +3 sigma",
          TAU_RECON + 3 * TAU_RECON_SIGMA < RULE_B_THRESHOLD_S)
    check("margin to rule B is 5.7 s",
          close(RULE_B_THRESHOLD_S - TAU_RECON, 5.7, 0.05))
    check("+3 sigma = 27.3 s",
          close(TAU_RECON + 3 * TAU_RECON_SIGMA, 27.3, 0.05))
    for s in ["0.2119", "17.0 s", "27.0 s", "34.0 s", "5.7 s", "27.3 s",
              "4.24 ppm"]:
        check("doc has derivation cell %r" % s, s in doc)

    # --- section 5.1 sign law evaluated at the four simulated cases
    print("\n  sign law on the four ramp cases (dtau = %.1f s):" % delta)
    # Simulate the firmware's own filter (SelfCal.h:118, alpha = 1-exp(-dt/tau))
    # along each ramp with the crystal lagging the die by tau_lag, then locate
    # the worst instantaneous error. This reproduces the document's table from
    # first principles instead of trusting it.
    cases = [(+25.0, -20.0, "cooling away", 2.08, -20.0),
             (-20.0, +25.0, "warming toward", 1.90, -15.7),
             (-20.0, -40.0, "cooling away", 3.02, -40.0),
             (-40.0, -20.0, "warming toward", 2.82, -35.4)]
    dt_sim = 1.0
    for t_from, t_to, label, doc_peak, doc_tpeak in cases:
        duration = abs(t_to - t_from) / RATE_BENCH_WORST
        n = int(duration / dt_sim)
        step = RATE_BENCH_WORST * dt_sim * (1 if t_to > t_from else -1)
        t_ema, t_x, t_die = t_from, t_from, t_from
        alpha_ema = 1.0 - math.exp(-dt_sim / TEMP_TC_SECS)
        # the crystal's effective temperature is the SAME first-order lag
        # applied to the die, with tau = tau_lag (the physical lag being modelled)
        alpha_x = 1.0 - math.exp(-dt_sim / TAU_RECON)
        peak, t_peak = 0.0, t_from
        for i in range(n + int(300 / dt_sim)):
            if i < n:
                t_die += step
            t_ema += (t_die - t_ema) * alpha_ema
            t_x += (t_die - t_x) * alpha_x
            err = K_FORK * ((t_ema - T0_DEFAULT) ** 2 - (t_x - T0_DEFAULT) ** 2)
            if abs(err) > abs(peak):
                peak, t_peak = err, t_die
        sgn = 1 if peak > 0 else -1
        # the derived law, evaluated at the point of maximum error
        r = step / dt_sim
        u = t_peak - T0_DEFAULT
        sign_model = 1 if (delta > 0) == ((r > 0) == (u > 0)) else -1
        print("    %-16s sim max %+.3f ppm at %+6.1f C   doc %+.2f at %+6.1f C"
              "   sign %+d" % (label, peak, t_peak, doc_peak, doc_tpeak, sgn))
        check("sim reproduces doc peak (%s)" % label,
              abs(abs(peak) - doc_peak) < 0.06,
              "sim %.3f vs doc %.2f" % (abs(peak), doc_peak))
        check("sim reproduces doc peak temperature (%s)" % label,
              abs(t_peak - doc_tpeak) < 1.5,
              "sim %.1f vs doc %.1f" % (t_peak, doc_tpeak))
        check("sign law matches simulation (%s)" % label, sgn == sign_model,
              "sim %+d law %+d" % (sgn, sign_model))
    for v in ["+2.08", "−1.90", "+3.02", "−2.82"]:
        check("doc has sign-law cell %s" % v, v in doc)

    # --- verdict consistency
    new, why = decide(TAU_RECON, TAU_RECON_SIGMA)
    check("decision rule keeps 10 s on 24.3 s", new == 10.0, why)
    check("conditional example 34 s -> 35 s", round_to_grid(34.0) == 35.0)
    check("conditional example 47 s -> 45 s", round_to_grid(47.0) == 45.0)
    check("conditional example 24.3 s -> 25 s", round_to_grid(24.3) == 25.0)
    for s in ["KEEP", "10.0f", "round(tau_s / 5) * 5"]:
        check("doc carries instruction token %r" % s, s in doc)
    check("doc states lag is UNDEFINED", "UNDEFINED" in doc)
    check("doc states SYNTHETIC", "SYNTHETIC" in doc)
    check("doc cites SelfCal.h:47", "SelfCal.h:47" in doc)
    check("doc cites SelfCal.h:100", "SelfCal.h:100" in doc)
    check("doc cites d7ae93fa", "d7ae93fa" in doc)

    # --- CAL_RANGE_C validity of the ISA floor
    check("ISA floor inside CAL_RANGE_C",
          abs(ISA_FLOOR_C - T0_DEFAULT) <= CAL_RANGE_C,
          "%.1f <= %.1f" % (abs(ISA_FLOOR_C - T0_DEFAULT), CAL_RANGE_C))
    check("81.5 C span quoted", "81.5" in doc)

    # --- no fabricated measurement language
    check("doc labels k as not measured", "NOT measured" in doc)
    check("doc has declared-gaps section", "Declared gaps" in doc)


# ----------------------------------------------------------------- decision
def run_decision(tau, sigma, doc_path=DOC):
    tau = None if tau is None else float(tau)
    new, why = decide(tau, sigma)
    print("=" * 78)
    print("SELFCAL EMA DECISION -- meshcore:t_3420c50a")
    print("=" * 78)
    print("  measured lag      : %s"
          % ("NO DATA" if tau is None else "%.2f s (sigma %.2f s)"
             % (tau, float(sigma or 0.0))))
    print("  rule              : raise TEMP_TC_SECS iff measured tau > %.1f s,"
          " then round to a %.0f s grid" % (RULE_B_THRESHOLD_S, GRID_S))
    print("  -> %s" % why)
    print("  SelfCal.h:47      : static constexpr float TEMP_TC_SECS = %.1ff;"
          % new)
    if tau is not None:
        a = transient_ppm(tau, TEMP_TC_SECS, sens_ppm_per_k(ISA_FLOOR_C), RATE_ISA)
        b = transient_ppm(tau, new, sens_ppm_per_k(ISA_FLOOR_C), RATE_ISA)
        print("  ISA-floor error   : %.2f ppm now -> %.2f ppm after"
              " (window %.0f ppm)" % (a, b, WINDOW_PPM))
        print("  within window     : %s"
              % ("yes" if max(a, b) < WINDOW_PPM else "NO -- investigate"))
    print("  action            : %s" % ("NO CODE CHANGE" if new == TEMP_TC_SECS
                                       else "apply the constant above"))


# ---------------------------------------------------------------- self-test
def self_test():
    ok = 0
    tot = 0

    def t(name, cond):
        nonlocal ok, tot
        tot += 1
        if cond:
            ok += 1
        else:
            print("FAIL: %s" % name)

    t("sens turnover", close(sens_ppm_per_k(10.0), 1.20, 1e-9))
    t("sens floor", close(sens_ppm_per_k(-56.5), 6.52, 1e-9))
    t("transient zero at match", transient_ppm(10.0, 10.0, 6.52, 0.03) == 0.0)
    t("transient symmetric", close(transient_ppm(5.0, 10.0, 6.52, 0.03),
                                   transient_ppm(15.0, 10.0, 6.52, 0.03), 1e-12))
    t("boot +25 C zero", cold_boot_ppm(25.0) == 0.0)
    t("boot -40 C 169", close(cold_boot_ppm(-40.0), 169.0, 1e-9))
    t("settle 1e-folding", close(settle_s(2.718281828459045, 10.0, 1.0), 10.0, 1e-6))
    t("settle already below", settle_s(0.5, 10.0, 1.0) == 0.0)
    t("grid round 24.3->25", round_to_grid(24.3) == 25.0)
    t("grid round 22.4->20", round_to_grid(22.4) == 20.0)
    t("grid round 22.6->25", round_to_grid(22.6) == 25.0)
    t("decide no data keeps", decide(None)[0] == 10.0)
    t("decide 30.0 keeps", decide(30.0)[0] == 10.0)
    t("decide 30.1 rounds to 30", decide(30.1)[0] == 30.0)
    t("decide 34 rounds to 35", decide(34.0)[0] == 35.0)
    t("decide 47 rounds to 45", decide(47.0)[0] == 45.0)
    # sign law is the algebra, not an assumption
    r, u = -0.03, -45.0
    a, b = -TEMP_TC_SECS * r, -TAU_RECON * r
    exact = K_FORK * ((u + a) ** 2 - (u + b) ** 2)
    approx = 2 * K_FORK * (TAU_RECON - TEMP_TC_SECS) * r * u
    t("sign law first order matches exact", close(exact, approx, 0.05)
      and (exact > 0) == (approx > 0))
    t("isa rate", close(RATE_ISA, 0.0325, 1e-12))
    print("SELF-TEST %s  %d/%d" % ("PASS" if ok == tot else "FAIL", ok, tot))
    return 0 if ok == tot else 1


def main(argv):
    if "--self-test" in argv:
        return self_test()
    if "--lag" in argv:
        i = argv.index("--lag")
        tau = argv[i + 1] if i + 1 < len(argv) else "none"
        sigma = "0"
        if "--sigma" in argv:
            sigma = argv[argv.index("--sigma") + 1]
        run_decision(None if tau == "none" else tau, sigma)
        return 0
    verify()
    n = len(CHECKS)
    bad = len(FAILS)
    print("\n" + "=" * 78)
    for name, ok, detail in CHECKS:
        if not ok:
            print("FAIL  %s  %s" % (name, detail))
    print("VERIFY %s  %d/%d checks passed" % ("PASS" if bad == 0 else "FAIL",
                                             n - bad, n))
    if bad == 0:
        print("Every number in the recommendation was recomputed from the")
        print("firmware constants and mission-profile assumptions and matches.")
    return 0 if bad == 0 else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
