# Failure-mode entry: cable jacket stiffening at -20 C / -40 C (strain into connectors and panel mounts)

Fleet card: `meshcore:t_6d5add05` ("Analyze jacket stiffening effects at
-20C/-40C") — first worker output for this card. Claimed by dq05
(2026-09-15 12:59:46+02:00), running 13:04:47+02:00.

Date: 2026-09-15 · Repo: meshcore (main) · Worker: dq05 (profile
worker-heavy) · Host: `c03rad0r-DQ05proplus`.
Artifacts: this directory (`bench/jacket-stiffening/`).

This is a **deepening of `04db4fae` FM-8** ("jacket stiffening ->
bend-radius violation -> shield deformation"). FM-8 exists in the
13-mode catalogue as one row; this card asks for the full four-attribute
entry with the strain-transfer path into connector bodies and panel
mounts worked out. Entry ID used here: **FM-8D** (D = deep-dive; does
not renumber the catalogue).

Standing constraints honored (unchanged from sibling sessions):

- **No RF coax exists on host or on any record** (`66573e52`: the cable
  is a MUST-PROCURE item, MPN TBD; `55585471` BOM: "Unknown (not on any
  record)"; `fe700201` 2a: none on hand). Nothing was measured.
- **No chamber located** (`24eb918c`/`766ac96d`/`ec80c11e`/`fe700201`/
  `40e1a49a`, fleet state re-read this session for the card ID: card
  found, body recovered, zero result-bearing fields on the chamber
  family). No cold run has occurred (`65c9c3df` caveat 4).
- **No outbound fetch** (standing dq05 operator constraint). The task
  asks to "cite the coax cable datasheet ... and the jacket material
  datasheet" — **no such datasheets exist on host and none may be
  fetched**, so every would-be-datasheet value below is explicitly
  labeled INDUSTRY-TYPICAL / UNVERIFIED, per fleet convention. Nothing
  fabricated; the fetch that would upgrade this entry is listed in
  Section 9.

---

## 1. THE ENTRY (acceptance deliverable)

**FM-8D — Cable jacket stiffening at low temperature -> elevated bending
stiffness and handling loads -> bend-radius violation + strain transfer
into connector bodies and panel mounts.**

| Attribute | Value |
|---|---|
| **(a) Mechanism** | The jacket polymer's Young's modulus E rises steeply as temperature drops toward (and below) its glass transition / low-temperature brittleness point. Bending stiffness EI and the moment needed to hold/force a bend M = E·I/R rise proportionally; a snag or repositioning force that a warm cable absorbs by draping is transmitted by the cold cable as a near-rigid lever into the connector termination, the SMA coupling-nut/bulkhead thread, the panel-mount retaining nut, and the panel hole edge. Differential axial shrinkage (jacket CTE ~10x metal, `04db4fae` 2.6) adds a tensile/compressive strain at the termination. |
| **(b) Likelihood -20 C** | **Mechanism certain in degree; damage likelihood bifurcates on jacket material, which is NOT on record (MPN TBD, `55585471` B1/B4):** PVC-jacket class (incl. most generic coax and the USB-C serial cable if PVC/TPE): **HIGH** — plasticized PVC is in its steep modulus-rise zone approaching brittleness at -20 C (many plasticizer grades already below their brittleness temperature), E up ~10-25x. FEP-jacket class (standard RG316/M17-113 construction, INDUSTRY-TYPICAL): **LOW** — FEP is still well above its Tg at -20 C, E up only ~2-4x. |
| **(b) Likelihood -40 C** | Same bifurcation, sharper: PVC class: **HIGH-CERTAIN** — essentially all plasticized-PVC grades are below their brittleness point; E up ~50-150x, jacket glassy, impact-crack risk added (frost-laden surface knocked during handling). FEP class: **LOW** (same 2-4x; no regime change between -20 and -40). USB-C cable (the only cable crossing the sealed boundary in the primary OTA variant, `fe700201`): **HIGH at -40** — no temp rating on record for it at all; typical COTS USB-C rating class 0..+70 / -20..+60 C (INDUSTRY-TYPICAL, UNVERIFIED) puts -40 C outside any on-record rating. |
| **(c) Reversibility** | **The stiffening itself is fully reversible** — modulus returns on warm-up with no thermal degradation at these temperatures, for both PVC and FEP classes. **Permanent sub-modes:** (1) shield-braid kink if the stiffened cable is forced below its minimum bend radius — permanent impedance bump, does not recover; (2) jacket crease if the outer fiber is bent past the glassy yield strain — permanent kink line; (3) cold-set of the cable shape is LOW-MEDIUM for the PVC class if held bent through a full cold cycle (mostly springs back on warm-up through the transition zone; residual set concentrates in the braid, i.e. it merges into sub-mode 1) and LOW for FEP (creeps negligibly at -40 C); (4) whatever damage the transmitted loads did at the connector/panel (loosened coupling/retaining nut, ovalized hole, lifted edge-launch pad) is permanent. |
| **(d) Consequence class** | **DEGRADES HARDWARE** (primary) — permanent shield kink, connector-body/termination strain, panel-mount preload loss. **Corrupts measurement data additionally for the conducted variant B** — a braid kink is an impedance bump (standing-wave/IL ripple), which corrupts any phase/power-quantitative use; for the primary decode-count edgescan it is a small fixed loss, harmless given the 165 dB budget (`04db4fae` 2.7 verdict carried). **NOT destruction-class** — forces are 0.1-0.3 N·m-class on metal connectors; worst credible permanent outcome is an edge-launch SMA pad lifted off the 0.8 mm FR-4 carrier (cheap, reworkable hardware; would remove the conducted path, not the campaign — the primary OTA path has no coax at all, `55585471` 3a). The campaign's one destruction-class mode (USB-C VBUS short on thaw) belongs to FM-4, not this entry. |

**Strain-transfer note (required by acceptance):** see Section 6 for the
worked path and numbers. Short form: a warm jacket (E ~20 MPa class)
makes the cable a compliant strap — M at R = 12.7 mm is ~0.002 N·m and a
1 N snag merely drapes the cable. The same PVC jacket glassy at -40 C
(E ~1-3 GPa) makes it a rigid lever: the identical snag on a 0.15 m
cold stub reacts ~0.15 N·m into the connector, and a bend forced at the
12.7 mm industry-nominal minimum loads the termination with
~0.11-0.34 N·m — 50-150x room temperature — which backs off coupling
and retaining nuts, prys the bulkhead in its 6.5 mm panel hole, and
concentrates on the edge-launch SMA solder pads. Consequence: connector
and panel degradation + the moisture paths of FM-5/FM-6 re-opened by
lost preload, and in variant B a permanent impedance discontinuity in
the measured path.

---

## 2. Datasheet citation status (what the task asks vs what exists)

The acceptance asks to "cite the coax cable datasheet (temperature
rating, bend radius, attenuation vs frequency, any temperature
coefficient) and the jacket material datasheet (low-temperature
brittleness / glass transition)". **Neither datasheet exists on host or
on any record**, and the no-outbound-fetch constraint stands
(`66573e52`, `fe700201`, `04db4fae` — denials recorded in prior
sessions, not retried). What exists is assembled below, with every
would-be-datasheet value labeled.

### 2.1 Coax cable "datasheet" values actually on record

| Datasheet item the task asks for | On-record value | Source + label |
|---|---|---|
| Temperature rating | "both [RG316/RG178] are rated to -40 C (PTFE dielectric)" — the project's own BOM sentence | `55585471` step 4.2 (verbatim). **A planning claim about the dielectric, NOT a vendor jacket rating.** INDUSTRY-TYPICAL RG316/M17-113 class service range is -55 to +200 C with FEP jacket — UNVERIFIED, no vendor datasheet |
| Bend radius (static min) | 12.7 mm (0.5 in), given as absolute mm not OD multiple (coincidentally ~5x OD) | `fe700201` 2b; carried `04db4fae` FM-8, `t_0d86117f` B1, `66573e52`. INDUSTRY NOMINAL, UNVERIFIED |
| Bend radius (alt rule-of-thumb) | 10x OD = 25.0 mm | `fe700201` 2b. RULE OF THUMB, UNVERIFIED |
| Bend radius (dynamic/repeated-flex — the one that governs handling) | **UNKNOWN — no source on host or in any prior bench report** | `66573e52`. This absence is itself the key finding: the governing spec for THIS failure mode is exactly the missing one |
| Attenuation vs frequency | Point value only: ~0.3 dB/m at 1 GHz -> ~0.15 dB for the 0.5 m cable at 868 MHz; total conducted path (2 cables + feedthrough + 3 mated SMA pairs) ~0.3-0.5 dB at 868 MHz. No swept table exists on record | `55585471` step 5, verbatim carried `04db4fae` 2.6 |
| Temperature coefficient | Copper resistivity 0.39 %/K -> conductor-dominated attenuation drops ~10 % over the 60 K swing (sqrt scaling) = ~0.02 dB change on the 0.65 m path; PTFE er tempco ~200 ppm/K -> ~4.5 deg phase over 0.5 m at 868 MHz; PTFE dielectric step near -20 C flagged INDUSTRY-KNOWN, UNVERIFIED | `04db4fae` 2.6 (computed from cited inputs); `65c9c3df` 3b. Both negligible for the decode-count protocol (165 dB budget) |
| MPN / vendor | **TBD — MUST-PROCURE, does not exist on host** | `55585471` B1/B4; `66573e52` fresh census |

### 2.2 Jacket material "datasheet" values (industry-typical, UNVERIFIED — no jacket material datasheet on host)

The jacket material is **not even identified on record** (MPN TBD,
`55585471` B1/B4). RG316 is commercially offered in more than one
jacket class, and the USB-C serial cable is an unidentified COTS part,
so the entry must cover the candidate classes:

| Jacket class | Where it plausibly appears in this campaign | Glass transition / low-temp behavior [ALL INDUSTRY-TYPICAL, UNVERIFIED] | E at room -> -40 C | Verdict at -20 / -40 C |
|---|---|---|---|---|
| Plasticized PVC | Generic/cheap coax patch cables; plausible for the COTS USB-C cable (or TPE, below) | Base polymer Tg ~+80 C is depressed by plasticizer; brittleness temperature (ASTM D746 class) typically -10 to -40 C, plasticizer-content dependent | ~20 MPa class -> 1-3 GPa (50-150x) once glassy | HIGH / HIGH-CERTAIN |
| FEP | Standard RG316 (M17/113 / MIL-DTL-17 class) construction — the most likely procured part | Tg ~-80 C class; stays well above Tg at both setpoints; low-temp service typically -55 C and below | ~2-4x rise | LOW / LOW |
| PE (solid polyethylene) | Some RG316-U / RG178 variants | Tg ~-110 C; stays ductile | small | LOW / LOW |
| TPE (thermoplastic elastomer) | Plausible for the COTS USB-C cable overmold | Service typically to -40 C; modulus rise moderate | ~3-10x | LOW-MEDIUM / MEDIUM (at or beyond rating edge) |
| PU (polyurethane jacket) | Some assemblies | Stays flexible to ~-40 C, some grades -60 | ~2-5x | LOW / LOW-MEDIUM |
| Silicone | Not plausible for coax jackets; carried for completeness | Tg ~-55 to -65 C (`04db4fae` 2.8) | small at both setpoints | LOW / LOW |

**USB-C serial cable (primary variant A's only crossing cable):** OD
4.0-5.0 mm INDUSTRY-TYPICAL UNVERIFIED (`fe700201` 3c); **no
temperature rating, no jacket material, no bend radius on any record.**
Typical COTS USB-C rating class 0..+70 or -20..+60 C (INDUSTRY-TYPICAL,
UNVERIFIED) — at -40 C it operates outside any on-record rating, and
its overmolded strain relief at the connector is the stiffest point of
the whole assembly, concentrating load directly into the USB-C
receptacle anchors on the DUT carrier (which also carry `04db4fae`
FM-10 CTE fatigue and FM-4's thaw risk). The on-record minimum bend
radius for it: none (`04db4fae` 2.7 states this explicitly).

---

## 3. (a) Mechanism — stiffening physics, worked

1. **Modulus rise near Tg/brittleness.** Thermoplastic jacket polymers
   show a steep (decades-scale) rise in Young's modulus E as the
   temperature drops through the rubbery-to-glassy transition
   [INDUSTRY-TYPICAL polymer behavior, UNVERIFIED for any specific part
   — no cable datasheet on host, `04db4fae` 2.7 carries the same
   label]. A flexible cable jacket sits at E ~20 MPa class at room
   temperature; glassy PVC sits at 1-3 GPa.
2. **Bending stiffness and bending moment scale linearly with E.** For
   a thin-wall tube jacket, I = pi/64 * (D^4 - d^4). RG316
   industry-nominal geometry: D = 2.50 mm (OD, `55585471` 3b /
   `fe700201` 2b), d = 1.78 mm (braid OD, INDUSTRY-TYPICAL, UNVERIFIED)
   -> **I = 1.43 mm^4**. Moment to hold/force a bend of radius R:
   **M = E * I / R** (checkable formula; inputs labeled).
   - Room temperature, E ~20 MPa, R = 12.7 mm: **M ~ 0.002 N·m** —
     negligible; the cable is a strap.
   - PVC jacket at -20 C (E up 10-25x): **M ~ 0.02-0.06 N·m**.
   - PVC jacket at -40 C (E up 50-150x): **M ~ 0.11-0.34 N·m** — i.e.
     the same physical bend now needs 50-150x the moment, reacted at
     the cable's anchored end: the connector.
   - FEP jacket at either setpoint (E up 2-4x): **M ~ 0.004-0.009
     N·m** — stays negligible.
3. **The room-temperature bend becomes a cold bend-radius violation.** A
   cable routed at its room-temperature minimum (12.7 mm static,
   INDUSTRY NOMINAL, `fe700201` 2b) cannot flex below it when cold;
   instead the cold jacket transmits the constraint load instead of
   absorbing it (`04db4fae` 2.7; `66573e52` 231-236). Where the
   routing forces the bend — the 90-deg turn at the bulkhead needs a
   27.9 mm swept envelope at R = 12.7 mm (`fe700201` 2d) — the reaction
   lands on the connector body and the panel mount (Section 6).
4. **Handling loads stop being absorbed.** Warm, a snag or reposition
   merely drapes the cable (local deformation, near-zero moment at the
   ends). Cold and glassy, the same cable is a near-rigid lever: a
   1 N handling force on a 0.15 m cold stub reacts **~0.15 N·m** at the
   termination (M = F*L, rigid-lever approximation); on the 0.5 m
   exterior run, ~0.5 N·m. Both exceed the cold bend moments of point 2
   — operator handling, not steady-state cold, is the dominant load
   case. This is why the **dynamic/repeated-flex bend radius** (the
   governing spec) matters more than the static one, and that spec is
   UNKNOWN on record (Section 2.1).
5. **Axial shrink adds a static strain at the termination.** Jacket CTE
   is ~10x metal (PVC-class ~170 vs copper ~17 ppm/K, `04db4fae` 2.6
   "jacket shrinks (PVC-class CTE ~10x metal); axial shrink of the
   cable vs the connector pulls on the termination — a strain
   mechanism feeding FM-8"). Over the 45-65 K swing: differential
   strain 0.69-0.99 %, i.e. 3.4-5.0 mm per 0.5 m IF free. The braided
   shield constrains most of it (braid grips rather than slides,
   Chinese-finger-trap geometry), so the net is a standing tensile load
   between jacket and conductor stack transmitted into the crimp/solder
   termination and the connector's capture of the cable — a pre-load
   that the bending moments of points 3-4 then modulate. Magnitude
   UNVERIFIED (no jacket shrink data on host); direction certain.
6. **Frost loading is an adjacent aggravator, not the cause.** Ice on
   the jacket (certain, moisture supply `65c9c3df`) adds mass and
   surface bonding (cable frozen to its routing/gasket), so a reposition
   force arrives as an impulse on a bonded, glassy, ice-loaded beam.
   The freeze-bond release also delivers shock loading — worse for a
   glassy (impact-brittle) PVC jacket than for a still-ductile FEP one.

---

## 4. (b) Likelihood at -20 C vs -40 C

Regime statement (carrying `04db4fae` verdict 3): **-20 vs -40 is the
same kind, worse degree — for PVC-class jackets -40 C is a genuinely
different regime (glassy + impact-brittle), for FEP-class jackets the
two setpoints are barely distinguishable.**

| Sub-case | -20 C | -40 C | Basis |
|---|---|---|---|
| Stiffening mechanism fires (E rises) | CERTAIN (degree depends on class) | CERTAIN | Polymer physics, INDUSTRY-TYPICAL |
| Damage requires: modulus x forced-bend or handling | PVC class: **HIGH** (10-25x E; some plasticizer grades already brittle) | PVC class: **HIGH-CERTAIN** (50-150x E; all grades below brittleness; impact-crack risk) | Section 3.2 numbers |
| FEP class (likely procured RG316) | **LOW** (2-4x E) | **LOW** (no regime change) | Section 2.2 |
| USB-C serial cable (primary path's only crossing cable) | MEDIUM (unknown jacket; if PVC already stiffening, if TPE near edge) | **HIGH** (outside any on-record rating class entirely) | Section 2.2 |
| Forced bend below Rmin at the bulkhead turn | Depends on routing — UNKNOWN, no chamber, routing not frozen (`t_e5d5eaae` undispatched; `fe700201` 2d clearance thresholds 14/26.25 mm) | same, worse when it happens | `66573e52` 226-229 |
| Quantitative damage threshold | Cannot be stated: would need the procured cable's vendor datasheet (dynamic bend radius, jacket material, modulus-vs-T curve) — none exists on host | same | Section 2.1 |

**Why the rating claim gives no -20/-40 discrimination:** the only
on-record temperature statement ("rated to -40 C (PTFE dielectric)",
`55585471` 4.2) addresses the dielectric, not the jacket. PTFE/FEP are
ductile at both setpoints (Tg ~-97 C, `65c9c3df` 3b, carried `04db4fae`
FM-11). The jacket — the component whose property change this entry is
about — has no identified material, hence no citable limit, hence the
bifurcated verdict instead of a single number.

---

## 5. (c) Reversibility

- **Modulus: fully reversible.** Warm the cable back to lab ambient and
  E returns; there is no thermal degradation, no plasticizer loss, no
  crosslink change at -20/-40 C exposure for either PVC or FEP class
  [INDUSTRY-TYPICAL, UNVERIFIED for any specific part]. A stiff cable
  that was merely cold (never bent past its limits, never snagged)
  comes back mechanically identical. This is the same reversible class
  `04db4fae` 2.7 assigned ("Jacket recovers; shield kink PERMANENT").
- **Cold-set deformation: LOW for FEP, LOW-MEDIUM for PVC.** Cold set
  (retained bend after hold-cold-then-warm) is a viscoelastic creep
  phenomenon concentrated near the transition zone. A glassy PVC jacket
  held bent through the soak mostly stores the deformation elastically
  and springs back as it warms through the transition; residual set
  appears mainly when the outer fiber exceeded yield (a crease/kink
  line) or when the braid took a set — both of which are the bend-
  violation sub-mode rather than time-at-temperature. FEP creeps
  negligibly at -40 C. Net: **if the routing respects the cold bend
  radius, no permanent cold-set should be expected; if it does not,
  the permanent damage is the kink, not polymer set.**
- **What does NOT recover:** (1) a shield-braid kink (permanent
  impedance bump, `04db4fae` 2.7), (2) a jacket crease past glassy yield,
  (3) connector/panel damage the transmitted loads caused — backed-off
  coupling or retaining nut (recoverable only by re-torque, i.e.
  operator action; the loosened state itself is what feeds FM-5/FM-6),
  galled threads, ovalized panel hole, lifted edge-launch pad, torn
  USB-C strain-relief overmold.

---

## 6. (d) Consequence class + the strain-transfer path (required note)

**Consequence class: DEGRADES HARDWARE (primary); additionally
CORRUPTS MEASUREMENT DATA for the optional conducted variant B; NOT
destruction-class.**

**Strain-transfer mechanism, worked (the note the acceptance asks
for):**

1. **Into the connector body.** The cold cable's bending moment
   (M = E·I/R, Section 3.2: 0.02-0.06 N·m at -20 C PVC, 0.11-0.34 N·m
   at -40 C PVC, vs 0.002 N·m warm) reacts at the SMA plug body. The
   load path: plug body -> coupling-nut thread -> mating faces /
   bulkhead jack thread. Two effects: (a) **preload loss** — the moment
   prys the mating plane and can back off a finger-tight coupling nut
   (no torque wrench exists; it is BOM item `55585471` 3b.4), which
   re-opens the interface gap that FM-2 (frost film) and FM-3 (ice
   jacking) exploit; (b) **thread and body wear** under repeated
   cold-handling moments (permanent, low rate).
2. **Into the panel mount.** The bulkhead jack is retained by its nut
   in a 6.5 mm hole (project's own documented wall-pass pattern:
   "Fully waterproof with SMA O-rings",
   `~/repos/balloon/tracker/hardware/enclosure/README_big.md:20-23`,
   read this session; Amphenol 132134-class per `40e1a49a`). A bending
   moment applied at the bulkhead becomes a **prying load on the
   retaining nut and the panel hole edge**: the nut sees a moment arm
   of order the panel thickness, and a 0.1-0.34 N·m cable moment on a
   small-diameter retaining nut is a kg-class lever load. Consequences:
   retaining-nut preload loss (the bulkhead loosens in the panel —
   intermittent, operator-invisible), hole-edge ovalization in thin or
   printed panels, and loss of O-ring squeeze — which converts this
   mechanical mode into a **moisture path** (feeds FM-6 seal failure
   and the FM-1..FM-3 frost chain on the next cooldown). For the
   chamber wall itself nothing can be said: no chamber exists on any
   record (Section 0 constraints); the 6.5 mm O-ring bulkhead pattern
   is the only on-record mount precedent.
3. **Into the DUT-side termination (the weakest link).** In the
   conducted variant the cold-side cable end terminates at the DUT's
   edge-launch SMA on the 0.8 mm FR-4, 75x55 mm carrier
   (`fe700201`: J1/J2 placed 2 mm inboard of the 55 mm board edges).
   A glassy 0.15 m stub reacting even a 1 N handling force delivers
   ~0.15 N·m at the launch — concentrated on the edge-launch pad
   solder joints, which are the least redundant element in the chain
   (metal connector bodies and bulkhead hardware yield/loosen; a
   lifted pad does not un-lift). This sub-case is what elevates the
   entry's consequence from "connector hardware" to "DUT carrier RF
   path" — still degrades-class (cheap, reworkable board; and only
   variant B uses it), but it is the single most consequential
   strain-transfer target.
4. **In the primary OTA variant** there is no coax; the strain path is
   the USB-C serial cable into its receptacle anchors on the SuperMini
   carrier — same lever physics with an even less-known jacket, at a
   connector whose failure mode is already flagged destruction-class
   on thaw (FM-4 VBUS). The stiffened-cable handling force itself is
   degrades-class (receptacle anchors, overmold tear), but any
   mechanical degradation of the receptacle compounds FM-4's
   liquid-ingress exposure.

**Data consequence, precisely bounded (carried from `04db4fae`
2.6/2.7):** a braid kink is a permanent impedance bump — it corrupts
any phase/power-quantitative measurement, and for the decode-count
edgescan it adds a small fixed loss that the 165 dB link budget
(`55585471` step 5) absorbs. The measurement-relevant risk of THIS
entry is therefore **indirect**: not the loss the kink adds, but the
intermittency the mechanical preload loss creates (a loosened coupling
nut or bulkhead is a time-varying contact — the between-scan-points
edge-shift class that the >5 ppm RMS residual check cannot catch when
it shifts uniformly, `04db4fae` 2.1).

---

## 7. Differences from and additions to the existing catalogue

| Point | `04db4fae` FM-8 (existing row) | This entry FM-8D (addition) |
|---|---|---|
| Likelihood | "HIGH at tight routing / HIGH" | Bifurcated by jacket class: PVC HIGH(-CERTAIN), FEP LOW; USB-C HIGH at -40. Routing gate unchanged (no chamber, routing unfrozen) |
| Mechanism | Modulus rises; forced bend kinks braid; strain into terminations | Worked moments (M = E·I/R with I = 1.43 mm^4), handling-lever loads (0.15-0.5 N·m per N), axial-shrink strain term, ice-bond shock term |
| Reversibility | "Jacket recovers; shield kink PERMANENT" | Same verdict, plus cold-set quantified (LOW FEP / LOW-MEDIUM PVC, set concentrates in the kink sub-mode) and the non-recovering collateral list (nuts, hole, pads) |
| Consequence | Data (impedance bump) + hardware, cheap class | Same class, plus the panel-mount prying path and the FM-5/FM-6/FM-4 coupling chain made explicit |
| Datasheet asks | Not asked | Tasked; answered as absence-of-source with every value labeled (Section 2) |

No conflict with the catalogue row; FM-8D refines it. The one
governing-spec absence worth restating: **the dynamic/repeated-flex
bend radius — the spec that governs cold handling — exists in no
on-host source** (`66573e52`), and the static 12.7 mm figure is
industry-nominal UNVERIFIED.

---

## 8. Source summary

| Claim | Source | Confidence |
|---|---|---|
| Card ID/body recovered (title, four attributes, citation demand) | `~/.hermes/bot/fleet_queue_state.json` task `meshcore:t_6d5add05` (read this session, verbatim body) | HIGH |
| Card claimed by dq05 12:59:46+02:00, running 13:04:47+02:00 | fleet_queue_state claims/running entries | HIGH |
| No RF coax on host or record; MPN TBD MUST-PROCURE; dynamic bend radius UNKNOWN | `66573e52` (fresh census + 6 sibling concurrences) | HIGH |
| RG316 OD 2.50 mm; min bend 12.7 mm static (abs); 10xOD alt 25.0 mm; swept envelope 27.9 mm at R=12.7 | `fe700201` 2b/2d; `55585471` 3b; carried `04db4fae`, `t_0d86117f` — INDUSTRY NOMINAL, UNVERIFIED | LOW-MEDIUM (planning inputs) |
| "Rated to -40 C (PTFE dielectric)" BOM claim | `55585471` step 4.2 verbatim (also `bench/rf-feedthrough-bom/REPORT.md:195`) | LOW-MEDIUM (project planning claim, not a vendor jacket rating) |
| Attenuation ~0.3 dB/m @1 GHz; ~0.15 dB per 0.5 m @868 MHz; path total 0.3-0.5 dB; 165 dB budget | `55585471` step 5 (`bench/rf-feedthrough-bom/REPORT.md:235-244`) | MEDIUM (planning figures) |
| Copper tempco 0.39 %/K, PTFE er ~200 ppm/K, Tg ~-97 C, PTFE dielectric step near -20 C flag | `65c9c3df` 3b; carried `04db4fae` 2.6 | MEDIUM (established material data, UNVERIFIED on host) |
| Jacket CTE ~10x metal; termination pull mechanism | `04db4fae` 2.6 verbatim | MEDIUM |
| FM-8 prior verdicts (HIGH/HIGH, jacket recovers / kink permanent, impedance bump + cheap-hardware class) | `04db4fae` 1 (master table row 8) + 2.7 | MEDIUM |
| Panel-mount pattern: 6.5 mm SMA bulkhead holes, "Fully waterproof with SMA O-rings" | `~/repos/balloon/tracker/hardware/enclosure/README_big.md:20-23` (read this session; project balloon-enclosure pattern, NOT chamber data) | MEDIUM (documented precedent, not the campaign hardware) |
| Edge-launch SMA on 0.8 mm FR-4 carrier, 2 mm inboard of 55 mm edges | `fe700201` (hub_board_f33.kicad_pcb via that report) | MEDIUM |
| Moisture supply certain at both setpoints (ice loading, freeze bonding) | `65c9c3df` Magnus table | HIGH |
| USB-C cable: only crossing cable in variant A; OD 4.0-5.0 mm INDUSTRY-TYPICAL; no temp rating/bend radius on record | `fe700201` 3c; `04db4fae` 2.7 | HIGH (for the absence) / LOW-MEDIUM (for the OD) |
| Jacket class table (PVC/FEP/PE/TPE/PU modulus + Tg behavior) | INDUSTRY-TYPICAL engineering knowledge — **UNVERIFIED, no jacket material datasheet on host, no outbound fetch per standing constraint** | LOW (deliberately labeled) |
| I = 1.43 mm^4; M = E·I/R numbers; 1 N lever moments; 0.69-0.99 % shrink strain | Computed this session from the labeled inputs above (formulas shown in Section 3) | MEDIUM (arithmetic checkable, inputs UNVERIFIED) |
| No outbound fetch attempted | Standing dq05 operator constraint (prior sessions' denials recorded, not retried) | HIGH |

---

## 9. What would resolve the unknowns (unblock path)

1. **Procure the RG316 assemblies** (BOM `t_0d86117f` B1/B4) and obtain
   the **vendor datasheet**: jacket material, static AND dynamic/repeat
   bend radius, temperature rating (jacket, not just dielectric),
   modulus or bend-force vs temperature if offered. One PDF replaces
   every INDUSTRY-TYPICAL label in Sections 2.2/3/4.
2. **Obtain the USB-C cable's rating** (it is a COTS part already in
   the loop — a part number read off its jacket/marking would let its
   datasheet be fetched when the fetch constraint lifts).
3. **Freeze the routing** (card `t_e5d5eaae`) — the forced-bend
   geometry at the bulkhead is the multiplier on every moment in
   Section 3; until routing is frozen, likelihood stays
   "HIGH-where-tight, unknown-where-not".
4. **Locate the chamber** (t_a2f7f281 family) — the panel-mount prying
   analysis (Section 6.2) is against the O-ring bulkhead precedent
   until a real wall exists to compare.
5. **Cold bend test at procured time**: one sacrificial cable, one
   ice-bath bend at R = 12.7 mm and at 25 mm, inspect braid — converts
   the reversibility verdict (Section 5) from physics to observation.