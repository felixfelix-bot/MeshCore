#!/usr/bin/env python3
"""
Reproducible Magnus-formula dew-point / frost-point table for the
condensation risk baseline.

Coefficients: Alduchov & Eskridge (1996).
  Water saturation: A_w = 17.625, B_w = 243.04
  Ice saturation:    A_i = 22.46,  B_i = 272.62

Inputs: warm-side ambient grid T = 20, 22, 25 C; RH = 30, 40, 50, 60 %.
Stdlib only (math).
"""

import math

A_W, B_W = 17.625, 243.04   # water
A_I, B_I = 22.46, 272.62    # ice

def dew_point_water(T, RH):
    """Magnus over water. T in C, RH in %."""
    if RH <= 0:
        return float('-inf')
    a = math.log(RH / 100.0) + A_W * T / (B_W + T)
    return B_W * a / (A_W - a)

def frost_point_ice(T, RH):
    """Magnus over ice. T in C, RH in %."""
    if RH <= 0:
        return float('-inf')
    a = math.log(RH / 100.0) + A_I * T / (B_I + T)
    return B_I * a / (A_I - a)

def fmt(x):
    if x is None:
        return "n/a"
    return f"{x:.1f}"

def main():
    temps = [20, 22, 25]
    rhs   = [30, 40, 50, 60]

    # sanity checks
    checks = [(22, 30, 4), (22, 50, 11), (22, 60, 14), (25, 50, 14)]
    print("=== Sanity checks (tolerance 1.5 C) ===")
    for T, RH, exp in checks:
        td = dew_point_water(T, RH)
        ok = "PASS" if abs(td - exp) <= 1.5 else "FAIL"
        print(f"  {T} C / {RH} % -> Td = {td:.1f} C  (expected ~{exp} C)  [{ok}]")
    print()

    print("=== Dew-point / frost-point table ===")
    print("| T [C] | RH [%] | Td water [C] | Tf ice [C] | sub-zero? |")
    print("|-------|--------|--------------|------------|-----------|")
    any_subzero = False
    for T in temps:
        for RH in rhs:
            td = dew_point_water(T, RH)
            tf = frost_point_ice(T, RH)
            sub = "YES" if td < 0 else "no"
            if td < 0:
                any_subzero = True
            tf_str = fmt(tf) if td < 0 else "n/a"
            print(f"| {T} | {RH} | {fmt(td)} | {tf_str} | {sub} |")
    print()
    print(f"Any sub-zero frost-point cell in this grid: {'YES' if any_subzero else 'NO'}")
    print("Coldest cell: 20 C / 30 % RH -> Td = "
          f"{dew_point_water(20,30):.1f} C (still above 0 C)")

    # Hand-worked example: 22 C / 50 % RH
    print()
    print("=== Hand-worked example: 22 C / 50 % RH ===")
    T, RH = 22, 50
    ln_term = math.log(RH/100.0)
    inner = A_W * T / (B_W + T)
    num = B_W * (ln_term + inner)
    den = A_W - ln_term - inner
    td = num / den
    print(f"  ln(RH/100) = ln(0.50) = {ln_term:.6f}")
    print(f"  A*T/(B+T) = {A_W}*{T}/({B_W}+{T}) = {inner:.6f}")
    print(f"  numerator   = {B_W}*({ln_term:.6f}+{inner:.6f}) = {num:.6f}")
    print(f"  denominator = {A_W}-{ln_term:.6f}-{inner:.6f} = {den:.6f}")
    print(f"  Td = {num:.6f}/{den:.6f} = {td:.2f} C")

    # Extended: what warm-side RH pushes dew point below 0 at each T?
    print()
    print("=== RH threshold for Td <= 0 C (dew point at/below freezing) ===")
    for T in [20, 22, 25]:
        lo, hi = 1.0, 100.0
        for _ in range(60):
            mid = (lo+hi)/2
            td = dew_point_water(T, mid)
            if td > 0:
                hi = mid
            else:
                lo = mid
        print(f"  T = {T} C: RH <= {lo:.1f} %  => Td <= 0 C")
        print(f"    (at RH = {lo:.0f}%: Td = {dew_point_water(T, lo):.2f} C)")

    # Cold-side surface temperatures
    print()
    print("=== Cold-side setpoints vs warm-side dew point ===")
    print("  If the warm-side connector/feedthrough surface cools below")
    print("  the lab dew point, condensation (Td > 0) or frost (Td <= 0)")
    print("  forms on the EXTERIOR of the feedthrough.")
    print()
    for T in [20, 22, 25]:
        for RH in [30, 40, 50, 60]:
            td = dew_point_water(T, RH)
            for sp in [-20, -40]:
                below = sp < td
                margin = td - sp
                print(f"  Lab {T} C / {RH}% (Td={td:.1f} C) vs cold side {sp} C: "
                      f"cold side is {margin:.1f} C below dew point "
                      f"-> {'CONDENSATION/FROST' if below else 'no condensation'}")

if __name__ == "__main__":
    main()