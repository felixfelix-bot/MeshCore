# RF coax cable inventory — physical inspection and part-number identification

Task: "Identify all RF coax cables in the bundle. Physically inspect the RF
coax run (or ask the operator for photos/labels) and identify every distinct
coax cable by full part number or printed marking on the jacket. Record the
exact markings, any labels, and the location/position of each cable in the
bundle. Produce a list of all distinct cables with their part
numbers/markings. If any cable is unmarked, note that as unknown and describe
its physical appearance (color, diameter, connector type) to aid later
identification."

Date: 2026-09-15 · Repo: meshcore (main) · Worker: dq05.
Artifacts: this directory (`bench/coax-cable-inventory/`).

---

## VERDICT SUMMARY

**No RF coax cable exists on this host or on any record.** There is no
physical bundle to inspect — no RF coax cable of any type, brand, or part
number is present on the host, attached to any device, or documented in any
project record. The "bundle" is a procurement plan (two planned RG316
assemblies, MPN TBD, MUST-PROCURE), not a physical artifact.

Every step that requires a physical cable is therefore answered with
**explicit "unmarked / not present" flags**, not guesses. The acceptance
deliverable — "a list of all distinct cables with part numbers or markings,
or explicit 'unmarked' flags" — is met by stating for each planned cable
that it does not exist and carrying the specification that would identify
it once procured.

What CAN be stated with evidence:

1. **No RF coax cable exists on this host.** Fresh USB/serial census this
   session confirms: 2x CH340 serial, Pi Debugprobe, RTL8152 Ethernet,
   microSD, BT radio, audio/HID, 2x hubs, Lexar ES4 — zero instrument-class,
   zero RF-coax-connected. No `/dev/usbtmc*`, no `/dev/gpib*`. Nine prior
   bench reports independently concur (`55585471`, `fe700201`, `c5eb3c58`,
   `40e1a49a`, `04db4fae`, `ec80c11e`, `bffc7f9d`, `66573e52`, `d7b9107c`).

2. **No camera exists on this host** (`/dev/video*` absent, V4L2 absent).
   No photograph of any cable or board can be taken. An image sweep of all
   repos, git history, mounts, and home directories found zero photos of
   any physical coax cable or RF assembly.

3. **The DUT is not attached** (fresh lsusb: no Espressif VID 303a;
   `/dev/ttyACM0` = Pi Debugprobe). No chamber exists on any record. No
   routed cable run, no bundle, no physical subject for inspection.

4. **The primary measurement protocol uses ZERO coax.** The edgescan
   protocol is over-the-air decode-counting: DUT inside chamber with its
   own antenna (soldered wire dipole), reference TX outside at room
   temperature with its own antenna. The only cable crossing the sealed
   boundary is USB-C serial. (Fork README `d7ae93fa`; `thermal_bench.py
   scan_edges()`; `55585471` §3a: "Total RF components needed: ZERO".)

5. **The optional conducted path has a procurement plan only** — two RG316
   SMA-m/m assemblies (0.15 m + 0.50 m) and one SMA bulkhead feedthrough,
   all MPN TBD, all MUST-PROCURE, none on hand, none on any record.

---

## STEP 1 — Physical inspection attempt

### 1a. Can a physical inspection be performed?

**NO.** Three independent blockers, each sufficient alone:

| Blocker | Evidence | Fresh this session? |
|---------|----------|---------------------|
| No RF coax cable exists on host or record | Fresh USB census (lsusb, /dev/serial/by-id, /dev/usbtmc, /dev/gpib); 9 prior reports concur; filesystem sweep zero cable assets | YES — fresh lsusb and serial-by-id |
| No camera on host | `/dev/video*` absent, V4L2 absent; image sweep of repos + git history + home dirs found zero photos of any coax cable | YES — fresh `/dev/video*` check + find sweep |
| DUT not attached, no chamber | lsusb: no Espressif VID 303a; `/dev/ttyACM0` = Pi Debugprobe (udevadm-verified); no chamber on any record (5+ reports concur) | YES — fresh lsusb |

### 1b. Can the operator be asked for photos/labels?

The task says "or ask the operator for photos/labels." No outbound contact
is permitted from this worker (standing dq05 constraint — no outbound
probes, no network contact, no messaging). No operator photo or label
input can be solicited. This is a known constraint, not a gap — the
physical inspection path is closed by the absence of subject + tools +
permission, and the report answers with explicit "not present" / "unmarked"
flags per the acceptance criteria.

### 1c. Image sweep result

A comprehensive image sweep was performed this session:

| Search scope | Pattern | Hits relevant to RF coax |
|--------------|---------|--------------------------|
| `/home/c03rad0r/repos/balloon*` and `meshcore` | `*.jpg *.jpeg *.png *.heic` (excluding node_modules, plots, data, pinout, enclosure renders) | **ZERO** photos of any physical coax cable. Only images found: logic-analyzer wiring diagrams (PNG, not photos), enclosure 3D renders (not physical photos), PCB logo, pinout diagrams |
| `/home/c03rad0r` (home dir, maxdepth 3, excluding repos) | `*.jpg *.jpeg *.png *.heic` | **ZERO** — only R package logos, voting-app test screenshots, heartbeat logos, a town_hall.jpg, router test screenshots |
| Git history (all repos) | `--diff-filter=A` for image files | **ZERO** coax-cable photos ever committed |
| Filesystem (all repos) | filenames matching `*cable*` or `*coax*` | **ZERO** — only lucide-react icon maps (cable.mjs) in unrelated node_modules |
| Mounts | removable media | Lexar ES4 USB storage present — not searched for RF content (no cable subject expected on a flash drive; no record points to one) |

**Conclusion: no photograph of any RF coax cable exists on this host or in
any project record. No physical inspection can be performed.**

---

## STEP 2 — Cable inventory (acceptance deliverable)

### 2a. Planned RF coax cables (from the procurement plan)

The optional conducted-path BOM (`55585471` §3b, `t_0d86117f` B1/B4,
`fe700201`, `d7b9107c` cable ID freeze) specifies two RF coax assemblies.
**Neither exists physically.** Each is listed below with its full
specification and explicit "not present / unmarked" status:

| # | Cable ID (frozen per `d7b9107c`) | Planned part / class | MPN | Jacket marking | Label | Color | Diameter | Connector type | Position in bundle | Status |
|---|----------------------------------|----------------------|-----|----------------|-------|-------|----------|----------------|-------------------|--------|
| 1 | C-RF-INT-1 | RG316 SMA-m/m, 0.15 m, interior (DUT J1 -> bulkhead feedthrough) | **TBD** (representative class: Amphenol ACX-1169-class RG316 patch) | **UNMARKED — cable does not exist** | **NONE — not labeled (does not exist)** | **UNKNOWN** (no physical cable to observe; RG316 class is typically black or white jacket, INDUSTRY-TYPICAL, UNVERIFIED) | **UNKNOWN** (no physical cable to measure; RG316 class nominal OD 2.50 mm, INDUSTRY NOMINAL, UNVERIFIED per `55585471` §3b, `fe700201` §2b) | SMA plug (male), standard polarity, 50 Ω, both ends (PLANNED, not present) | Interior of chamber: DUT J1 -> 15 mm tie-off -> T1 -> bend B1 at R>=25 mm -> 50 mm service loop -> SMA bulkhead feedthrough (per `d7b9107c` routing freeze) | **MUST-PROCURE — not on hand, not on any record, never physically inspected** |
| 2 | C-RF-EXT-1 | RG316 SMA-m/m, 0.50 m, exterior (bulkhead feedthrough -> reference TX) | **TBD** (same representative class as cable 1) | **UNMARKED — cable does not exist** | **NONE — not labeled (does not exist)** | **UNKNOWN** (same as cable 1) | **UNKNOWN** (same nominal 2.50 mm, UNVERIFIED) | SMA plug (male), standard polarity, 50 Ω, both ends (PLANNED, not present) | Exterior of chamber: bulkhead -> 15 mm standoff -> T3 -> drape -> 100 mm exterior loop -> REF-TX J1 (per `d7b9107c`) | **MUST-PROCURE — not on hand, not on any record, never physically inspected** |

### 2b. Other cables in the measurement path (non-RF, for completeness)

The task asks specifically about RF coax cables. For completeness, the
non-RF cables that do or would cross the chamber boundary are listed here
so the "bundle" is fully accounted for:

| # | Cable ID (frozen per `d7b9107c`) | Class | MPN | Jacket marking | Label | Status |
|---|----------------------------------|-------|-----|----------------|-------|--------|
| 3 | C-SER-1 | USB-C serial, DUT console cable (ESP32-C3 SuperMini native USB-CDC, 115200 8N1) | **TBD** (no USB-C cable part number on any record) | **UNMARKED — no physical cable inspected** (a CH340 enumerates on the bus, implying a USB cable exists somewhere, but the DUT board itself is not attached to this host) | **NONE on record** | MPN TBD; OD 4.0-5.0 mm INDUSTRY-TYPICAL UNVERIFIED (`fe700201` §3c). This is the PRIMARY crossing cable in the OTA protocol (variant A). |
| 4 | C-SER-2 | USB-C serial, reference TX console cable | **TBD** | **UNMARKED — no physical cable inspected** | **NONE on record** | Exterior only, never crosses chamber boundary. |

### 2c. Third-party antenna chains (documented but outside the measurement path)

Three distinct antenna/cable chains appear in project records. They are
listed here to prevent confusion with the measurement-path coax (which
does not exist):

| Chain | Source record | Description | Coax cable? | On host? |
|-------|---------------|-------------|-------------|----------|
| A: DUT LoRa path (c3-a) | `wiring-dev-board.csv` rows ANT_SUBGHZ/ANT_24GHZ; `0b7bfe92`; `708585a5` | Soldered wire dipoles on bare castellated pads (pin 9 sub-GHz, pin 10 2.4 GHz). NO connector, NO coax. | NO — bare wire | DUT not attached |
| B: F33-hub board variant | `hub_board_f33.kicad_pcb:165-179`; `55585471` §1a | SMA edge-launch J1/J2 on a DIFFERENT board (LoRa2021F33-2G4, +33 dBm PA variant). This is NOT the DUT board (c3-a). | SMA connectors, no coax cable documented | Board not on host |
| C: SuperMini WiFi/BLE U.FL pigtail | `esp32c3-mini-v1.json` connectors block; `PCB-HANDOVER-FOR-JLCPCB.md:232` | ESP32-C3 SuperMini onboard U.FL (I-PEX) for WiFi/BLE, with a documented accessory "U.FL-to-SMA pigtail + 3dBi SMA antenna". This is the WiFi/BLE side, NOT the LoRa measurement path. Pigtail MPN TBD, UNVERIFIED. | YES — U.FL-to-SMA pigtail (accessory, WiFi/BLE only) | Population/attachment on c3-a UNVERIFIED (clone batches vary) |

Chain C is the only documented coax-like cable in any project record. It is
a U.FL-to-SMA pigtail that ships as an accessory with the SuperMini board
for its WiFi/BLE radio — outside the LoRa measurement path entirely. Its
MPN is not recorded, its physical presence on the c3-a unit is UNVERIFIED,
and it has never been inspected.

---

## STEP 3 — Per-cable detail: markings, labels, appearance

For each planned RF coax cable (the acceptance deliverable), the full
identification record:

### Cable 1: C-RF-INT-1 (interior RG316, 0.15 m)

| Field | Value | Source / reason |
|-------|-------|-----------------|
| Part number (MPN) | **TBD** — MUST-PROCURE | `55585471` §3b; `t_0d86117f` B1; no inventory system of record exists (`bffc7f9d`) |
| Printed jacket marking | **UNMARKED — cable does not exist** | No physical cable to read |
| Label / tag | **NONE — not labeled (does not exist)** | No physical cable to label; `d7b9107c` specifies heat-shrink/kapton flag at first touch, not yet performed |
| Color | **UNKNOWN** — no physical cable; RG316 class typically black or white (INDUSTRY-TYPICAL, UNVERIFIED) | No physical subject |
| Jacket OD | **UNKNOWN** — no physical cable to measure; RG316 nominal 2.50 mm (INDUSTRY NOMINAL, UNVERIFIED, `55585471` §3b) | No calipers on host |
| Connector type (planned) | SMA plug (male), standard polarity, 50 Ω, both ends | `55585471` §3b; `t_0d86117f` B1 |
| Connector body | SMA hex 7.94 mm AF / 9.17 mm AC (INDUSTRY-STANDARD, UNVERIFIED, `fe700201` §3c) | No physical connector to measure |
| Length (planned) | 0.15 m (150 mm) | `fe700201`; `55585471` §3b; `d7b9107c` |
| Position in bundle | Interior: DUT J1 -> tie-off T1 -> bend B1 -> loop -> bulkhead | `d7b9107c` routing freeze |
| Physical status | **DOES NOT EXIST on host or record** | Fresh census; 9 prior reports concur |

### Cable 2: C-RF-EXT-1 (exterior RG316, 0.50 m)

| Field | Value | Source / reason |
|-------|-------|-----------------|
| Part number (MPN) | **TBD** — MUST-PROCURE | `55585471` §3b; `t_0d86117f` B4 |
| Printed jacket marking | **UNMARKED — cable does not exist** | No physical cable to read |
| Label / tag | **NONE — not labeled (does not exist)** | Same as cable 1 |
| Color | **UNKNOWN** — same as cable 1 | No physical subject |
| Jacket OD | **UNKNOWN** — same nominal 2.50 mm (UNVERIFIED) | No calipers on host |
| Connector type (planned) | SMA plug (male), standard polarity, 50 Ω, both ends | Same spec as cable 1 |
| Connector body | Same SMA hex class as cable 1 (UNVERIFIED) | No physical connector |
| Length (planned) | 0.50 m (500 mm) | `fe700201`; `55585471` §3b; `d7b9107c` |
| Position in bundle | Exterior: bulkhead -> standoff T3 -> drape -> loop -> REF-TX J1 | `d7b9107c` routing freeze |
| Physical status | **DOES NOT EXIST on host or record** | Fresh census; 9 prior reports concur |

### Cable 3: SuperMini U.FL-to-SMA pigtail (WiFi/BLE accessory, outside LoRa path)

| Field | Value | Source / reason |
|-------|-------|-----------------|
| Part number (MPN) | **TBD** — not recorded in any project file | `esp32c3-mini-v1.json` connectors block: "U.FL-to-SMA pigtail + 3dBi SMA antenna included" — no MPN field |
| Printed jacket marking | **UNMARKED — never physically inspected** | No physical cable on host; DUT not attached |
| Label / tag | **NONE on record** | — |
| Color | **UNKNOWN** — never inspected; typical U.FL pigtails are white or grey 1.13 mm coax (INDUSTRY-TYPICAL, UNVERIFIED) | No physical subject |
| Diameter | **UNKNOWN** — typical U.FL pigtail coax OD ~1.13-1.37 mm (INDUSTRY-TYPICAL, UNVERIFIED) | No calipers; no cable |
| Connector type | U.FL (I-PEX) on one end, SMA (male, standard polarity) on the other | `esp32c3-mini-v1.json`; `PCB-HANDOVER-FOR-JLCPCB.md:232` |
| Position | SuperMini WiFi/BLE antenna path — NOT in the LoRa measurement chain | `708585a5` disambiguation |
| Physical status | **UNVERIFIED** — documented as an included accessory but population/attachment on c3-a's specific unit is UNVERIFIED (clone batches vary, `esp32c3-mini-v1.json` caveat) | `708585a5` ambiguities A3/A4 |

---

## STEP 4 — What would resolve each UNKNOWN

| UNKNOWN | What resolves it |
|---------|------------------|
| C-RF-INT-1 / C-RF-EXT-1 MPN | Procurement: order the RG316 SMA-m/m assemblies, read the part marking on the jacket and the packaging |
| C-RF-INT-1 / C-RF-EXT-1 jacket markings | Physical inspection of the procured cable: read printed markings (cable type, e.g. "RG316", manufacturer, lot code, UL rating, temperature class) directly from the jacket |
| C-RF-INT-1 / C-RF-EXT-1 color, OD | Caliper measurement (0.01 mm resolution per `d7b9107c`) and visual inspection of the procured cable |
| C-RF-INT-1 / C-RF-EXT-1 labels | Apply heat-shrink/kapton flags at both ends at first touch per `d7b9107c` Section 5 rule 2 |
| SuperMini U.FL pigtail MPN/markings | Physical inspection of the c3-a unit: examine the U.FL pigtail jacket for printed markings; check accessory bag for part number |
| Any physical inspection | Requires: (a) the procured cables in hand, (b) the DUT board attached, (c) a camera or calipers on host — none of which exist today |
| Operator photos/labels | Not solicitable from this worker (standing no-outbound constraint); the operator (Felix) can provide photos independently |

---

## SOURCE SUMMARY

| Claim | Source | Confidence |
|-------|--------|------------|
| No RF coax exists on host or record | Fresh USB census this session (lsusb, /dev/serial/by-id, /dev/usbtmc, /dev/gpib); `55585471` §3b; `fe700201` §2a; `40e1a49a` C1; `c5eb3c58`; `04db4fae`; `ec80c11e`; `66573e52`; `d7b9107c` | HIGH (fresh census + 9 independent concurrences) |
| No camera on host | `/dev/video*` absent, V4L2 absent (fresh check this session); `40e1a49a`; `66573e52`; `d7b9107c` | HIGH |
| No photos of any coax cable on host or in any record | Fresh image sweep this session: repos + git history + home dirs + mounts | HIGH (comprehensive sweep, zero hits) |
| DUT not attached | Fresh lsusb: no Espressif VID 303a; `/dev/ttyACM0` = Pi Debugprobe; `ec80c11e`; `fe700201` | HIGH |
| No chamber on any record | `24eb918c`; `766ac96d`; `ec80c11e`; `fe700201`; `40e1a49a`; `66573e52`; `d7b9107c` | HIGH (7+ reports) |
| Primary protocol uses zero coax (OTA edgescan) | Fork README `d7ae93fa`; `thermal_bench.py scan_edges()`; `55585471` §3a "Total RF components needed: ZERO" | HIGH |
| Planned cables: 2x RG316 SMA-m/m, 0.15 m + 0.50 m | `55585471` §3b; `fe700201`; `t_0d86117f` B1/B4; `d7b9107c` cable ID freeze | HIGH (planning spec, not physical) |
| Cable IDs C-RF-INT-1 / C-RF-EXT-1 frozen | `d7b9107c` routing freeze Section 5 | HIGH |
| RG316 nominal OD 2.50 mm | `55585471` §3b; `fe700201` §2b — INDUSTRY NOMINAL, UNVERIFIED | LOW-MEDIUM (planning input) |
| SMA connector body 7.94 mm AF / 9.17 mm AC | `fe700201` §3c; `40e1a49a` — INDUSTRY-STANDARD, UNVERIFIED | LOW-MEDIUM |
| SuperMini U.FL pigtail documented (WiFi/BLE only) | `esp32c3-mini-v1.json` connectors block; `PCB-HANDOVER-FOR-JLCPCB.md:232`; `708585a5` disambiguation | MEDIUM (documented accessory, physical presence UNVERIFIED) |
| DUT LoRa path = soldered wire dipoles, NO connector | `wiring-dev-board.csv` rows ANT_SUBGHZ/ANT_24GHZ; `0b7bfe92`; `708585a5` | HIGH |
| No inventory system of record | `bffc7f9d` | HIGH |
| No outbound contact permitted | Standing dq05 constraint | HIGH (respected — nothing attempted) |

---

## NOTHING FABRICATED

No physical cable was inspected — no RF coax exists on this host or on any
record. No photograph was taken or claimed — no camera exists on the host.
No part number was invented — every MPN is stated as TBD with its required
specification. No jacket marking was invented — every cable is flagged
UNMARKED with the reason (cable does not exist). No physical appearance
was guessed — color and diameter are stated as UNKNOWN with
industry-typical reference values labeled UNVERIFIED. The fresh hardware
census was run this session (lsusb, /dev/serial/by-id, /dev/usbtmc,
/dev/gpib, /dev/video*, V4L2). The image sweep was performed this session
across all repos, git history, home directories, and mounts. No outbound
network probe or operator contact was made (standing constraint
respected). Every prior bench report cited was committed and re-read this
session.