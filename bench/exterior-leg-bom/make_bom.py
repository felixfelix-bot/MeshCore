#!/usr/bin/env python3
"""Generator for the chamber-EXTERIOR -> instrument BOM segment.

Card: meshcore:t_a4844b93 "Specify chamber-exterior to instrument line items".

Stdlib only. No clock, no randomness, no network. Rewrites
EXTERIOR-LEG-BOM.md and exterior_leg_bom.csv byte-identically on every run,
then self-checks the two acceptance conditions that are mechanically checkable:

  1. the 7 mandated columns appear in the card's exact order and every data
     row has all 7 cells non-empty;
  2. every row states series + gender transition + impedance (or an explicit
     N/A with its reason), carries a citation, and is annotated UNVERIFIED or
     declared NIL (no row may claim a positive VERIFIED status).

Exit code 0 = all checks pass, 1 = at least one check failed.
"""

import csv
import hashlib
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
MD = os.path.join(HERE, "EXTERIOR-LEG-BOM.md")
CSV = os.path.join(HERE, "exterior_leg_bom.csv")

# ---------------------------------------------------------------- columns ----
# Card step 2: "Columns exactly: Item description | QTY | Part number (...) |
# Disposition (...) | Lead-time estimate (...) | Source/vendor | Cited source
# for the connector identification."
HEADER = [
    "Item description",
    "QTY",
    "Part number (real MPN preferred; otherwise 'MPN TBD' plus required "
    "interface spec: connector series, gender, impedance, frequency rating, "
    "max VSWR)",
    "Disposition (ON-HAND / MUST-PROCURE / MUST-FABRICATE)",
    "Lead-time estimate",
    "Source/vendor",
    "Cited source for the connector identification",
]

# ------------------------------------------------------------------ rows -----
# E1 is the only firm procurement line on this segment (the exterior cable
# assembly, frozen as C-RF-EXT-1). E2/E3/E4 are conditional adapters: the
# instrument port is UNSPECIFIED (IF-10) and the feedthrough EXTERIOR face is
# UNKNOWN (IF-7), so the gender transition each of them would supply is real
# but not yet selected. E5/E6 are NIL declarations (nothing is bought): the
# card's step 1 asks for "any inline pad/attenuator explicitly required" and
# for every gender transition, so the two cases that turn out NOT to need a
# part are stated rather than silently dropped.

ROWS = [
    dict(
        rid="E1",
        desc=(
            "Chamber-EXTERIOR cable assembly - the exterior leg, bulkhead "
            "exterior face to the instrument port (frozen identifier "
            "C-RF-EXT-1). Gender transition: SMA-M plug (bulkhead exterior "
            "SMA-F jack) to SMA-M plug (instrument SMA-F jack) - male-to-male, "
            "no gender-changing adapter in this leg. Impedance 50 ohm."
        ),
        qty="1",
        spec=(
            "MPN TBD - required spec: RG316 coax (OD 2.5 mm, solid PTFE "
            "dielectric), 0.50 m, SMA plug (male pin) BOTH ends, standard "
            "polarity (NOT RP-SMA), straight, 50 ohm, 868 MHz measurement "
            "band, SMA-class DC-18 GHz class context, max VSWR 1.05:1 class at "
            "868 MHz for standard SMA, flex life adequate for a 25.0 mm min "
            "bend radius. Representative class named on record: Amphenol "
            "ACX-1169-class RG316 patch (exact-length variant TBD) - "
            "representative only, not an on-hand part."
        ),
        disp=(
            "MUST-PROCURE (nothing on this segment exists on any record: no "
            "coax of any type is on host or on record)"
        ),
        lead="2-5 days (procurement estimate carried from the sibling BOM)",
        vendor="Digi-Key / Mouser (vendor class; live availability UNVERIFIED)",
        cite=(
            "UNVERIFIED - see open risks. Identification from parent row IF-9 "
            "(bench/interface-normalization/INTERFACE-TABLE.md), which cites "
            "SUPPORTING bench/connector-adapter-bom/REPORT.md line B4 verbatim: "
            "\"RG316 coax assembly, SMA-male to SMA-male, 0.50 m (bulkhead to "
            "reference TX, exterior) | 1 | MPN TBD - same spec as B1, 0.50 m\" "
            "and bench/routing-freeze/REPORT.md verbatim: \"C-RF-EXT-1 | RG316 "
            "SMA-m/m, 0.50 m, exterior (bulkhead -> ref TX) | MUST-PROCURE, MPN "
            "TBD\". CONFLICT RESTATED INLINE: the bulkhead-side SMA-M plug "
            "presupposes an SMA-F jack on the feedthrough EXTERIOR face, which "
            "parent row IF-7 records as UNKNOWN - \"no port to inspect\" - "
            "because no chamber exists on any record; sibling (c) warns the two "
            "faces may differ in series (\"interior and exterior may differ "
            "(e.g. N-exterior / SMA-interior adapter feedthrough) - only a "
            "physical walk resolves each side separately\", "
            "bench/chamber-rf-feedthrough-list/FEEDTHROUGH-LIST.md FT-1). If "
            "the exterior face proves N-type, this assembly is wrong at that "
            "end and line E4 (or an N-type assembly) is required instead. The "
            "far end likewise assumes a female SMA jack at the instrument: "
            "IF-10 records the reference TX jack as document-based and any "
            "future bench instrument as UNSPECIFIED."
        ),
    ),
    dict(
        rid="E2",
        desc=(
            "Adapter, INSTRUMENT side, N-type case - SMA-F jack to N-M plug "
            "(gender transition: SMA-F to N-M). Fits the exterior cable's "
            "SMA-M plug (E1) into an instrument port that presents N-female. "
            "Impedance 50 ohm."
        ),
        qty="0-1 (0 today)",
        spec=(
            "MPN TBD - required spec: SMA jack (female) to N plug (male), "
            "50 ohm (NOT 75 ohm), DC-3 GHz, low-VSWR, standard polarity. No "
            "numeric max-VSWR value for an N/SMA adapter exists on any record, "
            "so the number must come from the procured part's datasheet at "
            "order time; frequency rating 868 MHz measurement band."
        ),
        disp=(
            "MUST-PROCURE - conditional (qty 0 today: no RF instrument exists; "
            "qty 1 only if a bench instrument with an N-female port is "
            "procured)"
        ),
        lead="1-3 days once the instrument is named (carried from the sibling BOM)",
        vendor="Digi-Key / Mouser (vendor class)",
        cite=(
            "UNVERIFIED - see open risks. Identification from parent row IF-10 "
            "(UNVERIFIED) which cites bench/instrument-rf-connectors/REPORT.md "
            "caveat 5 verbatim: \"Most sub-GHz signal generators and spectrum "
            "analyzers present N-type or 3.5 mm connectors (not SMA), which "
            "would require SMA-to-N or SMA-to-3.5mm adapters\", and "
            "bench/connector-adapter-bom/REPORT.md line B11 verbatim: "
            "\"Conditional instrument adapter: SMA-F jack to N-M plug (for a "
            "signal generator / analyzer with N-female port), or SMA-F to "
            "BNC-M if BNC | 0-1 | MPN TBD - required spec: 50 ohm, DC-3 GHz, "
            "low-VSWR adapter matching whatever instrument is eventually "
            "procured | CONDITIONAL (qty 0 today: no RF instrument exists - "
            "input 2)\". CONFLICT RESTATED INLINE: IF-10 is UNSPECIFIED for any "
            "future bench instrument - the de-facto far end is the reference TX "
            "MeshCore node, whose port is SMA (\"RF connector | SMA edge-launch, "
            "standard polarity, female jack, 50 ohm (same carrier board family "
            "as the DUT) | UNVERIFIED for the specific board assigned as "
            "reference TX\", bench/instrument-rf-connectors/REPORT.md), in which "
            "case NO adapter is needed at all and this line stays at qty 0. "
            "Buying it now would be a guess (B11: \"buying B11 now would be a "
            "guess\")."
        ),
    ),
    dict(
        rid="E3",
        desc=(
            "Adapter, INSTRUMENT side, BNC case - SMA-F jack to BNC-M plug "
            "(gender transition: SMA-F to BNC-M). Fits the exterior cable's "
            "SMA-M plug (E1) into an instrument port that presents BNC-female "
            "(the counter/instrument case). Impedance 50 ohm."
        ),
        qty="0-1 (0 today)",
        spec=(
            "MPN TBD - required spec: SMA jack (female) to BNC plug (male), "
            "50 ohm - a 75 ohm video/CCTV BNC is INADMISSIBLE (sibling hazard "
            "H1), DC-3 GHz, low-VSWR, bayonet coupling (no thread, so no torque "
            "spec applies to the BNC end). No numeric max-VSWR value for an "
            "SMA/BNC adapter exists on any record; frequency rating 868 MHz "
            "measurement band."
        ),
        disp=(
            "MUST-PROCURE - conditional (qty 0 today: no RF instrument exists; "
            "qty 1 only if a bench instrument with a BNC-female port is "
            "procured)"
        ),
        lead="1-3 days once the instrument is named (carried from the sibling BOM)",
        vendor="Digi-Key / Mouser (vendor class)",
        cite=(
            "UNVERIFIED - see open risks. Same identification basis as E2, "
            "verbatim from bench/connector-adapter-bom/REPORT.md B11: "
            "\"... or SMA-F to BNC-M if BNC\". CONFLICT RESTATED INLINE: the "
            "instrument port is UNSPECIFIED (parent row IF-10: no RF instrument "
            "exists on any record), and the sibling hazard H1 applies to this "
            "line specifically - verbatim: \"75 ohm vs 50 ohm: video/CCTV coax "
            "(RG-59/RG-6, 75 ohm, F/BNC) is commonly stocked in labs; the "
            "LR2021 system and every line in this BOM is 50 ohm\"; a 75 ohm BNC "
            "adapter would present an impedance discontinuity, not a "
            "transition."
        ),
    ),
    dict(
        rid="E4",
        desc=(
            "Adapter, BULKHEAD-EXTERIOR-FACE case - N-M plug to SMA-F jack "
            "(gender transition: N-M to SMA-F). Fits the exterior cable's "
            "SMA-M plug (E1) onto a feedthrough exterior face that proves to be "
            "an N-female jack instead of the planned SMA-F jack. Impedance "
            "50 ohm."
        ),
        qty="0-1 (0 today)",
        spec=(
            "MPN TBD - required spec: N plug (male) to SMA jack (female), "
            "50 ohm, DC-3 GHz, low-VSWR, standard polarity, brass/gold, PTFE "
            "dielectric. No numeric max-VSWR value for an N/SMA adapter exists "
            "on any record; frequency rating 868 MHz measurement band (N-class "
            "rating context only, UNVERIFIED on host)."
        ),
        disp=(
            "MUST-PROCURE - conditional (qty 0 today: no chamber exists on any "
            "record, so no exterior face exists to measure; qty 1 only if a "
            "located chamber's exterior face proves N-type)"
        ),
        lead="2-5 days (same procurement class as the SMA/N adapters; no on-record quote)",
        vendor="Digi-Key / Mouser (vendor class)",
        cite=(
            "UNVERIFIED - see open risks. Identification from parent row IF-7 "
            "(status UNVERIFIED / UNSPECIFIED) which cites SIBLING (c) "
            "bench/chamber-rf-feedthroughs/REPORT.md record F1 verbatim: "
            "\"Exterior-side connector family | UNKNOWN | same - note "
            "interior/exterior may differ (e.g. N-exterior/SMA-interior adapter "
            "feedthrough); only a physical walk resolves each side separately\", "
            "and bench/chamber-rf-feedthrough-list/FEEDTHROUGH-LIST.md FT-1 "
            "verbatim: \"UNKNOWN - no port to inspect; interior and exterior may "
            "differ (e.g. N-exterior / SMA-interior adapter feedthrough) - only "
            "a physical walk resolves each side separately\". CONFLICT RESTATED "
            "INLINE: this line exists only because IF-7 is UNKNOWN; the PLANNED "
            "class is an SMA jack-jack feedthrough (\"The planned/procurement "
            "feedthrough class is UNFILTERED by construction: an SMA "
            "panel-mount jack-jack bulkhead (Amphenol 132134-class per 55585471) "
            "is a direct gold-plated contact pair with PTFE dielectric - no "
            "filter elements\", bench/chamber-rf-feedthroughs/REPORT.md STEP 5), "
            "in which case no adapter is needed and this line stays at qty 0. "
            "A FILTERED OEM port would be unusable for the RF path at any "
            "gender (same report, LOUD FLAG)."
        ),
    ),
    dict(
        rid="E5",
        desc=(
            "Inline pad / attenuator on the exterior leg - NIL BY DESIGN: no "
            "attenuator, pad, LNA, bias tee or other inline RF element is "
            "required anywhere on this segment. Stated so its absence is not "
            "read as an omission (card step 1 asks for any inline pad the "
            "instrument port identification or feedthrough assessment requires; "
            "the sourced answer is that none is required)."
        ),
        qty="0",
        spec=(
            "N/A - no part. No inline RF element is required: the segment is a "
            "passive 50 ohm cable plus (conditionally) one gender transition, "
            "and no record specifies an attenuator, pad, amplifier, bias tee or "
            "filter for it."
        ),
        disp=(
            "NIL (qty 0) - not required. No ON-HAND / MUST-PROCURE / "
            "MUST-FABRICATE disposition applies because there is nothing to "
            "obtain; stating NIL with its reason is the honest disposition."
        ),
        lead="N/A - nothing to procure or fabricate",
        vendor="N/A - nothing to source",
        cite=(
            "NIL - reason cited. bench/instrument-rf-connectors/REPORT.md STEP "
            "1 verbatim: \"| Attenuator | NO | N/A | N/A | Not on any record or "
            "BOM; rf-feedthrough-bom 55585471 does not list one |\" and \"| "
            "Amplifier (LNA) | NO | N/A | N/A | cable-feedthrough-failure-modes "
            "04db4fae:460-461 (\\\"no LNA, attenuator, or RF instrument "
            "anywhere\\\") |\". Feedthrough assessment: no attenuator is "
            "required by the conducted path; the only attenuation issue on "
            "record is a FILTERED OEM port, which is a usability gate on the "
            "feedthrough (bench/chamber-rf-feedthroughs/REPORT.md STEP 5 LOUD "
            "FLAG), not a part to add here. Insertion loss of the whole "
            "conducted chain is ~0.3-0.5 dB at 868 MHz against a 165 dB link "
            "budget, i.e. no pad is needed to protect anything "
            "(bench/rf-feedthrough-bom/REPORT.md STEP 5)."
        ),
    ),
    dict(
        rid="E6",
        desc=(
            "Adapter, INSTRUMENT side, 3.5 mm / 2.92 mm (K) precision case - "
            "NIL BY DESIGN: no adapter is required. A 3.5 mm (or 2.92 mm K) "
            "male connector mates an SMA female jack directly. Stated because "
            "the instrument port identification names 3.5 mm as one of the two "
            "likely future instrument ports; the sourced answer is that this "
            "case adds no part."
        ),
        qty="0",
        spec=(
            "N/A - no part. The gender transition SMA-F to 3.5 mm-M is "
            "supplied by the instrument's own connector: same 1/4-36 UNS "
            "thread group, same 7.94 mm hex, 50 ohm, intentional mating."
        ),
        disp=(
            "NIL (qty 0) - not required. No disposition applies because no "
            "part is obtained; a precision adapter would be bought only to add "
            "cost (sibling H3)."
        ),
        lead="N/A - nothing to procure or fabricate",
        vendor="N/A - nothing to source",
        cite=(
            "NIL - reason cited. bench/connector-family-reference/REFERENCE.md "
            "note 2 verbatim: \"SMA vs 3.5 mm vs 2.92 mm (K) - same thread "
            "group, same hex, and they intentionally mate. Distinguish by "
            "markings (\\\"3.5mm\\\"/\\\"K\\\"), price/provenance, and the "
            "dielectric look ... At 868 MHz they are interchangeable "
            "electrically\"; and bench/connector-adapter-bom/REPORT.md H3 "
            "verbatim: \"Precision vs standard SMA: precision SMA / 3.5 mm "
            "connectors are dimensionally compatible but cost 5-10x; at 868 MHz "
            "(and even 2.4 GHz) standard SMA is fully adequate (VSWR spec "
            "1.05:1 class at these frequencies).\" The instrument port itself "
            "remains UNSPECIFIED (parent row IF-10) - the NIL is conditional on "
            "the mating being 3.5 mm-M, which is a physical check on the "
            "instrument when one exists."
        ),
    ),
]

# ---------------------------------------------------------------- prose ------
TITLE = """# Chamber-EXTERIOR to instrument - BOM line items

Card `meshcore:t_a4844b93` - "Specify chamber-exterior to instrument line items".
Profile `worker-base` - host `c03rad0r-DQ05proplus` - branch `worker-base/t_a4844b93`.

Deliverable: the BOM lines for the RF chain from the **chamber-exterior side of the bulkhead
feedthrough** to the **instrument port**. Machine twin: `exterior_leg_bom.csv` (same rows, same
column order, generated from the same in-memory list by `make_bom.py`).

---

## 0. Boundary, and the input this list is built from

**Starting boundary (inclusive of nothing):** the exterior face of the bulkhead feedthrough, parent
row `IF-7`. The feedthrough connector itself and everything on its chamber-interior side belong to
the sibling DUT-to-interior card (`t_fe6e9c1b`) and are **not** on this list. **Ending boundary:**
the instrument port, parent row `IF-10`.

Every connector identification below is **reused verbatim** from the parent's normalized interface
table (`bench/interface-normalization/INTERFACE-TABLE.md`, `bench/interface-normalization/interface_table.csv`,
branch `worker-base/t_1bb81290`, HEAD `d6bbc980`). Nothing is re-derived from raw sources: the parent
row id is named on every line, and the underlying sibling quotation the parent carried is quoted
again where a line needs it.

Rows consumed from the parent table: `IF-7` (bulkhead exterior face - UNKNOWN/UNSPECIFIED),
`IF-9` (the exterior cable assembly, frozen `C-RF-EXT-1`), `IF-10` (instrument port - UNVERIFIED,
no RF instrument exists). Corroborating rows for the boundary: `IF-8` (the wall bore - not a
component of this segment), `IF-11` (the non-RF serial crossing - not this segment).

**Honesty state carried forward:** the parent table has ZERO `VERIFIED` rows - the DUT is not
attached to any host, no chamber exists on any record, and no RF instrument exists. Every line on
this segment therefore inherits at least one UNVERIFIED input, and each line says which one.

---

## 1. THE SEGMENT BOM (columns exactly as the card mandates, in order)

"""

TAIL_1 = """
Rows `E1`-`E4` are the physical components of this segment; `E5`-`E6` are **NIL declarations**
(cases the card asks about that turn out to require no part). NIL rows carry `QTY 0` and a
disposition that says *why* nothing is obtained, rather than a wrong ON-HAND/MUST-PROCURE label -
stating NIL is part of the deliverable, not an omission.

---

## 2. CHAIN WALK - every gender transition on this segment, stated explicitly

```
[IF-7] bulkhead feedthrough, EXTERIOR face
       planned class: SMA-F jack  (UNKNOWN on any record - no chamber exists)
   |
   |  mates with the SMA-M plug of E1  (SMA-F jack <- SMA-M plug)
   v
[E1] C-RF-EXT-1  RG316 assembly, 0.50 m
       SMA-M plug === SMA-M plug, standard polarity, 50 ohm
   |                                   (male-to-male: NO gender adapter in the leg)
   |
   |  (a) direct mate, no adapter - instrument presents SMA-F jack
   |      => the de-facto case today: the reference TX node (IF-10)
   |  (b) E2   SMA-F jack  <- N-M plug      (instrument presents N-female)
   |  (c) E3   SMA-F jack  <- BNC-M plug    (instrument presents BNC-female)
   |  (d) E6   NIL - a 3.5 mm-M / 2.92 mm-M instrument port mates the
   |      SMA-F jack directly (same thread group) - no adapter bought
   |  (e) E5   NIL - no inline pad/attenuator anywhere on the segment
   v
[IF-10] instrument port
       today: reference TX MeshCore node, SMA-F jack, 50 ohm (UNVERIFIED)
       future: bench RF instrument - series UNSPECIFIED (N-female most likely)
```

Second conditional transition, at the **other** end of the same cable:

```
[IF-7] exterior face proves N-female instead of the planned SMA-F jack
   |  => E4   N-M plug <- SMA-F jack   (the cable's SMA-M plug lands on E4,
   v                                    and E4 plugs into the N-female face)
```

No other gender transition exists on this segment. `E1` is male-to-male at both ends; the planned
feedthrough is jack-jack, so the interior and exterior legs need no gender adapter in the base case
- this is the same statement the sibling BOM makes for the whole chain, verbatim:
"No gender-changing adapter exists in the basic chain (M-M cable assemblies, F-F bulkhead). All
connectors standard-polarity SMA, 50 ohm." (`bench/connector-adapter-bom/REPORT.md` STEP 3).

---

## 3. UNVERIFIED inputs - restated inline, not resolved

Rule 5 of the card is honoured literally: every line whose connector identification descends from a
row flagged `UNVERIFIED` or `UNSPECIFIED` in the parent table is kept, annotated
`UNVERIFIED - see open risks`, and restates the conflict inline. Here is the conflict inventory for
this segment, with both candidates retained.

| # | Parent row | What is unresolved | Both candidates (verbatim) |
|---|---|---|---|
| U1 | `IF-7` | **The feedthrough's exterior-face connector family.** No chamber exists on any record, so the face cannot be inspected. | Planned class: SMA-F jack, panel-mount jack-jack, unfiltered - "The planned/procurement feedthrough class is UNFILTERED by construction: an SMA panel-mount jack-jack bulkhead (Amphenol 132134-class per 55585471) is a direct gold-plated contact pair with PTFE dielectric - no filter elements" (`bench/chamber-rf-feedthroughs/REPORT.md` STEP 5). Contradicting possibility: "Exterior-side connector family | UNKNOWN | same - note interior/exterior may differ (e.g. N-exterior/SMA-interior adapter feedthrough); only a physical walk resolves each side separately" (same report, record F1) - carried as line `E4`. |
| U2 | `IF-7` | **The representative bulkhead part number** (consequential for this segment only in that the exterior face's gender is what the cable mates). | "Amphenol 132134-class" (standing BOM / sibling (b)) vs the later sibling correction: "One correction is carried rather than repeated: the standing BOM's 'Amphenol 132134' is a PCB jack, not a panel feedthrough (sibling vendor sheet section 1), so it is not used here as the bulkhead part" (card `t_a53c6efe`, status done). Series/gender/impedance are NOT in conflict - only the representative MPN. No bulkhead part appears on this list (it is the boundary, not a line). |
| U3 | `IF-10` | **The instrument port does not exist.** The far end is the reference TX node (SMA-F jack), document-based; any future bench instrument is UNSPECIFIED. | "NO RF INSTRUMENT EXISTS - the measurement chain has no instrument-side RF connector to identify" and "RF connector | SMA edge-launch, standard polarity, female jack, 50 ohm (same carrier board family as the DUT) | UNVERIFIED for the specific board assigned as reference TX" (`bench/instrument-rf-connectors/REPORT.md`); future case: "Most sub-GHz signal generators and spectrum analyzers present N-type or 3.5 mm connectors (not SMA), which would require SMA-to-N or SMA-to-3.5mm adapters" (same report, caveat 5) - carried as lines `E2`/`E3`/`E6`. |
| U4 | `IF-9` | **The exterior assembly itself does not exist** - MPN TBD by design, and its two ends assume jacks that are themselves unverified. | "MPN TBD - same spec as B1, 0.50 m" (`bench/connector-adapter-bom/REPORT.md` B4) vs the parent's note that the assembly "assumes a female SMA jack at the instrument - see IF-10, where the instrument itself is UNSPECIFIED" and presupposes the exterior face of `IF-7`. Carried on line `E1`. |

Open risks carried from the parent and the siblings, each with its own unblock path - none is
resolved here and none is dropped:

| Risk | Risk on this segment | Source it came from | What unblocks it |
|---|---|---|---|
| R-IF7 | The exterior-face series/gender is UNKNOWN, so line `E1`'s bulkhead-end gender and the need for `E4` are both undecided. | parent `IF-7`; sibling (c) `bench/chamber-rf-feedthroughs/REPORT.md` F1 + `bench/chamber-rf-feedthrough-list/FEEDTHROUGH-LIST.md` FT-1 | Locate the chamber, walk the wall, identify both faces separately (the parent's own remedy: "resolve with the identification kit on first sight"). |
| R-FILTER | A filtered OEM port would be unusable for the RF path regardless of gender. | sibling (c) STEP 5 LOUD FLAG, carried on parent `IF-6`/`IF-7` | Physical check on the located unit: bulky body / feedthrough-capacitor construction / "filtered" marking. |
| R-IF10 | The instrument port is UNSPECIFIED, so the adapter family (`E2`/`E3`/`E6`) is unselected. | parent `IF-10`; sibling (b) caveat 5 | Name/procure an instrument, then select the transition. Buying one now is a guess. |
| R-REFTX | Even the de-facto instrument (reference TX node) is document-based: board not attached, PCB revision not on record. | parent `IF-10`; sibling (b) STEP 2b | Attach the reference TX, read its port, photograph the jack. |
| R-PART | Every MPN on this list is TBD or representative; no inventory system of record exists, so nothing here is confirmed on hand. | sibling BOM R6 / `bench/rf-feedthrough-bom/REPORT.md`; the parent's `IF-9` | Confirm at order time; receiving inspection. |
| R-RP | Reverse-polarity SMA lookalikes are the single most likely wrong-part event on a 868 MHz purchase. | sibling hazard H2 (`bench/connector-adapter-bom/REPORT.md`) | Receiving inspection: the plug must present a center PIN. |
| R-75 | A 75 ohm substitution (video BNC / RG-59 class) is a mismatch, not a transition. | sibling hazard H1 | Verify "50 ohm"/"RG316" literally on the order and on the part. |

---

## 4. DELIBERATELY NOT ON THIS LIST (stated so absence is not read as a gap)

| Excluded item | Why | Owner / where it lives |
|---|---|---|
| The bulkhead feedthrough connector itself (both faces) | It is this card's starting boundary, not a component of the exterior leg. | sibling card `t_fe6e9c1b` (DUT-to-interior + feedthrough) |
| Chamber-interior cable assembly `C-RF-INT-1` and everything inside the chamber | Card step 4: interior items belong to the DUT-to-interior task. | sibling card `t_fe6e9c1b` |
| The chamber wall bore / drilling / sealing hardware | Mechanical penetration, not a connector on this segment; custodian-gated. | sealing section card (`t_a53c6efe`, SEAL-*) |
| Dust caps for the exterior face in the unmated/storage state | Protective accessory, not a signal-path component; owned by a dedicated section card. | terminations/caps section card (`t_436f6657`, TERM-*) |
| Torque wrench, spanners, connector savers, anti-rotation fixtures | Handling tooling for the whole chain, not a component of the exterior leg. | tooling section card (`t_378c5705`, TOOL-*/SAV-*) |
| Tape anchors / loom / cable ID labels for the exterior leg | Consumables governed by the frozen routing spec (`bench/routing-freeze/REPORT.md` §2.2: anchors at T3 plus one per 100 mm of parallel run, polyimide or glass-cloth class; IDs labelled at first touch both ends), not connector-identification BOM lines. No series/gender/impedance applies. | routing freeze `bench/routing-freeze/REPORT.md`; if the consolidator wants consumables in the final BOM, take them from that spec rather than from a connector line. |
| The reference TX's own serial cable `C-SER-2` and the operator workstation end | Outside the DUT-to-instrument chain by the parent's own scope note ("exterior only - never crosses"). | parent `IF-11` note; `bench/routing-freeze/REPORT.md` |
| The USB-C serial crossing `C-SER-1` | Non-RF control-path crossing, not part of this RF segment. | parent `IF-11`; sibling card `t_fe6e9c1b` / sealing section |

---

## 5. ACCEPTANCE SELF-CHECK (against the card's own sentence)

| Acceptance requirement | Status | Evidence |
|---|---|---|
| Every component on this segment appears exactly once with a quantity and a disposition | PASS | 6 rows, unique ids `E1`-`E6`; each carries QTY and a disposition string; the two zero-quantity rows are declared NIL with a reason instead of being dropped. The segment's only signal-carrying hardware is `E1` (firm) plus the three conditional transitions `E2`-`E4`. |
| Every line names series, gender transition, and impedance | PASS | Each `Part number` cell states the connector series, the gender transition, and "50 ohm" (or `N/A` with its reason on the two NIL rows). Checked mechanically by `make_bom.py`. |
| Every connector identification traces to a cited sibling source or is flagged UNVERIFIED | PASS | 6/6 rows carry a citation naming a committed `bench/` path or a parent row id, and 6/6 carry an `UNVERIFIED - see open risks` annotation or a `NIL - reason cited` declaration. Zero rows claim a positive `VERIFIED` status. |
| No component inside the chamber or the bulkhead connector itself is duplicated onto this list | PASS | Section 4 names the feedthrough, `C-RF-INT-1`, the bore/sealing, tooling, caps and the serial crossing as excluded with their owners; no row describes any of them. |

Mechanical check run by `make_bom.py` on every invocation: the 7 header cells match the card's column
list in order; every data row has exactly 7 non-empty cells; every row states an impedance value or
an explicit `N/A`; every row states a gender token or an explicit `N/A`; every row carries a
citation; every row is annotated `UNVERIFIED` or `NIL`; no row claims `VERIFIED`.

---

## 6. NOTHING FABRICATED

No connector series, gender, impedance, frequency rating, VSWR value, MPN, lead time or price on this
list is invented. Every identification is reused verbatim from the parent's normalized interface
table, which itself quotes committed sibling reports; every MPN is `MPN TBD` with the interface spec
the part must satisfy, except the one representative class the record names (Amphenol ACX-1169-class,
labelled representative). No conflict is resolved, no candidate is dropped, no `VERIFIED` status is
granted, and no measurement, photograph, physical inspection or outbound fetch is claimed: no cable,
no chamber, no instrument and no RF connector of this segment exists on any record or on this host.
Quantities of `0-1` mean exactly that - zero today, one if a stated condition materialises.

Reproduce: `python3 make_bom.py` rewrites `EXTERIOR-LEG-BOM.md` and `exterior_leg_bom.csv`
byte-identically (stdlib only; no clock, no randomness, no network), then runs the self-check.
"""


# ------------------------------------------------------------------ emit -----
def render_md():
    out = [TITLE]
    out.append("| " + " | ".join(HEADER) + " |")
    out.append("|" + "|".join([" --- "] * len(HEADER)) + "|")
    for r in ROWS:
        cells = [
            r["rid"] + " - " + r["desc"],
            r["qty"],
            r["spec"],
            r["disp"],
            r["lead"],
            r["vendor"],
            r["cite"],
        ]
        out.append("| " + " | ".join(c.replace("|", "\\|") for c in cells) + " |")
    out.append(TAIL_1)
    return "\n".join(out)


def write_files():
    md = render_md()
    with open(MD, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(md)
    with open(CSV, "w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(HEADER)
        for r in ROWS:
            w.writerow([
                r["rid"] + " - " + r["desc"],
                r["qty"],
                r["spec"],
                r["disp"],
                r["lead"],
                r["vendor"],
                r["cite"],
            ])
    return md


# ------------------------------------------------------------- self-check ----
def selfcheck(md):
    checks = []

    def ck(name, ok, detail=""):
        checks.append((name, bool(ok), detail))

    # 1. columns, in the card's order
    ck("7 header cells present in card order",
       all(h in md for h in HEADER) and len(HEADER) == 7,
       "header cells = %d" % len(HEADER))
    for i, h in enumerate(HEADER):
        ck("header[%d] rendered" % i, h in md)

    # 2. csv twin: same header, same row count, same cells
    with open(CSV, encoding="utf-8") as fh:
        rows = list(csv.reader(fh))
    ck("csv header == mandated header", rows[0] == HEADER)
    ck("csv row count == md row count", len(rows) - 1 == len(ROWS),
       "csv=%d rows=%d" % (len(rows) - 1, len(ROWS)))

    # 3. per-row content checks
    for r in ROWS:
        cells = [r["rid"] + " - " + r["desc"], r["qty"], r["spec"], r["disp"],
                 r["lead"], r["vendor"], r["cite"]]
        ck("%s: 7 non-empty cells" % r["rid"], all(c.strip() for c in cells))
        ck("%s: impedance stated or N/A" % r["rid"],
           ("50 ohm" in r["spec"]) or ("N/A" in r["spec"]))
        ck("%s: gender transition stated or N/A" % r["rid"],
           any(tok in r["spec"] for tok in ("plug", "jack", "N-M", "BNC-M",
                                            "3.5 mm-M", "N/A")))
        ck("%s: citation present" % r["rid"],
           ("bench/" in r["cite"]) or ("t_" in r["cite"]))
        ck("%s: annotated UNVERIFIED or NIL" % r["rid"],
           ("UNVERIFIED" in r["cite"]) or ("NIL" in r["cite"]))
        # No row may claim a POSITIVE verified status. A bare "VERIFIED"
        # substring inside "UNVERIFIED"/"UNSPECIFIED" is not a claim, so those
        # tokens are removed before the probe. (Verifier defect found on the
        # first run: the naive `"VERIFIED" not in spec` test failed E4, whose
        # spec legitimately ends "... UNVERIFIED on host". Fixed here; the
        # deliverable text was correct and is unchanged.)
        stripped = (r["spec"] + " " + r["disp"]).replace("UNVERIFIED", " ").replace("UNSPECIFIED", " ")
        ck("%s: no positive VERIFIED claim" % r["rid"],
           "VERIFIED" not in stripped)

    # 4. uniqueness / contiguity of ids
    ids = [r["rid"] for r in ROWS]
    ck("ids unique", len(set(ids)) == len(ids))
    ck("ids contiguous E1..E%d" % len(ROWS),
       ids == ["E%d" % (i + 1) for i in range(len(ROWS))])

    # 5. boundary: the bulkhead itself must not be a line item
    ck("no row is the bulkhead feedthrough itself",
       not any("bulkhead feedthrough" in r["desc"].lower()
               and "exterior face" not in r["desc"].lower() for r in ROWS))

    # 6. no interior-leg component duplicated onto this list
    ck("no interior-leg assembly listed",
       not any("C-RF-INT-1" in r["desc"] for r in ROWS))

    # 7. determinism: md content is a pure function of ROWS + prose
    ck("md deterministic (render twice equal)", render_md() == md)

    failed = [c for c in checks if not c[1]]
    for name, ok, detail in checks:
        print(("PASS  " if ok else "FAIL  ") + name + ((" :: " + detail) if detail and not ok else ""))
    print("")
    print("checks: %d  pass: %d  fail: %d" % (len(checks), len(checks) - len(failed), len(failed)))
    return 1 if failed else 0


def main():
    md = write_files()
    for p in (MD, CSV):
        with open(p, "rb") as fh:
            print("%s  %s" % (hashlib.sha256(fh.read()).hexdigest(), os.path.basename(p)))
    rc = selfcheck(md)
    return rc


if __name__ == "__main__":
    sys.exit(main())
