# FM-FT-MOUNT-01 — Feedthrough mechanical mount: cold-loosening by differential contraction

**Scope discipline: analysis only.** This entry documents a failure mode and its arithmetic.
It contains **no mitigation, no design change, no corrective action, and no recommendation of
any kind**. Values labelled `[A]` are stated modelling assumptions of the companion
calculator; values labelled `[S<n>]` are read from the reference list in §R.

Companion artifact (arithmetic, deterministic): `analysis/failure-modes/feedthrough_mount_thermal_calc.py`;
its frozen stdout is `analysis/failure-modes/feedthrough_mount_thermal_calc.out`. Every number
quoted below appears in that transcript.

---

## Record fields

| Field | Value |
|---|---|
| **ID** | FM-FT-MOUNT-01 |
| **Title** | Feedthrough mechanical mount — cold-loop loosening by differential contraction between connector body and panel (−20 °C and −40 °C duty) |
| **Item** | Panel-mounted SMA **feedthrough bulkhead adapter** retained by a single jam nut onto a panel face, static elastomeric seal at the body/panel interface. Reference part class: RF-LAMBDA `RFCARASFSFP01A` — *Feedthrough Bulkhead Adapter … SMA Female to SMA Female*, body material **stainless steel SU303**, centre pin brass/gold, insulator PEI `[S1]` |
| **Mount hardware** | Jam nut, SMA bulkhead class: quoted mount torque **12–15 in-lbs** (stainless body) / **8–10 in-lbs** (brass body) `[S2]` |
| **Duty** | Thermal loop from **+20 °C** assembly to **−20 °C** (transient, ascent) and **−40 °C** (soak, float altitude) |
| **(a) Mechanism** | §A — differential contraction of the paired metals, thread-preload loss, gasket compression-set relaxation |
| **(b) Likelihood −20 °C** | **LOW** — ≥55 % of nominal preload retained in every pairing tabulated; all parts inside their rated temperature range (§B.1) |
| **(b) Likelihood −40 °C** | **LOW–MODERATE** for the atmospheric duty; **MODERATE** for the stainless-body-in-aluminium-panel pairing and for the pressure-rated duty (§B.2) |
| **(c) Reversibility** | Path-dependent: the elastic path is **REVERSIBLE**; the compression-set, embedment, cold-flow and nut-rotation paths are **PERMANENT** (§C) |
| **(d) Consequence class** | **Class III — MAJOR, LATENT** (permanent loss of a rated function) (§D) |
| **References** | §R — 7 sources, each quoted with a number; identifiers in §R |

---

## (a) MECHANISM

The causal chain, in order.

**A.1 — The two metals and their mismatch.** The mount clamps a metal connector body to a metal
panel. The body is austenitic stainless steel — SU303 on the reference part `[S1]` — and the
panel is an aluminium alloy in the assumed configuration. The linear coefficients of thermal
expansion are, per `[S3]` (table unit as printed: `10⁻⁶ m/m °C = 1 μm/m °C`, i.e. ppm/K):

| Side of the joint | Material | α (ppm/K) | Source |
|---|---|---|---|
| Connector body | Stainless steel, austenitic 304 (applied to SU303 as `[A]`) | **17.3** | `[S3]` |
| Connector body (alt.) | Brass | **18 – 19** | `[S3]` |
| Panel | Aluminium | **23** | `[S3]` |
| Panel (alt.) | Aluminium alloys | **21 – 24** | `[S3]` |
| Panel (alt., benign) | Stainless steel 304 | **17.3** | `[S3]` |
| Polymer element (if present in the axial path) | PTFE | **112 – 135** | `[S3]` |
| Ceramic insulator (hermetic feedthrough class) | Alumina | **8.1** | `[S3]` |

The driving mismatch is **Δα = α_panel − α_body = 3.7 … 6.7 ppm/K** for a stainless body in an
aluminium panel (typical 5.7; worst 6.7 at the 24 ppm/K end of the alloy band), and
**Δα = 4.0 ppm/K** for a brass body (19) in an aluminium panel (23). In a stainless-panel
variant the mismatch is **0** and the mechanism has no driving term.

**A.2 — The contraction delta.** Cooling from the +20 °C assembly state gives a differential
free strain of

```
Δα · |ΔT|  =  5.7 ppm/K × 40 K  =  228 ppm     at −20 °C
            =  5.7 ppm/K × 60 K  =  342 ppm     at −40 °C      (worst pairing: 268 / 402 ppm)
```

**A.3 — Why a sub-micron length change moves a kilonewton of preload.** The panel contracts
more than the body along the clamped axis, so the clamped stack shortens *relative to* the
body's thread envelope and the axial interference that holds the jam nut in tension is
consumed. Over a 2 mm clamped stack `[A]` the free differential is only
**0.46 µm (−20 °C) / 0.68 µm (−40 °C)** for Δα = 5.7. The length is small because the joint is
stiff: the two load paths are in series — the body's thread cross-section in tension
(A_b = 20 mm² `[A]`, E = 193 GPa `[A]`) and the panel face in compression under the nut
(A_p = 45 mm² `[A]`, E = 69 GPa `[A]`). The resulting conversion factor `[FIRST-PRINCIPLES]` is

```
ΔF = Δα · ΔT / ( 1/(A_b·E_b) + 1/(A_p·E_p) )        →  1.72 MN of preload change per unit strain
                                                        ≈ 1.7 N of preload per ppm
```

That factor is **independent of the clamped stack thickness** for a purely metal load path, so
the loss figure below is set by the material pair and not by how thick the panel is.

**A.4 — Resulting thread preload loss.** The nominal preload comes from the quoted mount torque
`[S2]` through `T = K·d·F` with the conventional nut factor **K = 0.20** `[A]` and
d = 6.35 mm (1/4 in thread) `[A]`:

| Body / torque `[S2]` | F0 |
|---|---|
| Stainless, 12–15 in-lbs (1.36–1.69 N·m) | **1068 – 1334 N** |
| Brass, 8–10 in-lbs (0.90–1.13 N·m) | **712 – 890 N** |

Against that preload, the differential contraction removes (fully metal load path):

| Pairing | Δα | loss at −20 °C | loss at −40 °C | residual at −40 °C |
|---|---|---|---|---|
| SS body / Al panel (typical) | 5.7 | **392 N = 37 % of F0** | **589 N = 55 % of F0** | 479 N (of 1068 N) |
| SS body / Al panel (worst end of alloy band) | 6.7 | 461 N = 43 % | **692 N = 65 %** | 376 N |
| SS body / Al panel (benign end) | 3.7 | 255 N = 24 % | 382 N = 36 % | 686 N |
| Brass body / Al panel | 4.0 | 195 N = 27 % of 712 N | 292 N = 41 % | 420 N (of 712 N) |
| SS body / SS panel (control) | 0.0 | 0 N = 0 % | 0 N = 0 % | 1068 N |

Expressed as stress on the body's load cross-section the loss is **19.6 MPa (−20 °C) to
34.6 MPa (−40 °C worst)** — deep inside the elastic range of the body metal, which is what
makes this particular path reversible (§C, P1).

**A.5 — Gasket / compression-set relaxation.** The static seal is an elastomeric ring — 1.50 mm
cord at a nominal **20 % compression = 0.30 mm squeeze** `[S4]` in the assumed configuration.
The axial contraction consumes only **0.46 µm (−20 °C) and 0.68 µm (−40 °C) = 0.15 % and 0.23 %
of that squeeze**, so contraction alone does not flatten the seal. The relaxation path enters
for a different reason: compression set is the *permanent* deformation of the elastomer left
after the compressive force is removed `[S4]`, measured after **25 % compression, DIN 53517 /
ASTM D395 Method B, typically 24 h at +100 °C** `[S4]`. It is a material-state change, not a
thermal displacement: it is the reason a joint can be *geometrically* clamped and still carry
less sealing stress than the squeeze calculation predicts. The source consulted quotes its
sealing-force guidelines **"at +20 °C"** only `[S4]`, so the cold sealing force is not
quantified by that source.

**A.6 — The radial channel runs the other way.** For a body-to-bore radial seal the panel bore
contracts *more* than the body OD (0.72 µm at −20 °C, 1.09 µm at −40 °C on a 3.175 mm radius),
so radial squeeze **increases** while axial clamp load **decreases**. Both signs are recorded so
the net effect is not misread: the loosening is an axial-clamp phenomenon.

**A.7 — Polymer elements amplify the chain.** If any polymer element sits in the axial load path,
the mismatch jumps from 5.7 to **117.7 ppm/K** (PTFE 135 vs stainless 17.3, `[S3]`; PTFE is the
SMA insulator material per MIL-PRF-39012 Table I, as recorded in this register's companion entry
`[S_in-repo]`), and the free differential over the same 2 mm becomes **9.4 µm (−20 °C) /
14.1 µm (−40 °C)** — about 20× the metal-on-metal case. PTFE is also the one element in the chain
that cold-flows under sustained load, so the largest driving strain and the permanent-deformation
path coincide in the same part.

**A.8 — Transient offset during a fast ramp.** The body is exposed and the panel is lagged during
ascent; the same stiffness converts a body-to-panel offset into preload loss at
**9.8 N per K (Δα = 5.7) / 11.5 N per K (Δα = 6.7)** — a 5 K offset adds ≈49 N, i.e. small next
to the equilibrium terms in A.4.

**Ordered chain, one line:** CTE mismatch (17.3 vs 21–24 ppm/K `[S3]`) → differential strain
228 ppm at −20 °C / 342 ppm at −40 °C → clamped stack shortens relative to the body's thread
envelope (0.46 / 0.68 µm over 2 mm `[A]`) → thread preload falls 37 % / 55 % of F0 from
1068–1334 N `[S2]` → the static seal's remaining margin is now set by permanent
compression-set relaxation `[S4]` rather than by the geometric squeeze.

---

## (b) LIKELIHOOD

**Assumed configuration and preload (all `[A]` unless cited):** jam nut on a 6.35 mm-threaded
body, mount torque 12–15 in-lbs `[S2]`, nut factor K = 0.20, F0 = **1068–1334 N**; body load
area 20 mm²; panel bearing area 45 mm²; clamped stack 2 mm; 1.50 mm cord seal at 20 %
compression (0.30 mm squeeze, `[S4]`).

### B.1 — Likelihood at −20 °C: **LOW**

* Contraction delta: **228 ppm** (ΔT = 40 K, Δα = 5.7).
* Preload loss: **24–43 % of F0**, i.e. **255–461 N**, leaving **606–813 N** of the 1068 N
  nominal clamp. Every pairing tabulated retains **≥57 %** of its preload.
* Preload margin: the residual clamp is still hundreds of newtons — the seal remains compressed
  and the joint remains in tension; nothing in the chain crosses a yield or separation
  threshold. The loss is a *fraction*, not a breach.
* Part temperature ratings: the adapter is rated **−55 °C … +165 °C** with storage to
  **−60 °C** `[S1]`; the UHV feedthrough class quotes cable connectors **−65 °C … +165 °C**
  `[S6]`; the silicone ring is rated **−55 °C … +230 °C** `[S7]`. At −20 °C every element is
  comfortably inside its rating, so no material-state change is invoked and no rating breach
  occurs.
* Exposure character: −20 °C is passed **transiently** during ascent, so time-dependent paths
  (compression set, cold flow, embedment) get little time at temperature.
* Verdict: the mechanism is present and arithmetic-positive, but at −20 °C the preload margin
  absorbs it. **LOW.**

### B.2 — Likelihood at −40 °C: **LOW–MODERATE** (MODERATE for the SS-body/Al-panel pairing and
for the pressure-rated duty)

* Contraction delta: **342 ppm** (ΔT = 60 K, Δα = 5.7) — **1.5× the −20 °C case**; 402 ppm at the
  worst end of the alloy band.
* Preload loss: **36–65 % of F0**, i.e. **382–692 N**. Typical pairing: **589 N lost, 479 N
  residual**; worst pairing: **692 N lost, 376 N residual (35 % of F0)**; brass body: 292 N lost,
  420 N residual of 712 N.
* Preload margin collapse against a pressure load: the feedthrough's own rating class is
  pressure-bearing — the hermetic feedthrough catalogue quotes **2500 psig (172 bar) at 20 °C**,
  single-pin **3500 psig (241 bar)** `[S5]`. On the assumed 31.7 mm² bore `[A]` those ratings mean
  a **separating load of 546 N (2500 psig) to 764 N (3500 psig)**. A 589–692 N cold-induced
  preload loss therefore consumes essentially the entire cold margin a pressure-rated mount was
  relying on. In the atmospheric duty instead — the adapter is rated to **45000 ft** `[S1]`,
  where a sealed 1-atm cavity sees ≈**85.5 kPa (12.4 psi)** `[A, derived]` — the separating load
  is only **2.7 N**, so the margin survives; this is why the class is LOW–MODERATE rather than
  high for the atmospheric case.
* Exposure character: −40 °C is a **soak** (hours at float), not a transient — this is the case
  in which the permanent paths of §C get time to act, and the only case in which repeated
  cycling accumulates compression set and cold flow.
* Small compensating factor, stated for completeness: the panel bore contracts onto the body
  (radial squeeze +1.09 µm), and the elastomer's low-temperature limit (−55 °C `[S7]`) is not
  reached, so the elastomer itself is not embrittled at −40 °C — the loss is clamp-load and
  material-history driven, not a frozen-seal failure.
* Verdict: **LOW–MODERATE**; **MODERATE** where the body is stainless in an aluminium panel and
  the mount is cycled repeatedly through −40 °C, or where the joint is relied on at its
  pressure-rated load.

### B.3 — Why the two temperatures differ

1. **Strictly larger contraction delta.** 342 ppm vs 228 ppm (ratio 1.5) — the driving strain
   scales linearly with |ΔT| and nothing else in the chain saturates between the two points.
2. **Preload margin, not preload loss, is what changes class.** Loss goes 37 % → 55 % of F0 for
   the typical pairing: at −20 °C the joint keeps **>57 %** of its clamp in every pairing; at
   −40 °C the worst pairing keeps **35 %** and the typical pairing **45 %**. The step change is
   in the *remaining* margin.
3. **Transient versus soak.** −20 °C is passed in ascent; −40 °C is held for hours at float,
   which is the regime in which the permanent paths (compression set `[S4]`, PTFE cold flow,
   bearing embedment, nut rotation) are exercised at all.
4. **Pairing sensitivity can outweigh the temperature step.** Δα = 3.7 (benign alloy end) gives a
   smaller loss at −40 °C (382 N, 36 %) than Δα = 6.7 gives at −20 °C (461 N, 43 %) — a brass
   body (Δα = 4.0) buys back roughly a third of the −40 °C penalty, and a stainless panel has no
   driving term at either temperature.

---

## (c) REVERSIBILITY

Each identified path is classified, with the reason it is or is not recoverable.

| # | Path | Class | What makes it permanent / why warm-up restores it |
|---|---|---|---|
| **P1** | Elastic differential contraction of a fully metal load path (A.3–A.4) | **REVERSIBLE** | The relation is symmetric in ΔT: on return to +20 °C the differential strain returns to zero and the clamp load returns to F0. The loss stress is 19.6–34.6 MPa on the body cross-section — wholly elastic — so no geometry is lost. Exact reversal holds **only if no other path has acted**. |
| **P2** | Elastomeric gasket compression set (A.5) | **PERMANENT** | Defined as "the permanent deformation of an elastomer after the force which changed its shape has been removed" `[S4]`. The ring does not return to its unstressed cross-section, so the sealing stress that the original geometric squeeze produced is never recovered — even at +20 °C, the loss is in the material and not in the temperature. |
| **P3** | Plastic embedment / yield of the load-bearing faces (panel face under the jam nut, body shoulder) | **PERMANENT** | A plastically flattened bearing face permanently reduces the axial stack height. Warm-up re-expands the panel onto an already-shortened stack, so the original preload cannot be re-established by temperature — the joint re-tightens onto a *shorter* stack. |
| **P4** | Jam-nut rotation / ratcheting under thermal cycling | **PERMANENT** | The mechanism is a change of the nut's angular position, and angular position is not a function of temperature — warm-up does not unwind it. The mount is left loosened as a *position* change, independent of P1–P3. |
| **P5** | Cold flow / creep of a polymer element in the axial path (PTFE, 112–135 ppm/K `[S3]`; driving strain 9.4–14.1 µm over 2 mm, A.7) | **PERMANENT** | Cold flow is non-recoverable deformation under sustained load; the element that carries the largest thermal mismatch in the chain is also the one that cannot spring back. |
| **P6** | Radial contraction of the panel bore onto the body (A.6) | **REVERSIBLE, no loosening** | 0.72–1.09 µm of added radial squeeze; spring-back on warm-up; contributes to tightening, not to loosening. |

**Net classification.** The failure path is reversible **only while it stays purely elastic
(P1)**. Every path that leaves the mount **permanently loosened** is either a deformation path
that survives removal of the load — compression set (P2), plastic embedment (P3), polymer cold
flow (P5) — or a position path that temperature cannot undo (P4). Because both the −20 °C and
the −40 °C excursions drive the *same* differential, the elastic part re-tightens on every
warm-up while the non-elastic part ratchets: the mount's preload therefore need not return to
its initial value even when the temperature does.

---

## (d) CONSEQUENCE CLASS

**Assigned class: Class III — MAJOR, LATENT.** Scale used by this entry (stated because the
register's scale is fixed elsewhere): **Class I** no effect; **Class II** minor, bench-detectable
degradation; **Class III** major — permanent loss of a rated function, latent (no
self-annunciating signal); **Class IV** critical — hazardous or loss of a primary safety
function.

Justification against each function of the feedthrough:

1. **Seal integrity.** The jam-nut clamp is the load path that establishes the static seal's
   squeeze. Its permanent reduction is carried by compression set (P2, `[S4]`) and bearing
   embedment (P3), not by the recoverable thermal term. The seal is the part's raison d'être,
   so its loss is a functional loss, and it is **latent**: a reduced clamp produces no signal
   until ingress has already occurred.
2. **Electrical continuity.** The grounded-shield construction of the feedthrough class carries
   the outer-conductor return through the body-to-panel metal contact `[S6]`, and the RF element
   itself is specified as **50 Ω, VSWR 1.15 max, DC–27 GHz** `[S1]`. A reduced clamp raises and
   destabilises that contact resistance, converting a specified interface into an
   intermittent one — a rated-parameter loss on the electrical function as well as the
   mechanical one. The register's companion entry `[S_in-repo]` additionally records that the
   mated interface is required to be kept free of moisture and that the SMA part's ingress
   rating is quoted in the **mated** condition ("Mated / IP67"), which is precisely the
   condition a loosened mount compromises.
3. **Mechanical retention.** In the assumed single-jam-nut configuration the nut is the only
   axial retention of the feedthrough. Retained capability falls in proportion to residual
   preload: **479 N typical / 376 N worst at −40 °C against 1068–1334 N nominal** `[S2]` — a
   ~55–65 % reduction in the force available to resist cable pull, torque and vibration
   (the adapter is rated for **10 g rms vibration, 20 G / 11 ms shock** `[S1]`).
4. **Pressure / environmental rating breach.** The rated envelope is **−55 °C … +165 °C
   operation, −60 °C … +185 °C storage, 45000 ft altitude, 100 % RH at 35 °C** `[S1]`, and the
   pressure-bearing class is rated **2500 psig (172 bar) at 20 °C**, single-pin **3500 psig
   (241 bar)** `[S5]`. At −40 °C the mount retains **35–64 %** of nominal preload while the
   pressure rating implies a separating load of **546–764 N** on the assumed bore — the cold
   loss consumes the margin the rating depends on. That is a breach at the level of the *rated*
   envelope, which is what places the mode at Class III rather than Class II.

**Why not Class IV:** the item is a panel-mount feedthrough, not the containment boundary of a
hazardous pressure vessel, and no primary safety function is lost — the failure does not become
hazardous, it becomes unreliable and invisible.

**Why not Class II:** the dominant paths are permanent (P2/P3/P5 of §C) and the mode is latent
(no self-annunciating signal); a permanent, undetectable reduction of a rated function is above
a bench-detectable cosmetic degradation in this register's scale.

---

## Assumptions and honest flags

1. The magnitude of the effect is dominated by stated assumptions `[A]`: nut factor K = 0.20,
   thread diameter 6.35 mm, body load area 20 mm², panel bearing area 45 mm², clamped stack
   2 mm, seal cord 1.50 mm at 20 % compression. The sourced inputs are the CTE values `[S3]`,
   the mount torques `[S2]`, the ratio-based squeeze datum `[S4]`, and the temperature/pressure
   ratings `[S1]`, `[S5]`, `[S6]`, `[S7]`.
2. `ΔF = Δα·ΔT / (1/(A_b·E_b) + 1/(A_p·E_p))` and its length-independence for a metal load
   path are `[FIRST-PRINCIPLES]`; the load areas and moduli are assumptions, not sourced.
3. **SU303's own CTE was not read from a datasheet.** The value applied is the austenitic-304
   figure, 17.3 ppm/K `[S3]`; if SU303 differs, the loss scales with the difference.
4. If a compliant element (elastomer, PTFE) carries the axial load, its compliance dominates and
   the *force* loss falls below the tabulated values; the differential then appears primarily as
   a change in seal squeeze, which contraction alone changes by only 0.15–0.23 % of nominal.
5. The standard-atmosphere pressure at 45000 ft (15.8 kPa) is derived from the barometric
   relation `[A]`; `[S1]` supplies the altitude rating itself, not the pressure.
6. The thread series (1/4-36, 6.35 mm) and cord size (1.50 mm) are assumptions; the torque rows
   are quoted as printed for "SMA | Stainless steel" and "SMA | Brass" bulkhead jam nuts `[S2]`.
7. **Low-temperature seal-force data was not located in any source consulted.** `[S4]` states
   its sealing-force guideline values are "at +20 °C" `[S4]`, so the cold sealing-stress margin
   is unquantified by the sources and is not asserted here.
8. No claim is made that this mechanism has been observed on this specific hardware, nor at
   this specific altitude. The entry documents the mechanism, the arithmetic, and the two
   likelihood assessments.
9. The reference part `[S1]` is an SMA feedthrough bulkhead adapter, i.e. the feedthrough class
   named in the entry; the UHV feedthrough `[S6]` and the hermetic feedthrough catalogue `[S5]`
   are cited for their material set and ratings, not as the same part number.

---

## §R References

**[S1] RF-LAMBDA.** *Feedthrough Bulkhead Adapter — Coaxial Adapter, SMA Female to SMA Female*,
part **RFCARASFSFP01A**, drawing **D02-12** (dated JAN 8th 2003).
`rflambda.com/pdf/coaxialadapter/RFCARASFSFP01A.pdf`.
Quoted: "2.1 Opt. Temp. ‑55ºC~+165ºC"; "2.2 Storage Temp. ‑60ºC~+185ºC"; "2.3 Altitude 45000 ft";
"2.4 Vibration 10g rms (15 degree 2KHz)"; "2.5 Humidity 100% RH at 35c, 95%RH at 40 ºc";
"2.6 Shock 20G for 11msc"; material "Stainless Steel SU303"; "Center PIN … Brass with Gold
plating"; "DC‑27 GHz, 50 Ω, VSWR 1.15 max".
*Supplier of the feedthrough's environmental/pressure-relevant ratings and body material.*

**[S2] Centric RF.** *Bulkhead Jamb Nut Torque Recommendations.*
`centricrf.com/coaxial-jamb-nut-torque-recommendations/`.
Quoted rows: "SMA | Stainless steel | 0.437, 0.375 or 0.312 | **12 - 15 in-lbs**";
"SMA | Brass | 0.312 Hex | **8 - 10 in-lbs**".
*Mount (jam-nut) torque figures from which F0 is derived.*
Corroborating SMA torque datum: **Taoglas, "SMA Connector Torque Guide" (APN-25-8-001)**, which
quotes "Brass … **0.57 N-m (5 in-lb)**" and "Stainless Steel … **0.9 N-m (8 in-lb)**" for the
SMA coupling interface.

**[S3] The Engineering ToolBox.** *Coefficients of Linear Thermal Expansion.*
`engineeringtoolbox.com/linear-expansion-coefficients-d_95.html`.
Table unit as printed: "10⁻⁶ m/m °C = 1 μm/m °C". Quoted rows: "Steel Stainless Austenitic
(304) **17.3**"; "(316) **16.0**"; "(310) **14.4**"; "(410) **9.9**"; "Brass **18 - 19**";
"Aluminum **23**"; "Aluminum alloys **21 - 24**"; "Polytetrafluorethylene (PTFE) **112 - 135**";
"Alumina (aluminium oxide, Al2O3) **8.1**"; "Copper **16 - 16.7**".
*The materials reference supplying every CTE value in this entry.*

**[S4] Angst+Pfister.** *O-Rings Technical Guide* (80 pp., PDF), sections "Compression set" and
"Compression table for the most common O-Ring cross-sectional diameters"; design notes
"Force required for cross-sectional deformation".
Quoted: compression set "is tested to **DIN 53517 or ASTM D395 method B**, after **25 %
compression** by storing in air in a hot cabinet, usually for **24 h at +100° C**";
"Compression set is defined as the **permanent deformation of an elastomer** after the force
which changed its shape has been removed"; groove-depth table: cross-section "**1.50**" mm at
"**20**" % compression ⇒ D = 1.20 mm; "These are specific guideline values **at +20°C**".
*The mechanical/sealing datasheet for the gasket path and the permanence criterion.*

**[S5] CeramTec (Ceramaseal).** Hermetic feedthrough catalogue (PDF).
Quoted: "**Temperature Range -269°C to 450°C**"; "**Pressure @ 20°C 2500 PSIG (172 Bar)**";
"**Single pin: 3500 PSIG (241 Bar)**"; "**Insulation: Alumina ceramic**"; "Pressures to
**30,000 psig**".
*The pressure-rating reference for the feedthrough class.*

**[S6] Kurt J. Lesker Company.** *SMA Feedthroughs — CF Flange, Double-Ended*, part numbers
**IFDCG012012 / IFDCF012012** (page served in German).
Quoted: "Temperaturbereich der Kabelsteckverbinder **-65 °C bis 165 °C**" (cable-connector
temperature range −65 °C to +165 °C); "**Vakuum-Anwendung UHV**"; "**700V UND 1 AMP BEWERTUNG
PRO STIFT, 8GHZ**"; conductor material "**Edelstahl**" (stainless steel); insulator material
"**Aluminiumoxid**" (alumina); "Temperatur max. Heizrate **25 °C/Minute**".
*Second feedthrough-vendor source: material set (stainless pin + alumina), UHV service and
temperature range.*

**[S7] ERIKS nv.** *O-ring compound selection* brochure (PDF), compound table.
Quoted: "**Silicone, VMQ | 714177 | 70 | -55 to +230 °C**"; "Fluorosilicone, FVMQ | 614002 | 70 |
-50 to +220 °C"; "Fluorocarbon, FKM … | -20 to +200 °C"; "Teflex … VMQ | -60 to +200 °C".
*The seal elastomer's own temperature rating, used to show the seal material is inside its range
at both −20 °C and −40 °C.*

**[S_in-repo]** `analysis/failure-modes/sma-coax-interface-citations.md`, §S1 (MIL-PRF-39012F
Table I: PTFE fluorocarbon insulator material) and §S3 (HUBER+SUHNER SMA part datasheet:
"Environmental data → Ingress protection (IP Rating) — Mated / **IP67**"; "Operation temperature
**−65 °C … 165 °C**"). *In-register cross-reference only; not a source for any figure quoted in
this entry's arithmetic.*

**Companion artifact:** `analysis/failure-modes/feedthrough_mount_thermal_calc.py`
(deterministic, stdlib only) and its frozen output
`analysis/failure-modes/feedthrough_mount_thermal_calc.out`, which reproduces every number in
§A and §B.
