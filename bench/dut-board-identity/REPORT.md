# DUT board MPN, revision, and provenance

Fleet card: meshcore (DUT board identification task).
Date: 2026-09-15. Repo: meshcore (main). Worker: dq05.
Host: c03rad0r-DQ05proplus. Artifacts: this directory
(bench/dut-board-identity/).

The DUT is a two-chip hand-wired assembly on a breadboard (not a custom
PCB). It has two identifiable components, each with its own MPN:

  1. Radio module: NiceRF LoRa2021 (LR2021 Gen4, 18-pin castellated)
  2. Carrier/MCU:  ESP32-C3_Mini_V1 (Maker go, alias "ESP32-C3 Super Mini")

The assembly as a whole has no single board-level MPN. It is identified in
the repo by the campaign nickname "SkyMapper Board A" and the fleet
resource tag "c3-a". No custom PCB hosts the DUT RF ports — the RF exits
are soldered wire dipoles on the radio module's bare castellated pads (per
bench/dut-rf-ports/REPORT.md, committed 0b7bfe92).

---

## DELIVERABLE SUMMARY

| Field | Value | Confidence |
|---|---|---|
| Radio MPN | NiceRF LoRa2021 (LR2021 Gen4) | TENTATIVE — see provenance |
| Radio revision / hw version | Datasheet V1.3 (module); PCB package V1.2 (footprint) | TENTATIVE |
| Carrier MPN | ESP32-C3_Mini_V1 | TENTATIVE — see provenance |
| Carrier manufacturer | Maker go | TENTATIVE |
| Carrier revision / hw version | V1 (per board JSON "name" field) | TENTATIVE |
| Assembly name | SkyMapper Board A / fleet resource c3-a | TENTATIVE (campaign nickname, not a PCB MPN) |
| Alternate/compatible names | ESP32-C3 Super Mini, ESP32C3SuperMini (carrier aliases) | TENTATIVE |
| Board-level MPN | NONE — no single MPN for the hand-wired assembly | CONFIRMED (by absence) |
| Custom PCB | NONE — breadboard/jumper-wire assembly, not a PCB | CONFIRMED |

---

## PROVENANCE LIST (every identifier with its exact source)

### Radio module — NiceRF LoRa2021

| # | Identifier | Value | Source (exact path + line/field) | Source type |
|---|---|---|---|---|
| R1 | Module name | "NiceRF LoRa2021" | balloon repo: docs/inventory.md:16, table row 3, Komponente column | BOM / inventory |
| R2 | Chip designation | "LR2021 Gen4" | balloon repo: docs/inventory.md:16, Spezifikation column | BOM / inventory |
| R3 | Quantity on hand | 4 units | balloon repo: docs/inventory.md:16, Menge column | BOM / inventory |
| R4 | Source/vendor | "NiceRF" | balloon repo: docs/inventory.md:16, Quelle column | BOM / inventory |
| R5 | Unit price | ~10 EUR | balloon repo: docs/inventory.md:16, Einzelpreis column | BOM / inventory |
| R6 | Module dimensions | 19.72 x 15 x 2.2 mm, 18-pin castellated | balloon repo: docs/inventory.md:16, Spezifikation column | BOM / inventory |
| R7 | Firmware env binding | env LR2021_passive_mapper extends [NiceRF_LR2021], board = esp32c3_supermini | meshcore @ d7ae93fa: variants/nicerf_lr2021/platformio.ini, [NiceRF_LR2021] section, line "board = esp32c3_supermini" | Firmware config |
| R8 | DUT role assignment | "NiceRF LR2021 board (SkyMapper Board A or a spare)" running LR2021_passive_mapper, /dev/ttyACM0 | meshcore @ d7ae93fa: examples/passive_mapper/bench/README.md, "Bench setup" table, DUT row | Bench doc |
| R9 | Fleet resource tag | c3-a = "ESP32-C3 + LR2021 board A (MAC b0:a6:04:00:96:dc, /dev/ttyACM0)" | balloon repo: tools/balloon-board-lock.py:37 (RESOURCES block) | Fleet registry |
| R10 | MAC address (USB CDC serial) | B0:A6:04:00:96:DC | balloon repo: tools/balloon-board-lock.py:100 (BOARD_MACS dict, key "c3-a") | Fleet registry |
| R11 | Datasheet version | V1.3 (10 pages) | balloon repo @ cc92c869: docs/assets/lr2021/README.md:163 (asset table row for LoRa2021-Module-Datasheet-V1.3.pdf); PDF author metadata = "G-NiceRF" (git show cc92c869:docs/assets/lr2021/LoRa2021-Module-Datasheet-V1.3.pdf, PDF header %PDF-1.7, Author "(G-NiceRF)") | Vendor datasheet |
| R12 | PCB package version | V1.2 (footprint files: "LoRa2021 V1.2_pads.dxf", "LoRa2021V1.2_pads.pcb", "LoRa2021 V1.2_pads.asc") | balloon repo @ cc92c869: docs/assets/lr2021/README.md:166 (asset table row for LoRa2021_Package/) | Vendor PCB package |
| R13 | FCC ID | 2AD66-LORA2021-915 | balloon repo @ cc92c869: docs/assets/lr2021/README.md:19 (Certifications line) | Vendor cert reference |
| R14 | CE-RED certification | 6 test reports (EN 301 489, 300 220, 300 328, 62311, 62368, EU-Type Certificate) for LoRa2021-868 | balloon repo @ cc92c869: docs/assets/lr2021/README.md:165, 167 (CE-RED_Certification/ dir) | Vendor cert reference |
| R15 | Pinout (18 pins, pin 9 = ANT sub-GHz 50 ohm, pin 10 = 2.4G/S 50 ohm) | Pin table from datasheet V1.3 page 6 | balloon repo @ cc92c869: docs/assets/lr2021/README.md:21-40 (Complete Pinout table) | Vendor datasheet |
| R16 | Wiring correlation (GPIO map matches CSV pin-for-pin) | SCK=6/D6->pin5, MISO=2/D2->pin3, MOSI=7/D7->pin4, NSS=10/D10->pin6, BUSY=4/D4->pin7, RST=3/D3->pin14, DIO9=5/D5->pin15 | meshcore @ d7ae93fa: variants/nicerf_lr2021/platformio.ini build_flags (-D P_LORA_*) vs balloon repo: tracker/hardware/footprints/wiring-dev-board.csv rows | Firmware + wiring CSV cross-check |
| R17 | Antenna exits = soldered wire dipoles (NO connector) | pin 9 = "16.4cm wire @ 868 MHz", pin 10 = "3.1cm wire @ 2.4 GHz" | balloon repo: tracker/hardware/footprints/wiring-dev-board.csv, rows ANT_SUBGHZ / ANT_24GHZ | Wiring record |
| R18 | Product page URL | https://www.nicerf.com/lora-module/lora2021.html | balloon repo @ cc92c869: docs/assets/lr2021/README.md:178 | Vendor URL |
| R19 | Datasheet URL | https://www.nicerf.com/upload/20260410/854dad89545deb389f58e7f6a38971f4.pdf | balloon repo @ cc92c869: docs/assets/lr2021/README.md:179 | Vendor URL |

### Carrier board — ESP32-C3_Mini_V1

| # | Identifier | Value | Source (exact path + line/field) | Source type |
|---|---|---|---|---|
| C1 | Board name | "ESP32-C3_Mini_V1" | balloon repo: tracker/hardware/footprints/esp32c3-mini-v1.json, "board" field | Board spec JSON |
| C2 | Manufacturer | "Maker go" | balloon repo: tracker/hardware/footprints/esp32c3-mini-v1.json, "manufacturer" field | Board spec JSON |
| C3 | Aliases | ["ESP32-C3 Super Mini", "ESP32C3SuperMini"] | balloon repo: tracker/hardware/footprints/esp32c3-mini-v1.json, "aliases" array | Board spec JSON |
| C4 | Dimensions | 22.52 x 18.0 mm | balloon repo: tracker/hardware/footprints/esp32c3-mini-v1.json, "dimensions_mm" object | Board spec JSON |
| C5 | Chipset | ESP32-C3 FN4, RISC-V 160 MHz, 400 KB SRAM, 4 MB flash | balloon repo: tracker/hardware/footprints/esp32c3-mini-v1.json, "chipset" + "memory" fields | Board spec JSON |
| C6 | Connectors | USB Type-C, U.FL (I-PEX) for external antenna | balloon repo: tracker/hardware/footprints/esp32c3-mini-v1.json, "power.usb" + "connectors.antenna" fields | Board spec JSON |
| C7 | Quantity on hand | 20 units | balloon repo: docs/inventory.md:13, table row 1, Menge column | BOM / inventory |
| C8 | Source/vendor | AliExpress | balloon repo: docs/inventory.md:13, Quelle column | BOM / inventory |
| C9 | Unit price | 3.89 EUR | balloon repo: docs/inventory.md:13, Einzelpreis column | BOM / inventory |
| C10 | Firmware board binding | board = esp32c3_supermini (custom board JSON) | meshcore @ d7ae93fa: variants/nicerf_lr2021/platformio.ini, [NiceRF_LR2021] section | Firmware config |
| C11 | PlatformIO board JSON name | "ESP32-C3 SuperMini V1 (Maker go)" | meshcore @ d7ae93fa: boards/esp32c3_supermini.json, "name" field | Firmware board def |
| C12 | PlatformIO board JSON vendor | "Maker go" | meshcore @ d7ae93fa: boards/esp32c3_supermini.json, "vendor" field | Firmware board def |
| C13 | PlatformIO board JSON URL | https://www.aliexpress.com/item/1005006155740481.html | meshcore @ d7ae93fa: boards/esp32c3_supermini.json, "url" field | Firmware board def |
| C14 | Onboard regulator | ME6211 (3.3V) | balloon repo: tracker/hardware/footprints/esp32c3-mini-v1.json, "power.vreg" field | Board spec JSON |
| C15 | U.FL antenna accessories | "U.FL-to-SMA pigtail + 3dBi SMA antenna included" | balloon repo: tracker/hardware/footprints/esp32c3-mini-v1.json, "connectors.antenna_accessories" field | Board spec JSON |
| C16 | Wiring guide parts list | "1x ESP32-C3_Mini_V1 (Maker go, USB-C)" | balloon repo: docs/breadboard-wiring-guide.md:8 (Parts Needed list) | Wiring guide |
| C17 | DIY hub board plan reference | "U1 | ESP32-C3_Mini_V1 (Maker go) | Through-hole 2x8 pin header 2.54mm | 1 | Dev board, USB-C, U.FL antenna" | balloon repo: tracker/hardware/hub_board_diy/plan.md:22 (Components table) | PCB design plan |
| C18 | Flight board plan dual-footprint | Dev: ESP32-C3_Mini_V1 via 2x8 pin header; Flight: bare ESP-C3-12F via QFN-56 | balloon repo: tracker/hardware/FLIGHT-BOARD-PLAN.md:22-23 (Design Decisions, MCU section) | PCB design plan |
| C19 | Datasheet source URLs | 6 URLs (artronshop, sudo.is, icbbuy, fambach, github, mischianti) | balloon repo: tracker/hardware/footprints/esp32c3-mini-v1.json, "sources" array | Board spec JSON |

### Assembly-level identifiers

| # | Identifier | Value | Source (exact path + line/field) | Source type |
|---|---|---|---|---|
| A1 | Campaign nickname | "SkyMapper Board A" | meshcore @ d7ae93fa: examples/passive_mapper/bench/README.md, "Bench setup" table, DUT row ("NiceRF LR2021 board (SkyMapper Board A or a spare)") | Bench doc |
| A2 | Fleet resource tag | c3-a | balloon repo: tools/balloon-board-lock.py:37 | Fleet registry |
| A3 | MAC / USB CDC serial | B0:A6:04:00:96:DC | balloon repo: tools/balloon-board-lock.py:100 | Fleet registry |
| A4 | Device path | /dev/ttyACM0 | balloon repo: tools/balloon-board-lock.py:37; prior bench reports (0b7bfe92, ec80c11e, fe700201) | Fleet registry |
| A5 | Assembly type | Hand-wired breadboard (jumper wires, solder bridges) — NOT a custom PCB | balloon repo: docs/breadboard-wiring-guide.md:1 ("Breadboard Wiring Guide: ESP32-C3_Mini_V1 + LoRa2021 + GPS") | Wiring guide |
| A6 | Firmware environment | LR2021_passive_mapper (extends NiceRF_LR2021) | meshcore @ d7ae93fa: variants/nicerf_lr2021/platformio.ini, [env:LR2021_passive_mapper] section | Firmware config |
| A7 | "SkyMapper" string search scope | ZERO hits in balloon repo working tree or git history (re-verified this session via grep -rn); appears ONLY in meshcore bench/fork docs | meshcore @ d7ae93fa: examples/passive_mapper/bench/README.md (only hit) | Grep verification |

---

## REVISION / HARDWARE VERSION DETAIL

### Radio module (NiceRF LoRa2021)

Two distinct version numbers exist in the vendor assets:

1. Datasheet version: V1.3 — the module datasheet is labeled V1.3 (10
   pages, PDF author "G-NiceRF"). Source: balloon @ cc92c869:
   docs/assets/lr2021/README.md:163.
2. PCB package version: V1.2 — the mechanical footprint files are labeled
   V1.2 (LoRa2021 V1.2_pads.dxf, LoRa2021V1.2_pads.pcb, LoRa2021 V1.2
   _pads.asc). Source: balloon @ cc92c869:
   docs/assets/lr2021/README.md:166.

These are document revisions, NOT necessarily silkscreen revisions on the
physical module. No silkscreen text, printed label, or sticker has been
read from the physical module — the DUT is not attached to this host
(ttyACM0 = Pi Debugprobe per 0b7bfe92), and no photo of the physical
module exists in either repo.

The sibling high-power module LoRa2021F33-2G4 (different product, +33 dBm
PA variant, 2x SMA connectors) is explicitly recorded as "Version: V1.0"
in balloon: docs/inventory.md:44. This is NOT the DUT radio — it is a
different module on a different board (hub_board_f33.kicad_pcb), as
established by 0b7bfe92.

### Carrier board (ESP32-C3_Mini_V1)

The board JSON "name" field reads "ESP32-C3 SuperMini V1 (Maker go)"
(meshcore @ d7ae93fa: boards/esp32c3_supermini.json), implying hardware
version V1. No silkscreen revision mark (e.g. "REV B", "v1.3") has been
read from the physical board — no physical inspection was performed and no
photo exists. The ESP32-C3 Super Mini is a widely-clone-manufactured board;
the "Maker go" vendor attribution comes from the board spec JSON and
inventory, not from a silkscreen reading.

---

## ALTERNATE / COMPATIBLE NAMES

| Component | Primary name | Alternate names | Source |
|---|---|---|---|
| Carrier | ESP32-C3_Mini_V1 | "ESP32-C3 Super Mini", "ESP32C3SuperMini", "esp32c3_supermini" (PlatformIO board ID) | esp32c3-mini-v1.json "aliases" array; boards/esp32c3_supermini.json "name" field |
| Radio | NiceRF LoRa2021 | "LoRa2021", "LR2021 Gen4" | docs/inventory.md:16; platformio.ini [NiceRF_LR2021] section |
| Assembly | SkyMapper Board A | "c3-a" (fleet tag), "ESP32-C3 + LR2021 board A" | balloon-board-lock.py:37; bench README DUT row |

The LoRa2021F33-2G4 (+33 dBm PA variant) is NOT the same board — it has
SMA connectors, a metal shield, different pinout (9 pads per long edge),
and is recorded as a separate inventory item. It must not be confused with
the DUT radio (see 0b7bfe92 for the full disambiguation).

---

## CONFIDENCE ASSESSMENT

### Radio module: NiceRF LoRa2021 — TENTATIVE (HIGH confidence in identity, MEDIUM in revision)

The identity chain is strong: 5 concordant records (inventory.md,
platformio.ini, wiring-dev-board.csv, breadboard-wiring-guide.md,
FLIGHT-BOARD-PLAN.md) all name "NiceRF LoRa2021" / "LR2021 Gen4" with
matching pin counts, dimensions, and pin functions. The firmware GPIO map
matches the wiring CSV pin-for-pin (R16). The vendor datasheet V1.3 PDF
exists in git history with author metadata "G-NiceRF".

What makes it TENTATIVE rather than CONFIRMED:
- No physical inspection of the module on c3-a has been performed (DUT not
  attached to this host).
- No photo of the physical module exists in either repo.
- No silkscreen text, printed label, or sticker has been read from the
  actual hardware.
- The version numbers (V1.3 datasheet, V1.2 PCB package) are document
  revisions, not confirmed silkscreen marks on the physical module.
- The "NiceRF" brand attribution comes from the inventory and vendor
  downloads, not from a physical label on the module.

What would confirm it:
- Physical inspection of the c3-a assembly: read any silkscreen text,
  printed label, or sticker on the radio module.
- Photo of the module showing manufacturer marking.
- Cross-check the physical pin count (18) and dimensions (19.72 x 15 x 2.2
  mm) with calipers.

### Carrier board: ESP32-C3_Mini_V1 — TENTATIVE (HIGH confidence in identity, MEDIUM in revision)

The identity chain is strong: board spec JSON (19 fields, 6 source URLs),
inventory (20 units from AliExpress), firmware board JSON, wiring guide,
DIY hub plan, and flight board plan all concordantly name
"ESP32-C3_Mini_V1" / "ESP32-C3 Super Mini" by "Maker go" with matching
dimensions (22.52 x 18.0 mm), chipset (ESP32-C3 FN4), and connector set
(USB-C + U.FL).

What makes it TENTATIVE:
- No physical inspection of the c3-a carrier has been performed.
- No photo of the physical carrier exists in either repo.
- No silkscreen text or printed label has been read from the actual board.
- The "V1" hardware version comes from the board JSON "name" field, not
  from a physical silkscreen revision mark.
- The ESP32-C3 Super Mini is widely clone-manufactured; the "Maker go"
  attribution is from the JSON and inventory, not from a physical label.
- Some SuperMini batches omit the U.FL connector (per
  esp32c3-mini-v1.json caveats array: "U.FL antenna connector is in
  addition to onboard PCB antenna; some boards require solder bridge to
  switch"). Physical U.FL population on c3-a's specific unit is UNVERIFIED.

What would confirm it:
- Physical inspection of the c3-a carrier: read silkscreen text, confirm
  USB-C + U.FL presence, measure dimensions.
- Photo of the board showing silkscreen markings.
- USB CDC enumeration of B0:A6:04:00:96:DC on /dev/ttyACM0 to confirm the
  specific unit is the one referenced.

### Assembly name: SkyMapper Board A / c3-a — TENTATIVE (campaign nickname, not a product MPN)

"SkyMapper" appears ONLY in meshcore bench/fork docs (zero hits in the
balloon repo working tree and git history, re-verified this session). It is
the campaign/board nickname for the c3-a assembly, not a distinct PCB or
product. The fleet resource tag "c3-a" and MAC B0:A6:04:00:96:DC are the
durable identifiers, both from balloon-board-lock.py.

### Board-level MPN: NONE — CONFIRMED (by absence)

No single MPN exists for the hand-wired assembly. The DUT is a breadboard
assembly of two separately-purchased components (ESP32-C3_Mini_V1 carrier
+ NiceRF LoRa2021 radio module) joined by jumper wires and solder bridges,
per docs/breadboard-wiring-guide.md. No custom PCB hosts the DUT RF ports
— the RF exits are soldered wire dipoles on the radio module's bare
castellated pads (per bench/dut-rf-ports/REPORT.md, 0b7bfe92). The custom
PCB designs in the balloon repo (hub_board_v1.kicad_pcb,
hub_board_diy.kicad_pcb, hub_board_f33.kicad_pcb) are flight/DIY designs,
NOT the bench DUT.

---

## SILKSCREEN / LABEL / STICKER / QR / FCC-ID / CE-ID INVENTORY

No physical identifiers have been read from the DUT hardware. The DUT is
not attached to this host (ttyACM0 = Pi Debugprobe per 0b7bfe92). No camera
is available (no /dev/video*, no V4L2, per 40e1a49a). No photo of the
physical DUT exists in either repo. The following vendor-supplied
certification IDs exist in the repo but have NOT been matched to a
physical label on the c3-a unit:

| ID type | Value | Source | Physical label on c3-a? |
|---|---|---|---|
| FCC ID | 2AD66-LORA2021-915 | balloon @ cc92c869: docs/assets/lr2021/README.md:19 | UNVERIFIED (no physical inspection) |
| CE-RED | LoRa2021-868, 6 test reports | balloon @ cc92c869: docs/assets/lr2021/README.md:165, 167; CE-RED_Certification/ dir | UNVERIFIED (no physical inspection) |
| USB VID:PID | 0x303a:0x1001 (Espressif ESP32-C3) | meshcore @ d7ae93fa: boards/esp32c3_supermini.json, hwids field | UNVERIFIED on c3-a (DUT not attached) |
| MAC address | B0:A6:04:00:96:DC | balloon: tools/balloon-board-lock.py:100 | UNVERIFIED on c3-a (DUT not attached; would confirm via udevadm / USB CDC serial) |

---

## UNVERIFIED REGISTER

| # | Item | What would resolve it |
|---|---|---|
| U1 | Physical silkscreen text on the radio module | Photo or visual inspection of c3-a's LoRa2021 module |
| U2 | Physical silkscreen text on the carrier board | Photo or visual inspection of c3-a's ESP32-C3_Mini_V1 |
| U3 | Radio module revision mark (silkscreen "V1.3" or similar) | Physical inspection |
| U4 | Carrier board revision mark (silkscreen "V1" or "REV A/B") | Physical inspection |
| U5 | U.FL connector population on c3-a's specific carrier | Physical inspection (some SuperMini batches omit it) |
| U6 | FCC ID / CE-ID label physically present on the module | Physical inspection of radio module shield or label |
| U7 | MAC B0:A6:04:00:96:DC actually enumerates on /dev/ttyACM0 | USB CDC enumeration with DUT attached |
| U8 | Sticker / QR / serial number on either component | Physical inspection |
| U9 | Which of the 4 LoRa2021 units (inventory row 3) is on c3-a | Physical inspection or MAC-to-module correlation |
| U10 | Which of the 20 ESP32-C3_Mini_V1 units (inventory row 1) is on c3-a | Physical inspection or MAC-to-board correlation |

---

## SOURCES (all read fresh this session)

- meshcore @ d7ae93fa: examples/passive_mapper/bench/README.md
- meshcore @ d7ae93fa: variants/nicerf_lr2021/platformio.ini
- meshcore @ d7ae93fa: boards/esp32c3_supermini.json
- meshcore: bench/dut-rf-ports/REPORT.md (commit 0b7bfe92)
- balloon repo (working tree HEAD d8c7f8f6, branch autonomous/mesh-baseline):
  - docs/inventory.md
  - docs/breadboard-wiring-guide.md
  - tracker/hardware/footprints/esp32c3-mini-v1.json
  - tracker/hardware/footprints/wiring-dev-board.csv
  - tracker/hardware/FLIGHT-BOARD-PLAN.md
  - tracker/hardware/hub_board_diy/plan.md
  - tools/balloon-board-lock.py
- balloon repo @ cc92c869 (git history, not in working tree):
  - docs/assets/lr2021/README.md
  - docs/assets/lr2021/LoRa2021-Module-Datasheet-V1.3.pdf (PDF header
    verified: %PDF-1.7, Author "(G-NiceRF)")

No outbound fetches were performed (standing dq05 constraint). No physical
inspection was performed (DUT not attached, no camera). Nothing fabricated
— every identifier is labeled with its exact source.