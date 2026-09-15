# RF port connector and antenna configuration — SkyMapper Board A (c3-a)

Task (fleet offload card, meshcore): "Identify RF port connector and antenna
configuration. GOAL: Determine where the carrier physically exits the module
and how it is currently coupled to free space."

Date: 2026-09-15 · Repo: meshcore (main) · Worker: dq05 (profile worker-heavy)
· Host: `c03rad0r-DQ05proplus`. Artifacts: this directory
(`bench/rf-port-antenna-config/`).

Physical inspection was NOT possible this session (DUT not attached — fresh
USB census below; no camera on host). Every finding below is DOCUMENT-BASED,
read fresh this session from the named files in `~/repos/balloon` (working
tree HEAD `d8c7f8f6`, branch `autonomous/mesh-baseline`), balloon git history
(`cc92c869`), and meshcore git history (`d7ae93fa`). Nothing is taken from a
prior report without re-reading its underlying source. Sibling reports
`bench/dut-rf-ports/REPORT.md` (connector census, commit `0b7bfe92`) and
`bench/dut-board-identity/REPORT.md` cover adjacent ground; this report adds
the antenna-configuration detail those summaries point to.

---

## RF PORT (required output section)

| Field | Value | Evidence tag |
|---|---|---|
| Designator | **No board-silkscreen RF designator exists — the DUT is a hand-wired breadboard assembly, not a PCB.** The exit points are the radio module's own castellated pads: **LR2021 pin 9 "ANT"** (sub-GHz) and **LR2021 pin 10 "2.4G/S"** (2.4 GHz). Wiring-record row names: `ANT_SUBGHZ` / `ANT_24GHZ`. Nearest thing to a silkscreen designator in the design family: flight-board THT pads **AE1 "868MHz" / AE2 "2.4GHz"** (`hub_board_v1.kicad_pcb:233-243`) — NOT the DUT's hardware. | NOT physically MARKED — designator read from vendor datasheet pin table + wiring CSV; silkscreen itself unread (no physical board) |
| Connector series (measured path, sub-GHz 868 MHz, LR2021 pin 9) | **NONE — no connector of any series.** Soldered wire dipole on a bare castellated pad. Not U.FL, not W.FL, not SMA, not RP-SMA, not MMCX — no mating interface exists. The U.FL-vs-W.FL / SMA-vs-RP-SMA ambiguity does not arise on this port. | DOCUMENT-BASED (datasheet V1.3 §7 "external 50-ohm antenna" at bare pad; wiring CSV; KiCad footprint `custom:LoRa2021_Castellated` pads 9/10 = nets RF_SUB_868/RF_2G4_2400, no connector footprint) |
| Connector series (2.4 GHz, LR2021 pin 10) | **NONE — same class.** Documented as wire dipole 3.1 cm on this assembly's wiring record; wiring guide alternatively allows "leave floating or 50Ω term". THIS board's actual pin-10 disposition UNVERIFIED. | DOCUMENT-BASED |
| Connector series (ESP32-C3 SuperMini onboard, WiFi/BLE 2.4 GHz — OUTSIDE the LoRa measurement path) | **U.FL (I-PEX) female jack** per board spec JSON (`esp32c3-mini-v1.json` `connectors.antenna`: "U.FL (I-PEX) for external antenna"). Kit accessory: "U.FL-to-SMA pigtail + 3dBi SMA antenna included". Physical population on c3-a's specific SuperMini UNVERIFIED (some batches omit the U.FL; clone variation). | DOCUMENT-BASED — series recorded, not a guess; physical presence unread |
| Cable / external antenna presently attached? | **LR2021 path: NO cable, NO external antenna — the soldered wire IS the antenna; the carrier exits the module pad directly into free space.** SuperMini U.FL: unknown whether the included pigtail + 3dBi SMA antenna is plugged into c3-a's unit — no physical record either way; this port is WiFi/BLE only and irrelevant to the LoRa bench path. | DOCUMENT-BASED; physical state UNVERIFIED (§ Unverified U1) |
| On-board antenna in use? | **YES — hand-soldered wire dipole on LR2021 pin 9 is the sub-GHz antenna in use** (per the assembly's own wiring records). The SuperMini additionally has an onboard PCB trace antenna for WiFi/BLE (per JSON caveat: "U.FL antenna connector is in addition to onboard PCB antenna"), outside the measurement path. | DOCUMENT-BASED |

### Antenna description (sub-GHz, 868 MHz — the port the bench measures)

All items below are read from the wiring records; nothing was visually
inspected this session. No impedance calculations are attempted.

| Property | Value | Source |
|---|---|---|
| Type | **Center-fed wire dipole, hand-soldered** — a single stiff copper wire, bent 180° at the feed so the two legs extend in opposite directions | `breadboard-wiring-guide.md:53-56` ("Wire dipole soldered to Pin 9 (ANT)... Use stiff copper wire (30 AWG), bend 180° for dipole"); CSV row `ANT_SUBGHZ` ("Wire dipole, 16.4cm wire @ 868 MHz") |
| Approximate dimensions | **Leg: 8.6 cm per leg (λ/4 at 868 MHz ≈ 86.4 mm per the guide's own annotation), 30 AWG stiff copper wire** (≈0.25 mm conductor diameter per the AWG standard). Total wire on record: 16.4 cm (CSV/flight plan) vs 2×8.6 = 17.2 cm tip-to-tip implied by the guide — **0.8 cm discrepancy unresolved** (likely feed-gap/end-effect, not stated on any record) | `breadboard-wiring-guide.md:17,54`; `wiring-dev-board.csv:14`; `FLIGHT-BOARD-PLAN.md:85` |
| Orientation | No as-built orientation is recorded for c3-a. Documented handling guidance: "Keep clear of metal surfaces and other wires" (`wiring-guide:56`); documented test posture on the range bench: "antenna vertical" on TX and RX (`range-test-comprehensive-plan-2026-07-17.md:32-33`). Physical orientation of c3-a's dipole as it sits: UNVERIFIED | wiring guide; range-test plan |
| Feed point | **Directly at the LR2021 module's pin 9 castellated solder pad** — no feedline, no coax, no connector, no intervening pad. On the flight-board design the same concept lands net `RF_SUB_868` on a 2.0 mm THT pad (AE1) straight from module pad 9 | `wiring-dev-board.csv:14`; `hub_board_v1.kicad_pcb:152,237`; datasheet V1.3 §7 pin 9 |
| Visible matching components (series/shunt L or C) | **NONE on any record.** The datasheet presents pin 9 as a bare "external 50-ohm antenna" interface; the wiring guide's parts list contains only 2× 100 nF decoupling caps (power pins, not RF); `hub_board_v1` nets RF_SUB_868/RF_2G4_2400 connect module pads to antenna pads with **zero intervening components**; datasheet text (recovered from `cc92c869` PDF this session) contains no matching-network section. The dipole is presumed to be the 50 Ω load directly | datasheet V1.3 (pdftotext, 0 hits for matching); `breadboard-wiring-guide.md` parts list; `hub_board_v1.kicad_pcb` net grep |
| Feed gap / balun | Not mentioned on any record — UNVERIFIED whether the two legs are bent symmetric with a gap at the pad or one leg runs along the module edge | absence in all wiring records |

**Evidence tag for the antenna shape/type: INFERRED-FROM-ANTENNA-RECORDS
(document-based inference)** — the task's INFERRED-FROM-ANTENNA tag applies
in that no component value or physical feature was read directly; the dipole
geometry comes from the builder's own wiring records, not from eyes on the
hardware. Every dimension above carries the same tag.

### How the carrier is coupled to free space (goal restatement)

The 868 MHz carrier exits the LR2021 die → module pin 9 castellated pad →
**solder joint** → 30 AWG copper wire dipole (2 × 8.6 cm legs, bent 180°,
vertical in the documented test posture) → free space. There is no coax, no
connector, no matching network, and no radome on record anywhere in that
chain. Coupling is direct radiation from the wire.

### Photos

**No photos could be taken, and none exist:**

1. This host has **no camera device** — `/dev/video*` absent, no V4L2
   hardware (`ls /dev/video*` → No such file or directory; only `/dev/dri`
   render nodes exist). No `fswebcam`/`v4l2-ctl` tooling.
2. The DUT is **not attached** — fresh `lsusb` census this session: 2× QinHeng
   CH340 serial, Pi Debugprobe (`2e8a:000c`), Realtek BT/Ethernet, hubs, card
   readers; **no ESP32-C3 (Espressif VID 303a) or LR2021 device on the
   bus**. `/dev/ttyACM0` is the Pi Debugprobe, not the DUT.
3. **No photo of the physical c3-a assembly exists anywhere on this host** —
   swept this session: meshcore repo working tree (only `logo/meshcore.png`),
   balloon repo working tree (only ground-station pinout references,
   enclosure renders, and range-test data plots), balloon git history image
   names (plots/renders only), `/mnt/es4` and `/mnt/lexar-audit` (empty
   directories), `/media/c03rad0r` (empty; `/media/root` permission-denied),
   `~/Pictures`, `~/photos`, `~/Desktop`, `~/Downloads` (no image files).

What would settle it: attach c3-a to any fleet host and shoot a close-up of
pin 9/pin 10 and the full dipole region with any camera (a phone photo
side-loaded onto the host suffices); the filenames would then be recorded
here.

### Unresolved ambiguities (HARD-RULE compliance)

| # | Ambiguity | Status | What would settle it |
|---|---|---|---|
| A1 | As-built dipole length: 16.4 cm total (CSV, flight plan) vs 8.6 cm × 2 legs (wiring guide) — 0.8 cm apart, no feed-gap note on record | OPEN (both figures on record) | Caliper measurement of each leg on the physical board (board must be attached); or builder's statement |
| A2 | Physical state of c3-a pin 10 (2.4 GHz): wire dipole 3.1 cm per CSV, vs "leave floating or 50Ω term" per wiring guide — mutually inconsistent records | OPEN | Visual inspection of pin 10 on the physical board; DMM/continuity check for a termination resistor |
| A3 | SuperMini U.FL physically populated on c3-a's specific unit (clone batches vary; JSON caveat says some boards need a solder bridge to select it) | OPEN | Visual inspection; mating test with a known U.FL plug — the settling method if U.FL vs W.FL were ever in doubt; the board JSON records U.FL, so no guess is made here |
| A4 | Whether the included U.FL-to-SMA pigtail + 3dBi SMA antenna is currently plugged into the SuperMini | OPEN (WiFi/BLE path only, outside the LoRa measurement path) | Visual inspection |
| A5 | Dipole orientation/feed-gap as the board actually sits (recorded guidance says vertical, clear of metal) | OPEN | Visual inspection |
| A6 | Silkscreen designator on the physical module (any vendor marking at pad 9/10) | OPEN — never read | Visual inspection with magnifier; photograph |

No connector-series guess was required: on the measured path there is no
connector at all, and on the SuperMini the series (U.FL) is stated by the
board's own spec JSON, not inferred.

---

## Evidence chain (all read fresh this session)

| # | Fact | Source (verbatim anchor) |
|---|---|---|
| 1 | DUT = "NiceRF LR2021 board (SkyMapper Board A or a spare)" running `LR2021_passive_mapper`, `/dev/ttyACM0` | meshcore @ `d7ae93fa`, `examples/passive_mapper/bench/README.md` Bench-setup table, DUT row (re-read this session) |
| 2 | Fleet tag c3-a = "ESP32-C3 + LR2021 board A (MAC b0:a6:04:00:96:dc, /dev/ttyACM0)" | `balloon/tools/balloon-board-lock.py:37` RESOURCES block |
| 3 | Sub-GHz exit: pin 9 = "Wire dipole, 16.4cm wire @ 868 MHz" | `balloon/tracker/hardware/footprints/wiring-dev-board.csv` line 14 (row `ANT_SUBGHZ`) |
| 4 | 2.4 GHz exit: pin 10 = "Wire dipole, 3.1cm wire @ 2.4 GHz" | `wiring-dev-board.csv` line 15 (row `ANT_24GHZ`) |
| 5 | Dipole build detail: "Each leg: 8.6 cm (λ/4 at 868 MHz ≈ 86.4 mm); stiff copper wire (30 AWG), bend 180° for dipole; keep clear of metal surfaces and other wires" | `balloon/docs/breadboard-wiring-guide.md:53-56` |
| 6 | Pin 10 alternative: "(leave floating or 50Ω term)" | `breadboard-wiring-guide.md:38` |
| 7 | 30 AWG copper wire is the stocked antenna material | `balloon/docs/inventory.md:118` ("30 AWG Kupferdraht") |
| 8 | Module pins 9/10 are bare 50 Ω pads, no connector | LoRa2021 Module Datasheet V1.3 §7 (recovered from balloon git `cc92c869` as PDF this session; pdftotext lines 497/503: "sub-GHz band antenna interface, external 50-ohm antenna" / "2.4G and S band antenna interface, external 50-ohm antenna"); no matching-network text anywhere in the datasheet (grep 0 hits) |
| 9 | KiCad footprint = castellated SMD pads only; nets RF_SUB_868/RF_2G4_2400 go pad→antenna-pad with zero intervening components | `balloon/tracker/hardware/hub_board_v1.kicad_pcb:134-153,233-243` (net grep this session: only module pads 9/10 and AE1/AE2 THT pads carry those nets) |
| 10 | Flight-plan equivalents: "AE1 | Sub-GHz antenna pad | Wire dipole 16.4cm | THT pad"; "AE2 | 2.4 GHz antenna pad | Wire dipole 3.1cm | THT pad" | `balloon/tracker/hardware/FLIGHT-BOARD-PLAN.md:85-86` |
| 11 | SuperMini U.FL + accessories | `balloon/tracker/hardware/footprints/esp32c3-mini-v1.json` connectors block + caveats (read this session) |
| 12 | Documented test posture "antenna vertical" on TX and RX | `balloon/docs/range-test-comprehensive-plan-2026-07-17.md:32-33` |
| 13 | DUT not physically attached | fresh `lsusb` this session: 2× 1a86:7523 CH340, 2e8a:000c Pi Debugprobe, no Espressif VID 303a device |
| 14 | No camera on host; no DUT photos exist anywhere | `/dev/video*` absent; image sweep of both repos + git history + mounts + home dirs: 0 board photos |

Counter-source examined and excluded:
`balloon/docs/PCB-HANDOVER-FOR-JLCPCB.md:232` describes the DEV antenna as
"U.FL connector on dev module → SMA pigtail → 3 dBi rubber duck" — but that
document's own header says it is auto-generated from `~/repos/balloon-fresh/`
for the **RP2040 range-test bench** (firmware
`multi_radio_sweep_gps_v4.cpp`, TX board `tx`/`rx` RP2040 resources), NOT the
c3-a ESP32-C3 assembly. `balloon-fresh` does not exist on this host (`ls
~/repos/` checked). The c3-a assembly's own wiring record (items 3-6)
governs: soldered wire dipole, no connector. This is the same
board-family disambiguation established in `bench/dut-rf-ports/REPORT.md` §5,
re-confirmed here for the antenna-configuration angle with a newly found
variant of it (rubber-duck-on-pigtail belongs to the RP2040 dev bench, the
SMA J1/J2 variant belongs to the F33 hub board, and the U.FL-pigtail variant
belongs to the SuperMini's WiFi/BLE accessory kit — three different antenna
chains, none of them the c3-a LoRa path).

---

## UNVERIFIED register

| # | Item | Why unverified |
|---|---|---|
| U1 | Physical RF state of c3-a: are the dipoles actually soldered? pin-10 disposition? SuperMini U.FL populated? pigtail attached? | DUT not attached (USB census); no photo of c3-a exists on any record |
| U2 | As-built dipole leg lengths and total (16.4 vs 17.2 cm records diverge) | Two on-record specs differ; no measurement record |
| U3 | Dipole orientation as-sitting, feed gap, symmetry of the 180° bend | Not recorded; no visual inspection |
| U4 | Any matching component physically present at the pad (none is on record, but absence-of-record ≠ absence-on-board) | No physical inspection; datasheet and PCB files show none designed |
| U5 | SuperMini onboard PCB-trace antenna details (WiFi/BLE, outside measurement path) | JSON records its existence, no geometry |

---

## Downstream impact

For the thermal-bench campaign: the OTA edgescan protocol needs zero
connectors and is unaffected. The antenna is the least mechanically robust
element of the RF chain — a soldered 30 AWG wire, with no strain relief on a
breadboard assembly (the flight-board designs add edge THT pads "for strain
relief" per `PCB-HANDOVER-FOR-JLCPCB.md:236`; c3-a has none of that).
Thermal cycling of the bench must not touch the wire; any enclosure or bag
around the module for cold soaks (per the fork README's sealed-bag playback
note) must keep clearance from the dipole.

---

## Acceptance statement

- Designator and series: stated — module pin 9 "ANT" / pin 10 "2.4G/S"
  (datasheet pin names; no board silkscreen exists on a breadboard assembly),
  series = NONE on the LoRa path (explicitly not U.FL/W.FL/SMA/RP-SMA — no
  connector exists), U.FL on the SuperMini WiFi/BLE path per its board JSON.
  Nothing is guessed; silkscreen itself could not be read (no physical board)
  and that is explicitly marked.
- Cable/antenna status: stated — no cable or external antenna on the measured
  path; soldered wire dipole is the antenna in use; SuperMini pigtail
  attachment unknown and out of path.
- Antenna described (on-board): wire dipole, 2 × 8.6 cm 30 AWG stiff copper
  legs bent 180° at the LR2021 pin 9 pad, vertical in documented test
  posture, no matching components on record — visual-description basis only,
  no impedance calculations.
- Photos: cannot be taken — no camera device on host, DUT not attached, and
  no existing photo of the physical board anywhere on the host; reasons
  given above, settling actions listed.
- Ambiguities: all six registered (A1-A6) with what would settle each.