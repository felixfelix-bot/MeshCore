#!/usr/bin/env python3
"""PTFE cable-dielectric effect arithmetic for the failure-mode catalogue.

Prints every computed quantity cited in
bench/ptfe-dielectric-failure-modes/REPORT.md. Stdlib only.

Input provenance for every constant is documented inline and in
REPORT.md Section 6 (Sources). Constants labeled INDUSTRY-TYPICAL /
UNVERIFIED are bounds or order-of-magnitude estimates, NOT on-record
specs; no vendor datasheet exists on this host and no outbound fetch
is performed (standing operator constraint, reaffirmed in prior bench
reports).
"""
import math

# ---- on-record inputs (provenance in REPORT.md Section 6) ----
C        = 299_792_458.0          # m/s, defined
ER       = 2.1                    # PTFE dielectric constant (65c9c3df 3b)
TC_ER    = 200e-6                 # 1/K, PTFE er tempco (65c9c3df 3b)
CTE_CU   = 17e-6                  # 1/K, copper (04db4fae s5)
CTE_P    = (100e-6, 135e-6)       # 1/K, PTFE, INDUSTRY-TYPICAL UNVERIFIED (04db4fae s5)
ABSW_MAX = 0.01 / 100.0           # 0.01 wt% max moisture absorption, datasheet class (65c9c3df)
RHO_P    = 2.2e3                  # kg/m3, PTFE density, INDUSTRY-TYPICAL
RHO_W    = 1.0e3                  # kg/m3, water
ER_W     = 80.0                   # water er at RF (65c9c3df sources table)
L_FUS    = 333.5e3                # J/kg, latent heat of fusion, standard physics
T_MELT   = 273.15                 # K
RHO_ICE  = 916.7                  # kg/m3, ice (NOT 916.7e3), standard physics
BANDS    = (868e6, 2.4e9)         # campaign sub-GHz band; 2.4G second RF path
L_COLD   = 0.15                   # m, interior RG316 DUT->bulkhead (fe700201)
L_FULL   = 0.65                   # m, both segments 0.15 + 0.5 (fe700201)
SWINGS   = (("20 K  (-20 -> -40 C)", 20.0),
            ("45 K  (+25 -> -20 C)", 45.0),
            ("65 K  (+25 -> -40 C)", 65.0))

# ---- INDUSTRY-TYPICAL / UNVERIFIED inputs (no vendor datasheet on host) ----
D_W      = (1e-13, 1e-11)         # m2/s, water diffusivity in PTFE, wide literature range
PATH_R_D = 0.6e-3                 # m, radial dielectric-only path ((1.71-0.51)/2 mm, RG316 nominal)
PATH_R_J = 1.0e-3                 # m, radial jacket-to-core path ((2.50-0.51)/2 mm)
TAND_P   = (1e-4, 5e-4)           # PTFE loss tangent range
EAB_P    = (2.0, 4.0)             # PTFE elongation at break (200-400 %) -> engineering strain
Y_P      = (10e6, 20e6)           # Pa, PTFE yield strength, order class


def wl(length_m, f_hz):
    """Electrical length in wavelengths for solid-PTFE coax."""
    return length_m * f_hz * math.sqrt(ER) / C


def yrs(sec):
    return sec / (365.25 * 24.0 * 3600.0)


def line():
    print("-" * 72)


print("=" * 72)
print("PTFE cable-dielectric effect arithmetic (all inputs labeled in code)")
print("=" * 72)

# ---------------------------------------------------------------- section 1
line()
print("SECTION 1 - velocity factor and its temperature coefficient")
line()
vf = 1.0 / math.sqrt(ER)
tc_vf = -0.5 * TC_ER
print(f"VF = 1/sqrt(er)            = 1/sqrt({ER}) = {vf:.4f}")
print(f"  [industry-nominal RG316 VF 0.70: INDUSTRY-TYPICAL, UNVERIFIED on host]")
print(f"VF tempco = -0.5 * er_tempco = {-0.5*TC_ER:.3g} /K = {tc_vf*1e6:+.0f} ppm/K")
for name, dT in SWINGS:
    print(f"  VF excursion over {name}: {tc_vf*dT*100:+.3f} %")

# ---------------------------------------------------------------- section 2
line()
print("SECTION 2 - electrical length and phase swing vs temperature")
line()
print(f"electrical-length tempco (er term only)      = {0.5*TC_ER*1e6:+.0f} ppm/K")
print(f"electrical-length tempco (er + conductor CTE) = {(0.5*TC_ER+CTE_CU)*1e6:+.0f} ppm/K")
print()
for f in BANDS:
    print(f"--- f = {f/1e6:g} MHz ---")
    for L in (L_COLD, L_FULL):
        w = wl(L, f)
        print(f"  L = {L:.2f} m -> {w:.4f} wavelengths ({w*360:.1f} deg)")
        for name, dT in SWINGS:
            dphi_er = w * 360 * (0.5 * TC_ER) * dT
            dphi_tot = w * 360 * (0.5 * TC_ER + CTE_CU) * dT
            print(f"    swing {name}: phase {dphi_er:+.3f} deg (er only)"
                  f" / {dphi_tot:+.3f} deg (er+conductor)")
    print()
print("cross-check vs 04db4fae s2.6: 0.50 m @ 868 MHz, 60 K, er-term only:")
w5 = wl(0.50, 868e6)
print(f"  {w5:.3f} wl * 360 * 100 ppm/K * 60 K = {w5*360*(0.5*TC_ER)*60:+.2f} deg"
      f"  (04db4fae quotes 4.5 deg -> consistent)")

# ---------------------------------------------------------------- section 3
line()
print("SECTION 3 - BULK moisture absorption bound (datasheet-class max)")
line()
wt = ABSW_MAX                       # 0.01 wt% as a fraction
phi = wt * RHO_P / RHO_W            # mass fraction -> volume fraction
dER_rel = 3.0 * phi * (ER_W - ER) / (ER_W + 2 * ER)   # dilute-sphere mixing
dVF_rel = -0.5 * dER_rel
print(f"datasheet-class max absorption      = {ABSW_MAX*100:.2f} wt% (65c9c3df)")
print(f"  as volume fraction (rho_ptfe/rho_w = {RHO_P/RHO_W:.1f}): phi = {phi:.3g}"
      f" ({phi*100:.3f} vol%)")
print(f"dilute-sphere mixing, water er {ER_W} in matrix er {ER}:")
print(f"  d_er/er = 3*phi*(er_w-er)/(er_w+2*er) = {dER_rel:.3g} ({dER_rel*100:+.4f} %)")
print(f"  d_VF/VF = -0.5 * d_er/er            = {dVF_rel:.3g} ({dVF_rel*100:+.4f} %)")
for f in BANDS:
    for L in (L_COLD, L_FULL):
        w = wl(L, f)
        print(f"  phase shift at saturation max, {L:.2f} m @ {f/1e6:g} MHz:"
              f" {w*360*abs(dVF_rel):.4f} deg")
print("NOTE: this is the DATASHEET IMMERSION MAX reached instantly; actual")
print("campaign uptake is far below it and diffusion-limited (section 3b).")

line()
print("SECTION 3b - diffusion time constants (bound on reaching that max)")
line()
print(f"water diffusivity in PTFE D = {D_W[0]:.0e} .. {D_W[1]:.0e} m2/s"
      " [INDUSTRY-TYPICAL, wide range, UNVERIFIED]")
paths = (("radial, dielectric-only", PATH_R_D),
         ("radial, jacket-to-core ", PATH_R_J),
         ("axial, 0.15 m segment  ", 0.15),
         ("axial, 0.50 m segment  ", 0.50))
for pname, L in paths:
    t_lo = L * L / D_W[1]           # fastest D
    t_hi = L * L / D_W[0]           # slowest D
    fmt = (lambda s: f"{yrs(s):.1f} yr" if yrs(s) > 1 else
           (f"{s/86400:.1f} d" if s > 86400 else f"{s/3600:.1f} h"))
    print(f"  {pname} (L = {L*1000:.1f} mm): tau = L^2/D = {fmt(t_lo)} .. {fmt(t_hi)}")
print("NOTE: colder is slower (thermally activated); at -20/-40 C the lower")
print("end of the D range applies. Axial ingress through connector end faces")
print("is dead on any campaign timescale; radial ingress requires a")
print("shield/jacket breach (not assumed). Capillary wicking along a wet")
print("termination gap is a separate, faster mechanism (PDM-2, geometry-gated).")

line()
print("SECTION 3c - loss-tangent mixing bound at the saturation max")
line()
ER_INF, TAU_W = 4.5, 9.4e-12        # water high-f permittivity, relaxation time
EPS_S         = 78.3                # water static permittivity, standard physics
for f in BANDS:
    w = 2 * math.pi * f
    e2_w = (EPS_S - ER_INF) * w * TAU_W / (1 + (w * TAU_W) ** 2)  # water eps''
    e2_p = ER * TAND_P[1]           # PTFE eps'' at the HIGH end of its tan-d range
    e2_mix = (1 - phi) * e2_p + phi * e2_w
    print(f"  @ {f/1e6:g} MHz: water eps'' = {e2_w:.2f} (Debye, tau 9.4 ps, "
          f"UNVERIFIED-textbook constants)")
    print(f"    PTFE eps'' = {e2_p:.2e} (er*tan-d high end) -> "
          f"mix = {e2_mix:.2e}")
    lam0 = C / f
    a_d = 27.3 * e2_mix / (math.sqrt(ER) * lam0)   # dB/m for small tan-d
    print(f"    alpha_d(mix) = {a_d:.4f} dB/m -> {a_d*L_FULL:.4f} dB over "
          f"{L_FULL:.2f} m at the UNREACHABLE saturation max")
print("NOTE: dilute volume-weighted mixing, arithmetic bound only; the real")
print("campaign uptake is orders below phi_max (section 3b timescales).")

# ---------------------------------------------------------------- section 4
line()
print("SECTION 4 - CTE differential strain per thermal cycle")
line()
dCTE_lo = CTE_P[0] - CTE_CU
dCTE_hi = CTE_P[1] - CTE_CU
print(f"differential CTE PTFE-minus-copper = {dCTE_lo*1e6:.0f} .. {dCTE_hi*1e6:.0f} ppm/K")
for name, dT in SWINGS:
    s_lo = dCTE_lo * dT
    s_hi = dCTE_hi * dT
    print(f"  strain per {name}: {s_lo:.3e} .. {s_hi:.3e}"
          f"  ({s_lo*100:.3f} .. {s_hi*100:.3f} %)")
print(f"PTFE elongation at break {EAB_P[0]*100:.0f}-{EAB_P[1]*100:.0f} %"
      " [INDUSTRY-TYPICAL] -> strain margin vs worst cycle:")
margin = EAB_P[0] / (dCTE_hi * 65.0)
print(f"  {EAB_P[0]:.1f} / {dCTE_hi*65.0:.5f} = {margin:.0f} x")
print("NOTE: both setpoints are in the phase-II plateau (below the 19-30 C")
print("crystalline-transition region, 57-77 K above Tg -97 C): no ductile-")
print("brittle transition is crossed at either setpoint.")

# ---------------------------------------------------------------- section 5
line()
print("SECTION 5 - freezing pressure available for ice-wedging")
line()
v_w = 1.0 / RHO_W
v_i = 1.0 / RHO_ICE
dv = v_w - v_i
slope = L_FUS / (T_MELT * dv)
print(f"Clapeyron slope dP/dT = L/(T*(v_w - v_i))")
print(f"  = {L_FUS:.0f} / ({T_MELT:.2f} * {dv:.3e}) = {slope/1e6:.2f} MPa/K (magnitude)")
for T in (-20.0, -40.0):
    print(f"  melting-point depression to {T:.0f} C requires ~{abs(slope)*abs(T)/1e6:.0f} MPa")
print("  [ice-I melting curve is capped near ~210 MPa at ~-22 C, the")
print("   ice-I/ice-III/liquid triple point - INDUSTRY-STANDARD phase data,")
print("   UNVERIFIED on host; liquid below that is metastable/supercooled]")
print(f"PTFE yield strength {Y_P[0]/1e6:.0f}-{Y_P[1]/1e6:.0f} MPa [INDUSTRY-TYPICAL]:")
print(f"  available freezing pressure exceeds PTFE yield by >= "
      f"{210e6/Y_P[1]:.0f} x at BOTH setpoints -> damage is limited only by")
print("  how much liquid is confined and how compliant the pocket is")

# ---------------------------------------------------------------- section 6
line()
print("SECTION 6 - dielectric-loss insertion-loss bound")
line()
print("alpha_d [dB/m] = 27.3 * sqrt(er) * tan(delta) / lambda0  "
      "[standard transmission-line relation]")
for f in BANDS:
    lam0 = C / f
    for L in (L_FULL,):
        a_lo = 27.3 * math.sqrt(ER) * TAND_P[0] / lam0
        a_hi = 27.3 * math.sqrt(ER) * TAND_P[1] / lam0
        print(f"  @ {f/1e6:g} MHz (lambda0 = {lam0*1000:.1f} mm), tan(delta) "
              f"{TAND_P[0]:.0e}..{TAND_P[1]:.0e} [INDUSTRY-TYPICAL, UNVERIFIED]:")
        print(f"    alpha_d = {a_lo:.4f} .. {a_hi:.4f} dB/m"
              f" -> {a_lo*L:.4f} .. {a_hi*L:.4f} dB over {L:.2f} m")
print("vs conductor loss on record ~0.3 dB/m class (55585471 step 5):")
print(f"  conductor term ~0.2 dB over 0.65 m; the PTFE dielectric-loss term is")
print(f"  a minor fraction, and its temperature dependence is NOT on record.")

# ---------------------------------------------------------------- summary
line()
print("SECTION 7 - one-line consequences (quoted in REPORT.md)")
line()
print(f"VF {vf:.3f} (derived); VF tempco {tc_vf*1e6:+.0f} ppm/K")
print(f"bulk-absorption bound: dVF {dVF_rel*100:+.4f} %, phase "
      f"{wl(L_COLD,868e6)*360*abs(dVF_rel):.2f} deg (cold seg) .. "
      f"{wl(L_FULL,868e6)*360*abs(dVF_rel):.2f} deg (full path) @ 868 MHz")
print(f"ice-wedging: Clapeyron {abs(slope)/1e6:.1f} MPa/K, cap ~210 MPa, "
      f"vs PTFE yield {Y_P[0]/1e6:.0f}-{Y_P[1]/1e6:.0f} MPa")
line()
print("Nothing here is a measurement: all values are arithmetic from labeled")
print("inputs. No cable exists on hand (MUST-PROCURE per 55585471 3b); no")
print("outbound fetch was performed (standing operator constraint).")