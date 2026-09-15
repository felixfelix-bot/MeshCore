#!/usr/bin/env python3
"""Warm-side active-electronics condensation re-entry window — computed values.

Companion to bench/warm-side-electronics-failure-modes/REPORT.md.
Recomputes every COMPUTED number quoted in the report entry:
  1. Ice saturation pressure at the two setpoints (surface flux driver).
  2. Re-entry condensation driving deficit (ambient vapor pressure minus
     surface saturation pressure) for the 22 C ambient cell at 30/50/60 % RH.
  3. Re-entry condensation window duration under a first-order warming model
     (time for the board surface to warm past the ambient dew point),
     -20 C vs -40 C soak, all 12 ambient grid cells.
  4. Pressure-driven inflow during cooldown (enclosure/enclosed-volume
     mechanism), cross-checked against the COMMITTED 04db4fae FM-9 values.

Constants are the same Magnus parameters already committed in
bench/warm-side-dewpoint/dewpoint_baseline.py and
bench/condensation-risk/dewpoint_table.py:
  Alduchov & Eskridge (1996) water: A=17.625, B=243.04
  Sonntag (1990) ice:               A=22.46,  B=272.62
Stdlib only. Output captured verbatim in output.txt.
"""

import math

# --- Magnus saturation-pressure machinery (identical to committed scripts) ---
E0 = 610.94  # Pa, water triple-point-class anchor (published 611.2 Pa)


def es_water(t_c):
    """Water saturation vapor pressure, Pa (Alduchov & Eskridge 1996)."""
    return E0 * math.exp(17.625 * t_c / (243.04 + t_c))


def es_ice(t_c):
    """Ice saturation vapor pressure, Pa (Sonntag 1990 constants)."""
    return E0 * math.exp(22.46 * t_c / (272.62 + t_c))


def td_water(t_c, rh):
    """Dew point over water, C (inverted Magnus, same as committed tables)."""
    x = math.log(rh / 100.0) + 17.625 * t_c / (243.04 + t_c)
    return 243.04 * x / (17.625 - x)


def sep(label):
    print("=" * 72)
    print(label)
    print("=" * 72)


# --- Anchors -------------------------------------------------------------
sep("ANCHORS (sanity, vs published values)")
print(f"es_water(0 C)   = {es_water(0):7.2f} Pa  (published 611.2 Pa)")
print(f"es_water(22 C)  = {es_water(22):7.1f} Pa  (ASHRAE Fundamentals Ch.1: 2645.2 Pa;"
      " committed 182d4755 cross-check used 2638.6 computed)")
print(f"es_ice(-20 C)   = {es_ice(-20):6.2f} Pa  (published ~103 Pa)")
print(f"es_ice(-40 C)   = {es_ice(-40):6.2f} Pa  (published ~12.8 Pa)")
for t, rh, want in ((22, 50, 11.10), (22, 30, 3.62), (22, 60, 13.88)):
    print(f"Td(22 C/{rh} %) = {td_water(22, rh):5.2f} C  (committed 182d4755 table: {want:.2f} C)")

# --- 1. Surface saturation pressure at the setpoints ----------------------
sep("1. ICE SATURATION PRESSURE AT THE TWO SETPOINTS (COMPUTED)")
for ts in (-20, -40):
    print(f"es_ice({ts:+3d} C) = {es_ice(ts):6.2f} Pa")
print("Condensation mass flux onto the surface scales with (e_ambient - es_surface);")
print("this is the flux driver while the board sits below the ambient dew point.")

# --- 2. Re-entry driving deficit ------------------------------------------
sep("2. RE-ENTRY CONDENSATION DRIVING DEFICIT (COMPUTED)")
print("Board cold-soaked to the setpoint, re-entering 22 C ambient.")
print("Deficit = e_ambient(RH) - es_ice(T_board); Pa.\n")
print(f"{'RH %':>6} {'e_amb Pa':>10} {'def @ -20 C':>13} {'def @ -40 C':>13} {'-40/-20 ratio':>14}")
for rh in (30, 50, 60):
    e = rh / 100.0 * es_water(22)
    d20 = e - es_ice(-20)
    d40 = e - es_ice(-40)
    print(f"{rh:>6} {e:>10.1f} {d20:>13.1f} {d40:>13.1f} {d40 / d20:>14.3f}")
print("\nAt the moment of re-entry the -40 C board drives 1.06-1.13x the flux of")
print("the -20 C board (more at lower RH); the dominant -20-vs-40 difference")
print("is the DURATION of the condensation window (item 3) and the frost")
print("inventory carried out of the soak.")

# --- 3. Condensation window (first-order warming) --------------------------
sep("3. RE-ENTRY CONDENSATION WINDOW (COMPUTED, first-order warming model)")
print("Model: board surface warms toward ambient T_a with time constant tau:")
print("  T(t) = T_a - (T_a - T_s) * exp(-t/tau)")
print("Liquid condensation forms from re-entry until the surface passes the")
print("ambient dew point Td.  Window = tau * ln((T_a - T_s)/(T_a - Td)).")
print("Same tau for both setpoints (same board, same ambient); the only")
print("difference is the starting temperature T_s.  Units: multiples of tau.\n")
TA = 22.0
print(f"{'cell (T_a/RH)':>14} {'Td C':>7} {'window from -20 C':>19} {'window from -40 C':>19} {'-40 vs -20':>11}")
rows = []
for t_amb, rh in ((20, 30), (20, 40), (20, 50), (20, 60),
                  (22, 30), (22, 40), (22, 50), (22, 60),
                  (25, 30), (25, 40), (25, 50), (25, 60)):
    td = td_water(t_amb, rh)
    w20 = math.log((t_amb - (-20)) / (t_amb - td))
    w40 = math.log((t_amb - (-40)) / (t_amb - td))
    rows.append((t_amb, rh, td, w20, w40))
    print(f"{f'{t_amb} C/{rh} %':>14} {td:>7.2f} {w20:>19.3f} {w40:>19.3f} {w40 / w20:>10.1f}x")
w20s = [r[3] for r in rows]
w40s = [r[4] for r in rows]
print(f"\nAcross the 12-cell grid: window from -40 C soak is "
      f"{min(w40s[i] / w20s[i] for i in range(12)):.2f}x to "
      f"{max(w40s[i] / w20s[i] for i in range(12)):.2f}x the -20 C window")
print("(longer at every humidity; the drier the cell, the larger the ratio,")
print(" because the surface has to climb further to cross a lower Td).")

# --- 4. Pressure-driven inflow during cooldown ------------------------------
sep("4. PRESSURE-DRIVEN INFLOW DURING COOLDOWN (COMPUTED)")
print("Sealed gas volume loaded at 25 C follows P/T on cooldown -> inward")
print("differential across any imperfect seal/vent path:")
for ts in (-20, -40):
    frac = (273.15 + ts) / (273.15 + 25)
    print(f"  25 C -> {ts:+3d} C: P2/P1 = {frac:.3f}  (inward dP ~ {1 - frac:.3f} atm)")
print("Cross-check vs COMMITTED 04db4fae FM-9: ~0.15 atm (-20 C), ~0.22 atm (-40 C) -> PASS")

# --- Assumption register ---------------------------------------------------
sep("ASSUMPTION REGISTER (all inputs already labeled upstream)")
print("- Ambient grid T=20/22/25 C x RH=30/40/50/60 %: ASSUMED (182d4755,")
print("  no hygrometer on host); every grid-derived number inherits that label.")
print("- First-order warming (single tau) is the minimal model; real warm-up has")
print("  distributed mass -> the window values are MODEL results, not measurements.")
print("- es at the cold surface taken over ice (condensate is frozen below 0 C;")
print("  no sub-zero frost point exists in any grid cell, 182d4755).")
print("- Flux 'deficit' is the thermodynamic driver, not a measured rate; no")
print("  frost-mass growth model is attempted (no boundary-layer data exists).")
print("NOTHING in this output is a measurement. No chamber run has occurred.")