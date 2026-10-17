# BOM lines — DUT port(s) to chamber-interior to the bulkhead feedthrough (inclusive)

Kanban card: `meshcore:t_fe6e9c1b` — "Specify DUT to chamber-interior and feedthrough line items".
Profile `worker-base` · host `c03rad0r-DQ05proplus` · 2026-10-17 · workspace `/home/c03rad0r/worktrees/t_e1408991`.
Parent (input) card: `t_1bb81290` — normalized interface table (`bench/interface-normalization/INTERFACE-TABLE.md`,
branch `worker-base/t_1bb81290`, HEAD `d6bbc980`, pushed; verified live this session via
`git ls-remote fork refs/heads/worker-base/t_1bb81290` → `d6bbc9808baf9a7d55fbd2baf8d110fa57ebbd12`).

Sibling segment card (NOT this card's scope): `t_a4844b93` — chamber-exterior face to instrument port.
Consolidator: `t_bf841053`. Reviewer: `t_c37d162d`.

---

## 0. SEGMENT BOUNDARY (what is in, what is out)

**In:** from the DUT RF port of the measured leg, through the chamber-interior cable run, **up to and
including the bulkhead feedthrough connector that penetrates the chamber wall.**

**Out (owned by `t_a4844b93`, not listed here):** the exterior cable assembly `C-RF-EXT-1`, any adapter
that mates it to the instrument, and the instrument port itself (parent rows `IF-9`, `IF-10`).

**Out (owned by sibling section cards, cross-referenced in §5 so nothing is double-counted):** sealing
hardware `SEAL-1…SEAL-9/12/13` (`t_a53c6efe`), terminations/loads/caps `TERM-1…TERM-11` (`t_436f6657`),
torque/handling tooling and connector savers `TOOL-1…6`, `SAV-1…4` (`t_378c5705`).

**Interface points covered by this card:** `IF-1` (DUT RF port, measured 868 MHz leg), `IF-5` (interior
cable assembly, frozen ID `C-RF-INT-1`), `IF-6` (feedthrough chamber-interior face), `IF-7` (feedthrough
chamber-exterior face — the same physical connector, its far face), `IF-8` (the wall bore the feedthrough
mounts through).

**Explicitly NOT on this segment:** `IF-2` (DUT 2.4 GHz port) and `IF-3` (SuperMini U.FL) are not part of
the measured RF leg; their protective/terminating parts are `TERM-1`/`TERM-9` and `TERM-8` in `t_436f6657`.
`IF-4`/`IF-11` are the non-RF serial path. None of these appear below, and that absence is deliberate, not a gap.

---

## 1. INPUTS CONSUMED — verbatim reuse, nothing re-derived

The card forbids re-deriving connector identifications from raw sources. Every identification below is a
quotation from the parent table (which itself quotes the committed sibling reports), so the citation chain
DUT-port → instrument-port → feedthrough runs through one on-record hop only.

| Parent row | Value reused verbatim | Status carried |
|---|---|---|
| `IF-1` | CANDIDATE A: "NONE - soldered wire dipole on a bare castellated pad (no connector of any series)". CANDIDATE B: "SMA, standard polarity, edge-launch" / "F - female jack on the PCB edge-launch" | **UNVERIFIED** — two sibling outputs disagree on connector series (conflict X1) |
| `IF-5` | "SMA plug (male) to SMA plug (male) - both ends; standard polarity, straight. RG316 cable class" / "50 ohm - MUST-PROCURE spec value" | **UNVERIFIED** — planned procurement item, MPN TBD (conflict X2) |
| `IF-6` | "UNKNOWN - no chamber and no bulkhead exist on any record … The PLANNED procurement class is SMA, standard polarity, panel-mount jack-to-jack" | **UNVERIFIED / UNSPECIFIED** |
| `IF-7` | "Planned class: F - female jack on the exterior face (jack-jack feedthrough)" | **UNVERIFIED / UNSPECIFIED** (conflict X3 on the representative MPN) |
| `IF-8` | "the value that a located chamber's port must be measured against: SMA bulkhead jack needs 6.5 mm class (project's own documented pattern, enclosure/README_big.md:21-23 'Two SMA bulkhead holes (6.5mm)')" | **UNVERIFIED / UNSPECIFIED** |

Additional committed sources read this session **only** to (a) confirm a citation string or (b) state a
procurement spec the parent did not carry in column form — never to re-identify a connector:
`bench/connector-adapter-bom/REPORT.md` (lines B1/B4/B6, hazards H1/H2/H3, §5 loss figures),
`bench/rf-feedthrough-bom/REPORT.md` (§3b lines 1–3), `bench/chamber-rf-feedthroughs/REPORT.md` (records
F1/F2, STEP 5 LOUD FLAG), `bench/routing-freeze/REPORT.md` (`C-RF-INT-1`, bend/length budget),
`bench/rf-connector-geometry/REPORT.md`, `bench/connector-family-reference/REFERENCE.md` (row 1 thread/hex),
and the committed vendor evidence sheet
`~/reports/feedthrough-vendor-environmental-pressure-ratings-t_731d9414-2026-10-01.md`.

---

## 2. THE SEGMENT, WALKED — every physical item exactly once

```
DUT RF port (IF-1)  ──[RF-1a integral SMA-F jack  |  OR  RF-1b fabricated pigtail, solder pad -> SMA-M]
        │
        └── (optional SAV-1 SMA-M/F bullet saver, sibling t_378c5705 — cross-ref only, not a line here)
        │
   RF-2  C-RF-INT-1  RG316, SMA-M  ==  SMA-M, 0.15 m            [chamber interior]
        │
   RF-3  bulkhead feedthrough, SMA-F  ||wall||  SMA-F, jack-jack, unfiltered   [IF-6 | IF-8 | IF-7]
        │
        └── exterior face -> out of scope (sibling t_a4844b93, C-RF-EXT-1)
```

Gender transitions are therefore: **SMA-M (cable end) into SMA-F (DUT jack)** at one end and
**SMA-M into SMA-F (feedthrough interior face)** at the other. **No gender-changing adapter is required in
this segment as planned** — the M-M cable and the F-F feedthrough are complementary by construction
(`connector-adapter-bom` §STEP 3: "No gender-changing adapter exists in the basic chain"). The only adapter
that can be required is the *series* transition at the interior face if the located chamber presents a
non-SMA port (RF-4, qty 0 conditional).

**Inline pad / attenuator — deliberately NOT a line, with the reason stated (card step 1).** Neither the
parent interface table nor the feedthrough assessment requires one: `IF-5`/`IF-6`/`IF-7` carry no pad, and
the instrument-port sibling records "Attenuator | NO | Not on any record or BOM". Adding one would be an
invented part. It is instead raised as an open risk (R-4) because in the *conducted* contingency the
reference TX's +22 dBm would arrive at the DUT's receive port with no pad in between and the DUT's maximum
input rating is UNVERIFIED on record — a hazard for the consolidator to route, not a part to fabricate here.

---

## 3. BOM LINES — mandated columns, in order

| Item description | QTY | Part number (real MPN, or 'MPN TBD' + required interface spec: connector series, gender, impedance, frequency rating, max VSWR) | Disposition (ON-HAND / MUST-PROCURE / MUST-FABRICATE) | Lead-time estimate | Source/vendor | Cited source for the connector identification |
|---|---|---|---|---|---|---|
| **RF-1a — DUT-side RF interface, CANDIDATE B (doc-level carrier identity): the DUT carrier board's own SMA edge-launch jack.** Series **SMA**, standard polarity; gender **SMA-F (female jack)**, mating a male SMA plug; impedance **50 Ω**; frequency rating 868 MHz use in a DC-18 GHz SMA-class part (class-typical, UNVERIFIED on host); max VSWR ≤1.10:1 at 868 MHz — **REQUIREMENT**, not a confirmed rating (see §4). **No procurement: this is part of the DUT.** **UNVERIFIED — see open risks (X1):** the parent table carries this as CANDIDATE B only; the DUT-port sibling states the opposite verbatim: *"The DUT's LoRa measurement path has ZERO RF connectors. Both RF exits of the LR2021 radio are soldered wire dipoles on bare castellated module pads - no SMA, no U.FL, no MMCX, no connector of any kind"*. Conflict restated, not resolved. | 1 | `custom:SMA_Edge_Mount` footprint, value "SMA-868" on the carrier board — no MPN procured; **SMA, female jack, 50 Ω, standard polarity, edge-launch** | **ON-HAND** (only if CANDIDATE B is the physical board; part of the DUT, not a separate purchase) | — (not procured) | part of DUT carrier board (fleet resource `c3-a`) | Parent `IF-1` CANDIDATE B, quoting `bench/instrument-rf-connectors/REPORT.md`: *"RF port J1 (sub-GHz) \| SMA edge-launch, standard polarity - value \"SMA-868\", net RF_SUB_868, connected to LR2021 pin 9 (ANTA)"* citing `hub_board_f33.kicad_pcb:165-179`, footprint `custom:SMA_Edge_Mount`. **UNVERIFIED** — the same parent row records that the DUT-port sibling corrects this source: *"All three trace to tracker/hardware/hub_board_f33.kicad_pcb:165-179 - which is the 'Balloon Hub V2 - F33 2W PA' board … That is NOT the bench DUT"* |
| **RF-1b — DUT-side RF transition, CANDIDATE A (measured as-built state): fabricated coax pigtail soldered to LR2021 pin 9, terminating in an SMA plug.** Series **SMA** at the outer end, standard polarity; gender transition **bare castellated solder pad (no connector) → SMA-M (male plug)**; impedance **50 Ω**; frequency rating 868 MHz use (sub-GHz leg; the pigtail's own rating is set by the coax used); max VSWR ≤1.10:1 at 868 MHz — **REQUIREMENT**. Supplied cable class RG316 (`OD 2.5 mm, PTFE`) with the same **12.7 mm minimum static bend radius** required of `C-RF-INT-1`; RG316 service rating at −40 °C is **UNVERIFIED** on record. **UNVERIFIED — see open risks (X1/X2):** required only if CANDIDATE A is the physical board. Verbatim parent note: *"If SIBLING (a) is correct this row's gender is wrong at the DUT end and the interior leg must instead be FABRICATED (solder a coax pigtail to LR2021 pad 9) or the DUT swapped for the F33 hub board."* **Mutually exclusive with RF-1a and with RF-2** — it *is* the interior leg in that case (see §5). | 0 (1 if CANDIDATE A holds) | **MPN TBD — MUST-FABRICATE.** Required spec: RG316 (or RG178 where 12.7 mm bend is impossible) pigtail, one end stripped and soldered to the LR2021 pin-9 castellated pad, other end **SMA-M plug, 50 Ω, standard polarity**, 868 MHz use, ≤1.10:1 VSWR at 868 MHz, length ≤0.15 m | **MUST-FABRICATE** | fabricated at bench, <1 h once the DUT is in hand (lab coax stock + one SMA-M plug) | lab stock; SMA-M plug from Digi-Key/Mouser if not stocked | Parent `IF-1` CANDIDATE A + `IF-5` conflict note, quoting `bench/dut-rf-ports/REPORT.md`: *"Port 1 - ANT_SUBGHZ (LR2021 pin 9, sub-GHz 868 MHz): NO CONNECTOR. Wire dipole soldered to the bare pad."* and §7: *"bfc2a899 (connector-adapter-bom) Path B chain - RG316 SMA-m/m assemblies, SMA bulkhead, saver, termination - has nothing to mate to on the DUT side: the DUT's RF exit is a soldered wire, not an SMA jack."* |
| **RF-2 — Chamber-interior cable assembly, frozen ID `C-RF-INT-1`.** Series **SMA** both ends, standard polarity, straight; gender **SMA-M plug to SMA-M plug** (male pin at each end; mates the female jack at each terminus); impedance **50 Ω**; length **0.15 m**; cable class **RG316, OD 2.5 mm, PTFE dielectric**; frequency rating 868 MHz measurement band in a DC-18 GHz SMA-class assembly (class-typical, no per-part rating on record); max VSWR ≤1.10:1 at 868 MHz — **REQUIREMENT**; minimum static bend radius 12.7 mm (25.0 mm preferred). Assemblies to be ordered as **RG316, 50 Ω, standard polarity** — `connector-adapter-bom` H1 rejects 75 Ω (RG-59/RG-6, F/BNC) lookalikes and H2 flags RP-SMA as *"the single most likely procurement error"*. **UNVERIFIED — see open risks (X2):** this assembly's DUT-end gender presupposes a female SMA jack at the DUT; if CANDIDATE A holds, RF-1b replaces this line (qty drops to 0). | 1 (0 if RF-1b is used) | **MPN TBD.** Required spec: RG316 coax assembly, **SMA plug (male) both ends**, male pin, standard polarity, **50 Ω**, 0.15 m, PTFE dielectric, min static bend radius 12.7 mm, ≤1.10:1 VSWR at 868 MHz. Representative class on record: Amphenol **ACX-1169**-class RG316 SMA-m/m patch (exact-length variant TBD) | **MUST-PROCURE** | 2–5 days (Digi-Key / Mouser) | Digi-Key · Mouser · Amphenol RF | Parent `IF-5`, quoting `bench/connector-adapter-bom/REPORT.md` line B1: *"RG316 coax assembly, SMA-male to SMA-male, 0.15 m (DUT to bulkhead, interior) \| 1 \| MPN TBD - required spec: RG316 (OD 2.5 mm, PTFE), SMA plug both ends, male pin, 50 ohm, standard polarity"* and `bench/rf-connector-geometry/REPORT.md`: *"Planned coax, both ends (interior + exterior) \| SMA plug, standard polarity, straight \| male pin (plug), both ends \| documented BOM spec"*. Frozen ID from `bench/routing-freeze/REPORT.md`: *"C-RF-INT-1 \| RG316 SMA-m/m, 0.15 m, interior (DUT J1 -> bulkhead) \| MUST-PROCURE, MPN TBD"* |
| **RF-3 — Bulkhead feedthrough connector, the chamber-wall RF penetration (`IF-6` interior face \| `IF-8` wall bore \| `IF-7` exterior face). THIS IS THE INTERIOR SEGMENT'S TERMINAL ITEM.** Series **SMA**, standard polarity, **both faces**; gender **SMA-F to SMA-F** (female jack each side — a true two-sided jack-jack feedthrough, NOT a jack with a PCB solder tail); impedance **50 Ω**; **UNFILTERED by construction** (a filtered/EMI-suppressed body is a hard-gate reject for the 868 MHz measurement); mounts through the project's documented **6.5 mm panel hole** with a jam nut, O-ring sealed; frequency rating 868 MHz use in a DC-18 GHz SMA-class part (class-typical, UNVERIFIED); max VSWR ≤1.10:1 at 868 MHz — **REQUIREMENT**; on-record insertion loss ~0.05–0.1 dB at 868 MHz. **UNVERIFIED — see open risks (X3)** on the representative MPN, and **UNSPECIFIED** on every physical field of the installed part (no chamber exists on any record — parent `IF-6`/`IF-7`/`IF-8` are all UNKNOWN-with-reason; the LOUD FLAG applies: *"Filtered / EMI-suppressed? UNKNOWN - MUST BE CHECKED ON LOCATION. If any feedthrough body carries a filter … it is UNUSABLE for the RF measurement path"*). | 1 | **MPN TBD** — required spec: **SMA-F to SMA-F (jack both faces)**, panel/bulkhead mount, **50 Ω**, standard polarity, 6.5 mm-class panel hole, **unfiltered**, ≤1.10:1 VSWR at 868 MHz, DC-18 GHz SMA class. Representative candidate that IS positively documented as a two-sided part: **Pasternack PE9184** — vendor-quoted *"hermetic SMA(F)–SMA(F) bulkhead adapter"*, *"Leak rate not to exceed 1x10-7 cc/sec of helium @ 1 atm differential"* (operating-temperature range **not on record** → UNVERIFIED). **Two candidates cited in the record are NOT usable as a two-sided feedthrough and must not be ordered blind:** standing BOM's **Amphenol 132134** — vendor-verified *"SMA PCB Through Hole Straight Jack 50 Ohm"*, Panel Mounting Feature *"Not Applicable"*, IP *"Not Rated"*; and sibling `SEAL-1`'s **Amphenol 132421** — titled *"SMA PCB Through Hole Straight Jack Bulkhead 50 Ohm IP68"*, i.e. a single-ended jack with a PCB termination, so a jack-jack wall feedthrough is **not established** by its cited page | **MUST-PROCURE** | 2–5 days (stock class) if an unfiltered jack-jack part is selected; add ~5–10 days if a hermetic part is chosen | Digi-Key · Mouser · Pasternack · Amphenol RF | Parent `IF-6`/`IF-7` planned class + `bench/chamber-rf-feedthroughs/REPORT.md` STEP 5: *"The planned/procurement feedthrough class is UNFILTERED by construction: an SMA panel-mount jack-jack bulkhead … is a direct gold-plated contact pair with PTFE dielectric - no filter elements"*; bore from `IF-8` quoting *"SMA bulkhead jack needs 6.5 mm class (project's own documented pattern, enclosure/README_big.md:21-23 'Two SMA bulkhead holes (6.5mm)')"*; MPN candidates and the 132134/132421 corrections from `~/reports/feedthrough-vendor-environmental-pressure-ratings-t_731d9414-2026-10-01.md` §1, §2, §3 |
| **RF-4 — CONDITIONAL interior-face series-transition adapter** (required ONLY if the located chamber's interior port is not SMA-F). Series transition **SMA to N** or **SMA to 3.5 mm**; gender transition stated per case: **SMA-F (jack) to N-M (plug)** where the interior face is N-female, or **SMA-F to 3.5 mm-M** where it is 3.5 mm-female; impedance **50 Ω**; frequency rating DC-3 GHz minimum, DC-18 GHz preferred; max VSWR ≤1.10:1 at 868 MHz. **UNSPECIFIED — see open risks:** no chamber, no port and no gender exist on any record, so neither the series nor the gender of the far side is known; the parent table warns *"interior and exterior may differ (e.g. N-exterior / SMA-interior adapter feedthrough) - only a physical walk resolves each side separately"* and that a located chamber *"may instead present N-type, 3.5 mm, or a filtered OEM port"*. Buying this today would be a guess — carried at qty 0 for that reason. | 0 (1 if the located interior face is N-F or 3.5 mm-F) | **MPN TBD** — required spec: 50 Ω, **SMA-F to N-M** or **SMA-F to 3.5 mm-M** (both sexes stated explicitly at order), standard polarity on the SMA side, DC-3 GHz minimum, ≤1.10:1 VSWR at 868 MHz, brass/gold, PTFE | **MUST-PROCURE** (conditional — qty 0 today) | 1–3 days once the interior face is identified at the site walk | Digi-Key · Mouser · Pasternack | Parent `IF-6` (planned class SMA F-F, "no port to inspect"), `IF-7` (interior/exterior may differ, quoted above) and `IF-8` ("A located chamber may instead present N-type, 3.5 mm, or a filtered OEM port"), quoting `bench/chamber-rf-feedthrough-list/FEEDTHROUGH-LIST.md` FT-1 and `bench/chamber-rf-feedthroughs/REPORT.md` record F1. **UNSPECIFIED — no identification exists to cite; this line states the requirement, not a part** |

**Row count: 4 distinct physical items** (RF-1a + RF-1b are mutually exclusive candidates of the same
interface; RF-2, RF-3, RF-4). Excluding the mutually-exclusive pair, **3 line items are actually built or
bought** for this segment in either world: the DUT-side transition (integral jack *or* fabricated pigtail),
the interior cable, the bulkhead feedthrough — plus one conditional adapter at qty 0.

**Nothing else on this segment exists.** No inline pad/attenuator (§2), no second cable, no directional
coupler, no bias tee, no adapter in the basic chain (M-M cable + F-F feedthrough are complementary), no
instrument (none exists). Quantity of each item = 1 because the chain is a single serial run.

---

## 4. UNVERIFIED / UNSPECIFIED REGISTER — every flag, with its conflict restated inline

**Structural fact first, because it governs the whole table: the parent table has ZERO `VERIFIED` rows.**
The DUT is not attached to any host, no chamber exists on any record, and no RF instrument exists. Every
line above therefore inherits an open term, and none of them is resolved here.

| # | Line(s) | Flag | Conflict / gap, restated | Where it came from |
|---|---|---|---|---|
| **X1** | RF-1a, RF-1b, RF-2 | **UNVERIFIED** | **The DUT RF port may have no connector at all.** Sibling (a): *"ZERO RF connectors … soldered wire dipoles on bare castellated module pads"*. Sibling (b): *"SMA edge-launch, standard polarity - value 'SMA-868'"*. Sibling (a) records that it corrects (b)'s source (the F33 hub board is *"NOT the bench DUT"*); sibling (b) records its own caveat (*"The SkyMapper Board A PCB was not read directly"*). **Both candidates retained on two separate lines; neither is dropped.** | Parent `IF-1`, conflict table X1 |
| **X2** | RF-1b, RF-2 | **UNVERIFIED** | **The interior leg's DUT-end gender depends on X1.** `connector-adapter-bom` B1 is an SMA-m/m assembly, which presupposes an SMA-F jack at the DUT; verbatim: *"has nothing to mate to on the DUT side: the DUT's RF exit is a soldered wire, not an SMA jack."* If that holds, RF-2 drops to 0 and RF-1b (fabricated pigtail) *is* the interior leg. | Parent `IF-5`, conflict table X2 |
| **X3** | RF-3 | **UNVERIFIED** (representative MPN only) | **Which catalogue part represents the feedthrough.** Standing BOM / sibling (b): *"Amphenol 132134-class"*. Vendor evidence sheet: 132134 is *"SMA PCB Through Hole Straight Jack 50 Ohm"* with Panel Mounting Feature *"Not Applicable"*, IP *"Not Rated"* — **not a panel feedthrough**. Sibling sealing card `t_a53c6efe` replaced it with **132421**, whose own title is *"SMA PCB Through Hole Straight Jack Bulkhead 50 Ohm IP68"* — a PCB-terminated single-ended jack, so a jack-jack wall feedthrough is not established there either. **Series (SMA), gender (F-F) and impedance (50 Ω) are NOT in conflict** — only the representative MPN is. RF-3 therefore carries `MPN TBD` + the required F-F spec, with PE9184 named only as the one candidate the record positively documents as SMA(F)–SMA(F). | Parent `IF-7`, conflict table X3; `~/reports/feedthrough-vendor-environmental-pressure-ratings-t_731d9414-2026-10-01.md` §1 |
| **U1** | RF-3, RF-4 | **UNSPECIFIED** | **Every physical field of the installed feedthrough is UNKNOWN** — interior series, exterior series, gender per face, impedance, frequency rating, bore ID, panel thickness, filter construction. Verbatim: *"no thermal chamber exists on any record or host, so there is no bulkhead to walk"*; all five penetration classes F1–F5 are *"NON-EXISTENT on every record"*. | Parent `IF-6`, `IF-7`, `IF-8`; `bench/chamber-rf-feedthroughs` STEP 0/STEP 5; `bench/chamber-rf-feedthrough-list` FT-1…FT-5 |
| **U2** | RF-3 | **UNVERIFIED** | **Filtered construction would silently destroy the measurement.** *"If any feedthrough body carries a filter (marked 'filtered', or has a bulky body with feedthrough-capacitor construction), it is UNUSABLE for the RF measurement path"* — *"the single most dangerous silent-corruption risk in the conducted path"*. Not checkable without the chamber; carried as an order-time and site-visit gate. | `bench/chamber-rf-feedthroughs/REPORT.md` STEP 5 LOUD FLAG |
| **U3** | RF-1a, RF-1b, RF-2, RF-3, RF-4 | **UNVERIFIED (requirement, not rating)** | **Max VSWR ≤1.10:1 at 868 MHz is a requirement I state for order-time acceptance, not a confirmed property.** The record's only VSWR statement is a project claim — *"at 868 MHz (and even 2.4 GHz) standard SMA is fully adequate (VSWR spec 1.05:1 class at these frequencies)"* — and **no cited vendor page publishes a VSWR** for 132421, 901-1075x or the RG316 assembly class. Likewise the DC-18 GHz frequency rating is *class-typical*, UNVERIFIED on host. | `bench/connector-adapter-bom` H3; vendor sheet §2–§6 (absence stated there as an absence) |
| **U4** | RF-1a, RF-2, RF-3 | **UNVERIFIED** | **Impedance is inherited, not measured.** Parent: *"50 ohm - UNVERIFIED, inferred from the SMA family standard and the LR2021 datasheet's 50-ohm RF port; no connector datasheet on host"*. Stated on every line so no reader mistakes it for a measured value. | Parent `IF-1`, `IF-5`, `IF-6` |
| **U5** | RF-1b, RF-2 | **UNVERIFIED** | **RG316 at −40 °C**: no vendor cable datasheet on host; the −40 °C service floor and the 12.7 mm static bend radius are *"INDUSTRY NOMINAL, UNVERIFIED"* carried from the fit report. | `bench/routing-freeze/REPORT.md` (§bend rules), `bench/cable-feedthrough-failure-modes` |

**Not flagged, because they are committed on record:** the SMA thread/hex group (1/4"-36 UNS, 6.35 mm
major, 7.94 mm AF) in `bench/connector-family-reference/REFERENCE.md` row 1; the 6.5 mm panel-hole pattern
(`enclosure/README_big.md:21-23`); the frozen cable ID and its 0.15 m length (`bench/routing-freeze`);
the B1/B4 line specs (`bench/connector-adapter-bom`).

---

## 5. DE-CONFLICTION — what NOT to count twice (for the consolidator `t_bf841053`)

| Item | Other card / lineage that already carries it | Ruling |
|---|---|---|
| Bulkhead feedthrough **SMA-F/F, jack-jack, unfiltered, 6.5 mm hole** | sealing sibling `t_a53c6efe` **SEAL-1**; predecessor `connector-adapter-bom` **B2**; `rf-feedthrough-bom` §3b line 2 | **Same physical item, three citations.** RF-3 is the signal-path line with the full electrical spec (series/gender/impedance/frequency/VSWR) and the corrected MPN position; SEAL-1 is the sealing line. **Keep ONE row; keep the corrected MPN and the F-F requirement.** |
| Bulkhead **jam nut** and **sealing washer / O-ring** | `t_a53c6efe` **SEAL-2**, **SEAL-3**; `connector-adapter-bom` **B5** | **Not repeated here.** Mechanical sealing hardware belongs to the sealing card; RF-3 states only that the part must mount with a jam nut in a 6.5 mm hole. |
| **6.5 mm wall bore / drilling** | `connector-adapter-bom` **B3** (MUST-FABRICATE, custodian-gated; *"drilling a real chamber is a custodian decision - Felix … must approve any penetration"*) | **Not a component on this segment.** Prerequisite to RF-3, already carried. Not duplicated. |
| **Connector saver SMA-M/F** on the DUT jack | `t_378c5705` **SAV-1** (≡ predecessor **B6**) | **Cross-ref only.** If fitted, the chain reads DUT jack (F) → SAV-1 bullet (M/F) → RF-2 plug (M); gender stays consistent. No line here. |
| **Connector saver** on the feedthrough interior face | `t_378c5705` **SAV-2** | **Cross-ref only.** RF-3's interior face is the interface SAV-2 protects. |
| **SMA 50 Ω terminator / shorting cap / dust caps** | `t_436f6657` **TERM-1/TERM-4/TERM-5/TERM-6/TERM-7/TERM-9** | **Not on this segment.** They terminate/cap *unmated* ports; every port here is mated in-run. The feedthrough is in the signal path and must **never** be terminated in-run. |
| **Exterior cable `C-RF-EXT-1` (0.50 m), instrument adapter, instrument port** | sibling segment card **`t_a4844b93`** | **Out of scope.** RF-3's exterior face is that card's starting boundary. |
| **Antennas (A2/A6), sealed bag, desiccant, USB-C and console cables** | `connector-adapter-bom` **A2/A6/A3/A4/A7/A8** — the *primary over-the-air* path | **Not RF interior-segment items.** In PATH A no RF component exists on this segment at all; this table exists for the conducted contingency, exactly as the parent table states (*"The primary measurement path needs ZERO RF feedthrough parts"*). |

---

## 6. ACCEPTANCE CROSS-CHECK (card sentence by sentence)

| Acceptance requirement | Status |
|---|---|
| Every component on this segment appears exactly once with a quantity and a disposition | **PASS** — 4 lines: RF-1a (DUT integral jack, ON-HAND), RF-1b (fabricated pigtail, MUST-FABRICATE), RF-2 (`C-RF-INT-1`, MUST-PROCURE), RF-3 (feedthrough, MUST-PROCURE), plus RF-4 (conditional adapter, MUST-PROCURE qty 0). RF-1a/RF-1b are *mutually exclusive candidates of one interface*, declared as such on both rows and in §2/§4 — they are not a duplicate of one item. Nothing else exists on this segment and §5 shows every nearby item that belongs to a sibling. |
| Every line names series, gender transition and impedance | **PASS** — RF-1a SMA-F/50 Ω; RF-1b `pad → SMA-M`/50 Ω; RF-2 `SMA-M → SMA-M`/50 Ω; RF-3 `SMA-F → SMA-F`/50 Ω; RF-4 `SMA-F → N-M` / `SMA-F → 3.5 mm-M`/50 Ω. Impedance is stated on all five and its provenance (inferred, UNVERIFIED) is stated in U4. |
| Every connector identification traces to a cited sibling source or is flagged UNVERIFIED | **PASS** — every identification cell quotes the parent row (`IF-1/5/6/7/8`) and, through it, the committed sibling report with file path and/or line; the three rows whose identification is contested (X1, X2, X3) carry `UNVERIFIED — see open risks` and restate the conflict verbatim, and RF-4 carries `UNSPECIFIED` with the reason that no identification exists at all. |
| If a row came from a UNVERIFIED/UNSPECIFIED parent row, keep it and restate the conflict inline | **PASS** — all five rows derive from `UNVERIFIED`/`UNSPECIFIED` parent rows; each carries the flag **and** the conflict text in its own cells (§4 is the index, not a substitute). |
| Do not list the same physical item twice; if two roles use the same part, combine with summed QTY | **PASS** — no item repeats; the only multi-role item is the feedthrough itself (interior face, wall bore, exterior face = three interface points on ONE physical connector), which is **one** line (RF-3), not three. Cross-card overlaps are listed in §5 rather than re-listed. |
| Columns exactly as mandated | **PASS** — §3 header is the seven mandated columns in the card's order. |

---

## 7. NOTHING FABRICATED — and how this file can be re-checked

- **No part number is invented.** RF-3's `MPN TBD` names PE9184 only because the committed vendor sheet
  positively documents it as *"hermetic SMA(F)–SMA(F) bulkhead adapter"*; the two MPNs the record already
  cited (132134, 132421) are shown with their vendor-quoted titles and the reason neither is established as
  a two-sided feedthrough. RF-2 inherits the record's *"representative class"* (ACX-1169) explicitly labelled
  as a class. RF-1a, RF-1b and RF-4 carry no MPN at all.
- **No identification is re-derived.** Every series/gender/impedance cell traces to a parent row and the
  committed sibling report behind it; the raw sources were not re-read to produce a new identification.
- **No measurement, photograph, physical inspection, bench measurement or chamber observation is claimed.**
  No chamber, no bulkhead, no DUT, no RF instrument and no coax exist on this host or on any record.
- **No VSWR, insertion-loss, temperature or impedance figure is asserted as a part property.** The
  ≤1.10:1 and DC-18 GHz values are labelled REQUIREMENT / class-typical and their absence from vendor pages
  is stated (U3); the 0.05–0.1 dB feedthrough figure is quoted as the record's planning figure.
- **Conflicts are emitted, not resolved** (X1, X2, X3) — including one the parent could not have known:
  sibling `SEAL-1`'s 132421 is titled a *PCB through-hole jack*, so the jack-jack feedthrough this segment
  needs is **not** established by either Amphenol candidate on record.
- **Verification:** `_verify_t_fe6e9c1b.py` in this workspace re-derives the acceptance conditions from the
  shipped file (column count and order, one QTY + one disposition token per row, series/gender-transition
  and 50 Ω present on every row, UNVERIFIED/UNSPECIFIED annotation on every row that inherits one, citation
  presence, no duplicate physical item, no `VERIFIED` claim). Results are recorded in the completion handoff.
- **Workspace/repo:** this workspace is a scratch directory and is **not a git repository**
  (`git status` → *"fatal: not a git repository"*), so there is nothing to commit here; the deliverable is
  written to `~/reports/` with a workspace copy and attached to the card, matching the three sibling
  section cards on this decomposition (`t_436f6657`, `t_378c5705`, `t_a53c6efe`). The parent's repo artefact
  (`bench/interface-normalization/`) lives on branch `worker-base/t_1bb81290` and was **read from git, not
  modified**.
