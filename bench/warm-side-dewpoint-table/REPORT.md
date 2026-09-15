# Magnus dew/frost-point table — warm-side ambient grid

Task (fleet offload, meshcore): compute the reproducible psychrometric
table that is the quantitative core of the condensation baseline, for the
warm-side ambient grid T = 20, 22, 25 C x RH = 30, 40, 50, 60 % (12 cells).
Scope: analysis only — no heating/insulation/mitigation design, no
codebase changes outside this directory.

Date: 2026-09-15 · Repo: meshcore (main) · Worker: dq05.
Artifacts: this directory (`bench/warm-side-dewpoint-table/`) —
`magnus_dewpoint_table.py` (runnable, stdlib `math` only), `output.txt`
(verbatim run).

Input provenance: all 12 ambient cells are **ASSUMED** (planning bracket,
zero anchoring to this bench) — carried by
`bench/warm-side-ambient-register/` (83afdc21) and originally from fleet
cards t_1add22bc / t_09c431c2 via `bench/condensation-risk/` §1b (65c9c3df).
This task is independent of whether a hygrometer reading exists; none does
(no probe on bench, per 83afdc21).

Method: Magnus formula, Alduchov & Eskridge (1996) coefficients.
Water saturation, A = 17.625, B = 243.04:

    Td = B * (ln(RH/100) + A*T/(B+T)) / (A - ln(RH/100) - A*T/(B+T))

Ice saturation, A = 22.46, B = 272.62 (same functional form), used only
where Td < 0 C.

---

## (a) Table — 12 rows, all cells ASSUMED

| T [C] | RH [%] | Td water [C] | Tf ice [C] |
|-------|--------|--------------|------------|
| 20 | 30 | 1.9 | n/a |
| 20 | 40 | 6.0 | n/a |
| 20 | 50 | 9.3 | n/a |
| 20 | 60 | 12.0 | n/a |
| 22 | 30 | 3.6 | n/a |
| 22 | 40 | 7.8 | n/a |
| 22 | 50 | 11.1 | n/a |
| 22 | 60 | 13.9 | n/a |
| 25 | 30 | 6.2 | n/a |
| 25 | 40 | 10.5 | n/a |
| 25 | 50 | 13.9 | n/a |
| 25 | 60 | 16.7 | n/a |

Full-precision Td range: +1.89 C (20 C / 30 %) to +16.70 C (25 C / 60 %).

## Frost-point note (explicit negative statement)

**NO cell in this grid yields a sub-zero frost point.** Every one of the
12 cells has Td > 0 C, so the ice branch never activates and the Tf
column is 'n/a' throughout — 0 of 12 cells sub-zero. The coldest cell,
20 C / 30 % RH, gives Td = 1.89 C (~1.9 C), still above 0 C, exactly as
expected. Physical reason: in every cell the ambient vapor pressure
e = RH/100 · es_water(T) exceeds the triple-point pressure (~611.2 Pa), so
the ice-saturation isotherm sits above 0 C everywhere in the grid;
deposition from vapor (frost without a liquid step) cannot occur at the
ambient side. The downstream frost-vs-liquid call is therefore
unambiguous: **condensate arrives as liquid at the Td isotherm**
(+1.9 to +16.7 C) and freezes only where a surface is below 0 C.

## Sanity checks (asserted in the script, tolerance ~1 C)

| Check | Computed Td | Expected | Deviation | Result |
|-------|-------------|----------|-----------|--------|
| 22 C / 30 % | 3.62 C | ~4 C | -0.38 C | PASS |
| 22 C / 50 % | 11.10 C | ~11 C | +0.10 C | PASS |
| 22 C / 60 % | 13.88 C | ~14 C | -0.12 C | PASS |
| 25 C / 50 % | 13.86 C | ~14 C | -0.14 C | PASS |

All four anchors PASS; no row deviates by more than ~1 C, so no row was
flagged for investigation. The script additionally asserts this per anchor
and prints FAIL - INVESTIGATE if any deviation exceeded 1.0 C.

## Independent cross-check vs committed siblings

This is the third implementation of this grid on the bench lineage; the
two committed siblings agree cell-for-cell at 0.1 C:

- vs `bench/warm-side-dewpoint/` (182d4755): max |ΔTd| = 0.04 C (that
  script prints 2 decimals; the residual is print-rounding only).
- vs `bench/condensation-risk/dewpoint_table.py` (65c9c3df): max
  |ΔTd| = 0.00 C (exact agreement on all 12 rounded values).

The 182d4755 script additionally cross-checked these coefficients against
Bolton (1980) eq. 15 (agreement within 0.015 C) and the ASHRAE
Fundamentals Ch. 1 saturation table (within -0.25 %), so the coefficient
set is externally anchored, not just internally consistent.

## (b) Reproducibility

`python3 bench/warm-side-dewpoint-table/magnus_dewpoint_table.py`
(stdlib `math` only, no dependencies; byte-identical on rerun — verified
by diff this session). Script in full, then its verbatim printed output:

```python
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
```

Verbatim output (`output.txt`):

```
=== Sanity checks (card anchors, tolerance 1.0 C) ===
  22 C / 30 % -> Td =  3.62 C (expected ~4 C, dev -0.38 C)  [PASS]
  22 C / 50 % -> Td = 11.10 C (expected ~11 C, dev +0.10 C)  [PASS]
  22 C / 60 % -> Td = 13.88 C (expected ~14 C, dev -0.12 C)  [PASS]
  25 C / 50 % -> Td = 13.86 C (expected ~14 C, dev -0.14 C)  [PASS]

=== Magnus dew/frost-point table, warm-side ambient grid (ALL 12 CELLS ASSUMED) ===
Td = dew point over water (A=17.625, B=243.04, Alduchov & Eskridge 1996).
Tf = frost point over ice (A=22.46, B=272.62, Sonntag 1990), same functional form;
     reported only where Td < 0 C, else 'n/a'.

| T [C] | RH [%] | Td water [C] | Tf ice [C] |
|-------|--------|--------------|------------|
| 20 | 30 |          1.9 |        n/a |
| 20 | 40 |          6.0 |        n/a |
| 20 | 50 |          9.3 |        n/a |
| 20 | 60 |         12.0 |        n/a |
| 22 | 30 |          3.6 |        n/a |
| 22 | 40 |          7.8 |        n/a |
| 22 | 50 |         11.1 |        n/a |
| 22 | 60 |         13.9 |        n/a |
| 25 | 30 |          6.2 |        n/a |
| 25 | 40 |         10.5 |        n/a |
| 25 | 50 |         13.9 |        n/a |
| 25 | 60 |         16.7 |        n/a |

Sub-zero frost-point cells: 0 of 12.
  Coldest cell (20 C / 30 % RH): Td = 1.89 C (~1.9 C), still ABOVE 0 C.
  -> NO cell in this grid yields a sub-zero frost point.
     Explicit negative statement: in every cell the ambient
     vapor pressure exceeds the triple-point pressure, so the
     ice-saturation isotherm sits above 0 C; vapor deposits
     as LIQUID at the Td isotherm (all Td = +1.9 to +16.7 C),
     and it can freeze only where a surface is below 0 C.

=== Hand-worked example: T = 22 C, RH = 50 % (numeric proof) ===
  ln(RH/100)      = ln(0.50)              = -0.693147
  A*T/(B+T)       = 17.625*22/(243.04+22)       = 1.462987
  s = ln(RH/100) + A*T/(B+T)   = -0.693147 + 1.462987 = 0.769840
  numerator  B*s  = 243.04*(0.769840)  = 187.101801
  denominator A-s = 17.625 - (0.769840)   = 16.855160
  Td = 187.101801 / 16.855160 = 11.10 C  -> table row 22 / 50 -> 11.1 C

Sanity checks: ALL PASS
```

## (c) Hand-worked example row (numeric proof): T = 22 C, RH = 50 %

Substituting into Td = B·(ln(RH/100) + A·T/(B+T)) / (A − ln(RH/100) − A·T/(B+T))
with A = 17.625, B = 243.04, T = 22, RH = 50:

- ln(RH/100) = ln(0.50) = −0.693147
- A·T/(B+T) = 17.625 × 22 / (243.04 + 22) = 387.75 / 265.04 = 1.462987
- s = ln(RH/100) + A·T/(B+T) = −0.693147 + 1.462987 = 0.769840
- numerator = B·s = 243.04 × 0.769840 = 187.101801
- denominator = A − s = 17.625 − 0.769840 = 16.855160
- **Td = 187.101801 / 16.855160 = 11.10 C** → table row 22 / 50 → 11.1 C ✓

## Citations

- Alduchov, O. A. & Eskridge, R. E. (1996). Improved Magnus' form
  approximation of saturation vapor pressure. J. Appl. Meteor., 35,
  601-609. (water constants A = 17.625, B = 243.04)
- Sonntag, D. (1990). Important new values of the physical constants of
  1986, including three new saturation pressure formulas. Z. Meteorol.,
  70, 340-344. (ice constants A = 22.46, B = 272.62, as prescribed by the
  task card)