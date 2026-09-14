# Chamber feedthrough port survey + mechanical fit of DUT + RF cable

Task (fleet card `meshcore:t_48e048a1`): "Survey chamber feedthrough port and
mechanical fit of DUT + RF cable. GOAL: Establish the physical/mechanical
answer to whether the DUT module and its RF coax can be routed into the
thermal chamber through the existing door gasket and/or feedthrough port
while the chamber is sealed and running setpoints."

Date: 2026-09-14, session 23:3x local (UTC+2) · Repo: meshcore (main) ·
Worker: dq05 (profile worker-heavy) · Host: `c03rad0r-DQ05proplus`.
Artifacts: this directory (`bench/chamber-feedthrough-fit/`).

This is the first worker output for card `t_48e048a1` (fleet state re-read
this session: decision None, no result fields; the committed chamber-feasibility
comment `fe84bf84` lists it as "input 1, undispatched"). This report is the
missing input.

---

## VERDICT SUMMARY

**MECHANICAL FIT: UNKNOWN — blocked entirely on the chamber side.**
No chamber has ever been located or identified (re-verified this session;
sibling cards dispatched tonight concur: chamber-nameplate `24eb918c`
BLOCKED, chamber-controller `766ac96d` UNKNOWN, chamber-holds `72f3aab9`
UNVERIFIED). There is no penetration to enumerate, no port to measure, no
gasket to characterize. Every chamber-side row below is UNKNOWN for that
reason — not for lack of trying (attempts in Appendix A).

**What IS established (all sourced, this report's contribution):**

1. The DUT side is fully dimensioned from on-record sources: module
   19.72 x 15.05 mm [datasheet/citation chain below], carrier-board family
   75 x 55 x 0.8 mm [KiCad Edge.Cuts + thickness + silkscreen], antenna =
   wire dipole 8.6 cm legs or SMA stub, serial = USB-C cable. Nothing on the
   DUT side is oversized: the board fits any freezer/chamber door opening by
   an order of magnitude (door opening itself UNKNOWN — chamber unidentified;
   the claim is an engineering inference from the DUT dimensions, labeled as
   such).
2. **The primary edgescan protocol requires NO RF penetration at all** (fork
   README `d7ae93fa`: reference TX at room temperature outside, DUT inside,
   over-the-air; `thermal_bench.py scan_edges()` counts decoded packets).
   The ONLY thing that must cross the sealed boundary in the primary path is
   **one USB-C serial cable**.
3. The optional conducted path adds one RG316 coax (OD 2.50 mm nominal,
   industry standard — no vendor datasheet on host, UNVERIFIED for a specific
   part) and is best served NOT by a big cable port but by an **SMA bulkhead
   feedthrough in a 6.5 mm panel hole** — this project's own documented
   wall-pass-through pattern (`enclosure/README_big.md`: "Two SMA bulkhead
   holes (6.5mm) ... Fully waterproof with SMA O-rings").
4. A fit-decision table (Step 3 below) converts to instant PASS/FAIL the
   moment any chamber port is measured: port ID vs the computed thresholds —
   no re-analysis needed.
5. Sealing: a round cable crossing a flat door gasket always leaves a leak
   path (no gasket compression on the cable footprint); at -20/-40 C that
   leak continuously feeds humid lab air to a surface 22-57 C below the dew
   point (condensation-risk `65c9c3df`) → frost at the crossing, progressive
   gasket jacking, degrading seal. Glanded/bulkhead penetrations preserve the
   seal; drilling requires the identified chamber + custodian approval.

**What is too big / what blocks:** nothing on the DUT side is too big. The
blocker is the absence of the chamber itself. The largest rigid item that
must cross the boundary in the primary path is the USB-C connector overmold
(wider than a 6.5 mm SMA-bulkhead-class bore; exact overmold width has NO
on-record source — measure at run time), which forces one of: door-gasket
crossing (seal degraded), a drilled port sized to the measured overmold, or
a USB-C panel-mount bulkhead coupler (BOM report `55585471` already lists
this as the conditional serial feedthrough).

---

## STEP 1 — Penetration inventory (every available penetration)

Per the card: dedicated feedthrough port(s), door gasket pass-through,
unused bulkhead holes, cable boot. Chamber never located → **no penetration
of any class was observed, measured, or ruled out.** All rows UNKNOWN:

| ID | Penetration class | Location | Inner diameter (mm) | Occupied? | Status | Reason |
|----|-------------------|----------|--------------------|-----------|--------|--------|
| P1 | Dedicated feedthrough port | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | No chamber located; no make/model/serial on any record (chamber-ownership `11e43b0a`/`4b3ec9b5`, nameplate `24eb918c` BLOCKED tonight) |
| P2 | Door gasket pass-through | UNKNOWN | UNKNOWN (gasket geometry UNKNOWN: thickness, width, durometer, compression) | UNKNOWN | UNKNOWN | Same — no door exists on record to inspect |
| P3 | Unused bulkhead holes | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | Same |
| P4 | Cable boot(s) | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | Same |
| P5 | Spare flange / blank cutouts | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | Same |

No row can carry a measured value: there is no physical subject. The
sourcing rule of sibling card `t_f2b50f53` (no estimated diameters, every
unmeasured value UNKNOWN with reason) is followed exactly. What would
produce these rows: one site visit with calipers/tape to an identified unit
(see Unblock path).

---

## STEP 2 — Coax slack, bend radius, swept envelope

### 2a. What coax exists

**None on hand, none on record.** No RF cable is inventoried anywhere in the
repo or on this host (BOM report `55585471` "Unknown (not on any record)";
USB census this session: 2x CH340, Pi Debugprobe, RTL8152, microSD,
audio/HID/hubs — no cable, no connectors, no instruments). The conducted
path exists only as a procurement plan (RG316, 0.15 m + 0.5 m).

### 2b. RG316 dimensions and minimum bend radius (planning values, bases labeled)

| Parameter | Value | Source label |
|---|---|---|
| Jacket OD | 2.50 mm nominal | INDUSTRY NOMINAL (RG316 spec class; cited as "RG316, OD 2.5mm" in BOM report `55585471` step 3b; no vendor datasheet on host — UNVERIFIED for a specific part) |
| Min bend radius, static | 12.7 mm (0.5 in) | INDUSTRY NOMINAL — UNVERIFIED (no vendor datasheet on host; no outbound fetch performed this session per operator constraint) |
| Min bend radius, rule-of-thumb alt. | 10 x OD = 25.0 mm | RULE OF THUMB (commonly quoted coax guidance; basis stated, UNVERIFIED) |
| Dielectric | PTFE, rated to -65 C or lower | condensation-risk `65c9c3df` section 3b ("PTFE ... rated to -65 C or lower") |
| Cable-to-cable tolerance at -20/-40 C | jacket stiffening affects forced bends | analysis card `t_d5ff2595` (undispatched); PTFE Tg -97 C per `65c9c3df` |

The bend radius numbers are the ONLY figures in this report not traceable to
a file on host or a committed report; they are labeled accordingly and are
planning inputs, not measurements. **Replace with the procured part's
datasheet value before relying on them.**

### 2c. Available slack

UNMEASURABLE — no chamber, no instrument, no routed cable. In-chamber free
length, exterior free length, and tightest forced bend are all UNKNOWN until
a chamber is located and the routing frozen (sibling card `t_e5d5eaae`
defines the routing-freeze step; undispatched).

### 2d. Swept-envelope requirement (arithmetic shown, per card acceptance)

For a coax entering a bulkhead bore and turning 90° toward the DUT, with
bend radius R and cable OD t, the swept envelope at the interior wall face
is a circle of diameter 2R + t, and the turn needs R + t/2 of clearance from
the port face:

- RG316 at R = 12.7 mm, t = 2.5 mm:
  swept diameter = 2(12.7) + 2.5 = **27.9 mm**;
  clearance from port face = 12.7 + 1.25 = **13.95 -> ~14 mm**.
- RG316 at the 10xOD rule R = 25.0 mm:
  swept diameter = 2(25.0) + 2.5 = **52.5 mm**; clearance = 25.0 + 1.25 =
  **26.25 mm**.

Interior clearance available: UNKNOWN (chamber unidentified — no interior
dimensions on record). The requirement above is what the chamber must
provide near the port for a 90° coax turn; an axial exit with the first bend
farther inside relaxes it.

---

## STEP 3 — DUT envelope and bundle cross-section vs port diameter

### 3a. DUT module with enclosure/harness (every dimension sourced)

The DUT is SkyMapper Board A: ESP32-C3 SuperMini + NiceRF LR2021,
SMA edge-launch RF ports, USB-C serial (resource `c3-a`,
MAC b0:a6:04:00:96:dc — `balloon-board-lock.py` resource map). Protocol
enclosure = **a sealed bag around the module** (fork README `d7ae93fa`
verbatim, "Playback notes from the mule"), not a rigid case; the balloon
dev-case is a different assembly and is used here only as a dimension source.

| Item | Dimension | Source |
|---|---|---|
| NiceRF LR2021 module | **19.72 x 15.05 mm** | BOM report `55585471` (citing NiceRF LoRa2021 datasheet V1.3 Pin Definition section, downloaded in that session); corroborated `enclosure/README.md` variant A "NiceRF LoRa2021 bare module (19.72x15mm)". Skill reference `nicerf-lora2021f33-pinout.md` gives **19.81 x 14.98 mm** (revision discrepancy, 0.09/0.07 mm) — bounding value used for fit: **19.81 x 15.05 mm** |
| Module antenna interface | castellated PCB pads, pin 9 ANTA (sub-GHz), pin 10 2.4/S_ANTA — no connector on the module | BOM report `55585471` citing datasheet V1.3 |
| Carrier board (family) | **75 x 55 mm, 0.8 mm thick, 2-layer** | `hub_board_f33.kicad_pcb`: Edge.Cuts `gr_rect (start 0 0) (end 75 55)`; `(thickness 0.8)`; B.SilkS text "JLCPCB 2-layer 0.8mm" — CAVEAT: SkyMapper Board A PCB not read directly (same caveat as BOM report #1); family file |
| RF connectors on carrier | 2x SMA end-launch, J1 "SMA-868" at (2, 28), J2 "SMA-2G4" at (73, 28) — i.e. ~2 mm inboard of each 55-mm edge, ~mid-height | `hub_board_f33.kicad_pcb:165-181`, footprint `custom:SMA_Edge_Mount`; independently confirmed in prose by condensation-risk `65c9c3df` line 305 ("SMA edge-launch connector") |
| ESP32-C3 SuperMini | 22.52 x 18 mm | `enclosure/README.md` ("esp_w = 22.52") and `balloon_dev_case.scad` parameter block |
| Antenna (in-chamber, primary path) | wire dipole, 8.6 cm legs, or SMA stub | balloon repo `IMPLEMENTATION-PLAN.md:41` (via BOM report `55585471`) |
| Serial cable | USB-C (SuperMini native USB-CDC), 115200 8N1, `/dev/ttyACM0` | fork README `d7ae93fa` "Bench setup" table |
| Module height / tallest protrusion | UNKNOWN | no height datum on any record (datasheet page images on disk not machine-readable this session; no vision tool bound); shield-can height must be measured with calipers at run time |

Effective DUT envelope for door/port transit: the **carrier board
75 x 55 x 0.8 mm bare** (plus SMA connector bodies at both 55-mm edges and
the SuperMini's ~22.5 x 18 mm footprint with USB-C overmold protruding at
one edge — protrusion heights UNKNOWN) inside a sealed bag adding a few mm
per side. The module-only alternative is 19.81 x 15.05 mm.

### 3b. What must cross the sealed boundary, per protocol variant

**Variant A — primary edgescan (over-the-air):** DUT + antenna inside;
reference TX outside at room temperature; measurement is decode-count, not
RF power. Crossing the boundary: **1x USB-C serial cable ONLY.**
(Fork README `d7ae93fa` Bench-setup table; `thermal_bench.py scan_edges()`
reads decoded-packet counts over the DUT CLI; BOM report `55585471` step 2.)

**Variant B — optional conducted path:** DUT SMA -> RG316 -> SMA bulkhead
feedthrough -> RG316 -> reference TX/instrument outside; plus the same
USB-C serial cable. Crossing: 1x RG316 coax + 1x USB-C cable.

### 3c. Bundle cross-sections (computed; bases labeled)

Single-cable and bundled equivalent diameters (two tangent circles a and b
taped side-by-side: envelope = a+b wide x max(a,b) high; equivalent OD =
sqrt((a+b)^2 + max(a,b)^2); +0.5 mm loom):

| Bundle | Composition | Computation | Equivalent OD |
|---|---|---|---|
| A (primary) | 1x USB-C cable, OD 4.0-5.0 mm [INDUSTRY-TYPICAL, UNVERIFIED — no cable on hand, no spec on record; MEASURE] | single cable | **4.0-5.0 mm** |
| B, separate penetrations | RG316 (2.50 mm) alone; USB-C alone | single cables | **2.5 mm** / 4.0-5.0 mm |
| B, jointly taped | RG316 + USB-C (4.5 mm midrange) | sqrt(7.0^2 + 4.5^2) = 8.32; +0.5 loom | **~8.8 mm** (9.5 mm if USB-C OD is 5.0) |

Connector-pass constraint (the connector, not the cable, sizes the bore if
the cable cannot be cut and re-terminated):

| Rigid item crossing | Across-flats / overmold | Bore it needs | Basis |
|---|---|---|---|
| USB-C plug overmold | ~9-12 mm wide, 3-6 mm thick | ≥ overmold width (measured) → practically **≥ 12-13 mm** | INDUSTRY-TYPICAL, UNVERIFIED — no USB-C overmold dimension on any record; measure before drilling |
| SMA male connector, hex nut | 5/16 in = 7.94 mm across flats, 9.17 mm across corners | ≥ ~9.5-10 mm if the mated connector must pass the bore | INDUSTRY-STANDARD SMA, UNVERIFIED on host |
| Bare RG316 (no connector) | 2.50 mm OD | ≥ 3.0 mm at 20% clearance (1.2 x 2.5) | computed from nominal OD |

### 3d. FIT-DECISION TABLE — port ID thresholds (the numbers a measured port must beat)

Once a real penetration is measured (ID = P, inner diameter), the fit is
decided by comparison — no re-analysis:

| Path / item | Min bore, cable only | Min bore, connector passes | Recommended penetration instead |
|---|---|---|---|
| A: USB-C serial (primary, mandatory) | ≥ 6.0 mm (1.2 x 5.0) | ≥ measured overmold (~12-13 mm, UNVERIFIED) | (1) door-gasket crossing (seal degraded — Step 4); (2) drilled port + cable gland sized to measured overmold; (3) USB-C panel-mount bulkhead coupler (standard hardware; BOM `55585471` row 3 "USB bulkhead feedthrough ... Conditional") |
| B: RG316 RF (optional) | ≥ 3.0 mm | ≥ ~9.5-10 mm (SMA nut) | **SMA bulkhead feedthrough in a 6.5 mm panel hole** — the project's own documented pattern (`enclosure/README_big.md`: "Two SMA bulkhead holes (6.5mm) ... Screw SMA connectors through from outside ... Fully waterproof with SMA O-rings"); the feedthrough IS the penetration, connector never passes through a bore |
| Antenna-in-chamber (primary) | n/a — nothing crosses; wire dipole/stub lives inside | n/a | none (over-the-air through the wall; if the wall is metal, OTA fails → variant B becomes mandatory — BOM `55585471` step 5 caveat) |

Interior-side requirement for variant B: the 90°-turn swept envelope of
27.9-52.5 mm diameter (Step 2d) must fit the chamber's interior clearance
near the port — UNKNOWN until the chamber is identified.

### 3e. Module through door vs through port

- **Module/board through the DOOR (open, then closed with cable(s)
  crossing):** 75 x 55 x 0.8 mm board in a sealed bag passes any door or lid
  opening of any freezer/chamber class [engineering inference — door opening
  itself UNKNOWN; no on-record door dimension]. FIT: expected trivially
  PASS, unverifiable until a unit exists.
- **Module through a PORT:** irrelevant — the module is placed inside via
  the door; only cables cross the sealed boundary (per protocol; fork
  README places the DUT inside and the reference TX outside).

---

## STEP 4 — Door sealing with cable crossing, and thermal-stability impact

**Can the door still seal with the cable crossing the gasket?**
Chamber-specific answer UNKNOWN (no gasket on record to test). The
conditional engineering answer, per penetration strategy:

1. **Cable crossing the door gasket (no drilled port):** a rigid round cable
   crossing a flat/ profile gasket prevents full gasket compression on the
   cable's footprint → **a leak path is certain** (gasket geometry UNKNOWN:
   compression, durometer all UNKNOWN). Consequences at the -20/-40 C
   setpoints, from the established physics in condensation-risk `65c9c3df`:
   - **Air exchange:** the leak continuously feeds warm humid lab air to the
     cold side; in every lab-ambient cell (20-25 C, 30-60 % RH) the cold side
     sits 22-57 C below the dew point, so the infiltrating moisture
     condenses and freezes AT the crossing.
   - **Frost growth at the crossing:** ice accumulation progressively
     jacks the gasket open (positive feedback) over a multi-hour session,
     worsening both the leak and the local thermal load.
   - **Cold-bridge:** the cable's copper conductors short the cold interior
     to the warm exterior face (`65c9c3df` section 2b mechanism — the
     exterior feedthrough face settles below the lab dew point); frost on
     the warm-side face is CERTAIN without mitigation (feedthrough heater
     +15 C recommended, `65c9c3df` section 4c).
   - A magnetic-latch freezer gasket (a candidate class; actual class
     UNKNOWN) additionally loses magnetic contact over the cable footprint.
2. **Drilled port + cable gland (e.g. PG-class, the project's own documented
   gland pattern — `enclosure/README.md` "3x cable gland holes (6mm)",
   PG7 glands):** door seal untouched; the gland seals on the cable OD
   (4.0-5.0 mm USB-C is inside a PG7-class clamping range [INDUSTRY-TYPICAL,
   UNVERIFIED] — BUT the USB-C connector overmold does NOT pass a PG7 nut
   bore; the gland must be sized to the measured overmold, or a
   connector-less cable + bulkhead coupler used). Wall drilling requires the
   identified chamber and custodian approval (chamber custodian: Felix,
   MEDIUM, chamber-ownership `4b3ec9b5`) — a human gate, not an agent
   action.
3. **SMA bulkhead feedthrough (variant B RF path):** 6.5 mm hole, O-ring
   sealed — the project's own documented fully-waterproof wall-pass pattern
   (`enclosure/README_big.md`). Preserves door seal; no cable crosses the
   gasket; the feedthrough itself is the cold-bridge and carries the
   condensation/frost exposure already assessed in `65c9c3df` (REQUIRED
   desiccant + sealed DUT bag; RECOMMENDED feedthrough heater, conformal
   coating/boots).

**Thermal-stability net effect:** gasket-crossing = uncontrolled air
exchange + local thermal load + certain frost at the crossing (worst case
for a stability-sensitive measurement); glanded/bulkhead penetrations =
door seal preserved, leak eliminated, residual cold-bridge managed by the
`65c9c3df` mitigations. The chamber's actual gasket compression and seal
quality are UNKNOWN — quantify only after the chamber is identified.

---

## STEP 5 — Routing sketch (reconstructed; NOT drawn from a physical chamber)

**Photographs: impossible.** No camera device on this host — `/dev/video*`
absent (verified this session: "No such file or directory"), no V4L2
subsystem, no UVC device in the USB census; the one HID/audio composite
(0573:1573) had its video capability unprobed (operator denied the sysfs
probe in the nameplate session tonight, `24eb918c` — not retried). There is
also no physical subject: no chamber located. Sketch below is reconstructed
from on-record dimensions only; every number's source is tagged.

### Variant A — primary edgescan (over-the-air): only USB crosses

```
                 OUTSIDE (lab, ~20-25 C)                 |CHAMBER WALL      |   INSIDE (setpoint -40..+25 C)
                                                       |(material,        |
                                                       | thickness, gasket|   ALL UNKNOWN - no unit located)
                                                       | geometry UNKNOWN) |
                                                          |
   host c03rad0r-DQ05proplus ==USB-C======================|==================c3-a  SkyMapper Board A
   /dev/ttyACM0 (Pi Debugprobe TODAY, not DUT;           |  crossing point  |  [carrier 75x55x0.8 mm, KiCad
   DUT absent from host per USB census)                   |  = P2 door-     |   Edge.Cuts/thickness; SMA J1/J2
                                                          |   gasket or a    |   at 55-mm edges, 2 mm inboard]
   reference TX (c3-b or any MeshCore node)               |   drilled+glanded|      |
   868 MHz SF8/BW62.5, ROOM TEMP                          |   port P? [ID    |      +-- wire dipole 8.6 cm legs
   (never frozen - warm-TX/cold-RX model)  ~~~~ OTA ~~~~~>|   UNKNOWN]       |      |   [IMPLEMENTATION-PLAN.md:41]
   868 MHz RF crosses the WALL ITSELF, not a port          |                  |  sealed bag around the module
                                                           |                  |   [fork README d7ae93fa verbatim]
   NO RF cable, NO RF feedthrough in this variant          |                  |
```

### Variant B — optional conducted path: SMA bulkhead feedthrough (recommended)

```
   OUTSIDE                                                 |    |    INSIDE
                                                           |    |
   reference TX / instrument --RG316 0.5 m--[SMA m]--(SMA bulkhead feedthrough, 6.5 mm panel hole,
                                                           |    |  O-ring sealed - enclosure/README_big.md)
                                                           |    |     |
   host ==USB-C=============================================|====|=====c3-a SkyMapper Board A, J1 "SMA-868"
   (USB-C gasket crossing or glanded port, as variant A)   |    |      |
                                                           |    |   RG316 0.15 m [SMA m]-- first bend >= R=12.7 mm
                                                           |    |   swept envelope 2R+t = 27.9 mm at the turn
                                                           |    |   [R: industry nominal, UNVERIFIED - Step 2b]
```

Sketch caveats: wall/gasket/port icons are placeholders (no chamber);
interior clearances, door size, and gasket profile are UNKNOWN; the DUT-side
geometry (board, connectors, antenna, bag) is to scale in mm per the sources
in Step 3a, everything else is schematic.

---

## Source summary

| Claim | Source | Confidence |
|---|---|---|
| Chamber unidentified; no penetration exists on any record | chamber-ownership `11e43b0a`/`4b3ec9b5`; chamber-nameplate `24eb918c` (BLOCKED, tonight); chamber-controller `766ac96d`; chamber-holds `72f3aab9`; fleet state re-read this session (all locate/identify cards resultless) | HIGH (5 independent reports, re-verified) |
| Primary edgescan is over-the-air; ref TX outside at room temp; only serial crosses | fork README `d7ae93fa` "Bench setup"; `thermal_bench.py scan_edges()`; BOM `55585471` | HIGH |
| LR2021 module 19.72 x 15.05 mm (bounding 19.81 x 15.05) | BOM `55585471` (datasheet V1.3); `enclosure/README.md` variant A; skill ref `nicerf-lora2021f33-pinout.md` (19.81 x 14.98) | HIGH (3 text sources; 0.09 mm cross-source spread noted) |
| Carrier board family 75 x 55 x 0.8 mm; SMA J1/J2 at 55-mm edges | `hub_board_f33.kicad_pcb` Edge.Cuts, thickness, footprint at (2,28)/(73,28); corroborated `65c9c3df:305` | HIGH for the family file; MEDIUM for Board A specifically (PCB not read directly — BOM caveat #1 carried forward) |
| ESP32-C3 SuperMini 22.52 x 18 mm | `enclosure/README.md` + `balloon_dev_case.scad` | HIGH |
| SMA bulkhead wall-pass pattern: 6.5 mm hole, O-rings, "fully waterproof" | `enclosure/README_big.md` "SMA Antenna Pass-Through" | HIGH (documented project design number) |
| Cable-gland wall-pass pattern: 6 mm holes, PG7 glands | `enclosure/README.md` | HIGH (same) |
| Wire dipole 8.6 cm legs | `IMPLEMENTATION-PLAN.md:41` via BOM `55585471` | MEDIUM (carried from BOM report) |
| RG316 OD 2.50 mm; min bend R 12.7 mm static; 10xOD alt | INDUSTRY NOMINAL — no vendor datasheet on host, no outbound fetch (operator constraint); BOM `55585471` cites the OD as nominal | LOW-MEDIUM planning inputs, UNVERIFIED — replace with procured part datasheet |
| USB-C cable OD 4.0-5.0 mm; overmold ~9-12 mm | INDUSTRY-TYPICAL, UNVERIFIED — no cable or spec on record | LOW — measure at run time |
| Frost/condensation certain at -20/-40 C; cold-bridge mechanism; mitigations | condensation-risk `65c9c3df` (Magnus grid, Zones, sections 2b, 4a-4d) | HIGH (committed, reproducible script) |
| No camera on host | `/dev/video*` absent (this session); no UVC in USB census; `24eb918c` (video-capability probe operator-denied, not retried) | HIGH |
| No DUT, no RF instrument, no coax on host | USB census this session (2x CH340, Pi Debugprobe as /dev/ttyACM0 via udevadm, RTL8152, microSD, audio/HID) | HIGH |
| Chamber custodian Felix (drilling approval would be his gate) | chamber-ownership `4b3ec9b5` (MEDIUM) | MEDIUM (carried forward) |

---

## Caveats and honest gaps

1. **Every chamber-side dimension is UNKNOWN** and will remain so until a
   unit is physically located. Nothing in this report should be read as a
   chamber property.
2. **The two industry-nominal figures** (RG316 OD and bend radius, USB-C
   OD/overmold) are the only unsourced numbers, and they are labeled
   INDUSTRY NOMINAL/TYPICAL + UNVERIFIED wherever used, and appear only in
   threshold math whose inputs are to be replaced with measured/datasheet
   values. No measured value was invented.
3. **SkyMapper Board A PCB was not read directly** (carried caveat from BOM
   report #1); board dimensions are from the family PCB file and are labeled
   family-level.
4. **Module height is UNKNOWN** — no height datum on any record; measure
   with calipers when the module is provisioned (it is not attached to any
   fleet host).
5. The fit-decision table assumes the primary protocol (OTA); if the
   chamber turns out to be a metal-walled unit, OTA fails and variant B
   becomes mandatory (BOM `55585471` step 5) — the table already covers it.
6. Photos impossible (no camera, no subject); the sketch is a
   reconstruction from cited dimensions, labeled as such.

---

## Unblock path (exact, ordered)

1. Locate the chamber (cards `t_a2f7f281`/`t_b09424f1`/`t_ffc911f6` —
   all resultless tonight; requires a human to name the unit + location).
2. One site visit with calipers + flexible tape + camera: measure every
   penetration (IDs P1-P5 rows above; protocol defined by sibling card
   `t_f2b50f53`/`t_03954030`), gasket cross-section, door opening, interior
   clearances, and wall material/thickness (metal vs non-metal decides OTA
   vs conducted).
3. Compare measured port IDs against the Step 3d fit-decision table →
   instant PASS/FAIL per item.
4. Measure the actual USB-C overmold and the procured RG316 datasheet bend
   radius; replace the UNVERIFIED planning inputs.
5. If drilling is required: custodian approval (Felix, chamber-ownership
   `4b3ec9b5`) — human gate.
6. Apply `65c9c3df` mitigations before any sub-zero setpoint (desiccant,
   sealed DUT bag, optional N2 purge, feedthrough heater).

---

## Nothing fabricated

No penetration, port diameter, gasket property, door dimension, or chamber
attribute was invented — every such field is UNKNOWN with the reason. All
DUT-side and cable-side dimensions are cited to files read this session
(KiCad PCB, enclosure READMEs, balloon IMPLEMENTATION-PLAN.md, board-lock
resource map, committed bench reports, skill reference, fork README via
`git show`). The four industry-nominal planning figures are explicitly
labeled UNVERIFIED. No photograph is claimed. The USB census (DUT absent,
/ttyACM0 = Pi Debugprobe) was re-run this session via `lsusb` + `udevadm`.