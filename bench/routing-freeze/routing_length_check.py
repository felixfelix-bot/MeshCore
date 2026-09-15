#!/usr/bin/env python3
"""Routing-freeze geometry self-check for card t_e5d5eaae.

Every input is labeled with its provenance class:
  [RECORD]      a number already committed on this repo's record (prior
                bench report or fleet card) -- reused verbatim.
  [SPEC]        a number this freeze *sets* (required spec), not measured.
  [INDUSTRY-NOMINAL-UNVERIFIED] carried from fe700201 2b; no vendor
                datasheet exists on host, no outbound fetch performed.

Nothing here is a measurement. No cable, chamber, caliper, or tape
measure exists on this host (fresh census 2026-09-15; seven prior
concurrences). This script exists so the frozen routing's DECISIONS are
checkable arithmetic, not prose.

Run:  python3 routing_length_check.py
Output is written to stdout; committed verbatim as output.txt.
"""

import math

print("routing_length_check.py -- routing freeze t_e5d5eaae, 2026-09-15")
print("=" * 66)
print("All geometric inputs INDUSTRY-NOMINAL UNVERIFIED (fe700201 2b):")
print("  RG316 OD t = 2.50 mm; static min bend R_min = 12.7 mm;")
print("  10xOD rule-of-thumb R = 25.0 mm. No vendor datasheet on host.")
print()

# ---------------------------------------------------------------- inputs
# [INDUSTRY-NOMINAL-UNVERIFIED] fe700201 2b / 55585471 3b
OD_RG316 = 2.50      # mm, jacket OD
OD_USBC = 4.5        # mm, mid-range of the 4.0-5.0 mm planning band
R_MIN_STATIC = 12.7   # mm, RG316 static min bend radius (absolute value)
R_RULE_THUMB = 25.0  # mm, 10xOD conservative alt rule

# [RECORD] fe700201 2a / 55585471 3b / t_0d86117f B1/B4 planned lengths
L_INT = 0.150        # m, interior RG316 assembly (DUT J1 -> bulkhead)
L_EXT = 0.500        # m, exterior RG316 assembly (bulkhead -> ref TX)

# [SPEC] routing freeze minimum service loops (this document sets these)
LOOP_MIN_INT = 0.05  # m, minimum interior service loop
LOOP_MIN_EXT = 0.10  # m, minimum exterior service loop

# [RECORD] fe700201 2d swept-envelope arithmetic (recomputed here)
print("--- swept envelope at the bulkhead 90-degree turn ---")
for label, R in (("static min bend R=12.7 mm", R_MIN_STATIC),
                 ("10xOD rule-of-thumb R=25.0 mm", R_RULE_THUMB)):
    swept = 2 * R + OD_RG316
    clearance = R + OD_RG316 / 2
    print(f"{label:34s}: swept diameter = {swept:5.1f} mm, "
          f"clearance from port face = {clearance:5.2f} mm")
print()

# ------------------------------------------------- planned-length check
print("--- planned assembly lengths vs frozen routing minimums ---")
print(f"interior planned L = {L_INT:.3f} m [RECORD]; "
      f"frozen minimum = tie-off + bend + {LOOP_MIN_INT:.2f} m loop")
print(f"exterior planned L = {L_EXT:.3f} m [RECORD]; "
      f"frozen minimum = bend + {LOOP_MIN_EXT:.2f} m loop")
print()

# Minimum interior leg: straight entry tie-off (15 mm) + quarter-arc at
# R_min (2*pi*R/4) + straight run to the loop + loop itself.
arc_q = math.pi * R_MIN_STATIC / 2.0   # mm, 90-degree arc at R_min
arc_q_rule = math.pi * R_RULE_THUMB / 2.0
tie_off = 15.0                          # mm [SPEC], first tie point standoff
print(f"90-deg arc length at R=12.7 mm  = {arc_q:6.1f} mm")
print(f"90-deg arc length at R=25.0 mm  = {arc_q_rule:6.1f} mm")
print(f"tie-off standoff from connector = {tie_off:5.1f} mm [SPEC]")
print()

for name, L in (("interior (C-RF-INT-1, 0.15 m)", L_INT),
                ("exterior (C-RF-EXT-1, 0.50 m)", L_EXT)):
    L_mm = L * 1000.0
    # most conservative committed rule: 10xOD arc + tie-off + loop
    budget = tie_off + arc_q_rule + (LOOP_MIN_INT if L == L_INT else LOOP_MIN_EXT) * 1000.0
    verdict = "PASSES" if L_mm >= budget else "FAILS -- re-plan length"
    print(f"{name}:")
    print(f"  planned {L_mm:6.1f} mm vs minimum budget "
          f"{tie_off:.0f}+{arc_q_rule:.1f}+"
          f"{(LOOP_MIN_INT if L == L_INT else LOOP_MIN_EXT)*1000:.0f} = {budget:6.1f} mm"
          f" -> {verdict}")
print()

# ----------------------------------------------------- bundle OD check
print("--- taped bundle OD (planning inputs, NOT measured) ---")
# fe700201 3c computation, reproduced exactly
d1 = OD_RG316
d2 = OD_USBC
taped = math.sqrt((d1 + d2) ** 2 + d2 ** 2) + 0.5  # +0.5 mm loom allowance
print(f"RG316 {d1} mm + USB-C {d2} mm taped side-by-side,"
      f" +0.5 mm loom -> equivalent OD = {taped:.2f} mm")
print("(identical arithmetic to fe700201 3c; inputs UNVERIFIED)")
print()

# ------------------------------------------------- cable ID inventory
print("--- cable ID list (frozen identifiers, zero physical instances) ---")
rows = [
    # id, class, status, crossing, note
    ("C-RF-INT-1", "RG316 SMA-m/m assembly, 0.15 m, interior",
     "MUST-PROCURE", "variant B only",
     "DUT J1 -> T1 -> bulkhead FT-DOOR/WALL; loop 50 mm"),
    ("C-RF-EXT-1", "RG316 SMA-m/m assembly, 0.50 m, exterior",
     "MUST-PROCURE", "variant B only",
     "bulkhead -> T3 -> reference TX; loop 100 mm"),
    ("C-SER-1", "USB-C serial, DUT console (variant A primary crossing)",
     "TBD-MPN on record? NO -- part number not on record",
     "variant A primary",
     "ttyACM0 per protocol; routed per variant-A rule"),
    ("C-SER-2", "USB-C serial, reference TX console",
     "TBD", "exterior only (never crosses)",
     "reference TX host port; outside chamber wall"),
]
for cid, cls, status, crossing, note in rows:
    print(f"{cid:12s} | {cls}")
    print(f"{'':12s} | status: {status}")
    print(f"{'':12s} | crossing: {crossing}")
    print(f"{'':12s} | {note}")
print()
print("FT- prefix rule for chamber ports: t_03954030 (FT-DOOR-n /")
print("FT-WALL-<SIDE>-n, clockwise from door hinge). Tie points T1..T3")
print("are new identifiers minted by this freeze.")
print()

# ------------------------------------------------ ambient evidence
print("--- ambient/bench conditions evidence (fresh read 2026-09-15) ---")
print("acpitz /sys/class/thermal/thermal_zone0 = 27800 -> 27.8 C (host")
print("  motherboard sensor; NOT bench ambient air -- labeled proxy)")
print("x86_pkg_temp thermal_zone1 = 95 -> 95.0 C reading is a package")
print("  throttle sensor artifact, not ambient; excluded as proxy")
print("Assumed ambient cells in every prior report: 20/22/25 C ASSUMED,")
print("  RH 30-60% ASSUMED (65c9c3df; warm-side-dewpoint all-cells-ASSUMED)")
print("Jacket warm/flexible: UNKNOWABLE -- no cable exists to touch")
print("Tension: UNKNOWABLE -- no routing exists to tension")
print()
print("END routing_length_check.py")