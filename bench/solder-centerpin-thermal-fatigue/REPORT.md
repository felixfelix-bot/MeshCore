# Solder-joint and center-pin thermal-fatigue failure modes at -20 C / -40 C

Task (fleet card, ID not stated in the task body): "Analyze solder-joint and
center-pin thermal-fatigue failure modes. Produce a structured failure-mode
catalogue entry set for solder joints and center-pin conductors under -20C
and -40C thermal cycling. Cover explicitly: (1) CTE mismatch across the
joint stack (brass or steel center pin, PTFE dielectric, coax jacket/outer
conductor); (2) cyclic thermal fatigue leading to an open or
high-resistance joint; (3) the specific order-of-magnitude of CTE mismatch
between the pin alloy and PTFE and what that implies for shear at the
joint."

Date: 2026-09-15 · Repo: meshcore (main) · Worker: dq05 (profile
worker-heavy) · Host: `c03rad0r-DQ05proplus`.
Artifacts: this directory (`bench/solder-centerpin-thermal-fatigue/`):
`REPORT.md` (this file), `fatigue_arithmetic.py` (stdlib-only recompute of
every number quoted here), `output.txt` (verbatim capture, rerun
byte-identical).

**Scope discipline:** per the acceptance criteria this report contains NO
mitigation recommendations. Section 6 records only which UNVERIFIED values
block tighter quantification.

**Card-ID note:** the task body does not state the fleet card ID. No
NSEC on this host (standing fleet norm) → no kanban comment possible;
the comment body is delivered in the worker's reply for the dispatcher
to attach.

**Provenance convention (unchanged from sibling reports):** COMMITTED =
value in a prior bench report with its own source table; VERBATIM =
quoted from a project file read this session; INDUSTRY-TYPICAL =
standard material data with no datasheet on host (no outbound fetch per
standing operator constraint), labeled UNVERIFIED; COMPUTED = arithmetic
shown in `fatigue_arithmetic.py` and reproduced in `output.txt`.

---

## VERDICT SUMMARY

1. **The center pin is a variant-B object.** In the PRIMARY (over-the-air)
   path there is no coaxial center pin in the RF path at all: the DUT's RF
   exits are soldered wire dipoles on bare castellated pads, and the only
   cable crossing the boundary is USB-C serial (`0b7bfe92`, HIGH — 4
   concordant document records). Center-pin and coax-termination modes
   below therefore apply to the OPTIONAL conducted path (2x RG316 +
   SMA bulkhead, MUST-PROCURE per BOM `55585471` 3b) or to any future
   pigtail soldered to LR2021 pad 9. DUT-side SOLDER joints, by contrast,
   exist in BOTH variants and see the full chamber swing.
2. **Order-of-magnitude answer (task item 3): PTFE expands ~6x faster
   than the pin alloy.** CTE: brass ~19, stainless ~17 (COMMITTED,
   `65c9c3df`, HIGH) vs PTFE ~100-135 ppm/K (INDUSTRY-TYPICAL, UNVERIFIED)
   → ratio 5.3-7.9x, ~6x as the order of magnitude. What that implies for
   shear at the joint: **not stress — micro-slip.** A fully-clamped
   differential strain over the 65 K swing would load the pin to
   640 MPa (brass) / 1236 MPa (stainless) (COMPUTED) — above any pin
   alloy's yield — so the stack cannot and does not stay clamped. The
   softest member relieves: PTFE, modulus ~200x lower than brass
   (INDUSTRY-TYPICAL, UNVERIFIED), with flow strength ~7-25 MPa against a
   delivered interface stress bound of only ~3.2 MPa (COMPUTED). The ~6x
   mismatch is spent as µm-scale slip (32 µm axial over a 5 mm bead,
   6.4 µm diametral at a 1 mm bore radius, 65 K — COMPUTED), not as shear
   delivered into the pin or its solder joint.
3. **The primary-path solder joints have no CTE-fatigue strain source.**
   The wire dipoles are copper wire on copper pads — dCTE ≈ 0, cyclic
   shear ≈ 0 (COMPUTED, Section 3.3). The joints that DO see cyclic shear
   are the FR4-attached ones (LR2021 castellated pads to carrier, USB-C
   anchor, and — F33 board only — SMA edge-launch, which is NOT the DUT
   per the `0b7bfe92` correction) and the variant-B center-pin solder
   terminations. Worst case (Cu vs FR-4, dCTE 4 ppm/K in-plane, 0.5-1.0 mm
   effective length, 0.1 mm meniscus): cyclic shear strain 0.09-0.26 %
   per 65 K cycle vs SAC's elastic shear limit ~0.10 % (COMPUTED from
   INDUSTRY-TYPICAL inputs) — above threshold at the warm end of the
   cycle, marginally.
4. **Likelihood is LOW at both setpoints because the cycle count is 3
   orders of magnitude below the fatigue class.** SAC fatigue at this ΔT
   is a thousands-of-cycles class (Coffin-Manson exponent ~2, `04db4fae`
   2.10); the campaign plans ~3-4 cycles per run-day (`72f3aab9` via
   `04db4fae`) = 0.3-0.4 % of a 1000-cycle floor per run-day (COMPUTED).
   The -40 C cycle carries 2.09x the damage of the -20 C cycle by ΔT²
   (COMPUTED) — worse in degree, same regime, chain-consistent with
   `04db4fae` FM-10 (LOW / LOW-MEDIUM).
5. **The cold end is not where fatigue damage accrues.** At -40 C SAC sits
   at T/Tm ≈ 0.476 — below the ~0.5 creep threshold, cold half-cycle
   essentially elastic — and SAC's ductile-to-brittle transition is
   "well below -40 C" (`65c9c3df` 3c, VERBATIM), so no embrittlement
   screen fires at either setpoint. Damage (creep/relaxation + any plastic
   shear) accrues at the WARM end of every cycle (T/Tm up to 0.608 at
   +25 C, COMPUTED). "Colder" buys a larger strain range, not a more
   fragile joint.
6. **The realistic joint-killer in this campaign is not fatigue — it is
   ice.** Moisture supply is certain at both setpoints (`65c9c3df`,
   HIGH): the +9 % freeze expansion acting at an already-stressed or
   contaminated meniscus (`65c9c3df` 3c) cracks joints at cycle counts
   where fatigue cannot. Gated by water actually reaching the joint
   (sealed-bag protocol on the DUT; mated interfaces on variant B).
7. **Nothing here is measured.** No run has occurred, no DUT attached,
   no chamber exists (`65c9c3df` caveat, `fe700201`, `ec80c11e` concur).
   All likelihoods are physics priors. No value is fabricated; every
   number below is COMMITTED / VERBATIM / INDUSTRY-TYPICAL-labeled /
   COMPUTED with visible arithmetic.

---

## 0. Where solder joints and center pins actually exist

Joint inventory from the on-record hardware chain (`0b7bfe92`, `55585471`,
`fe700201`, `65c9c3df`):

| # | Joint / conductor | Stack across the joint | Exists today | Path |
|---|---|---|---|---|
| J1 | LR2021 castellated pads → carrier/wiring (18-pin module) | SAC / Cu pad / FR-4 in-plane 13-17, z 45-70 | YES (4 modules on hand) | A+B |
| J2 | Wire-dipole solder joints (16.4 cm / 3.1 cm Cu wire → module pad) | SAC / Cu wire / Cu pad — dCTE ≈ 0 | YES (document-based; as-built UNVERIFIED) | A+B |
| J3 | USB-C receptacle anchors (the only boundary-crossing cable, primary path) | SAC / Cu / FR-4 + SS shield | YES | A+B |
| J4 | SMA edge-launch J1/J2 (brass body → FR-4) | SAC / brass ~19 / FR-4 13-17 ip, 45-70 z | NO — on hub_board_f33 (F33 module), NOT the LR2021 DUT (`0b7bfe92` correction) | neither (conditional) |
| J5 | RG316 SMA plug center-pin termination (Cu conductor ↔ pin) | SAC or crimp / Cu / brass or stainless pin | NO — RG316 MUST-PROCURE (`55585471` 3b) | B only |
| J6 | SMA bulkhead jack-jack center pin in PTFE bead (Amphenol 132134-class) | brass or stainless pin / PTFE ~100-135 / brass body — NO solder, machined capture | NO — MUST-PROCURE | B only |
| J7 | RG316 braid → plug outer conductor (crimp/solder) | Cu braid / brass, under jacket | NO — MUST-PROCURE | B only |

Thermal cycle definition (COMMITTED): 4 setpoints +25/0/-20/-40 C, ~3-4
ramps per session, 10-min holds (`72f3aab9` via `04db4fae` 0). Swing seen
by every joint: 45 K per -20 C visit, 65 K per -40 C visit, both from a
+25 C assembly/lab state. Ramp rates are slow (heating 3.0, cooling 1.5,
feedthrough-derated 1.05 C/min — `472922d4`, planning estimates, LOW
confidence): gradient across the 19.72 mm module at 1.05 K/min is ~0.4 mK
(COMPUTED) — no thermal-shock term exists anywhere in this catalogue;
all modes below are strain-driven, not shock-driven.

---

## 1. MASTER TABLE (acceptance deliverable)

Path: A = primary OTA (no center pin exists), B = optional conducted
(MUST-PROCURE). Likelihood scale: CERTAIN / HIGH / MEDIUM / LOW /
NEGLIGIBLE / N-A (path does not exist). Consequence classes per the task:
DATA (corrupts measurement data only), DEGRADE (degrades hardware),
DESTROY (destroys hardware).

| # | ID | Failure mode | Task item | Path | -20 C | -40 C | Reversible? | Consequence class |
|---|---|---|---|---|---|---|---|---|
| 1 | SF-1 | Pin-vs-PTFE diametral gap cycling in the bulkhead bead | (1) | B | CERTAIN (small) | CERTAIN (small, 1.4x) | Reversible | DATA only |
| 2 | SF-2 | Pin axial micro-slip / setback drift in the bead | (1) | B | CERTAIN (small) | CERTAIN (small, 1.4x) | Reversible | DATA only |
| 3 | SF-3 | Solder-joint cyclic CTE-mismatch shear fatigue → crack → intermittent high-R → open | (2) | A (J1-J3) + B (J5, J7) | LOW | LOW-MEDIUM | PERMANENT when it occurs | DEGRADE (+DATA precursor) |
| 4 | SF-4 | Termination axial-strain cycling: jacket/outer vs center stack | (1) | B | MEDIUM-LOW | MEDIUM | Jacket recovers; stretched/cracked termination PERMANENT | DEGRADE (+DATA) |
| 5 | SF-5 | PTFE bead cold-flow / clamp-relief under cyclic pinch | (3) | B | LOW | LOW | Permanent accumulation (slow) | DEGRADE |
| 6 | SF-6 | Ice-expansion (+9 %) loading at a marginal/contaminated solder meniscus | (2)-adjacent | A+B | MEDIUM (gated by moisture reaching joint) | MEDIUM (more mass, harder ice) | PERMANENT (cracked meniscus) | DEGRADE (+DATA) |
| 7 | SF-7 | Solder low-temperature embrittlement (DBTT screen) | (2) | A+B | NEGLIGIBLE | NEGLIGIBLE | N/A | (DEGRADE/DESTROY if it occurred — screened out) |

---

## 2. Per-entry detail (a-d attributes per acceptance)

### 2.1 SF-1 — Pin-vs-PTFE diametral gap cycling (task item 1)

- **(a) Mechanism (material properties).** The bulkhead center pin (brass
  ~19 / stainless ~17 ppm/K, COMMITTED `65c9c3df`) floats in a PTFE
  dielectric bead (~100-135 ppm/K, INDUSTRY-TYPICAL UNVERIFIED; er ~2.1,
  Tg -97 C, COMMITTED `65c9c3df`). On cooldown the bead shrinks ~6x more
  than the pin it captures: differential diametral strain over the swing
  = 4.4 µm at a 1 mm bore radius for -20 C (45 K), 6.4 µm for -40 C
  (65 K) (COMPUTED). The RF consequence is a small cyclic change in the
  bead's effective bore → impedance/discontinuity modulation of the
  interface region — the same class of effect as the frost-film modes in
  `04db4fae` FM-2, but mechanically driven and fully deterministic.
- **(b) Likelihood -20 vs -40.** CERTAIN (small) at both — it is
  geometry, guaranteed by the CTE values; magnitude scales linearly with
  ΔT, so -40 C is ~1.4x the -20 C displacement. Below any solder-fatigue
  consideration: no solder is in this stack (machined capture, J6).
- **(c) Reversible.** Fully — the gap reopens to its warm dimension on
  warm-up; no hysteresis mechanism exists below bead damage (SF-5).
- **(d) Consequence class.** DATA only. For the decode-count edgescan it
  is absorbed by the ~165 dB link budget (`55585471` step 5); for any
  future phase/power-quantitative variant it is a small cyclic S11/IL
  term at the interface (same boundary as `04db4fae` 2.6's calibration
  answer).

### 2.2 SF-2 — Pin axial micro-slip / setback drift (task item 1)

- **(a) Mechanism.** The same ~6x mismatch acts axially: over a 5 mm
  SMA-class bead the pin-bead pair accumulates 22 µm (-20 C cycle) to
  32 µm (-40 C cycle) of relative axial displacement per swing (COMPUTED).
  Because PTFE cannot clamp the pin (see Section 3 — the compliant-member
  bound), the pin is free to track its own contraction, changing pin
  protrusion/setback at the mating plane by µm-scale amounts, and
  relaxing any friction-capture preload a little each cold excursion.
- **(b) Likelihood -20 vs -40.** CERTAIN (small) both; 1.4x displacement
  at -40 C. Not a fatigue mode at campaign cycle counts (µm slip on a
  ground/machined seat, no strain concentration).
- **(c) Reversible.** Displacement reverses with temperature. The
  preload-relaxation component is ratcheting in principle — but at 3-4
  cycles/run-day vs a slip seat designed for mate/demate cycling, the
  ratchet is not resolvable (folded into SF-5 for the bead itself).
- **(d) Consequence class.** DATA only (mating-plane reference drift,
  same class as `04db4fae` FM-5's torque-loss mode, which it feeds).

### 2.3 SF-3 — Solder-joint cyclic shear fatigue → open / high-resistance joint (task item 2, central entry)

- **(a) Mechanism.** Every solder joint whose two sides have different
  CTEs sees a shear strain cycle Δγ = Δα·ΔT·(L/h) each swing (L =
  distance from the strain-neutral point, h = meniscus/joint height).
  Stacks on record (COMMITTED/INDUSTRY-TYPICAL per Section 4):
  - J1/J3 (Cu vs FR-4): dCTE 0-4 ppm/K in-plane (z-axis 45-70, but the
    relevant in-plane term for pad joints) → Δγ 0.09-0.26 % per 65 K
    cycle at L = 0.5-1.0 mm, h = 0.1 mm (COMPUTED);
  - J5 (variant B center-pin termination, Cu conductor vs brass/stainless
    pin): dCTE 0-2 ppm/K → Δγ 0-0.13 % per 65 K cycle (COMPUTED);
  - J2 (wire dipole, Cu-on-Cu): dCTE ≈ 0 → Δγ ≈ 0 — **the primary-path
    RF joints have no cyclic strain source from CTE mismatch at all**;
  - J4 (SMA edge-launch, F33 board only): brass vs FR-4 — the classic
    connector fatigue stack, but not this DUT (`0b7bfe92`).
  SAC's elastic shear limit is ~0.10 % (COMPUTED from E ~45 GPa, yield
  ~28 MPa, INDUSTRY-TYPICAL UNVERIFIED): the worst FR-4 joints exceed it
  at the warm end of a -40 C cycle; pin-termination joints sit at/below
  it; dipole joints are at zero. Where Δγ exceeds the elastic limit,
  plastic shear at the warm end + relaxation during the 10-min holds
  (T/Tm 0.52-0.61 ≥ 0.5 creep threshold, COMPUTED) accumulates
  Coffin-Manson damage; crack initiation → crack growth → intermittent
  high-resistance (visible as serial dropouts / decode-count noise)
  → open joint. Precursor order is exactly the task's phrase: cyclic
  fatigue → high-R → open.
- **(b) Likelihood -20 vs -40.** LOW at -20 (45 K swing) / LOW-MEDIUM at
  -40 (65 K swing — 2.09x damage per cycle by the ΔT² scaling `04db4fae`
  2.10 uses as its conservative bound; 1.44x by strain-range). Both far
  below threshold in CYCLE COUNT: SAC fatigue at this strain range is a
  thousands-of-cycles class (`04db4fae` 2.10, COMMITTED); the campaign
  plans ~3-4 cycles/run-day = 0.3-0.4 % of even a 1000-cycle floor
  (COMPUTED). Even at -40 C, a sound joint cannot nucleate a measurable
  crack in one campaign; a MARGINAL joint (cold solder, contaminated
  meniscus, pre-stressed from dipole handling) can crack earlier — but
  the driver for marginal joints at cold is SF-6, not fatigue. Note the
  fatigue threshold explicitly: at -40 C the joint's cold half-cycle is
  BELOW the creep threshold (T/Tm 0.476 < 0.5, COMPUTED) and SAC has no
  embrittlement there (SF-7) — the -40 excursion adds strain range, not
  fragility; damage accrues warm.
- **(c) Reversible.** NO — fatigue cracking is permanent and progressive.
  The intermittent-high-R precursor is transient in appearance but the
  underlying crack is monotonic.
- **(d) Consequence class.** DEGRADE (the joint is permanently damaged;
  hardware function lost at the joint) with a DATA precursor (intermittent
  high-R corrupts decode counts / serial before the open). It does not
  DESTROY hardware: the failed joint disables a path; it does not take
  other hardware with it (contrast `04db4fae` FM-4's USB-C VBUS short,
  the campaign's only destruction-class mode).

### 2.4 SF-4 — Termination axial-strain cycling: jacket/outer vs center stack (task item 1)

- **(a) Mechanism.** A coax termination is a strain-gauge stack in
  series: jacket (fluoropolymer/PVC-class CTE ~70-140 ppm/K,
  INDUSTRY-TYPICAL UNVERIFIED) + braided outer conductor (Cu) + PTFE
  dielectric + Cu center conductor (all ~17-135 ppm/K per Section 4).
  On cooldown the jacket and dielectric contract several times more than
  the metal members and the jacket STIFFENS (`04db4fae` FM-8, HIGH at
  tight routing); the contraction mismatch appears as axial load on the
  plug termination: the braid/outer crimp or solder (J7) and the center-pin
  joint (J5) carry the difference. Cyclic repetition fatigues the
  termination the same way SF-3 fatigues a shear joint, plus a
  one-time-per-route risk of a shield kink at a below-minimum bend
  (RG316 min bend radius 12.7 mm, INDUSTRY NOMINAL UNVERIFIED, `fe700201`
  2b; `04db4fae` FM-8).
- **(b) Likelihood -20 vs -40.** MEDIUM-LOW at -20 / MEDIUM at -40:
  both scale with ΔT (contraction and stiffness), and -40 C rides the
  stiffening regime `04db4fae` FM-8 flags HIGH. Gated by routing: free
  cable with slack sees near-zero axial load; tight routing sees real
  load. No chamber/routing exists yet (`fe700201`), so the gate value
  is UNKNOWN — the rating spans the recorded range.
- **(c) Reversible.** The elastic load reverses each warm-up; the
  consequences (stretched braid, loosened crimp, fatigued solder,
  kinked shield) are PERMANENT.
- **(d) Consequence class.** DEGRADE (+DATA for any quantitative variant:
  a shield kink is an impedance bump, `04db4fae` FM-8).

### 2.5 SF-5 — PTFE bead cold-flow / clamp-relief (task item 3, shear implication)

- **(a) Mechanism.** This entry records what the ~6x mismatch does NOT
  do. If the bead clamped the pin, the fully-clamped stress over 65 K
  would be 640 MPa (brass) / 1236 MPa (stainless) (COMPUTED) — above any
  pin yield, so clamping is physically impossible; the stack relieves
  through the softest member. PTFE's modulus is ~200x below brass
  (INDUSTRY-TYPICAL UNVERIFIED) and its flow/shear strength is ~7-25 MPa
  against a delivered interface stress bound of ~3.2 MPa (COMPUTED):
  the interface slips/creeps at low stress instead of storing load. The
  residual mechanism is PTFE cold flow: sustained below-yield stress,
  repeated each cold excursion, deforms the bead bore permanently at the
  pin capture points — a slow dimensional drift of the RF geometry.
- **(b) Likelihood -20 vs -40.** LOW both: the delivered stress (~3.2 MPa
  at 65 K, ~2.2 MPa at 45 K, COMPUTED) sits below the flow-strength class
  even at the -40 C end; PTFE is above Tg (-97 C) and remains ductile at
  both setpoints (COMMITTED `65c9c3df` 3b). Flow is a
  many-thousands-of-cycles accumulator; the campaign spends 3-4.
- **(c) Reversible.** Cold flow is PERMANENT (viscous deformation, not
  elastic). Magnitude at campaign cycle counts: unmeasurably small.
- **(d) Consequence class.** DEGRADE (bead geometry drift) — the slowest
  hardware-degradation term in this catalogue; no data impact at the
  decode-count protocol's margins.

### 2.6 SF-6 — Ice-expansion loading at a marginal solder meniscus (task item 2-adjacent, the realistic joint-killer)

- **(a) Mechanism.** Water freezing expands ~9 % by volume (COMMITTED
  `65c9c3df`); a film of water in a board joint's meniscus crevice or
  under a connector body exerts wedging stress on freeze. At a SOUND
  joint this is survivable; at a marginal one (cold joint, contaminated
  or pre-cracked meniscus, castellated-pad joint already stressed by
  dipole wire flexure) the wedge opens the crack — "the ice expansion can
  stress the joint... can crack the joint if the joint is already
  stressed" (`65c9c3df` 3c, VERBATIM). Each freeze/thaw with ionic
  contamination also accelerates corrosion at the joint (`65c9c3df` 3c).
  This is the mechanism that actually cracks solder at cycle counts the
  campaign will experience; pure CTE fatigue (SF-3) will not.
- **(b) Likelihood -20 vs -40.** MEDIUM both, gated NOT by temperature
  but by water reaching the joint: on the DUT by sealed-bag integrity
  (`04db4fae` FM-4), on variant B by interface exposure (FM-2/FM-3).
  At -40 C more water has deposited, it stays frozen through the hold
  (no transient melt near 0 C), and the ice is mechanically harder
  (`65c9c3df` 2d) — worse in degree, same gate.
- **(c) Reversible.** The ice is; the cracked meniscus is PERMANENT.
- **(d) Consequence class.** DEGRADE (+DATA: the cracked joint is an
  intermittent high-R/open — the same serial/decode corruption as
  SF-3's end state, arriving by a different mechanism).

### 2.7 SF-7 — Solder low-temperature embrittlement screen (task item 2, "below solder fatigue threshold" resolved)

- **(a) Mechanism.** Candidate mechanism: SAC crossing a ductile-to-
  brittle transition at cold, cracking under shock. Material answer:
  SAC's ductile-to-brittle transition is "well below -40 C"
  (`65c9c3df` 3c, VERBATIM, COMMITTED); at -40 C SAC is at T/Tm ≈ 0.476
  — still a ductile metal, no DBTT to cross at either setpoint. The
  campaign's ramp rates (1.05-3.0 C/min, `472922d4`) additionally
  produce no thermal shock anywhere (0.4 mK across the module,
  COMPUTED).
- **(b) Likelihood -20 vs -40.** NEGLIGIBLE at both — screened out by
  material data, not by cycle count. This entry exists to answer the
  "below solder fatigue threshold" question explicitly for BOTH senses:
  no cold embrittlement threshold is crossed, and the cold half-cycle is
  below the creep threshold (T/Tm < 0.5, COMPUTED).
- **(c) Reversible.** N/A (no mechanism fires).
- **(d) Consequence class.** None while screened out; had it existed it
  would be DEGRADE-to-DESTROY. Recorded so the mitigation task does not
  spend effort on it.

---

## 3. Order-of-magnitude analysis (task item 3, explicit)

### 3.1 The mismatch

CTE: brass ~19, stainless ~17 ppm/K (COMMITTED `65c9c3df` sources table,
HIGH) — vs PTFE ~100-135 ppm/K (INDUSTRY-TYPICAL UNVERIFIED, `04db4fae`
2.10; er 2.1 / Tg -97 C / <0.01 % moisture / tempco ~200 ppm/K COMMITTED
`65c9c3df`).

- Ratio PTFE/pin: **5.3-7.9x → order of magnitude ~6x** (COMPUTED).
- Absolute mismatch: dCTE 81-118 ppm/K depending on pin alloy and where
  in the PTFE range; the brass-vs-stainless pin choice moves it by only
  2 ppm/K — a second-order term (COMPUTED).
- Differential free strain per swing: 0.44 % (45 K) / 0.64 % (65 K);
  32 µm axial slip over a 5 mm bead, 6.4 µm diametral at 1 mm bore
  radius at -40 C (COMPUTED).

### 3.2 What it implies for shear at the joint — the compliant-member bound

A fully-clamped stack would develop σ = E·Δα·ΔT: 640 MPa in the brass pin,
1236 MPa in stainless, at the -40 C swing (COMPUTED) — above yield for
any pin alloy (brass yield ~350-500 MPa class, INDUSTRY-TYPICAL
UNVERIFIED). Conclusion chain:

1. The stack cannot stay clamped → it must relieve.
2. The relieving member is the softest: PTFE, modulus ~200x below brass.
3. The stress the mismatch can actually deliver is bounded by what PTFE
   can sustain before flowing: ~3.2 MPa at the interface (COMPUTED) —
   BELOW PTFE's ~7-25 MPa flow-strength class (INDUSTRY-TYPICAL
   UNVERIFIED).
4. Therefore the ~6x mismatch is spent as **µm-scale micro-slip** at the
   pin/PTFE interface (SF-1/SF-2), **not as shear stress delivered into
   the pin or its solder joint**. The pin arrives at its solder joint
   nearly stress-free axially; the joint's own CTE pair (SF-3) is what
   fatigues it, and that pair's mismatch is 0-4 ppm/K — an order of
   magnitude smaller than the pin/PTFE pair.

### 3.3 Cross-check per joint (COMPUTED, Section 4 of `output.txt`)

| Joint pair | dCTE (ppm/K) | Δγ per 65 K cycle, L 0.5-1.0 mm, h 0.1 mm | vs SAC elastic limit ~0.10 % |
|---|---|---|---|
| Cu wire on Cu pad (dipole, J2 — primary path) | ~0 | ~0 | below — no strain source |
| Cu vs FR-4 in-plane (J1/J3) | 0-4 | 0-0.26 % | worst case ABOVE at warm end |
| Cu vs brass/stainless pin (J5) | 0-2 | 0-0.13 % | at/below |
| PTFE vs SAC (the bead's own capture, no solder) | ~75-114 | n/a (no joint) | relieved by slip (SF-5) |
| Pin vs PTFE (J6) | 81-118 | n/a (no joint — machined capture) | slip, not shear (SF-1/2) |

---

## 4. Sources (numbers, per acceptance)

| # | Claim + number | Source | Status |
|---|---|---|---|
| 1 | Pin-alloy CTE: stainless ~17, brass ~19 ppm/K | `bench/condensation-risk/REPORT.md` sources table (commit `65c9c3df`) | COMMITTED, HIGH |
| 2 | Solder-alloy CTE: SAC ~21-25 ppm/K; Cu ~17; FR-4 in-plane 13-17 / z 45-70; PTFE ~100-135 ppm/K | `bench/cable-feedthrough-failure-modes/REPORT.md` 2.10 + 5 (commit `04db4fae`) | COMMITTED, labeled INDUSTRY-TYPICAL UNVERIFIED there |
| 3 | SAC fatigue class: Coffin-Manson, "thousands-of-cycles class (exponent ~2)" at this ΔT; campaign ~3-4 cycles/run-day; LOW / LOW-MEDIUM at -20 / -40; ΔT² scaling 2.09x | `04db4fae` FM-10 + 2.10 + `72f3aab9` card spec | COMMITTED |
| 4 | PTFE: Tg -97 C (ductile at both setpoints), er ~2.1, moisture <0.01 %, tempco ~200 ppm/K; ice +9 % expansion, resistivity 10^7-10^8 Ω·m; "ice expansion can stress the joint... can crack the joint if the joint is already stressed"; SAC DBTT "well below -40 C" | `bench/condensation-risk/REPORT.md` 3b/3c (commit `65c9c3df`) | COMMITTED, HIGH (3c VERBATIM) |
| 5 | Coax thermal-cycle reliability note: "both [RG316/RG178] are rated to -40 C (PTFE dielectric)"; RG316 loss ~0.3 dB/m at 1 GHz; RG316 + SMA bulkhead + torque wrench all MUST-PROCURE | `bench/rf-feedthrough-bom/REPORT.md` 4.2/5/3b (commit `55585471`) | COMMITTED (rating claim is the project's own; vendor datasheet UNVERIFIED) |
| 6 | Coax cold reliability modes: jacket stiffening HIGH at tight routing (FM-8); bend radius 12.7 mm INDUSTRY NOMINAL; bulk cable tempco CERTAIN-small (FM-7); RG316 OD 2.5 mm | `04db4fae` 2.7/2.8 + `bench/chamber-feedthrough-fit/REPORT.md` 2 (commit `fe700201`) | COMMITTED |
| 7 | DUT joint inventory: RF exits are soldered wire dipoles on bare castellated pads (no connector); F33-board SMA is a different board/module; USB-C is the only boundary cable in the primary path | `bench/dut-rf-ports/REPORT.md` (commit `0b7bfe92`) | COMMITTED, document-based HIGH |
| 8 | Ramp rates: heating 3.0 / cooling 1.5 / derated 1.05 C/min (planning estimates, LOW confidence); deepest ramp 19.0 min cross-check | `bench/chamber-ramp-rates/REPORT.md` (commit `472922d4`) | COMMITTED |
| 9 | Elastic moduli E: brass ~100 GPa, stainless ~193 GPa, PTFE ~0.5 GPa, SAC ~45 GPa; SAC yield ~28 MPa RT, Tm ~490 K; brass yield ~350-500 MPa; PTFE flow strength ~7-25 MPa; creep threshold T/Tm ≈ 0.5 | standard material data | INDUSTRY-TYPICAL, **UNVERIFIED on host** |
| 10 | All ratios, strains, µm slips, stresses, Δγ, T/Tm values in Sections 2-3 | `fatigue_arithmetic.py` → `output.txt` (this directory) | COMPUTED, rerun byte-identical |

Two-source acceptance: sources #1 (pin-alloy CTE, numbers) and #2
(solder-alloy CTE, numbers) are the required pair; #4 and #5 carry the
material-mechanism and coax-cycle reliability numbers respectively.

---

## 5. Caveats and honest gaps

1. **No PTFE, no pin, no coax, no DUT is on hand.** No chamber exists
   (`fe700201`, `ec80c11e`, `24eb918c` concur); the RG316/bulkhead chain
   is MUST-PROCURE (`55585471`); the DUT is not attached (`0b7bfe92`).
   Every part-specific number is INDUSTRY-TYPICAL and must be replaced by
   the procured parts' datasheets.
2. **As-built solder state UNVERIFIED.** Joint quality (cold joints,
   meniscus geometry, flux residue) determines whether SF-6's "already
   stressed" condition holds; no physical inspection has ever been
   performed (board never attached, no photo on record — `0b7bfe92` U1).
3. **Likelihoods are physics priors**, not observations — no run has
   occurred (`65c9c3df` caveat 4). They assume the moisture supply the
   dew-point grid established (CERTAIN at both setpoints) and zero
   mitigation.
4. **The solder alloy itself is UNVERIFIED on record.** Hand-wired
   prototype joints could be SAC or SnPb; SnPb (CTE ~25 ppm/K similar;
   BETTER low-cycle fatigue ductility, INDUSTRY-TYPICAL) would only lower
   SF-3's likelihood. The catalogue's conclusions do not hinge on the
   choice; the flag is carried for honesty.
5. **Fatigue-life quantification is deliberately coarse.** The
   thousands-of-cycles class is used as an order-of-magnitude floor, not
   a prediction — no Engelmaier constants, no joint-geometry
   finite-element work exists on any record, and none is needed to answer
   the 3-4-cycle campaign question (0.3-0.4 % utilization).

---

## 6. Nothing fabricated / handoff note

Every number is COMMITTED (prior bench reports with source tables),
VERBATIM (project files quoted), INDUSTRY-TYPICAL (labeled UNVERIFIED), or
COMPUTED (arithmetic in `fatigue_arithmetic.py`, reproduced in
`output.txt`). No run, chamber, cable, or joint was inspected because none
exists/occurred; nothing was simulated; no mitigation is recommended
anywhere, per the acceptance criteria.

Handoff (what blocks tighter quantification — not how to fix it): the
procured RG316/bulkhead datasheets (jacket polymer CTE, pin alloy
identity, termination type solder-vs-crimp), the as-built joint inspection
(SF-6's "already stressed" gate), and any future phase-quantitative
variant decision (SF-1/SF-2 relevance). Fleet consumers: `04db4fae`'s
mitigation task should treat SF-3/SF-6 as one merged target (joint
integrity) and can spend zero effort on SF-7 (screened out) and SF-5
(3 orders below its accumulation regime).