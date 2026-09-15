# Merged connector/adapter BOM — DUT -> chamber interior -> feedthrough -> exterior -> instrument

Fleet card: `meshcore:t_0d86117f` — "Compile connector/adapter BOM with
procurement and RF loss analysis."

Date: 2026-09-15 · Repo: meshcore (main) · Worker: dq05.
Artifacts: this directory (`bench/connector-adapter-bom/`).

---

## STEP 0 — Inputs consumed (not re-derived)

This task merges three sibling outputs. The **current-wave** sibling cards
(`t_b1049504` DUT-port physical, `t_da54b09f` instrument-port,
`t_923c4eca` feedthrough survey) were all claimed but produced **zero
output** (fleet-state re-read this session: no result fields anywhere;
`t_923c4eca`'s 02:59 session is kickoff-only — prompt, no work). The
**committed on-record equivalents** are consumed instead, per the standing
fleet rule that resultless cards do not block a merge that cites them.

| # | Sibling input | Finding carried into this BOM | Source (committed) | Current-wave card status |
|---|---|---|---|---|
| 1 | DUT port identification | DUT RF port = **SMA edge-launch, standard polarity, female jack**, ref J1 "SMA-868" (sub-GHz, net `RF_SUB_868`); second port J2 "SMA-2G4" (net `RF_2G4_2400`). LR2021 module itself has **castellated PCB pads** (pin 9 ANTA, pin 10 2.4/S_ANTA) — no connector on the module; the SMA is on the SkyMapper carrier board. | `55585471` (bench/rf-feedthrough-bom/REPORT.md) §1a + `hub_board_f33.kicad_pcb:165-179` (footprint `custom:SMA_Edge_Mount`, J1 at (2,28), J2 at (73,28)) + NiceRF LoRa2021 datasheet V1.3 pin table + `65c9c3df` line 305-306 verbatim ("SMA edge-launch connector") — all re-verified by citation check this session | `t_b1049504` claimed, **NO OUTPUT** -> OPEN RISK R1 |
| 2 | Instrument port identification | **No RF instrument exists** (USB census, 2x CH340 + Pi Debugprobe + RTL8152 + microSD, zero instrument-class, re-verified in `ec80c11e` and `04db4fae`). The de-facto "instrument" is the **reference TX board** (any MeshCore node, 868 MHz SF8/BW62.5, kept at room temperature outside the chamber), whose RF port is the **same SMA female jack** family as the DUT (SkyMapper family, resource `c3-b`). | `55585471` §1b + fork README `d7ae93fa:examples/passive_mapper/bench/README.md` "Bench setup" table + `balloon-board-lock.py` resource map + `023c5e86`/`c4be4400` USB censuses | `t_da54b09f` claimed, **NO OUTPUT** -> OPEN RISK R2 |
| 3 | Feedthrough assessment | Chamber feedthrough status **UNKNOWN** — chamber unidentified on every record (no make/model/manual; `24eb918c`, `766ac96d`, `72f3aab9`, `ec80c11e` all resultless/blocked). Project's own documented wall-pass pattern = **SMA bulkhead feedthrough in a 6.5 mm panel hole sealed with SMA O-rings** (enclosure/README_big.md:20-26 "Two SMA bulkhead holes (6.5mm) ... Fully waterproof with SMA O-rings"). Mechanical-fit verdict of the one committed survey = UNKNOWN, blocked on chamber side. | `fe700201` (bench/chamber-feedthrough-fit/REPORT.md, card `t_48e048a1`) + enclosure/README_big.md:20-26 + README.md:27,72 re-read this session | `t_923c4eca` claimed 02:58, kickoff-only session, **NO OUTPUT** -> OPEN RISK R3 |

Supporting findings consumed as constraints (not identifications):
- `04db4fae` — failure-mode catalogue: top-ranked reversible failure = ice
  bridging at exposed/unmated SMA interfaces (dust caps matter); RG316 -40 C
  rating and 12.7 mm bend radius UNVERIFIED; nitrile O-ring material at -40 C
  MEDIUM-HIGH vs silicone LOW; answer carried: no cable-level temperature
  calibration for the decode-count protocol, YES for any power/phase-
  quantitative variant.
- `65c9c3df` — condensation CERTAIN at -20/-40 C: desiccant + sealed DUT bag
  REQUIRED (fork README:54 verbatim "a sealed bag around the module").
- `bffc7f9d` — no booking/parts inventory system of record exists on this
  host: "ON-HAND" claims are limited to what records enumerate.
- `ec80c11e` — worker host not attached to any chamber; DUT not attached to
  any fleet host (fresh USB census).

---

## STEP 1 — Chain verdict (from the consumed findings, not re-derived)

The normative measurement protocol (`d7ae93fa:examples/passive_mapper/
bench/README.md`, `thermal_bench.py scan_edges()`) is **over-the-air**: the
DUT inside the chamber receives a reference TX outside the chamber through
its own antenna, and the measurement is a **decoded-packet count per injected
frequency offset**, not an RF power measurement. Therefore:

- **PATH A (primary, over-the-air):** the literal wire chain
  "DUT -> interior -> feedthrough -> exterior -> instrument" is **EMPTY of
  RF components**. The RF signal crosses the wall by air (antenna -> wall ->
  antenna); the only conductor crossing the sealed boundary is the USB-C
  serial/control cable.
- **PATH B (optional conducted contingency):** if the (unidentified) chamber
  is metal — a Faraday cage — over-the-air fails and the coax + bulkhead
  chain becomes mandatory (`55585471` caveat 4).

The BOM below gives every line for both paths, each item exactly once, with
quantity, part number / required interface spec, procurement disposition,
lead time, vendor, and cited source.

---

## STEP 2 — BOM, PATH A (primary, over-the-air edgescan)

| # | Item | QTY | Part number / required spec | Disposition | Lead time / vendor | Source |
|---|---|---|---|---|---|---|
| A1 | SMA edge-launch RF connector, sub-GHz (DUT port, J1 "SMA-868", female jack, 50 Ω, standard polarity) | 1 | `custom:SMA_Edge_Mount` footprint, value "SMA-868" — already soldered on the SkyMapper carrier board | **ON-HAND** (part of DUT, fleet resource `c3-a`) | — | `hub_board_f33.kicad_pcb:165-179` via `55585471` §1a; `65c9c3df:305-306` verbatim |
| A2 | 868 MHz antenna at the DUT (mates J1) — choose ONE implementation: (i) SMA-male stub, 868 MHz, 50 Ω, ~2 dBi, standard polarity; or (ii) wire dipole, 8.6 cm legs each side, on an SMA-male mount | 1 | (i) MPN TBD — required spec: SMA plug (male), 868 MHz, 50 Ω, ≥50 W rated not needed (RX only), standard polarity — OR (ii) fabricated from solid-core wire, MPN N/A | (i) **MUST-PROCURE** or (ii) **MUST-FABRICATE** | (i) 1-3 days, Digi-Key/Mouser/AliExpress-class; (ii) <1 h, lab wire stock | Dipole spec: `~/repos/balloon/IMPLEMENTATION-PLAN.md:41` "Cut wire dipole antennas (868 MHz: 8.6 cm legs each side)" — re-read this session (55585471 cited this line under a stale `tracker/hardware/` prefix; file lives at repo root — corrected here) |
| A3 | Sealed bag around the DUT (protocol-required moisture barrier) | 1 | Zip-seal ESD-safe bag or equivalent, sized ≥ module+carrier (~75x55 mm board + SMA connector clearance) | **ON-HAND** (consumable lab stock; no inventory record — `bffc7f9d`) | — | Fork README `d7ae93fa` line 54 verbatim via `55585471`; REQUIRED per `65c9c3df` |
| A4 | Desiccant (silica gel), inside sealed bag / chamber | 2+ packs | MPN TBD — spec: indicating silica gel, 1-2 g per litre of enclosed volume | **ON-HAND** (consumable lab stock, assumed; not on any record) | — | `65c9c3df` mitigation table (REQUIRED) |
| A5 | Reference TX board ("instrument" side of the OTA link) | 1 | Any MeshCore node on nominal frequency, 868 MHz SF8/BW62.5, transmitting continuously; fleet resource `c3-b` (SkyMapper family) | **ON-HAND** (`c3-b` per `balloon-board-lock.py`) | — | Fork README "Bench setup" via `55585471` §1b, source table line "Reference TX = c3-b or any spare MeshCore node" |
| A6 | 868 MHz antenna at the reference TX (mates its J1 SMA jack) — same choice as A2: SMA-m stub OR wire dipole on SMA mount | 1 | Same required spec as A2 | **MUST-PROCURE** (1) or **MUST-FABRICATE** (1) — pair with A2 decision | Same as A2 | Same as A2 (antenna on ref TX: `55585471` §1b "The reference TX has its own antenna (wire dipole or SMA-connected stub)") |
| A7 | USB-C data cable, DUT serial CLI (ESP32-C3 SuperMini native USB-CDC, 115200 8N1, `/dev/ttyACM0`) — MUST be data-capable, not charge-only; length must span chamber interior to host (≥1.5 m recommended, UNMEASURED) | 1 | Standard USB-C data cable, USB 2.0 adequate | **ON-HAND** (enumerated on the bus; DUT itself not attached to any fleet host — `ec80c11e`) | — (1 spare RECOMMENDED, 1-3 days) | Fork README "Bench setup" via `55585471` §3a line 3 |
| A8 | USB serial cable for the reference TX (CH340 console, `/dev/ttyUSB0`) | 1 | USB-A to board's console port (board-dependent; CH340 enumerate implies micro-B/adapter) | **ON-HAND** (2x QinHeng CH340 enumerated in USB census) | — | Fork README via `55585471` §3a line 4; USB census `023c5e86`/`ec80c11e` |

**Path A RF-component procurement count: ZERO mandatory.** Two antennas
(A2+A6) are the only RF items and can be fabricated from wire in <1 h each.

---

## STEP 3 — BOM, PATH B (optional conducted contingency; mandatory if chamber is metal)

Chain with every gender transition explicit:

```
DUT J1 [SMA-F jack, edge-launch, on PCB]
  ->(mates) RG316 assembly #1, SMA-M plug === SMA-M plug, 0.15 m   [interior]
  ->(mates) SMA bulkhead feedthrough [SMA-F jack | wall | SMA-F jack]
  ->(mates) RG316 assembly #2, SMA-M plug === SMA-M plug, 0.50 m   [exterior]
  ->(mates) Reference TX J1 [SMA-F jack]
```

No gender-changing adapter exists in the basic chain (M-M cable assemblies,
F-F bulkhead). All connectors standard-polarity SMA, 50 Ω.

| # | Item | QTY | Part number / required spec | Disposition | Lead time / vendor | Source |
|---|---|---|---|---|---|---|
| B1 | RG316 coax assembly, SMA-male to SMA-male, 0.15 m (DUT to bulkhead, interior) | 1 | **MPN TBD** — required spec: RG316 (OD 2.5 mm, PTFE), SMA plug both ends, male pin, 50 Ω, standard polarity, flex life adequate for 12.7 mm min bend radius. Representative class per `55585471`: Amphenol ACX-1169-class RG316 patch (exact-length variant TBD) | **MUST-PROCURE** (not on any record) | 2-5 days, Digi-Key/Mouser | `55585471` §3b line 3; lengths from `fe700201` (0.15 m + 0.5 m) |
| B2 | SMA bulkhead feedthrough, panel-mount jack-to-jack (the wall penetration) | 1 | **MPN TBD** — required spec: SMA female jack both sides, panel mount, 50 Ω, standard polarity, PTFE, with jam nut. Representative class per `55585471`: Amphenol 132134-class SMA panel jack-jack | **MUST-PROCURE** (chamber feedthrough population UNKNOWN — R3) | 2-5 days, Digi-Key/Mouser | `55585471` §3b line 2; wall-pass pattern from enclosure/README_big.md:20-26 via `fe700201` |
| B3 | Panel penetration: 6.5 mm hole in chamber wall (only if no existing feedthrough) + deburr + rust-proofing | 0-1 | Fabrication: 6.5 mm bore per project's own SMA bulkhead pattern; panel material/thickness UNKNOWN (chamber unidentified) | **MUST-FABRICATE** (conditional on B2 being needed AND no existing feedthrough) | Site visit; **custodian gate: Felix (`4b3ec9b5` MEDIUM) — no drilling without approval** | enclosure/README_big.md:21 "Two SMA bulkhead holes (6.5mm)" via `fe700201`; drill-gate per `fe700201` unblock path |
| B4 | RG316 coax assembly, SMA-male to SMA-male, 0.50 m (bulkhead to reference TX, exterior) | 1 | **MPN TBD** — same spec as B1, 0.50 m | **MUST-PROCURE** | 2-5 days, Digi-Key/Mouser | `55585471` §3b line 1; length `fe700201` |
| B5 | SMA O-ring sealing washers for the bulkhead, **silicone** (not nitrile) | 2 | **MPN TBD** — required spec: silicone elastomer (Tg -55..-65 C class), SMA-bulkhead size; nitrile explicitly REJECTED for -40 C service | **MUST-PROCURE** (with B2; many bulkheads ship with O-rings — verify at order) | 1-3 days (or included with B2) | Enclosure pattern: README_big.md:23 "Fully waterproof with SMA O-rings" + README.md:72 "O-ring cord (2mm) ~220mm — Nitrile or silicone" (material now DECIDED: silicone, per `04db4fae` nitrile-at-minus-40C MEDIUM-HIGH vs silicone LOW) |
| B6 | Connector saver on DUT J1: SMA male-to-female bullet adapter (takes mate/demate cycles off the soldered edge-launch) | 1 | **MPN TBD** — required spec: SMA plug (male) to SMA jack (female), 50 Ω, standard polarity, brass/gold, PTFE dielectric, DC-3 GHz | **MUST-PROCURE** (RECOMMENDED-strong: edge-launch solder joint is the CTE-fatigue weak point, ~3-4 cycles/session per `04db4fae` FM-4) | 2-5 days, Digi-Key/Mouser | Hazard rationale from `04db4fae` (solder/center-pin CTE fatigue class); port identity from input 1 |
| B7 | SMA 50 Ω termination (load) for the unused J2 "SMA-2G4" port | 1 | **MPN TBD** — required spec: SMA plug (male), 50 Ω, DC-3 GHz, ≥1 W, VSWR <1.2:1 | **MUST-PROCURE** (prevents the unused 2.4 GHz port radiating/ESD; a dust cap is the minimum) | 1-3 days, Digi-Key/Mouser | J2 identity from input 1 (`hub_board_f33.kicad_pcb:175-179`); load-or-cap rule standard practice, no project record cites a load (flagged, not sourced to project) |
| B8 | SMA dust caps, male + female (protect every unmated SMA from frost/ice bridging — top-ranked reversible failure mode) | 4 | **MPN TBD** — representative class per `55585471`: Amphenol 132172-class SMA dust caps; required spec: standard SMA, 2x male-plug caps + 2x female-jack caps, with retaining chains preferred | **MUST-PROCURE** | 1-3 days, Digi-Key/Mouser | `55585471` §3b line 6; ice-bridging hazard `04db4fae` FM-1 (CERTAIN, top rank) |
| B9 | Torque wrench for SMA: 5/16 in, 0.9 N·m (8 in-lb) breakaway | 1 | Representative MPN per `55585471`: Fujiya FTK-16SR or equivalent SMA torque wrench | **MUST-PROCURE** (finger-tight is insufficient for stable, repeatable mating) | 3-7 days | `55585471` §3b line 4 |
| B10 | Open-end spanner, 8 mm (5/16 in = 7.94 mm AF) for bulkhead jam nut / connector hexes | 1 | Any 8 mm open-end spanner (jam-nut counterhold during torque) | **MUST-PROCURE** (trivial; likely already in lab tooling — not on any record) | Same-day, hardware store | SMA hex 7.94 mm AF from `fe700201` fit table (industry-standard SMA, UNVERIFIED on host) |
| B11 | Conditional instrument adapter: SMA-F jack to N-M plug (for a signal generator / analyzer with N-female port), or SMA-F to BNC-M if BNC | 0-1 | **MPN TBD** — required spec: 50 Ω, DC-3 GHz, low-VSWR adapter matching whatever instrument is eventually procured | **CONDITIONAL** (qty 0 today: no RF instrument exists — input 2) | 1-3 days once instrument known | `55585471` §3b line 5 (conditional adapter row); instrument absence re-verified `ec80c11e` |

Notes:
- In Path B the antennas (A2/A6) are REMOVED — J1 on both ends is taken by
  the coax; keep one stub on hand to sanity-check the OTA range before
  sealing the chamber.
- Items A3 (sealed bag), A4 (desiccant), A7 (USB-C), A8 (USB) remain
  REQUIRED in Path B — the DUT still needs serial control and moisture
  protection; they appear once, in Path A, and carry over.
- Path B adds a 5th mated SMA pair if B6 (saver) is used: its 0.05-0.1 dB is
  inside the loss band below.

---

## STEP 4 — Hazard lines (explicit mismatch risks)

| # | Hazard | Where it bites | Control |
|---|---|---|---|
| H1 | **75 Ω vs 50 Ω**: video/CCTV coax (RG-59/RG-6, 75 Ω, F/BNC) is commonly stocked in labs; the LR2021 system and every line in this BOM is **50 Ω**. A 75 Ω substitution adds a 14 dB return loss floor and a 0.18 dB mismatch loss at minimum, and mis-terminates the PA on TX. | B1/B4 cable procurement | Spec says RG316 (which only exists as 50 Ω); verify "RG316" literally on the order, reject "RG59/RGB" lookalikes |
| H2 | **Reverse-polarity SMA (RP-SMA)**: WiFi-industry RP-SMA plugs look nearly identical to standard SMA but have NO center pin (pin/socket swapped) — they will not mate and, worse, a "RP-SMA to SMA" forced or threaded-almost-home junction damages the jack. 868 MHz antennas are frequently sold in RP-SMA. | A2/A6 antenna procurement, B1/B4 assemblies, B2/B5/B6/B7/B8 | Every line above says "standard polarity"; at receiving, check the plug has a **center PIN** (male plug = pin) before mating. This is the single most likely procurement error. |
| H3 | **Precision vs standard SMA**: precision SMA / 3.5 mm connectors are dimensionally compatible but cost 5-10x; at 868 MHz (and even 2.4 GHz) standard SMA is fully adequate (VSWR spec 1.05:1 class at these frequencies). | B2/B6/B11 procurement | Buy standard SMA; precision adds nothing below 18 GHz except cost. LOW risk. |
| H4 | **U.FL vs SMA conflict (carried from input 1)**: the earlier schematic (`v_c3_flight-erc.rpt:434-442`, Molex 73412 U.FL footprints) and `~/repos/balloon/IMPLEMENTATION-PLAN.md:42` ("Connect antennas to U.FL connectors on LoRa2021 modules") describe U.FL, but the **fabricated PCB** (`hub_board_f33.kicad_pcb:165-179`) uses `custom:SMA_Edge_Mount` SMA. Resolution (consumed from `55585471`): the fabricated board wins — **SMA**. UNVERIFIED on the physical SkyMapper Board A (R1). | Whole BOM: if the physical board were U.FL, every SMA line changes to a U.FL pigtail (U.FL to SMA-female bulkhead cable) | R1 site check: look at J1 — SMA edge-launch has a visible hex/round barrel at the board edge; U.FL is a tiny 3 mm press-fit |
| H5 | **Hypothetical instrument port**: no RF instrument exists today (input 2). If one is procured later, its port (N-female most likely on sig gens/analyzers, BNC on counters) defines adapter B11 — buying B11 now would be a guess. | B11 | Leave B11 at qty 0-1 CONDITIONAL until an instrument is named |
| H6 | **O-ring material at -40 C**: nitrile (typical TR-10 -26..-46 C) approaches/loses elasticity at -40 C -> compression set, seal leak, and the sealed volume actively pumps moist air inward at -40 C (0.22 atm inward per `04db4fae`). Silicone (Tg -55..-65 C) stays elastic. | B5 | B5 spec'd silicone, overriding the enclosure README's undecided "Nitrile or silicone" |
| H7 | **Charge-only USB-C cable**: USB-C cables that lack data lines enumerate as nothing on `/dev/ttyACM0` — the DUT CLI disappears silently mid-campaign. | A7 | Use a known data cable; verify `ls /dev/ttyACM0` after every re-seat |

---

## STEP 5 — RF-loss accounting

Assumed figures (all from the committed sibling BOM `55585471` §5, which
labels them industry-typical; **no vendor datasheet exists on this host** —
no outbound fetch per standing operator constraint — so every dB figure
below is UNVERIFIED against a specific procured part):

| Element | @ 868 MHz | @ 2.4 GHz (informational) | Source |
|---|---|---|---|
| RG316 cable | ~0.3 dB/m | ~0.45-0.5 dB/m (sqrt-f scaling, industry-typical) | `55585471` §5 ("loss ~0.3 dB/m at 1 GHz" applied to 868 MHz there); `04db4fae` re-computed 0.65 m -> ~0.2 dB at room |
| Mated SMA pair | ~0.05-0.1 dB | ~0.1-0.3 dB (industry-typical) | `55585471` §5 |
| SMA bulkhead feedthrough | ~0.05-0.1 dB | ~0.1-0.2 dB (industry-typical) | `55585471` §5 |

Path B arithmetic at 868 MHz (assembly loss convention: a cable assembly's
loss includes its own two mated pairs):

- RG316 assembly #1, 0.15 m: ~0.05-0.10 dB
- RG316 assembly #2, 0.50 m: ~0.15-0.20 dB
- SMA bulkhead (jack-jack, mated both sides): ~0.05-0.10 dB
- Connector saver pair (if B6 used): ~0.05-0.10 dB
- **TOTAL: ~0.30-0.50 dB at 868 MHz** (consistent with `55585471` §5's
  "0.3-0.5 dB for a 2-cable + 1-feedthrough path"); at 2.4 GHz the same
  chain is roughly **0.7-1.1 dB** (scaled estimate, UNVERIFIED) — noted for
  completeness only, the protocol has no 2.4 GHz measurement.

Path A (primary): **0.00 dB added** — no RF connector, adapter, feedthrough,
or coax exists in the measurement chain; the OTA path loss (distance, wall
attenuation, orientation) is a link-budget variable, not an insertion loss,
and the decode-threshold protocol is insensitive to it as long as RSSI stays
above sensitivity.

**The one-sentence statement (task step 4):**

> At 868 MHz — the only frequency the edgescan protocol measures (2.4 GHz
> shown for completeness) — the optional conducted chain (two RG316
> assemblies totalling 0.65 m at ~0.3 dB/m plus one SMA bulkhead and four to
> five mated SMA pairs at 0.05-0.1 dB each, all industry-typical figures
> carried from committed BOM `55585471` §5 and UNVERIFIED against vendor
> datasheets) adds approximately **0.3-0.5 dB**, which the decode-threshold
> packet-count protocol tolerates without ANY recalibration — no numeric
> correction is even needed, because the 165 dB link budget (+22 dBm
> reference TX vs -143 dBm DUT sensitivity, `55585471` §5) makes sub-dB loss
> invisible to the decode-vs-offset curve — but if a power- or
> phase-quantitative variant is ever run, calibration MUST be redone at the
> new reference plane (the DUT SMA J1 connector face), since the added
> chain's loss would be uncharacterized and a numeric correction would
> require a measured (not assumed) chain loss that does not exist.

Recalibration decision, restated plainly (same conclusion as `04db4fae`'s
temperature-calibration answer, which this merge adopts):
- Primary decode-count protocol (either path): **no recalibration, no
  numeric correction** — the measurement is a packet count at injected
  offsets; added fixed loss shifts absolute RSSI only.
- Any future power/phase-quantitative variant: **calibrate at the DUT
  connector face (J1)** — a numeric correction is insufficient because the
  chain loss figures are UNVERIFIED (R5).

---

## STEP 6 — Procurement summary

MUST-PROCURE (Path B selected, all in one order, ~2-7 days total):
1. RG316 SMA-m/m assembly 0.15 m x1 (B1)
2. RG316 SMA-m/m assembly 0.50 m x1 (B4)
3. SMA panel jack-jack bulkhead x1 (B2)
4. Silicone SMA O-ring washers x2 (B5)
5. SMA connector saver M-F x1 (B6)
6. SMA 50 Ω male termination x1 (B7)
7. SMA dust caps x4 (B8)
8. SMA torque wrench 0.9 N·m x1 (B9)
9. 8 mm open-end spanner x1 (B10)
Vendor class: Digi-Key / Mouser (per `55585471` §4 lead-time estimates;
live availability UNVERIFIED — no outbound fetch from this host).
If Path A is selected: only the two 868 MHz antennas (A2/A6) are procured
(1-3 days) — or fabricated as wire dipoles in <1 h from lab wire stock.

MUST-FABRICATE:
- Wire dipoles (Path A option, 8.6 cm legs each side —
  `~/repos/balloon/IMPLEMENTATION-PLAN.md:41`).
- 6.5 mm panel bore (B3) — conditional, custodian-gated (Felix).

ON-HAND (per records; no inventory system exists — `bffc7f9d`):
- DUT board with J1/J2 SMA soldered (fleet `c3-a`; not attached to any
  fleet host — `ec80c11e`).
- Reference TX (fleet `c3-b`).
- USB-C data cable, USB console cable (enumerated CH340 x2 + ttyACM0
  path).
- Sealed bag + desiccant assumed as consumable lab stock (REQUIRED by
  `65c9c3df` / fork README:54).

Exactly-once audit (acceptance): RF signal-path items appear exactly once —
Path A: A1-A8 (8 lines); Path B: B1-B11 (11 lines); the two paths are
mutually exclusive at the RF plane (antennas XOR coax); shared/control items
(A3, A4, A7, A8) appear once in Path A and carry over to Path B by note.
No connector identification appears without a cited source (source column
on every line).

---

## Source summary

| Claim carried | Source | Confidence |
|---|---|---|
| DUT RF port = SMA edge-launch, female jack, J1 "SMA-868" / J2 "SMA-2G4", standard polarity | `hub_board_f33.kicad_pcb:165-179` (re-read this session) via `55585471` §1a; `65c9c3df:305-306` verbatim | HIGH (fabricated PCB file), physical board unverified (R1) |
| LR2021 module = PCB pads (pin 9 ANTA, pin 10 2.4/S_ANTA), no connector on module | NiceRF LoRa2021 datasheet V1.3 pin table via `55585471` §1a | HIGH |
| No RF instrument on host; reference TX is the OTA "instrument", kept at room temp | `55585471` §1b; USB censuses `023c5e86`/`c4be4400`/`ec80c11e`; fork README `d7ae93fa` "Bench setup" | HIGH |
| Protocol = decode-count edgescan (not power measurement) | `thermal_bench.py scan_edges()` via `55585471`; fork README `d7ae93fa` | HIGH |
| Chamber feedthrough UNKNOWN; wall-pass pattern = SMA bulkhead in 6.5 mm hole with SMA O-rings | `fe700201`; enclosure/README_big.md:20-26 (re-read this session) | HIGH (pattern), UNKNOWN (actual chamber) |
| O-ring cord spec "2mm, AS568 compatible, Nitrile or silicone" | enclosure/README.md:27,72 (re-read this session) | HIGH (pattern); silicone DECIDED here per `04db4fae` |
| Wire dipole 868 MHz, 8.6 cm legs | `~/repos/balloon/IMPLEMENTATION-PLAN.md:41` (re-read this session; 55585471's `tracker/hardware/` prefix was stale — corrected) | HIGH |
| RG316 0.15 m + 0.50 m lengths | `fe700201` fit computations via `55585471` §3b | MEDIUM (planning lengths, chamber unlocated) |
| ~0.3 dB/m RG316, 0.05-0.1 dB per mated SMA pair, 0.05-0.1 dB bulkhead, 0.3-0.5 dB chain @ 868 MHz | `55585471` §5 (industry-typical, UNVERIFIED — R5) | MEDIUM |
| 165 dB link budget (+22 dBm ref TX, -143 dBm DUT sensitivity) | `55585471` §5; `04db4fae` | HIGH |
| No recalibration for decode-count; recal at DUT face for power-quantitative | This merge, adopting `04db4fae`'s calibration answer + `55585471` §5 | HIGH (consistency of two committed reports) |
| Dust caps / ice bridging top-ranked reversible failure | `04db4fae` FM-1 | HIGH |
| No inventory system of record | `bffc7f9d` | HIGH |
| Representative MPNs (132134-class, ACX-1169-class, 132172-class, FTK-16SR) | `55585471` §3b | MEDIUM (representative, not on-hand) |

---

## Nothing fabricated

No physical hardware was inspected in this merge (DUT not attached to any
fleet host — `ec80c11e`; no chamber located). Every connector identification
is consumed from the cited committed reports and re-verified by reading the
underlying citation sources this session where reachable (PCB file, enclosure
READMEs, IMPLEMENTATION-PLAN.md, fork README). One stale citation path
carried from `55585471` was corrected rather than repeated (A2 dipole
source). MPNs marked TBD are stated as TBD with a required interface spec —
no part number is invented. Lead times and dB figures are the sibling
reports' estimates, labeled UNVERIFIED. The three current-wave sibling
cards produced no output and are flagged as open risks R1-R3, R9 — nothing
was simulated on their behalf.

---

## OPEN RISKS (UNVERIFIED identifications) — terminating list

| # | Open risk | What unblocks it |
|---|---|---|
| R1 | **DUT J1 SMA identification is document-based, not physical**: the SkyMapper Board A PCB was never read directly; identification rests on the carrier-board-family PCB file (`hub_board_f33.kicad_pcb`) + `65c9c3df`'s verbatim "SMA edge-launch". Current-wave physical card `t_b1049504` claimed but produced no output. If the physical board followed the older U.FL schematic (H4), every SMA line in this BOM changes. | One site visit: photo + thread check of J1 (SMA barrel vs 3 mm U.FL press-fit). |
| R2 | **Instrument side is vacuous — no RF instrument exists.** Card `t_da54b09f` claimed, no output. B11 (instrument adapter) is a guess until an instrument is named; its port type (N/BNC/SMA) is unknown. | Procure/name an instrument, then re-run this BOM's B11 line. |
| R3 | **Chamber feedthrough population/mounting UNKNOWN** — chamber unidentified on every record; `fe700201`'s fit verdict is UNKNOWN; current-wave card `t_923c4eca` claimed 02:58 with a kickoff-only session. B2/B3 assume NO existing feedthrough (procure-and-drill); if the chamber has a factory RF feedthrough, B2/B3 may be unnecessary (or already N-type — see B11). | Locate the chamber (cards `t_a2f7f281`/`t_b09424f1`/`t_ffc911f6`), run the `t_923c4eca` survey for real. |
| R4 | **Faraday-cage contingency unresolved**: if the unidentified chamber is metal, Path A (OTA) fails entirely and Path B becomes mandatory (feedthrough + drilling + custodian gate). | Same as R3. |
| R5 | **Every loss figure and cable rating is UNVERIFIED**: no vendor datasheet on host, no outbound fetch permitted; RG316 -40 C rating (`04db4fae`), 12.7 mm bend radius (`fe700201`, industry-nominal), 0.3 dB/m and 0.05-0.1 dB/pair (`55585471` §5) are all industry-typical assumptions. The 0.3-0.5 dB total could be off by ~2x. | Obtain the specific procured assemblies' datasheets at order time; verify by measurement if a power-quantitative variant is planned. |
| R6 | **All MPNs are representative classes** (Amphenol 132134-class, ACX-1169-class, 132172-class, Fujiya FTK-16SR per `55585471`); exact-length/variant part numbers are TBD and no inventory system of record exists (`bffc7f9d`) — nothing in MUST-PROCURE is confirmed on-hand. | Confirm at order time. |
| R7 | **Antenna polarity/impedance hazard (H2)** is UNVERIFIED until parts in hand — 868 MHz RP-SMA lookalikes are the most likely wrong-part event. | Receiving inspection (center pin present). |
| R8 | **USB-C pass-through dimensions UNVERIFIED** (`fe700201`): overmold OD ~9-12 mm industry-typical, cable length across the chamber boundary unmeasured — A7's length requirement is a recommendation, not a measurement. | Caliper site visit per `t_f2b50f53`/`t_03954030` protocol. |
| R9 | **Sibling outputs may yet land**: the three current-wave cards (`t_b1049504`, `t_da54b09f`, `t_923c4eca`) are claimed and running as of this session's fleet-state read; if they later produce outputs that conflict with the consumed on-record findings, this merge must be revisited. Conflicts consumed today: none found between `55585471` §1a/§1b and `fe700201` — they agree on SMA edge-launch, OTA-primary, chamber-UNKNOWN. The one stale citation found (dipole source path, A2) is corrected in place. Consistency note: the sibling coax-dimension card (`bench/coax-bundle-dimensions/REPORT.md`, committed this same session) independently corroborates B1/B2/B4 — same RG316 SMA-m/m 0.15 m + 0.50 m, same SMA bulkhead, same 12.7 mm bend radius, standard polarity 50 Ω — and cites this BOM's B1 spec; no conflict. | Re-read fleet state on next dispatch. |