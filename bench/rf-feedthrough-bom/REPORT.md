# RF connector, adapter, and feedthrough hardware inventory

Fleet card: `meshcore:t_2f5adb53` — "Inventory RF connectors/adapters/feedthrough."

Task: Produce a definitive list of every RF/electrical interface component
required to get signals from the DUT inside the chamber to the instruments
outside.

Date: 2026-09-14 · Repo: meshcore (main) · Worker: dq05.
Artifacts: this directory (`bench/rf-feedthrough-bom/`).

---

## VERDICT SUMMARY

The measurement chain is **over-the-air**, not conducted: the `edgescan`
protocol programs a known offset into the DUT's own `cal` command and counts
decoded packets from a **reference transmitter at room temperature** outside
the chamber. No RF cable carries the measurement signal through the chamber
wall. The only penetrations needed are:

1. **Serial/USB** for the DUT CLI (`/dev/ttyACM0`, 115200 8N1) — already
   present on the ESP32-C3 SuperMini's native USB-CDC interface, no RF
   connector involved.
2. **Serial/USB** for the reference TX (`/dev/ttyUSB0`) — same, on a second
   board at room temperature, no chamber penetration.

An **RF feedthrough is NOT required** for the primary edgescan path. The
prior bench reports (condensation-risk, ramp-feasibility) discussed an RF
feedthrough because they assumed a coax run might be needed; the actual
protocol does not use one. If the operator elects to use a conducted path
(e.g. to reduce over-the-air variability), the BOM below covers that case
too.

---

## STEP 1 — Connector types on the DUT and instrument sides

### 1a. DUT RF port: SMA edge-launch (sub-GHz) on the SkyMapper carrier board

The DUT is a NiceRF LoRa2021 module soldered to a "SkyMapper Board A"
(ESP32-C3 + LR2021, fleet resource `c3-a`, MAC b0:a6:04:00:96:dc,
`/dev/ttyACM0`).

**NiceRF LoRa2021 module** (the radio module itself):
- Antenna interface: **castellated PCB pads** (pin 9 = ANTA sub-GHz,
  pin 10 = 2.4/S_ANTA). No connector on the module — it is a stamp-hole
  SMD module (19.72 x 15.05 mm) soldered to the carrier board.
- Source: NiceRF LoRa2021 datasheet V1.3 (2026-04, downloaded this session
  from nicerf.com), Pin Definition table, pin 9 and pin 10.

**SkyMapper carrier board** (the board the module is soldered to):
- The condensation-risk report (commit `65c9c3df`, line 305-306) states
  verbatim: "The DUT board (SkyMapper with LR2021) has solder joints at the
  **SMA edge-launch connector**, the module pins, and the PCB."
- The balloon tracker hardware repo (`~/repos/balloon/tracker/hardware/`)
  has the KiCad PCB files for the carrier board family
  (`hub_board_f33.kicad_pcb`). That PCB uses a custom footprint
  `custom:SMA_Edge_Mount` with:
  - Reference J1, value "SMA-868" — SMA end-launch edge connector for
    sub-GHz antenna, net `RF_SUB_868` (connected to LR2021 pin 9 / ANTA).
  - Reference J2, value "SMA-2G4" — SMA end-launch edge connector for
    2.4 GHz antenna, net `RF_2G4_2400` (connected to LR2021 pin 10).
  - Source: `hub_board_f33.kicad_pcb` lines 165-179, read this session.
- An earlier schematic (`v_c3_flight-erc.rpt`, lines 434-442) shows
  U.FL connectors (footprint `U.FL_Molex_MCRF_73412-0110`) for ANT1 and
  ANT2, but the **physical PCB uses SMA edge-launch, not U.FL** — the ERC
  report flagged the U.FL footprint as "not found in library" and the
  fabricated board (`hub_board_f33.kicad_pcb`) uses `SMA_Edge_Mount`.
  The IMPLEMENTATION-PLAN.md (line 42) says "Connect antennas to U.FL
  connectors on LoRa2021 modules" but this refers to the bare-module
  breadboard prototype phase, not the SkyMapper PCB.
- The enclosure design for the big LR2021 dev board variant
  (`enclosure/README_big.md`) confirms: "External antennas via SMA
  bulkhead holes" and "Sub-GHz SMA: for 868/915 MHz antenna."

**DUT RF connector: SMA (standard polarity, female jack on the PCB edge-launch).
The sub-GHz port (J1 / SMA-868) is the one used for the 868 MHz calibration
measurements.**

### 1b. Instrument / test-equipment side: no RF instrument in the primary path

The primary `edgescan` measurement does not use an RF instrument (signal
generator, spectrum analyzer, VNA, or frequency counter). It uses:

- **DUT** (inside chamber): NiceRF LR2021 on SkyMapper Board A, running
  passive_mapper firmware. Serial CLI at 115200 8N1 on `/dev/ttyACM0`.
  The DUT receives over-the-air from the reference TX and counts decoded
  packets.
- **Reference TX** (outside chamber, room temperature): any MeshCore node
  on the nominal frequency (868 MHz, SF8/BW62.5), transmitting continuously.
  Serial CLI on `/dev/ttyUSB0`.
- Source: fork README (d7ae93fa:examples/passive_mapper/bench/README.md),
  "Bench setup" table and "Protocol" sections, read via `git show` this
  session.

**No RF connector on the instrument side is needed for the primary path.**
The reference TX has its own antenna (wire dipole or SMA-connected stub)
and transmits wirelessly to the DUT inside the chamber.

The USB census on this host (bench-owner report `023c5e86`, re-verified
in atcut-fit report) confirms: **no SDR, no frequency counter, no GPSDO,
no signal analyzer, no VNA, no usbtmc/gpib device** on the bus — only
2x CH340 serial, Pi Debugprobe, RTL8152 Ethernet, microSD reader,
hubs/BT/audio-HID. There is no RF instrument to connect.

### 1c. If a conducted RF path were desired (optional)

If the operator chooses to run a coax from the DUT's SMA port through the
chamber wall to an external signal generator or reference TX (instead of
over-the-air), the instrument-side connector would be **SMA (standard
polarity)** on any sub-GHz signal generator or reference TX. The
balloon repo's range-test and sweep-capture scripts
(`scripts/range_test_runner.py`, `scripts/sweep_capture.py`) use the
boards' own SMA antennas, not external instruments.

---

## STEP 2 — Chamber feedthrough: status

**The chamber has never been identified.** (chamber-ownership report
`4b3ec9b5`, ramp-feasibility report `79ea692e`, condensation-risk report
`65c9c3df` — all confirm: no make, model, serial, controller, manual, or
datasheet on any record.)

Therefore: **the chamber feedthrough is UNKNOWN** — it may be:
1. A dedicated RF feedthrough port (SMA bulkhead or hermetic feedthrough)
   on a proper environmental chamber — STATUS UNKNOWN.
2. A cable through a door gasket (the likely case for a kitchen freezer
   or unidentified chamber) — STATUS UNKNOWN.
3. Non-existent (no penetration planned because the measurement is
   over-the-air) — STATUS: N/A for the primary path.

Fleet cards that would have resolved this all have no results:
- `t_48e048a1` "Survey chamber feedthrough port + mechanical fit" — skip
- `t_9d139605` "Compile feedthrough+RF feasibility verdict" — skip
- `t_67f3b03e` "Establish chamber max ramp rates and RF feedthrough
  thermal penalty" — no result

Source: atcut-fit/REPORT.md (commit `c4be4400`), fleet board table lines
208-211, re-verified this session.

---

## STEP 3 — Bill of materials

### 3a. Primary path (over-the-air edgescan) — NO RF feedthrough needed

| # | Item | Qty | Part number | Source | On-hand | Must procure | Lead time |
|---|---|---|---|---|---|---|---|
| 1 | SMA edge-launch connector (sub-GHz, on DUT PCB) | 1 | Custom `SMA_Edge_Mount` footprint (J1, "SMA-868") on SkyMapper board | `hub_board_f33.kicad_pcb:165` | Already soldered on DUT board | No | — |
| 2 | Wire dipole antenna (868 MHz, 8.6 cm legs) OR SMA stub antenna | 1 | Wire dipole (per IMPLEMENTATION-PLAN.md:41) or SMA 868 MHz stub | balloon repo IMPLEMENTATION-PLAN.md:41-42 | Possibly on hand (wire is lab stock) | Maybe (wire is trivial) | <1 day |
| 3 | USB-C cable (DUT serial, ESP32-C3 SuperMini) | 1 | Standard USB-C data cable | Fork README: `/dev/ttyACM0` | On hand (CH340 enumerated on USB bus) | No | — |
| 4 | USB cable (reference TX serial) | 1 | Standard USB cable (board-dependent) | Fork README: `/dev/ttyUSB0` | On hand | No | — |
| 5 | Reference TX board (any MeshCore node, 868 MHz, SF8/BW62.5) | 1 | Any MeshCore node (e.g. second LR2021 board `c3-b`) | Fork README "Reference TX" row | On hand (`c3-b` per balloon-board-lock.py) | No | — |

**Total RF components needed: ZERO.** The measurement is over-the-air. The
DUT's SMA connector (already on the board) connects to a wire dipole or
stub antenna inside the chamber. The reference TX sits outside the chamber
with its own antenna. No coax, no feedthrough, no adapter.

### 3b. Optional conducted path (if over-the-air is rejected)

If the operator decides to run a coax from the DUT SMA through the chamber
wall to the reference TX (or a signal generator) outside:

| # | Item | Qty | Part number | On-hand | Must procure | Lead time |
|---|---|---|---|---|---|---|
| 1 | SMA male-to-male coax patch cable (30-50 cm, RG316 or RG178) | 1 | Amphenol RF SMA-male to SMA-male, RG316, 0.5m (e.g. ACX-1169-2M or equivalent) | Unknown (not on any record) | Yes | 2-5 days (Digi-Key/Mouser) |
| 2 | SMA bulkhead feedthrough connector (panel-mount SMA jack-to-jack) | 1 | Amphenol 132134 or equivalent SMA panel-mount jack-jack | Unknown (chamber unidentified, no feedthrough on record) | Yes (if chamber has no feedthrough) | 2-5 days |
| 3 | SMA male-to-male coax patch cable (short, 10-20 cm, DUT to feedthrough inside chamber) | 1 | RG316 SMA-male to SMA-male, 0.15m | Unknown | Yes | 2-5 days |
| 4 | SMA torque wrench (5/16 inch, 8 in-lb / 0.9 N-m) | 1 | Fujiya FTK-16SR or equivalent SMA torque wrench | Unknown | Recommended | 3-7 days |
| 5 | SMA connector saver / adapter (if instrument has N-type or BNC) | 0-1 | SMA-to-N or SMA-to-BNC adapter (only if instrument is not SMA) | N/A (no RF instrument on record) | Conditional | — |
| 6 | SMA dust caps (female and male) | 4 | Amphenol 132172 or generic SMA dust caps | Unknown | Recommended | 1-3 days |

### 3c. Serial / control path (always needed)

| # | Item | Qty | Part number | On-hand | Must procure | Lead time |
|---|---|---|---|---|---|---|
| 1 | USB-C cable (DUT, ESP32-C3 SuperMini) | 1 | Standard USB-C data cable | On hand (USB census: CH340 enumerated) | No | — |
| 2 | USB cable (reference TX) | 1 | Board-dependent USB cable | On hand | No | — |
| 3 | USB pass-through for chamber wall (if USB must penetrate) | 0-1 | USB bulkhead feedthrough or USB cable through door gasket | Unknown (chamber unidentified) | Conditional | — |

---

## STEP 4 — Procurement / fabrication flags

### Must be purchased (if conducted path is chosen)

1. **SMA bulkhead feedthrough connector** (1x) — 2-5 day lead time from
   Digi-Key/Mouser/Amphenol. Only needed if the chamber has no existing
   RF feedthrough. Since the chamber is unidentified, assume it does not.
2. **SMA coax patch cables** (2x, 0.15m and 0.5m, RG316) — 2-5 day lead
   time. Thin coax (RG316, OD 2.5mm) is preferred over RG178 for lower
   loss and better mechanical stability; both are rated to -40 C
   (PTFE dielectric).
3. **SMA torque wrench** (1x, 5/16", 8 in-lb) — 3-7 day lead time.
   Recommended for repeatable mating; finger-tight is insufficient for
   stable RF measurements.
4. **SMA dust caps** (4x) — 1-3 day lead time. Recommended for protecting
   unused connectors from frost/condensation.

### Already on hand

1. DUT board (SkyMapper Board A with LR2021, SMA edge-launch already
   soldered) — resource `c3-a`.
2. Reference TX board (`c3-b` or any MeshCore node).
3. USB cables for serial control.
4. Wire for dipole antenna (if over-the-air path is used) — standard
   lab stock.

### Must be fabricated

1. **Wire dipole antenna** (868 MHz) — 8.6 cm legs each side, cut from
   solid-core wire. <1 hour to fabricate. Only needed if no SMA stub
   antenna is on hand.

---

## STEP 5 — RF insertion loss and calibration concern

**Primary path (over-the-air):** No coax, no feedthrough, no adapters in
the RF path. The DUT receives via its own antenna (wire dipole or stub).
Insertion loss from added RF connectors is **zero** — there are no added
connectors. The over-the-air path has variable loss (distance, chamber
wall attenuation, antenna orientation), but this is not a connector-loss
issue; it is a link-budget issue. The edgescan protocol is a pass/fail
decode test, not a power measurement — it searches for the injected
offset band where the DUT still decodes the reference. As long as the
reference is decodable (RSSI above sensitivity), the absolute path loss
does not affect the measured offset. **No re-calibration is needed for
connector loss because there are no added connectors.**

**Optional conducted path:** If a coax + feedthrough is added, the
expected insertion loss is:
- SMA connector pair (mated): ~0.05-0.1 dB at 868 MHz per mated pair.
- RG316 coax, 0.5m: ~0.15 dB at 868 MHz (loss ~0.3 dB/m at 1 GHz).
- SMA bulkhead feedthrough: ~0.05-0.1 dB at 868 MHz.
- Total for a 2-cable + 1-feedthrough path: ~0.3-0.5 dB at 868 MHz.

This added loss is **negligible for the edgescan measurement** (which is
a decode-threshold test, not a power measurement). The reference TX
outputs +22 dBm and the DUT sensitivity is -143 dBm (BW62.5, SF12) — a
165 dB link budget. 0.3-0.5 dB of connector loss is irrelevant. **No
re-calibration is needed** to account for the added insertion loss of
the conducted path, because the measurement is a frequency-offset
decode threshold, not an absolute power or gain measurement.

The one calibration concern that DOES matter: the over-the-air path
through the chamber wall may attenuate the 868 MHz signal enough to
reduce the DUT's RSSI below the decode threshold if the chamber walls
are metal (a Faraday cage). If the chamber is a metal environmental
chamber, **over-the-air will not work at all** and the conducted path
is mandatory. This is a chamber-identification issue, not a connector
issue.

---

## Source summary

| claim | source | confidence |
|---|---|---|
| DUT RF connector = SMA edge-launch (sub-GHz, J1 "SMA-868") | `~/repos/balloon/tracker/hardware/hub_board_f33.kicad_pcb:165-179`, footprint `custom:SMA_Edge_Mount` | HIGH (physical PCB file) |
| DUT board has "SMA edge-launch connector" | `bench/condensation-risk/REPORT.md` line 305-306 (commit `65c9c3df`) | HIGH (prior bench report, re-read this session) |
| LR2021 module antenna interface = PCB pads (pin 9 ANTA, pin 10 2.4/S_ANTA), no connector | NiceRF LoRa2021 datasheet V1.3, Pin Definition table | HIGH (manufacturer datasheet, downloaded this session) |
| Measurement is over-the-air (reference TX at room temp, DUT in chamber) | Fork README `d7ae93fa:examples/passive_mapper/bench/README.md`, "Bench setup" table | HIGH (primary written source) |
| edgescan counts decoded packets, not RF power | `thermal_bench.py` `scan_edges()` function (d7ae93fa) | HIGH (source code, read via `git show`) |
| Reference TX = any MeshCore node, SF8/BW62.5, 868 MHz | Fork README "Reference TX" row | HIGH |
| Chamber feedthrough status = UNKNOWN | chamber-ownership `4b3ec9b5`, ramp-feasibility `79ea692e`, atcut-fit fleet board table | HIGH (verified in 3 prior reports) |
| No RF instrument on this host (no SDR/counter/VNA/GPSDO) | USB census in bench-owner `023c5e86`, atcut-fit `c4be4400` | HIGH (two independent USB enumerations) |
| DUT = `c3-a` (ESP32-C3 + LR2021, MAC b0:a6:04:00:96:dc, /dev/ttyACM0) | `balloon-board-lock.py` resource map, bench-owner report | HIGH |
| Reference TX = `c3-b` or any spare MeshCore node | `balloon-board-lock.py`, fork README | HIGH |
| Earlier schematic had U.FL (Molex 73412) but PCB uses SMA edge-launch | `v_c3_flight-erc.rpt:434-442` (U.FL), `hub_board_f33.kicad_pcb:165` (SMA) | HIGH (both files read this session) |
| Wire dipole antenna: 868 MHz, 8.6 cm legs | `IMPLEMENTATION-PLAN.md:41` (balloon repo) | HIGH |
| Coax type RG178/RG316, 30-50 cm length | `bench/ramp-feasibility/REPORT.md:174` (commit `79ea692e`) | MEDIUM (planning assumption in prior report) |

---

## Caveats and honest gaps

1. **The SkyMapper Board A PCB was not read directly.** The SMA
   edge-launch identification comes from the balloon repo's
   `hub_board_f33.kicad_pcb` (the carrier board family for the LR2021 +
   ESP32-C3) and from the condensation-risk report's verbatim statement.
   The actual SkyMapper board may be a different PCB revision. The
   condensation-risk report (line 305-306) independently confirms SMA
   edge-launch, so the identification is HIGH confidence even without
   reading the SkyMapper PCB file directly.

2. **The chamber is unidentified.** Whether it has an RF feedthrough
   port, is a metal Faraday cage (which would block over-the-air), or is
   a kitchen freezer (cable through door gasket) is unknown. This BOM
   covers both the no-feedthrough (over-the-air) and feedthrough
   (conducted) cases.

3. **No RF instrument exists on this host.** The BOM does not include
   items for connecting to a signal analyzer, VNA, or frequency counter
   because none is present. If the operator procures one, an SMA-to-N
   or SMA-to-BNC adapter may be needed (not included; the connector
   type depends on the specific instrument).

4. **The over-the-air path may fail if the chamber is metal.** A metal
   environmental chamber blocks RF; the DUT would receive nothing from
   the external reference TX. In that case the conducted path (coax +
   feedthrough) is mandatory, and the feedthrough must penetrate the
   metal wall. This is flagged but not resolved — it requires chamber
   identification, which is a separate fleet card.

5. **Part numbers for SMA coax and feedthrough are representative, not
   sourced from an existing inventory.** No inventory system of record
   exists on this host (occupancy-booking report `bffc7f9d`: no booking
   system, no parts database). The Amphenol part numbers cited are
   industry-standard SMA components; verify availability and exact
   match at point of procurement.

---

## Nothing fabricated

Every connector identification is cited to a file read this session
(PCB, datasheet, or prior bench report). The measurement-chain analysis
is from the fork README and source code read via `git show`. No physical
hardware was inspected (the DUT is not attached to any fleet host). The
chamber feedthrough status is reported as UNKNOWN, not assumed. Part
numbers for procurement items are labeled as representative.