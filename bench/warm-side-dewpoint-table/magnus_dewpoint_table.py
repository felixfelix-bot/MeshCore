#!/usr/bin/env python3
"""
Reproducible Magnus dew/frost-point table for the warm-side ambient grid.

Card: compute the psychrometric core of the condensation baseline.
Grid: warm-side ambient T = 20, 22, 25 C x RH = 30, 40, 50, 60 % (12 cells,
ALL ASSUMED — provenance per bench/warm-side-ambient-register/ 83afdc21).

Method: Magnus formula, Alduchov & Eskridge (1996) coefficients.
  Water saturation, A = 17.625, B = 243.04:
    Td = B * (ln(RH/100) + A*T/(B+T)) / (A - ln(RH/100) - A*T/(B+T))
  Ice saturation, A = 22.46, B = 272.62 (same functional form),
  reported for a cell only where Td < 0 C ('n/a' otherwise).

Citations:
  Alduchov, O. A. & Eskridge, R. E. (1996). Improved Magnus' form
  approximation of saturation vapor pressure. J. Appl. Meteor., 35, 601-609.
  (water constants A = 17.625, B = 243.04)
  Sonntag, D. (1990). Z. Meteorol., 70, 340-344. (ice constants A = 22.46,
  B = 272.62, as prescribed by the task card)

Stdlib math only. Byte-identical reruns; output in output.txt.
"""

import math

# --- coefficients -----------------------------------------------------------
A_W, B_W = 17.625, 243.04   # water (Alduchov & Eskridge 1996)
A_I, B_I = 22.46, 272.62    # ice (Sonntag 1990; prescribed by task card)

# --- input grid (ALL CELLS ASSUMED) ------------------------------------------
TEMPS = [20, 22, 25]
RHS = [30, 40, 50, 60]


def dew_point(T, RH, A=A_W, B=B_W):
    """Td [C] from ambient T [C] and RH [%] via the Magnus form.

    Ambient above 0 C is in equilibrium with liquid water, so the dew
    point is computed over water with A_W/B_W; the ice pair A_I/B_I
    gives the frost point (same functional form).
    """
    g = A * T / (B + T)
    ln = math.log(RH / 100.0)
    return B * (ln + g) / (A - ln - g)


# --- sanity checks (card-specified anchors, tolerance ~1 C) -------------------
CHECKS = [
    (22, 30, 4.0),   # expected ~4 C
    (22, 50, 11.0),  # expected ~11 C
    (22, 60, 14.0),  # expected ~14 C
    (25, 50, 14.0),  # expected ~14 C
]
TOL = 1.0


def sanity_checks():
    print("=== Sanity checks (card anchors, tolerance 1.0 C) ===")
    all_pass = True
    for T, RH, expected in CHECKS:
        td = dew_point(T, RH)
        dev = td - expected
        ok = abs(dev) <= TOL
        all_pass = all_pass and ok
        print(f"  {T} C / {RH:2d} % -> Td = {td:5.2f} C "
              f"(expected ~{expected:.0f} C, dev {dev:+.2f} C)  "
              f"[{'PASS' if ok else 'FAIL - INVESTIGATE'}]")
    return all_pass


def main():
    checks_ok = sanity_checks()
    print()

    print("=== Magnus dew/frost-point table, warm-side ambient grid "
          "(ALL 12 CELLS ASSUMED) ===")
    print("Td = dew point over water (A=17.625, B=243.04, "
          "Alduchov & Eskridge 1996).")
    print("Tf = frost point over ice (A=22.46, B=272.62, Sonntag 1990), "
          "same functional form;")
    print("     reported only where Td < 0 C, else 'n/a'.")
    print()
    print("| T [C] | RH [%] | Td water [C] | Tf ice [C] |")
    print("|-------|--------|--------------|------------|")
    subzero = []
    for T in TEMPS:
        for RH in RHS:
            td = dew_point(T, RH)
            if td < 0.0:
                tf = dew_point(T, RH, A_I, B_I)
                subzero.append((T, RH, td, tf))
                print(f"| {T} | {RH} | {td:12.1f} | {tf:10.1f} |")
            else:
                print(f"| {T} | {RH} | {td:12.1f} |        n/a |")
    print()
    if subzero:
        print(f"Sub-zero frost-point cells: {len(subzero)} of 12 ->")
        for T, RH, td, tf in subzero:
            print(f"  {T} C / {RH} %: Td = {td:.1f} C, Tf = {tf:.1f} C")
    else:
        print("Sub-zero frost-point cells: 0 of 12.")
        coldest_T, coldest_RH = 20, 30   # card-specified coldest cell
        td_coldest = dew_point(coldest_T, coldest_RH)
        print(f"  Coldest cell (20 C / 30 % RH): Td = {td_coldest:.2f} C "
              f"(~{td_coldest:.1f} C), still ABOVE 0 C.")
        print("  -> NO cell in this grid yields a sub-zero frost point.")
        print("     Explicit negative statement: in every cell the ambient")
        print("     vapor pressure exceeds the triple-point pressure, so the")
        print("     ice-saturation isotherm sits above 0 C; vapor deposits")
        print("     as LIQUID at the Td isotherm (all Td = +1.9 to +16.7 C),")
        print("     and it can freeze only where a surface is below 0 C.")

    # --- hand-worked example row (numeric proof): T = 22 C, RH = 50 % --------
    print()
    print("=== Hand-worked example: T = 22 C, RH = 50 % (numeric proof) ===")
    T, RH = 22, 50
    g = A_W * T / (B_W + T)          # A*T/(B+T)
    ln = math.log(RH / 100.0)        # ln(RH/100)
    s = ln + g                       # substitution
    num = B_W * s                    # numerator
    den = A_W - s                    # denominator
    td = num / den
    print(f"  ln(RH/100)      = ln({RH/100.0:.2f})              = {ln:.6f}")
    print(f"  A*T/(B+T)       = {A_W}*{T}/({B_W}+{T})       = {g:.6f}")
    print(f"  s = ln(RH/100) + A*T/(B+T)   = {ln:.6f} + {g:.6f} = {s:.6f}")
    print(f"  numerator  B*s  = {B_W}*({s:.6f})  = {num:.6f}")
    print(f"  denominator A-s = {A_W} - ({s:.6f})   = {den:.6f}")
    print(f"  Td = {num:.6f} / {den:.6f} = {td:.2f} C  -> table row 22 / 50 -> 11.1 C")
    print()
    print(f"Sanity checks: {'ALL PASS' if checks_ok else 'FAILURES PRESENT'}")


if __name__ == "__main__":
    main()