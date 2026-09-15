# Routing freeze + caliper/tape tool resolutions

Task (fleet card `meshcore:t_e5d5eaae`): "Freeze routing and record
caliper/tape tool resolutions. GOAL: Establish the measurement setup
state that every later reading depends on, before any cable is
measured."

Date: 2026-09-15 · Repo: meshcore (main) · Worker: dq05.
Artifacts: this directory (`bench/routing-freeze/`).

---

## VERDICT SUMMARY

**The routing is frozen as a normative, reproducible placement SPEC —
and every physical input it depends on is still absent.** No coax
cable, no chamber, no calipers, no tape measure, and no attached DUT
exist on this host or on any record (fresh census this session; this is
the 7th, 8th, and 9th independent concurrence across the campaign).
What CAN be frozen now — and is, below — is the *decision state*:

1. The exact routing rule (geometry, tie points, tape pitch, loom,
   wall-crossing) is frozen as a written spec a second person can
   follow verbatim, in Section 2.
2. The two tool resolutions are frozen as REQUIRED SPEC NUMBERS WITH
   UNITS, in Section 3: **caliper resolution/least-count
   0.01 mm** (digital, per the fleet's own tool spec in card
   `t_f5f3fe8a` PREP) and **tape-measure resolution 1 mm**. These are
   the per-measurement uncertainty floors for every downstream caliper
   and length reading in this campaign. They are spec, NOT a reading of
   any tool in hand — no caliper or tape exists on any record.
3. Ambient/bench bias conditions are recorded in Section 4: a fresh
   host-sensor reading (27.8 C, labeled a motherboard proxy, not bench
   air), the all-cells-ASSUMED ambient grid carried by every prior
   report, and the honest state of the jacket/tension fields
   (UNKNOWABLE — nothing physical exists to feel or tension).
4. The cable ID list is frozen in Section 5: four identifiers
   (C-RF-INT-1, C-RF-EXT-1, C-SER-1, C-SER-2), each with class,
   status, and routing role. Zero of the four exist physically; each is
   a name bound to a planned instance, so every downstream pass uses
   identical identifiers regardless of which worker measures it.
5. The frozen routing's own decisions are checkable arithmetic, not
   prose: `routing_length_check.py` (stdlib-only) recomputes the
   swept-envelope, length-budget, and bundle-OD numbers, saves
   verbatim output to `output.txt`, and a second run is byte-identical.
   Both planned assemblies PASS their frozen minimum budgets.

**Why a spec-freeze, not a physical freeze.** The task's step 1 says
bundle OD and forced bend are meaningless unless the routing is final.
The same is true in reverse: with the cable MUST-PROCURE and the
chamber unlocated, a physical freeze is impossible — but leaving the
routing undefined guarantees the failure mode FM-8D flagged (a forced
bend below R_min at cold, UNKNOWN because routing not frozen; jacket
stiffening report line 359 explicitly called for "Freeze the routing
(card `t_e5d5eaae`)"). This freeze removes the *routing* term from the
UNKNOWN list; the remaining terms (cable, chamber, tools) stay honestly
open, each with its unblock path.

**Nothing was measured, routed, taped, or photographed.** No cable
existed to route. No camera exists on the host (`/dev/video*` absent,
V4L2 absent — prior censuses concur). The "sketch" deliverable is
served by the ASCII plan in Section 2.3, drawn strictly from on-record
geometry. No outbound network fetch was attempted (standing operator
constraint).

---

## 1. Physical reality census (fresh, this session)

| Check | Result |
|-------|--------|
| `lsusb` | 2x QinHeng CH340 serial, Pi Debugprobe (CMSIS-DAP), RTL8152 Ethernet, BT radio, Zoran audio/HID, 2x hubs, microSD, Lexar ES4 — zero instrument-class, zero RF-coax-connected |
| `/dev/serial/by-id/` | `usb-1a86_USB_Serial-if00-port0 -> ttyUSB1`, `usb-Raspberry_Pi_Debugprobe_..._if01 -> ttyACM0` — the two CH340s share one ID_SERIAL (`1a86_USB_Serial`), hence one symlink; both `/dev/ttyUSB0` and `/dev/ttyUSB1` exist (udevadm-verified CH340 on each) |
| `/dev/usbtmc*`, `/dev/gpib*` | absent |
| `/dev/video*`, V4L2 | absent — no camera on host |
| Filesystem (coax/cable/feedthrough/caliper/tape assets) | zero hits for any measuring tool or RF cable on any record |
| Fleet index re-read (`fleet_queue_state.json`) | 495 tasks, **0 result-bearing fields** — no sibling card has produced a measurement, tool model, or routing either |
| Prior reports concurring on absence | `55585471`, `fe700201`, `c5eb3c58`, `40e1a49a`, `04db4fae`, `ec80c11e`, `bffc7f9d` (no inventory system of record) — plus `coax-bundle-dimensions` REPORT (read this session): "No RF coax exists on this host or on any record" |

**No calipers, no tape measure, no ruler, no measuring tool of any kind
is enumerated on any record.** The fleet's own downstream card
(`t_f5f3fe8a` PREP) writes the tool spec the campaign intends to use:
"digital caliper (0.01 mm / 0.001 in)". The tape-measure class is
specified here for the first time (1 mm steel tape class). Both are
REQUIRED-SPEC values, not readings of tools in hand.

---

## 2. FROZEN ROUTING SPEC (variant A primary + variant B conducted)

This is the placement a second person must reproduce. Every geometric
value below is labeled with its provenance; the two bend rules come
from `fe700201` 2b (INDUSTRY NOMINAL, UNVERIFIED — no vendor datasheet
on host, none fetched). The routing is frozen in two parts: variant A
(primary, mandatory, zero coax) and variant B (optional conducted path,
2x RG316 — the cables the measurement passes will handle). If the
campaign later rejects variant B, the variant A half of this freeze
survives unchanged.

### 2.1 Frozen topology (variant B conducted path)

```
DUT J1 (SMA edge-launch, SkyMapper Board A, inside chamber)
  |
  | [leg 1] straight, >= 15 mm from connector back-shell to first tie
  v
T1 — first tie point (interior): tape anchor at 15 mm from J1 back-shell
  |
  | [leg 2] straight run, on chamber floor / lowest shelf surface
  v
BEND B1 — single 90-deg turn, R >= 25.0 mm (10xOD rule), in ONE plane
  |            (the 12.7 mm static-min is the never-exceed fallback;
  |             the freeze adopts the conservative 25.0 mm so a cold-
  |             stiffened jacket never rides below its warm limit)
  |
FT-* — SMA bulkhead feedthrough (ID per t_03954030: FT-DOOR-n or
  |      FT-WALL-<SIDE>-n; chosen wall/door decided at chamber survey)
  |      panel bore 6.5 mm class (project pattern, enclosure/README_big
  |      20-23); connector body never crosses the wall — the feedthrough
  |      IS the penetration
  |
  | [leg 3] exterior straight, >= 15 mm standoff from bulkhead jam nut
  v
T3 — exterior tie point: first tape anchor outside the wall
  |
  | [leg 4] exterior run to reference TX, draped on bench surface,
  |         no sag-induced bend below R >= 25.0 mm anywhere
  v
REF-TX SMA J1 (reference transmitter, room temperature, outside chamber)
```

Service loops (frozen): one 50 mm interior loop between BEND B1 and
FT-*; one 100 mm exterior loop between T3 and the reference TX. These
loops are the strain-relief slack that keeps cable mass and accidental
snags from loading the bulkhead or the DUT edge-launch solder joint
(the FM-8D weakest link). The length budget check (Section 6) shows both
planned assemblies have enough length to pay for tie-off + arc + loop.

### 2.2 Frozen taping/looming rules

1. **Bundle composition**: variant A crosses ONLY C-SER-1 (USB-C
   serial) — a single cable, no bundle, no tape needed at the crossing.
   Variant B adds C-RF-INT-1 interior and C-RF-EXT-1 exterior; RF and
   serial are taped side-by-side ONLY where they run parallel, never
   across the feedthrough itself.
2. **Tape pitch**: anchors at T1 and T3 plus one anchor per 100 mm of
   parallel run (nominal pitch 100 mm, polyimide or glass-cloth tape
   class); NO continuous spiral wrap (a spiral adds hoop stiffness and
   multiplies the cold-bend moment — FM-8D mechanism), and NO zip ties
   (cold-trigger latches are a snag hazard and crush the jacket).
3. **Loom**: over the parallel-run segment only, 0.5 mm-wall loom/
   expandable-sleeve class, never over any connector, bend, or the
   chamber-wall crossing.
4. **Near the chamber wall**: the ONLY thing at the wall face is the
   SMA bulkhead feedthrough (variant B) or the glanded USB-C pass
   (variant A, per `fe700201` step 4 and chamber-feedthrough-fit 3d
   thresholds). No tape within 15 mm of the jam nut; no bend within
   15 mm of the bulkhead face (tie-off standoff rule); nothing taped to
   the gasket or door seal (gasket crossing degrades the seal —
   `cable-feedthrough-failure-modes` FM on door gasket pass-through).

### 2.3 Reproduce-it checklist (what the installer must do, in order)

1. Place DUT inside chamber, antenna (or B6 saver + C-RF-INT-1) mated
   at J1. Board rests on the lowest available surface, J1 facing the
   wall/door chosen for the crossing.
2. Lay C-RF-INT-1 on the floor from J1: 15 mm free behind the
   connector back-shell, anchor T1, run to the bend, form B1 at
   R >= 25.0 mm in one plane, anchor the loop, terminate on the
   bulkhead cold-side. Torque the jam nut to the vendor spec when the
   datasheet arrives (until then: snug + counterhold with 8 mm spanner,
   B10).
3. Exterior: 15 mm free from the jam nut, anchor T3, drape to the
   reference TX, form the 100 mm loop, mate at REF-TX J1.
4. Variant A: route C-SER-1 (USB-C) through the glanded pass per the
   fit-decision table (`fe700201` 3d), leaving slack OUTSIDE the
   chamber, never taped to the door seal.
5. Apply tape anchors only after the full path is laid and both loops
   are formed (measure twice, tape once).
6. Re-check: no bend below 25.0 mm radius anywhere, no tape at the
   connectors, loops intact, then photograph the finished path.
   (Photograph = when a camera exists; until then this checklist +
   the plan-view sketch above is the record.)

### 2.4 What the freeze does NOT decide (and why)

- Which wall/door hosts the bulkhead: the chamber is unlocated (all
  locate cards resultless); the FT-* ID is assigned at chamber survey
  per `t_03954030`.
- Exact DUT position inside: depends on chamber interior geometry
  (UNKNOWN — no chamber).
- Tape brand: not on record, not specced beyond class (polyimide/
  glass-cloth); the physical property that matters (no cold-embrittle
  adhesive off-gassing onto connectors) is carried by the class spec.
- Torque values: vendor datasheet not yet obtained (B2/B5/B6 all
  MUST-PROCURE, MPN TBD).

---

## 3. Tool resolutions (REQUIRED SPEC, numbers with units)

| Tool | Required spec | Resolution (least count) | Status | Source |
|------|--------------|--------------------------|--------|--------|
| Digital caliper | stainless digital-vernier class, jaw + step + depth faces, 0-150 mm range covers all planned dimensions (max: 0.50 m exterior run is a tape job; max caliper job = bulkhead jam-nut ~ 10 mm class) | **0.01 mm** (digital least-count; imperial 0.001 in) | MUST-PROCURE — none on host/record | Spec matches fleet card `t_f5f3fe8a` PREP verbatim: "digital caliper (0.01 mm / 0.001 in)" |
| Tape measure | steel blade, mm-graduated, >= 1 m | **1 mm** | MUST-PROCURE — none on host/record | Spec set by this freeze (first on record); 1 mm = smallest graduation readable to half-division (0.5 mm) with parallax; campaign lengths (0.15/0.50 m runs, loops) all tape jobs |

**Per-measurement uncertainty floors going downstream:** every caliper
reading carries ±0.01 mm least-count (report as the resolution floor;
add calibration-zero check per `t_03954030` protocol: zero on closed
jaws, exclude any gauge whose zero is off by more than 0.05 mm); every
length reading carries ±1 mm least-count. These floors apply to ALL
downstream cards (`t_9693c9bb` cable OD, `t_69bc5ef5` module envelope,
`t_f5f3fe8a` port caliper pass, `t_ad3aee13` penetrations): a
downstream reading may cite its own tool only if that tool's
resolution is better than or equal to these numbers, else the reading
inherits the worse floor and must say so.

**No tool make/model exists to record.** The fleet's no-inventory
status (`bffc7f9d`) and the fresh census make "make/model" an
absence-of-source answer: the required spec numbers above are what
downstream passes can rely on. When the caliper is procured, its
make/model/serial replaces the spec row with a measured row and this
report is superseded by a one-line update (see Section 8 unblock).

---

## 4. Ambient / bench conditions (bias fields)

| Field | Value | Provenance |
|-------|-------|------------|
| Host sensor temperature | 27.8 C | fresh read this session: `/sys/class/thermal/thermal_zone0` (acpitz) = 27800 milli-C. **Labeled proxy — host motherboard, NOT bench air.** No ambient-air sensor exists on any record. |
| Second thermal zone | excluded | `x86_pkg_temp` = 95.0 C is a package-throttle sensor, not ambient; excluded as a proxy. |
| Bench ambient air T | **UNKNOWN** | no ambient sensor on host or record; all prior reports carry 20/22/25 C ASSUMED grids (`65c9c3df`, warm-side-dewpoint "every cell ASSUMED") |
| Bench RH | **UNKNOWN** | 30-60 % ASSUMED class (same sources) |
| Jacket warm/flexible? | **UNKNOWABLE** | no cable exists to touch; answer recorded as the spec requirement instead: all routing/bending/taping operations SHALL be performed at room temperature (jacket flexible) BEFORE any cold exposure — bending a glassy cold jacket is the FM-8D mechanism. Once C-RF-INT-1/EXT-1 are procured, the field becomes "warm at routing time, verify by hand-flex" on the capture sheet. |
| Cable under tension? | **UNKNOWABLE at freeze; SPEC: NO** | no routing exists yet; the freeze bans tension: cables lie slack, loops carry the slack, nothing suspends weight. A tensioned cable transmits cold-contraction load into the DUT edge-launch (weakest link, FM-8D) and the bulkhead jam nut. |

**Bias direction note for downstream:** all planned measurements are
dimensional (OD, lengths) at room temperature. Thermal expansion of
PTFE-class jackets is order 10^-4 mm/mm-K (~100-200 ppm/K) — over a
0.50 m run that is ~0.01 mm/K, i.e. a 5 K ambient error moves a length
reading by ~0.05 mm, below the 1 mm tape floor and far below any
decision threshold; for OD the effect is ~0.0005 mm/K on 2.5 mm —
negligible against the 0.01 mm caliper floor. Ambient bias is
therefore dominated by the ASSUMED-vs-actual ambient gap for
*condensation/frost models*, not by dimensional readings; recording the
27.8 C proxy keeps even that term anchored.

---

## 4a. Photo/sketch requirement status

"Photograph or sketch the routed path" — **NOT PERFORMED.** No camera
(`/dev/video*` and V4L2 absent, multiple prior censuses concur) and no
routed cable exist. The deliverable is served by the ASCII plan-view
sketch in Section 2.1 plus the per-step checklist in 2.3; both derive
only from on-record geometry (planned lengths, bend rules, feedthrough
pattern). When a camera and the physical run exist, the photograph
supersedes the ASCII sketch, per the t_03954030 photo-log protocol.

---

## 5. Cable ID list (FROZEN identifiers)

| ID | Class / role | Status | Crossing | Routing rule |
|----|--------------|--------|----------|--------------|
| C-RF-INT-1 | RG316 SMA-m/m, 0.15 m, interior (DUT J1 -> bulkhead) | MUST-PROCURE, MPN TBD (`t_0d86117f` B1) | variant B only | 15 mm tie-off -> T1 -> B1 at R>=25 mm -> 50 mm loop -> bulkhead cold side |
| C-RF-EXT-1 | RG316 SMA-m/m, 0.50 m, exterior (bulkhead -> ref TX) | MUST-PROCURE, MPN TBD (`t_0d86117f` B4) | variant B only | 15 mm tie-off -> T3 -> drape -> 100 mm loop -> REF-TX J1 |
| C-SER-1 | USB-C serial, DUT console cable | MPN TBD (no USB-C cable part number on any record; OD 4.0-5.0 mm INDUSTRY-TYPICAL UNVERIFIED) | **variant A primary crossing** | glanded pass per `fe700201` 3d/step-4 rule; slack outside chamber; never taped to door seal |
| C-SER-2 | USB-C serial, reference TX console cable | MPN TBD | exterior only — never crosses | from reference TX to its host port; outside chamber wall |

Rules that make the IDs durable:

1. **Tie points and bends get IDs too**: T1 (first interior anchor),
   B1 (the interior bend), T3 (first exterior anchor). Downstream
   cards measuring "the tightest bend near the chamber wall" measure
   B1; "slack" measures the two loops by cable ID.
2. **Labels are physical at first touch**: each cable gets a labeled
   flag (heat-shrink or kapton tag) at BOTH ends at the moment it is
   first handled, carrying the ID exactly as written here. No
   downstream pass may mint a new identifier for an object already
   named here (per the `t_03954030` anti-collision rule for FT- IDs).
3. **The ID binds to the instance, not the length**: if C-RF-INT-1 is
   later procured at a different length than the 0.15 m plan, the ID
   survives; the length change is recorded against the ID, not by
   renaming.
4. C-SER-1/C-SER-2 distinction matters: both are USB-C serial, but
   only C-SER-1 crosses the sealed boundary and is therefore subject to
   the whole crossing/leak/frost mode family; C-SER-2 never enters
   chamber-adjacent service. A downstream pass that measures "the
   USB-C cable" without an ID is unmergeable — hence the freeze.

---

## 6. Frozen-decision arithmetic (checkable, stdlib-only)

`routing_length_check.py` recomputes every number this freeze decides,
with each input labeled [RECORD]/[SPEC]/[INDUSTRY-NOMINAL-UNVERIFIED].
Output saved verbatim in `output.txt`; rerun is byte-identical
(`diff` clean). Key results:

| Check | Result |
|-------|--------|
| Swept envelope at the bulkhead turn, R=12.7 mm | 27.9 mm swept diameter; 14.0 mm clearance from port face (reproduces `fe700201` 2d) |
| Swept envelope, R=25.0 mm (frozen rule) | 52.5 mm swept; 26.25 mm clearance |
| 90-deg arc length at R=25.0 mm | 39.3 mm |
| C-RF-INT-1 length budget: 15 mm tie-off + 39.3 mm arc + 50 mm loop = 104.3 mm vs planned 150.0 mm | **PASSES** (46% margin) |
| C-RF-EXT-1 length budget: 15 mm + 39.3 mm + 100 mm = 154.3 mm vs planned 500.0 mm | **PASSES** (3.2x margin) |
| Taped bundle OD (RG316 2.5 + USB-C 4.5, +0.5 loom) | 8.82 mm (reproduces `fe700201` 3c ~8.8 mm; inputs UNVERIFIED) |

The interior margin (46 %) is the freeze's actionable number: the
0.15 m plan survives the conservative 25.0 mm bend rule and both
loops. If the chamber survey later finds the bulkhead farther from the
DUT than 150 - 104 = ~46 mm of straight run allows, the FIRST
correction is lengthening C-RF-INT-1 at procurement, NOT tightening
the bend — that priority order is part of the freeze.

---

## 7. Source summary

| Claim | Source | Confidence |
|-------|--------|------------|
| Card `t_e5d5eaae` exists in the shared fleet index; task body = this task | `fleet_queue_state.json` task `meshcore:t_e5d5eaae` (read this session) | HIGH |
| No caliper/tape/measuring tool on any record | Fresh census; `bffc7f9d` no inventory system; zero tool hits across 495-task fleet index re-read | HIGH |
| No RF coax exists; 2x RG316 MUST-PROCURE, MPN TBD | `coax-bundle-dimensions` REPORT; `t_0d86117f` B1/B4; `55585471` 3b; `fe700201` 2a | HIGH (9th concurrence) |
| No chamber on any record; FT-* wall/door undecided | `24eb918c`, `766ac96d`, `ec80c11e`, `fe700201`, `40e1a49a`, penetrations.csv G1/P1 | HIGH |
| No camera on host | `/dev/video*` absent this session; prior censuses concur | HIGH |
| Caliper spec 0.01 mm | Fleet card `t_f5f3fe8a` PREP verbatim "digital caliper (0.01 mm / 0.001 in)" | HIGH (as spec; no tool in hand) |
| Tape spec 1 mm | Set by this freeze; steel-tape mm-graduation class | SPEC (first on record) |
| Bend rules 12.7 mm static / 25.0 mm 10xOD | `fe700201` 2b — INDUSTRY NOMINAL, UNVERIFIED (no vendor datasheet on host; nothing fetched) | carried, LOW-MEDIUM as before |
| RG316 OD 2.50 mm; USB-C OD 4.0-5.0 mm; bundle 8.82 mm | `fe700201` 2b/3c arithmetic, reproduced exactly in `routing_length_check.py` | carried, LOW-MEDIUM |
| Planned lengths 0.15 m / 0.50 m | `fe700201` 2a; `55585471` 3b; `t_0d86117f` B1/B4 | MEDIUM (planning inputs) |
| Bulkhead pattern 6.5 mm bore, SMA O-rings, feedthrough-as-penetration | `enclosure/README_big.md` 20-23 via `fe700201`; penetrations.csv P1 notes | HIGH as project pattern |
| FT- ID scheme | Fleet card `t_03954030` body | HIGH |
| acpitz 27.8 C fresh proxy read | `/sys/class/thermal/thermal_zone0` this session | HIGH (as labeled proxy) |
| Ambient grid 20/22/25 C + RH 30-60 % all ASSUMED | `65c9c3df`; warm-side-dewpoint "every cell ASSUMED" | carried |
| FM-8D called for this freeze | jacket-stiffening REPORT (routing-unfrozen risk row + unblock item 3) | HIGH |
| PTFE CTE ~100-200 ppm/K scale for bias note | `65c9c3df` source table (CTE labels) + `04db4fae` | carried |

---

## 8. What would supersede this freeze (unblock path, ordered)

1. **Procure the two RG316 assemblies** (`t_0d86117f` B1/B4) — with the
   freeze's priority rule: lengthen C-RF-INT-1 at order time rather
   than ever tightening B1 below 25.0 mm.
2. **Procure the caliper + tape** to the specs in Section 3; record
   make/model/serial + zero-check in the capture sheet, replacing the
   spec rows.
3. **Locate the chamber** (locate cards all resultless so far) — the
   FT-* ID assignment and the wall/door decision happen at survey per
   `t_03954030`.
4. **Execute the Section 2.3 checklist physically** with the parts in
   hand, label both ends of every cable per Section 5 rule 2, then
   photograph (camera still absent — this step blocks on hardware).
5. Downstream passes (`t_9693c9bb`, `t_f5f3fe8a`, `t_69bc5ef5`,
   `t_ad3aee13`) then measure against the frozen IDs, using the tool
   floors from Section 3.

---

## NOTHING FABRICATED

No physical measurement was performed — no cable existed to route or
tape, no caliper or tape exists to read, no chamber exists to route
through, no DUT is attached. No photograph or drawing of a physical
layout was produced; the ASCII plan-view is explicitly a SPEC sketch
from on-record inputs only. The two tool resolutions are stated as
REQUIRED SPEC (with the fleet's own 0.01 mm card language quoted), not
as readings of tools in hand. The acpitz 27.8 C value is a labeled
proxy read fresh from sysfs, not claimed as bench ambient. Every
carried number keeps its UNVERIFIED label and source. The arithmetic in
`routing_length_check.py` is reproducible stdlib-only with verbatim
`output.txt` and a byte-identical rerun. No outbound network fetch was
attempted (standing constraint respected). The fleet index was read
locally (established permitted pattern).