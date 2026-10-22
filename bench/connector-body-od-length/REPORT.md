# Connector body OD and body length, matched to cable ID — MEASUREMENT-READY / NO-DATA

Card: meshcore `t_87830aa4` — "Measure connector body OD and length, matched to
cable ID." (child of the decomposed root `t_7a16e421`).
Date: 2026-10-17 (08:4x–09:1x local, UTC+2). Host: `c03rad0r-DQ05proplus`.
Worker: `default` (run 2128). Board: meshcore, repo `~/repos/meshcore`,
branch `main`. Workspace: `/home/c03rad0r/worktrees/t_e1408991` (scratch).

tags: no-code, docs, read-only
tier: docs (declared) — this card ships no source-code change; the deliverable
is a written measurement-readiness record plus one stdlib check script and its
verbatim output. The physical measurement the card asks for cannot be performed
on this host (§2) and **no number is invented to fill the gap**.

---

## VERDICT SUMMARY

**Zero of the required numbers exist, because zero of the subject connectors
exist.** Every connector on the coax run is a *procurement plan*, not a physical
part: the two RG316 assemblies and the SMA bulkhead feedthrough are all
`MUST-PROCURE, MPN TBD` (`bench/connector-adapter-bom/REPORT.md` B1/B2/B4), the
chamber that would host the bulkhead does not exist on any record (FT-1..FT-5
all `NON-EXISTENT`, `bench/chamber-rf-feedthrough-list/`), and **no caliper
exists on this host or on any record** (fresh census §2; `bench/routing-freeze`
§1/§3 — the caliper is `MUST-PROCURE`).

So the honest answer to every "body OD" and "body length" cell is `UNKNOWN`,
with the specific reason and the specific tool/access that would resolve it.
That is not an incomplete card: the card's own acceptance clause anticipates
exactly this case — *"Unmeasurable features are flagged UNKNOWN with the
tool/access that would resolve them."*

What this card DOES deliver, all sourced and reproducible:

1. **The complete connector census of the coax run — 7 bodies, each appearing
   exactly once, each tied to a cable ID** (§4), plus the one conditional body
   (BOM B6) and an explicit out-of-run list so nothing is silently missing or
   double-counted.
2. **The instrument declaration this card must reuse** (§3): the frozen caliper
   spec and least-count, and the uncertainty cell every future reading inherits.
3. **A per-connector answer table** (§5): cable ID, designator-if-marked, body
   OD, body length, uncertainty, and what is measurable vs obscured — with the
   forward-looking jaw-placement notes (threads, jam nut, O-rings, ID flags,
   PCB side) that a future caliper pass must not get wrong.
4. **The exact resolution for each UNKNOWN** (§6): which tool or access settles
   it, including the ones a caliper *cannot* settle (thread-flank inspection for
   standard-vs-RP, x-ray/CT for the panel-side barrel, destructive boot removal).
5. **A fresh physical census taken this session** (§2) and a **checkable
   connector-run arithmetic audit** (§7) — 6 of 7 checks PASS, the 7th being the
   honest measurement gap itself.

A downstream consumer must read this as a **NO-DATA census + verified-blocker
record**, never as a completed measurement. Nothing here supersedes a measured
value.

---

## 1. What the card asked for, and the acceptance test applied

| # | Card requirement | Satisfiable on this host? |
|---|---|---|
| 1 | For each connector, measure **body OD** with calipers | **No** — no connector exists to measure; no caliper exists to measure with |
| 2 | For each connector, measure **body length** with calipers | **No** — same |
| 3 | Measure the metal/connector body itself, **not** the jacket or a heat-shrink boot | **No** — nothing physical; recorded instead as the jaw-placement rule for the future pass (§5) |
| 4 | **Note if a boot or sealant prevents a clean jaw placement** | **Partially** — no part to inspect, but the plan's own obstructions are enumerable from the frozen spec (§5, "measured vs obscured") |
| 5 | **Match each connector EXPLICITLY to the cable it terminates** | **Yes** — deliverable §4; the chain is frozen (`bench/connector-adapter-bom` STEP 3, `bench/routing-freeze` §5) |
| 6 | **Uncertainty = ± caliper resolution, with units** | **Yes as spec, n/a as reading** — §3 |
| 7 | Every connector in the run appears **exactly once** | **Yes** — §4 + the §7 audit (7 bodies, 8 interface-halves, 4 joints) |
| 8 | Every value is a number with units sourced to the caliper model + resolution | **No numbers exist**; the source of record is the caliper SPEC, and its make/model is itself UNKNOWN (no tool) |
| 9 | Unmeasurable features flagged UNKNOWN with the resolving tool/access | **Yes** — §6 |

---

## 2. Fresh physical census (this session, 2026-10-17)

Re-run now so the NO-DATA verdict is anchored to evidence taken this session,
not inherited from the 2026-09-15 sibling reports. Full verbatim output:
`output_t_87830aa4.txt` (§7 reproducibility). Summary:

| Check | Result | Consequence for this card |
|---|---|---|
| `lsusb` | 4 root hubs, Realtek BT radio `0bda:b850`, Lexar ES4 `21c4:0004`, Zoran audio/HID `0573:1573` | zero instrument-class, zero coax-connected device |
| `/dev/serial/by-id/` | **absent** (directory does not exist) | DUT and reference TX are **not attached** to this host |
| `/dev/ttyACM*`, `/dev/ttyUSB*` | **absent** | no board on the bus at all |
| `/dev/usbtmc*`, `/dev/gpib*` | **absent** | no bus-instrument measurement path |
| `/dev/video*`, `/dev/media*`, `/sys/class/video4linux` | **absent** | no camera → the "photograph the connector / read its marking" alternative is unavailable |
| Caliper / micrometer / vernier / tape-measure assets (bounded find over `$HOME` L1, `~/reports`, `~/repos`, `~/.hermes`, `~/Documents`, `~/Downloads`) | **ZERO HITS** | **no measuring instrument on this host** |
| Physical RF coax / connector assets in the repo tree (bounded find, `*rg316*`, `*rg-316*`, `*sma*`, `*.s2p`, files only) | **ZERO HITS** (the only name matches are *report directories* named for the subject, e.g. `bench/sma-ice-bridging-failure-modes/` — not assets) | no cable, no connector, no Touchstone data |
| Connector / cable photographs in `~/reports` or `~/.hermes/kanban` | **ZERO HITS** | no photo exists to read a marking or scale a body from |
| Procurement record naming a representative SMA MPN (`ACX-1169`, `132134`) | one **citation** in `bench/chamber-rf-feedthrough-list/feedthrough_list.csv` | the class is *cited in a report*; no order, no PO, no part on hand |

**Census verdict:** this host is a headless server with no connector, no cable,
no caliper, no camera and no attached DUT. Every value in §5 is therefore not
merely unmeasured — it is **not measurable here**, and the honest source cell is
`UNKNOWN`, never an estimate.

Cross-checks (independent, committed, all concur): `bench/routing-measurements`
(t_93afb6e2, 2026-10-17), `bench/coax-cable-inventory` (t_9cfb7abd, 2026-10-17),
`bench/rf-connector-geometry`, `bench/coax-bundle-dimensions`,
`bench/chamber-rf-feedthrough-list`, `bench/connector-adapter-bom`,
`bench/routing-freeze` — plus the board's own result register: **0 of the 917
meshcore tasks carry a caliper reading of any connector body** (the only two
results matching "caliper"/"body OD" are reference-sheet and protocol cards).

---

## 3. Instrument declaration this card must reuse (SETUP dependency)

The card requires the **same caliper model/resolution declared in setup**. The
setup lane is sibling card `t_1efbbeea` ("Declare instruments and tape coax
bundle in final install routing"), which at write time was **in flight with no
result** (state re-read this session: `ready`, run 2127 ended without output, no
artifact file). The declaration of record is therefore the frozen spec the
setup lane is chartered to restate:

| Instrument | Declared spec | Resolution (least count) | Status | Source |
|---|---|---|---|---|
| **Digital caliper** | stainless digital-vernier class; jaw + step + depth faces; 0–150 mm range (covers every planned connector dimension — the largest is the bulkhead jam-nut/hex ≈ 10 mm class) | **±0.01 mm** (digital least-count; 0.001 in imperial) | **MUST-PROCURE — no caliper on host or record** | `bench/routing-freeze/REPORT.md` §3 (card `t_e5d5eaae`), matching fleet card `t_f5f3fe8a` PREP verbatim: "digital caliper (0.01 mm / 0.001 in)" |
| Tape measure (not used by this card) | steel blade, mm-graduated, ≥1 m | ±1 mm | MUST-PROCURE | same §3 |

**Caliper make/model/serial: UNKNOWN.** No tool exists, so there is no make,
model or serial to record — the numbers above are a *required spec*, not a
reading of a tool in hand. When the caliper is procured, its make/model/serial
replaces the spec row and every reading below becomes a measured value.

**Uncertainty rule for this card (as required):** uncertainty = ± caliper
resolution = **±0.01 mm**, and it is *only* meaningful attached to a reading.
Because no reading exists, every uncertainty cell in §5 reads
`n/a — no reading taken; floor would be ±0.01 mm`. Two further rules from the
frozen setup apply to the future pass: (a) zero-check first — zero on closed
jaws, reject a gauge whose zero is off by more than 0.05 mm; (b) a downstream
reading may cite a different tool only if that tool's resolution is ≤ 0.01 mm,
otherwise it inherits the worse floor and must say so.

---

## 4. THE RUN — connector census (acceptance item: every connector exactly once)

The "coax run" is the frozen **variant-B conducted path**
(`bench/connector-adapter-bom/REPORT.md` STEP 3; `bench/routing-freeze` §2.1):

```
DUT carrier J1 [SMA-F edge-launch jack]                    <- inside chamber
  ->(mates) C-RF-INT-1  SMA-M plug === SMA-M plug, 0.15 m  [interior]
  ->(mates) SMA bulkhead feedthrough [SMA-F jack | WALL | SMA-F jack]
  ->(mates) C-RF-EXT-1  SMA-M plug === SMA-M plug, 0.50 m  [exterior]
  ->(mates) REF-TX J1 [SMA-F edge-launch jack]             <- outside chamber
```

**Seven connector bodies, each listed exactly once:**

| # | Connector (body) | Cable ID it terminates | Kind |
|---|---|---|---|
| CN-1 | DUT carrier J1 "SMA-868", edge-launch female jack | **C-RF-INT-1** | board jack |
| CN-2 | C-RF-INT-1 plug, DUT end (male pin, straight) | **C-RF-INT-1** | cable plug |
| CN-3 | C-RF-INT-1 plug, bulkhead end (male pin, straight) | **C-RF-INT-1** | cable plug |
| CN-4 | SMA bulkhead feedthrough, panel-mount jack-jack, jam nut | **C-RF-INT-1** (interior interface) **+ C-RF-EXT-1** (exterior interface) | bulkhead — **one body, two coaxial interfaces** |
| CN-5 | C-RF-EXT-1 plug, bulkhead end (male pin, straight) | **C-RF-EXT-1** | cable plug |
| CN-6 | C-RF-EXT-1 plug, ref-TX end (male pin, straight) | **C-RF-EXT-1** | cable plug |
| CN-7 | REF-TX J1 edge-launch female jack | **C-RF-EXT-1** | board jack |

**Why CN-4 is one row and not two.** The bulkhead is a single metal body with a
single OD and a single length; its two coaxial interfaces (cold side, warm side)
are not two connectors. Counting it twice would inflate the run to 8 and break
the identity below. The acceptance rule "every connector appears exactly once"
is therefore satisfied by one row carrying *both* cable IDs.

**Identity audit (checkable, §7):** 6 single-interface bodies + 1 two-interface
body = **8 interface-halves = 4 mating joints** — `J1|CN-2`, `CN-3|CN-4`,
`CN-4|CN-5`, `CN-6|CN-7`. The chain closes with no orphan connector and no free
interface, and each cable terminates exactly two cable-end plugs
(C-RF-INT-1 → CN-2, CN-3; C-RF-EXT-1 → CN-5, CN-6).

**Conditional body — in the run only if BOM B6 is used:**

| # | Connector (body) | Cable ID | Note |
|---|---|---|---|
| CN-8 | Connector saver (BOM B6), SMA male-to-female bullet adapter at DUT J1 | C-RF-INT-1 | **CONDITIONAL**: `bench/connector-adapter-bom` B6 is "MUST-PROCURE (RECOMMENDED-strong)" to spare the soldered edge-launch; if fitted it inserts one more body (2 interfaces) between CN-1 and CN-2. Decision open → it must be measured too, or explicitly waived. Bodies in run = **8 if B6 is used**. |

**Explicitly OUT of the run** (so no connector is silently missing or doubled):
B7 SMA 50 Ω termination load on DUT J2 (the 2.4 GHz port is not on the conducted
path); B8 SMA dust caps ×4 (protective caps, not connectors — they cover an
interface only while UNMATED, and must be removed before any jaw placement);
C-SER-1 / C-SER-2 USB-C cable ends (not coax connectors); the ESP32-C3 SuperMini
U.FL/I-PEX receptacle (WiFi/BLE, not the LR2021 868 MHz measurement path);
FT-1..FT-5 chamber feedthroughs (all `NON-EXISTENT` — no chamber, no bulkhead).

---

## 5. Per-connector answer table (the card's required row format)

Uncertainty column: `n/a — no reading; floor would be ±0.01 mm (caliper least
count, `bench/routing-freeze` §3, REQUIRED SPEC)` for **every** row. It is
stated once here and applies to all seven bodies (and CN-8).

| # | Cable ID it terminates | Type / designator if marked | Body OD (mm) | Body length (mm) | Measured vs obscured — jaw-placement note |
|---|---|---|---|---|---|
| **CN-1** | C-RF-INT-1 | SMA edge-launch female jack, ref **J1 "SMA-868"** on the SkyMapper carrier (`hub_board_f33.kicad_pcb`, footprint `custom:SMA_Edge_Mount`); **marking UNKNOWN** — no part exists to read, and the LR2021 module itself carries **no connector** (soldered wire dipole on a castellated pad) | **UNKNOWN** | **UNKNOWN** | Measure the threaded boss + hex above the board face (mating plane → board face). The **solder side / board-side body is obscured by the PCB** — as-installed body length is only measurable to the board face. Nothing covers the front face when unmated (remove the B8 dust cap first). Resolve: board in hand (fleet resource `c3-a`) or the carrier's footprint/3D data. |
| **CN-2** | C-RF-INT-1 | SMA plug, male pin, straight, standard polarity; **marking UNKNOWN** (procurement class Amphenol ACX-1169-class, MPN TBD) | **UNKNOWN** | **UNKNOWN** | Body = coupling nut + knurled barrel. **Specify the surface**: OD *over the coupling-nut cylinder/knurl*, NOT across-flats of the hex (a caliper on the hex measures a different quantity, AF ≈ 7.94 mm REFERENCE — not a body OD). Cable-entry shoulder may be covered by a moulded strain-relief boot and/or the plan's **heat-shrink/kapton ID flag** (`routing-freeze` §5 rule 2 puts a flag at BOTH cable ends) — the flag must not be laid over the body. Measure **UNMATED**, before mating. |
| **CN-3** | C-RF-INT-1 | as CN-2 (same assembly, other end) | **UNKNOWN** | **UNKNOWN** | as CN-2; additionally, once installed this end sits at the bulkhead with "no tape within 15 mm of the jam nut" (`routing-freeze` §2.2 rule 4) — tape must not cover the body. |
| **CN-4** | **C-RF-INT-1** (interior interface) **+ C-RF-EXT-1** (exterior interface) | SMA bulkhead feedthrough, panel-mount jack-jack, jam nut, standard polarity; representative class Amphenol 132134-class, MPN TBD; **marking UNKNOWN** | **UNKNOWN** | **UNKNOWN** | Body = threaded barrel + hex + jam nut + (silicone) O-rings. **As installed, the barrel inside the panel bore and the far-side thread are obscured by the panel and the jam nut** — a caliper can reach only the exposed interior/exterior barrel stubs and the hex, so as-installed *body length* is **not measurable without removing the jam nut** (which breaks the O-ring seal; treat as semi-destructive). Barrel OD over threads ≠ OD over the unthreaded shoulder ≠ hex AF — state which surface. No sealant is specced (the project seals with SMA O-rings, `balloon tracker/hardware/enclosure/README_big.md:20-26`), but if a sealant is ever applied at the wall it obscures the barrel. |
| **CN-5** | C-RF-EXT-1 | SMA plug, male pin, straight, standard polarity; **marking UNKNOWN** | **UNKNOWN** | **UNKNOWN** | as CN-2/CN-3 (obverse side of the wall). |
| **CN-6** | C-RF-EXT-1 | as CN-5 (same assembly, other end) | **UNKNOWN** | **UNKNOWN** | as CN-2/CN-3. |
| **CN-7** | C-RF-EXT-1 | SMA edge-launch female jack, REF-TX **J1** (`custom:SMA_Edge_Mount` on the hub-board family PCB); **marking UNKNOWN** | **UNKNOWN** | **UNKNOWN** | as CN-1 (board-mounted jack; solder side obscured by its PCB). The specific reference-TX board is itself UNVERIFIED. |
| CN-8 *(conditional)* | C-RF-INT-1 | SMA male-to-female bullet adapter (BOM B6), straight; **marking UNKNOWN** | **UNKNOWN** | **UNKNOWN** | Two coaxial interfaces; measure only if B6 is fitted. Body OD of a bullet adapter is *not* the same part as a plug body — do not copy CN-2's numbers onto it. |

**Every OD and every length above is `UNKNOWN` because the part does not exist
and no caliper exists.** No cell is filled with an estimate.

### 5.1 Reference values that are NOT measurements (so they are never mistaken for one)

These are on record, carry provenance labels, and are **forbidden in the
measurement column**:

| Quantity | Value | Label / source |
|---|---|---|
| SMA coupling thread | 1/4"-36 UNS, major Ø **6.35 mm**, pitch **0.7056 mm/thread** | COMMITTED family key — `bench/connector-family-reference/REFERENCE.md` row 1; `bench/rf-connector-geometry` STEP 5 |
| SMA hex across-flats / across-corners | AF **7.94 mm** (5/16 in) / AC **9.17 mm** (derived) | INDUSTRY-STANDARD SMA, UNVERIFIED on host — `fe700201` §3c; `40e1a49a` |
| SMA plug **body length** | industry-typical **~15–22 mm** | ENGINEERING KNOWLEDGE, UNVERIFIED — `bench/rf-connector-geometry` STEP 5 (the card there records the value itself as UNKNOWN) |
| Bulkhead barrel through the panel | Ø 6.35 mm barrel in a documented **6.50 mm** panel hole (0.15 mm diametral clearance) | documented project pattern + arithmetic — `fe700201`, `README_big.md:20-23` |
| TNC hex (for family separation) | AF **12.7 mm**, AC 14.66 mm — the committed kit value "~9.5 mm" is geometrically impossible and is corrected here | COMMITTED + COMPUTED-CORRECTED — `REFERENCE.md` row 7 audit B2 |

---

## 6. WHAT WOULD RESOLVE EACH UNKNOWN (the unblock path)

| Unknown | Resolved by | Tool / access |
|---|---|---|
| Body OD of CN-2/3/5/6 (+CN-8) | Procure B1/B4 (+B6); caliper the coupling-nut cylinder at 3 axial stations (mating plane, mid-body, back shoulder); report min/max if out-of-round | **digital caliper, ±0.01 mm** (MUST-PROCURE) |
| Body length of CN-2/3/5/6 | Caliper mating plane → cable-entry shoulder (unmated, boot/flag out of the jaws) | **digital caliper, ±0.01 mm** |
| Body OD / length of CN-1, CN-7 (board jacks) | Carrier boards in hand (`c3-a`, ref-TX board) and/or the footprint's mechanical drawing | **board access** (`c3-a` is a fleet resource but not attached to any host) + caliper or vendor drawing |
| Body OD / length of CN-4 (bulkhead) as a loose part | Procure B2; caliper barrel (over threads and over the unthreaded shoulder, stating which), hex AF/AC, overall end-to-end length | **caliper** + the vendor drawing shipped with the part |
| CN-4 **as installed** (panel-side barrel length, far-side thread) | Jam-nut removal (breaks the O-ring seal — **semi-destructive**) or a non-contact interior view | **x-ray / CT scan** of the assembled wall, or destructive disassembly |
| Solder-side geometry of CN-1/CN-7 | Desolder (**destructive**) or image the joint | **x-ray** or a footprint/3D model from the board source |
| Designator / printed marking on any connector | The part in hand, or the vendor label on the shipping bag | **macro camera** (no camera exists on this host) or the datasheet that ships with the order |
| **Standard vs reverse-polarity** for any of the above | **A caliper can never settle this** — RP swaps only the centre contacts; thread, hex and body geometry are identical | **thread-flank inspection / contact-pin inspection** (the on-site discriminators in `bench/chamber-rf-feedthroughs/REPORT.md:148-154`), or the part's MPN |
| Family confirmation (SMA vs 3.5 mm / 2.92 mm-K, which share the 1/4"-36 thread) | Thread-pitch gauge + centre-pin Ø + dielectric inspection | **thread-pitch gauge / optical comparator** |
| Chamber-side feedthrough identity (FT-1..FT-5) | A site visit to a named chamber (all five states are `NON-EXISTENT` today) | **physical access** + custodian approval (Felix, MEDIUM per `4b3ec9b5`) |

---

## 7. Reproducibility and the checkable audit

`connector_census_t_87830aa4.py` (stdlib only; no network, no clock, no
randomness) re-runs the §2 census and audits the §4 connector-run arithmetic.
Verbatim output: `output_t_87830aa4.txt`. **A second run is byte-identical**
(verified this session, `cmp` clean).

Audit result (verbatim, tail of the output):

```
[PASS] no measuring instrument asset on host: 0 hit groups
[PASS] no physical RF coax/connector asset in repo tree: zero
[PASS] no connector photograph exists: zero
[PASS] bulkhead counted once, not twice: CN-4 carries 2 coaxial interfaces in 1 body row
[PASS] interface arithmetic closes: 7 bodies -> 8 halves -> 4 mating joints
[PASS] every run body is tied to a cable ID: no orphan connector
[PASS] each of the 2 RF cables terminates exactly 2 cable-end plugs: C-RF-INT-1: CN-2,CN-3 ; C-RF-EXT-1: CN-5,CN-6
[PASS] cable-ID coverage complete: frozen coax IDs present: ['C-RF-EXT-1', 'C-RF-INT-1']
[FAIL] measured numbers available for any body: 0 of 7 bodies have a measured OD or length -- no part exists (UNKNOWN)
```

**6 of 7 checks PASS.** The single FAIL is not a defect in the audit — it is the
honest measurement gap this record exists to report. It is asserted as a check
precisely so that a future run cannot silently claim the numbers without a real
caliper reading flipping it to PASS.

---

## 8. NOTHING FABRICATED

No measurement was performed and none is claimed. No connector body OD and no
body length is stated as a measurement anywhere in this record. No cable, no
connector, no caliper, no camera and no attached DUT exist on this host (fresh
census, §2). No photograph is claimed (no camera, no subject). No datasheet
value is claimed (no vendor datasheet on host; the standing no-outbound-fetch
constraint is respected — nothing attempted). Every reference figure is labelled
with its provenance class (COMMITTED / COMPUTED / INDUSTRY-TYPICAL / ENGINEERING
KNOWLEDGE, all UNVERIFIED on host) and is excluded from the measurement column.
The connector census and its interface arithmetic are reproducible and
cross-checked. The unblock path for every UNKNOWN is named with a specific tool
or access.
