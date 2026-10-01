# RF matching network + antenna geometry — CORROBORATION ONLY

**Card:** meshcore `t_a82deb2b` — "Document RF matching network and antenna geometry as corroboration only"
**Author:** worker-base · **Date:** 2026-10-01 · **Tier:** docs (read-only; no source file changed by this run)
**Board repo:** `~/repos/meshcore` (HEAD `26f93b71`) · **Source repo:** `~/repos/balloon` (HEAD `75913e2a`)

Corroboration-only pass. Nothing in this document overrides a config value or a
marked value, and **no frequency is derived from geometry anywhere in this
document** — geometry statements are reduced to dimension-vs-wavelength *ratios*
and band-level language only.

---

## 0. Scope: two objects that must not be conflated

| Object | What it is | Silk? | Matching network |
|---|---|---|---|
| **DUT** — "SkyMapper Board A" (`c3-a`) | Hand-wired **breadboard assembly**: NiceRF LoRa2021 module on an ESP32-C3 SuperMini carrier | **None** — a hand-wired breadboard has no PCB silkscreen (sibling `708585a5`) | not established — see §1.4 |
| **`hub_board_v1.kicad_pcb`** | the KiCad *design file* for an unfabricated carrier hub board (50 × 40 mm Edge.Cuts) | Yes — design silk `F.SilkS` reads **`868MHz`** / **`2.4GHz`** | **none** |

The card asks for "silkscreen or schematic reference", so both are documented.
Every statement below is explicitly scoped to one of these two objects. **No
physical board was inspected** — the DUT is not attached and no camera exists on
this host (standing constraint; siblings `708585a5` / `0b7bfe92` / `f14f6a92`).

---

## 1. Matching network — topology and values

**Result (scoped): on the `hub_board_v1.kicad_pcb` design there is NO matching
network — zero intervening components between module pin and antenna pad.** This
is a *structural* finding read out of connectivity data, not an inference from
absence of documentation.

### 1.1 Connectivity — the load-bearing evidence

`hub_board_v1.kicad_pcb`, nets `12` = `RF_SUB_868` and `13` = `RF_2G4_2400`.
Every pad on those nets (absolute board coordinates):

| Net | Pad A | Pad B | Intervening parts |
|---|---|---|---|
| `RF_SUB_868` (net 12) | `U2` pad 9 @ (15.10, 19.84) | `AE1` pad 1 @ (48.00, 20.00) | **none** |
| `RF_2G4_2400` (net 13) | `U2` pad 10 @ (34.91, 19.84) | `AE2` pad 1 @ (48.00, 25.00) | **none** |

Each net carries exactly **two** nodes. There is no third node, therefore no L,
C, R, balun, filter or switch sits anywhere on that RF path. Copper is a direct
trace:

| Net | Segments | Width | Total copper | Layers | Vias |
|---|---|---|---|---|---|
| `RF_SUB_868` | 3 | 0.8 mm | 36.745 mm | F.Cu only | 0 |
| `RF_2G4_2400` | 4 | 0.8 mm | 23.935 mm | F.Cu (3) + B.Cu (1) | 2 (φ0.6/0.3 mm) |

The generated netlist `tracker/hardware/hub_board/hub_schematic.net` confirms the
same two-node topology independently, and the generator
`hub_board/hub_schematic.py:408-411` states the intent verbatim:

```
408:    # 9. Antenna wire pads
410:    rf_subghz += ant_sub["1"]     # 16.4cm wire dipole (868 MHz Sub-GHz)
411:    rf_2g4    += ant_2g4["1"]     # 3.1cm wire dipole (2.4 GHz)
```

### 1.2 Component census of `hub_board_v1.kicad_pcb` — no inductors exist at all

```
Capacitor_SMD:C_0402_1005Metric          x 5     Capacitor_SMD:C_0805_2012Metric  x 2
Capacitor_THT:CP_Radial_D8.0mm_P3.50mm   x 1     Resistor_SMD:R_0402_1005Metric   x 5
Diode_SMD:D_SOD-123 x 1   LED_SMD:LED_0603_1608Metric x 1   Package_TO_SOT_SMD:SOT-23-5 x 1
TestPoint:TestPoint_Pad_D1.0mm x 6        TestPoint:TestPoint_THTPad_D2.0mm_Drill1.0mm x 2
Connector_PinHeader_2.54mm: 1x02 x1, 1x04 x2, 1x13 x1
custom:ESP32-C3_Mini_V1_Header x 1        custom:LoRa2021_Castellated x 1
```

`hub_board_v1.kicad_pcb` contains **zero inductors**, and no capacitor on it
sits on an RF net (see §1.1). This independently rules out any L/C matching
topology on that design. The capacitors present are on the power rails; their
individual roles were not traced this pass and are not claimed beyond that.

### 1.3 Values, topology, and silkscreen / schematic reference

| Item | Value |
|---|---|
| Component designators (L/C) | **none exist** on the RF path — 0 inductors on `hub_board_v1`, 0 extra nodes on either RF net |
| Topology | direct module pin → antenna pad; single-ended 50 Ω; no pi/T/L network, no balun, no DC block, no RF switch. (SP4T switch and FEM are *planned options only*, `docs/component-guide.md:238-250` — not present in any design) |
| Schematic reference | `hub_board/hub_schematic.py:213-218` (`AE`/`AE1`, values `ANT_SUB_868` / `ANT_2G4_2400`), `:408-411`; netlist `hub_schematic.net` nets `RF_SUB_868` / `RF_2G4_2400` |
| Silkscreen reference | `hub_board_v1.kicad_pcb` `F.SilkS` `Value` texts: **`868MHz`** (AE1), **`2.4GHz`** (AE2), font 0.8 mm |
| Vendor datasheet | NiceRF `LoRa2021-Module-Datasheet-V1.3.pdf` pin table: pin 9 "sub-GHz band antenna interface, **external 50-ohm antenna**"; pin 10 "2.4G and S band antenna interface, **external 50-ohm antenna**" (balloon git `cc92c869`, `docs/assets/lr2021/`) |

The datasheet has **no** matching-network section and no recommended L/C values
(`grep -ci matching` over the extracted text = **0**). The module is specified as
a bare 50 Ω interface.

### 1.4 Explicit limit of the claim — the DUT's matching network is NOT established

§1.1-1.3 establish this **only for the `hub_board_v1` design file**. The DUT is a
hand-wired assembly, not that board, so this pass does **not** claim "the DUT has
no matching network". There is a record asserting the module carries an *onboard*
matching network — `docs/coordination/PCB-AUTO-ROUTE-EXECUTION-PLAN-V2.md:209`
("the LR2021 module has its own onboard matching network and the antenna traces
are short (<10mm)") — which sits **outside** the DUT's own record set (the DUT's
records are `wiring-dev-board.csv`, `breadboard-wiring-guide.md`,
`FLIGHT-BOARD-PLAN.md`). No designator, value, topology or schematic for any DUT
matching network exists on any record, and the datasheet's own pin table
specifies a bare 50 Ω interface. **Verdict for the DUT: no matching network is
recorded; whether the module die contains one internally is not decidable from
the records on this host and is left open.** It is flagged here rather than
resolved, and it does not affect the marked band.

### 1.5 Designator collision between the two schematic-side artifacts (read with care)

The schematic-side references for the antenna pads **collide with each other** —
recorded here because a reader following the "schematic reference" column would
otherwise be sent to the wrong band:

| Artifact | 868 MHz pad | 2.4 GHz pad |
|---|---|---|
| `hub_board_v1.kicad_pcb` `F.SilkS` (and `FLIGHT-BOARD-PLAN.md:85-86`) | **`AE1`** | **`AE2`** |
| `hub_board/hub_schematic.net` (generated) | `AE` (unannotated) | **`AE1`** (unannotated) |

So netlist ref `AE1` sits on net `RF_2G4_2400`, while the *same* designator `AE1`
on the board sits on net `RF_SUB_868`. The collision is an artifact of the
generator using one placeholder ref (`hub_schematic.py:214,217`, both
`ref="AE"`) that KiCad auto-annotated differently in each output. **The
authoritative anchor is the net name, never the ref designator**: `RF_SUB_868` ⇔
868 MHz pad, `RF_2G4_2400` ⇔ 2.4 GHz pad. This pass used the net names
throughout. (Net *codes* are likewise per-file — net 12 in the PCB vs net 12 in
the netlist are different nets — so codes are quoted only alongside their file.)

---

## 2. Antenna — type, geometry, dimensions, markings

**Result: the antenna is NOT a printed PCB element.** `hub_board_v1.kicad_pcb`
contains **no drawn antenna geometry** — `gr_line`/`gr_poly`/`gr_arc` graphic
count on the copper/silk layers = 0, and no antenna-class footprint exists in the
census (no `Antenna*`, `Yagi`, `Patch`, `Monopole`, `Coil` names). The antenna is
a **hand-soldered external wire element** attached to a plain through-hole / SMD
pad.

### 2.1 Type and dimensions (as recorded — no dimension measured this pass)

| Antenna | Type | Construction | Dimension | Marking |
|---|---|---|---|---|
| Sub-GHz (pin 9) | wire dipole, centre-fed | soldered to pad `AE1` / `AE` | **16.4 cm total** | design silk **`868MHz`**; DUT has no silk — wiring row name `ANT_SUBGHZ` |
| 2.4 GHz (pin 10) | wire dipole, centre-fed | soldered to pad `AE2` / `AE1` | **3.1 cm total** | design silk **`2.4GHz`**; DUT has no silk — wiring row name `ANT_24GHZ` |

A second construction record — `docs/breadboard-wiring-guide.md:52-56` —
describes each sub-GHz element as a **λ/4 element of 8.6 cm per leg**, bent 180°
at the pad. Both records are reproduced as-is. The divergence between the
16.4 cm and 2×8.6 cm records is **disclosed, not resolved** (open item; sibling
`708585a5` ambiguity A1).

### 2.2 Annotation self-consistency check — INFERRED-FROM-ANTENNA

The sources attach their own λ labels. Comparing each recorded dimension to the
nominal free-space wavelength of the band **the source itself names**
(`wavelength_a82deb2b.py`; ratios only — no frequency is computed or stated):

| Recorded dimension | Source's own label | dim ÷ nominal λ of that label | Reading |
|---|---|---|---|
| 16.4 cm | "λ/2 @ 868 MHz" (`component-guide.md:69`) | 0.95 | consistent within end-effect spread |
| 8.6 cm | "λ/4 @ 868 MHz" (`breadboard-wiring-guide.md:55`) | 1.00 | consistent |
| 3.1 cm | "λ/2 @ 2.4 GHz" (`component-guide.md:70`) | **0.50** | **factor-2 mismatch** |

**INFERRED-FROM-ANTENNA:** the 3.1 cm element is the λ/4 dimension in its
labelled band, not λ/2 as the sources annotate it. This is a **documentation
defect in the corroborating sources**, stated at band level only. It is one
concrete reason antenna geometry must remain corroboration-only and must never
override a marked value.

### 2.3 Markings on the antenna itself

None. A bare copper wire carries no printed marking. The only DUT-side "marking"
is the wiring-row label in `tracker/hardware/footprints/wiring-dev-board.csv`
(`ANT_SUBGHZ`, `ANT_24GHZ`); on the design file it is the `F.SilkS` value text
plus the `AE1` / `AE2` reference designators.

### 2.4 Explicit non-antenna: the feed trace is not a radiator

**INFERRED-FROM-ANTENNA:** both RF nets run 23.9 / 36.7 mm of 0.8 mm-wide copper
on `hub_board_v1`. Treated as microstrip this is a *feed line*, not a radiating
element — stated so a later reader does not mistake trace length for antenna
geometry. No impedance or electrical-length calculation is performed on it, and
no frequency is derived from it.

---

## 3. Findings table (card-required format)

| # | Observation | Source (board / schematic / silk reference) | Evidence label | Implication (explicitly an inference) |
|---|---|---|---|---|
| 1 | `hub_board_v1` RF path has **no matching network**: exactly 2 nodes per RF net, 0 intervening parts | `hub_board_v1.kicad_pcb` nets 12/13 (`U2.9→AE1`, `U2.10→AE2`); `hub_board/hub_schematic.net`; `hub_schematic.py:213-218` | **MARKED** | Inference: the radio is used at its native 50 Ω interface, so no narrowband tuning element exists that could shift the band — this corroborates the marked band, it does not set it |
| 2 | `hub_board_v1` contains **0 inductors**, and no capacitor on it sits on an RF net | `hub_board_v1.kicad_pcb` footprint census + net 12/13 pad lists (§1.1) | **MARKED** | Inference: any L/C match topology is ruled out for this design by structural absence |
| 3 | Module antenna pins specified as bare 50 Ω | NiceRF datasheet V1.3 pin table (balloon git `cc92c869`), pin 9 / pin 10 | **MARKED** | Inference: vendor intends an external 50 Ω antenna directly on the pin — consistent with #1 |
| 4 | Antenna pads: `AE1` silk value **`868MHz`**, `AE2` silk value **`2.4GHz`** | `hub_board_v1.kicad_pcb` `F.SilkS` Value texts | **MARKED** | Inference: the board silk already names the bands, so the geometry below can only corroborate, never set, them |
| 5 | Sub-GHz element is a hand-soldered **wire dipole**, 16.4 cm total | `wiring-dev-board.csv` row `ANT_SUBGHZ`; `FLIGHT-BOARD-PLAN.md:85`; `component-guide.md:69` | **MARKED** | Recorded dimension, not geometry-derived — no inference is drawn from it here; see #8 for the labelled inference |
| 6 | 2.4 GHz element is a hand-soldered **wire dipole**, 3.1 cm total | `wiring-dev-board.csv` row `ANT_24GHZ`; `FLIGHT-BOARD-PLAN.md:86`; `component-guide.md:70` | **MARKED** | Recorded dimension, not geometry-derived — no inference is drawn from it here; see #10 for the labelled inference |
| 7 | Same sub-GHz element also recorded as **2 legs × 8.6 cm** | `breadboard-wiring-guide.md:52-56` | **MARKED** | Recorded dimension, not geometry-derived — no inference is drawn from it here; see #9. Divergence vs #5 (0.8 cm) is left open |
| 8 | 16.4 cm measures 0.95 × the nominal free-space λ/2 of the band the source names | derived from #5 | **INFERRED-FROM-ANTENNA** | Inference: the sub-GHz element's length is **consistent with the sub-GHz band marked in #4**. Band-level statement only |
| 9 | 8.6 cm measures 1.00 × the nominal free-space λ/4 of the band the source names | derived from #7 | **INFERRED-FROM-ANTENNA** | Inference: corroborates #8's band-level reading; the two sub-GHz records agree to within 5 % of each other in wavelength terms |
| 10 | 3.1 cm measures 0.50 × the nominal free-space λ/2 the source labels it, i.e. it is the λ/4 dimension of that band | derived from #6 | **INFERRED-FROM-ANTENNA** | Inference: the 2.4 GHz element's length is **consistent with the 2.4 GHz band marked in #4**. The source's own λ annotation is a factor-2 error (§2.2), recorded not silently corrected |
| 11 | Antenna is **not** a printed board element; the PCB holds no drawn antenna | `hub_board_v1.kicad_pcb` (0 graphics, 0 antenna footprints, Edge.Cuts 50×40 mm) | **MARKED** | Inference: the card's example phrase "printed trace length" does not apply to this design — the radiator is external wire |
| 12 | Feed trace 23.9 / 36.7 mm × 0.8 mm is a **feed line**, not a radiator | `hub_board_v1.kicad_pcb` segment geometry | **INFERRED-FROM-ANTENNA** | Inference: this copper must not be read as antenna geometry |

**Acceptance check:** every geometry-derived statement (#8, #9, #10, #12)
carries the `INFERRED-FROM-ANTENNA` label and is expressed as a
dimension-vs-wavelength ratio. **No precise carrier frequency is asserted from
geometry anywhere in this document.** (The frequency-shaped strings `868MHz` and
`2.4GHz` appear only as *marked* silk/record values quoted from the board and the
documents, never as a figure derived from a dimension.)

---

## 4. Hard-rule compliance — what was NOT done

- No config value or marked value is overridden by geometry. Items #8-#10 and #12
  are labelled `INFERRED-FROM-ANTENNA`; the geometry each is derived from sits in
  its "source"/"observation" columns, and the band-level reading is confined to
  its "implication" column.
- **No ppm, no calibration, no frequency offset, no error budget computed.**
- **No frequency derived from geometry at all.** Geometry is reported as
  *ratios* against the wavelength of the band the source itself names; the only
  frequency-shaped strings in this document are the **marked** silk/record
  values (`868MHz`, `2.4GHz`) quoted from the board and the record labels.
- No physical measurement was taken; every dimension is a documented record, not
  a caliper reading. The 16.4 cm vs 2×8.6 cm divergence is disclosed, not
  reconciled, and the source docs' λ/2-vs-λ/4 mislabel is disclosed, not
  silently corrected.
- §1.4 scopes the "no matching network" finding to `hub_board_v1` and leaves the
  DUT's internal module question open rather than overclaiming.
- No outbound network contact, no probes (standing constraint).

---

## 5. Provenance

| Artifact | Location | Identity |
|---|---|---|
| Board (design) | `~/repos/balloon/tracker/hardware/hub_board_v1.kicad_pcb` | last touched by `698a039e` |
| Netlist | `~/repos/balloon/tracker/hardware/hub_board/hub_schematic.net` | generated by `hub_schematic.py` |
| Netlist generator | `~/repos/balloon/tracker/hardware/hub_board/hub_schematic.py:213-218,408-411` | — |
| Vendor datasheet | `~/repos/balloon` git `cc92c869:docs/assets/lr2021/LoRa2021-Module-Datasheet-V1.3.pdf` | 836 317 B; extracted with `pdftotext -layout` |
| Wiring records | `wiring-dev-board.csv`, `docs/breadboard-wiring-guide.md:52-56`, `FLIGHT-BOARD-PLAN.md:85-86`, `docs/component-guide.md:69-70` | balloon working tree `75913e2a` |
| Analysis scripts | `tracelen_a82deb2b.py`, `netcheck_a82deb2b.py`, `wavelength_a82deb2b.py` (workspace `~/worktrees/t_e1408991/`) | read-only |

**Consistency with siblings:** agrees with `708585a5` (rf-port-antenna-config —
no connector, bare pads, wire dipole) and `0b7bfe92` (dut-rf-ports — zero
connectors on the LR2021 path). The F33 module/board family (which does carry
SMA connectors and a +33 dBm PA) is a different module on a different board and
is excluded, per `0b7bfe92`.

**Duplicate check:** no pre-existing deliverable for `t_a82deb2b` exists —
`grep -rIl "a82deb2b" ~/reports/ ~/repos/meshcore/` returns nothing, and no
`bench/*match*` directory exists on the meshcore board.

---

## 6. Review history

- **Pass 1** — cold cross-family review by `deepseek/deepseek-v4-flash` (non-GLM
  family, zero prior context) returned **VERDICT: REJECTED** with 4 major
  findings, all addressed: (a) precise derived frequencies in the findings table
  → replaced with dimension-vs-wavelength ratios; (b) unlabelled arithmetic table
  → labelled `INFERRED-FROM-ANTENNA`; (c) "no matching network" overclaimed for
  the DUT → scoped to `hub_board_v1` with an explicit §1.4 open item;
  (d) §1.2/§4 internal inconsistency → corrected.
  Artifact: `~/reports/reviews/meshcore-t_a82deb2b-deepseek_deepseek-v4-flash-pass1.md`
- **Pass 2** — same lane, re-reviewed the revised artifact; the run exhausted its
  completion budget on reasoning and returned `finish_reason=length` **with no
  verdict emitted** (the documented reasoning-first trap). Its transcript
  surfaced one substantive nit, which was applied: the §2.4 feed-trace geometry
  statement was given the `INFERRED-FROM-ANTENNA` label (row #12 likewise).
  Artifact: `~/reports/reviews/meshcore-t_a82deb2b-deepseek_deepseek-v4-flash-pass2.md`
- **Pass 3** — same lane, re-run with a verdict-forcing prompt (the constraint is
  disclosed here as a prompt change, not a re-roll artifact) →
  **VERDICT: APPROVED, MAJOR: none**, 5 minor findings. All five applied on this
  final revision: (i) the "no frequency anywhere" self-claim reworded to "no
  precise carrier frequency is asserted from geometry" + an explicit note that
  `868MHz`/`2.4GHz` occur only as marked values; (ii) label normalised from
  `MARKED (record)` to `MARKED`; (iii) rows 5-7 implication cells now cite the
  labelled inference rows instead of reading "No inference"; (iv) §4's
  "confined to the implication column" corrected; (v) the unsupported
  "every capacitor is a power-rail decoupler" overclaim replaced with the
  structural statement actually proven by §1.1.
  Artifact: `~/reports/reviews/meshcore-t_a82deb2b-deepseek_deepseek-v4-flash-pass3.md`
- **Pass 4** — same lane, verdict-forcing prompt, on the revised text →
  **VERDICT: APPROVED, MAJOR: none**, 1 minor (the `AE1`/`AE2` designator
  collision between the board file and the generated netlist, not disambiguated).
  Applied on this final revision as §1.5.
  Artifact: `~/reports/reviews/meshcore-t_a82deb2b-deepseek_deepseek-v4-flash-pass4.md`
- **Verdict credited to the floor gate: APPROVED** (passes 3 and 4, both
  line-initial `VERDICT: APPROVED` on material revisions). Pass 1's REJECTED and
  the later APPROVEDs are **not netted out**: pass 1 was correct on the artifact
  as it then stood, and its findings are preserved above. An independent reviewer
  may prefer to verify the APPROVED against this final text.
