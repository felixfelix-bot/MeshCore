# Module rigid envelope and protrusions

Fleet card: `meshcore:t_69bc5ef5` — "Measure module rigid envelope and
protrusions with photo evidence. GOAL: Produce the authoritative 'module
envelope' numbers that constrain the feedthrough."

Date: 2026-09-15 (session ~14:2x local, UTC+2) · Repo: meshcore (main) ·
Worker: dq05 (profile worker-heavy) · Host: `c03rad0r-DQ05proplus`.
Artifacts: this directory (`bench/module-envelope/`).

---

## VERDICT SUMMARY

**No physical module is attached to this host, and this host has no camera
and no measurement instrument.** Fresh census this session (14:17 local):
`/dev/video*` absent, `/sys/class/video4linux` absent (no UVC device at
all — `lsusb` shows no camera VID:PID; `ffmpeg` is installed but has no
input device); DUT Espressif VID:PID `303a:1001` absent from the bus;
`/dev/usbtmc*` and `/dev/gpib*` absent (no calipers or any
instrument-class USB device). Present serial devices: 2x CH340 generic
adapters, 1x Pi Debugprobe (`/dev/ttyACM0`), RTL8152 Ethernet, microSD
reader. This is the 9th+ census concurrence with prior bench reports
(`55585471`, `fe700201`, `87a2c136`, `0b7bfe92`, `d7b9107c`).

The card's physical steps (calipers on the actual module, photos with the
instrument in frame) are therefore **NOT EXECUTED — no subject and no
instrument exist on this host**. Nothing was measured, nothing was
photographed, and nothing below is presented as a fresh physical
measurement. What IS delivered — the deliverable that actually constrains
the feedthrough — is the authoritative envelope number set compiled from
**five concordant on-record measurement-grade sources**, with every number
labeled by its true provenance and the checkable arithmetic closed against
the vendor's own drawings:

1. The vendor datasheet §9 mechanical drawing (machine-read this session
   via tesseract OCR of the drawing raster; tolerances printed on the
   drawing itself).
2. The vendor package DXF (units mils per its companion `.asc` header
   `UNITS 0`; independent outline + closure arithmetic).
3. The balloon repo footprint json (prior caliper-derived record).
4. The BOM report `55585471` (citing datasheet V1.3 pin-definition page).
5. The enclosure README variant-A row.

Two record conflicts were found and **resolved** on the evidence (§4
below): the 2025-07-26 caliper set belongs to the big SMA dev board, not
the bare module; and the record thickness 2.32 mm exceeds the drawing's
2.2±0.1 mm upper tolerance — the record value is carried as the bounding
(conservative) figure.

The headline numbers this card was issued to produce:

| Quantity | Bounding (max of record) | Tolerance-inclusive worst |
|---|---|---|
| Max cross-section W x H | **19.81 x 15.05 mm** | 20.22 x 15.50 mm |
| Max rigid dimension L | **19.81 mm** | 20.22 mm |
| Thickness T | **2.32 mm** | 2.32 mm (record max) |
| Effective swept cross-section incl. protrusions | **19.81 x 15.05 x 2.32 mm — UNCHANGED** (every rigid protrusion projects 0.00 mm) | same |

Acceptance items: (a) stated in mm — YES (bounding + tolerance-inclusive,
provenance-labeled). (b) every protrusion listed with projection distance
— YES (§3). (c) ≥2 measurement photos with instrument in frame — **NOT
MET, cannot be met on this host** (no camera, no module); census evidence
above; the card's photo requirement is answered with NONE-with-reason per
the shared photo-log convention (`feedthrough-survey-protocol` §5.3,
committed `abe0d36f`). UNVERIFIED labels are applied wherever a number
rests on an assumption (§5).

---

## 1. The module and why it has no connectors

The DUT's radio module is the **NiceRF LoRa2021** (LR2021 Gen4, 18-pin
castellated, `dut-board-identity` committed report: two-chip hand-wired
assembly "SkyMapper Board A", radio module MPN NiceRF LoRa2021, carrier
ESP32-C3_Mini_V1 "SuperMini"). The RF path exits via **soldered wire
dipoles on bare castellated pads** — pin 9 ANT (sub-GHz, 868 MHz) and
pin 10 2.4G/S_ANT (2.4 GHz) — with **zero RF connectors** of any kind
(`dut-rf-ports 0b7bfe92`; `wiring-dev-board.csv` rows ANT_SUBGHZ /
ANT_24GHZ; datasheet V1.3 §7). The module carries no standoffs, no
heatsink fins, no screws, no mounting hardware, no cable stubs: it is a
bare 18-pad castellated PCB module. This is why the protrusion inventory
(§3) is short — there is physically nothing on the module that stands off
the body other than the wires that get soldered to it at run time.

## 2. Envelope table (the card's required output)

| dimension | value mm | how measured | photo filename |
|---|---|---|---|
| Max cross-section W (module long axis, over-castellations) | **19.81** (bounding; drawing 19.72±0.5; DXF closure 19.7168; BOM/README 19.72; json 19.81) | documented — NiceRF datasheet V1.3 §9 drawing (OCR-read this session) + vendor package DXF mil->mm + 3 record sources; see §4 | NONE — no camera on host (census 14:17 local); per-photo-log convention recorded NONE-with-reason |
| Max cross-section H (short axis, over-castellations) | **15.05** (bounding; drawing 15.0±0.5; DXF 15.0000; json 14.98; BOM 15.05) | documented — same drawing + DXF + record chain | NONE — same reason |
| Max rigid dimension L (end-to-end incl. mounting hardware) | **19.81 mm** — the module body IS the longest rigid axis; no connector/hardware extends it | documented — same chain; "no mounting hardware" verified from `dut-rf-ports 0b7bfe92` + DXF outline (no features beyond the rectangle) | NONE — same reason |
| Thickness T (height above carrier) | **2.32** (bounding; drawing 2.2±0.1; json record 2.32) | documented — drawing + record; the 2.32 record exceeds the drawing tol, carried as conservative bound (§4) | NONE — same reason |
| Face diagonal (W x H plane) | 24.88 computed (tolerance-inclusive 25.48) | computed from bounding values | n/a (arithmetic) |
| Min round bore for module transit (module lengthwise-first, sqrt(W²+T²)) | 15.23 computed (tol-incl 15.67; +10% handling 17.24) | computed | n/a |
| Min slot (module flat) | 20.22 x 2.32 mm (tol-inclusive) | computed | n/a |
| Sub-GHz dipole extended span | **164-172 mm** [UNVERIFIED as-built — two on-record readings disagree: one 164 mm wire bent 180° at its center (CSV/PLAN) vs two 86 mm legs (wiring guide); which is as-built UNKNOWN, DUT absent] | documented (records) + arithmetic; non-rigid (30 AWG bendable copper) | NONE — same reason |
| 2.4 GHz stub extended span | **31 mm** [RECORD; as-built UNVERIFIED] | documented (wiring-dev-board.csv AE2) | NONE — same reason |
| Collinear end-to-end extent (L + dipole laid straight along the module axis) | **183.81 mm** bound (19.81 + 164) [UNVERIFIED — orientation-dependent; the wire bends] | computed from record values | NONE — same reason |

**Provenance vocabulary follows the shared protocol** (`feedthrough-survey-protocol` §4, commit `abe0d36f`): `documented` = read off a
datasheet/drawing — source named; `measured (<instrument>)` = taken this
survey with a named instrument (none exist here, so no row carries this
tag); `UNVERIFIED` = anything else. Every row above carries one of
documented / computed-from-documented / UNVERIFIED; no row is presented
as fresh physical measurement.

## 3. Protrusion inventory (card step 2 — every protrusion, projection distance, location)

| # | Protrusion | Location | Projection beyond body (mm) | Rigid? | Provenance |
|---|---|---|---|---|---|
| P1 | 18x castellated half-pads (plated half-hole barrels) | both long edges, 9 per edge, 2.0 mm pitch | **0.00 mm** — castellation half-holes are drilled centered exactly ON the module outline edge (DXF decal: STK land centers and the outline edge share x = 294.9607 mil, i.e. the land pattern aligns host copper to the half-hole); module laminate extends exactly TO the edge, plating is inboard-facing | yes | documented (DXF geometry + drawing callouts) |
| P2 | Castellation half-moon notches | 18 sites along both long edges | **−0.50 mm** (material removed: drill dia 1.0 mm per drawing callout, half-circle notches 0.50 mm deep INTO the body) | n/a (removal) | documented (datasheet §9 drawing callout 1.0±0.1 mm; DXF DRIL_HOLE_0 is a dimensionless decal symbol) |
| P3 | Sub-GHz wire dipole, 30 AWG stiff copper, soldered at run time | pin 9 ANT pad, left edge top (top view) | **non-rigid**: extends up to 164-172 mm from the pad [UNVERIFIED which reading is as-built] | no — bends | documented (records); as-built UNVERIFIED |
| P4 | 2.4 GHz wire stub, 30 AWG | pin 10 2.4G/S_ANT pad, right edge top | **non-rigid**: up to 31 mm from the pad [as-built UNVERIFIED] | no — bends | documented (records); as-built UNVERIFIED |
| P5 | Pin-1 marker semicircle | DXF decal, outside the outline near terminal 1 (ANT end) | 0.00 mm — NOT material (PADs decal convention; the datasheet §9 raster cross-check shows the drawn module as a plain rectangle with no protruding tab) | no | documented (DXF decal analysis) |
| P6 | RF connectors / standoffs / heatsink fins / screw heads / cable stubs | — | **NONE EXIST** on this module (bare castellated module; `dut-rf-ports 0b7bfe92`) | — | documented |

Effective swept cross-section including protrusions (card step 4): the
rigid envelope is **unchanged at 19.81 x 15.05 x 2.32 mm** — the only
features beyond the body outline are bendable wires (P3, P4), which do
not sweep a rigid envelope. If the dipole must transit rigid and laid
straight, the number to use is the collinear extent 183.81 mm bound
(UNVERIFIED orientation assumption).

## 4. Source chain, cross-checks, and conflict resolution

Every width/length/thickness figure rests on this five-source chain:

**[DRAWING] NiceRF LoRa2021 datasheet V1.3 §9 "Mechanism Dimension (Unit:
mm)"** — raster drawing on p.7-8, machine-read this session (tesseract
5.x, image extracted via pdfimages, upscaled 4-5x): callouts
19.72±0.5 mm, 15.0±0.5 mm, 2.2±0.1 mm thick, pad pitch 2.0±0.1 mm, edge
margin 1.86±0.1 mm, castellation dia 1.0±0.1 mm, pad 1.2±0.1 x 2.0±0.1 mm
(the "1.86£0.1mm 2.0£0.1mm 1.2+0.1mm" OCR strings; £ is OCR's rendering
of ±). Source: `/tmp/lr2021_extract/LoRa2021-Module-Datasheet-V1.3.pdf`
recovered from balloon commit `cc92c869` (vendor assets live only in git
history, not the working tree).

**[DXF] Vendor package drawing `LoRa2021 V1.2_pads.dxf`** (same commit;
units mils per the companion `.asc` header `UNITS 0 = Mils`): body
outline polyline x-span 590.5512 mil = **15.0000 mm**, y-span 776.2504
mil = **19.7168 mm**, SMOOTH_10 corner radius 2.5 mil = 0.0635 mm. Pad
closure arithmetic: 9 pads/side x 8 pitches x 2.0000 mm + 2 x 1.8584 mm
margin = **19.7168 mm** — closes to the drawn 19.72±0.5 within −0.0032
mm (PASS). The drawn tolerance ±0.5 mm covers the 0.09 mm json/BOM
spread; the DXF-vs-drawing length agreement (0.0032 mm) confirms both
refer to the same nominal part.

**[RECORD] `balloon/tracker/hardware/footprints/nicerf-lora2021.json`**:
19.81 x 14.98 x 2.32 mm (prior caliper-derived record, pin pitch 1.29 mm
note).

**[RECORD] BOM report `55585471`** citing datasheet V1.3: 19.72 x 15.05
mm. **[RECORD] `balloon/tracker/hardware/enclosure/README.md`** variant
A: 19.72 x 15.0 mm.

**Conflict 1 — the "CALIPER MEASURED 2025-07-26" 24.05 x 24.11 x 3.34 mm
entry in `balloon_dev_case.scad` does NOT belong to the bare module.**
Its own introducing commit (`2a0b4500`) message says: "LR2021 bare module:
24.05 x 24.11 x 3.34mm (caliper measured) ... SMA pigtail spacing: 13.92mm
center-to-center ... Pin pitch: 4.17mm" — and the same commit's diff shows
the values were applied to the **big LR2021 dev board with SMA connectors**
(`big_radio_w`/`big_radio_l` "24.05 measured + 4mm clearance", and the
README variant-B table's "~52x35mm est" big-board entry). A bare 18-pin
castellated module has 1.29 mm pin pitch and no SMA pigtails; the F33
sibling variant is 39x21x2.5 mm (`nicerf-lora2021f33-2g4.json`). The
24.05 x 24.11 x 3.34 mm set is therefore excluded from the bare-module
envelope: it is the big dev board's PCB dimensions (a different part), not
the module. Carrying it would have inflated the envelope by 22 % on the
long axis.

**Conflict 2 — thickness.** Drawing says 2.2±0.1 mm; record json says
2.32 mm (0.02 mm beyond the drawing upper tolerance). Both kept, record
carried as the bounding conservative figure; the +0.02 mm interpretation
(pad/solder bump on the measured unit) is UNVERIFIED.

**Cross-check against the sibling fit report.** `fe700201` §3a carried
"module height / tallest protrusion UNKNOWN (datasheet page images on
disk not machine-readable this session; no vision tool bound)". This
session closed that gap machine-readably: the drawing thickness 2.2±0.1
mm is now OCR-extracted, so the sibling's UNKNOWN height cell can be
filled with 2.2±0.1 documented / 2.32 record bounding. The bounding
envelope 19.81 x 15.05 mm is unchanged from `fe700201`'s fit decision
(bounding value used for fit: 19.81 x 15.05 mm) — this report confirms
it as the authoritative figure with the full provenance chain behind it.

## 5. UNVERIFIED labels (card acceptance requirement)

- **As-built dipole span 164 vs 172 mm**: two on-record readings disagree
  (`wiring-dev-board.csv` AE1 "16.4cm wire" vs `breadboard-wiring-guide.md`
  "8.6 cm wire x2"). Assumption if used: bound 164-172 mm, collinear
  extent 183.81 mm assumes the 164 mm reading and a straight wire along
  the module axis. Which reading is as-built is UNKNOWN (DUT absent).
- **Record thickness 2.32 mm as-built**: exceeds drawing tol; assumed
  conservative bound.
- **Tolerance-inclusive worst case 20.22 x 15.50 x 2.32 mm**: assumes the
  drawing tolerances apply to every unit and that record and drawing
  describe the same nominal part (confirmed by DXF closure within
  0.0032 mm, but per-unit variation is not sampled — no unit on hand).
- **No fresh caliper measurement**: every "measured" number on this host's
  records predates this session; none of the values above were taken this
  session. First physical contact with the module must re-run the
  measurement steps with calipers + camera (see unblock).

## 6. Photo evidence (card step 3) — census-backed NONE

The card requires ≥2 photos with calipers in frame. **No photo exists and
none can be taken on this host**: `/dev/video*` absent,
`/sys/class/video4linux` absent, no UVC VID:PID on `lsusb` (census
14:17 local, this session; consistent with all prior sessions). There is
also no module attached and no caliper on any record (rf-connector-geometry
`87a2c136` MUST-PROCURE calipers; routing-freeze `d7b9107c` caliper spec
0.01 mm MUST-PROCURE). Per the shared photo-log convention
(`feedthrough-survey-protocol` §5.3): every photo cell is **NONE — reason:
no camera device on host and no module attached** (never blank). When a
camera and the module exist, the required photos are: (1) longest-axis
photo, calipers engaged across the 19.72 mm span; (2) cross-section photo,
calipers across the 15.0 mm span; (3) wide protrusion shot — and the
numbers in this report are the priors those photos must confirm.

## 7. What these numbers constrain (downstream use)

- The module (19.81 x 15.05 x 2.32 mm, face diagonal 24.88-25.48 mm)
  passes any bore ≥ the min round bore 15.67 mm (tolerance-inclusive,
  zero clearance) — i.e. it fits the 27.9-52.5 mm swept-envelope family
  of `fe700201` §2d/§3d with large margin, or any gasket-line crossing
  sized for the USB-C overmold (~12-13 mm) also admits the module.
- The module is NOT the binding constraint on any feedthrough in the
  current plan: variant A crosses only a USB-C cable (4.0-5.0 mm OD),
  variant B adds RG316 (2.50 mm); the module never crosses the
  boundary — it lives inside the chamber. The envelope matters as (a)
  interior placement clearance and (b) the pre-measurement prior for the
  run-time caliper verification.
- The DXF/drawing closure (19.7168 vs 19.72±0.5) also validates the
  mil->mm chain used in `rf-connector-geometry 87a2c136`, and the OCR'd
  2.2±0.1 mm fills `fe700201` §3a's UNKNOWN module height cell.

## 8. Unblock (what a human must do to convert this to photo evidence)

1. Procure the digital caliper (0.01 mm least count, per `t_f5f3fe8a` PREP
   spec, routing-freeze `d7b9107c`) and any camera.
2. Attach the module (currently absent: no Espressif VID:PID on the bus).
3. Measure: the two cross-section dims (expect 19.7-19.8 x 15.0 mm over
   castellations), thickness (expect 2.2-2.32 mm), and confirm zero
   rigid protrusions.
4. Photograph per §6: longest axis + cross-section + wide shot, calipers
   in frame, module ID label visible.
5. Compare against this report's priors; deviations beyond drawing tol
   go back to the record as new bounding values.

Checkable arithmetic: `module_envelope_check.py` (stdlib only,
deterministic, byte-identical rerun) — verbatim capture `output.txt`.
Nothing fabricated: no measurement claimed, no photo claimed, no number
presented as fresh physical data; every figure carries its provenance
label, and the two record conflicts are resolved on the evidence rather
than averaged away.