# Chamber-EXTERIOR to instrument - BOM line items

Card `meshcore:t_a4844b93` - "Specify chamber-exterior to instrument line items".
Profile `worker-base` - host `c03rad0r-DQ05proplus` - branch `worker-base/t_a4844b93`.

Deliverable: the BOM lines for the RF chain from the **chamber-exterior side of the bulkhead
feedthrough** to the **instrument port**. Machine twin: `exterior_leg_bom.csv` (same rows, same
column order, generated from the same in-memory list by `make_bom.py`).

---

## 0. Boundary, and the input this list is built from

**Starting boundary:** the exterior face of the bulkhead feedthrough, parent row `IF-7`. The
feedthrough connector itself and everything on its chamber-interior side belong to the sibling
DUT-to-interior card (`t_fe6e9c1b`) and are **not** on this list. **Ending boundary:** the
instrument port, parent row `IF-10`.

Every connector identification below is **reused verbatim** from the parent's normalized interface
table (`bench/interface-normalization/INTERFACE-TABLE.md` and `interface_table.csv`, branch
`worker-base/t_1bb81290`, HEAD `d6bbc980`). Nothing is re-derived from raw sources: the parent row id
is named on every line, and the sibling quotation the parent carried is quoted again where a line
needs it.

Rows consumed from the parent table: `IF-7` (bulkhead exterior face - UNKNOWN/UNSPECIFIED), `IF-9`
(the exterior cable assembly, frozen `C-RF-EXT-1`), `IF-10` (instrument port - UNVERIFIED, no RF
instrument exists). Boundary context only, not components of this segment: `IF-8` (the wall bore) and
`IF-11` (the non-RF serial crossing).

**Honesty state carried forward:** the parent table has ZERO `VERIFIED` rows - the DUT is not
attached to any host, no chamber exists on any record, and no RF instrument exists. Every line on
this segment therefore inherits at least one UNVERIFIED input, and each line says which one.

---

## 1. THE SEGMENT BOM (columns exactly as the card mandates, in order)


| Item description | QTY | Part number (real MPN preferred; otherwise 'MPN TBD' plus required interface spec: connector series, gender, impedance, frequency rating, max VSWR) | Disposition (ON-HAND / MUST-PROCURE / MUST-FABRICATE) | Lead-time estimate | Source/vendor | Cited source for the connector identification |
| --- | --- | --- | --- | --- | --- | --- |
| E1 - Chamber-EXTERIOR cable assembly - the exterior leg, bulkhead exterior face to the instrument port (frozen identifier C-RF-EXT-1). Gender transition: SMA-M plug (mates the bulkhead exterior SMA-F jack) to SMA-M plug (mates the instrument SMA-F jack) - male-to-male, so no gender-changing adapter exists inside the leg itself. Impedance 50 ohm. | 1 | MPN TBD - required spec: RG316 coax (OD 2.5 mm, solid PTFE dielectric), 0.50 m, SMA plug (male pin) at BOTH ends, standard polarity (NOT RP-SMA), straight, 50 ohm, 868 MHz measurement band, SMA class (DC-18 GHz class context), max VSWR 1.05:1 class at 868 MHz (standard-SMA class figure; no per-part value on any record), flex life adequate for a 25.0 mm minimum bend radius (the routing freeze's 10xOD rule). Representative class named on record: Amphenol ACX-1169-class RG316 patch (exact-length variant TBD) - representative only, not an on-hand part. | MUST-PROCURE - nothing on this segment exists on any record (no coax of any type is on this host or on any record) | 2-5 days (procurement estimate carried from the sibling BOM) | Digi-Key / Mouser (vendor class; live availability UNVERIFIED) | UNVERIFIED - see open risks. Identification reused from parent row IF-9 (bench/interface-normalization/INTERFACE-TABLE.md), which cites SUPPORTING bench/connector-adapter-bom/REPORT.md line B4 verbatim: "RG316 coax assembly, SMA-male to SMA-male, 0.50 m (bulkhead to reference TX, exterior) \| 1 \| MPN TBD - same spec as B1, 0.50 m" and bench/routing-freeze/REPORT.md verbatim: "C-RF-EXT-1 \| RG316 SMA-m/m, 0.50 m, exterior (bulkhead -> ref TX) \| MUST-PROCURE, MPN TBD". CONFLICT RESTATED INLINE: the bulkhead-side SMA-M plug presupposes an SMA-F jack on the feedthrough EXTERIOR face, which parent row IF-7 records as UNKNOWN - "no port to inspect" - because no chamber exists on any record; sibling (c) warns the two faces may differ in series ("interior and exterior may differ (e.g. N-exterior / SMA-interior adapter feedthrough) - only a physical walk resolves each side separately", bench/chamber-rf-feedthrough-list/FEEDTHROUGH-LIST.md FT-1) - that case is served by role (b) of E2. The far end likewise assumes a female SMA jack at the instrument: IF-10 records the reference TX jack as document-based and any future bench instrument as UNSPECIFIED (served by E2 role (a) or E3). |
| E2 - Adapter, 50 ohm, SMA-F jack to N-M plug (gender transition: SMA-F to N-M) - ONE physical part serving TWO conditional roles, merged here with a summed QTY per card step 6: role (a) INSTRUMENT side - takes the exterior cable's SMA-M plug (E1) into an instrument port that presents N-female; role (b) BULKHEAD-EXTERIOR side - takes an N-female exterior face into the same SMA-M cable plug (E1) when a located chamber's feedthrough proves N-type on the outside, as an alternative to buying a second N-type exterior assembly. The hardware is identical in both roles (one N plug, one SMA jack), which is why it is not two lines. Impedance 50 ohm. | 0-2 (0 today; 1 if role (a) applies, 1 if role (b) applies, 2 if both) | MPN TBD - required spec: SMA jack (female) to N plug (male), 50 ohm (a 75 ohm N variant is INADMISSIBLE - sibling hazard H1), DC-3 GHz, standard polarity, low-loss, PTFE dielectric, brass/gold. Max VSWR: no numeric value for an SMA/N adapter exists on any record, so the figure must be taken from the procured part's datasheet at order time; frequency rating 868 MHz measurement band (N-class DC-11 GHz class context, UNVERIFIED on host). | MUST-PROCURE - conditional (qty 0 today: no RF instrument exists, and no chamber exists so no exterior face exists to inspect; qty 1-2 only if role (a) or role (b) materialises) | 1-5 days once the condition is known (sibling BOM: 1-3 days for the instrument case, 2-5 days for the bulkhead class) | Digi-Key / Mouser (vendor class) | UNVERIFIED - see open risks. Role (a) from parent row IF-10 (UNVERIFIED), citing bench/instrument-rf-connectors/REPORT.md caveat 5 verbatim: "Most sub-GHz signal generators and spectrum analyzers present N-type or 3.5 mm connectors (not SMA), which would require SMA-to-N or SMA-to-3.5mm adapters", and bench/connector-adapter-bom/REPORT.md line B11 verbatim: "Conditional instrument adapter: SMA-F jack to N-M plug (for a signal generator / analyzer with N-female port), or SMA-F to BNC-M if BNC \| 0-1 \| MPN TBD - required spec: 50 ohm, DC-3 GHz, low-VSWR adapter matching whatever instrument is eventually procured \| CONDITIONAL (qty 0 today: no RF instrument exists - input 2)". Role (b) from parent row IF-7 (UNVERIFIED/UNSPECIFIED), citing SIBLING (c) bench/chamber-rf-feedthroughs/REPORT.md record F1 verbatim: "Exterior-side connector family \| UNKNOWN \| same - note interior/exterior may differ (e.g. N-exterior/SMA-interior adapter feedthrough); only a physical walk resolves each side separately", and bench/chamber-rf-feedthrough-list/FEEDTHROUGH-LIST.md FT-1 verbatim: "UNKNOWN - no port to inspect; interior and exterior may differ (e.g. N-exterior / SMA-interior adapter feedthrough) - only a physical walk resolves each side separately". CONFLICT RESTATED INLINE: neither role is selected. IF-10's de-facto instrument is the reference TX node whose port is SMA - "RF connector \| SMA edge-launch, standard polarity, female jack, 50 ohm (same carrier board family as the DUT) \| UNVERIFIED for the specific board assigned as reference TX" (bench/instrument-rf-connectors/REPORT.md) - in which case role (a) stays at qty 0 and no adapter is needed at all; the standing BOM says buying it now "would be a guess". IF-7's PLANNED class is an SMA jack-jack feedthrough - "The planned/procurement feedthrough class is UNFILTERED by construction: an SMA panel-mount jack-jack bulkhead (Amphenol 132134-class per 55585471) is a direct gold-plated contact pair with PTFE dielectric - no filter elements" (bench/chamber-rf-feedthroughs/REPORT.md STEP 5) - in which case role (b) stays at qty 0. A FILTERED OEM port would be unusable for the RF path at any gender (same report, LOUD FLAG). |
| E3 - Adapter, 50 ohm, SMA-F jack to BNC-M plug (gender transition: SMA-F to BNC-M) - INSTRUMENT side only: takes the exterior cable's SMA-M plug (E1) into an instrument port that presents BNC-female (the counter/instrument case). A distinct physical part from E2 (different second-end series), so it is its own line. Impedance 50 ohm; the BNC end is a 2-lug bayonet, so no torque value applies to it. | 0-1 (0 today) | MPN TBD - required spec: SMA jack (female) to BNC plug (male), 50 ohm - a 75 ohm video/CCTV BNC is INADMISSIBLE (sibling hazard H1: the shell and bayonet are identical between 50 and 75 ohm and they mate mechanically), DC-3 GHz, low-loss, PTFE (or equivalent low-loss) dielectric on the 50 ohm part. Max VSWR: no numeric value for an SMA/BNC adapter exists on any record - take it from the procured part's datasheet at order time; frequency rating 868 MHz measurement band. | MUST-PROCURE - conditional (qty 0 today: no RF instrument exists; qty 1 only if a bench instrument with a BNC-female port is procured) | 1-3 days once the instrument is named (carried from the sibling BOM) | Digi-Key / Mouser (vendor class) | UNVERIFIED - see open risks. Identification from parent row IF-10 (UNSPECIFIED for any future bench instrument), citing bench/connector-adapter-bom/REPORT.md line B11 verbatim: "... or SMA-F to BNC-M if BNC". CONFLICT RESTATED INLINE: the instrument port does not exist on any record - "NO RF INSTRUMENT EXISTS - the measurement chain has no instrument-side RF connector to identify" (bench/instrument-rf-connectors/REPORT.md) - so the BNC case is hypothetical; and the sibling hazard H1 applies specifically to a BNC purchase, verbatim: "75 ohm vs 50 ohm: video/CCTV coax (RG-59/RG-6, 75 ohm, F/BNC) is commonly stocked in labs; the LR2021 system and every line in this BOM is 50 ohm". A 75 ohm BNC adapter would be an impedance discontinuity, not a transition. |
| E4 - Inline pad / attenuator on the exterior leg - NIL BY DESIGN: no attenuator, fixed pad, LNA, bias tee or other inline RF element is required anywhere on this segment. Stated as a line so its absence cannot be read as an omission - card step 1 requires any inline pad that the instrument-port identification or feedthrough assessment makes necessary, and the sourced answer is that neither does. Impedance N/A (no part). | 0 | N/A - no part, therefore no series, gender transition, impedance or frequency rating applies. The segment is a passive 50 ohm cable plus (conditionally) one gender transition; no record specifies an attenuator, pad, amplifier, bias tee or filter for it. | NIL (qty 0) - not required. No ON-HAND / MUST-PROCURE / MUST-FABRICATE disposition applies because there is nothing to obtain; the honest disposition is NIL with its reason. | N/A - nothing to procure or fabricate | N/A - nothing to source | NIL - reason cited. bench/instrument-rf-connectors/REPORT.md STEP 1 verbatim: "\| Attenuator \| NO \| N/A \| N/A \| Not on any record or BOM; rf-feedthrough-bom 55585471 does not list one \|" and "\| Amplifier (LNA) \| NO \| N/A \| N/A \| cable-feedthrough-failure-modes 04db4fae:460-461 (\"no LNA, attenuator, or RF instrument anywhere\") \|". Feedthrough assessment: no attenuator is required by the conducted path - the only attenuation issue on record is a FILTERED OEM port, which is a usability gate on the feedthrough itself (bench/chamber-rf-feedthroughs/REPORT.md STEP 5 LOUD FLAG), not a part to add here and never something a pad can correct. Insertion loss of the whole conducted chain is ~0.3-0.5 dB at 868 MHz against a 165 dB link budget, so no pad is needed to protect any port (bench/rf-feedthrough-bom/REPORT.md STEP 5). |
| E5 - Adapter, INSTRUMENT side, 3.5 mm / 2.92 mm (K) precision case - NIL BY DESIGN: no adapter is required. A 3.5 mm (or 2.92 mm K) male connector mates an SMA female jack directly. Stated because the instrument-port identification names 3.5 mm as one of the two likely future instrument ports; the sourced answer is that this case adds no part. Impedance N/A (no part; the mating itself is 50 ohm). | 0 | N/A - no part. The gender transition SMA-F to 3.5 mm-M is supplied by the instrument's own connector: same 1/4-36 UNS thread group, same 7.94 mm hex, 50 ohm, intentional mating. Nothing is bought. | NIL (qty 0) - not required. No disposition applies because no part is obtained; a precision adapter would be bought only to add cost (sibling H3). | N/A - nothing to procure or fabricate | N/A - nothing to source | NIL - reason cited. bench/connector-family-reference/REFERENCE.md note 2 verbatim: "SMA vs 3.5 mm vs 2.92 mm (K) - same thread group, same hex, and they intentionally mate. Distinguish by markings (\"3.5mm\"/\"K\"), price/provenance, and the dielectric look ... At 868 MHz they are interchangeable electrically"; bench/connector-adapter-bom/REPORT.md H3 verbatim: "Precision vs standard SMA: precision SMA / 3.5 mm connectors are dimensionally compatible but cost 5-10x; at 868 MHz (and even 2.4 GHz) standard SMA is fully adequate (VSWR spec 1.05:1 class at these frequencies)." The instrument port itself remains UNSPECIFIED (parent row IF-10) - the NIL holds only once a physical check confirms the instrument's mating connector really is 3.5 mm-M/2.92 mm-M. |

Rows `E1`-`E3` are the physical parts of this segment; `E4`-`E5` are **NIL declarations** (cases the
card asks about that turn out to require no part). NIL rows carry `QTY 0` and a disposition that says
*why* nothing is obtained, rather than a mislabelled ON-HAND/MUST-PROCURE - stating NIL is part of
the deliverable, not an omission.

**One part, two roles, one line (card step 6).** `E2` is a single piece of hardware - an SMA jack on
one end and an N plug on the other. It appears once, with a summed conditional quantity, because
"the N adapter for an N-female instrument port" and "the N adapter for an N-type bulkhead exterior
face" are physically the same part. Listing them as two lines would double-count a single item, which
the card forbids.

---

## 2. CHAIN WALK - every gender transition on this segment, stated explicitly

```
[IF-7] bulkhead feedthrough, EXTERIOR face
       planned class: SMA-F jack  (UNKNOWN on any record - no chamber exists)
   |
   |  role (b) of E2, only if the face proves N-female:
   |      N-female  <-[ E2: N-M plug | SMA-F jack ]<-  SMA-M plug of E1
   |
   |  base case: direct mate, SMA-F jack <- SMA-M plug of E1
   v
[E1] C-RF-EXT-1  RG316 assembly, 0.50 m
       SMA-M plug === SMA-M plug, standard polarity, 50 ohm
       (male-to-male: NO gender adapter inside the leg)
   |
   |  (a) direct mate, no adapter - instrument presents SMA-F jack
   |      => the de-facto case today: the reference TX node (IF-10)
   |  (b) E2   SMA-F jack  <- N-M plug      (instrument presents N-female)
   |  (c) E3   SMA-F jack  <- BNC-M plug    (instrument presents BNC-female)
   |  (d) E5   NIL - a 3.5 mm-M / 2.92 mm-M instrument port mates the
   |      SMA-F jack directly (same thread group) - no adapter bought
   |  (e) E4   NIL - no inline pad/attenuator anywhere on the segment
   v
[IF-10] instrument port
       today: reference TX MeshCore node, SMA-F jack, 50 ohm (UNVERIFIED)
       future: bench RF instrument - series UNSPECIFIED (N-female most likely)
```

No other gender transition exists on this segment. `E1` is male-to-male at both ends and the planned
feedthrough is jack-jack, so the base case needs no gender adapter at all - the same statement the
sibling BOM makes for the whole chain, verbatim: "No gender-changing adapter exists in the basic
chain (M-M cable assemblies, F-F bulkhead). All connectors standard-polarity SMA, 50 ohm."
(`bench/connector-adapter-bom/REPORT.md` STEP 3).

---

## 3. UNVERIFIED inputs - restated inline, not resolved

Rule 5 of the card is honoured literally: every line whose connector identification descends from a
row flagged `UNVERIFIED` or `UNSPECIFIED` in the parent table is kept, annotated
`UNVERIFIED - see open risks`, and restates the conflict inline. Conflict inventory for this segment,
both candidates retained:

| # | Parent row | What is unresolved | Both candidates (verbatim) |
|---|---|---|---|
| U1 | `IF-7` | **The feedthrough's exterior-face connector family.** No chamber exists on any record, so the face cannot be inspected. Drives `E1`'s bulkhead-end gender and role (b) of `E2`. | Planned class: SMA-F jack, panel-mount jack-jack, unfiltered - "The planned/procurement feedthrough class is UNFILTERED by construction: an SMA panel-mount jack-jack bulkhead (Amphenol 132134-class per 55585471) is a direct gold-plated contact pair with PTFE dielectric - no filter elements" (`bench/chamber-rf-feedthroughs/REPORT.md` STEP 5). Contradicting possibility: "Exterior-side connector family | UNKNOWN | same - note interior/exterior may differ (e.g. N-exterior/SMA-interior adapter feedthrough); only a physical walk resolves each side separately" (same report, record F1). |
| U2 | `IF-7` | **The representative bulkhead part number.** No bulkhead part appears on this list (the feedthrough is the boundary, not a line) - recorded because it is the source of the exterior-face gender assumption that `E1` depends on. | "Amphenol 132134-class" (standing BOM / sibling (b)) vs the later sibling correction: "One correction is carried rather than repeated: the standing BOM's 'Amphenol 132134' is a PCB jack, not a panel feedthrough (sibling vendor sheet section 1), so it is not used here as the bulkhead part" (card `t_a53c6efe`, status done). Series/gender/impedance are NOT in conflict - only the representative MPN. |
| U3 | `IF-10` | **The instrument port does not exist.** The far end is the reference TX node (SMA-F jack), document-based; any future bench instrument is UNSPECIFIED. Drives `E2` role (a), `E3` and `E5`. | "NO RF INSTRUMENT EXISTS - the measurement chain has no instrument-side RF connector to identify" and "RF connector | SMA edge-launch, standard polarity, female jack, 50 ohm (same carrier board family as the DUT) | UNVERIFIED for the specific board assigned as reference TX" (`bench/instrument-rf-connectors/REPORT.md`); future case: "Most sub-GHz signal generators and spectrum analyzers present N-type or 3.5 mm connectors (not SMA), which would require SMA-to-N or SMA-to-3.5mm adapters" (same report, caveat 5). |
| U4 | `IF-9` | **The exterior assembly itself does not exist** - MPN TBD by design, and both of its ends assume jacks that are themselves unverified. | "MPN TBD - same spec as B1, 0.50 m" (`bench/connector-adapter-bom/REPORT.md` B4) vs the parent's own note that the assembly "assumes a female SMA jack at the instrument - see IF-10, where the instrument itself is UNSPECIFIED" and presupposes the exterior face of `IF-7`. |

Open risks, each with the sibling source it came from and its unblock path - none resolved here, none
dropped:

| Risk | Risk on this segment | Source it came from | What unblocks it |
|---|---|---|---|
| `R-IF7` | The exterior-face series/gender is UNKNOWN, so `E1`'s bulkhead-end gender and role (b) of `E2` are both undecided. | parent `IF-7`; sibling (c) `bench/chamber-rf-feedthroughs/REPORT.md` F1 + `bench/chamber-rf-feedthrough-list/FEEDTHROUGH-LIST.md` FT-1 | Locate the chamber, walk the wall, identify both faces separately - the parent's own remedy: "resolve with the identification kit on first sight". |
| `R-FILTER` | A filtered OEM port would be unusable for the RF path regardless of gender, and no adapter can correct it. | sibling (c) STEP 5 LOUD FLAG, carried on parent `IF-6`/`IF-7` | Physical check on the located unit: bulky body / feedthrough-capacitor construction / "filtered" marking. |
| `R-IF10` | The instrument port is UNSPECIFIED, so which transition (`E2` role (a) / `E3` / `E5`) applies is unselected. | parent `IF-10`; sibling (b) caveat 5 | Name or procure an instrument, then select the transition. Buying one now "would be a guess". |
| `R-REFTX` | Even the de-facto instrument (reference TX node) is document-based: board not attached, PCB revision not on record. | parent `IF-10`; sibling (b) STEP 2b | Attach the reference TX, read its port, photograph the jack. |
| `R-PART` | Every MPN here is TBD or representative, and no inventory system of record exists, so nothing on this segment is confirmed on hand. | sibling R6 `bench/rf-feedthrough-bom/REPORT.md`; parent `IF-9` | Confirm at order time; receiving inspection. |
| `R-RP` | Reverse-polarity SMA lookalikes are the single most likely wrong-part event on an 868 MHz purchase. | sibling hazard H2 (`bench/connector-adapter-bom/REPORT.md`) | Receiving inspection: the plug must present a center PIN. |
| `R-75` | A 75 ohm substitution (video BNC / RG-59 class) is a mismatch, not a transition - acute on `E3`. | sibling hazard H1 | Verify "50 ohm" / "RG316" literally on the order and on the part. |

---

## 4. DELIBERATELY NOT ON THIS LIST (stated so absence is not read as a gap)

| Excluded item | Why | Owner / where it lives |
|---|---|---|
| The bulkhead feedthrough connector itself (both faces) | It is this card's starting boundary, not a component of the exterior leg. | sibling card `t_fe6e9c1b` (DUT-to-interior + feedthrough) |
| Chamber-interior cable assembly `C-RF-INT-1` and everything inside the chamber | Card step 4: interior items belong to the DUT-to-interior task. | sibling card `t_fe6e9c1b` |
| The chamber wall bore / drilling / sealing hardware | Mechanical penetration, not a connector on this segment; custodian-gated. | sealing section card (`t_a53c6efe`, SEAL-*) |
| Dust caps for the exterior face in the unmated/storage state | Protective accessory, not a signal-path component; owned by a dedicated section card. | terminations/caps section card (`t_436f6657`, TERM-*) |
| Torque wrench, spanners, connector savers, anti-rotation fixtures | Handling tooling for the whole chain, not a component of the exterior leg. | tooling section card (`t_378c5705`, TOOL-*/SAV-*) |
| Tape anchors / loom / cable ID labels for the exterior leg | Consumables governed by the frozen routing spec (`bench/routing-freeze/REPORT.md` §2.2: anchor at T3 plus one per 100 mm of parallel run, polyimide or glass-cloth class; IDs labelled at first touch both ends), not connector-identification BOM lines - no series/gender/impedance applies. | routing freeze `bench/routing-freeze/REPORT.md`; a consolidator wanting consumables should take them from that spec, not from a connector line. |
| The reference TX's own serial cable `C-SER-2` and the operator-workstation end | Outside the DUT-to-instrument chain by the parent's own scope note ("exterior only - never crosses"). | parent `IF-11` note; `bench/routing-freeze/REPORT.md` |
| The USB-C serial crossing `C-SER-1` | Non-RF control-path crossing, not part of this RF segment. | parent `IF-11`; sibling card `t_fe6e9c1b` / sealing section |

---

## 5. ACCEPTANCE SELF-CHECK (against the card's own sentence)

| Acceptance requirement | Status | Evidence |
|---|---|---|
| Every component on this segment appears exactly once with a quantity and a disposition | PASS | 5 rows with unique ids `E1`-`E5`; each carries QTY and a disposition; the two zero-quantity rows are declared NIL with a reason instead of being dropped; the one part that serves two roles is a single line with a summed conditional QTY (`E2`). Signal-carrying hardware is `E1` (firm) plus the conditional transitions `E2`/`E3`. |
| Every line names series, gender transition, and impedance | PASS | Each `Part number` cell states the connector series, the gender transition, and "50 ohm" - or `N/A` with its reason on the two NIL rows. Checked mechanically by `make_bom.py`. |
| Every connector identification traces to a cited sibling source or is flagged UNVERIFIED | PASS | 5/5 rows carry a citation naming a committed `bench/` path or a parent row id, and 5/5 carry an `UNVERIFIED - see open risks` annotation or a `NIL - reason cited` declaration. Zero rows claim a positive verified status. |
| No component inside the chamber or the bulkhead connector itself is duplicated onto this list | PASS | Section 4 names the feedthrough, `C-RF-INT-1`, the bore/sealing, tooling, caps and the serial crossing as excluded with their owners; no row describes any of them. |
| No physical item listed twice; duplicate roles combined with a summed QTY (step 6) | PASS | One row per distinct part; the SMA-jack/N-plug adapter's two roles are merged on `E2` with QTY `0-2`. Checked mechanically: every distinct MPN-TBD interface spec maps to exactly one row. |

Mechanical check run by `make_bom.py` on every invocation: the 7 header cells match the card's column
list in order; every data row has exactly 7 non-empty cells; every row states an impedance value or
an explicit `N/A`; every row states a gender token or an explicit `N/A`; every row carries a citation;
every row is annotated `UNVERIFIED` or `NIL`; no row claims a positive verified status; part specs
are unique after the declared merge; no row is the feedthrough or the interior leg.

---

## 6. NOTHING FABRICATED

No connector series, gender, impedance, frequency rating, VSWR value, MPN, lead time or price on this
list is invented. Every identification is reused from the parent's normalized interface table, which
itself quotes committed sibling reports; every MPN is `MPN TBD` with the interface spec the part must
satisfy, except the one representative class the record names (Amphenol ACX-1169-class, explicitly
labelled representative). No conflict is resolved, no candidate is dropped, no positive verified
status is granted, and no measurement, photograph, physical inspection or outbound fetch is claimed:
no cable, no chamber, no instrument and no RF connector of this segment exists on any record or on
this host. `0-1` and `0-2` mean exactly that - zero today, one/two only if a stated condition
materialises.

Reproduce: `python3 make_bom.py` rewrites `EXTERIOR-LEG-BOM.md` and `exterior_leg_bom.csv`
byte-identically (stdlib only; no clock, no randomness, no network), then runs the self-check.
