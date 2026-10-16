#!/usr/bin/env python3
"""
routing_measure_check_t_93afb6e2.py -- forced-bend / slack / bundle-OD
measurement-readiness check for meshcore card t_93afb6e2
("Measure bundle OD, slack, and forced bend at the routing path").

Purpose: this card's acceptance asks for MEASURED numbers. None can be
taken (no cable, no caliper, no tape, no chamber, no camera, no DUT on
this host). What CAN be done -- and is, here, reproducibly -- is:

  (a) recompute the ON-RECORD planning/derived numbers so the report's
      "planning value" column is not a copy-paste (reproduces the
      sibling freezes t_e5d5eaae / fe700201 arithmetic);
  (b) compute the FREE-MARGIN numbers that answer the card's step 2
      (available slack) at planning level; and
  (c) print the static-vs-dynamic decision inputs for step 4.

Every input is labelled [RECORD] (on-record source), [SPEC] (frozen
routing spec), or [INDUSTRY-NOMINAL-UNVERIFIED]. NO MEASUREMENT is
performed; no physical tool is read.

Rerun is byte-identical (stdlib only, no timestamps, no randomness).
"""

# ---------------- inputs ----------------
# [INDUSTRY-NOMINAL-UNVERIFIED] fe700201 2b: RG316 jacket OD (mm)
RG316_OD = 2.50
# [INDUSTRY-NOMINAL-UNVERIFIED] fe700201 2b: static min bend radius (mm),
#   given as an ABSOLUTE value, NOT an OD multiple
R_STATIC_MIN = 12.7
# [INDUSTRY-NOMINAL-UNVERIFIED] fe700201 2b: 10xOD rule-of-thumb (mm)
R_10XOD = 25.0
# [SPEC] frozen routing rule adopted by t_e5d5eaae (conservative)
R_FROZEN = 25.0
# [INDUSTRY-TYPICAL-UNVERIFIED] USB-C serial OD (mm), 4.0-5.0 range; mid 4.5
USB_C_OD = 4.5
# [SPEC] loom wall thickness (mm)
LOOM = 0.5
# [SPEC] tie-off standoff from connector back-shell (mm)
TIE_OFF = 15.0
# [SPEC] frozen service loops (mm)
LOOP_INT = 50.0
LOOP_EXT = 100.0
# [RECORD] planned assembly lengths (mm)
PLAN_INT = 150.0
PLAN_EXT = 500.0
# [SPEC] tool resolution floors (t_e5d5eaae sec 3)
CALIPER_FLOOR = 0.01   # mm least count
TAPE_FLOOR = 1.0       # mm least count


def arc_len_90(radius_mm: float) -> float:
    """90-degree arc length = (pi/2) * R."""
    import math
    return (math.pi / 2.0) * radius_mm


def swept_diameter(radius_mm: float, cable_od_mm: float) -> float:
    """Outer swept diameter of a cable bent to centreline radius R: 2R + t."""
    return 2.0 * radius_mm + cable_od_mm


def clearance_from_face(radius_mm: float, cable_od_mm: float) -> float:
    """Clearance from the port face to the outside of the bend: R + t/2."""
    return radius_mm + cable_od_mm / 2.0


def bundle_envelope(od_a: float, od_b: float, loom: float) -> float:
    """Equivalent OD of two round cables of OD a,b taped side-by-side,
    plus a loom wall on each side. Reproduces fe700201 3c / t_e5d5eaae
    sec 6 arithmetic: sqrt((a+b)^2 + b^2) + loom."""
    import math
    return math.sqrt((od_a + od_b) ** 2 + od_b ** 2) + loom


def main() -> None:
    import math
    L = []
    L.append("routing_measure_check_t_93afb6e2.py -- meshcore t_93afb6e2")
    L.append("=" * 66)
    L.append("NO MEASUREMENT PERFORMED. All inputs on-record / spec /")
    L.append("industry-nominal-UNVERIFIED. Physics reproduced, not measured.")
    L.append("")
    L.append("--- STEP 1: bundle OD ---")
    L.append("single RG316 cable envelope (variant A has NO bundle):")
    L.append("  RG316 alone                                = %.2f mm" % RG316_OD)
    L.append("taped bundle, RG316 coax + USB-C side-by-side (variant A+B")
    L.append("parallel run) -- PLANNING ARITHMETIC, NOT A MEASUREMENT:")
    env = bundle_envelope(RG316_OD, USB_C_OD, LOOM)
    L.append("  sqrt((%.2f+%.2f)^2 + %.2f^2) + %.2f loom  = %.2f mm"
             % (RG316_OD, USB_C_OD, USB_C_OD, LOOM, env))
    L.append("  (published on record as ~8.8 mm; recomputed here %.2f)" % env)
    L.append("  3 per-point caliper/tape readings along the run : UNKNOWN")
    L.append("  mean of the 3 readings                         : UNKNOWN")
    L.append("  measured cross-section shape (round/oval/ribbon): UNKNOWN")
    L.append("  cables actually in the bundle                  : UNKNOWN")
    L.append("")
    L.append("--- STEP 2: slack survey ---")
    arc = arc_len_90(R_FROZEN)
    L.append("90-deg arc at frozen R=%.1f mm          = %.1f mm" % (R_FROZEN, arc))
    L.append("90-deg arc at static-min R=%.1f mm      = %.1f mm"
             % (R_STATIC_MIN, arc_len_90(R_STATIC_MIN)))
    L.append("tie-off standoff                         = %.1f mm [SPEC]" % TIE_OFF)
    min_int = TIE_OFF + arc + LOOP_INT
    min_ext = TIE_OFF + arc + LOOP_EXT
    L.append("")
    L.append("interior C-RF-INT-1 (planned %.1f mm) vs frozen minimum budget:"
             % PLAN_INT)
    L.append("  budget = %.1f tie-off + %.1f arc + %.1f loop = %.1f mm"
             % (TIE_OFF, arc, LOOP_INT, min_int))
    L.append("  free margin = %.1f - %.1f = %.1f mm  (%.0f%% spare)"
             % (PLAN_INT, min_int, PLAN_INT - min_int,
                100.0 * (PLAN_INT - min_int) / PLAN_INT))
    L.append("exterior C-RF-EXT-1 (planned %.1f mm):" % PLAN_EXT)
    L.append("  budget = %.1f + %.1f + %.1f = %.1f mm"
             % (TIE_OFF, arc, LOOP_EXT, min_ext))
    L.append("  free margin = %.1f - %.1f = %.1f mm  (%.0f%% spare)"
             % (PLAN_EXT, min_ext, PLAN_EXT - min_ext,
                100.0 * (PLAN_EXT - min_ext) / PLAN_EXT))
    L.append("  MEASURED usable free length, inside / outside / tied-down")
    L.append("    each                                : UNKNOWN")
    L.append("  NOTE: 'free length' is a property of the INSTALLED path,")
    L.append("    i.e. (planned length) - (length consumed by the actual")
    L.append("    routing). Only the budget check above is on record; the")
    L.append("    real consumption depends on the unlocated chamber.")
    L.append("")
    L.append("--- STEP 3/5: forced bend ---")
    for r, tag in ((R_STATIC_MIN, "static min"), (R_FROZEN, "frozen rule")):
        L.append("R=%.1f mm (%s): swept diameter = %.1f mm, clearance = %.2f mm"
                 % (r, tag, swept_diameter(r, RG316_OD),
                    clearance_from_face(r, RG316_OD)))
    L.append("  MEASURED tightest bend radius centreline     : UNKNOWN")
    L.append("  MEASURED second-tightest bend                : UNKNOWN")
    L.append("  second bend within 20%% of tightest?          : UNKNOWN")
    L.append("    (frozen path defines ONE deliberate bend B1; the exterior")
    L.append("     drape carries no specified bend below %.1f mm, so no"
             % R_FROZEN)
    L.append("     distinct 2nd bend is DEFINED, let alone measured)")
    L.append("")
    L.append("--- STEP 4: static vs dynamic ---")
    L.append("Decision inputs from the frozen routing spec (t_e5d5eaae):")
    L.append("  B1 is a bend in the INTERIOR floor run, anchored at T1,")
    L.append("    formed at install time, one plane, R>=%.1f mm [SPEC]"
             % R_FROZEN)
    L.append("  no moving joint / no articulation in the path [SPEC]")
    L.append("  cable lies slack, no tension, loops carry slack [SPEC]")
    L.append("  -> the forced bend is STATIC (installed, not moving in")
    L.append("     operation) -- determination from SPEC, not observation")
    L.append("  governing spec once measured = STATIC min bend radius")
    L.append("    (%.1f mm industry-nominal-UNVERIFIED), NOT a dynamic value"
             % R_STATIC_MIN)
    L.append("  dynamic min bend radius on record           : UNKNOWN")
    L.append("")
    L.append("--- tool floors that will bound every future reading ---")
    L.append("caliper least count = %.2f mm; tape least count = %.1f mm [SPEC]"
             % (CALIPER_FLOOR, TAPE_FLOOR))
    L.append("")
    L.append("END routing_measure_check_t_93afb6e2.py")
    print("\n".join(L))


if __name__ == "__main__":
    main()
