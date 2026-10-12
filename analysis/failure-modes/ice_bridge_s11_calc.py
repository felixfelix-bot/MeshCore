#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ice_bridge_s11_calc.py -- Quantitative backbone for the failure-mode catalogue
entry on condensed-water/ice shunt bridging across a (mated or unmated) SMA
coax interface, Z0 = 50 Ohm, band DC-6 GHz.

ANALYSIS ONLY. No mitigation / fix / recommendation content.

Model levels:
  L1  assumed lumped resistive shunt Z across the interface plane (closed form)
  L2  physically-derived bridge admittance from film geometry x material
      complex permittivity / conductivity, evaluated per frequency (Debye)
  L3  distributed-line cross-check of L1/L2 where the bridge's electrical size
      approaches lambda/10 in the bridge medium

Run:  python3 ice_bridge_s11_calc.py
Prints the markdown tables transcribed into
sma-ice-bridge-s11-return-loss.md.
"""
import cmath
import math

# ---------------------------------------------------------------- constants
Z0 = 50.0                       # system impedance (Ohm)
Y0 = 1.0 / Z0                   # 0.02 S
C_LIGHT = 299792458.0
EPS0 = 8.8541878128e-12
MU0 = 4.0e-7 * math.pi

# --- assumed SMA interface geometry --------------------------------------
A_IN = 0.635e-3                 # centre-pin radius (0.050"/2), m
B_IN = 2.10e-3                  # shield inner / PTFE outer radius, m (typical SMA)
LN_BA = math.log(B_IN / A_IN)   # 1.194
GAP_R = B_IN - A_IN             # 1.465 mm radial pin-to-shield span

# --- assumed bridge extent (electrical-size basis) ------------------------
L_BRIDGE = 2.0e-3               # characteristic bridge region extent, m
                                       # (axial mating-plane region ~1-3 mm)

SPOT_FREQS = [("DC", 1e-6), ("868 MHz", 868e6), ("915 MHz", 915e6),
              ("1 GHz", 1e9), ("2.4 GHz", 2.4e9), ("6 GHz", 6e9)]


# ---------------------------------------------------------------- helpers
def gamma_shunt_parallel(z):
    """Gamma looking into plane where shunt z sits across matched Z0 load."""
    zl = (Z0 * z) / (Z0 + z)            # Z0 || z
    return (zl - Z0) / (zl + Z0)


def gamma_shunt_closedform(z):
    """Gamma = -Z0 / (2 z + Z0)   (algebraically identical)."""
    return -Z0 / (2.0 * z + Z0)


def gamma_shunt_admittance(y):
    """Gamma = -y / (2 Y0 + y), y = shunt admittance (S)."""
    return -y / (2.0 * Y0 + y)


def gamma_unmated(z):
    """Unmated port: the bridge alone is the termination."""
    return (z - Z0) / (z + Z0)


def rl_db(g):
    a = abs(g)
    if a < 1e-12:
        return float('inf')
    return -20.0 * math.log10(a)


def vswr(g):
    a = abs(g)
    if a >= 1.0 - 1e-12:
        return float('inf')
    if a < 1e-12:
        return 1.0
    return (1.0 + a) / (1.0 - a)


def mismatch_loss_db(g):
    """-10 log10(1-|G|^2): delivered-power loss vs a perfect match."""
    return -10.0 * math.log10(1.0 - abs(g) ** 2)


def debye(f, eps_s, eps_inf, tau):
    """Complex relative permittivity eps* = eps' - j eps'' (relaxation only).

    Single-pole Debye relaxation. Returns (eps_p, eps_pp_debye) with the
    convention eps* = eps' - j eps''. Ionic conduction is NOT folded in here;
    it is added once as a parallel conductance (or as sigma/(w*eps0) when a
    bulk eps* is needed for propagation constants).
    """
    w = 2.0 * math.pi * f
    e = complex(eps_inf, 0.0) + complex(eps_s - eps_inf, 0.0) / (
        1.0 + 1j * w * tau)
    return e.real, -e.imag


def eps_bulk(f, mat):
    """Bulk complex relative permittivity incl. ionic conduction (for
    propagation constants): eps* = eps' - j(eps''_Debye + sigma/(w eps0))."""
    eps_s, eps_inf, tau, sigma, _ = MATS[mat]
    eps_p, eps_pp = debye(f, eps_s, eps_inf, tau)
    w = 2.0 * math.pi * f
    return complex(eps_p, -(eps_pp + sigma / (w * EPS0)))


# --- material parameter sets (ALL stated assumptions; see doc) -------------
MATS = {
    # name: (eps_s, eps_inf, tau [s], sigma [S/m], comment)
    "ice -20C":    (98.0, 3.1, 6.0e-4, 1.0e-5,
                   "pure ice; Debye relaxation sub-kHz, RF sees eps_inf"),
    "water 0C":   (87.9, 5.7, 17.7e-12, 2.0e-3,
                   "clean melt/condensate"),
    "dirty cond": (87.9, 5.7, 17.7e-12, 1.0e-2,
                   "urban/coastal aerosol condensate"),
    "brine 0C":   (70.0, 5.7, 25.0e-12, 10.0,
                   "road-salt / sea-spray contaminated meltwater"),
    "seawater 0C": (81.0, 5.7, 19.0e-12, 3.0,
                   "seawater at 0C"),
    "supercool -20C": (105.0, 5.7, 90.0e-12, 2.0e-3,
                   "metastable supercooled water at -20C (approx. lit. values)"),
}


def sector_K(theta_rad, l_ax):
    """Coax-sector geometry factor K = theta * l_ax / ln(b/a)  [m].

    G_ion = sigma * K ;  C = eps0 * eps' * K ;  G_diel = w * eps0 * eps'' * K
    (full ring: theta = 2*pi -> standard coax formulas)
    """
    return theta_rad * l_ax / LN_BA


def film_Y(f, mat, theta_rad, l_ax):
    """Bridge admittance (S) of a liquid/ice sector bridging pin-to-shield.

    Y = G_ion + G_diel + jB with
      G_ion  = sigma * K          (ionic conduction, counted ONCE)
      G_diel = w*eps0*eps''_Debye*K   (dipole relaxation loss)
      B      = w*eps0*eps'*K      (displacement)
    K = theta*l_ax/ln(b/a).
    """
    eps_s, eps_inf, tau, sigma, _ = MATS[mat]
    K = sector_K(theta_rad, l_ax)
    if f <= 1.0:                       # DC: displacement and dielectric loss -> 0
        return complex(sigma * K, 0.0), sigma * K, 0.0, 0.0
    eps_p, eps_pp = debye(f, eps_s, eps_inf, tau)
    g_ion = sigma * K
    g_diel = 2.0 * math.pi * f * EPS0 * eps_pp * K
    b = 2.0 * math.pi * f * EPS0 * eps_p * K
    return complex(g_ion + g_diel, b), g_ion, g_diel, b


# ---------------------------------------------------------------- L1: closed form
def section_L1():
    print("## S1. Algebra cross-check (three identical forms)\n")
    print("| R (Ohm) | Gamma via Z0||R | Gamma via -Z0/(2R+Z0) | "
          "Gamma via -Y/(2Y0+Y) |")
    print("|---|---|---|---|")
    for r in (1000.0, 100.0, 20.0, 5.0):
        g1 = gamma_shunt_parallel(complex(r, 0))
        g2 = gamma_shunt_closedform(complex(r, 0))
        g3 = gamma_shunt_admittance(1.0 / r)
        assert abs(g1 - g2) < 1e-12 and abs(g1 - g3) < 1e-12
        print("| %.0f | %+.6f | %+.6f | %+.6f |" % (r, g1.real, g2.real, g3.real))
    print("\nAll three forms agree to machine precision.\n")

    print("## S2. Assumed lumped resistive bridge across mated Z0=50 Ohm "
          "interface\n")
    print("| Bridge Z (Ohm) | \\|Gamma\\| | Return loss (dB) | VSWR | "
          "Delivered-power loss (dB) | P in bridge / P_inc |")
    print("|---|---|---|---|---|---|")
    rows = []
    for r in (1000.0, 500.0, 250.0, 100.0, 50.0, 20.0, 5.0):
        g = gamma_shunt_closedform(complex(r, 0))
        p_bridge = Z0 * abs(1.0 + g) ** 2 / r       # V^2/R with V^2=P*Z0*|1+G|^2
        # conservation: |G|^2 + p_bridge + p_load50 == 1
        p_load50 = Z0 * abs(1.0 + g) ** 2 / Z0
        cons = abs(g) ** 2 + p_bridge + p_load50
        assert abs(cons - 1.0) < 1e-9, (r, cons)
        rows.append((r, g))
        print("| %.0f | %.4f | %.2f | %.2f | %.3f | %.3f |" % (
            r, abs(g), rl_db(g), vswr(g), mismatch_loss_db(g), p_bridge))
    print("\nEnergy conservation verified per row: "
          "|G|^2*P + P_bridge + P_load50 = P_inc.\n")

    print("## S3. Spot-frequency flatness of the resistive rows "
          "(pure-R shunt is frequency-flat)\n")
    print("| R (Ohm) | " + " | ".join(lbl for lbl, _ in SPOT_FREQS) + " |")
    print("|---|" + "---|" * len(SPOT_FREQS))
    for r in (1000.0, 100.0, 20.0, 5.0):
        vals = []
        for lbl, f in SPOT_FREQS:
            g = gamma_shunt_closedform(complex(r, 0))   # no f dependence
            vals.append("%.4f" % abs(g))
        print("| %.0f | %s |" % (r, " | ".join(vals)))
    print("\nIdentical across DC-6 GHz: a purely resistive bridge has no "
          "frequency dependence in the lumped model.\n")

    # worst-case film heating point
    print("Worst-case bridge dissipation vs R: P_bridge/P_inc = 200R/(2R+50)^2")
    print("maximum at R = 25 Ohm -> 0.500 of incident power.\n")

    # unmated port
    print("## S7. Unmated port: bridge alone is the termination\n")
    print("| Bridge Z (Ohm) | Gamma | Return loss (dB) | VSWR |")
    print("|---|---|---|---|")
    for r in (1000.0, 500.0, 100.0, 50.0, 20.0, 5.0):
        g = gamma_unmated(complex(r, 0))
        print("| %.0f | %+.3f | %.2f | %.2f |" % (r, g.real, rl_db(g), vswr(g)))
    print("")


# ---------------------------------------------------------------- L2: films
FILM_STATES = [
    # (label, material, theta_rad, l_ax_m)
    ("pure ice droplet, -20C", "ice -20C", 2.0, 1.0e-3),
    ("clean meltwater droplet 0C (1 mm, 2 rad)", "water 0C", 2.0, 1.0e-3),
    ("dirty condensate droplet 0C (1 mm, 2 rad)", "dirty cond", 2.0, 1.0e-3),
    ("supercooled droplet -20C (1 mm, 2 rad)", "supercool -20C", 2.0, 1.0e-3),
    ("brine droplet 0C (1 mm, 2 rad)", "brine 0C", 2.0, 1.0e-3),
    ("flooded annulus: full ring, 2 mm, brine", "brine 0C", 2.0 * math.pi, 2.0e-3),
]


def section_L2():
    print("## S4. Physically-derived film bridges (complex Y(f))\n")
    print("Geometry factor K = theta*l_ax/ln(b/a); G = sigma*K; "
          "C = eps0*eps'*K; G_diel = w*eps0*eps''*K\n")
    for label, mat, theta, l_ax in FILM_STATES:
        K = sector_K(theta, l_ax)
        eps_s, eps_inf, tau, sigma, comment = MATS[mat]
        g_ion_dc = sigma * K
        print("### %s\n" % label)
        print("  material: %s (%s); K = %.3e m; DC shunt R = %.1f Ohm\n"
              % (mat, comment, K, 1.0 / g_ion_dc if g_ion_dc > 0 else float('inf')))
        print("| f | C (pF) | G_ion (S) | G_diel (S) | B (S) | |Y| (S) | "
              "|Z|_eff (Ohm) | \\|Gamma\\| | RL (dB) | VSWR |")
        print("|---|---|---|---|---|---|---|---|---|---|")
        for lbl, f in SPOT_FREQS:
            Y, g_ion, g_diel, b = film_Y(f, mat, theta, l_ax)
            g = gamma_shunt_admittance(Y)
            if f > 1.0:
                eps_p, _ = debye(f, eps_s, eps_inf, tau)
                c_pf = EPS0 * eps_p * K
            else:
                c_pf = 0.0
            zeff = 1.0 / abs(Y) if abs(Y) > 0 else float('inf')
            print("| %s | %.3f | %.2e | %.2e | %.2e | %.2e | %.1f | %.4f | %.2f | %.2f |" % (
                lbl, c_pf * 1e12, g_ion, g_diel, b, abs(Y), zeff,
                abs(g), rl_db(g), vswr(g)))
        print("")


# ---------------------------------------------------------------- validity
def section_validity():
    print("## S5. Lumped-validity: bridge extent vs wavelength in medium\n")
    print("Bridge extent assumed %s mm; lumped shunt adequate while "
          "extent < lambda/10 in the bridge medium.\n" % (L_BRIDGE * 1e3))
    media = [("water 0C", 87.9, 5.7, 17.7e-12, 2.0e-3),
             ("supercooled -20C", 105.0, 5.7, 90.0e-12, 2.0e-3),
             ("brine 0C", 70.0, 5.7, 25.0e-12, 10.0),
             ("ice -20C", 98.0, 3.1, 6.0e-4, 1.0e-5)]
    print("| medium | eps' @ 1 GHz | eps' @ 2.4 GHz | eps' @ 6 GHz | "
          "lambda/10 @ 868 MHz (mm) | @ 2.4 GHz (mm) | @ 6 GHz (mm) |")
    print("|---|---|---|---|---|---|---|")
    for name, eps_s, eps_inf, tau, sigma in media:
        eps_at = {lbl: debye(f, eps_s, eps_inf, tau)[0] for lbl, f in SPOT_FREQS}
        lam10_at = {}
        for lbl, f in SPOT_FREQS:
            if f <= 1.0:
                continue
            lam10_at[lbl] = C_LIGHT / (f * math.sqrt(eps_at[lbl])) / 10.0 * 1e3
        print("| %s | %.1f | %.1f | %.1f | %.1f | %.1f | %.1f |" % (
            name,
            eps_at["1 GHz"], eps_at["2.4 GHz"], eps_at["6 GHz"],
            lam10_at["868 MHz"], lam10_at["2.4 GHz"], lam10_at["6 GHz"]))
    print("\nReading the table: a 2 mm bridge stays lumped-valid wherever its "
          "lambda/10 entry exceeds 2.0 mm. At 868-915 MHz all listed media "
          "give lambda/10 > 2 mm (water-class 3.7-4.2 mm, ice 19.6 mm), so "
          "the lumped-shunt model is adequate at the sub-GHz band edges. At "
          "2.4 GHz water-class lambda/10 is 1.4-2.0 mm -- AT or BELOW the "
          "assumed 2 mm extent, so the criterion flags the lumped numbers as "
          "upper bounds; at 6 GHz water-class lambda/10 is 0.6-1.4 mm and "
          "the flag is stronger. Ice (eps'=3.1) keeps lambda/10 = 2.8 mm at "
          "6 GHz and stays lumped-valid to ~9 GHz. Table S6 quantifies the "
          "actual error the flag corresponds to: for a droplet shunt on a "
          "through-going 50 Ohm line the distributed treatment differs from "
          "the lumped by only +0.01 to +0.20 dB (868 MHz to 6 GHz); for the "
          "flooded annulus (2 mm of brine-filled line) the error reaches "
          "+0.96 dB at 6 GHz.\n")


# ---------------------------------------------------------------- L3: distributed
def abcd_gamma_in(A, B, Cc, D, zl=Z0):
    zin = (A * zl + B) / (Cc * zl + D)
    return (zin - Z0) / (zin + Z0)


def line_abcd(z0c, gamma_len):
    """ABCD of a transmission-line section of electrical length gamma_len."""
    ch = cmath.cosh(gamma_len)
    sh = cmath.sinh(gamma_len)
    return ch, z0c * sh, sh / z0c, ch


def section_L3():
    print("## S6. Distributed cross-check of the lumped numbers\n")

    # (a) meniscus distributed along 1 mm of the PTFE line, clean water 0C
    print("### (a) clean-water droplet (2 rad x 1 mm) as a distributed "
          "shunt along the line vs lumped\n")
    mat = "water 0C"
    theta, l_ax = 2.0, 1.0e-3
    K = sector_K(theta, l_ax)
    eps_s, eps_inf, tau, sigma, _ = MATS[mat]
    v_p = C_LIGHT / math.sqrt(2.1)              # PTFE-filled 50 Ohm line
    L_pul = Z0 / v_p
    C_pul = 1.0 / (Z0 * v_p)
    print("Base line: PTFE eps_r=2.1, v_p = %.3e m/s, L' = %.1f nH/m, "
          "C' = %.1f pF/m\n" % (v_p, L_pul * 1e9, C_pul * 1e12))
    print("| f | \\|Gamma\\| lumped | \\|Gamma\\| distributed | RL lumped (dB) | "
          "RL distributed (dB) | RL diff (dB) |")
    print("|---|---|---|---|---|---|")
    for lbl, f in SPOT_FREQS:
        if f <= 1.0:
            continue
        Y_tot, _, _, _ = film_Y(f, mat, theta, l_ax)
        g_lump = gamma_shunt_admittance(Y_tot)
        y_a = Y_tot / l_ax                       # per-unit-length added shunt
        w = 2.0 * math.pi * f
        z_pul = 1j * w * L_pul
        y_pul = 1j * w * C_pul + y_a
        z0c = cmath.sqrt(z_pul / y_pul)
        gam = cmath.sqrt(z_pul * y_pul) * l_ax
        A, B, Cc, D = line_abcd(z0c, gam)
        g_dist = abcd_gamma_in(A, B, Cc, D)
        print("| %s | %.4f | %.4f | %.2f | %.2f | %+.2f |" % (
            lbl, abs(g_lump), abs(g_dist), rl_db(g_lump), rl_db(g_dist),
            rl_db(g_dist) - rl_db(g_lump)))
    print("")

    # (b) flooded annulus: 2 mm of line where dielectric is brine
    print("### (b) flooded annulus (2 mm of line filled with brine, "
          "eps* = 70 - j*loss) vs its lumped equivalent\n")
    mat = "brine 0C"
    eps_s, eps_inf, tau, sigma, _ = MATS[mat]
    l_ax = 2.0e-3
    theta = 2.0 * math.pi
    K = sector_K(theta, l_ax)
    print("| f | \\|Gamma\\| lumped | \\|Gamma\\| distributed | RL lumped (dB) | "
          "RL distributed (dB) | RL diff (dB) |")
    print("|---|---|---|---|---|---|")
    for lbl, f in SPOT_FREQS:
        if f <= 1.0:
            continue
        Y_tot, _, _, _ = film_Y(f, mat, theta, l_ax)
        g_lump = gamma_shunt_admittance(Y_tot)
        eps_star = eps_bulk(f, mat)     # relaxation + ionic conduction, once
        z0c = (LN_BA / (2.0 * math.pi)) * cmath.sqrt(MU0 / (EPS0 * eps_star))
        gam = 1j * 2.0 * math.pi * f * cmath.sqrt(MU0 * EPS0 * eps_star) * l_ax
        A, B, Cc, D = line_abcd(z0c, gam)
        g_dist = abcd_gamma_in(A, B, Cc, D)
        print("| %s | %.4f | %.4f | %.2f | %.2f | %+.2f |" % (
            lbl, abs(g_lump), abs(g_dist), rl_db(g_lump), rl_db(g_dist),
            rl_db(g_dist) - rl_db(g_lump)))
    print("")

    # sanity limit: a shrinking section with the SAME total added shunt
    # admittance must reproduce the lumped value (validates the ABCD path)
    Y_tot, _, _, _ = film_Y(6e9, "water 0C", 2.0, 1.0e-3)
    g_lump = abs(gamma_shunt_admittance(Y_tot))
    v_p = C_LIGHT / math.sqrt(2.1)
    L_pul = Z0 / v_p
    C_pul = 1.0 / (Z0 * v_p)
    w = 2.0 * math.pi * 6e9
    z_pul = 1j * w * L_pul
    C_pul0 = C_pul
    g_lim = None
    for l_small in (1.0e-3, 1.0e-4, 1.0e-5, 1.0e-6):
        y_a = Y_tot / l_small                 # same TOTAL added Y, spread thinner
        y_pul = 1j * w * C_pul0 + y_a
        z0c = cmath.sqrt(z_pul / y_pul)
        gam = cmath.sqrt(z_pul * y_pul) * l_small
        A, B, Cc, D = line_abcd(z0c, gam)
        g_lim = abs(abcd_gamma_in(A, B, Cc, D))
        print("  limit sweep: l = %.0e m -> |Gamma| = %.6f (lumped %.6f)"
              % (l_small, g_lim, g_lump))
    print("Limit check converges to the lumped value as section length -> 0.\n")
    # matched no-bridge check
    z0c2 = cmath.sqrt(Z0 + 0j) if False else 50.0 + 0j
    A, B, Cc, D = line_abcd(50.0 + 0j, 1j * 2.0 * math.pi * 6e9 / C_LIGHT
                            * math.sqrt(2.1) * 2.0e-3)
    g_match = abs(abcd_gamma_in(A, B, Cc, D))
    print("No-bridge check (plain 2 mm PTFE 50 Ohm section): |Gamma| = %.2e "
          "(must be ~0)\n" % g_match)


# ------------------------------------------------------- intermittent sweep
def section_intermittent():
    print("## S8. Intermittent sweep: RL as bridge conductance varies\n")
    print("| R (Ohm) | \\|Gamma\\| | RL (dB) | VSWR |")
    print("|---|---|---|---|")
    for r in (1000.0, 700.0, 500.0, 300.0, 200.0, 100.0, 70.0, 50.0,
              30.0, 20.0, 10.0, 7.0, 5.0):
        g = gamma_shunt_closedform(complex(r, 0))
        print("| %.0f | %.4f | %.2f | %.2f |" % (r, abs(g), rl_db(g), vswr(g)))
    g1000 = gamma_shunt_closedform(complex(1000.0, 0))
    g500 = gamma_shunt_closedform(complex(500.0, 0))
    g5 = gamma_shunt_closedform(complex(5.0, 0))
    print("")
    print("Full assumed-range excursion (1 kOhm -> 5 Ohm): %.1f dB to %.2f dB "
          "= %.1f dB of return-loss swing." % (
              rl_db(g1000), rl_db(g5), rl_db(g1000) - rl_db(g5)))
    print("Hundreds-of-ohms-to-few-ohms excursion (500 -> 5 Ohm): %.2f dB "
          "to %.2f dB = %.1f dB swing." % (
              rl_db(g500), rl_db(g5), rl_db(g500) - rl_db(g5)))
    print("Delivered-power swing over the same 500 -> 5 Ohm sweep: %.3f dB "
          "to %.2f dB loss (factor %.2f).\n" % (
              mismatch_loss_db(g500), mismatch_loss_db(g5),
              10 ** ((mismatch_loss_db(g5) - mismatch_loss_db(g500)) / 10.0)))


# ------------------------------------------------------------- DC-blocked
def section_dc():
    print("## S9. DC leakage magnitudes for the same resistive bridges "
          "(12 V bias potential at the plane, I = V/R)\n")
    print("| R (Ohm) | I_leak at 12 V (mA) | P_leak at 12 V (mW) |")
    print("|---|---|---|")
    for r in (1000.0, 500.0, 100.0, 50.0, 20.0, 5.0):
        print("| %.0f | %.1f | %.0f |" % (r, 12.0 / r * 1e3, 144.0 / r * 1e3))
    print("P_leak = V^2/R = 144 mW * (1000 Ohm / R). A 20 Ohm bridge draws "
          "600 mA at 12 V and dissipates 7.2 W in the film itself.\n")


# --------------------------------------------------------------- receive side
def s21_shunt(Y):
    """|S21| of a shunt Y in an otherwise-matched Z0 through path."""
    return 2.0 / abs(2.0 + Y * Z0)


def transducer_loss_db(Y):
    return -20.0 * math.log10(s21_shunt(Y))


def section_rx():
    print("## S10. Receive-side magnitudes\n")
    print("Mismatch loss (reflection only): -10log10(1-|G|^2).\n")
    print("| R (Ohm) | \\|Gamma\\| | mismatch loss (dB) | P_bridge/P_inc |")
    print("|---|---|---|---|")
    for r in (1000.0, 500.0, 250.0, 100.0, 50.0, 25.0, 20.0, 5.0):
        g = gamma_shunt_closedform(complex(r, 0))
        p_bridge = Z0 * abs(1.0 + g) ** 2 / r
        print("| %.0f | %.4f | %.3f | %.3f |" % (
            r, abs(g), mismatch_loss_db(g), p_bridge))
    print("")
    print("Transducer loss (what a 50 Ohm receiver actually receives through "
          "the bridged plane, relative to available power; includes power "
          "burned in the bridge): -20log10|1+G| = -20log10(2R/(2R+50))\n")
    print("| R (Ohm) | \\|S21\\| | transducer loss (dB) |")
    print("|---|---|---|")
    for r in (1000.0, 500.0, 250.0, 100.0, 50.0, 25.0, 20.0, 5.0):
        Y = 1.0 / r
        print("| %.0f | %.4f | %.2f |" % (
            r, s21_shunt(Y), transducer_loss_db(Y)))
    print("")

    print("### S11. Added noise figure of the lossy bridge (passive network "
          "at physical temperature Tb)\n")
    print("Matched-environment available-gain relation for a shunt bridge: "
          "1/G_av = 1/|S21|^2 = ((2R+50)/(2R))^2\n")
    print("NF = 1 + (Tb/T0)(1/G_av - 1), T0 = 290 K. At Tb = T0 the noise "
          "penalty equals the transducer loss (passive network emitting its "
          "own temperature); a cold bridge (-20 C, Tb = 253 K) is slightly "
          "quieter than its loss. Mismatch-reflection subtleties make these "
          "an upper bound on the delivered-noise penalty.\n")
    T0 = 290.0
    print("| R (Ohm) | 1/G_av (lin) | NF @ Tb=290K (dB) | NF @ Tb=253K (dB) |")
    print("|---|---|---|---|")
    for r in (1000.0, 250.0, 100.0, 50.0, 25.0, 20.0, 5.0):
        inv_g = 1.0 / (s21_shunt(1.0 / r) ** 2)
        nf290 = 10.0 * math.log10(1.0 + (inv_g - 1.0) * 290.0 / T0)
        nf253 = 10.0 * math.log10(1.0 + (inv_g - 1.0) * 253.0 / T0)
        print("| %.0f | %.2f | %.2f | %.2f |" % (r, inv_g, nf290, nf253))
    print("")

    print("### S12. Intermittent contact as amplitude modulation: envelope "
          "steps and sidebands\n")
    print("Square-wave switching between bridge states A and B at rate f_sw:")
    print("envelope levels |1+G_A|, |1+G_B|; first sideband relative to "
          "mean carrier = 2(EA-EB)/(pi*(EA+EB))\n")
    print("| state A | state B | envelope ratio (dB) | 1st sideband (dBc) |")
    print("|---|---|---|---|")
    for ra, rb in ((250.0, 5.0), (500.0, 5.0), (500.0, 300.0),
                   (100.0, 20.0), (1000.0, 100.0)):
        ea = abs(1.0 + gamma_shunt_closedform(complex(ra, 0)))
        eb = abs(1.0 + gamma_shunt_closedform(complex(rb, 0)))
        ratio_db = 20.0 * math.log10(ea / eb)
        sb = 2.0 * (ea - eb) / (math.pi * (ea + eb))
        print("| %.0f Ohm | %.0f Ohm | %.2f | %.1f |" % (
            ra, rb, ratio_db, -20.0 * math.log10(sb)))
    print("")

    print("### S13. Film-state receive losses (transducer) at spot "
          "frequencies\n")
    for label, mat, theta, l_ax in FILM_STATES:
        print("  %s:" % label)
        print("| f | \\|S21\\| | transducer loss (dB) |")
        print("|---|---|---|")
        for lbl, f in SPOT_FREQS:
            if f <= 1.0:
                continue
            Y, _, _, _ = film_Y(f, mat, theta, l_ax)
            print("| %s | %.4f | %.2f |" % (
                lbl, s21_shunt(Y), transducer_loss_db(Y)))
        print("")
    print("### S14. Nonlinear intermittent contact: harmonic / mixing products "
          "from a weakly rectifying film\n")
    print("Model: contact I-V i = G1*v + G2*v^2 (+ G3*v^3), bridge across a "
          "50 Ohm environment.\n")
    print("v = Vpk*cos(w t); 2nd-harmonic current amplitude = G2*Vpk^2/2; "
          "fundamental = G1*Vpk.\n")
    print("2f power ratio ~ ((G2/G1)*Vpk/2)^2; two-tone IM2 at |f1-f2| "
          "~ half that (Vpk split across tones).\n")
    print("G2/G1 = alpha is ASSUMED (a film property, not derivable here): "
          "alpha = 1e-3..1e-1 V^-1 spans a nearly-ohmic wet film to a "
          "heavily oxidised/arcing junction.\n")
    print("| alpha (1/V) | Vpk = 1.265 V (+14 dBm, R=100) 2f (dBc) | "
          "Vpk = 4.44 V (+30 dBm, R=20) 2f (dBc) | IM2 at |f1-f2| for "
          "+30 dBm case (dBc) |")
    print("|---|---|---|---|")
    v14 = math.sqrt(25e-3 * Z0) * math.sqrt(2) * abs(
        1.0 + gamma_shunt_closedform(complex(100.0, 0)))     # Vpk at plane
    v30 = math.sqrt(1.0 * Z0) * math.sqrt(2) * abs(
        1.0 + gamma_shunt_closedform(complex(20.0, 0)))
    for alpha in (1e-3, 1e-2, 5e-2, 1e-1):
        h14 = 20.0 * math.log10(alpha * v14 / 2.0)
        h30 = 20.0 * math.log10(alpha * v30 / 2.0)
        im2 = h30 - 6.0            # two tones split the peak envelope
        print("| %.0e | %.1f | %.1f | %.1f |" % (alpha, h14, h30, im2))
    print("")
    print("Envelope for burst noise: the intermittent bridge switches the "
          "receiver's delivered power between states A and B (table S12); "
          "each make/break event steps the received carrier by the envelope "
          "ratio and generates the sideband row above. Contact bounce at "
          "kHz-MHz rates puts this energy INSIDE typical channel bandwidths "
          "(LoRa BW 62.5-812.5 kHz).\n")
    print("| R (Ohm) | P_bridge @ +14 dBm (mW) | melt rate (mg/min) | "
          "P_bridge @ +30 dBm (mW) | melt rate (mg/min) |")
    print("|---|---|---|---|---|")
    LATENT = 334.0e3          # J/kg
    for r in (1000.0, 100.0, 50.0, 25.0, 20.0, 5.0):
        g = gamma_shunt_closedform(complex(r, 0))
        p_bridge = Z0 * abs(1.0 + g) ** 2 / r     # fraction of P_inc
        cells = []
        for p_inc_w in (25e-3, 1.0):              # +14 dBm, +30 dBm
            p_w = p_bridge * p_inc_w
            mg_min = p_w / LATENT * 1e6 * 60.0     # W / (J/kg) = kg/s; -> mg/min
            cells.append("%.2f" % (p_w * 1e3))
            cells.append("%.2f" % mg_min)
        print("| %.0f | %s | %s | %s | %s |" % (r, cells[0], cells[1],
                                                cells[2], cells[3]))
    print("")

    print("E-field across the 1.47 mm radial gap at 1 W and 10 W (V_rms = "
          "sqrt(P*Z0*|1+G|^2)):\n")
    for p in (1.0, 10.0):
        for r in (50.0, 25.0, 20.0):
            g = gamma_shunt_closedform(complex(r, 0))
            v = math.sqrt(p * Z0 * abs(1.0 + g) ** 2)
            e = v / GAP_R
            print("  P = %.0f W, R = %.0f Ohm: V = %.2f V_rms, "
                  "E = %.0f V/m" % (p, r, v, e))
    print("")


def main():
    print("ice_bridge_s11_calc.py -- computed tables (all inputs are stated "
          "assumptions)\n")
    print("Interface: Z0 = %.0f Ohm, a = %.3f mm, b = %.2f mm, ln(b/a) = %.3f, "
          "radial gap = %.2f mm\n" % (
              Z0, A_IN * 1e3, B_IN * 1e3, LN_BA, GAP_R * 1e3))
    section_L1()
    section_L2()
    section_validity()
    section_L3()
    section_intermittent()
    section_dc()
    section_rx()


if __name__ == "__main__":
    main()