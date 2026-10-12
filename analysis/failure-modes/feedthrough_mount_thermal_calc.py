#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FM-FT-MOUNT-01 companion calculator.

Differential contraction / thread-preload arithmetic for the feedthrough
mechanical mount in a cold soak (-20 C, -40 C).

ANALYSIS ONLY. Deterministic, no network, no random, Python stdlib only.

Every constant below is either
  [S<n>]  = read from a named source (see the reference list in the entry), or
  [A]     = a stated modelling assumption of this calculator (not cited).

Run:  python3 analysis/failure-modes/feedthrough_mount_thermal_calc.py
"""

import math

# ---------------------------------------------------------------- sources ---

# [S3] Engineering ToolBox, "Coefficients of Linear Thermal Expansion".
#      Table unit as printed: "10^-6 m/m oC = 1 um/m oC"  (== ppm/K)
CTE = {                       # ppm/K = um/(m*K)
    "ss_304":        17.3,    # [S3] "Steel Stainless Austenitic (304)"
    "ss_316":        16.0,    # [S3] "Steel Stainless Austenitic (316)"
    "ss_310":        14.4,    # [S3] "Steel Stainless Austenitic (310)"
    "ss_410":         9.9,    # [S3] "Steel Stainless Ferritic (410)"
    "brass_lo":      18.0,    # [S3] "Brass  18 - 19"
    "brass_hi":      19.0,    # [S3] "Brass  18 - 19"
    "al_pure":       23.0,    # [S3] "Aluminum  23"
    "al_alloy_lo":   21.0,    # [S3] "Aluminum alloys  21 - 24"
    "al_alloy_hi":   24.0,    # [S3] "Aluminum alloys  21 - 24"
    "ptfe_lo":      112.0,    # [S3] "Polytetrafluorethylene (PTFE)  112 - 135"
    "ptfe_hi":      135.0,    # [S3] "Polytetrafluorethylene (PTFE)  112 - 135"
    "alumina":        8.1,    # [S3] "Alumina (aluminium oxide, Al2O3)  8.1"
    "copper_lo":     16.0,    # [S3] "Copper  16 - 16.7"
    "copper_hi":     16.7,
}

# [S2] Centric RF, "Bulkhead Jamb Nut Torque Recommendations".
IN_LB = 0.112984829            # N*m per in-lb
TORQUE = {                     # (lo, hi) in N*m
    "SMA stainless body": (12 * IN_LB, 15 * IN_LB),   # [S2] "SMA | Stainless steel | 12 - 15 in-lbs"
    "SMA brass body":     (8 * IN_LB, 10 * IN_LB),    # [S2] "SMA | Brass | 0.312 Hex | 8 - 10 in-lbs"
}

# [S4] Angst+Pfister, "O-Rings Technical Guide".
SQEEZE_NOMINAL_MM = 0.30       # [S4] cord d2 = 1.50 mm at 20 % compression ->
                               #      groove depth D = 1.20 mm  => 0.30 mm squeeze
CORD_D2_MM = 1.50              # [S4] table column "1.50"

# [S5] CeramTec Ceramaseal hermetic feedthrough catalogue.
PSIG = 6894.757293168          # Pa per psi
P_HERMETIC_RATED_PA = 2500 * PSIG     # [S5] "Pressure @ 20 C 2500 PSIG (172 Bar)"
P_HERMETIC_ONEPIN_PA = 3500 * PSIG    # [S5] "Single pin: 3500 PSIG (241 Bar)"

# [S1] RF-LAMBDA feedthrough bulkhead adapter datasheet.
RATED_ALT_FT = 45000           # [S1] "2.3 Altitude  45000 ft"
RATED_TEMP_LO = -55.0          # [S1] "2.1 Opt. Temp. -55 C ~ +165 C"

# [A] modelling assumptions of this calculator -------------------------------
T_REF_C = 20.0                 # assembly / reference temperature
E_PA = {                       # Young's modulus, assumed
    "ss":    193e9,
    "brass": 100e9,
    "al":     69e9,
    "ptfe":   0.5e9,
}
A_BODY_M2 = 20.0e-6            # assumed load-bearing thread cross-section (1/4-36 body)
A_PANEL_M2 = 45.0e-6           # assumed annular bearing area under a 0.375" hex jam nut
K_TORQUE = 0.20                # assumed nut factor K in T = K*d*F
D_THREAD_M = 6.35e-3           # assumed thread nominal diameter (1/4" = 6.35 mm)
BORE_AREA_M2 = math.pi / 4 * D_THREAD_M ** 2   # assumed pressure-loaded bore area
HAB_OUTSIDE_PA = 15_800.0      # [A] standard-atmosphere pressure at the rated altitude (derived, not cited)
SEA_LEVEL_PA = 101_325.0       # [A] standard sea-level pressure


def header(t):
    print("\n" + t)
    print("-" * len(t))


def preload(torque_lo, torque_hi):
    """T = K * d * F  ->  F = T / (K * d)."""
    return (torque_lo / (K_TORQUE * D_THREAD_M),
            torque_hi / (K_TORQUE * D_THREAD_M))


def joint_stiffness(beta_body, beta_panel):
    """1/k = 1/(A_b E_b) + 1/(A_p E_p)   [1/N];  k in N per unit axial strain."""
    inv = 1.0 / (A_BODY_M2 * beta_body) + 1.0 / (A_PANEL_M2 * beta_panel)
    return 1.0 / inv, inv


def dF_thermal(alpha_body, alpha_panel, dT_K, beta_body, beta_panel):
    """Preload LOSS = |(alpha_panel - alpha_body) * dT| / (1/(A_b E_b) + 1/(A_p E_p))  [N].

    dT_K is negative for a cold soak; the loss is returned as a positive number.
    """
    _, inv = joint_stiffness(beta_body, beta_panel)
    return abs((alpha_panel - alpha_body) * 1e-6 * dT_K / inv)


def main():
    print("FM-FT-MOUNT-01  feedthrough mechanical mount, cold-loosening arithmetic")
    print("reference temperature  : %+.0f C" % T_REF_C)
    print("torque coefficient K   : %.2f        [A]" % K_TORQUE)
    print("thread dia             : %.2f mm     [A]" % (D_THREAD_M * 1e3))
    print("body load area A_b     : %.1f mm^2   [A]" % (A_BODY_M2 * 1e6))
    print("panel bearing area A_p : %.1f mm^2   [A]" % (A_PANEL_M2 * 1e6))

    header("S3  CTE constants as read from the source table  [S3]")
    print("%-14s %8s  %s" % ("key", "ppm/K", "source row (as printed)"))
    for key, val, src_row in (
        ("ss_304",     "17.3",  "Steel Stainless Austenitic (304)"),
        ("ss_316",     "16.0",  "Steel Stainless Austenitic (316)"),
        ("ss_310",     "14.4",  "Steel Stainless Austenitic (310)"),
        ("ss_410",     "9.9",   "Steel Stainless Ferritic (410)"),
        ("brass_lo",   "18.0",  "Brass  18 - 19"),
        ("brass_hi",   "19.0",  "Brass  18 - 19"),
        ("al_pure",    "23.0",  "Aluminum  23"),
        ("al_alloy_lo", "21.0", "Aluminum alloys  21 - 24"),
        ("al_alloy_hi", "24.0", "Aluminum alloys  21 - 24"),
        ("ptfe_lo",    "112.0", "Polytetrafluorethylene (PTFE)  112 - 135"),
        ("ptfe_hi",    "135.0", "Polytetrafluorethylene (PTFE)  112 - 135"),
        ("alumina",    "8.1",   "Alumina (aluminium oxide, Al2O3)  8.1"),
        ("copper_lo",  "16.0",  "Copper  16 - 16.7"),
        ("copper_hi",  "16.7",  "Copper  16 - 16.7"),
    ):
        print("%-14s %8s  %s" % (key, val, src_row))

    header("S2  jam-nut torque -> thread preload  (T = K d F)")
    print("%-20s %14s %14s" % ("body", "torque N*m", "preload N"))
    pre = {}
    for name, (t_lo, t_hi) in TORQUE.items():
        f_lo, f_hi = preload(t_lo, t_hi)
        pre[name] = (f_lo, f_hi)
        print("%-20s %6.2f - %6.2f %6.0f - %6.0f" % (name, t_lo, t_hi, f_lo, f_hi))

    header("S3  differential CTE of the pairing  (alpha_panel - alpha_body, ppm/K)")
    pairings = [
        ("SS body in Al-alloy panel (worst)",   CTE["ss_304"],    CTE["al_alloy_hi"]),
        ("SS body in Al-alloy panel (typical)", CTE["ss_304"],    23.0),
        ("SS body in Al-alloy panel (best)",    CTE["ss_304"],    CTE["al_alloy_lo"]),
        ("Brass body in Al-alloy panel",        CTE["brass_hi"],  23.0),
        ("SS body in SS panel (control)",       CTE["ss_304"],    CTE["ss_304"]),
        ("Brass body in SS panel (control)",    CTE["brass_hi"],  CTE["ss_304"]),
    ]
    print("%-38s %7s %7s %10s" % ("pairing", "a_body", "a_panel", "d_alpha"))
    for label, a_b, a_p in pairings:
        print("%-38s %7.1f %7.1f %+10.1f" % (label, a_b, a_p, a_p - a_b))

    header("differential strain (alpha_panel - alpha_body) * dT, in ppm")
    for d_alpha in (5.7, 6.7, 3.7, 4.0):
        print("d_alpha %4.1f ppm/K -> %5.0f ppm at -20 C (40 K), %5.0f ppm at -40 C (60 K)"
              % (d_alpha, d_alpha * 40, d_alpha * 60))

    header("free differential contraction over a clamped metal stack (um)")
    print("stack thickness 2.0 mm  [A]")
    print("%8s %14s %14s" % ("dT (K)", "-20 C case", "-40 C case"))
    for d_alpha in (5.7, 6.7, 3.7, 4.5):
        per_k = d_alpha * 1e-6 * 2.0e-3
        print("%8s %14.3f %14.3f   (d_alpha = %.1f ppm/K)"
              % ("40 / 60", per_k * 40 * 1e6, per_k * 60 * 1e6, d_alpha))

    header("S4  squeeze budget: contraction vs nominal O-ring squeeze")
    print("nominal squeeze          : %.2f mm = %.0f um  [S4, d2=%.2f mm at 20%%]"
          % (SQEEZE_NOMINAL_MM, SQEEZE_NOMINAL_MM * 1e3, CORD_D2_MM))
    for name, dT in (("-20 C", 40), ("-40 C", 60)):
        d = 5.7e-6 * dT * 2.0e-3 * 1e6
        print("%-8s axial contraction  : %6.3f um  = %6.3f %% of nominal squeeze" % (name, d, d / (SQEEZE_NOMINAL_MM * 1e3) * 100))
    r = D_THREAD_M / 2
    for name, dT in (("-20 C", 40), ("-40 C", 60)):
        d = 5.7e-6 * dT * r * 1e6
        print("%-8s radial (bore - OD) : %6.3f um  (bore closes on body: squeeze INCREASES)" % (name, d))

    header("preload LOSS and residual margin  (fully metal load path)")
    print("%-26s %5s %7s %7s %7s %9s %9s" % ("pairing", "dT K", "dF N", "MPa", "F0 N", "loss %F0", "residual N"))
    rows = (
        ("SS body in Al panel",     CTE["ss_304"],   23.0,             "ss",    "al", "SMA stainless body"),
        ("SS body in Al panel(hi)", CTE["ss_304"],   CTE["al_alloy_hi"], "ss", "al", "SMA stainless body"),
        ("SS body in Al panel(lo)", CTE["ss_304"],   CTE["al_alloy_lo"], "ss", "al", "SMA stainless body"),
        ("Brass body in Al panel",  CTE["brass_hi"], 23.0,             "brass", "al", "SMA brass body"),
        ("SS body in SS panel",     CTE["ss_304"],   CTE["ss_304"],    "ss",    "al", "SMA stainless body"),
    )
    for label, a_b, a_p, e_b, e_p, tname in rows:
        f_lo, f_hi = pre[tname]
        for dT, tag in ((40, "-20"), (60, "-40")):
            loss = dF_thermal(a_b, a_p, -dT, E_PA[e_b], E_PA[e_p])
            print("%-26s %5s %7.0f %7.1f %7.0f %8.0f%% %10.0f"
                  % (label, tag, loss, loss / A_BODY_M2 / 1e6, f_lo,
                     loss / f_lo * 100, f_lo - loss))
        print("%-26s %5s %7s %7s %7.0f %8.0f%% %10.0f"
              % ("", "", "", "", f_hi, dF_thermal(a_b, a_p, -60, E_PA[e_b], E_PA[e_p]) / f_hi * 100,
                 f_hi - dF_thermal(a_b, a_p, -60, E_PA[e_b], E_PA[e_p])))
    print("'MPa' = preload-loss stress on A_b;  'loss %F0' and 'residual' are")
    print("computed against F0 from the 12-15 in-lb jam-nut torque (F0_lo above).")

    header("PTFE in the axial load path (contrast case)")
    d_alpha = CTE["ptfe_hi"] - CTE["ss_304"]
    for name, dT in (("-20 C", 40), ("-40 C", 60)):
        print("%-8s d_alpha %6.1f ppm/K -> free contraction over 2.0 mm: %7.3f um"
              % (name, d_alpha, d_alpha * 1e-6 * dT * 2.0e-3 * 1e6))

    header("transient body-vs-panel offset (fast ramp)")
    _, inv = joint_stiffness(E_PA["ss"], E_PA["al"])
    for d_alpha in (5.7, 6.7):
        per_k = d_alpha * 1e-6 / inv
        print("d_alpha %4.1f ppm/K -> loss %5.1f N per K of body-panel offset (5 K -> %5.1f N)"
              % (d_alpha, per_k, per_k * 5))

    header("pressure load on the bore (separating force)")
    print("bore area                : %.2f mm^2  [A]" % (BORE_AREA_M2 * 1e6))
    for label, dp, src in (
        ("sealed 1 atm vs 45000 ft", SEA_LEVEL_PA - HAB_OUTSIDE_PA, "S1 altitude rating"),
        ("hermetic class 2500 psig", P_HERMETIC_RATED_PA, "S5"),
        ("hermetic class 3500 psig", P_HERMETIC_ONEPIN_PA, "S5"),
    ):
        print("%-26s dP %9.0f Pa (%6.1f psi) -> F %8.1f N   [%s]"
              % (label, dp, dp / PSIG, dp * BORE_AREA_M2, src))
    print("nominal UHV/vacuum-side note: UHV parts are rated for vacuum, not for")
    print("positive internal pressure      [S6 Lesker: 'Vakuum-Anwendung UHV']")

    header("temperature ratings of the parts in the path")
    print("feedthrough adapter      : %+.0f C .. +165 C operation, -60 C .. +185 C storage  [S1]"
          % RATED_TEMP_LO)
    print("feedthrough (UHV, CF)    : cable connectors -65 C .. +165 C                      [S6]")
    print("silicone O-ring (VMQ 70) : -55 C .. +230 C, 70 IRHD                              [S7]")
    print("seal force data quoted   : +20 C only  [S4 'guideline values at +20 C']")
    print(" => at -40 C every part is inside its rated range; the loss mechanism is")
    print("    mechanical (contraction/preload), not a rating breach of the materials")

    pass


if __name__ == "__main__":
    main()
