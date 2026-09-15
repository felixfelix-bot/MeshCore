#!/usr/bin/env python3
"""Recomputes every number quoted in bench/solder-centerpin-thermal-fatigue/REPORT.md.

Stdlib only, print only. Provenance of every input constant is labeled here
and in REPORT.md Section 4. UNVERIFIED labels follow the fleet convention:
INDUSTRY-TYPICAL values have no datasheet on this host (no outbound fetch
per standing operator constraint); they are standard material data, not
vendor claims. Committed-report values are cited by commit SHA.
"""
import math

# ---------------- input constants (provenance-labeled) ----------------
# CTE in ppm/K
CTE_BRASS = 19.0        # 65c9c3df sources table (HIGH, committed report)
CTE_STAINLESS = 17.0    # 65c9c3df sources table (HIGH)
CTE_COPPER = 17.0       # 04db4fae Sec 2.10/5 [INDUSTRY-TYPICAL, UNVERIFIED]
CTE_SAC_LO, CTE_SAC_HI = 21.0, 25.0   # 04db4fae Sec 2.10 [INDUSTRY-TYPICAL, UNVERIFIED]
CTE_FR4_IP_LO, CTE_FR4_IP_HI = 13.0, 17.0  # 04db4fae [INDUSTRY-TYPICAL, UNVERIFIED]
CTE_PTFE_LO, CTE_PTFE_HI = 100.0, 135.0    # 04db4fae Sec 2.10 [INDUSTRY-TYPICAL, UNVERIFIED]

# Elastic moduli, Pa [INDUSTRY-TYPICAL, UNVERIFIED on host]
E_BRASS = 100e9
E_STAINLESS = 193e9
E_PTFE = 0.5e9
E_SAC = 45e9           # SAC305 class
NU_SAC = 0.36

# SAC305 class strength/temperature data [INDUSTRY-TYPICAL, UNVERIFIED]
SIGMA_Y_SAC_RT = 28e6          # tensile yield ~25-30 MPa at room temperature
TM_SAC = 490.0                 # melting point ~217 C = 490 K

# Campaign thermal cycle definition (committed reports)
T_LAB = 25.0
T_MINUS20 = -20.0
T_MINUS40 = -40.0
DT_20 = T_LAB - T_MINUS20      # 45 K
DT_40 = T_LAB - T_MINUS40      # 65 K
CYCLES_PER_RUN_DAY = (3, 4)   # 72f3aab9 card spec via 04db4fae Sec 0
CM_LIFE_CLASS = 1000.0         # "thousands of cycles" conservative floor, 04db4fae Sec 2.10

# Geometry [INDUSTRY-TYPICAL class scales, UNVERIFIED as-built — no board attached]
BEAD_LEN_MM = 5.0              # SMA-class dielectric bead axial length
BORE_R_MM = 1.0                # SMA-class dielectric bore radius
MENISCUS_H_MM = 0.1            # solder meniscus / joint standoff height
EFFECTIVE_L_MM = (0.5, 1.0)    # effective distance from strain-neutral point to joint


def sec(title):
    print("\n== " + title + " ==")


sec("1. CTE mismatch ratio: pin alloy vs PTFE (order-of-magnitude deliverable)")
for name, cte_pin in (("brass", CTE_BRASS), ("stainless", CTE_STAINLESS), ("copper", CTE_COPPER)):
    lo = CTE_PTFE_LO / cte_pin
    hi = CTE_PTFE_HI / cte_pin
    mid = (CTE_PTFE_LO + CTE_PTFE_HI) / 2 / cte_pin
    da_lo = CTE_PTFE_LO - cte_pin
    da_hi = CTE_PTFE_HI - cte_pin
    print(f"  PTFE/pin({name}): {lo:.1f}x..{hi:.1f}x (midpoint {mid:.1f}x); "
          f"dCTE {da_lo:.0f}..{da_hi:.0f} ppm/K")
print(f"  brass-vs-stainless pin spread: {CTE_BRASS - CTE_STAINLESS:.0f} ppm/K "
      f"(material choice of pin alloy is a second-order term)")

sec("2. Differential free strain per swing, pin-vs-PTFE")
DA_PIN_PTFE = (CTE_PTFE_LO + CTE_PTFE_HI) / 2 - CTE_BRASS   # ~98 ppm/K (brass pin)
for label, dT in (("-20 C cycle", DT_20), ("-40 C cycle", DT_40)):
    eps = DA_PIN_PTFE * 1e-6 * dT
    slip = eps * BEAD_LEN_MM * 1e3   # um over bead length
    gap = eps * BORE_R_MM * 1e3      # um at bore radius
    print(f"  {label} (dT={dT:.0f} K): free strain {eps*100:.2f}% "
          f"({eps*1e6:.0f} ue); axial slip over {BEAD_LEN_MM:.0f} mm bead {slip:.1f} um; "
          f"diametral gap change at {BORE_R_MM:.0f} mm bore radius {gap:.1f} um")

sec("3. What the mismatch implies for shear/stress: compliant-member bound")
print("  If the differential strain were FULLY CLAMPED into each member (sigma=E*da*dT):")
for name, E, da in (("brass pin", E_BRASS, DA_PIN_PTFE),
                    ("stainless pin", E_STAINLESS, DA_PIN_PTFE),
                    ("PTFE", E_PTFE, DA_PIN_PTFE)):
    s = E * da * 1e-6 * DT_40
    print(f"    fully-clamped sigma({name}) over 65 K = {s/1e6:.0f} MPa")
print("  brass yield is ~350-500 MPa class [INDUSTRY-TYPICAL]: a clamped pin would")
print("  yield -> the stack CANNOT stay clamped; it must relieve. The reliever is the")
print(f"  softest member: PTFE, modulus {E_BRASS/E_PTFE:.0f}x lower than brass.")
s_ptfe = E_PTFE * DA_PIN_PTFE * 1e-6 * DT_40
print(f"  Delivered stress bound at the pin/PTFE interface: ~{s_ptfe/1e6:.1f} MPa")
print(f"  (PTFE shear/flow strength ~7-25 MPa class [INDUSTRY-TYPICAL]: the interface")
print("   slides/creeps at low stress instead of storing load -> the ~6x CTE mismatch")
print("   appears as um-scale micro-slip, NOT as stress delivered into the pin or its")
print("   solder joint. Modulus ratio brass/PTFE = %.0fx, stainless/PTFE = %.0fx."
      % (E_BRASS / E_PTFE, E_STAINLESS / E_PTFE))

sec("4. Solder-joint delivered shear vs SAC elastic limit (the fatigue threshold)")
G_SAC = E_SAC / (2 * (1 + NU_SAC))
tau_y = SIGMA_Y_SAC_RT / math.sqrt(3)
gamma_y = tau_y / G_SAC
print(f"  SAC: E={E_SAC/1e9:.0f} GPa, G={G_SAC/1e9:.1f} GPa, "
      f"RT yield ~{SIGMA_Y_SAC_RT/1e6:.0f} MPa -> elastic shear limit gamma_y ~{gamma_y*100:.2f}%")
for dalpha, tag in ((abs(CTE_COPPER - CTE_FR4_IP_LO), "Cu-vs-FR4 worst (dCTE=4)"),
                    (abs(CTE_COPPER - CTE_FR4_IP_HI), "Cu-vs-FR4 best (dCTE=0)"),
                    (abs(CTE_BRASS - CTE_COPPER), "brass-pin-vs-Cu (dCTE=2)"),
                    (abs(CTE_SAC_LO - CTE_COPPER), "SAC-vs-Cu (dCTE=4)")):
    for L in EFFECTIVE_L_MM:
        dg = dalpha * 1e-6 * DT_40 * (L / MENISCUS_H_MM)
        dg20 = dalpha * 1e-6 * DT_20 * (L / MENISCUS_H_MM)
        flag = "ABOVE" if dg > gamma_y else ("at/below" if dg > 0.5 * gamma_y else "below")
        print(f"  {tag}, L={L:.1f} mm, h={MENISCUS_H_MM:.2f} mm: "
              f"d_gamma(65K)={dg*100:.3f}%  d_gamma(45K)={dg20*100:.3f}%  -> {flag} elastic limit")
print("  Cu-wire-on-Cu-pad (wire dipole): dCTE~0 -> d_gamma ~ 0 (no cyclic strain source)")

sec("5. Where in the cycle damage can accumulate: SAC homologous temperature")
for tC in (25.0, 0.0, -20.0, -40.0):
    Th = (tC + 273.15) / TM_SAC
    print(f"  T={tC:+.0f} C: T/Tm(SAC)={Th:.3f}"
          + ("  creep active (relaxation on 10-min holds)" if Th >= 0.5 else
             "  creep strongly suppressed (cold half-cycle ~elastic)"))

sec("6. Coffin-Manson scaling and campaign utilization")
print(f"  dT^2 relative damage per cycle: -40 vs -20 = (65/45)^2 = {(65/45)**2:.2f}x"
      "  [04db4fae Sec 2.10 conservative bound]")
print(f"  strain-range scaling (elastic regime, damage at warm end): 65/45 = {65/45:.2f}x")
for n in CYCLES_PER_RUN_DAY:
    print(f"  utilization at {n} cycles/run-day vs {CM_LIFE_CLASS:.0f}-cycle class life: "
          f"{n/CM_LIFE_CLASS*100:.1f}% per run-day")

sec("7. Ramp-rate context (no thermal-shock term)")
print("  on-record rates: heating 3.0, cooling 1.5, feedthrough-derated cooling 1.05 C/min"
      " (472922d4, planning estimates LOW confidence)")
print(f"  deepest single ramp 20 K at 1.05 C/min = {20/1.05:.1f} min (matches 472922d4)")
print(f"  full-session swing seen by the joints per run-day: {DT_40:.0f} K (25 -> -40 -> 25)")