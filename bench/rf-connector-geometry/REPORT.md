# RF path geometry inputs — connector type, cable OD, min bend radius

Task (fleet offload, meshcore): "Identify RF connector type, cable OD and min
bend radius. GOAL: Establish the RF path geometry inputs for the
swept-envelope calculation."

Date: 2026-09-15 · Repo: meshcore (main) · Worker: dq05 (profile worker-heavy)
· Host: `c03rad0r-DQ05proplus`. Artifacts: this directory
(`bench/rf-connector-geometry/`).

---

## VERDICT SUMMARY

**No physical RF connector or cable exists to inspect, measure or photograph.**
Every step that requires a physical subject is therefore answered with
evidence-backed classification, not simulation. What CAN be delivered — and is,
below — is the complete geometry-input set for the swept-envelope calculation
as **planning values with explicit source labels**, plus the geometry
arithmetic itself (reproducible, cross-checked against the committed record).

Three findings govern everything:

1. **The DUT's RF path has ZERO connectors.** The LR2021 measurement path
   (868 MHz RX, the path the edgescan campaign measures) exits the DUT via a
   **soldered wire dipole on a bare castellated pad** — no SMA, no U.FL, no
   connector of any kind (`0b7bfe92`, design sources re-read this session:
   `~/repos/balloon/tracker/hardware/footprints/wiring-dev-board.csv` row
   `ANT_SUBGHZ` "Wire dipole, 16.4cm wire @ 868 MHz"; LoRa2021 Module
   Datasheet V1.3 §7 pin 9 "external 50-ohm antenna"). There is no connector
   face to photograph and no mating interface to measure.

2. **No coax cable exists on this host or on any record** (fresh census this
   session, STEP 0 below; `66573e52` "No RF coax exists on host or record";
   `55585471` §3b every coax line "Unknown (not on any record)"). The
   conducted path is a procurement plan: 2× RG316 SMA-m/m assemblies
   (0.15 m + 0.50 m) + 1× SMA bulkhead jack-jack feedthrough
   (`t_0d86117f` B1/B2/B4, all MUST-PROCURE). Cable OD and bend radius are
   therefore industry-nominal planning values, every one labeled UNVERIFIED —
   the task's own steps 2 and 4 prescribe exactly this for the unmarked case.

3. **The swept-envelope geometry inputs exist and are consolidated** in the
   deliverable table below, with the swept-envelope arithmetic (2R + t;
   R + t/2) reproduced and cross-checked against the committed figures in
   `fe700201` §2d (27.9 / ~14 mm at R=12.7; 52.5 / 26.25 mm at R=25.0) —
   all cross-checks PASS (`swept_envelope.py`, byte-identical rerun).

---

## STEP 0 — Fresh hardware census (why no measurement or photo is possible)

All checks run this session (2026-09-15), verbatim results in the census
block; summary:

| Check | Result |
|-------|--------|
| `lsusb` | 2× QinHeng CH340 serial, Pi Debugprobe, RTL8152 Ethernet, microSD reader, BT radio, Zoran audio/HID, 2× hubs, USB mass storage — **zero RF coax, zero instrument-class, zero camera** |
| `/dev/serial/by-id/` | 2× CH340 (`ttyUSB0`, `ttyUSB1`) + Pi Debugprobe (`ttyACM0`) — serial consoles only; **no ESP32-C3/LR2021/DUT attached** |
| `/dev/usbtmc*`, `/dev/gpib*` | absent — no bench instrument |
| `/dev/video*`, `/dev/media*`, V4L2 | **absent — no camera device exists on this host**; `v4l2-ctl` not installed |
| Filesystem (coax/cable/feedthrough search) | zero RF cable assets on disk |
| Prior reports | `66573e52` (coax census + 6 concurrences), `55585471` "Unknown (not on any record)", `40e1a49a` "no camera on host", `fe700201`, `04db4fae`, `c5eb3c58` — all concur |

**Photo acceptance:** "At least one close-up photo of the connector and one of
the cable jacket markings." **No photograph is claimed.** Two independent
reasons, both census-evidenced: (a) **no camera device exists on this host**
(no `/dev/video*`, no V4L2, `v4l2-ctl` absent — re-verified this session, and
no camera has ever appeared in any fleet census; a prior video-capability
probe was operator-denied in `24eb918c` and was not retried); and (b) **no
subject exists** — there is no connector on the DUT measurement path (wire
dipoles), no coax cable on host or record, and no MPN print to photograph.
Per fleet precedent, fabricating a photo (or re-labelling a stock/render image
as evidence) would be data fabrication; none was made.

---

## STEP 1 — Connector identification (module side and cable side)

**Module side — DUT (SkyMapper Board A / c3-a, LR2021): NONE.**
The measured RF path (ANT_SUBGHZ, LR2021 pin 9, 868 MHz) exits via a soldered
wire dipole on a bare castellated pad. Connector count on the measurement
path: **0**. The only connector-bearing RF port on the DUT assembly is the
ESP32-C3 SuperMini's onboard **U.FL (I-PEX) female jack** — WiFi/BLE radio
only, NOT on the LR2021 measurement path, physical population on c3-a's
unit UNVERIFIED (no board attached; SuperMini clones vary).
Sources re-read this session: `wiring-dev-board.csv` rows 14-15;
`esp32c3-mini-v1.json` (`connectors.antenna: "U.FL (I-PEX) for external
antenna"`, `antenna_accessories: "U.FL-to-SMA pigtail + 3dBi SMA antenna
included"`); full evidence chain in `0b7bfe92`.

**Cable side — planned RG316 assemblies (variant B conducted path): SMA
plug (male), standard polarity, both ends, straight.** Gender by
construction: the BOM spec is "SMA plug both ends, male pin, 50 Ω, standard
polarity" (`t_0d86117f` B1/B4, re-read this session). Standard (not
reverse) polarity is a procurement requirement, and RP-SMA is flagged as
incompatibility hazard H2 in the same BOM ("WiFi-industry RP-SMA plugs ...
will not mate"). Straight (not right-angle) is the class of every cited
representative MPN (Amphenol ACX-1169-class RG316 patch, `55585471` §3b line
1). No right-angle variant is specified or required anywhere on record.
No physical connector exists to verify against — identification is
**document-based** (BOM spec + representative class), UNVERIFIED on host.

**Feedthrough (the wall penetration, variant B): SMA bulkhead jack-to-jack,
panel mount, standard polarity, 50 Ω, PTFE, with jam nut** — Amphenol
132134-class, MUST-PROCURE (`t_0d86117f` B2; `55585471` §3b line 2). The
project's own documented bulkhead pattern: "Two SMA bulkhead holes (6.5mm) on
the side wall ... Screw SMA connectors through from outside ... Fully
waterproof with SMA O-rings" (`~/repos/balloon/tracker/hardware/enclosure/
README_big.md:20-23`, re-read this session).

**Reference TX (warm side): SMA edge-launch female jack, 50 Ω** — from the
hub-board-family PCB (`hub_board_f33.kicad_pcb` J1/J2, footprint
`custom:SMA_Edge_Mount`, re-read this session); `55585471`:77-79 "SMA standard
polarity, female jack on the PCB edge-launch". NOT the DUT board; the
reference TX is a second MeshCore node (`d7ae93fa` fork README bench table).

**Per-subject connector table (acceptance: connector type identified):**

| Subject | Connector | Gender / orientation | Source label |
|---|---|---|---|
| DUT, LR2021 ANT_SUBGHZ pin 9 (the measured 868 MHz path) | **NONE — soldered wire dipole on bare pad** | N/A — no mating interface | documented (wiring CSV, datasheet V1.3 §7, KiCad footprint; re-read this session); physical state UNVERIFIED |
| DUT, LR2021 ANT_24GHZ pin 10 | NONE — wire dipole (documented alternative: floating or 50 Ω term) | N/A | documented; this board's disposition UNVERIFIED |
| DUT assembly, SuperMini WiFi/BLE ANT | U.FL (I-PEX) female jack (not on measurement path) | female receptacle on PCB | documented (`esp32c3-mini-v1.json`); population on c3-a UNVERIFIED |
| Planned coax, both ends (interior + exterior) | **SMA plug, standard polarity, straight** | male pin (plug), both ends | documented BOM spec (`t_0d86117f` B1/B4; `55585471` §3b) — UNVERIFIED, no physical part |
| Planned SMA bulkhead feedthrough | SMA panel-mount jack-jack, jam nut | female both sides | documented BOM spec (`t_0d86117f` B2; Amphenol 132134-class) — UNVERIFIED, no physical part |
| Reference TX board (warm side) | SMA edge-launch | female jack on PCB edge | documented (family PCB `hub_board_f33.kicad_pcb`; `55585471`:77-79) — not the DUT; specific board UNVERIFIED |

RP-SMA, N, BNC: **excluded on record** — RP-SMA is a flagged non-mating
hazard (`t_0d86117f` H2); N/BNC appear only as conditional adapters "only if
instrument is not SMA" (`55585471` §3b line 5); no N or BNC instrument
exists on record (`c5eb3c58`).

---

## STEP 2 — Cable manufacturer + part number (jacket print)

**No cable exists; no jacket print exists to read.** Cable manufacturer and
MPN: **UNKNOWN — MUST-PROCURE** (per `t_0d86117f` B1/B4: "MPN TBD — required
spec: RG316 (OD 2.5 mm, PTFE), SMA plug both ends, male pin, 50 Ω, standard
polarity"; representative class Amphenol ACX-1169-class). Per task step 2's
unmarked-cable rule, the assumed standard is stated and marked:

**Assumed standard: RG-316 (military-spec-class flexible PTFE coax, 50 Ω).**
**UNVERIFIED** — this is the committed procurement spec class carried in
`55585471` §3b ("RG316, OD 2.5mm"), `fe700201` §2b, `t_0d86117f` B1, and the
entire bench report series; it is not a reading of any physical jacket.
RG-178 was considered and rejected on record (higher loss; RG316 selected
for lower loss and better mechanical stability — `55585471` §4.2,
`66573e52`). LMR-100: never on any record.

---

## STEP 3 — Cable outer diameter (OD)

**No calipers exist on this host** (no measuring device in the census; no
physical tool on any record — `66573e52`), **and no cable exists to measure.**
The value is carried as the planning input:

**OD = 2.50 mm (0.098 in) — INDUSTRY NOMINAL, UNVERIFIED.**
Source: RG316 spec class; cited as "RG316, OD 2.5mm" in BOM report `55585471`
§3b; carried in `fe700201` §2b and throughout the bench series. No vendor
datasheet exists on host; no outbound fetch is permitted from this host
(standing operator constraint — respected, nothing attempted). There is no
"measured" value and no "documented" (datasheet) value — only the
industry-nominal class value, which is why every consumer in this report
labels it UNVERIFIED and why the swept-envelope numbers below are planning
outputs, not measurements.

---

## STEP 4 — Minimum bend radius (static and dynamic)

**Min bend radius, static (installed): 12.7 mm (0.5 in) — INDUSTRY NOMINAL,
UNVERIFIED.** Given as an **absolute mm value, NOT an OD multiple** — it
coincidentally equals ~5× OD (5.08×, computed in `swept_envelope.py`), but
the source states mm (`fe700201` §2b; carried in `04db4fae` FM-8,
`t_0d86117f` B1 "flex life adequate for 12.7 mm min bend radius").
No vendor datasheet on host; no outbound fetch permitted.

**Rule-of-thumb alternative (task step 4's requested fallback): 10× OD =
25.0 mm — RULE OF THUMB, UNVERIFIED.** Basis: commonly quoted coax
installation guidance (bend radius ≥ 10× cable OD for solid-dielectric
coax); carried as the more conservative alternative in `fe700201` §2b. This
is the rule assumed where a manufacturer figure is absent; it is the more
conservative of the two candidates (25.0 vs 12.7 mm), so using it does not
understate the swept envelope.

**Min bend radius, dynamic (repeated flex): UNKNOWN.** Not stated in any
on-host source — no vendor datasheet exists and none can be fetched.
Industry-typical dynamic bend radius for RG316-class assemblies is ~10× OD
or greater — ENGINEERING KNOWLEDGE, UNVERIFIED, recorded only to give the
swept-envelope consumer a bound, not a fact.

**OD-multiple audit (arithmetic, `swept_envelope.py`):** R_static/OD =
12.7/2.50 = 5.08×. The two candidate radii therefore differ by exactly 2×
(25.0/12.7 = 1.97×), which is why the two swept-envelope outputs below
differ by the same ratio.

---

## STEP 5 — Connector mating depth/length and across-flats/nut size

**Mating (thread engagement) depth: UNKNOWN.** No vendor datasheet on host
or record for any SMA connector; no physical connector to measure. The SMA
family key is documented: coupling thread 1/4"-36 UNS, major OD 6.35 mm,
pitch 0.7056 mm/thread (`40e1a49a` identification kit, family-typical
UNVERIFIED). Industry-typical SMA plug body length ~15-22 mm — engineering
knowledge, UNVERIFIED (`66573e52`).

**Across flats / nut size: 7.94 mm (5/16 in) across flats; 9.17 mm across
corners — INDUSTRY-STANDARD SMA hex, UNVERIFIED on host** (`fe700201` §3c;
`40e1a49a`). Wrench access (for the torque step later): 5/16-in SMA torque
wrench, 0.9 N·m / 8 in-lb breakaway (`t_0d86117f` B9, Fujiya FTK-16SR-class)
or an 8 mm open-end spanner for the bulkhead jam nut (`t_0d86117f` B10).
Across-corners derived: AF/cos 30° = 7.94/0.8660 = 9.17 mm — arithmetic
cross-check vs committed 9.17 PASS.

**Bulkhead pass-through geometry (documented project pattern):** SMA
threaded barrel 6.35 mm major OD through the documented 6.50 mm panel hole →
diametral clearance 0.15 mm (0.075 mm radial). The 7.94 mm AF hex cannot
pass the 6.50 mm hole (9.17 AC > 6.50) — the feedthrough is mounted
nut-one-side and **the feedthrough itself IS the penetration**
(`fe700201`; README_big.md:20-23).

---

## DELIVERABLE TABLE — RF path geometry inputs (acceptance)

| Parameter | Value | Unit | Source label |
|---|---|---|---|
| Connector, DUT RF exit (measured path, pin 9) | NONE — soldered wire dipole on bare pad | — | documented (wiring CSV + datasheet V1.3 §7 + KiCad footprint, re-read this session); physical UNVERIFIED |
| Connector, cable ends (planned RG316 asm) | SMA plug, standard polarity, straight | — | documented BOM spec (`t_0d86117f` B1/B4) — UNVERIFIED, no physical part |
| Connector, bulkhead feedthrough (planned) | SMA panel jack-jack, jam nut | — | documented BOM spec (`t_0d86117f` B2) — UNVERIFIED |
| Cable standard / MPN | RG-316 class; MPN TBD | — | UNVERIFIED (assumed standard per task step 2; committed BOM spec `55585471` §3b, `t_0d86117f` B1; representative Amphenol ACX-1169-class) |
| Cable OD | 2.50 (0.098 in) | mm | INDUSTRY NOMINAL — UNVERIFIED (`55585471` §3b; `fe700201` §2b; no datasheet on host, none fetchable) |
| Min bend radius, static (installed) | 12.7 (0.5 in), absolute value | mm | INDUSTRY NOMINAL — UNVERIFIED (`fe700201` §2b; `04db4fae` FM-8; `t_0d86117f` B1) |
| Min bend radius, rule-of-thumb alt | 10× OD = 25.0 | mm | RULE OF THUMB — UNVERIFIED (commonly quoted coax guidance ≥10× OD; `fe700201` §2b) |
| Min bend radius, dynamic | UNKNOWN (~10× OD industry-typical bound) | mm | UNVERIFIED / UNKNOWN — no on-host source |
| SMA hex across flats (wrench size) | 7.94 (5/16 in); AC 9.17 derived | mm | INDUSTRY-STANDARD SMA — UNVERIFIED on host (`fe700201` §3c; `40e1a49a`) |
| SMA coupling thread | 1/4"-36 UNS, major OD 6.35, pitch 0.7056 | mm | family key — UNVERIFIED (`40e1a49a`) |
| Mating depth / connector body length | UNKNOWN (industry-typical ~15-22 mm) | mm | UNVERIFIED — no datasheet, no part to measure |
| Bulkhead panel hole | 6.50 | mm | DOCUMENTED project pattern (balloon `tracker/hardware/enclosure/README_big.md:21`) |
| Swept diameter at 90° turn, R = 12.7 mm | 27.90 (= 2R + t) | mm | computed (this session, `swept_envelope.py`) from UNVERIFIED inputs; cross-check vs committed `fe700201` §2d PASS |
| Port-face clearance at R = 12.7 mm | 13.95 (~14) | mm | computed from UNVERIFIED inputs; cross-check PASS |
| Swept diameter at 90° turn, R = 25.0 mm | 52.50 | mm | computed from UNVERIFIED inputs; cross-check PASS |
| Port-face clearance at R = 25.0 mm | 26.25 | mm | computed from UNVERIFIED inputs; cross-check PASS |
| Close-up photos (connector, jacket) | NONE — no camera, no subject | — | census STEP 0; nothing fabricated |

---

## REPRODUCIBILITY

`swept_envelope.py` (stdlib only): prints every input with its source label,
computes both swept-envelope candidates and the hex/thread/hole geometry,
and self-checks against the committed figures in `fe700201` §2d (27.9 / 14 /
52.5 / 26.25 / 9.17). Output saved to `output.txt`; rerun is byte-identical
(verified this session). Nothing measured, nothing simulated, nothing
fetched, no clock/randomness/network.

---

## WHAT WOULD RESOLVE EACH UNKNOWN (unblock path)

1. **Procure the RG316 assemblies + SMA bulkhead** (`t_0d86117f`
   B1/B2/B4/B9) — parts in hand resolve OD, bend radius (from the vendor
   datasheet that ships with the order), MPN and connector dimensions; the
   BOM line items exist for exactly this purpose.
2. **Obtain the vendor datasheet** for the specific procured assembly —
   resolves jacket OD (documented label), static AND dynamic bend radius,
   connector body length, mating engagement. No outbound fetch from this
   host; the datasheet must come with the part.
3. **Caliper measurement** (calipers not on host): jacket OD, hex across
   flats, body length — converts UNVERIFIED to measured.
4. **Photograph** connector faces and jacket print with any camera
   (camera not on host) — resolves the photo acceptance item; the planned
   identification kit (`40e1a49a` § first-sight procedure) gives the
   on-site discriminators: thread major OD 6.35 mm vs TNC 11.1 vs N 15.9;
   36 vs 28 vs 24 TPI; hex 7.94 mm → SMA; bayonet lugs → BNC.
5. **Physical inspection of c3-a** (board not attached to any fleet host):
   resolves U1/U2/U3 of `0b7bfe92` — whether the wire dipoles are actually
   soldered, their as-built length, and the SuperMini U.FL population.

---

## NOTHING FABRICATED

No measurement was performed and none is claimed: no cable, no connector, no
DUT RF port, no calipers and no camera exist on this host (fresh census,
STEP 0). No photograph is claimed (no camera, no subject). No datasheet
value is claimed (none on host, none fetched — standing no-outbound-fetch
constraint respected, nothing attempted). Every industry-nominal,
rule-of-thumb and engineering-knowledge value is labeled UNVERIFIED with
its carrier source; every computed figure shows its arithmetic; the
committed-record cross-checks all PASS. The DUT's wire-dipole finding rests
on design files re-read this session, not on prior-report trust.