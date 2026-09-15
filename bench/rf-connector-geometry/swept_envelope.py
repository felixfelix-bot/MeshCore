#!/usr/bin/env python3
"""RF path geometry inputs for the swept-envelope calculation.

Task (fleet offload, meshcore bench/rf-connector-geometry/): identify RF
connector type, cable OD and min bend radius. GOAL: establish the RF path
geometry inputs for the swept-envelope calculation.

THIS SCRIPT IS ARITHMETIC ONLY. No measurement is performed or simulated.
Every physical input is a PLANNING value labeled UNVERIFIED: no coax cable,
no SMA connector, no feedthrough, no DUT RF connector (the LR2021
measurement path exits via soldered wire dipoles), no calipers and no
camera exist on this host. Census evidence in REPORT.md STEP 0.

Inputs, each labeled with its source:
  OD            = 2.50 mm   RG316 jacket OD -- INDUSTRY NOMINAL, UNVERIFIED
                           (RG316 spec class; BOM report 55585471 section 3b
                           "RG316, OD 2.5mm"; carried in fe700201 section 2b;
                           no vendor datasheet on host, no outbound fetch)
  R_static      = 12.7 mm   RG316 min bend radius, static (installed) --
                           INDUSTRY NOMINAL, UNVERIFIED (fe700201 section 2b;
                           carried in 04db4fae FM-8, t_0d86117f B1). Given as
                           an ABSOLUTE mm value, NOT as an OD multiple.
  R_rule10      = 10 x OD   rule-of-thumb min bend radius -- RULE OF THUMB,
                           UNVERIFIED (commonly quoted coax guidance,
                           fe700201 section 2b). More conservative alternative.
  R_dynamic     = None      RG316 min bend radius, dynamic (repeated flex) --
                           UNKNOWN, not stated in any on-host source.
  AF            = 7.94 mm   SMA hex across flats (5/16 in) -- INDUSTRY
                           STANDARD SMA, UNVERIFIED on host (fe700201 3c;
                           40e1a49a identification kit)
  thread_major  = 6.35 mm   SMA coupling thread major OD, 1/4"-36 UNS --
                           family key, UNVERIFIED (40e1a49a identification kit)
  tpi           = 36        SMA thread pitch, turns per inch -- family key,
                           UNVERIFIED (40e1a49a identification kit)
  panel_hole    = 6.50 mm   SMA bulkhead panel hole, project's own documented
                           pattern -- DOCUMENTED (balloon repo,
                           tracker/hardware/enclosure/README_big.md:21
                           "Two SMA bulkhead holes (6.5mm) ... Screw SMA
                           connectors through from outside")
  R committed cross-check figures (fe700201 section 2d, committed report):
                           swept diameter 27.9 mm and clearance ~14 mm at
                           R=12.7; 52.5 mm and 26.25 mm at R=25.0.

Outputs (all printed, none invented): swept diameter 2R+t and port-face
clearance R+t/2 at both bend-radius candidates; hex across-corners from
the documented across-flats; thread pitch in mm; barrel-to-hole clearance;
OD-multiple audit of the absolute bend-radius figure. Byte-identical rerun
expected (no randomness, no clock, no network).
"""

import math

# ---- labeled inputs (see docstring) ---------------------------------------
OD = 2.50          # mm, INDUSTRY NOMINAL, UNVERIFIED
R_STATIC = 12.7    # mm, INDUSTRY NOMINAL, UNVERIFIED (absolute, not OD x)
R_RULE10_MULT = 10  # x OD, RULE OF THUMB, UNVERIFIED
AF = 7.94          # mm across flats, INDUSTRY-STANDARD SMA, UNVERIFIED on host
THREAD_MAJOR = 6.35  # mm, 1/4"-36 UNS major OD, family key UNVERIFIED
TPI = 36           # threads per inch, family key UNVERIFIED
PANEL_HOLE = 6.50  # mm, DOCUMENTED project pattern (balloon enclosure README)

# committed cross-check figures, fe700201 section 2d
XCHECK = {
    "swept_diam_R_static": 27.9,
    "clearance_R_static": 14.0,   # committed as "13.95 -> ~14"
    "swept_diam_R_rule10": 52.5,
    "clearance_R_rule10": 26.25,
    "across_corners": 9.17,
}

failures = []


def check(name, computed, committed, tol=0.051):
    ok = abs(computed - committed) <= tol
    if not ok:
        failures.append(name)
    return ok


print("=" * 74)
print("RF PATH GEOMETRY INPUTS -- swept-envelope arithmetic (UNVERIFIED inputs)")
print("=" * 74)
print()
print("INPUTS (no measurement performed; every input is a planning value)")
print(f"  cable OD t               = {OD:.2f} mm     INDUSTRY NOMINAL, UNVERIFIED")
print(f"  min bend R, static       = {R_STATIC:.2f} mm     INDUSTRY NOMINAL, UNVERIFIED (absolute)")
print(f"  min bend R, rule-of-thumb = {R_RULE10_MULT}x OD          RULE OF THUMB, UNVERIFIED")
print("  min bend R, dynamic       = UNKNOWN      not on any on-host source")
print(f"  SMA hex across flats     = {AF:.2f} mm     INDUSTRY-STANDARD SMA, UNVERIFIED on host")
print(f"  SMA thread major OD      = {THREAD_MAJOR:.2f} mm     1/4\"-36 UNS family key, UNVERIFIED")
print(f"  SMA thread pitch         = {TPI} TPI -> {25.4 / TPI:.4f} mm/thread (family key, UNVERIFIED)")
print(f"  panel hole (bulkhead)    = {PANEL_HOLE:.2f} mm     DOCUMENTED project pattern (balloon")
print("                                          enclosure README_big.md:21)")
print()

# ---- candidate bend radii ---------------------------------------------------
R_rule10 = R_RULE10_MULT * OD  # 25.0 mm
print("CANDIDATE MIN BEND RADII")
print(f"  R_static  = {R_STATIC:.2f} mm ({R_STATIC / 25.4:.3f} in)")
print(f"  R_rule10  = {R_RULE10_MULT}x {OD:.2f} = {R_rule10:.2f} mm")
print(f"  OD-multiple audit: R_static / OD = {R_STATIC / OD:.2f}x -- the industry")
print(f"    nominal is an ABSOLUTE mm value that COINCIDENTALLY equals ~5x OD;")
print(f"    it was NOT derived as an OD multiple (fe700201 2b).")
print()

# ---- swept envelope at a 90 deg turn at the bulkhead ------------------------
# For a coax entering a bulkhead bore and turning 90 degrees toward the DUT:
#   swept envelope diameter = 2R + t   (circle swept at the interior wall face)
#   clearance from port face = R + t/2  (fe700201 section 2d geometry)
print("SWEPT ENVELOPE AT A 90-DEG TURN AT THE BULKHEAD (2R + t; R + t/2)")
for label, R in (("R_static  (12.7 mm)", R_STATIC), ("R_rule10  (10x OD)", R_rule10)):
    swept = 2 * R + OD
    clearance = R + OD / 2
    print(f"  {label}: swept diameter = 2({R:.2f}) + {OD:.2f} = {swept:.2f} mm;"
          f" port-face clearance = {R:.2f} + {OD / 2:.2f} = {clearance:.2f} mm")
print()

# ---- cross-checks against committed figures (fe700201 section 2d) ----------
print("CROSS-CHECK vs COMMITTED FIGURES (fe700201 section 2d)")
swept_static = 2 * R_STATIC + OD
clear_static = R_STATIC + OD / 2
swept_rule10 = 2 * R_rule10 + OD
clear_rule10 = R_rule10 + OD / 2
pairs = [
    ("swept diameter @ R_static", swept_static, XCHECK["swept_diam_R_static"]),
    ("clearance @ R_static", clear_static, XCHECK["clearance_R_static"]),
    ("swept diameter @ R_rule10", swept_rule10, XCHECK["swept_diam_R_rule10"]),
    ("clearance @ R_rule10", clear_rule10, XCHECK["clearance_R_rule10"]),
]
for name, computed, committed in pairs:
    ok = check(name, computed, committed)
    print(f"  {name:28s} computed {computed:7.2f} vs committed {committed:6.2f}"
          f"  -> {'PASS' if ok else 'FAIL'}")
print()

# ---- connector hex and wrench geometry --------------------------------------
print("SMA CONNECTOR HEX / WRENCH GEOMETRY (industry-standard SMA, UNVERIFIED on host)")
ac = AF / math.cos(math.radians(30))
ok = check("across corners", ac, XCHECK["across_corners"])
print(f"  across flats  = {AF:.2f} mm (5/16 in)  -> wrench: 5/16-in torque wrench")
print(f"                  (0.9 N*m / 8 in-lb breakaway, BOM t_0d86117f B9) or 8 mm")
print(f"                  open-end spanner for the bulkhead jam nut (B10)")
print(f"  across corners = AF / cos(30 deg) = {AF:.2f} / {math.cos(math.radians(30)):.4f}"
      f" = {ac:.2f} mm   -> cross-check vs committed 9.17 mm:"
      f" {'PASS' if ok else 'FAIL'}")
print(f"  mating (coupling) thread = 1/4\"-36 UNS, major OD {THREAD_MAJOR:.2f} mm,")
print(f"                  pitch {25.4 / TPI:.4f} mm/thread; ENGAGEMENT LENGTH"
      " (mating depth) = UNKNOWN --")
print("                  no vendor datasheet on host; no on-record value.")
print()

# ---- bulkhead pass-through geometry -----------------------------------------
print("BULKHEAD PASS-THROUGH GEOMETRY (documented project pattern)")
dclear = PANEL_HOLE - THREAD_MAJOR
print(f"  SMA threaded barrel ({THREAD_MAJOR:.2f} mm major OD) through the")
print(f"  documented {PANEL_HOLE:.2f} mm panel hole: diametral clearance"
      f" = {PANEL_HOLE:.2f} - {THREAD_MAJOR:.2f} = {dclear:.2f} mm"
      f" ({dclear / 2:.3f} mm radial).")
print(f"  The hex nut/jam nut ({AF:.2f} mm AF, {ac:.2f} mm AC) CANNOT pass the")
print(f"  {PANEL_HOLE:.2f} mm hole ({ac:.2f} > {PANEL_HOLE:.2f}) -- the connector")
print("  is mounted nut-one-side; the feedthrough IS the penetration (fe700201).")
print()

# ---- dynamic bend radius -----------------------------------------------------
print("MIN BEND RADIUS, DYNAMIC (repeated flex)")
print("  UNKNOWN -- not stated in any on-host source (no vendor datasheet;")
print("  industry-typical dynamic values for RG316-class assemblies are ~10x OD")
print("  or greater, ENGINEERING KNOWLEDGE, UNVERIFIED).")
print()

print("=" * 74)
if failures:
    print(f"RESULT: {len(failures)} CROSS-CHECK FAILURE(S): {', '.join(failures)}")
    raise SystemExit(1)
print("RESULT: ALL CROSS-CHECKS PASS (byte-identical rerun expected;")
print("stdlib only, no randomness, no clock, no network, nothing measured).")
print("=" * 74)