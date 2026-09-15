# DUT-side RF port connector identification — SkyMapper Board A (c3-a)

Task (fleet card `meshcore:t_b1049504`): "Identify DUT-side RF port connector
type(s) and count. GOAL: Establish exactly what connector(s) exit the
device-under-test (DUT) on its RF port(s) — no assumptions."

Date: 2026-09-15 · Repo: meshcore (main) · Worker: dq05 (profile worker-heavy)
· Host: `c03rad0r-DQ05proplus`. Artifacts: this directory
(`bench/dut-rf-ports/`).

Design files cited live in the sibling repo `~/repos/balloon` (working-tree
HEAD `6c18d6a3`) and in meshcore git history (`d7ae93fa`). Every claim below
was read fresh this session from the named file; nothing is taken from a
prior report without re-reading its underlying source.

---

## VERDICT SUMMARY

**The DUT's LoRa measurement path has ZERO RF connectors.** Both RF exits of
the LR2021 radio are **soldered wire dipoles on bare castellated module pads**
— no SMA, no U.FL, no MMCX, no connector of any kind:

- **Port 1 — ANT_SUBGHZ (LR2021 pin 9, sub-GHz 868 MHz): NO CONNECTOR.**
  Wire dipole soldered to the bare pad. On-record length: "16.4cm wire
  @ 868 MHz" (`tracker/hardware/footprints/wiring-dev-board.csv`, row
  `ANT_SUBGHZ`); per-leg spec "8.6 cm (λ/4 ≈ 86.4 mm), stiff copper wire
  30 AWG, bend 180°" (`docs/breadboard-wiring-guide.md:54-56`); flight-plan
  equivalent "AE1 | Sub-GHz antenna pad | Wire dipole 16.4cm | THT pad"
  (`tracker/hardware/FLIGHT-BOARD-PLAN.md:85`).
- **Port 2 — ANT_24GHZ (LR2021 pin 10, 2.4 GHz): NO CONNECTOR.** Same class:
  "Wire dipole, 3.1cm wire @ 2.4 GHz" (`wiring-dev-board.csv`, row
  `ANT_24GHZ`); flight-plan "AE2 | 2.4 GHz antenna pad | Wire dipole 3.1cm |
  THT pad" (`FLIGHT-BOARD-PLAN.md:86`). One documented variant says pin 10
  may instead be "leave floating or 50Ω term"
  (`breadboard-wiring-guide.md:38`) — physical disposition of THIS board's
  pin 10 is UNVERIFIED (see §6).
- **Port 3 — ESP32-C3 SuperMini onboard U.FL (WiFi/BLE 2.4 GHz): U.FL (I-PEX)
  female jack** — but this port belongs to the MCU's own 2.4 GHz radio, NOT
  to the LR2021 measurement path. Source:
  `tracker/hardware/footprints/esp32c3-mini-v1.json` → `connectors.antenna:
  "U.FL (I-PEX) for external antenna"`, `antenna_accessories: "U.FL-to-SMA
  pigtail + 3dBi SMA antenna included"`. Physical presence of this U.FL on
  c3-a's specific SuperMini unit is UNVERIFIED (no physical inspection;
  some SuperMini batches omit it).

**Connector count on the RF path the thermal-bench campaign measures: 0.**
Total coaxial connectors exiting the DUT assembly: 1 (the SuperMini's U.FL,
WiFi/BLE only, outside the measured path).

**Correction of prior reports.** Three committed reports identify the DUT RF
port as "SMA edge-launch" (`55585471` rf-feedthrough-bom §1a;
`65c9c3df` condensation-risk line ~305 "SMA edge-launch connector";
`bfc2a899` connector-adapter-bom line A1). All three trace to
`tracker/hardware/hub_board_f33.kicad_pcb:165-179` — which is the
**"Balloon Hub V2 — F33 2W PA"** board hosting the **LoRa2021F33-2G4**
module (39×21 mm, +33 dBm PA variant, different pinout). That is NOT the
bench DUT: `bfc2a899` itself flagged this as open risk R1 ("the SkyMapper
Board A PCB was never read directly"). The DUT's own wiring record resolves
R1 — the answer is **no connector at all**, not SMA. See §5.

---

## 1. DUT identity — evidence chain (all read this session)

| # | Fact | Source (verbatim anchor) |
|---|---|---|
| 1 | DUT = "NiceRF LR2021 board (SkyMapper Board A or a spare)" running env `LR2021_passive_mapper`, serial CLI `/dev/ttyACM0` | fork bench README @ meshcore `d7ae93fa`, `examples/passive_mapper/bench/README.md` "Bench setup" table, DUT row |
| 2 | Fleet resource `c3-a` = "ESP32-C3 + LR2021 board A (MAC b0:a6:04:00:96:dc, /dev/ttyACM0)" | `~/repos/balloon/tools/balloon-board-lock.py` RESOURCES block |
| 3 | Env `LR2021_passive_mapper` extends `NiceRF_LR2021`, which sets `board = esp32c3_supermini` (= ESP32-C3_Mini_V1 / SuperMini carrier, bare LR2021 via SPI) | meshcore @ `d7ae93fa`, `variants/nicerf_lr2021/platformio.ini` `[NiceRF_LR2021]` + `[env:LR2021_passive_mapper]` |
| 4 | Firmware GPIO map matches the wiring CSV pin-for-pin: SCK=6/D6→pin5, MISO=2/D2→pin3, MOSI=7/D7→pin4, NSS=10/D10→pin6, BUSY=4/D4→pin7, RST=3/D3→pin14, DIO9=5/D5→pin15 | `platformio.ini` build_flags (`-D P_LORA_*`) vs `wiring-dev-board.csv` rows |
| 5 | The same CSV documents the antenna exits: pin 9 = "Wire dipole, 16.4cm wire @ 868 MHz", pin 10 = "Wire dipole, 3.1cm wire @ 2.4 GHz" | `wiring-dev-board.csv` rows `ANT_SUBGHZ`, `ANT_24GHZ` |

Chain 1→5 ties the DUT (SkyMapper Board A = c3-a) to the ESP32-C3 SuperMini
+ bare-LR2021 hand-wired assembly whose antenna exits are soldered wires.
"SkyMapper" appears ONLY in meshcore bench/fork docs (zero hits in the
balloon repo working tree and git history, re-verified this session) — it is
the campaign/board nickname for the c3-a assembly, not a distinct PCB.

**Radio MPN (task step 2):** "NiceRF LoRa2021" (LR2021 Gen4 chip, 18-pin
castellated, 19.72×15×2.2 mm, 4 units on hand) — `docs/inventory.md:16` +
pin detail block. No more specific orderable part string exists on any
record on this host.
**Carrier MPN:** "ESP32-C3_Mini_V1", manufacturer "Maker go", alias
"ESP32-C3 Super Mini", 22.52×18.0 mm, 4 MB flash —
`footprints/esp32c3-mini-v1.json` (`board`, `manufacturer`, `aliases`,
`dimensions_mm`).

---

## 2. Per-port deliverable table (task step 4)

| Port | Connector family | Gender / polarity | Frequency rating | SOURCE | Status |
|---|---|---|---|---|---|
| ANT_SUBGHZ — LR2021 pin 9 (ANTA), sub-GHz RX path measured by the edgescan campaign | **NONE — soldered wire dipole on bare castellated pad** (wire is the antenna; there is no mating interface) | N/A (no mating interface exists) | 868 MHz (record: "16.4cm wire @ 868 MHz"; per-leg λ/4 ≈ 86.4 mm, 30 AWG copper) | `wiring-dev-board.csv` row ANT_SUBGHZ; `breadboard-wiring-guide.md:16,37,54-56`; `FLIGHT-BOARD-PLAN.md:85`; module pad definition: LoRa2021 Module Datasheet V1.3 §7 pin table (pin 9 ANTA "sub-GHz band antenna interface, external 50-ohm antenna") | Document-based (HIGH, 4 concordant records); physical state UNVERIFIED — board not attached |
| ANT_24GHZ — LR2021 pin 10 (2.4/S_ANTA) | **NONE — soldered wire dipole on bare pad** (documented alternative: "leave floating or 50Ω term") | N/A | 2.4 GHz (record: "3.1cm wire @ 2.4 GHz") | `wiring-dev-board.csv` row ANT_24GHZ; `breadboard-wiring-guide.md:38`; `FLIGHT-BOARD-PLAN.md:86`; datasheet V1.3 §7 (pin 10 "2.4G and S band antenna interface, external 50-ohm antenna") | Document-based; THIS board's actual pin-10 disposition (dipole vs floating vs terminated) UNVERIFIED — no physical board |
| SuperMini onboard ANT — ESP32-C3 WiFi/BLE radio | **U.FL (I-PEX)** per board record | Female jack (U.FL receptacle on PCB; mating U.FL plug is male) | 2.4 GHz use (802.11 b/g/n + BLE 5.0); U.FL family RF rating itself not on record | `esp32c3-mini-v1.json` `connectors.antenna` + `wireless` | Document-based; physical population on c3-a's unit UNVERIFIED (SuperMini clones vary); NOT part of the LoRa measurement path |

**Count: 0 RF connectors on the LR2021 measurement path; 1 U.FL on the
assembly (WiFi/BLE only).**

Impedance note: the LR2021 datasheet V1.3 specifies both antenna interfaces
as "external 50-ohm antenna" — the wire dipoles are the 50 Ω load, not a
connector.

---

## 3. Datasheet / design cross-check (task steps 2-3)

**LoRa2021 Module Datasheet V1.3** — recovered this session from balloon git
history (commit `36952f72`, 2026-06-27, path then
`docs/assets/lr2021/LoRa2021-Module-Datasheet-V1.3.pdf`; the file is no
longer in the working tree). §7 "Pin definition": pin 9 = ANTA / ANT —
"sub-GHz band antenna interface, external 50-ohm antenna"; pin 10 =
2.4/S_ANTA — "2.4G and S band antenna interface, external 50-ohm antenna".
**The module presents castellated solder pads, not a connector** — confirmed
by the KiCad footprint `custom:LoRa2021_Castellated`
(`hub_board_v1.kicad_pcb:134-153`, pads 9/10 = nets `RF_SUB_868` /
`RF_2G4_2400`). Features list: Sub-GHz 433/470/868/915 MHz; high band
1900/2400 MHz.

**Task step 3 (pigtail):** No pigtail exists or is expected on the LR2021
path — there is no U.FL/IPEX/MMCX on that path to pigtail from. The only
pigtail on record anywhere in the DUT assembly is the SuperMini's
**U.FL-to-SMA pigtail + 3dBi SMA antenna**, documented as an *included
accessory* of the ESP32-C3_Mini_V1 kit (`esp32c3-mini-v1.json`,
`antenna_accessories`). **Pigtail MPN: not on any record (TBD)**; the gender
of its far-end SMA is also not stated on record (industry-typical pigtails
end in an SMA female jack, but that is NOT recorded here as fact —
UNVERIFIED).

---

## 4. Physical inspection (task step 1) — NOT PERFORMED

Fresh USB census this session: 2× QinHeng CH340 serial + Pi Debugprobe; no
ESP32-C3 or LR2021 device on any fleet host. The DUT is not attached, so
magnifier/caliper inspection, thread-pitch measurement, body/center-pin
diameter, dielectric and gender verification were **impossible** — and per
the design files there is no connector to measure on the RF path anyway.
All connector findings above are document-based; every physical dimension
is marked UNVERIFIED in §6.

---

## 5. Why prior reports said "SMA" — board-family disambiguation

Five distinct hardware artifacts carry LR2021-family radios; only ONE has
SMA, and it is not the DUT:

| Board / artifact | Radio | RF exit | On record as | Is it the DUT? |
|---|---|---|---|---|
| c3-a bench assembly ("SkyMapper Board A") | bare NiceRF LoRa2021, 18-pin castellated | **Soldered wire dipoles, pins 9/10 — NO connector** | `wiring-dev-board.csv` + `breadboard-wiring-guide.md` + fork README `d7ae93fa` + board-lock `c3-a` + firmware env chain | **YES — the DUT** |
| `hub_board_v1.kicad_pcb` "Balloon Hub V1 — Non-PA (GPIO fix)" | bare LoRa2021 (`custom:LoRa2021_Castellated`) | AE1/AE2 = THT test-point pads, 2.0 mm dia, nets RF_SUB_868 / RF_2G4_2400 — wire dipole pads, NO connector (`hub_board_v1.kicad_pcb:233-243`, `FLIGHT-BOARD-PLAN.md:85-86`) | grep for SMA/U.FL/BNC/MMCX/N-type footprints: **0 hits** | No (flight hub family, same antenna concept as DUT) |
| `hub_board_diy/` | LoRa2021F33-2G4 (sch: `LoRa2021F33_Left/Right`) | PCB (86 lines) contains **no RF connector footprint at all** | grep 0 hits | No |
| `hub_board_f33.kicad_pcb` "Balloon Hub V2 — F33 2W PA" | **LoRa2021F33-2G4** (39×21 mm, +33 dBm PA, different pinout) | **J1 "SMA-868" + J2 "SMA-2G4", `custom:SMA_Edge_Mount`** (`hub_board_f33.kicad_pcb:165-179`) — the ONLY SMA board in the family | `55585471` §1a, `65c9c3df:~305`, `bfc2a899` A1 cite it as "the DUT" | **NO — different radio module AND different board** |
| `schematics/v_c3_flight.kicad_sch` + `output/v_c3_flight_final.kicad_pcb` | **LR2021F33** + ESP32-C3-WROOM-02 + RFM9XW | U.FL Molex MCRF 73412-0110 — ANT1 (and ANT2 in sch; the fabricated PCB carries only ANT1, net `RF_OUT`) (`v_c3_flight.kicad_sch:3303-3412`, `v_c3_flight_final.kicad_pcb:105-111`) | ERC rpt `v_c3_flight-erc.rpt:434-442` (footprint-not-found) | No (flight-board design exercise) |

The prior SMA identification (a) read the wrong board (F33 2W-PA hub, not
the c3-a bench assembly) and (b) treated a carrier-board-family file as the
DUT's own PCB — the same caveat `55585471`/`bfc2a899` themselves recorded.
Two secondary errata in the record, resolved here:

- `~/repos/balloon/IMPLEMENTATION-PLAN.md:42` — "Connect antennas to U.FL
  connectors on LoRa2021 modules": **cannot be executed literally**; the
  bare LoRa2021 has no U.FL (datasheet V1.3 §7). `55585471:70-72` reads this
  line as referring to "the bare-module breadboard prototype phase", but a
  bare module has no U.FL in any phase — the plan line is an erratum (or
  anticipated a never-built carrier). No U.FL was ever soldered to an
  LR2021 on record.
- Antenna-length discrepancy (not connector-relevant, recorded for
  completeness): CSV/plan say the sub-GHz dipole is **16.4 cm** overall;
  the wiring guide says **8.6 cm per leg** (= 17.2 cm tip-to-tip, λ/4
  ungapped). The 0.8 cm difference (feed gap / end-effect shortening) is
  not explained on any record — physical as-built length UNVERIFIED.

---

## 6. UNVERIFIED register (acceptance: zero unqualified guesses)

| # | Item | Why unverified |
|---|---|---|
| U1 | Physical RF state of c3-a (are the wire dipoles actually soldered? pin-10 disposition? SuperMini U.FL populated?) | DUT not attached to any fleet host (USB census); no photo of c3-a exists on any record (only pinout/reference images found) |
| U2 | Wire dipole as-built dimensions (16.4 cm vs 2×8.6 cm) | Two on-record specs differ; no measurement record |
| U3 | SuperMini U.FL pigtail MPN and far-end SMA gender | `esp32c3-mini-v1.json` names the accessory but no MPN/gender anywhere on host |
| U4 | U.FL RF frequency rating | No connector datasheet on host; only the radio's 2.4 GHz use is on record |
| U5 | Thread pitch / body Ø / center-pin Ø / dielectric / gender checks of task step 1 | Not measurable: no connector exists on the RF path per design files, and no physical board is attached |
| U6 | More specific radio order code than "NiceRF LoRa2021" | Not on any record on this host |

---

## 7. Downstream impact (for the BOM consumers)

`bfc2a899` (connector-adapter-bom) Path B chain — RG316 SMA-m/m assemblies,
SMA bulkhead, saver, termination — has **nothing to mate to on the DUT side**:
the DUT's RF exit is a soldered wire, not an SMA jack. The primary OTA
edgescan protocol (`thermal_bench.py scan_edges()`) is unaffected — it needs
zero connectors. If a conducted path is ever required for the DUT, it must be
FABRICATED (solder a coax pigtail to LR2021 pad 9) or the DUT swapped for
the F33 hub board (which does have SMA J1/J2) — a board swap, not a cable
purchase. This resolves `bfc2a899` open risk R1 in the direction opposite
its H4 hedge: the physical SkyMapper Board A, per its own wiring record,
follows **neither** SMA **nor** U.FL — it has no connector.

---

## 8. Source summary

| Claim | Source |
|---|---|
| DUT = LR2021 board "SkyMapper Board A" (c3-a), env LR2021_passive_mapper | fork README @ meshcore `d7ae93fa` bench-setup table; `balloon-board-lock.py` RESOURCES |
| DUT carrier = ESP32-C3_Mini_V1 "Maker go" (SuperMini) | `esp32c3-mini-v1.json`; `variants/nicerf_lr2021/platformio.ini` (`board = esp32c3_supermini`) |
| RF exits = soldered wire dipoles, pins 9/10, 16.4 cm @ 868 MHz / 3.1 cm @ 2.4 GHz | `wiring-dev-board.csv` rows ANT_SUBGHZ/ANT_24GHZ; `breadboard-wiring-guide.md:16,37-38,54-56`; `FLIGHT-BOARD-PLAN.md:85-86` |
| Module antenna interfaces = bare 50 Ω pads (no connector) | LoRa2021 Module Datasheet V1.3 §7 pin table (balloon git `36952f72`); footprint `custom:LoRa2021_Castellated` pads 9/10 |
| SuperMini onboard U.FL + U.FL-to-SMA pigtail accessory | `esp32c3-mini-v1.json` `connectors` |
| SMA J1/J2 belong to hub_board_f33 (F33 PA variant), not the DUT | `hub_board_f33.kicad_pcb:86,89-98,165-179`; `nicerf-lora2021f33-2g4.json` (different pinout); `inventory.md:34-39` ("2x SMA connectors on board edge" — F33 product line) |
| U.FL ANT1/ANT2 belong to the v_c3_flight flight design, not the DUT | `schematics/v_c3_flight.kicad_sch:3303-3412` (LR2021F33 + WROOM-02); `v_c3_flight_final.kicad_pcb:105-111` |
| Prior SMA-on-DUT claims being corrected | `55585471` §1a; `65c9c3df` ~line 305; `bfc2a899` line A1 / H4 / R1 |
| DUT not physically attached | USB census this session (2× CH340 + Pi Debugprobe; no ESP32-C3/LR2021) |

**Acceptance statement:** every DUT RF port is named above with a connector
type (two × NONE/wire-solder on the LR2021 path, one × U.FL on the SuperMini
WiFi/BLE path) and a cited source; zero ports left as an unqualified guess;
everything not confirmable is registered in §6 with the reason.