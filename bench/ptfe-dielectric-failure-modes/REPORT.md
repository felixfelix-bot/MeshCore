# PTFE cable-dielectric failure-mode catalogue: moisture uptake + -20/-40 C thermal cycling

Task (fleet card, ID not stated in the task body): "Analyze PTFE dielectric
moisture and thermal-cycle failure modes. Produce a structured failure-mode
catalogue entry set for the PTFE cable dielectric under moisture uptake and
repeated -20 C to -40 C thermal cycling."

Date: 2026-09-15 · Repo: meshcore (main) · Worker: dq05 (profile
worker-heavy) · Host: `c03rad0r-DQ05proplus`.
Artifacts: this directory (`bench/ptfe-dielectric-failure-modes/`):
this report, `ptfe_dielectric_calc.py` (all arithmetic, stdlib only,
reproducible), `output.txt` (saved script output, the numbers cited below).

**Card-ID note:** the task body does not state the fleet card ID. A
fleet-state lookup to recover it was operator-denied in a prior session
(recorded in `04db4fae` section 6.6, not retried). No kanban comment
possible (no NSEC on this host — standing fleet norm).

**Scope discipline:** per the acceptance criteria, this report contains
NO mitigation recommendations. Section 8 lists only cross-links and
record corrections.

**Relationship to the prior catalogue:** `04db4fae`
(`bench/cable-feedthrough-failure-modes/`) covered the PTFE dielectric in
one entry (FM-11, four lines). This report is the dedicated deep-dive the
new card asks for: 7 entries with full per-entry attributes, computed
bounds, and explicit drift-vs-jump classification. It supersedes FM-11's
*depth* but not its verdict (verdicts agree; one flagged discrepancy is
corrected in Section 8, Entry 5).

---

## VERDICT SUMMARY

1. **The PTFE dielectric in this campaign exists only in the planned
   (variant B) conducted path** — the 0.15 m + 0.50 m RG316 segments
   (solid PTFE dielectric, er ~2.1) and the SMA bulkhead feedthrough's
   PTFE bead. Both are MUST-PROCURE, not on hand, never cycled
   (`55585471` 3b, `fe700201` 2a, `0b7bfe92`). The primary OTA path
   (variant A) contains NO coax PTFE dielectric in the measured path
   (wire dipoles, air dielectric, `0b7bfe92`).
2. **Bulk moisture uptake in the PTFE is electrically negligible even at
   the datasheet-class saturation max** (<0.01 wt% absorption ->
   dVF/VF -0.0305 %, phase <=0.30 deg over the full 0.65 m path at
   868 MHz, computed), and the campaign cannot approach that max: water
   diffusivity in PTFE makes the axial path dead (tau ~70-7100 yr for
   0.15 m) and the radial path requires a shield+jacket breach (tau
   10 h-42 d even if breached, longer cold). **Reversible, no
   cycle-accumulation, slow-drift class, zero impact on the primary
   decode-count measurement.**
3. **Surface adsorption/frost at exposed PTFE faces (the bulkhead bead
   gap, termination faces) is the only moisture effect with real
   magnitude** — an er ~3.2 lossy frost volume in the interface region.
   It is reversible (dries) but *time-varying during a run*, which makes
   it drift-UNTRACKABLE by calibration between scan points
   (`04db4fae`'s low-residual wrong-k class). It corrupts conducted-path
   data only; the PTFE itself is undamaged.
4. **Micro-cracking from freeze/thaw has a real driving force (freezing
   pressure up to ~210 MPa vs PTFE yield 10-20 MPa, an order of
   magnitude) but a near-dead access gate**: solid extruded RG316 PTFE
   is non-porous, and both setpoints keep PTFE 57-77 K above its Tg
   (-97 C) inside the phase-II plateau, below the +19/+30 C transition
   region but far from any embrittlement. LOW likelihood at both
   setpoints; **permanent and ratcheting once initiated**; corruption is
   the discontinuous/intermittent class.
5. **Thermal-cycling electrical excursion (er tempco) is CERTAIN but
   small and perfectly reproducible**: VF tempco -100 ppm/K -> phase
   +4.4 deg (45 K, +25 to -20) and +6.4 deg (65 K, +25 to -40) over the
   full path at 868 MHz, or +2.0 deg for the -20 to -40 sub-swing.
   Slow, monotonic, calibration-trackable — the benign class. The
   campaign crosses the +19 C crystalline transition on every first
   ramp, a small slope-discontinuity flagged UNVERIFIED (magnitude not
   on record; Section 8, Entry 5 corrects the prior report's placement
   of this step).
6. **Nothing in the PTFE-dielectric set reaches "destroys hardware".**
   Highest class is *degrades hardware* (a crack or cold-flow
   relocation changes the dielectric geometry permanently but the cable
   still passes RF).

Likelihood scale (inherited from `04db4fae`): CERTAIN (physics-guaranteed
given the established moisture supply, no mitigation assumed) / HIGH /
MEDIUM / LOW / N/A.

---

## 0. Physical scope: where PTFE sits in this measurement

| Item | Ground |
|---|---|
| Conducted path (variant B, planned): RG316 SMA-m/m 0.15 m (interior, DUT -> bulkhead) + 0.50 m (exterior), solid PTFE dielectric, er ~2.1 | `55585471` 3b; `fe700201` 2a; `bench/coax-bundle-dimensions/REPORT.md` (dielectric row) |
| SMA bulkhead feedthrough (Amphenol 132134-class jack-jack) with PTFE bead — the ONE exposed PTFE dielectric face pair in the frost zone | `55585471` 3b; `fe700201` |
| Primary path (variant A): wire dipoles on bare pads, NO coax, NO PTFE dielectric in the measured RF path | `0b7bfe92` |
| Neither cable nor feedthrough exists on hand; no run has occurred; no chamber exists | `fe700201`, `72f3aab9`, `c4be4400` (via `04db4fae` section 0) |
| Moisture supply certain: cold side sits 22-57 C below lab dew point in every lab-ambient cell; frost WILL deposit on every surface reaching cold-side temperature | `65c9c3df` (HIGH, Magnus grid) |
| Exterior feedthrough face at -40 C setpoint: est. -15 to -30 C (copper center conductor cold-bridge) | `65c9c3df` 2b |
| Cable temp rating on record: "both [RG316/RG178] are rated to -40 C (PTFE dielectric)" — project BOM claim; **no vendor datasheet on host; specific part UNVERIFIED** | `55585471` 4.2 |
| PTFE material data on record: moisture absorption <0.01 wt%; Tg ~-97 C; er ~2.1; er tempco ~200 ppm/K; CTE 100-135 ppm/K [INDUSTRY-TYPICAL] | `65c9c3df` 3b + source table; CTE from `04db4fae` section 5 (labeled there) |
| Campaign cycles: setpoints +25/0/-20/-40 C, >=2 ramps required, ~3-4 thermal cycles per run day | `72f3aab9`; `79ea692e` |
| Primary measurement: decode-count edgescan, ~165 dB link budget; conducted loss ~0.3-0.5 dB class, ~0.02 dB temperature variation, cannot move a decode edge | `55585471` step 5; `04db4fae` 2.6 |

The USB-C serial cable's dielectric is not PTFE-verified and carries no RF
measurement — excluded. The LR2021 module substrate is not PTFE — excluded.

---

## 1. MASTER TABLE (acceptance deliverable: one entry per failure mode)

Consequence classes are the task's three: corrupts data only / degrades
hardware / destroys hardware. "Corruption character" answers the task's
explicit drift-vs-jump question for each dielectric mode.

| # | ID | Failure mode | Driver | (a) Mechanism (short) | (b) -20 C | (b) -40 C | (c) Reversible? | (d) Consequence class | Corruption character | Cycle scaling |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | PDM-1 | Bulk water absorption -> er/VF/phase drift | moisture | Fickian diffusion into solid PTFE; nonpolar C-F matrix -> near-zero solubility; bounded by datasheet max | LOW | LOW (slower diffusion cold) | Fully reversible (dries) | Corrupts data only (and only phase-quantitative variants; primary decode-count unaffected) | Slow monotonic drift; calibration-trackable | None — no ratchet; resets each dry-out |
| 2 | PDM-2 | Surface adsorption / frost on exposed PTFE faces (bead gap, termination faces) | moisture (+cold) | vapor deposits as frost (er ~3.2, lossy) in the interface region; PTFE hydrophobicity shapes crystal growth, not whether | HIGH | HIGH (more mass, stays frozen through hold) | Reversible (sublimates/dries); PTFE face itself undamaged | Corrupts data only | Time-varying growth BETWEEN scan points — NOT cleanly trackable; the low-residual wrong-k hazard class (`04db4fae` 2.1) | Per-cycle reset; no accumulation on the PTFE |
| 3 | PDM-3 | Freeze/thaw micro-cracking / ice-wedging in pre-existing defects | moisture x cold (coupled) | confined water freezes; ~9 % expansion; freezing pressure up to ~210 MPa vs PTFE yield 10-20 MPa; access gated on defect + water entry | LOW | LOW (slightly more deposit mass, harder ice) | NO — crack is permanent; ratchets once initiated | Degrades hardware + corrupts data | Discontinuous / intermittent (crack opens-closes, ice in/out) — NOT trackable | Threshold-then-progressive: ~0 until first crack, then grows with N |
| 4 | PDM-4 | Thermal-cycle fatigue of the dielectric (no ice) | cycling | CTE mismatch PTFE-minus-copper 83-118 ppm/K -> 0.37-0.77 % strain per cycle vs 200-400 % elongation at break (margin ~260x) | LOW | LOW (~2x damage per cycle by dT^2, still LOW) | Strain reversible; a fatigue crack is permanent | Degrades hardware (+data when it snaps) | Discontinuous when it occurs; no drift precursor | Coffin-Manson class: thousands of cycles at 45-65 K; campaign's ~3-4/day is negligible |
| 5 | PDM-5 | Temperature-driven er/VF excursion + transition-region step | cycling | er tempco ~200 ppm/K -> VF tempco -100 ppm/K; phase +4.4 deg (45 K) / +6.4 deg (65 K) full path @868 MHz; +19 C crystalline transition crossed each ramp | CERTAIN (small) | CERTAIN (small) | Fully reversible, no hysteresis expected below jacket-damage thresholds | Corrupts data only (phase-quantitative variants; decode-count immune, 165 dB budget) | Slow monotonic drift; the ideal calibration-trackable case | Reproducible every cycle; zero accumulation |
| 6 | PDM-6 | Cold-flow / creep of PTFE under cyclic termination clamp | cycling | PTFE has the highest creep of common dielectrics; bead/dielectric under sustained + cyclic compression can relocate material permanently | LOW-MEDIUM both | LOW-MEDIUM both | NO — dimensional relocation is permanent (tiny, accumulating) | Degrades hardware (slight) + corrupts phase-quantitative data | Slow drift, accumulating — trackable while fresh calibration exists | Accumulates with N (creep ~log-time, plus per-cycle increments) |
| 7 | PDM-7 | Dielectric-loss (tan-delta) term and its perturbations | cycling (+moisture bound) | PTFE tan-delta 1e-4..5e-4 -> alpha_d 0.007-0.037 dB over 0.65 m @868 MHz, minor vs ~0.2 dB conductor term; moisture bound 0.067 dB at the unreachable saturation max | CERTAIN (negligible) | CERTAIN (negligible) | Fully reversible | Corrupts data only (power-quantitative variants; magnitude negligible) | Slow drift | None |

No entry reaches "destroys hardware": the worst structural outcome (PDM-3
crack) leaves the cable passing RF with degraded impedance/phase
stability. Destruction-class outcomes in the wider campaign live outside
the PTFE dielectric (e.g. `04db4fae` FM-4: USB-C short on thaw).

---

## 2. Per-entry detail

### 2.1 PDM-1 — Bulk moisture absorption (task item 1a)

**(a) Mechanism tied to material properties.** Water enters bulk PTFE
only by molecular diffusion through the polymer matrix. PTFE's fully
fluorinated carbon backbone is nonpolar and has very low surface energy
(~18-20 mN/m [INDUSTRY-STANDARD, UNVERIFIED on host]; water contact angle
~108-114 deg), so water solubility in PTFE is near-zero — which is why
the material datasheet class reports moisture absorption **<0.01 wt%**
(`65c9c3df` source table, "e.g. DuPont Teflon PTFE", HIGH). Two
consequences follow:

- *Electrical bound at the datasheet max.* Treating the max as
  saturation and using dilute-sphere mixing (water er ~80 in matrix
  er ~2.1): volume fraction phi = 0.00022 (0.022 vol%),
  d_er/er = +0.0611 %, **d_VF/VF = -0.0305 %**, phase shift
  **<=0.30 deg over the full 0.65 m path at 868 MHz** (0.07 deg for the
  0.15 m cold segment; ~0.83 deg at 2.4 GHz). Loss side: even at that
  unreachable max, mixed tan-delta gives alpha_d ~0.10 dB/m -> **0.067
  dB over 0.65 m @868 MHz** (script Section 3c). Linear dimensional
  swelling from that uptake is ~0.007 % (73 ppm) — comparable to a
  ~0.6-0.9 K thermal shift, negligible.
- *Access bound.* Water diffusivity in PTFE is ~1e-13..1e-11 m2/s
  [INDUSTRY-TYPICAL, wide range, UNVERIFIED]; diffusion time tau ~ L^2/D:
  **radial 0.6 mm (dielectric-only) = 10 h-42 d; radial 1.0 mm
  (jacket-to-core) = 1.2-116 d; axial 0.15 m = 71-7130 yr** (script
  Section 3b). The axial path is dead on any campaign timescale. The
  radial path requires the shield+braid+jacket to be breached (not
  assumed) — the dielectric is only directly exposed at the
  termination/bead faces. Diffusion is thermally activated: at -20/-40 C
  the slow end of the range applies, and the cold face spends the hold
  frozen (ice at the surface does not diffuse).

**(b) Likelihood.** -20 C: **LOW**. -40 C: **LOW** (marginally lower
still — slower diffusion cold; more of the deposited water is committed
to surface ice). Reasoning: both setpoints sit far below the dew-point
inversion so moisture supply at the cold face is certain, but the
bulk-uptake *rate* is diffusion-gated to effectively zero within a
run day, and the max effect is negligible anyway.

**(c) Reversible vs permanent.** Fully **reversible** — physical
sorption/desorption, no chemical or dimensional change of the matrix.
Drying at room temperature recovers er/VF completely; no hysteresis
mechanism exists at these uptake levels.

**(d) Consequence class.** Corrupts measurement data only — and only for
a phase/power-quantitative variant of the measurement (none is planned;
the primary decode-count protocol has ~165 dB budget vs a <=0.30 deg,
<=0.067 dB bound). **Corruption character: slow, monotonic,
calibration-trackable drift** — a compensation curve could absorb it even
if it were reached. No hardware impact.

**Cycle scaling:** none. Uptake re-equilibrates toward (tiny) ambient
solubility each warm-up and re-freezes out each cooldown; there is no
ratchet — the effect cannot accumulate across cycles.

### 2.2 PDM-2 — Surface adsorption of water / frost on exposed PTFE faces (task item 1b)

**(a) Mechanism.** The only PTFE faces exposed to air in this campaign
are the bulkhead feedthrough's bead faces and the two cable termination
faces (variant B). The mated SMA interface is not hermetic: humid air
trapped at mating time plus frost-point physics (cold side 22-57 C below
lab dew point, `65c9c3df`) deposits water on every cold face — PTFE
included. PTFE's hydrophobicity (~110 deg contact angle) means liquid
wets it poorly, but at these temperatures deposition is vapor -> ice
(frost), which nucleates on any cold surface regardless of wettability;
hydrophobicity shapes crystal morphology, not whether frost grows. The
result is a frost volume of **er ~3.2, tan-delta ~0.001-0.01, resistivity
~10^7-10^8 Ohm-m** (`65c9c3df` sources table: von Hippel; Hobbs) sitting
in what should be an air/PTFE interface gap — an impedance
discontinuity + shunt loss + phase-length perturbation of the interface
region. This is the same physical mode as `04db4fae` FM-1/FM-2
(interface moisture); the PTFE-specific content here is that the
dielectric surface itself is undamaged and the effect is fully
attributable to the *deposited* phase, not to the polymer.

**(b) Likelihood.** -20 C: **HIGH**. -40 C: **HIGH** (worse in degree:
larger vapor-pressure deficit grows frost faster and the interface stays
below 0 C through the entire hold — no transient near-melt windows as a
-20 C hold can see during ramps). Reasoning: requires exposed face +
certain moisture supply; both present whenever the conducted path exists
unmitigated.

**(c) Reversible vs permanent.** Reversible on warm-up
(sublimates/dries). The PTFE face itself is unchanged (no sorption,
no staining — water uptake at the surface of PTFE is adsorption, not
absorption). Adjacent-metal corrosion from melted residue is a
connector/metal mode (`04db4fae` FM-1/FM-12 territory), not a PTFE
mode.

**(d) Consequence class.** Corrupts measurement data only (conducted-path
S11/IL/phase). **Corruption character: time-varying between scan points —
NOT a clean slow drift.** A frost volume that grows during a soak
shifts each scan point by a different amount (fit residual rises,
flagged); a frost state that persists uniformly across a whole scan
shifts every point identically — **low residual, wrong k** — which the
fit's own >5 ppm RMS check cannot catch (`04db4fae` 2.1, quoting the fit
guidance). This is the most dangerous corruption class for any
phase-quantitative use of the conducted path. No hardware damage to the
dielectric.

**Cycle scaling:** per-cycle reset (frost is gone after warm-up). No
accumulation on the PTFE itself. The cumulative hazard is purely in the
data (each run's affected points are permanently bad).

### 2.3 PDM-3 — Freeze/thaw micro-cracking (ice-wedging) (task item 2)

**(a) Mechanism.** Water confined in a void, craze, or delamination
within or adjacent to the dielectric expands ~9 % on freezing
(`65c9c3df`). In a stiff confinement the freezing pressure rises along
the ice-I melting curve: computed Clapeyron slope **13.4 MPa/K**
(script Section 5), i.e. the melting point is depressed ~1 C per
13.4 MPa — up to the ice-I/ice-III/liquid triple point cap
**~210 MPa at ~-22 C** [INDUSTRY-STANDARD phase data, UNVERIFIED on
host]. Against that, PTFE's yield strength is **10-20 MPa at room
temperature** (higher when cold, but still an order of magnitude below
the available ~200 MPa class pressure). So *if* liquid water is confined
in a defect, the wedge pressure can locally yield/deform PTFE and can
propagate a crack — at BOTH setpoints, because even the -20 C hold is
~20 C of freezing below the 210 MPa cap and -40 C is metastable-frozen
with no liquid escape. The gate is access: solid extruded RG316
dielectric is non-porous (unlike foam-PTFE constructions, which are the
industry's real freeze-cracking victims); water must first find a
pre-existing defect *and* a path to it. Note the on-record tension about
cold toughness: `65c9c3df` 3a says "useful toughness drops below -20 C"
while `04db4fae` FM-3 (quoting the same source's 3b) says PTFE remains
ductile above Tg (-97 C). Both agree no glass transition is crossed
above -40 C; the disagreement is only in how much toughness declines —
and PTFE's routine cryogenic service (down to -200 C class, gaskets and
dielectrics) supports the ductile reading [INDUSTRY-STANDARD, UNVERIFIED
on host]. Either reading keeps PDM-3 LOW at the campaign's cycle counts.

**(b) Likelihood.** -20 C: **LOW**. -40 C: **LOW** (marginally higher:
more deposited mass near the coldest faces, harder/more aggressive ice
`65c9c3df` 2d, longer frozen hold). Reasoning per the task's transition
hint: both setpoints are in the phase-II plateau — below the +19/+30 C
crystalline-transition region, 57-77 K above Tg — so neither setpoint
crosses any transition and neither adds a brittleness mechanism; the
difference is only deposit mass/ice hardness.

**(c) Reversible vs permanent.** **Permanent.** A crack or delamination
does not heal. Worse, it ratchets: once a crack exists it is a better
water trap than the original defect (capillary wicking along a wet gap is
fast, unlike bulk diffusion — script Section 3b note), so each
subsequent freeze/thaw cycle wedges it further. Damage is
threshold-then-progressive.

**(d) Consequence class.** **Degrades hardware** (dielectric integrity;
impedance bump at the crack; the cable still passes RF) **+ corrupts
data**. **Corruption character: discontinuous / intermittent** — a crack
opens and closes with temperature and water phase, producing step
changes in reflection/IL/phase that no calibration can track; this is
the open/intermittent class, not drift.

**Cycle scaling:** ~zero for the first N cycles (gated on a defect
holding water), then progressive growth with N once initiated. The
campaign's ~3-4 cycles/run day is far below any credible initiation
count for sound solid dielectric; the realistic initiation sites are
termination/bead defects introduced at assembly (soldering a pigtail per
`0b7bfe92` downstream note), not the pristine extruded bulk.

### 2.4 PDM-4 — Thermal-cycle fatigue of the dielectric without ice (task item 2 complement)

**(a) Mechanism.** Every ramp cycles a CTE mismatch strain across the
dielectric: PTFE ~100-135 ppm/K vs copper ~17 ppm/K
(`04db4fae` section 5, INDUSTRY-TYPICAL labels carried) ->
differential 83-118 ppm/K -> computed strain per cycle **0.37-0.53 %
over the +25 to -20 swing (45 K), 0.54-0.77 % over +25 to -40 (65 K),
0.17-0.24 % over the -20 to -40 sub-swing** (script Section 4). Against
elongation at break of 200-400 % [INDUSTRY-TYPICAL] the worst cycle uses
~1/260 of the material's strain budget. PTFE above Tg is ductile; both
setpoints are 57-77 K above Tg, below the +19/+30 C transition region
but with no embrittlement transition in between.

**(b) Likelihood.** -20 C: **LOW** (45 K swing). -40 C: **LOW** (65 K
swing, ~2x damage per cycle by the dT^2 fatigue metric, still LOW vs the
strain margin). Reasoning: same phase-II plateau at both endpoints —
the setpoint choice changes only swing magnitude, not mechanism.

**(c) Reversible vs permanent.** The strain excursion is fully
reversible (it *is* the PDM-5 electrical excursion's mechanical twin).
A fatigue crack, if ever formed, is permanent.

**(d) Consequence class.** Degrades hardware when it occurs (+ data
corruption in the same discontinuous class as PDM-3). **Corruption
character: discontinuous** — fatigue cracks open/close with temperature;
no slow drift precursor exists at the RF level for a crack this small.

**Cycle scaling:** Coffin-Manson class — thousands of cycles at 45-65 K
swings [standard reliability practice, labeled UNVERIFIED]; the
campaign's ~3-4 cycles/run day is a negligible fraction. No meaningful
accumulation is expected within the campaign's life.

### 2.5 PDM-5 — Temperature-driven er / VF / phase excursion (task item 3: velocity factor + phase length + phase stability)

**(a) Mechanism.** PTFE's dielectric constant is ~2.1 with an er tempco
of ~200 ppm/K (`65c9c3df` 3b) -> VF = 1/sqrt(er) = **0.690 derived**
(industry-nominal RG316 VF 0.70 [INDUSTRY-TYPICAL, UNVERIFIED on host];
consistent) and **VF tempco -100 ppm/K**, electrical-length tempco
+100 ppm/K (er) / +117 ppm/K (er + conductor CTE). Computed phase
excursions over the campaign's swings (script Section 2):

| Swing | Cold segment 0.15 m @868 MHz | Full path 0.65 m @868 MHz | Full path 0.65 m @2.4 GHz (context only) |
|---|---|---|---|
| -20 <-> -40 C (20 K) | +0.45 deg | +2.0 deg | +5.4 deg |
| +25 -> -20 C (45 K) | +1.0 deg | +4.4 deg | +12.2 deg |
| +25 -> -40 C (65 K) | +1.5 deg | +6.4 deg | +17.6 deg |

(Cross-check: the script reproduces `04db4fae` 2.6's committed 4.5 deg
figure for 0.50 m/60 K to within rounding — +4.53 deg. Consistent.)
Phase *stability* in the sense of repeatability: below the +19 C
crystalline transition the er-vs-T curve is smooth, so on the -20/-40
plateau the excursion is monotonic and near-linear. The campaign
nevertheless crosses the **+19 C transition on every first ramp**
(+25 -> 0 C), where PTFE undergoes its well-known second-order
crystalline transition (phase II -> IV at ~19 C, IV -> I at ~30 C)
[INDUSTRY-STANDARD, UNVERIFIED on host] — a small slope discontinuity in
er/electrical length that the coax industry calls the PTFE step
(magnitude NOT on record; see Section 8 Entry 5 for the prior report's
placement discrepancy). Both setpoints are BELOW the transition region:
the step is a ramp-crossing event, not a hold state.

**(b) Likelihood.** -20 C: **CERTAIN (small)**. -40 C: **CERTAIN
(small)** — pure physics, present on every ramp, larger at -40 only
through the bigger swing.

**(c) Reversible vs permanent.** Fully reversible, no hysteresis
expected below jacket-damage thresholds (`04db4fae` FM-7 concurs).
Reproduces identically every cycle.

**(d) Consequence class.** Corrupts measurement data only — and only a
phase-quantitative variant; the primary decode-count edgescan has ~165
dB of link budget against a <=7.5 deg phase / ~0.02 dB loss change
(`55585471` step 5, `04db4fae` 2.6). **Corruption character: slow,
monotonic, calibration-trackable drift — the benign case**: a
temperature-indexed compensation absorbs it entirely, and the k/T0
fit's structure (offset vs T) already lives in a temperature-parameter
space.

**Cycle scaling:** zero accumulation; identical every cycle. (Whether any
phase-quantitative variant would need cable-level temperature
characterization was already answered by `04db4fae` 2.6 and is not
re-argued here — no mitigation content is included in this report, per
the acceptance criteria.)

### 2.6 PDM-6 — Cold-flow / creep of the PTFE under cyclic termination clamp

**(a) Mechanism.** PTFE has the highest cold-flow (creep under load) of
the common dielectrics [INDUSTRY-STANDARD material behavior, UNVERIFIED
on host] — the property behind its gasket fame and the reason PTFE
beads in connectors are mechanically captured. The bulkhead bead and
the crimp/solder termination see sustained compression from the
connector design PLUS cyclic modulation from differential contraction
(PDM-4's strain cycle). Sustained stress relaxes by creep; each thermal
cycle adds a small permanent relocation increment. Net long-term effect:
bead/dielectric geometry shifts -> a slowly moving impedance
discontinuity and reference-plane drift at the termination.

**(b) Likelihood.** -20 C: **LOW-MEDIUM**. -40 C: **LOW-MEDIUM**
(creep rate is lower when cold — thermally activated — but the stress
excursions are larger). Reasoning: mechanism certain in class (PTFE
always creeps under load), magnitude small because the SMA bead is
captured (constrained) and the loads are assembly-level, not
ice-wedge-level.

**(c) Reversible vs permanent.** **Permanent** — creep relocation does
not reverse (annealing-class recovery is not in any campaign profile).
It is the canonical "dimensional/structural change" of the task's
reversibility question, distinct from every moisture effect.

**(d) Consequence class.** Degrades hardware (slight, progressive) +
corrupts phase-quantitative data. **Corruption character: slow drift,
accumulating** — trackable by a fresh calibration until the reference
plane has moved enough to matter; NOT a jump.

**Cycle scaling:** accumulates with cycle count N and ~log(time)
(creep), decelerating. Over a campaign of tens of cycles the total is
small; it matters only for a long-lived reference path.

### 2.7 PDM-7 — Dielectric-loss term (task item 3: insertion loss)

**(a) Mechanism.** The PTFE dielectric contributes an insertion-loss
term alpha_d = 27.3*sqrt(er)*tan(delta)/lambda0: with PTFE tan-delta
1e-4..5e-4 [INDUSTRY-TYPICAL, UNVERIFIED on host], computed
**0.007-0.037 dB over the full 0.65 m path at 868 MHz**
(0.021-0.103 dB at 2.4 GHz) — a minor fraction of the ~0.2 dB conductor
term (~0.3 dB/m class, `55585471` step 5). Moisture perturbation of this
term is bounded by the PDM-1 saturation max: <=0.067 dB @868 MHz
(script Section 3c) at an uptake level the campaign cannot approach.
The temperature dependence of PTFE's tan-delta is NOT on record.

**(b) Likelihood.** -20 C: **CERTAIN (negligible magnitude)**.
-40 C: **CERTAIN (negligible magnitude)** — the term exists at all
temperatures; no transition is crossed at either setpoint that would
step it.

**(c) Reversible vs permanent.** Fully reversible.

**(d) Consequence class.** Corrupts measurement data only, in
power-quantitative variants, at magnitudes the ~165 dB budget cannot
see. **Corruption character: slow drift**, if it is ever resolvable at
all.

**Cycle scaling:** none.

---

## 3. -20 C vs -40 C: regime summary

| Aspect | -20 C | -40 C | Ground |
|---|---|---|---|
| Position vs PTFE transitions | Phase-II plateau: below +19/+30 C transition region, 77 K above Tg (-97 C) | Same plateau, 57 K above Tg | `65c9c3df` 3b + standard phase data (labeled) |
| Transition crossed by a setpoint's hold? | No | No | same |
| Bulk uptake rate | LOW (diffusion-gated; slow end of D range) | LOW (slower still, thermally activated) | script 3b |
| Frost deposit at exposed faces | HIGH (certain supply) | HIGH, faster growth + frozen through hold | `65c9c3df` 2d |
| Ice character | softer, near-melting during ramps | harder, "more mechanically aggressive" | `65c9c3df` 2d |
| Ice-wedge driving pressure available | up to ~210 MPa class (before the -22 C cap; -20 C is 2 K above the cap) | metastable beyond cap, still order-of-magnitude above PTFE yield | script 5 |
| CTE strain cycle (from +25) | 0.37-0.53 % | 0.54-0.77 % | script 4 |
| Electrical excursion (full path, 868 MHz) | +4.4 deg | +6.4 deg | script 2 |
| Cable rating position | within "rated to -40 C" | ON the on-record rating edge; vendor verification required at procurement | `55585471` 4.2 |
| Net verdict | same *kinds* of every mode; smaller degree | same kinds; larger degree; nothing qualitatively new appears below -20 C for the PTFE itself | this report |

The task's transition hint resolves cleanly: **both setpoints are below
PTFE's useful transition region** (+19/+30 C crystalline transitions)
and above its Tg (-97 C) — the PTFE at -40 C is the same phase-II solid
as at -20 C, only 20 K colder. Every difference between the setpoints
for the dielectric is one of degree (more deposited mass, harder ice,
bigger excursion, bigger strain), not of kind.

---

## 4. Reversibility map and cycle-count scaling (task item 4)

| Entry | Drying-out recovers it? | Permanent component | Scales with cycle count N? |
|---|---|---|---|
| PDM-1 bulk uptake | Yes, fully | none | no — resets, no ratchet |
| PDM-2 surface frost | Yes, fully (PTFE face unchanged) | none on the PTFE | no — per-cycle reset |
| PDM-3 ice-wedging crack | no (crack remains) | the crack itself | yes — threshold-then-progressive ratchet once initiated |
| PDM-4 thermal fatigue strain | strain yes | crack if formed | damage metric ~ dT^2 per cycle; thousands-of-cycles class; negligible at campaign N |
| PDM-5 er/VF tempco | n/a (not moisture) — recovers with temperature | none | no — reproducible every cycle, zero accumulation |
| PDM-6 cold-flow | no | dimensional relocation | yes — accumulates ~log-time + per-cycle, decelerating |
| PDM-7 tan-delta term | yes | none | no |

Campaign cycle budget on record: >=2 ramps required per session, ~3-4
thermal cycles per run day, 4 setpoints (+25/0/-20/-40)
(`72f3aab9`, `79ea692e`). Only PDM-3 (post-initiation) and PDM-6
accumulate with N; both are LOW/LOW-MEDIUM at that budget.

### 4.1 Where each measured-parameter change lives (task item 3 map)

| Parameter | Moisture-driven | Cycling-driven | Entry |
|---|---|---|---|
| Velocity factor | dVF/VF -0.0305 % at the unreachable datasheet max; actual ~0 | -0.45 % (+25 -> -20) / -0.65 % (+25 -> -40) / -0.20 % (-20 <-> -40), tempco -100 ppm/K | PDM-1 / PDM-5 |
| Insertion loss | <=0.067 dB @868 MHz at the saturation max; frost at faces: unbounded interface shunt (PDM-2) | dielectric term 0.007-0.037 dB @868 MHz; its tempco not on record | PDM-1/2/7 |
| Phase length | <=0.30 deg @868 MHz full path at the saturation max | +4.4 deg (45 K) / +6.4 deg (65 K) / +2.0 deg (-20<->-40) full path @868 MHz | PDM-1 / PDM-5 |
| Phase stability (repeatability) | frost growth/decay between scan points — the untrackable class | monotonic, reproducible, +19 C step crossed on every first ramp (magnitude not on record) | PDM-2 / PDM-5 (+PDM-6 drift, PDM-3 jumps) |

---

## 5. Sources (numeric, per acceptance criteria)

| # | Claim (number) | Source | Confidence / label |
|---|---|---|---|
| 1 | PTFE material datasheet class: moisture absorption **<0.01 wt%**, Tg **~-97 C**, er **~2.1**, er tempco **~200 ppm/K** | `65c9c3df` (`bench/condensation-risk/REPORT.md`) source table, citing "Typical PTFE material datasheet (e.g. DuPont Teflon PTFE)" | HIGH as carried on record; **no vendor PTFE datasheet exists on host**; no outbound fetch (standing operator constraint) |
| 2 | PTFE CTE **100-135 ppm/K**; copper ~17 ppm/K | `04db4fae` section 5 material table | INDUSTRY-TYPICAL, UNVERIFIED on host (labeled there) |
| 3 | Cable temperature rating: **"both [RG316/RG178] are rated to -40 C (PTFE dielectric)"**; RG316 solid PTFE dielectric, er ~2.1; -40..+200 C class | BOM `55585471` 4.2 (project's own claim) + `bench/coax-bundle-dimensions/REPORT.md` dielectric row | MEDIUM — on-record claim, **specific procured part UNVERIFIED, no vendor cable datasheet on host** |
| 4 | Velocity-factor "spec": derived **VF = 1/sqrt(2.1) = 0.690** from the on-record er; industry-nominal RG316 **0.70** | derivation (this directory, script Section 1) + industry-nominal label | HIGH (arithmetic) / INDUSTRY-TYPICAL (the 0.70 nominal, UNVERIFIED) |
| 5 | PTFE second-order transitions **~+19 C and ~+30 C** (crystalline); both setpoints below the region | standard material data | INDUSTRY-STANDARD, **UNVERIFIED on host** — flagged; corrects `04db4fae`'s "near -20 C" placement (Section 8, Entry 5) |
| 6 | Ice er **~3.2**, tan-delta **0.001-0.01**, resistivity **10^7-10^8 Ohm-m**, water **~80**, freezing expansion **~9 %** | `65c9c3df` sources table (von Hippel; Hobbs) | HIGH (well-established) |
| 7 | Dew-point margins **22-57 C** below dew point across the lab grid | `65c9c3df` (computed, Magnus) | HIGH |
| 8 | Conducted path: 0.15 m + 0.50 m RG316, ~0.3 dB/m class, ~165 dB link budget, decode-count protocol | `55585471` 3b/step 5; `fe700201`; `04db4fae` 2.6 | HIGH (committed prior reports) |
| 9 | Water diffusivity in PTFE **1e-13..1e-11 m2/s**; PTFE tan-delta **1e-4..5e-4**; PTFE yield **10-20 MPa**; elongation at break **200-400 %**; surface energy **18-20 mN/m**; contact angle **~110 deg**; ice-I triple point **~210 MPa at ~-22 C**; Clapeyron slope computed **13.4 MPa/K** | INDUSTRY-TYPICAL / standard physics — computed where stated (script Sections 3b/5/6) | MEDIUM (standard values; no on-host datasheet; every number labeled in the script) |
| 10 | Campaign cycles: 4 setpoints, **~3-4 thermal cycles/run day**, >=2 ramps required | `72f3aab9`; `79ea692e` | HIGH |
| 11 | LR2021 operating **-40..+85 C** (context: -40 C is the radio's edge, not the PTFE's) | LR2021 datasheet Rev 2.1, Table 3-2 (on-host PDF, prior session extraction) | HIGH (manufacturer datasheet) |

The acceptance criteria's two required source classes are satisfied by
rows 1 (PTFE material datasheet class, with numbers) and 3+4 (cable
temperature rating and velocity-factor spec, with numbers), with the
honest caveat that both are datasheet-CLASS values carried on the
project record — no PTFE or cable vendor document exists on this host
and none was fetched (standing operator constraint, respected; nothing
attempted this session).

---

## 6. Caveats and honest gaps

1. **No cable, connector, or feedthrough exists on hand.** The entire
   catalogue is a prior enumeration for a MUST-PROCURE planned path
   (`55585471` 3b); nothing has been cycled and no frost has been
   observed because no run has occurred (`c4be4400` via `04db4fae`).
2. **No PTFE or cable vendor datasheet exists on host.** Every
   part-specific value is datasheet-class/industry-typical and labeled
   UNVERIFIED. The procured part's datasheet (absorption, temp rating,
   VF spec, phase-stability curves, cold-flow data) replaces those
   labels at procurement.
3. **The +19 C transition step magnitude is not on record.** The step's
   existence is industry-known; its size for a specific RG316 is not.
   Until a vendor phase-stability curve is on record, any
   phase-quantitative design crossing +19 C carries an unquantified
   discontinuity.
4. **Diffusivity, tan-delta, yield, and elongation values are
   order-class bounds**, chosen as labeled ranges precisely because no
   datasheet exists; verdicts (LOW/negligible) are robust across the
   stated ranges because the margins are 2-4 orders.
5. **PTFE cold toughness on record is internally inconsistent**
   (`65c9c3df` "useful toughness drops below -20 C" vs `04db4fae`
   "remains ductile above Tg"). Both readings leave PDM-3/PDM-4 LOW at
   the campaign's cycle budget; the discrepancy is flagged, not
   adjudicated — no datasheet on host to adjudicate it.
6. **The ice-wedge pressure numbers are equilibrium-class bounds.**
   Real confined pockets are compliance-limited and rarely reach the
   cap; the bound establishes *capability* (order of magnitude above
   PTFE yield), not expected stress.
7. **No fleet-state lookup was attempted** (operator-denied in a prior
   session; recorded in `04db4fae` 6.6). The card ID is therefore not
   cited.

---

## 7. Nothing fabricated

Every number in this report is one of: (a) committed in a prior bench
report with its own source table (`65c9c3df`, `55585471`, `fe700201`,
`04db4fae`, `0b7bfe92`); (b) computed by `ptfe_dielectric_calc.py` in
this directory, with the script's saved output (`output.txt`) matching
every quoted figure, inputs labeled IN the script, and a cross-check
that reproduces `04db4fae`'s committed 4.5-deg figure (+4.53 deg); or
(c) explicitly labeled INDUSTRY-TYPICAL / INDUSTRY-STANDARD /
UNVERIFIED. No measurement was invented, no cable was tested (none
exists), no vendor document was consulted (none on host, no outbound
fetch attempted), and no mitigation is recommended anywhere, per the
acceptance criteria.

---

## 8. Cross-links and record corrections

1. **`04db4fae` FM-11** (PTFE bulk uptake / micro-cracking, four lines)
   is deepened by PDM-1/PDM-3/PDM-4 here. Verdicts agree: uptake LOW and
   reversible; cracking LOW and permanent-when-it-occurs. This report
   adds the bounds (why LOW, numerically) and the drift-vs-jump split.
2. **`04db4fae` FM-1/FM-2** (interface frost) are the interface-region
   twins of PDM-2; the PTFE-specific contribution here is the
   corruption-character classification and the statement that the PTFE
   face itself survives frost cycles undamaged.
3. **`04db4fae` FM-7** (bulk cable tempco) is the conducted-path-wide
   version of PDM-5/PDM-7; the 4.5-deg cross-check ties the two
   computations together.
4. **`04db4fae` FM-10** (solder CTE fatigue) is the joint-level twin of
   PDM-4; the dielectric has a ~260x strain margin where joints were
   argued thousands-of-cycles — different margins, same LOW verdict.
5. **CORRECTION of `04db4fae` section 2.6's flag:** the prior report
   recorded the industry-known PTFE dielectric step as "near -20 C"
   (LOW-MEDIUM, flagged UNVERIFIED). Standard material data places
   PTFE's second-order crystalline transitions at **~+19 C and ~+30 C**
   (phase II below +19 C), with a broad amorphous beta relaxation also
   reported in the -30..+20 C region. The step the coax industry
   observes at the crystalline transition is therefore crossed during
   this campaign's **+25 -> 0 C ramp segment, at both setpoint plans
   equally** — not during the -20/-40 holds. Neither placement is
   host-verifiable today (no vendor phase-stability curve on host); the
   correction matters because it moves the discontinuity from the
   cold holds (where the prior report's phrasing suggested it) to the
   warm ramp segment every session necessarily crosses.
6. **Downstream handoff (facts, not mitigations):** PDM-2 is the only
   PTFE-path mode that can silently corrupt a phase-quantitative
   measurement (untrackable growth); PDM-3/PDM-6 are the only permanent
   modes; everything else is reversible drift bounded orders below the
   measurement's sensitivity. No entry destroys hardware.