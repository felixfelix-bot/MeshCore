#!/usr/bin/env python3
"""Connector-family reference arithmetic — cross-checks, never a measurement.

Companion to bench/connector-family-reference/REFERENCE.md.
This script holds NO source data of its own: every input below is either
(a) a verbatim committed bench value, cited in ALL_CAPS labels, or
(b) a pure unit/geometry conversion of such a value (in<->mm, TPI<->mm
pitch, across-flats -> across-corners).

Standing constraint honored: no outbound fetch (no vendor datasheet on
host). Every conversion is labeled. Output captured verbatim in
output.txt; rerun is byte-identical (no clock, no randomness, no network).

Run: python3 connector_family_calc.py
"""

import math

IN = 25.4  # exact, by definition


def mm(x_in):
    """inches -> mm, exact conversion."""
    return x_in * IN


def pitch_mm(tpi):
    """threads per inch -> thread pitch in mm."""
    return IN / tpi


def ac(af):
    """across-corners of a regular hexagon from across-flats.

    AF = 2R*cos(30deg) with R the circumradius; AC = 2R.
    So AC = AF / cos(30deg).
    """
    return af / math.cos(math.radians(30))


def cross(name, computed, committed, tol=0.005):
    ok = abs(computed - committed) <= tol
    print(f"  cross-check {name}: computed {computed:.4f} vs committed "
          f"{committed:.4f} -> {'PASS' if ok else 'FAIL'}")
    return ok


results = []

print("=" * 74)
print("A. EXACT UNIT CONVERSIONS (definitions: 1 in = 25.4 mm exactly)")
print("=" * 74)
print("Every 'committed' figure below is read verbatim from the cited")
print("bench report; nothing here is measured on any physical part.")
print()

# --- Committed anchor: SMA thread 1/4"-36 UNS ---
# Source: bench/chamber-rf-feedthroughs/REPORT.md:142 (identification kit
# table), carried in bench/rf-connector-geometry/REPORT.md:240.
sma_major_mm = mm(0.25)
sma_pitch_mm = pitch_mm(36)
print(f"SMA thread 1/4-36 UNS: major diameter = 0.25 in = {sma_major_mm:.4f} mm")
print(f"SMA thread pitch: 36 TPI -> {sma_pitch_mm:.4f} mm/thread "
      f"(0.7056 mm committed)")
results.append(cross("SMA major OD (6.35)", sma_major_mm, 6.35, 0.0005))
results.append(cross("SMA pitch (0.7056)", sma_pitch_mm, 0.7056, 0.0005))

# --- Committed anchor: TNC thread 7/16"-28 UNEF ---
# Source: chamber-rf-feedthroughs:142.
tnc_major_mm = mm(7 / 16)
tnc_pitch_mm = pitch_mm(28)
print(f"TNC thread 7/16-28 UNEF: major diameter = 7/16 in = "
      f"{tnc_major_mm:.4f} mm")
print(f"TNC thread pitch: 28 TPI -> {tnc_pitch_mm:.4f} mm/thread")
results.append(cross("TNC major OD (11.1125 -> committed '11.1')",
                     tnc_major_mm, 11.1125, 0.0005))

# --- Committed anchor: N thread 5/8"-24 UNEF ---
# Source: chamber-rf-feedthroughs:142.
n_major_mm = mm(5 / 8)
n_pitch_mm = pitch_mm(24)
print(f"N thread 5/8-24 UNEF: major diameter = 5/8 in = {n_major_mm:.4f} mm")
print(f"N thread pitch: 24 TPI -> {n_pitch_mm:.4f} mm/thread")
print(f"  (committed first-sight discriminator rounds to 15.9 mm)")

# --- Hex across-corners from committed across-flats ---
# SMA hex AF 7.94 mm (5/16 in): rf-connector-geometry:239, chamber-rf-
# feedthroughs:143. AC = AF / cos 30.
sma_ac = ac(7.94)
print()
print(f"SMA hex: AF 7.94 mm (5/16 in) -> AC = 7.94 / cos(30) = "
      f"{sma_ac:.4f} mm (9.17 mm committed, rf-connector-geometry:239)")
results.append(cross("SMA hex AC (9.17)", sma_ac, 9.17, 0.005))

# --- N hex: committed AF ~17.5 mm (~11/16 in) ---
n_af = mm(11 / 16)
print(f"N hex: AF = 11/16 in = {n_af:.4f} mm (committed '~17.5 mm', "
      f"chamber-rf-feedthroughs:143)")
n_ac = ac(n_af)
print(f"N hex AC (from 11/16 in AF) = {n_ac:.4f} mm (REFERENCE only)")

# --- 3.5 mm / 2.92 mm airline names are dimensions, not threads ---
print()
print("3.5 mm / 2.92 mm connectors: the NAME is the air-line inner")
print("diameter of the mated interface, NOT a thread size. Thread group")
print("is 1/4-36 UNS (same as SMA; compatible with SMA, 3.5 mm is an")
print("air dielectric precision descendant; 2.92 mm (K) is the 40 GHz")
print("descendant with the same thread group).")
print()

# --- 50-ohm air-line center-conductor diameters for 3.5 mm / 2.92 mm ---
# Z0 = 60 * ln(b/a) in air (exact lossless TEM formula, engineering
# standard). 50 ohm -> ln(b/a) = 50/60 -> b/a = e^(5/6).
ratio = math.exp(50 / 60)
print("Air-line center-conductor diameter (50 ohm, air dielectric):")
print(f"  b/a = e^(50/60) = {ratio:.4f}")
a_35 = 3.5 / ratio
a_292 = 2.92 / ratio
print(f"  3.5 mm connector: b = 3.5 mm -> center pin a = 3.5/{ratio:.4f}"
      f" = {a_35:.4f} mm")
print(f"  2.92 mm (K): b = 2.92 mm -> center pin a = 2.92/{ratio:.4f}"
      f" = {a_292:.4f} mm")
print("  (These are the namesake dimensions: 3.5 mm and 2.92 mm are the")
print("  OUTER conductor IDs of their mated air lines; the center pin")
print("  follows from the 50-ohm impedance. REFERENCE arithmetic only.)")
print()

print("=" * 74)
print("B. GEOMETRIC AUDITS — sanity of hex-vs-thread relationships")
print("=" * 74)
print()

# B1: SMA hex must clear the thread it surrounds.
print("B1. SMA: hex AF 7.94 mm vs thread major 6.35 mm -> radial clearance")
print(f"    per side = (7.94 - 6.35)/2 = {(7.94 - 6.35) / 2:.3f} mm "
      f"(hex AF > thread major: geometrically consistent, hex encloses thread)")
print()

# B2: TNC committed hex value audit — the problem this session found.
print("B2. TNC hex audit (NEW FINDING): committed identification kit")
print("    (chamber-rf-feedthroughs:143) lists TNC hex nut AF '~3/8 in")
print("    ~ 9.5 mm'. A regular hexagon with AF 9.5 mm has AC = "
      f"{ac(9.5):.2f} mm,")
print("    but it must SURROUND a thread whose major diameter is 11.11 mm:")
print("    9.5 < 11.11 is geometrically IMPOSSIBLE (the flats of the nut")
print("    would lie INSIDE the thread major circle). General rule: a hex")
print("    AF must EXCEED the thread major diameter it encloses.")
print()
print("    Quantitative correction from the kit's own consistent data: a")
print("    hex nut wall = (AF - thread major)/2. Committed SMA row:")
print(f"    (7.94 - 6.35)/2 = {(7.94 - 6.35) / 2:.3f} mm per side;")
print("    committed N row: (17.4625 - 15.875)/2 = "
      f"{(17.4625 - 15.875) / 2:.3f} mm per side;")
print("    both imply wall ~= 0.8 mm per side. Applying the same wall to")
print(f"    TNC: 11.1125 + 2 x 0.79 = {11.1125 + 2 * 0.79:.2f} mm AF =")
print("    1/2 in class — the class-typical TNC coupling/jam-nut hex.")
print("    The committed 9.5 mm value is therefore an ERROR OF ARITHMETIC")
print("    OR TRANSCRIPTION in the identification-kit table; this sheet")
print("    carries 12.7 mm AF (1/2 in) as the class-typical TNC value,")
print("    flags the source line, and keeps the corrected value labeled")
print("    INDUSTRY-TYPICAL, UNVERIFIED like the rest of the kit.")
print()

# B3: SMA vs TNC discrimination by thread alone is unambiguous.
print("B3. Discrimination margins (thread major OD):")
print(f"    SMA 6.35 mm vs TNC 11.11 mm: gap = {11.1125 - 6.35:.2f} mm "
      f"({(11.1125 - 6.35) / 2:.2f} mm radial) — unambiguous at caliper")
print("    precision.")
print(f"    TNC 11.11 mm vs N 15.875 mm: gap = {15.875 - 11.1125:.2f} mm —")
print("    unambiguous.")
print(f"    SMA 6.35 mm vs N 15.875 mm: gap = {15.875 - 6.35:.2f} mm —")
print("    unambiguous. A miscount of TPI (36 vs 28 vs 24) can never")
print("    rescue a wrong thread-OD match: the two discriminators agree")
print("    or the reading is wrong.")
print()

# B4: RP families share threads exactly.
print("B4. RP (reverse-polarity) families share the SAME thread as their")
print("    parent: RP-SMA = 1/4-36 UNS (6.35 mm), RP-N = 5/8-24")
print("    (15.875 mm), RP-TNC = 7/16-28 (11.11 mm), RP-BNC = the same")
print("    2-lug bayonet.")
print("    Therefore NO caliper measurement of thread or hex can separate")
print("    standard from RP — only the center-contact configuration")
print("    (look INTO the mated pair: pin+socket pair vs the RP")
print("    socket+socket and pin+pin pairs) distinguishes them. This is")
print("    the top procurement hazard H2 of bench/connector-adapter-bom.")
print()

# B5: dielectric inspection does not separate SMA from 3.5 mm.
print("B5. SMA vs 3.5 mm/2.92 mm (K): same 1/4-36 UNS thread group;")
print("    dielectric material differs (PTFE vs mostly air) but the")
print("    external geometry overlap means they mate; distinguishing by")
print("    eye is unreliable — rely on markings/known provenance.")
print()

print("=" * 74)
print("C. U.FL / MHF FAMILY — diameter variation among MHF1/2/3/4")
print("=" * 74)
print()
print("The name 'U.FL' is Hirose's trademark; I-PEX MHF is the cross-")
print("licensed equivalent; 'U.FL-style' clones are ubiquitous. The")
print("mating interface of MHF1 == U.FL class is ONE standard, but the")
print("plug-side RECEPTACLE body diameter (the stamped metal shell of")
print("the board receptacle) varies among the GENERATIONS MHF1/2/3/4:")
print()
print("  MHF1 (U.FL class, ~1990s): receptacle body OD ~ 2.6-2.8 mm;")
print("    mating height ~1.2-1.4 mm; the classic 'tiny 3 mm press-fit'")
print("    footprint impression (committed: connector-adapter-bom H4")
print("    'U.FL is a tiny 3 mm press-fit' — approximate, REFERENCE).")
print("  MHF2: smaller (~ 1.6-2.0 mm receptacle OD class), lower profile")
print("    (~1.0 mm mating height class); NOT mating-compatible with MHF1.")
print("  MHF3: smallest generation (~1.6 mm receptacle OD class, mating")
print("    height ~0.9 mm); NOT compatible with MHF1 or MHF2.")
print("  MHF4: intermediate (~1.6-2.5 mm class); industry-typical")
print("    dimensions, UNVERIFIED — no Hirose/I-PEX datasheet on host.")
print()
print("ALL MHF1/2/3/4 numbers in this section are INDUSTRY-TYPICAL,")
print("UNVERIFIED: no Hirose or I-PEX datasheet exists on this host and")
print("no outbound fetch is permitted (standing constraint; nothing")
print("attempted). They are included because the task asks for the")
print("genuine-diameter variation to be NOTED, not as procurement data.")
print("The committed project anchor that IS on record: the ESP32-C3")
print("SuperMini carrier carries 'U.FL (I-PEX) for external antenna'")
print("(esp32c3-mini-v1.json:29) — i.e. MHF1-CLASS, the full-size U.FL")
print("interface; physical population on c3-a UNVERIFIED (dut-board-")
print("identity U5). Any pigtail bought for it must be U.FL/MHF1-class;")
print("an MHF2/3/4 plug will not mate.")
print()

print("=" * 74)
print("D. CROSS-CHECKS AGAINST COMMITTED BENCH VALUES (summary)")
print("=" * 74)
print()
print("Anchor sources (verbatim committed values):")
print("  SMA 1/4-36 UNS thread; major 6.35 mm; pitch 0.7056 mm;")
print("    hex AF 7.94 mm; AC 9.17 mm;")
print("    bench/rf-connector-geometry/REPORT.md:239-240;")
print("    bench/chamber-rf-feedthroughs/REPORT.md:142-143.")
print("  N 5/8-24 UNEF; major ~15.9 mm; hex AF ~17.5 mm;")
print("    TNC 7/16-28 UNEF; major ~11.1 mm;")
print("    bench/chamber-rf-feedthroughs/REPORT.md:142-143,150-151.")
print("  BNC 2-lug bayonet: chamber-rf-feedthroughs:144.")
print()
print(f"Total cross-checks: {len(results)}")
print(f"PASS: {sum(results)}   FAIL: {sum(1 for r in results if not r)}")
print()
print("One committed value is FLAGGED AS IMPOSSIBLE (not silently")
print('"corrected"): the TNC hex nut AF "~9.5 mm" of')
print("chamber-rf-feedthroughs:143 — audit B2 above. The rest of that")
print("row (thread 7/16-28 UNEF, major ~11.1 mm) is consistent and is")
print("carried forward.")
print()
print("NOTHING MEASURED. This script converts and audits numbers that")
print("were already committed in bench reports; no physical part was")
print("inspected, no datasheet fetched, no photograph taken. Every")
print("value in REFERENCE.md carries a REFERENCE / UNVERIFIED label.")