# Damage and measurement-reliability failure modes: cables and feedthrough at -20 C / -40 C

Task (fleet card, ID not stated in the task body): "Enumerate damage and
measurement-reliability failure modes on cables and feedthrough. GOAL:
Independent of the physics verdict, catalogue what can be damaged or made
unreliable by moisture, frost, and thermal cycling, so the mitigation list
is grounded in real failure modes."

Date: 2026-09-15 · Repo: meshcore (main) · Worker: dq05 (profile
worker-heavy) · Host: `c03rad0r-DQ05proplus`.
Artifacts: this directory (`bench/cable-feedthrough-failure-modes/`).

**Parallelism:** this card runs in parallel with the formation
assessment. No formation-assessment input was awaited or consulted: a
grep of all `bench/*/REPORT.md` this session found no formation output
on record. This catalogue does not depend on it.

**Card-ID note:** the task body does not state the fleet card ID. A
fleet-state lookup to recover it was operator-denied this session
(recorded, not retried). No kanban comment possible (no NSEC on this
host — standing fleet norm).

**Scope discipline:** per the acceptance criteria, this report contains
NO mitigation recommendations. Section 8 lists only *which failure
modes* the mitigation task must address and which UNVERIFIED values
block quantification — not how to mitigate them.

---

## VERDICT SUMMARY

1. **Moisture supply is certain at both setpoints.** Every failure mode
   below is downstream of one established fact (condensation-risk
   `65c9c3df`, Magnus table, HIGH confidence): in every lab-ambient cell
   (20-25 C, 30-60 % RH) the cold side sits 22-57 C below the dew point,
   so water WILL deposit as liquid-then-ice on every surface that reaches
   the cold-side temperature, including the exterior feedthrough face.
   Likelihood ratings below therefore rate *the mechanism's response to
   that moisture and cold*, not the presence of moisture.
2. **12 failure modes are catalogued** (7 scope items, with the two
   path-dependent items split). Ranked master table in Section 1.
3. **What differs between -20 C and -40 C is not *kind* but *degree***
   (plus two genuinely different regimes: elastomer stiffness at -40 C,
   and harder/more aggressive ice at -40 C). Both setpoints are inside
   the LR2021 operating range (-40 to +85 C, datasheet Table 3-2, read
   this session from the on-host Rev 2.1 PDF); -40 C sits exactly ON
   the radio's rated edge and abs max is -55 C — the DUT itself has
   zero margin below -40 C, so any mechanism that pushes the die colder
   than chamber air (e.g. evaporative or radiative effects) has no
   datasheet guardrail.
4. **The measurement is robust to slow/small RF changes, NOT to
   intermittent ones.** The primary edgescan is a decode-count
   threshold measurement with a 165 dB link budget (BOM `55585471`
   step 5): bulk cable attenuation/phase temperature drift (computed
   in 2.6: ~10 % conductor-loss change, ~4.5 deg phase over the full
   60 K swing) cannot move a decode edge. Ice bridging and
   intermittent contact CAN (2.1, 2.2) — they shift the decode edge
   between scan points, and a shift that persists across a whole scan
   produces a *low-residual, wrong* k/T0 pair, which the fit's own
   >5 ppm RMS residual check (`65c9c3df` quoting the fit guidance)
   cannot catch. That is the most dangerous data-corruption class
   in this catalogue.
5. **No chamber, cable, feedthrough, or RF instrument exists on any
   record or on this host** (re-verified via sibling cards this
   session: nameplate `24eb918c`, controller `766ac96d`, feedthrough-fit
   `fe700201`, holds `72f3aab9`). This is a mechanism catalogue grounded
   in material physics and the on-record measurement chain — a prior
   enumeration, not a post-run observation. No frost has been observed
   because no run has occurred (`65c9c3df` caveat 4).

---

## 0. Hardware baseline the catalogue applies to

Two protocol variants exist (fork README `d7ae93fa`, "Bench setup" +
`thermal_bench.py scan_edges()`; both read via `git show` this session):

- **Variant A — primary (over-the-air):** DUT inside chamber (LR2021 on
  SkyMapper Board A, 2x SMA edge-launch J1 "SMA-868"/J2 "SMA-2G4" on the
  75x55 mm carrier, `hub_board_f33.kicad_pcb` via `fe700201`), wire
  dipole (8.6 cm legs) or SMA stub antenna inside, reference TX outside
  at room temperature. **Only 1x USB-C serial cable crosses the sealed
  boundary.** No coax, no RF feedthrough, no RF instrument (USB census:
  no SDR/VNA/counter — BOM `55585471`).
- **Variant B — optional conducted path:** adds DUT SMA -> RG316
  (0.15 m) -> SMA bulkhead feedthrough (Amphenol 132134-class panel
  jack-jack, project's own documented wall-pass pattern, 6.5 mm panel
  hole, "Fully waterproof with SMA O-rings", `enclosure/README_big.md`
  via `fe700201`) -> RG316 (0.5 m) -> reference TX outside.

**Measurement signal:** decoded-packet counts from the DUT CLI over
serial (`scan_edges()`); per-point required-compensation values are
fitted to the parabola `applied_offset = k*(T-T0)^2` for the per-module
calibration blob (fork README `d7ae93fa` model section).

Material ground truth used below (source table in Section 5):

| Item | Value | Source |
|---|---|---|
| Moisture supply | dew point 1.9-16.7 C across the 12-cell ambient grid; cold side 22-57 C below it | `65c9c3df` (computed, HIGH) |
| Exterior feedthrough face temp | est. -5 to -15 C at -20 C setpoint, -15 to -30 C at -40 C (copper center conductor dominates) | `65c9c3df` 2b |
| Ice | er ~3.2 (water ~80), tan d ~0.001-0.01, resistivity ~10^7-10^8 Ohm·m (pure; lower if contaminated), +9 % volume on freezing | `65c9c3df` (von Hippel, Hobbs) |
| PTFE | Tg ~-97 C, moisture absorption <0.01 %, er ~2.1, tempco ~200 ppm/K | `65c9c3df` (DuPont Teflon PTFE class) |
| CTE | stainless ~17, brass ~19 ppm/K; copper ~17 ppm/K [INDUSTRY-TYPICAL]; PTFE ~100-135 ppm/K [INDUSTRY-TYPICAL, UNVERIFIED on host]; SAC solder ~21-25 ppm/K [INDUSTRY-TYPICAL, UNVERIFIED] | `65c9c3df` + labels |
| Cable temp rating | "both [RG316/RG178] are rated to -40 C (PTFE dielectric)" — the project's own BOM claim; **no vendor datasheet on host; specific procured part UNVERIFIED** | BOM `55585471` step 4.2 |
| Seal elastomer (project pattern) | SMA O-rings (`README_big.md`); O-ring cord "Nitrile or silicone", 2 mm, AS568-compatible (`enclosure/README.md:27,72`) — **material not picked on record; both analysed** | enclosure READMEs |
| Enclosure plastic precedent | ASA dev case rated "-20C to +90C" — **no on-record enclosure material is rated to -40 C** | `enclosure/README.md:46` |
| DUT radio ratings | operating -40 to +85 C, abs max -55 to +125 C | LR2021 datasheet Rev 2.1, Tables 3-1/3-2, read from on-host PDF this session |
| Protocol enclosure | sealed bag around the module (verbatim fork README `d7ae93fa`: "an IPA/dry-ice bath plus a bare board equals condensation and ice on the RF path") | fork README |
| Setpoints | +25 / 0 / -20 / -40 C, 10-min holds, >=2 ramps per session (~3-4 thermal cycles per run day) | `72f3aab9` card spec + ramp-feasibility `79ea692e` |

Likelihood scale: **CERTAIN** (physics-guaranteed given the established
moisture supply, no mitigation assumed) / **HIGH** / **MEDIUM** / **LOW**
/ **N/A** (path does not exist in that variant).

---

## 1. MASTER RANKED FAILURE-MODE TABLE (acceptance deliverable)

Ranked by expected damage to the campaign: likelihood x consequence,
where consequence weights (a) silent corruption of the k/T0 calibration
blob highest (it poisons every downstream altitude compensation),
(b) run-visible data loss next, (c) permanent hardware damage last
(the hardware is cheap and few cycles are planned — but it is still
catalogued). Path: A = primary OTA, B = optional conducted.

| # | ID | Failure mode | Scope item | Path | Mech. (short) | -20 C | -40 C | Reversible? | Data? | HW? |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | FM-1 | Ice bridging center-pin to shield at exposed/unmated interface | 4 | B (A: DUT SMA only if stub removed) | frost shunts pin-shield; 10^7-10^8 Ohm·m lossy film, changes with growth/crack/melt | CERTAIN | CERTAIN | Reversible (dries) but intermittent DURING run | YES — moves decode edge; low-residual wrong-k class | No (unless carbon-tracks after arcing — none here, +22 dBm TX only) |
| 2 | FM-2 | Frost/ice film inside the mated SMA interface | 1 | B | humid air sealed in interface condenses on cold internal faces; er step + lossy film in the gap | HIGH | HIGH | Reversible (dries) | YES — S11/IL/phase of conducted path | No |
| 3 | FM-3 | Ice expansion (9 %) in interface degrading mating plane / cracking PTFE bead | 1 | B | water in threads/gap freezes, jacks faces apart, loads bead | MEDIUM | MEDIUM (harder ice, more mass) | **PERMANENT** (lifted face, cracked bead) | YES (reference-plane drift) | YES |
| 4 | FM-4 | DUT-board condensation (sealed-bag breach): solder, pads, USB-C port | 3+7 | A+B | bag breach lets 22-57 C-below-dew-point air reach board | MEDIUM (bag is protocol) | MEDIUM | Frost reversible; corrosion + residue PERMANENT | YES (RF path + serial) | YES — USB-C VBUS short on thaw = destruction class |
| 5 | FM-5 | Thread galling / torque loss from differential contraction + ice in threads | 1 | B | CTE mismatch 45-65 K swing; frozen thread on disassembly | MEDIUM | MEDIUM-HIGH | Torque loss reversible; **galling PERMANENT** | YES (mating-plane reference) | YES |
| 6 | FM-6 | O-ring / elastomer seal: compression set + low-T stiffening | 6 | B (+chamber gasket UNKNOWN) | nitrile near/below TR-10 at -40 loses squeeze; cyclic set | LOW (both materials OK at -20) | LOW (silicone) / **MEDIUM-HIGH (nitrile)** | Compression set **PERMANENT**; stiffening reversible on warm-up | Indirect (feeds moisture supply to FM-1..4) | YES (seal) |
| 7 | FM-7 | Bulk cable tempco: attenuation + phase vs temperature | 2+5 | B | conductor rho drops ~20 % over 60 K; PTFE er tempco ~200 ppm/K | CERTAIN (small) | CERTAIN (small) | Reversible (recovers with T) | NO for decode-count (computed 2.7); YES for any phase/power-quantitative variant | No |
| 8 | FM-8 | Jacket stiffening -> bend-radius violation -> shield deformation | 5 | A (USB-C) + B (RG316) | PVC/PU-type jacket modulus rises at cold; forced bend kinks braid | HIGH at tight routing | HIGH | Jacket recovers; **shield kink PERMANENT** | YES (impedance bump = standing-wave/IL change) | YES |
| 9 | FM-9 | Pressure-driven inflow through imperfect seals during cooldown | 6 | A+B | sealed volume at -40 C: P drops to 233/298 = 78 % of load-time P -> ~0.22 atm inward ΔP; -20 C: 85 %, ~0.15 atm | MEDIUM | MEDIUM | Reversible (pressure returns on warm-up) | Indirect (feeds moisture supply) | No |
| 10 | FM-10 | Solder-joint CTE fatigue from thermal cycling | 3 | A+B | SAC joint cycled 45-65 K; Coffin-Manson class (thousands of cycles at this ΔT) | LOW | LOW-MEDIUM | **PERMANENT** when it occurs; intermittent high-R before open | YES (drift-then-fail) | YES |
| 11 | FM-11 | PTFE bulk moisture uptake / micro-cracking | 2 | B | uptake <0.01 % (negligible); micro-cracking not expected above Tg -97 C | LOW | LOW | Reversible (dries) / PERMANENT if crack | NO (VF change negligible, 2.7) | Only via FM-3 bead crack |
| 12 | FM-12 | Warm-side active electronics condensation (ref TX, host, any future LNA/instrument) | 7 | A+B | cold metalwork extends below lab dew point near the feedthrough; ref TX placed adjacent gets frost | LOW (protocol keeps ref TX at room temp away from chamber) | LOW-MEDIUM (bigger cold footprint) | Frost reversible; corrosion PERMANENT | YES (reference drift corrupts OTA baseline) | YES (corrosion) |
| — | FM-13 | Wire-dipole frost loading (bonus, scope 5-adjacent) | 5 | A | ice layer on 8.6 cm legs adds dielectric, detunes resonance | CERTAIN (thin) | CERTAIN (thicker) | Reversible (dries) | YES only if link operates at decode edge (link budget says margin exists) | No |

Cross-check vs the 7 scope items: 1 -> FM-2, FM-3, FM-5; 2 -> FM-7, FM-11;
3 -> FM-4, FM-10; 4 -> FM-1; 5 -> FM-7, FM-8, FM-13; 6 -> FM-6, FM-9;
7 -> FM-4, FM-12. No scope item is uncovered.

---

## 2. Per-mode detail

### 2.1 FM-1 — Ice bridging center pin to shield (scope 4)

**Where the exposed interfaces are.** Variant B has three mated SMA
pairs (DUT/bulkhead-cold-side, bulkhead/warm-side, cable ends) plus any
temporarily unmated connector face (dust-cap-free open jack, or the
DUT's spare J2 "SMA-2G4" port if nothing is mated to it — two SMA
edge-launch connectors exist on the board, `hub_board_f33.kicad_pcb`
via `fe700201`, and a spare open jack inside a frost zone is a live
antenna for this mode). Variant A has the DUT-side SMA mated to the
dipole/stub plus possibly one open jack.

**Mechanism.** Frost deposits directly on any exposed dielectric/metal
interface (moisture supply certain, Section 0). A frost layer bridging
the pin-to-shield gap is a lossy shunt: resistivity ~10^7-10^8 Ohm·m
pure, lower with ionic contamination (finger oils, flux residue —
`65c9c3df` 3d), and at RF a complex shunt admittance (er ~3.2 + loss
tangent 0.001-0.01, higher if contaminated). Effects: return-loss
degradation (impedance of the interface region changes), added loss,
and if the bridge reaches the center pin, intermittent shunt leakage.
The shunt impedance is time-varying (frost grows during the soak,
cracks with handling/vibration, partially melts near 0 C during ramps)
— i.e. it moves the DUT's effective decode threshold *between scan
points*.

**Effect on S11/return loss and low-level measurements.** S11
degradation is guaranteed in degree, small-to-moderate in size (thin
film); for the decode-count edgescan the damage path is not S11 per se
but the decode-edge shift: excess insertion loss or detuning moves the
band where the DUT still decodes the reference. Because edgescan
locates an *edge* (offset band where decode stops), any path change
larger than the offset step size aliases directly into the measured
"required compensation". A bridge that forms during one soak point and
grows between points shifts each point by a different amount -> the
fit residual rises (>5 ppm RMS flags it, `65c9c3df` quoting the fit
guidance). A bridge that exists uniformly for the whole scan shifts
every point the same way -> **low residual, wrong k** — the fit's own
quality check cannot see it. That is the top-ranked danger.

**-20 vs -40:** CERTAIN at both given the moisture supply; -40 C grows
frost faster (larger vapor-pressure deficit) and the ice is harder
(`65c9c3df` 2d: "colder, more mechanically aggressive"), so the shunt is
thicker and changes more abruptly with handling.
**Reversible:** fully — the bridge sublimates/dries on warm-up. But the
corruption it produced in the run's data is permanent (bad points
recorded).
**Data vs HW:** corrupts data; no hardware destruction at these power
levels (+22 dBm reference, no arcing energy).

### 2.2 FM-2 — Frost/ice film inside a MATED interface (scope 1a)

**Mechanism.** A mated SMA pair is not hermetic: the coupling-nut thread
path and the pin-gap are open to air that was trapped at mating time. If
mated in humid lab air and then cooled 45-65 K below the lab dew point
(the interface IS cold-side or below), the trapped moisture condenses ON
the internal mating faces and freezes: a dielectric film (er ~3.2, tan d
0.001-0.01) inside what should be an air/PTFE gap, plus a possible film
on the pin contact (raises DC contact resistance, intermittently).
Result: impedance discontinuity (reflection), added insertion loss, and
phase-length change of the interface region (`65c9c3df` 3a, which
identifies this as "a direct measurement corruption").

**-20 vs -40:** HIGH at both (requires trapped humidity + cold; both
present). At -40 C the interface is further below the frost point, so a
larger fraction of the trapped water has deposited, and it stays frozen
through the whole hold (no partial melt near 0 C as can transiently
happen at -20 C ramps).
**Reversible:** yes — dries out on warm-up; but the mating faces may
keep a residue film (see FM-3/FM-5 for the permanent sub-modes).
**Data vs HW:** corrupts data (S11/IL/phase of the conducted path);
hardware intact.

### 2.3 FM-3 — Ice expansion degrading the mating plane (scope 1b)

**Mechanism.** Water in the threads/bead gap expands ~9 % on freezing
(`65c9c3df` 3a), exerting force: it can lift the mating faces apart
(degrading the outer-conductor reference plane — the connector's
mechanical impedance datum), and can crack the PTFE dielectric bead
(PTFE is above its Tg (-97 C) and remains ductile, `65c9c3df` 3b, but the
bead is thin and geometrically constrained). The prior report judged
permanent deformation of a *properly torqued* SMA unlikely ("rated for
significant mechanical load") — with the same caveat carried here: no
torque spec is enforceable until the SMA torque wrench on the BOM
(`55585471` step 3b.4) exists, and finger-tight mating lowers the
threshold for face-lift dramatically.

**-20 vs -40:** MEDIUM both; -40 C worse (harder ice exerts force more
brittle-ly, and more total water has deposited).
**Reversible:** NO — lifted faces, galled/deformed threads, cracked
beads are permanent; the connector may still "work" but with a degraded
reference plane.
**Data vs HW:** both — reference-plane drift corrupts every subsequent
measurement made through that connector; the connector is damaged.

### 2.4 FM-4 — DUT-board condensation on bag breach; USB-C port; thaw-out (scope 3+7)

**Mechanism.** The protocol's only DUT-side protection is the sealed bag
(fork README `d7ae93fa` verbatim; `65c9c3df` section 5). A breach
(any unsealed seam, puncture during placement, or re-opening mid-campaign)
exposes bare PCB, solder joints, castellated module pads, and the
USB-C receptacle to air 22-57 C below its dew point: frost directly on
conductors. With ionic contamination (flux residue, finger oils) each
freeze/thaw accelerates corrosion at joints (`65c9c3df` 3c).

**The thaw-out window is the destruction risk.** During extraction to
lab air all frost melts within minutes: liquid water (conductive once
contaminated) on a *powered* board. The USB-C receptacle carries 5 V on
VBUS — liquid bridging VBUS to ground/data in the receptacle is a
short/degradation path for the port and potentially the SuperMini's
USB-CDC (the DUT's only measurement/control interface, `/dev/ttyACM0`).
Frost itself (frozen, ~10^7-10^8 Ohm·m) is far less dangerous than the
thawed film.

**-20 vs -40:** likelihood gated by bag integrity (MEDIUM both — it is
a protocol-discipline failure, not a setpoint physics one); severity
higher at -40 (more deposited mass melts at once).
**Reversible:** frost dries; corrosion, residue, and any USB-C damage
are permanent.
**Data vs HW:** both — serial corruption loses/drops decode counts
(campaign data), RF path films corrupt it; hardware destruction
possible (USB-C short).

### 2.5 FM-5 — Thread galling / torque loss (scope 1c)

**Mechanism.** Differential contraction across the 45-65 K swing:
brass ~19 vs stainless ~17 ppm/K (`65c9c3df` 3a) -> ~0.1-0.11 %
dimensional change over 60 K; on a 5 mm thread radius that is ~6 um of
relative shift — enough to change joint preload (loosening OR
over-clamping depending on which part contracts more), not enough to
yield sound hardware. Water that entered the thread and frozen acts as
a spacer and abraive: disassembly under ice load can gall the thread
(the `65c9c3df` 3a note). Preload loss also feeds FM-2/FM-3: a looser
joint opens the interface gap.

**-20 vs -40:** MEDIUM at -20; MEDIUM-HIGH at -40 (bigger ΔT from
assembly torque temperature, more ice mass in threads).
**Reversible:** torque loss is reversible (re-torque warm); galling and
thread damage are permanent.
**Data vs HW:** both (mating-plane reference drift; damaged threads).

### 2.6 FM-7 — Bulk cable temperature response: attenuation, phase, and the calibration question (scope 2+5)

**What actually changes with temperature (mechanism):**

- **Conductor loss:** copper resistivity falls ~0.39 %/K
  [INDUSTRY-TYPICAL tempco, UNVERIFIED on host]; over a 60 K cooldown
  that is ~-20 % resistance -> conductor-dominated attenuation drops
  ~10 % (sqrt scaling). For RG316 at 868 MHz (~0.3 dB/m, mostly
  conductor loss at this frequency) on 0.65 m total: ~0.2 dB at room
  -> ~0.02 dB improvement at -40 C. Computed from the BOM loss figure
  (`55585471` step 5: ~0.3 dB/m at 1 GHz class).
- **Dielectric phase:** er of PTFE is ~2.1 with tempco ~200 ppm/K
  (`65c9c3df` 3b). Phase scales as sqrt(er): d(phi)/phi ~ 100 ppm/K.
  Over the 60 K swing: 0.6 %. Electrical length of 0.5 m RG316 at
  868 MHz: L*f*sqrt(er)/c = 0.5 x 8.68e8 x 1.449 / 3e8 = 2.1
  wavelengths -> 2.1 x 360 x 0.006 ~= **4.5 degrees** total phase
  change. (PTFE is also known in the coax industry for a dielectric
  step near -20 C — INDUSTRY-KNOWN, **UNVERIFIED on host, no outbound
  fetch per operator constraint**; flagged for verification before any
  phase-quantitative use.)
- **Jacket/dielectric mechanical:** jacket shrinks (PVC-class CTE
  ~10x metal); axial shrink of the cable vs the connector pulls on the
  termination — a strain mechanism feeding FM-8.

**Does the measurement need a cable-level temperature calibration?**

- **For the primary/edgescan decode-count protocol: NO.** The
  measurement is a decode threshold with ~165 dB link budget
  (`55585471` step 5: ref TX +22 dBm, DUT sensitivity -143 dBm); total
  conducted-path losses ~0.3-0.5 dB and their ~0.02 dB temperature
  variation, and 4.5 deg of phase, cannot move a decode decision. The
  reference TX stays at room temperature by protocol (fork README:
  "keep it at room temperature"), so the cable tempco affects only the
  fixed conducted path, not the reference.
- **For any phase- or power-quantitative variant (if one is ever
  introduced): YES** — then the cable pair becomes part of the
  measurement and its phase/loss vs temperature must be characterized
  (or the cable held at constant temperature). This is a conditional
  answer, recorded because the question was asked explicitly.

**-20 vs -40:** CERTAIN (small) at both; monotonic with ΔT, larger at
-40 C.
**Reversible:** fully — recovers with temperature, no hysteresis
expected below jacket damage thresholds.
**Data vs HW:** no data impact for decode-count (computed above);
hardware intact.

### 2.7 FM-8 — Jacket stiffening, bend-radius violation, connector strain (scope 5)

**Mechanism.** Coax/USB-C jacket polymers (PVC/PU-class) rise in
modulus as temperature drops [INDUSTRY-TYPICAL polymer behavior,
UNVERIFIED for any specific part — no cable datasheet on host]. A cable
routed at its minimum bend radius at room temperature becomes
effectively below minimum bend radius when cold: the cold jacket cannot
flex, so the shield braid takes the strain — deforming into an
impedance kink (permanent), and transmitting force into the connector
terminations (feeding FM-5 preload loss and termination strain).
Relevant routing: the RG316 90-deg turn at the bulkhead needs R = 12.7 mm
static minimum [INDUSTRY NOMINAL, UNVERIFIED — `fe700201` 2b] with a
27.9 mm swept envelope; the USB-C cable at the gasket crossing (variant
A) has no on-record minimum bend radius (OD 4.0-5.0 mm itself
INDUSTRY-TYPICAL UNVERIFIED, `fe700201` 3c).

**-20 vs -40:** HIGH both where routing is tight (the cold-side cable
IS at chamber temperature); worse at -40 (stiffer jacket, more shrinkage
strain).
**Reversible:** the stiffness recovers; a braided-shield kink does not.
**Data vs HW:** a kink is a permanent impedance bump (standing waves ->
IL/ripple change, corrupting any quantitative RF measurement; for
decode-count, a small fixed loss — harmless given the budget); hardware
damage is real but cheap-hardware class.

### 2.8 FM-6 — O-ring / elastomer seal: glass transition and compression set (scope 6a)

**What is on record:** the project's own wall-pass pattern seals with
"SMA O-rings" (`enclosure/README_big.md`) and the enclosure family uses
2 mm AS568-compatible cord in "Nitrile or silicone"
(`enclosure/README.md:27,72`). The material is not chosen on record, so
both are analysed. The chamber's own door-gasket class is UNKNOWN
(fe700201 P2: geometry, durometer, compression all UNKNOWN).

**Mechanism.** An O-ring seals by elastic squeeze. Two cold failure
mechanisms: (a) the elastomer stiffens as it approaches its
glass transition — nitrile's TR-10 (retraction) is typically -26 to
-46 C depending on ACN content [INDUSTRY-TYPICAL, UNVERIFIED on host]:
at -40 C a typical nitrile is at or below its limit and loses live
squeeze; silicone's Tg is ~-55 to -65 C [INDUSTRY-TYPICAL, UNVERIFIED]
so it stays elastic at -40 C. (b) compression set: sustained squeeze at
temperature permanently deforms the ring; cycling cold-hot accelerates
it. Both mechanisms reduce contact stress -> leak path.

**Consequence for THIS campaign:** the seal is not itself a measurement
path — a leaking feedthrough O-ring does not corrupt the RF signal; it
feeds the moisture supply (FM-1..FM-4 get more water at the worst place)
and degrades the chamber's hold capability (cold leak = frost supply
along the leak). The protocol's actual DUT seal is the bag (FM-4).

**-20 vs -40:** LOW at -20 C (both materials OK); at -40 C: LOW for
silicone, MEDIUM-HIGH for nitrile. Because the record does not pick the
material, the -40 C rating is "LOW-to-MEDIUM-HIGH pending the
procurement choice".
**Reversible:** stiffening is reversible (elasticity returns on
warm-up); compression set is permanent.
**Data vs HW:** indirect data impact; hardware (seal) damage in the
set case.

### 2.9 FM-9 — Pressure-driven inflow during cooldown (scope 6b)

**Mechanism (computed).** Any gas volume sealed at load time (chamber
with a decent gasket, gland, or even the bag's dead space) follows
P/T: cooling 25 C -> -40 C drops absolute pressure to 233/298 = 78 %
(-22 %, ~0.22 atm inward differential); 25 C -> -20 C gives 253/298 =
85 % (~0.15 atm). The differential drives outside (humid lab) air IN
through any imperfect seal — i.e. it actively pumps the moisture supply
to the coldest surfaces, and does so most strongly at -40 C. Note: the
bag itself is flexible — a bag partially collapses and equalizes
without pumping (the dev-case precedent for a rigid sealed box is a
Gore vent, `enclosure/README.md:32); the chamber's gasket class and
leak rate are UNKNOWN (`fe700201` P2).

**-20 vs -40:** MEDIUM both (any real gasket leaks; rate unknown);
roughly proportional to ΔP so ~1.5x worse at -40 C.
**Reversible:** yes — pressure returns on warm-up.
**Data vs HW:** indirect (feeds FM-1..FM-4); no direct damage.

### 2.10 FM-10 — Solder-joint CTE fatigue (scope 3)

**Mechanism.** The DUT's joints (SMA edge-launch launch pads, LR2021
castellated pads, USB-C receptacle anchors) see CTE mismatch cycling:
copper ~17, FR-4 in-plane ~13-17 / through-plane ~45-70 ppm/K
[INDUSTRY-TYPICAL, UNVERIFIED], SAC solder ~21-25 ppm/K, PTFE ~100-135
ppm/K in the connector. Each 25->-40->25 cycle is a 65 K shear cycle on
every joint; lead-free SAC fatigue life at this ΔT is in the
thousands-of-cycles class (Coffin-Manson-type behavior, exponent ~2)
[standard reliability-engineering practice, no on-host reference —
labeled UNVERIFIED]. The campaign plans ~3-4 cycles per run day
(`79ea692e` ramp plan) — far below any credible fatigue life for a
sound joint. The realistic risk is not fatigue of good joints but
ice-expansion stress on marginal ones (FM-3's mechanism applied to
solder menisci, `65c9c3df` 3c) and corrosion at contaminated joints.

**-20 vs -40:** LOW at -20 (45 K swing); LOW-MEDIUM at -40 (65 K swing,
~2x the damage per cycle by ΔT^2 scaling).
**Reversible:** no — fatigue cracking is permanent and progressive;
the precursor is intermittent high-resistance (data drift) before the
open.
**Data vs HW:** both, but a low likelihood.

### 2.11 FM-11 — PTFE bulk moisture uptake / micro-cracking (scope 2)

**Mechanism.** Bulk PTFE absorbs <0.01 % water (`65c9c3df` 3b) — bulk
dielectric constant/velocity factor change from moisture uptake is
negligible. Micro-cracking from freeze/thaw is not expected at -20/-40 C
because PTFE is far above its Tg (-97 C) and remains ductile
(`65c9c3df` 3b). The dielectric's real cold exposure is the surface/bead
(FM-2, FM-3), not the bulk. The RG316 datasheet temperature rating on
record ("rated to -40 C", `55585471` step 4.2) covers both setpoints —
with the standing caveat that no specific vendor datasheet exists on
host and the procured part must be verified (RG316-class industry parts
are commonly rated below -40 C, but that is per-vendor data, UNVERIFIED
here).

**-20 vs -40:** LOW both.
**Reversible:** uptake reversible (dries); a crack, if it ever forms,
is permanent.
**Data vs HW:** no data impact (VF change negligible for decode-count,
2.6); hardware only via the bead-crack path (FM-3).

### 2.12 FM-12 — Warm-side active electronics (scope 7)

**What exists:** in the primary path there is no LNA, attenuator, or RF
instrument anywhere (USB census: no SDR/VNA/counter, `55585471` 1b).
The warm-side active hardware is: the reference TX (a MeshCore node,
explicitly kept at room temperature by protocol), the host serial link,
and the chamber controller (none exists — `766ac96d`). The DUT itself is
the cold-side active electronics (covered by FM-4; rated -40 to +85 C
operating).

**Mechanism.** The cold-bridge physics extends below the lab dew point
along any metal/heat-conductive path from the chamber (feedthrough body,
cable shields — `65c9c3df` 2b). A warm-side board placed against or near
that cold metalwork collects frost/condensation on its own connectors
and PCB; thaw-out leaves liquid water on active hardware. Corrosion at
connector contacts degrades reference-TX RF and serial over repeated
runs; a frost film on the reference TX's antenna connector shifts the
OTA baseline (the reference must stay ON-frequency for the compensation
to be meaningful — fork README sign-convention section: the model
compensates for a *warm* transmitter; a drifted reference corrupts every
point by a common-mode error that the fit cannot separate from DUT
drift).

**-20 vs -40:** LOW at both given protocol placement (room temperature,
away from the chamber); MEDIUM only if placement is adjacent to cold
metalwork. The -40 C setpoint has a larger cold footprint (colder
exterior faces, `65c9c3df` 2b), so the keep-clear radius is larger.
**Reversible:** frost yes; corrosion permanent.
**Data vs HW:** both, protocol-gated likelihood.

### 2.13 FM-13 — Wire-dipole frost loading (scope 5-adjacent, included for completeness)

**Mechanism.** The primary-path antenna (wire dipole, 8.6 cm legs,
`fe700201` 3a) accumulates frost in the cold zone: an ice layer is a
dielectric loading on the legs (er ~3.2) — it detunes the resonance
downward and adds loss, i.e. a time-growing link-budget penalty inside
the chamber. For the decode-count measurement this only matters if the
link is operating near the decode edge; the link budget has large
margin (`55585471` step 5). Listed because it is a real cold-zone RF
effect on the primary path's only RF element, ranked last for that
reason.
**-20 vs -40:** CERTAIN (thin) / CERTAIN (thicker, faster growth —
vapor-pressure deficit).
**Reversible:** fully (sublimates/dries).
**Data vs HW:** data only at the decode edge; no hardware damage.

---

## 3. -20 C vs -40 C: regime summary

| Aspect | -20 C | -40 C | Ground |
|---|---|---|---|
| Moisture deposition | certain (21.9 C below best-case dew point) | certain, faster accumulation (41.9 C below) | `65c9c3df` 2d |
| Exterior feedthrough face | est. -5 to -15 C | est. -15 to -30 C | `65c9c3df` 2b |
| Ice character | softer, near-melting, adhesive, can transiently melt near 0 C during ramps | harder, "more mechanically aggressive" | `65c9c3df` 2d |
| PTFE dielectric | above Tg, ductile, fine | same (Tg -97 C) | `65c9c3df` 3b |
| Cable rating | within "rated to -40 C" | at the rating's edge; vendor verification REQUIRED at procurement | `55585471` 4.2 |
| Elastomer seal | both nitrile and silicone OK | nitrile at/below typical TR-10; silicone OK | Section 2.8 (UNVERIFIED ranges) |
| DUT radio | mid-range | ON the operating-range edge (Table 3-2: -40 min); abs max -55 C | LR2021 Rev 2.1 (on host) |
| Pressure inflow ΔP | ~0.15 atm | ~0.22 atm | Section 2.9 (computed) |
| Thermal-cycle damage per cycle | 45 K swing | 65 K swing (~2x by ΔT^2) | Section 2.10 |

Both setpoints produce the same *kind* of every failure mode; -40 C is
worse in degree for FM-1, FM-3, FM-5, FM-7, FM-8, FM-9, FM-10, FM-13,
and materially different for FM-6 (nitrile) and FM-4/7 (DUT at its
rating edge, zero margin).

---

## 4. Explicit answers to the sub-questions posed by the scope

1. *Frost/ice on the mating plane as dielectric gap/contaminant?* Yes —
   er ~3.2 film with tan d 0.001-0.01 changes the interface impedance
   (FM-2); reversible; corrupts conducted-path S11/IL/phase.
2. *Ice expanding in the interface degrading the mechanical reference
   plane?* Yes — 9 % expansion can lift faces/crack the bead (FM-3);
   permanent; both data and hardware.
3. *Thread galling/torque loss?* Yes — CTE mismatch over 45-65 K
   changes preload (~0.1 % dimensional, ~6 um at a 5 mm radius); ice in
   threads galls on disassembly (FM-5); torque loss reversible,
   galling permanent.
4. *PTFE moisture uptake/micro-cracking changing VF/IL/phase?* Bulk:
   no (<0.01 % uptake, Tg -97 C — FM-11). Surface/interface: yes
   (FM-2). Bulk phase tempco exists but is 4.5 deg over the full swing —
   negligible for decode-count (FM-7).
5. *Solder/center-pin CTE fatigue at -20/-40?* Real mechanism, LOW
   likelihood at the campaign's ~3-4 cycles (thousands-of-cycles class
   at 65 K) — FM-10; permanent when it occurs.
6. *Ice bridging pin-to-shield and its effect on S11/low-level
   measurements?* Yes — certain wherever an exposed interface exists;
   time-varying shunt corrupts decode-edge scans, including the
   low-residual wrong-k class the fit check cannot catch (FM-1).
7. *Bulk cable effects + cable-level temperature calibration needed?*
   Jacket stiffening/bend-radius violations: real and HIGH at tight
   routing (FM-8). Attenuation/phase tempco: certain but negligible for
   decode-count; **calibration NOT needed for the current protocol;
   needed for any phase/power-quantitative variant** (FM-7).
8. *Feedthrough O-ring glass transition/compression set, seal
   integrity, connector-to-panel differential contraction loosening the
   mount?* Nitrile at -40 C is at/below typical TR-10 (MEDIUM-HIGH);
   silicone OK (LOW); compression set permanent. Mount loosening:
   connector-to-panel differential contraction over 65 K is ~0.1 %
   (~6 um class) — loosening is possible on a marginal mount, reversible
   by re-torque (folded into FM-5's mechanism class). Vacuum: no
   vacuum chamber exists on any record — vacuum-integrity mode is
   N/A-unverifiable; pressure inflow IS real and computed (FM-9).
9. *Warm-side active electronics?* None exists in the RF path
   (no instrument); reference TX is protocol-kept at room temperature;
   likelihood LOW unless placed against cold metalwork (FM-12). The
   genuinely exposed active hardware is the DUT itself (FM-4).

---

## 5. Sources

| claim | source | confidence |
|---|---|---|
| Dew-point grid, 22-57 C margins, condensation CERTAIN at both setpoints | `bench/condensation-risk/REPORT.md` (`65c9c3df`), Magnus/Alduchov-Eskridge script | HIGH (prior committed report, recomputed there) |
| Ice er ~3.2 / water ~80, tan d 0.001-0.01, resistivity 10^7-10^8 Ohm·m, +9 % expansion | `65c9c3df` sources table (von Hippel; Hobbs, "Ice Physics") | HIGH (well-established) |
| PTFE: Tg -97 C, <0.01 % moisture absorption, er ~2.1, tempco ~200 ppm/K | `65c9c3df` (DuPont Teflon PTFE class datasheets) | HIGH |
| CTE stainless ~17 / brass ~19 ppm/K | `65c9c3df` | HIGH |
| CTE copper ~17 / PTFE ~100-135 / SAC ~21-25 / FR-4 in-plane 13-17, z 45-70 ppm/K | INDUSTRY-TYPICAL material data — **no datasheet on host, UNVERIFIED** | MEDIUM (standard values) |
| Cable temp rating "both are rated to -40 C (PTFE dielectric)" | BOM report `55585471` step 4.2 (the project's own claim; **no vendor datasheet on host**) | MEDIUM (on-record claim, part UNVERIFIED) |
| Representative parts whose vendor datasheets apply: Amphenol 132134-class SMA bulkhead, ACX-1169-class RG316 patch, SMA torque wrench 0.9 N·m | `55585471` step 3b | MEDIUM (representative, not on-hand inventory) |
| Seal elastomer on record: SMA O-rings; 2 mm AS568 cord "Nitrile or silicone" | `~/repos/balloon/tracker/hardware/enclosure/README_big.md:23`, `enclosure/README.md:27,72` (read this session) | HIGH (project files, verbatim) |
| Nitrile TR-10 ~-26..-46 C (ACN-dependent); silicone Tg ~-55..-65 C; compression-set behavior | INDUSTRY-TYPICAL elastomer data — **no elastomer datasheet on host, UNVERIFIED** | MEDIUM (standard ranges; material not picked on record) |
| ASA enclosure "-20C to +90C" (no on-record material rated -40 C) | `enclosure/README.md:46` | HIGH (verbatim) |
| Gore-Tex vent precedent for pressure equalization | `enclosure/README.md:32` | HIGH (verbatim) |
| LR2021 operating -40..+85 C, abs max -55..+125 C | NiceRF LR2021/LR2022/LR2012 datasheet Rev 2.1, Tables 3-1/3-2, p.37 — **on-host PDF** (`~/repos/balloon/docs/LR2021_LR2022_LR2012_Datasheet_Rev2.1.pdf`), extracted this session with pdftotext | HIGH (manufacturer datasheet) |
| Measurement chain: OTA edgescan, decode counts, room-temp reference TX, sealed bag, k/T0 fit, >5 ppm residual guidance | fork README `d7ae93fa:examples/passive_mapper/bench/README.md` + `thermal_bench.py` (read via `git show` this session) | HIGH (primary sources) |
| Conducted-path insertion loss ~0.3-0.5 dB, 165 dB link budget, no recalibration needed | `55585471` step 5 | HIGH (prior committed report) |
| RG316 OD 2.5 mm, bend radius 12.7 mm (INDUSTRY NOMINAL UNVERIFIED), swept envelope 27.9 mm | `fe700201` step 2 (prior committed report, labels carried) | MEDIUM (as labeled there) |
| Chamber/feedthrough do not exist; penetration inventory all UNKNOWN | `fe700201`, `24eb918c`, `766ac96d`, `72f3aab9` (sibling cards, this session's commits) | HIGH (exhaustively verified on record) |
| Setpoints +25/0/-20/-40 C, ~3-4 ramps/session | card `72f3aab9`, ramp-feasibility `79ea692e` | HIGH |
| Copper resistivity tempco ~0.39 %/K; conductor-loss sqrt scaling; Coffin-Manson ΔT^~2 solder fatigue class | standard electrical/reliability engineering — **no on-host reference, labeled UNVERIFIED** | MEDIUM (standard practice) |
| PTFE dielectric step near -20 C (known coax-industry effect) | INDUSTRY-KNOWN — **UNVERIFIED on host, no outbound fetch per operator constraint** | LOW-MEDIUM (flagged for verification) |
| Phase/attenuation computations (4.5 deg, ~0.02 dB, 0.6 % VF) | computed this session from the cited er/CTE/loss inputs; arithmetic shown in 2.6 | HIGH (arithmetic from labeled inputs) |

**On "vendor environmental notes":** no connector-vendor environmental
note (Amphenol/Hubner+Suhner class) is on host, and no outbound fetch is
permitted (standing operator constraint, reaffirmed by this session's
denied commands). The vendor guidance layer of this catalogue therefore
rests on (a) the BOM's representative part numbers as *the parts whose
datasheets must be consulted at procurement* (`55585471` 3b), and
(b) the standard-material data layer of `65c9c3df`. Every claim that
would require a vendor note is labeled UNVERIFIED above.

---

## 6. Caveats and honest gaps

1. **No chamber exists.** No feedthrough, gasket, gland, or door has
   been located on any record (`fe700201` P1-P5 all UNKNOWN). All
   feedthrough-specific modes (FM-3/5/6/9) are therefore conditional on
   the hardware class the fit task (`t_48e048a1`) will meet.
2. **No cable, connector, or O-ring is on hand.** Every dimension,
   rating, and material value specific to a part (RG316 bend radius,
   jacket polymer, O-ring material choice, cable temp rating) is
   INDUSTRY-TYPICAL and UNVERIFIED — labeled per row in Section 5. The
   procured parts' datasheets replace these labels.
3. **Likelihood ratings are physics priors, not observations.** No run
   has occurred (`65c9c3df` caveat 4). The ratings assume the moisture
   supply established by the dew-point grid and zero mitigation.
4. **The O-ring material is not picked on record** ("Nitrile or
   silicone") — the -40 C seal rating spans LOW-to-MEDIUM-HIGH until
   procurement decides it.
5. **The -40 C setpoint rides the DUT's datasheet edge** (-40 to +85 C
   operating). Any mechanism that makes the die colder than chamber air
   has no rated margin beneath it; abs max -55 C is only 15 C below the
   setpoint.
6. **Operator-denied actions this session (recorded, not retried):**
   fleet-state lookup (card-ID recovery) and a hermes-profile directory
   search. Both denials are consistent with standing constraints; the
   report loses only the card-ID citation, noted in the header.

---

## 7. Nothing fabricated

Every material property cited is either (a) committed in a prior bench
report with its own source table (`65c9c3df`, `55585471`, `fe700201`),
(b) verbatim from project files read this session (enclosure READMEs,
fork README, thermal_bench.py via git show), (c) extracted this session
from the on-host LR2021 datasheet PDF, or (d) labeled INDUSTRY-TYPICAL /
UNVERIFIED. The three computed quantities (phase shift, loss change,
pressure ratio) show their arithmetic inline. No frost was observed, no
chamber was inspected (none exists), and no vendor document was
consulted (none on host, no outbound fetch). No mitigation is
recommended anywhere in this report, per the acceptance criteria.

---

## 8. Handoff to the mitigation task (what it must cover — not how)

The mitigation task (next card) receives from this catalogue:

1. **A ranked target list**: FM-1 and FM-2 (mating-plane moisture — the
   only modes that can silently corrupt the k/T0 blob), FM-3/FM-5
   (permanent connector damage), FM-4 (bag integrity + USB-C
   thaw-out), FM-6 (nitrile-vs-silicone -40 C decision), FM-8
   (routing/bend margin), FM-9 (pressure inflow).
2. **The low-residual-wrong-k hazard** (2.1): mitigations that only
   address run-visible corruption (residual spikes, dropped points)
   do not cover this mode; it must be prevented at the source, not
   detected in the fit.
3. **The answered calibration question** (2.6): no cable temperature
   calibration is required for the decode-count protocol; the mitigation
   task should not spend effort there.
4. **UNVERIFIED blockers that prevent quantification** (replace before
   the mitigation task can size anything): RG316 vendor bend radius
   and temp rating; USB-C overmold and jacket spec; O-ring material
   choice and its TR-10/compression-set datasheet; chamber gasket
   class; SMA torque practice (wrench from `55585471` 3b.4). None of
   these values exist on any record today.