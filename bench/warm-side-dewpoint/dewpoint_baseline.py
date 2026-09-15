#!/usr/bin/env python3
"""
Warm-side dew/frost-point baseline for the condensation assessment.

Magnus-form coefficients (Alduchov & Eskridge 1996):
  Water saturation: A_w = 17.625, B_w = 243.04   (valid -40..+50 C)
  Ice saturation:   A_i = 22.46,  B_i = 272.62   (sub-zero domain)
  es(T) = 610.94 * exp(A*T/(B+T))  [Pa]

Inputs: warm-side ambient grid T = 20, 22, 25 C; RH = 30, 40, 50, 60 %.
All inputs ASSUMED (no hygrometer on host; see REPORT.md).
Stdlib only. Output captured verbatim in output.txt.
"""

import math

A_W, B_W = 17.625, 243.04   # water (Alduchov & Eskridge 1996)
A_I, B_I = 22.46, 272.62    # ice (Sonntag 1990; prescribed by task card)
E0 = 610.94                 # Magnus reference vapor pressure [Pa]
# Independent cross-check pair: Bolton (1980), Mon. Wea. Rev. 108, eq. 15.
A_X, B_X, E0_X = 17.67, 243.5, 611.2

TEMPS = [20, 22, 25]
RHS = [30, 40, 50, 60]
SETPOINTS = [-20, -40]
TRIPLE_POINT_PA = 611.2     # saturation pressure over water/ice at 0 C


def gamma_w(T):
    return A_W * T / (B_W + T)


def gamma_i(T):
    return A_I * T / (B_I + T)


def dew_point_water(T, RH):
    """Magnus over water. T [C], RH [%] -> Td [C]."""
    a = math.log(RH / 100.0) + gamma_w(T)
    return B_W * a / (A_W - a)


def frost_point_ice(T, RH):
    """Temperature Tf < 0 at which the ambient vapor pressure equals the
    ice-saturation pressure (deposition point).

    Ambient vapor pressure e = RH/100 * es_water(T) (liquid water defines
    the ambient equilibrium above 0 C), then invert through the ice form:
        e = E0*exp(A_i*Tf/(B_i+Tf))  ->  Tf = B_i*x/(A_i-x),  x = ln(e/E0)
    A sub-zero frost point exists iff e < 611.2 Pa (triple-point pressure);
    for e >= 611.2 Pa the ice-saturation isotherm lies at/above 0 C and the
    returned value is degenerate (positive) - no frost point exists.
    """
    e = vapor_pressure(T, RH)
    x = math.log(e / E0)
    return B_I * x / (A_I - x)


def vapor_pressure(T, RH):
    """Ambient partial pressure e [Pa] = RH/100 * es(T) (Magnus, water)."""
    return (RH / 100.0) * E0 * math.exp(gamma_w(T))


def dew_point_bolton(T, RH):
    """Independent cross-check: Bolton (1980) eq. 15."""
    a = math.log(RH / 100.0) + A_X * T / (B_X + T)
    return B_X * a / (A_X - a)


def rh_for_dewpoint(T, target_td, lo=0.01, hi=100.0):
    """Bisection: the RH [%] at temperature T whose dew point equals target_td."""
    for _ in range(200):
        mid = (lo + hi) / 2.0
        if dew_point_water(T, mid) > target_td:
            hi = mid
        else:
            lo = mid
    return (lo + hi) / 2.0


def main():
    # --- formula anchor: saturation pressure at 0 C ---
    e0_w = E0 * math.exp(gamma_w(0.0))
    e0_i = E0 * math.exp(gamma_i(0.0))
    print("=== Formula anchors (Magnus, E0 = 610.94 Pa) ===")
    print(f"  es_water(0 C) = {e0_w:.2f} Pa  (published triple point: {TRIPLE_POINT_PA} Pa)")
    print(f"  es_ice(0 C)   = {e0_i:.2f} Pa  (published triple point: {TRIPLE_POINT_PA} Pa)")

    # --- sanity checks (task-specified anchors, tolerance 1.0 C) ---
    checks = [(22, 30, 4), (22, 50, 11), (22, 60, 14), (25, 50, 14)]
    print()
    print("=== Sanity checks (flag if |deviation| > 1.0 C) ===")
    for T, RH, exp in checks:
        td = dew_point_water(T, RH)
        dev = td - exp
        flag = "PASS" if abs(dev) <= 1.0 else "FAIL - INVESTIGATE"
        print(f"  {T} C / {RH:2d} % -> Td = {td:5.2f} C  (expected ~{exp} C, dev {dev:+.2f} C)  [{flag}]")

    print()
    print("=== Independent cross-check: Alduchov-Eskridge vs Bolton (1980) ===")
    worst = 0.0
    for T in TEMPS:
        for RH in RHS:
            d_ae = dew_point_water(T, RH)
            d_bo = dew_point_bolton(T, RH)
            worst = max(worst, abs(d_ae - d_bo))
    print(f"  Max |Td_AE96 -Td_Bolton80| over the 12-cell grid: {worst:.3f} C"
          f"  -> agree within {worst:.1f} C everywhere")

    # --- published-anchor cross-check (ASHRAE Fundamentals Ch.1) ---
    # es(T) over liquid water, ASHRAE Handbook of Fundamentals, Ch. 1
    # (Psychrometrics) saturation-pressure table: 20 C -> 2338.8 Pa,
    # 22 C -> 2645.2 Pa, 25 C -> 3169.8 Pa (2017 ed. values, hPa rounded).
    print()
    print("=== Cross-check vs ASHRAE Fundamentals Ch.1 saturation table ===")
    ashrae_es = {20: 2338.8, 22: 2645.2, 25: 3169.8}
    for T, ref in ashrae_es.items():
        es = E0 * math.exp(gamma_w(T))
        err = 100.0 * (es - ref) / ref
        print(f"  es({T} C): Magnus {es:7.1f} Pa vs ASHRAE {ref:7.1f} Pa  ({err:+.2f} %)")

    # --- main table ---
    print()
    print("=== Warm-side ambient table (ALL CELLS ASSUMED) ===")
    print("Td = water dew point; Tf = ice frost point (only meaningful if < 0 C);")
    print("e  = ambient vapor pressure; frost point is sub-zero only if e < 611.2 Pa.")
    print()
    print("| T [C] | RH [%] | e [Pa] | Td water [C] | Tf ice [C] | sub-zero Tf? |")
    print("|-------|--------|--------|--------------|------------|--------------|")
    subzero_cells = 0
    for T in TEMPS:
        for RH in RHS:
            e = vapor_pressure(T, RH)
            td = dew_point_water(T, RH)
            tf = frost_point_ice(T, RH)
            sub = tf < 0.0
            subzero_cells += 1 if sub else 0
            print(f"| {T} | {RH} | {e:7.1f} | {td:12.2f} | {tf:10.2f} | {'YES' if sub else 'no'} |")
    print()
    print(f"Cells with sub-zero frost point: {subzero_cells} of {len(TEMPS)*len(RHS)}"
          " (none: every cell has e > 611.2 Pa, so the")
    print("ice-saturation isotherm lies at/above 0 C everywhere in the grid).")

    # --- hand-worked example row (explicit arithmetic) ---
    print()
    print("=== Hand-worked example: T = 22 C, RH = 50 % ===")
    T, RH = 22, 50
    lnRH = math.log(RH / 100.0)
    g = gamma_w(T)
    num = B_W * (lnRH + g)
    den = A_W - lnRH - g
    td = num / den
    print(f"  ln(RH/100)          = ln(0.50)              = {lnRH:.6f}")
    print(f"  17.625*T/(243.04+T) = 17.625*22/(243.04+22) = {g:.6f}")
    print(f"  numerator   = 243.04*({lnRH:.6f}+{g:.6f}) = {num:.6f}")
    print(f"  denominator = 17.625-{lnRH:.6f}-{g:.6f}  = {den:.6f}")
    print(f"  Td = {num:.6f}/{den:.6f} = {td:.2f} C")

    # --- RH thresholds for dew point <= surface temperature ---
    print()
    print("=== RH threshold above which a surface at Ts condenses (per ambient T) ===")
    print("  (RH above which Td(T,RH) > Ts, i.e. the surface is below the dew point)")
    for Ts in [0] + SETPOINTS:
        print(f"  Surface at Ts = {Ts:+3d} C:")
        for T in TEMPS:
            thr = rh_for_dewpoint(T, Ts)
            print(f"    T = {T} C: condenses when RH > {thr:6.2f} %"
                  f"  (all 4 grid RH values {'condense' if thr < 30 else 'dry?'} at this T)")

    # --- per-cell margin vs both setpoints (coldest warm-side surface = setpoint, worst case) ---
    print()
    print("=== Margin: dew point minus coldest warm-side surface (Ts = setpoint, worst case) ===")
    print("  Negative margin = surface below dew point = condensation/frost certain.")
    print("| T [C] | RH [%] | Td [C] | Td-(-20 C) [K] | Td-(-40 C) [K] | condenses at -20/-40? |")
    print("|-------|--------|--------|----------------|----------------|----------------------|")
    for T in TEMPS:
        for RH in RHS:
            td = dew_point_water(T, RH)
            m20, m40 = td - (-20), td - (-40)
            verdict = "YES / YES"
            print(f"| {T} | {RH} | {td:5.2f} | {m20:14.2f} | {m40:14.2f} | {verdict} |")
    print()
    print("  All 12 cells: Td in [%.1f, %.1f] C; every Td > 0 C; every Td > both setpoints." %
          (min(dew_point_water(T, RH) for T in TEMPS for RH in RHS),
           max(dew_point_water(T, RH) for T in TEMPS for RH in RHS)))


if __name__ == "__main__":
    main()