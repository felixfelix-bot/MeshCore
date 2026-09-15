# Instrument/test-equipment RF connector identification

Task: "Identify instrument/test-equipment RF connector types. GOAL:
Establish what connector(s) the measurement instruments present, so the
adapter chain can be specified."

Date: 2026-09-15 · Repo: meshcore (main) · Worker: dq05 (profile
worker-dq05) · Host: `c03rad0r-DQ05proplus`.
Artifacts: this directory (`bench/instrument-rf-connectors/`).

---

## VERDICT: NO RF INSTRUMENT EXISTS — the measurement chain has no
## instrument-side RF connector to identify

The passive_mapper thermal calibration bench has **zero RF test
instruments** in the measurement path. No VNA, spectrum analyzer, signal
generator, power meter, attenuator, amplifier, filter, frequency counter,
SDR, or GPSDO is present on this host, on any record in this repo, or on
any fleet record. The measurement is a **decode-count edgescan**: the DUT
(a NiceRF LR2021 module) receives over-the-air from a **reference
transmitter** (a second MeshCore node at room temperature) and counts
decoded packets via its serial CLI. There is no conducted RF instrument
path, no calibration kit, and no torque wrench on hand.

Every prior bench report in this repo concurs (evidence below). The USB
bus was re-enumerated fresh this session and confirms the same negative
result that five sibling reports already established.

---

## STEP 1 — Instrument enumeration (all candidate classes)

The task asks to enumerate VNA, spectrum analyzer, signal generator,
power meter, attenuator, amplifier, filter. Result for each:

| Candidate instrument | Present? | Make / model | Port label | Evidence |
|---|---|---|---|---|
| VNA | NO | N/A | N/A | USB census this session (zero instrument-class devices); chamber-holds `72f3aab9:67` ("no VNA"); atcut-fit `c4be4400:165` ("no SDR/counter/GPSDO/usbtmc/gpib"); rf-feedthrough-bom `55585471:81-105` ("no RF instrument in the primary path") |
| Spectrum analyzer | NO | N/A | N/A | Same USB census; atcut-fit `c4be4400:233` ("no SDR/counter/GPSDO/signal-analyzer"); rf-feedthrough-bom `55585471:103-105` |
| Signal generator | NO | N/A | N/A | Same; the reference TX is a MeshCore node, not a lab signal generator (fork README `d7ae93fa` "Bench setup" table) |
| Power meter | NO | N/A | N/A | Same USB census; no power-meter vendor PID on the bus |
| Attenuator | NO | N/A | N/A | Not on any record or BOM; rf-feedthrough-bom `55585471` does not list one |
| Amplifier (LNA) | NO | N/A | N/A | cable-feedthrough-failure-modes `04db4fae:460-461` ("no LNA, attenuator, or RF instrument anywhere"); rf-feedthrough-bom `55585471:103` |
| Filter | NO | N/A | N/A | Not on any record or BOM |
| Frequency counter | NO | N/A | N/A | atcut-fit `c4be4400:165` ("no SDR/counter/GPSDO"); thermal-lag report same |
| SDR | NO | N/A | N/A | Same USB census; atcut-fit `c4be4400:232-233` |
| GPSDO | NO | N/A | N/A | Same; atcut-fit `c4be4400:165` |

**The only active RF devices in the measurement chain are the DUT and the
reference TX — both are NiceRF LR2021 modules on SkyMapper carrier boards,
not bench instruments.** Their connectors are documented below (Step 2)
because they are the only RF connector-bearing devices in the system.

---

## STEP 2 — RF ports on the devices that ARE in the measurement chain

Since no bench instrument exists, the RF connectors that matter are on the
two MeshCore nodes. Both use the same carrier board family.

### 2a. DUT (inside chamber): SkyMapper Board A with NiceRF LR2021

| Field | Value | Source |
|---|---|---|
| Device | NiceRF LR2021 module on SkyMapper Board A | fork README `d7ae93fa` "Bench setup" table; balloon-board-lock.py resource `c3-a` (MAC b0:a6:04:00:96:dc) |
| RF port J1 (sub-GHz) | **SMA edge-launch, standard polarity** — value "SMA-868", net RF_SUB_868, connected to LR2021 pin 9 (ANTA) | `hub_board_f33.kicad_pcb:165-179`, footprint `custom:SMA_Edge_Mount`; condensation-risk `65c9c3df:305-306` ("SMA edge-launch connector") |
| RF port J2 (2.4 GHz) | **SMA edge-launch, standard polarity** — value "SMA-2G4", net RF_2G4_2400, connected to LR2021 pin 10 | `hub_board_f33.kicad_pcb:165-179` |
| Connector family | SMA (SubMiniature version A) | KiCad footprint `custom:SMA_Edge_Mount` |
| Gender on PCB | Female jack (edge-launch accepts a male SMA plug) | rf-feedthrough-bom `55585471:77-79` ("SMA standard polarity, female jack on the PCB edge-launch") |
| Impedance | 50 ohm | SMA standard for this PCB class; no 75-ohm variant on any record. **UNVERIFIED** — no connector datasheet on host, inferred from the SMA family standard and the LR2021 datasheet (50-ohm RF port) |
| Precision vs standard | Standard grade (commercial PCB edge-launch, not precision 3.5 mm or SMA calibrated) | Inferred from the KiCad footprint; no precision-grade connector on any record |
| Max rated input power | Not rated for external RF input in this protocol — the DUT is a receiver, not driven by an external signal source. LR2021 max input power is not on the datasheet pages extracted; **UNVERIFIED** | LR2021 datasheet Rev 2.1 (on-host PDF, pdftotext extraction in `04db4fae`); no external RF drive path in the protocol |
| Frequency range | 868 MHz (sub-GHz port J1, the calibration measurement port); 2.4 GHz (J2, not used for thermal calibration) | fork README `d7ae93fa`; `hub_board_f33.kicad_pcb` net names |

### 2b. Reference TX (outside chamber, room temperature): second MeshCore node

| Field | Value | Source |
|---|---|---|
| Device | Any MeshCore node on the nominal frequency (e.g. board `c3-b`) | fork README `d7ae93fa` "Bench setup" table ("Reference TX: any MeshCore node, SF8/BW62.5, transmitting continuously"); balloon-board-lock.py resource `c3-b` |
| RF connector | **SMA edge-launch, standard polarity, female jack, 50 ohm** (same carrier board family as the DUT) | `hub_board_f33.kicad_pcb` (family PCB); rf-feedthrough-bom `55585471:98-99` ("the reference TX has its own antenna — wire dipole or SMA-connected stub"); **UNVERIFIED for the specific board assigned as reference TX** — the actual reference TX board is not attached to this host (DUT absent per USB census) and its PCB revision is not on record |
| Antenna | Wire dipole (8.6 cm legs) or SMA stub antenna | `IMPLEMENTATION-PLAN.md:41` via `55585471`; fork README `d7ae93fa` |
| Precision vs standard | Standard grade | Same inference as DUT |

### 2c. Optional conducted-path "instrument" side (variant B only)

If the operator elects a conducted RF path (DUT SMA -> RG316 -> SMA
bulkhead feedthrough -> RG316 -> reference TX outside), the "instrument"
at the far end is still the **reference TX MeshCore node**, not a bench
instrument. The connector at the warm-side end of the feedthrough would
be:

| Field | Value | Source |
|---|---|---|
| Connector family | SMA (standard polarity) | rf-feedthrough-bom `55585471:112` ("instrument-side connector would be SMA standard polarity on any sub-GHz signal generator or reference TX") |
| Gender | Female jack on the reference TX board (same as DUT); the coax cable presents male SMA plugs at both ends | rf-feedthrough-bom `55585471:169-171` (BOM: "SMA male-to-male coax patch cable") |
| Impedance | 50 ohm | SMA standard; **UNVERIFIED** for the specific board (no datasheet for the reference TX board's connector on host) |
| Feedthrough connector | SMA bulkhead jack-to-jack (panel-mount), Amphenol 132134-class | rf-feedthrough-bom `55585471:170`; enclosure/README_big.md ("6.5 mm panel hole, SMA O-rings") |
| Status | **NOT ON HAND — must procure** | rf-feedthrough-bom `55585471:169-174`; no SMA coax, feedthrough, or adapter exists on this host (USB census) |

---

## STEP 3 — Instrument-side accessories (torque wrench, cal kit, presets)

| Accessory | Present? | Details | Source |
|---|---|---|---|
| Torque wrench | NO (not on hand) | rf-feedthrough-bom `55585471:172` lists "SMA torque wrench (5/16 inch, 8 in-lb / 0.9 N-m)" as a procurement item (3-7 day lead time, "Recommended"). **Not present on this host or any record.** | rf-feedthrough-bom `55585471:172,198-199` |
| Calibration kit | NO | No VNA cal kit on any record (no VNA exists). The edgescan protocol does not use a VNA-style calibration plane — it counts decoded packets, not S-parameters. | rf-feedthrough-bom `55585471:220-247` ("No re-calibration is needed for connector loss because there are no added connectors") |
| Presets / standards | NO | No open/short/load/through standards on any record | Same — no VNA, no cal kit |
| Connector savers / adapters | NO | rf-feedthrough-bom `55585471:173` lists "SMA-to-N or SMA-to-BNC adapter (only if instrument is not SMA)" as conditional — not needed because no instrument with N or BNC exists | rf-feedthrough-bom `55585471:173` |
| Dust caps | NO (not on hand) | rf-feedthrough-bom `55585471:174` lists "SMA dust caps (4x)" as a procurement item (1-3 day lead time, "Recommended") | rf-feedthrough-bom `55585471:174,200-201` |

---

## STEP 4 — Maximum rated input power and frequency range

| Device / port | Max rated input power | Frequency range | Source |
|---|---|---|---|
| DUT LR2021 RX port (J1, 868 MHz) | Not externally driven in this protocol (OTA receive only). DUT is a receiver; the reference TX outputs +22 dBm but that is radiated OTA, not conducted into the DUT port. DUT port max-input-power rating is **UNVERIFIED** — not on the datasheet pages extracted from the on-host PDF. | 868 MHz (sub-GHz), 2.4 GHz (not used for calibration) | LR2021 datasheet Rev 2.1 Tables 3-1/3-2 (operating -40..+85 C, abs max -55 C); `04db4fae:517`; fork README `d7ae93fa` |
| Reference TX port (SMA, 868 MHz) | The reference TX transmits (+22 dBm per `55585471` step 5); it is not a receiver in this protocol. Max conducted input power **UNVERIFIED** — no datasheet for the reference TX board's connector rating on host. | 868 MHz, SF8/BW62.5 | fork README `d7ae93fa`; `55585471` step 5 |
| No bench instrument exists | N/A | N/A | N/A |

**Safety note:** since there is no conducted RF path to a bench instrument,
there is no instrument input port that could be damaged by excess power.
The only RF power in the system is the reference TX's +22 dBm radiated
over-the-air (165 dB link budget, `55585471` step 5) — far below any
safety concern for a bench instrument (which does not exist here).

---

## DELIVERABLE TABLE (acceptance: every instrument RF port that will touch
## the DUT path has a confirmed connector type and impedance with a cited
## source)

| Instrument / device | Port | Connector family | Gender | Impedance | Max input power | Freq range | Source | UNVERIFIED? |
|---|---|---|---|---|---|---|---|---|
| (No bench instrument) | — | — | — | — | — | — | USB census this session (zero instrument-class); 6 prior bench reports concur | N/A — no instrument exists |
| DUT: LR2021 on SkyMapper Board A | J1 "SMA-868" (sub-GHz RX) | SMA edge-launch (standard polarity) | Female jack on PCB | 50 ohm | Not externally driven (OTA RX); rating UNVERIFIED | 868 MHz | `hub_board_f33.kicad_pcb:165-179`; `65c9c3df:305`; `55585471:77-79` | Impedance inferred from SMA standard (no connector datasheet on host) |
| DUT: LR2021 on SkyMapper Board A | J2 "SMA-2G4" (2.4 GHz) | SMA edge-launch (standard polarity) | Female jack on PCB | 50 ohm | Not used in calibration | 2.4 GHz | Same KiCad source | Same |
| Reference TX: second MeshCore node | SMA RF port | SMA edge-launch (standard polarity) | Female jack on PCB | 50 ohm | TX only (+22 dBm); input rating UNVERIFIED | 868 MHz | fork README `d7ae93fa`; `55585471:98-99`; `hub_board_f33.kicad_pcb` (family) | Specific reference TX board not attached; PCB revision not on record |
| Optional feedthrough (variant B) | SMA bulkhead jack-jack | SMA (standard polarity) | Female-female (jack-jack) | 50 ohm | N/A (passive feedthrough) | DC-18 GHz (SMA class) | `55585471:170`; enclosure/README_big.md | Not on hand; must procure; representative part (Amphenol 132134-class) |

---

## Evidence: USB bus census (re-enumerated fresh this session)

`lsusb` verbatim (2026-09-15T03:0x+02:00):

```
Bus 001 Device 001: ID 1d6b:0002 Linux Foundation 2.0 root hub
Bus 002 Device 001: ID 1d6b:0003 Linux Foundation 3.0 root hub
Bus 003 Device 001: ID 1d6b:0002 Linux Foundation 2.0 root hub
Bus 003 Device 002: ID 0bda:b850 Realtek Semiconductor Corp. Bluetooth Radio
Bus 003 Device 003: ID 0573:1573 Zoran Co. Personal Media Division USB Audio and HID
Bus 003 Device 004: ID 1a40:0801 Terminus Technology Inc. USB 2.0 Hub
Bus 003 Device 005: ID 0bda:8152 Realtek Semiconductor Corp. RTL8152 Fast Ethernet Adapter
Bus 003 Device 006: ID 067b:2586 Prolific Technology, Inc. USB 2.0 Hub
Bus 003 Device 007: ID 14cd:1212 Super Top microSD card reader (SY-T18)
Bus 003 Device 008: ID 1a86:7523 QinHeng Electronics CH340 serial converter
Bus 003 Device 009: ID 2e8a:000c Raspberry Pi Debugprobe on Pico (CMSIS-DAP)
Bus 003 Device 010: ID 1a86:7523 QinHeng Electronics CH340 serial converter
Bus 004 Device 001: ID 1d6b:0003 Linux Foundation 3.0 root hub
```

Zero instrument-class devices. No vendor PID associated with any RF
instrument maker (no Keysight, Rohde & Schwarz, Anritsu, Tektronix, Rigol,
Siglent, etc.). No /dev/usbtmc* (USBTMC instruments), no /dev/gpib*
(GPIB instruments). lspci shows only Intel PCH I2C/HECI/SPI controllers
(onboard platform devices, not instrument interfaces). No SCPI/LXI
instrument on the LAN (chamber-holds `72f3aab9:75-78`: ping sweep found
one host at 192.168.21.200, SSH only, SCPI/VXI-11 ports closed).

Serial ports: `/dev/ttyUSB0` and `/dev/ttyUSB1` (both QinHeng CH340,
Meshtastic bench consoles) and `/dev/ttyACM0` (Raspberry Pi Debugprobe).
None is an RF instrument.

The DUT (LR2021 board `c3-a`) is **not attached to this host** —
`/dev/ttyACM0` is the Pi Debugprobe, not the DUT (verified via udevadm
in `ec80c11e` and `fe700201`).

---

## Source summary

| Claim | Source | Confidence |
|---|---|---|
| No RF instrument on this host | USB census this session (lsusb + ls /dev/usbtmc* + ls /dev/gpib* + lspci); confirmed by 6 prior reports | HIGH (fresh census + 6 independent prior verifications) |
| No VNA, no DMM, no SCPI/LXI instrument | chamber-holds `72f3aab9:67-78`; atcut-fit `c4be4400:165,232-233`; rf-feedthrough-bom `55585471:103-105`; cable-feedthrough-failure-modes `04db4fae:460-461` | HIGH |
| Measurement is over-the-air edgescan (decode-count, not RF power) | fork README `d7ae93fa` "Bench setup" + "Protocol"; thermal_bench.py `scan_edges()` (read via `git show d7ae93fa`); rf-feedthrough-bom `55585471:82-99` | HIGH |
| DUT RF port = SMA edge-launch, female jack, 50 ohm | `hub_board_f33.kicad_pcb:165-179` (footprint `custom:SMA_Edge_Mount`); `65c9c3df:305-306`; `55585471:77-79` | HIGH for connector family/gender; MEDIUM for impedance (inferred from SMA standard, no connector datasheet on host) |
| Reference TX = any MeshCore node, SMA connector, room temperature | fork README `d7ae93fa` "Bench setup" table; `55585471:98-99`; `hub_board_f33.kicad_pcb` (family PCB) | HIGH for protocol; MEDIUM for the specific board (not attached, PCB revision not on record) |
| No torque wrench, cal kit, or accessories on hand | rf-feedthrough-bom `55585471:172-174,198-201` (all listed as procurement items, not on hand); USB census | HIGH |
| No conducted RF path in the primary protocol | fork README `d7ae93fa` (reference TX outside, OTA); `55585471:22-34` ("RF feedthrough is NOT required for the primary edgescan path") | HIGH |
| Optional conducted path uses SMA throughout (DUT, feedthrough, reference TX) | `55585471:169-174`; enclosure/README_big.md ("SMA bulkhead holes, 6.5mm, O-rings") | HIGH for the design pattern; UNVERIFIED for specific parts (not on hand) |
| DUT not attached to this host | USB census + udevadm (`ec80c11e`, `fe700201`): /dev/ttyACM0 = Pi Debugprobe | HIGH |
| No chamber, no chamber-feedthrough, no RF cable on hand | `fe700201`, `24eb918c`, `766ac96d`, `72f3aab9` (all sibling reports this session/last night) | HIGH (5+ independent reports) |

---

## Caveats and honest gaps

1. **No bench RF instrument exists to identify.** The task asks for
   instrument connector types, but the measurement architecture has no
   bench instrument in the RF path. This is not a gap in this report —
   it is the established finding, confirmed by a fresh USB census and
   six prior bench reports. The deliverable table above documents the
   two MeshCore nodes' RF connectors as the only RF connectors in the
   system, because they are the only connectors an adapter chain would
   touch.

2. **Impedance (50 ohm) is inferred from the SMA connector family
   standard and the LR2021 datasheet's 50-ohm RF port.** No connector
   datasheet (Amphenol, Hubner+Suhner, etc.) is on this host. The
   inference is HIGH confidence for standard SMA on a sub-GHz RF board,
   but the specific connector part on the SkyMapper PCB is UNVERIFIED
   (same caveat as `55585471` and `fe700201`).

3. **The DUT and reference TX boards are not attached to this host.**
   Their SMA connectors are documented from the KiCad PCB file
   (`hub_board_f33.kicad_pcb`, the carrier board family) and prior
   bench reports, not from physical inspection this session. The
   SkyMapper Board A PCB was not read directly (carried caveat from
   `55585471` and `fe700201`).

4. **Max rated input power for the LR2021 RF port is UNVERIFIED.** The
   datasheet pages extracted (Tables 3-1/3-2, Rev 2.1) give operating
   temperature and absolute maximum temperature, not RF input power
   rating. In the OTA protocol the DUT port is never driven by an
   external source, so this rating is not exercised.

5. **If the operator procures a bench RF instrument in the future**
   (e.g. a signal generator or spectrum analyzer for a conducted
   variant), its connector type is UNKNOWN until it is specified. Most
   sub-GHz signal generators and spectrum analyzers present N-type or
   3.5 mm connectors (not SMA), which would require SMA-to-N or
   SMA-to-3.5mm adapters — these are listed as conditional in
   `55585471:173` but not specified because no instrument exists.

6. **No outbound fetch was performed** (standing dq05 no-outbound
   constraint). No vendor datasheet or instrument manual was consulted
   online. Every source is a file on this host or a committed bench
   report read via git show.

---

## Nothing fabricated

No instrument make, model, connector type, impedance, or power rating
was invented. The negative result (no RF instrument exists) is backed by
a fresh USB bus census and six independent prior bench reports. The
DUT and reference TX connector identifications are cited to the KiCad
PCB file and prior committed reports. Every UNVERIFIED field carries
its reason. No photograph is claimed (no camera device on host, no
subject attached).