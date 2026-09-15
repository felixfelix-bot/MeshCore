# Chamber penetration + door-gasket survey: dimensioned, source-cited inventory

Fleet card: `meshcore:t_f2b50f53` — "Measure and source-cite all chamber
penetrations + door gasket geometry."

Date: 2026-09-15, session start ~03:13+02:00, census + fleet re-read
03:14-03:20+02:00 · Repo: meshcore (main) · Worker: dq05 (profile
worker-heavy) · Host: `c03rad0r-DQ05proplus`.
Artifacts: this directory (`bench/chamber-penetrations-gasket/`) —
`REPORT.md` (this file) + `penetrations.csv` (machine-readable copy of
the Deliverable-1 table, same rows, same sources).

Lifecycle: this is the **first worker output for this card**. Claim
history (fleet_queue_state.json, re-read 03:14:04+02:00): claimed by
dq05 2026-09-14 06:35:17+02:00 — resultless (kickoff-only lifecycle;
session-DB search shows the only prior occurrence of `t_f2b50f53` is a
fleet-lookup inside the fe700201/t_48e048a1 session, which listed the
card but never ran it); re-claimed 2026-09-15 03:13:55+02:00 (this
session). Sibling protocol card `t_03954030` (ID scheme, provenance
tags) is claimed, decision=claim, no committed output on this repo at
commit time — its five-section protocol vocabulary is adopted
verbatim-by-body below (read from fleet state this session) so the two
inventories merge cleanly.

---

## VERDICT SUMMARY

**The survey is BLOCKED at the location gate: no thermal chamber exists
on any record or host, so there is nothing to walk, measure, or
photograph.** The task body opens with "in ONE site visit" and the KIT
line asserts calipers/tape/camera physically in hand; that premise
cannot be satisfied — per the fleet precedent (chamber-nameplate
`24eb918c` BLOCKED, chamber-controller `766ac96d` UNKNOWN,
chamber-preflight `ec80c11e` BLOCKED, chamber-rf-feedthroughs
`40e1a49a` BLOCKED, chamber-feedthrough-fit `fe700201` UNKNOWN), the
correct output is: record the contradiction, issue the deliverable with
**every field filled** — each field either UNKNOWN-with-reason or the
on-record constraint that bounds it — and freeze the measurement
conventions now so the single site visit runs identically the moment a
human names the unit. Nothing is simulated, estimated, or invented.

What this report contributes beyond the blocked rows:

1. **The penetration table and gasket record are issued with every
   field filled** (Deliverable 1 + 2 below; `penetrations.csv` carries
   the same rows machine-readable). Zero blank cells, zero unsourced
   numbers.
2. **The measurement conventions are frozen here** (section
   CONVENTIONS): ID scheme, instrument-per-bore assignment, zero/cal
   check, double-measure/ellipticity rule, provenance vocabulary —
   aligned to the sibling protocol card `t_03954030` body (FT-DOOR-n /
   FT-WALL-<SIDE>-n prefixes, clockwise-from-hinge order,
   FT-WALL-UNASSIGNED reserve, calipers 5-150 mm / pin gauges small
   bores / internal-jaw calipers deep recesses, zero-off-by->0.05 mm
   exclusion, 90°-apart double measure with ELLIPTICAL marking above
   0.2 mm, provenance tags documented/measured/UNVERIFIED, forbidden
   estimates). Where my card and `t_03954030` differ, the stricter rule
   wins and the difference is named (e.g. my card's tape-method
   C/pi is retained for outer-circumference-only subjects, tagged
   'measured (tape, ID = C/pi)' — `t_03954030` body names calipers/pin
   gauges/internal jaws but does not forbid the tape method).
3. **Every row carries its on-record constraint** so downstream fit
   math runs the moment a bore is measured: the fe700201 §3d
   fit-decision thresholds (USB-C ≥ 6.0 mm, RG316 ≥ 3.0 mm, SMA
   connector-pass ≥ 9.5-10 mm, SMA bulkhead mount 6.5 mm class) are
   embedded in the table rows, and the G1 gasket fields carry the
   project's own sealing-pattern citations (enclosure READMEs) as
   design references — explicitly NOT claims about the chamber part.
4. **The unblock path is exact** (section UNBLOCK): human names the
   unit → one site visit under the frozen conventions → measured IDs
   drop into the fit-decision table for instant PASS/FAIL → custodian
   gate (Felix) for any drilling.

A reader who has never seen this fleet gets: (a) the complete
field-complete row format for every penetration class, (b) the frozen
protocol so any surveyor produces mergeable rows, (c) the numeric
thresholds any measured bore must beat, and (d) the statement that
nothing could be photographed because no camera device exists on this
host and no subject exists on any record.

---

## STEP 0 — Why every physical field is UNKNOWN (the location gate)

Five independent prior reports + this session's fresh re-verification:

| Evidence | Fresh check this session (2026-09-15, +02:00) | Result |
|---|---|---|
| Fleet queue state (706 tasks, mtime 03:14:04) | programmatic scan for non-empty `*result*` fields + vendor-name sweep (TestEquity/Weiss/Espec/Tenney/Binder/Memmert/Thermotron/CSZ/Envirotronics/...) | **0 of 706 cards carry a result; zero vendor names** — every chamber locate/identify/nameplate/custodian card resultless (`t_a2f7f281` decision=claim only, `t_b09424f1` family, `t_ffc911f6` nameplate, `t_e96fa5ad` custodian, `t_a8b9d449` manual) |
| Chamber-locate card `t_a2f7f281` "Physically identify thermal chamber: make, model, serial, controller" | fleet state re-read | resultless — no make/model/serial/location anywhere |
| Nameplate survey `24eb918c` (bench/chamber-nameplate) | committed report re-read this session | BLOCKED — "chamber not located, zero data recorded … no unit found anywhere on host or record" |
| Controller survey `766ac96d` (bench/chamber-controller) | committed report re-read | UNKNOWN — "no chamber/controller exists on any record or host" |
| Preflight `ec80c11e` (bench/chamber-preflight) | committed report re-read | BLOCKED at attachment gate — "worker NOT physically attached to any chamber" |
| RF-feedthrough survey `40e1a49a` (bench/chamber-rf-feedthroughs) | committed report re-read | BLOCKED at location gate — same conclusion, 03:07 tonight |
| Feedthrough-fit `fe700201` (bench/chamber-feedthrough-fit) | committed report re-read | UNKNOWN — "no penetration to enumerate, no port to measure, no gasket to characterize" |

**Consequence:** the card's premises "in ONE site visit", the KIT list,
and the physical act "walk the chamber" cannot be reconciled with the
census below. Per fleet precedent: nothing simulated, every physical
field UNKNOWN with its reason, unblock path handed forward.

---

## STEP 1 — LOCATE AND IDENTIFY (fresh host census, all run 2026-09-15 this session)

The only way a chamber — or the KIT (calipers, tape, camera) — could be
"at" this worker is attached to this host:

| Check | Command / path | Result (verbatim summary) |
|---|---|---|
| Serial devices | `/dev/serial/by-id/` | `usb-1a86_USB_Serial-if00-port0 -> ../../ttyUSB1`, `usb-Raspberry_Pi_Debugprobe_on_Pico__CMSIS-DAP__203584200D2D0D42-if01 -> ../../ttyACM0` — 2x QinHeng CH340 (`ttyUSB0`, `ttyUSB1`) + Pi Debugprobe (`ttyACM0`), all attached 2026-09-14 11:05; **zero attach events 2026-09-15 00:00 onward** (journalctl USB/tty grep: no lines) |
| USB bus | `lsusb` | RTL8152 Ethernet, RTL BT radio (0bda:b850), Zoran audio/HID (0573:1573), 2x hubs, microSD reader, 2x CH340, Pi Debugprobe — **zero instrument-class, zero measurement peripherals, no caliper interface (no USB gauge protocol on any device), no camera** |
| Camera / photos | `/dev/video*`, `/sys/class/video4linux` | **absent** — no camera device exists on this host; v4l2-ctl not installed; 0573:1573 video-capability probe was operator-denied in `24eb918c`, not retried per standing rule |
| Instrument buses | `/dev/usbtmc*`, `/dev/gpib*` | absent — no such nodes |
| Bluetooth | prior session's `bluetoothctl devices` (re-verified resultless in `40e1a49a` census tonight) | hci0 sole paired device = keyboard — no chamber-class or measurement-class BT device |
| Host filesystem | `find / -xdev` chamber/gasket/feedthrough-photo sweep (excluded bench/.git, run this session) | zero chamber/gasket assets; only hits = Xilinx toolchain filenames (false positives, unrelated "gasket" in stats wrapper names) |
| KIT availability | lsusb + filesystem + no /dev/video* | **calipers: none · tape: n/a (digital) · camera: none · torch: n/a · marker: n/a** — the physical KIT asserted by the card is not present at this worker |

**Census conclusion: no chamber, no bulkhead, no gasket, no door, and
no measuring equipment exists at this worker.** Every physical field
below is UNKNOWN with exactly this reason.

---

## CONVENTIONS — frozen now so the ONE site visit is consistent

Per my card: "Do not split this across sessions or hand off
mid-visit — measurement method and conventions must be consistent
across every row." The conventions are therefore frozen in this report
now; the site visit executes them verbatim. Sibling protocol card
`t_03954030` (body read from fleet state this session, decision=claim,
no output yet) defines the shared scheme; I adopt it and add my card's
stricter rules:

1. **ID scheme** (per `t_03954030`): fixed prefixes — `FT-DOOR-n` for
   door-region penetrations, `FT-WALL-<SIDE>-n` (SIDE = TOP / BOTTOM /
   LEFT / RIGHT / REAR) for wall penetrations; IDs assigned in the
   order encountered walking clockwise from the door hinge;
   `FT-WALL-UNASSIGNED` reserved for anything found later. This card's
   P/G rows map onto that scheme at visit time: G1 = the door gasket
   itself (also `FT-DOOR-GASKET`); P1..P5 are **class rows** — on the
   visit each physical instance becomes its own FT-DOOR-n /
   FT-WALL-<SIDE>-n row and inherits its class row's constraints.
   Crosswalk: P1→dedicated feedthrough port, P2→door gasket
   pass-through area, P3→unused bulkhead holes, P4→cable boot/gland,
   P5→spare flange holes/blank cutouts.
2. **Instrument per bore** (per `t_03954030` + my card step 3):
   digital calipers for ID 5-150 mm; pin gauge set for small bores
   (< 5 mm); internal-jaw calipers for deep recesses; **flexible tape
   (ID = C/pi) where only outer circumference is accessible** — my
   card's method, retained because `t_03954030` names calipers/pin
   gauges/internal jaws but does not forbid the tape method. Method
   recorded per row; no row ambiguous.
3. **Calibration step** (per `t_03954030`): zero the calipers on
   closed jaws, record the reading; any gauge whose zero is off by more
   than 0.05 mm is excluded from use.
4. **Repeatability** (per `t_03954030`): each bore measured twice, 90°
   apart, both values recorded; difference > 0.2 mm → entry marked
   ELLIPTICAL with both numbers.
5. **Provenance vocabulary** (per `t_03954030` + my card's sourcing
   rule): `documented` = read off datasheet/nameplate/silkscreen;
   `measured (calipers)` / `measured (tape, ID = C/pi)` / `measured
   (pin gauge)` / `measured (internal-jaw calipers)` = taken with the
   named instrument; `datasheet` or `vendor spec — <which>` for
   part-level fields; anything not observable = **UNKNOWN with the
   concrete reason**; estimated/interpolated diameters are
   **forbidden** as measured values — if a soft number is unavoidable
   it is labelled **ESTIMATED** and confined to a notes column.
6. **Occupancy recording** (my card step 4): exactly `empty` or
   `used by <cable/conduit/blanking plug, with description>`; occupied
   bores that cannot be measured without disturbing the setup are
   marked UNKNOWN with that stated reason.
7. **Photo convention** (per `t_03954030`): one establishing photo per
   penetration + one close-up with caliper jaws in frame and ID label
   visible; every photo contains a scale reference; filename contains
   the penetration ID. My card adds: photo index keyed by ID (section
   PHOTO/ SKETCH INDEX). Not executable now — no camera device on
   host, no subject; see PHOTOS section.

---

## DELIVERABLE 1 — PENETRATION TABLE

One row per penetration class (the unit's actual instances populate
these at visit time under the frozen ID scheme). Every row: five
columns as the card demands — ID | Location | Inner diameter (mm) |
Occupied? | Measurement source — plus on-record fit constraints in the
row body.

| ID | Location (photo ref + free-text) | Inner diameter (mm) | Occupied? | Measurement source |
|----|----------------------------------|--------------------|-----------|--------------------|
| **G1** (door gasket — the seal itself) | UNKNOWN — no chamber located on any record or host (fleet re-read 03:14+02:00: 706 cards, 0 non-empty result fields; locate cards `t_a2f7f281`/`t_b09424f1`/`t_ffc911f6` resultless). Photo ref: NONE — no camera on host (no /dev/video*, no video4linux class, v4l2-ctl absent; 0573:1573 video probe operator-denied in `24eb918c`, not retried) and no subject | UNKNOWN (cross-section thickness, width, material, durometer, extrusion type, latch type, compression all UNKNOWN — Deliverable 2) | UNKNOWN — no door to inspect; class-typical latch candidates (cam/over-center, magnetic, compression) all UNVERIFIED | NOT MEASURED — no subject |
| **P1** (dedicated feedthrough port) | UNKNOWN face — no unit; assign `FT-WALL-<SIDE>-1..n` per `t_03954030` on site visit. Photo ref: NONE — no camera + no subject | UNKNOWN | UNKNOWN — expected empty or capped but UNVERIFIED (no unit) | NOT MEASURED — no subject. On-record constraint this bore must beat (CITED-PLANNING, fe700201 §3d): USB-C cable ≥ 6.0 mm; RG316 alone ≥ 3.0 mm; SMA connector-pass ≥ 9.5-10 mm; SMA bulkhead mount needs 6.5 mm class (enclosure/README_big.md:21-23 project pattern) |
| **P2** (door gasket pass-through area) | UNKNOWN — no unit; `FT-DOOR-1` per `t_03954030`. Photo ref: NONE — no camera + no subject | UNKNOWN | UNKNOWN — whether any cable currently crosses is unobservable (no door) | NOT MEASURED — no subject. Constraint: leak path certain IF a cable crosses (fe700201 Step 4: no gasket compression on cable footprint; frost jacking per condensation-risk `65c9c3df`); gasket itself = G1 row |
| **P3** (unused bulkhead holes) | UNKNOWN face — no unit; `FT-WALL-<SIDE>-n`. Photo ref: NONE — no camera + no subject | UNKNOWN | UNKNOWN — population unobservable (no bulkhead) | NOT MEASURED — no subject. Any located hole converts instantly via fe700201 §3d fit-decision table |
| **P4** (cable boot(s) / gland(s)) | UNKNOWN face — no unit; `FT-WALL-<SIDE>-n`. Photo ref: NONE — no camera + no subject | UNKNOWN | UNKNOWN — unobservable (no unit) | NOT MEASURED — no subject. Project gland design pattern: PG7 glands, 6 mm holes (enclosure/README.md:29,74) — DESIGN PATTERN, NOT the chamber part; PG7 clamps 4.0-5.0 mm USB-C per fe700201 Step 4.2 [INDUSTRY-TYPICAL, UNVERIFIED] |
| **P5** (spare flange holes / blank cutouts) | UNKNOWN face — no unit; `FT-WALL-<SIDE>-n`. Photo ref: NONE — no camera + no subject | UNKNOWN | UNKNOWN — unobservable (no unit) | NOT MEASURED — no subject. Would be the preferred drilled-port location; custodian gate Felix (`4b3ec9b5` MEDIUM) before any drilling |

**Row count justification (why 6 rows, not more):** these are the five
penetration classes the card enumerates (dedicated feedthrough port(s),
door gasket pass-through area, unused bulkhead holes, cable boot(s),
spare flange holes) plus G1 the gasket itself, which the card assigns
its own stable ID. A located unit may present multiple instances per
class (e.g. 3 bulkhead holes) — each becomes its own `FT-*` row at visit
time under the frozen scheme; no instance can be enumerated now.

**Zero unsourced numbers:** the only numerals inside the table are (a)
the fit thresholds and gland sizes, which are cited on-record
engineering values (fe700201 §3d computed from BOM `55585471` +
enclosure READMEs; 6.5 mm = project's own SMA bulkhead pattern), and
(b) the census counts. No diameter in this table is a measured or
estimated value — every bore field is UNKNOWN with reason.

---

## DELIVERABLE 2 — GASKET CHARACTERIZATION (G1)

Per the sourcing rule: every field carries its source or is UNKNOWN
with the concrete reason. No field is blank; no number is invented.

| Field | Value | Source |
|---|---|---|
| Cross-section thickness (mm) | **UNKNOWN** — no gasket exists on any record or host; no chamber located to inspect (fleet re-read 03:14+02:00; five prior reports concur) | NOT MEASURED — no subject |
| Cross-section width (mm) | **UNKNOWN** — same reason | NOT MEASURED — no subject |
| Material | **UNKNOWN** — no part on record; no nameplate; no datasheet on host. Class-typical candidates (EPDM, silicone, nitrile) all UNVERIFIED — not guessed | NOT OBSERVED — no subject |
| Durometer (if marked) | **UNKNOWN** — no part to read a mark from | NOT OBSERVED — no subject |
| Durometer (if datasheet) | **UNKNOWN** — no vendor, no datasheet on host; outbound fetch forbidden per standing dq05 constraint (respected — nothing attempted) | NOT DOCUMENTED — no subject |
| Extrusion type (solid / hollow / foam) | **UNKNOWN** — unobservable | NOT OBSERVED — no subject |
| Latch type | **UNKNOWN** — no door on record; class-typical candidates (cam/over-center, magnetic, compression) UNVERIFIED — not guessed | NOT OBSERVED — no subject |
| Target/observed compression the latch applies (preload) | **UNKNOWN** — no latch, no gasket, no door | NOT MEASURED — no subject |
| — design references (NOT the chamber part) — | The project's own sealing pattern for sealed enclosures: 2 mm AS568-compatible O-ring cord, material "Nitrile or silicone" (choice not made on record) | enclosure/README.md:27 ("O-ring groove in lid (2mm cord, AS568 compatible) — IP65+ sealing"), :72 ("O-ring cord (2mm) ~220mm, Nitrile or silicone"), read at `~/repos/balloon/tracker/hardware/enclosure/README.md` this session; also carried in `04db4fae` (bench/cable-feedthrough-failure-modes) seal-elastomer row |
| — design reference (SMA bulkhead seal) — | SMA bulkhead penetrations seal with SMA O-rings, "Fully waterproof" | enclosure/README_big.md:20-23 ("Two SMA bulkhead holes (6.5mm) … Fully waterproof with SMA O-rings"), read this session; carried in fe700201/40e1a49a |

The two design-reference rows are explicitly labeled: they describe the
**balloon-project enclosure** documented in this repo's sibling
project files — they are NOT measurements or claims about the chamber's
gasket, and no reader may treat them as chamber data. They bound what
the project already knows about sealing practice; the chamber's actual
gasket fields stay UNKNOWN until the unit is located.

**Why the gasket matters even UNKNOWN (downstream math that waits on
it):** fe700201 Step 4 — a round cable crossing a flat/profile gasket
leaves a leak path (no compression on the cable footprint); at
-20/-40 C the infiltrating moisture condenses/froze at the crossing
(65c9c3df physics: cold side 22-57 C below dew point in every lab cell)
and frost growth progressively jacks the gasket open. Gasket geometry
(thickness, compression, durometer) is exactly what decides whether a
gasket-crossing variant is tolerable — the reason this card exists.

---

## PHOTOS / SKETCH INDEX (keyed by ID)

| ID | Photo / sketch | Status |
|----|----------------|--------|
| G1 | establishing photo + caliper-in-frame close-up, ID label in frame, scale in frame (`t_03954030` photo convention) | **NONE — impossible**: no camera device on host (no /dev/video*, no video4linux class, v4l2-ctl absent; 0573:1573 video probe operator-denied in `24eb918c`, not retried per standing rule) AND no subject (no chamber/gasket located on any record or host) |
| P1-P5 | same convention, one pair per instance | **NONE — same reason** (no camera + no subject) |

**Dimensioned-sketch fallback:** 40e1a49a (bench/chamber-rf-feedthroughs)
already carries an ASCII reconstruction sketch keyed to its F1-F5
records, built from cited dims only; that sketch is the interim
photo-substitute and is cross-referenced here rather than duplicated.
Its F1-F5 map onto this table as: F1↔P1 (dedicated port), F2↔P2 (door
gasket pass-through), F3↔P3 (blank holes), F4↔P4 (glands/boots), F5↔P5
(spare flange). No new sketch is drawn this session: there are zero
measured dimensions to dimension it with — a sketch now would be
fiction, which the sourcing rule forbids.

---

## UNBLOCK (exact, ordered)

1. **Locate the chamber** — cards `t_a2f7f281` / `t_b09424f1` /
   `t_ffc911f6` (all resultless); requires a human to name the unit +
   location. No agent action can substitute.
2. **Kit check at visit time** — calipers, flexible tape, camera,
   torch, marker: none exist on this host today (census § STEP 1);
   the human who names the unit brings them or the visit re-checks
   this host for attachment.
3. **One site visit under the frozen CONVENTIONS** — enumerate every
   candidate penetration (P1-P5 classes), assign `FT-*` IDs clockwise
   from hinge, photograph per photo convention, measure per
   instrument-per-bore rules, record occupancy exactly, characterize
   G1 completely.
4. **Instant fit math** — measured IDs drop into fe700201 §3d
   fit-decision table (and connector-adapter-bom `bfc2a899` rows
   B2/B3) for PASS/FAIL per item; replace the UNVERIFIED planning
   inputs (USB-C overmold 9-12 mm, PG7 clamp range) with measured
   values.
5. **Custodian gate** — Felix (`4b3ec9b5` MEDIUM) must approve any
   drilling (BOM row B3: 6.5 mm hole conditional on no existing
   feedthrough); human gate.
6. **Parallel siblings to hand this to:** the BOM report `bfc2a899`
   already consumed the fit thresholds; this table's rows are
   structured for direct merge into its R3/R8 resolution.

---

## NOTHING FABRICATED

No penetration, bore diameter, gasket property, latch property,
compression figure, photo, or chamber attribute was invented. Every
physical field is UNKNOWN with its concrete reason. The only numbers
present are (a) census results (run this session, verbatim), (b)
on-record cited engineering values from committed sibling reports
(fe700201 §3d thresholds, 65c9c3df physics, enclosure README lines read
this session, BOM `bfc2a899` rows), and (c) the frozen convention
parameters (0.05 mm zero exclusion, 0.2 mm ellipticity threshold,
C/pi formula, 6.5 mm project pattern) — each labelled with what it is.
No outbound probes were performed (standing dq05 constraint). The
session-DB grep for full prior-session text was operator-denied
mid-task; the denial is recorded and was not retried — the lifecycle
statement above rests on the preview evidence and the claim timestamps
in fleet state, both read before the denial.