# Warm-side active-electronics failure modes — condensation on cold-soaked boards, ingress, drift (single structured entry)

Task (fleet offload, meshcore): catalogue instrument-side electronics
failure modes; produce one structured entry for the warm-side active
electronics (LNA, attenuator, sensor, bias tee). Scope: mechanism
(condensation on cold-soaked boards after re-entry to warm humid air,
moisture ingress into enclosure, gain/offset drift or failure),
likelihood at -20 C vs -40 C, reversible vs permanent, consequence
class; what active element would typically sit there and what its own
environmental rating covers. **No mitigation content** (per acceptance).

Date: 2026-09-15 · Repo: meshcore (main) · Worker: dq05.
Artifacts: this directory (`bench/warm-side-electronics-failure-modes/`)
— `condensation_window.py` + `output.txt` (re-entry window model),
`ipx0_verify.py` + `output_ipx0.txt` (CE-RED form selection verification).

---

## 0. Census first — what actually sits on the warm side of this bench

The task names LNA, attenuator, sensor, bias tee as the nominal warm-side
active chain. For THIS bench the census is settled on record:

- **No RF instrument, LNA, attenuator, or bias tee exists on this host or
  in the measurement chain** — USB census commits `c5eb3c58`
  (instrument-rf-connectors) and `55585471` (rf-feedthrough-bom, step: "no
  RF instrument on host (USB census: no SDR/counter/VNA/GPSDO)"), with 4
  prior concurrences (72f3aab9, c4be4400, 55585471, 04db4fae). The
  passive_mapper edgescan is OTA decode-count: DUT LR2021 inside the
  chamber, reference TX outside at room temperature.
- The warm-side ACTIVE electronics that actually exist in this campaign
  are: (1) the **reference TX** — "any MeshCore node" (fork README
  `d7ae93fa`, bench/README.md:50: "keep it at room temperature"), whose
  active element is the same LR2021-class radio; (2) the **host-side
  sensor chain** — the DUT's own die temperature sensor ("The die sensor
  sits next to the PA", fork README `d7ae93fa` bench/README.md:182) and
  the chamber's built-in air-temperature sensor (chamber-log-protocol
  A.3, PROTOCOL.md:32-38, sensor id field PROTOCOL.md:156); (3) the
  **chamber's own control electronics**. No warm-side LNA / attenuator /
  bias tee is deployed or planned in the primary path (55585471: primary
  path needs ZERO RF components; optional conducted variant B adds only
  a passive SMA bulkhead + RG316 — still no active element).
- Therefore this entry covers the failure modes as specified, with the
  understanding that the exposed warm-side active element in this
  campaign is the reference TX / die sensor / chamber electronics class,
  not a front-end LNA chain. **If a conducted variant B or any future
  instrument (LNA, step attenuator, bias tee, power sensor) is added to
  the warm side, every mode below applies to it identically in kind.**

## 1. The structured entry — WAE-1: warm-side active electronics, condensation + ingress + drift

| # | ID | Mode | Mechanism | Likelihood @ -20 C | Likelihood @ -40 C | Reversible? | Consequence class |
|---|----|------|-----------|--------------------|--------------------|-------------|-------------------|
| 1 | WAE-1 | Cold-soaked active board re-enters warm humid air → condensation film across active circuitry; enclosure moisture ingress; gain/offset drift or hard failure | (a) below | (b) below | (b) below | (c) below | (d) below |

### 1a. Mechanism

**Condensation on cold-soaked boards after re-entry.** Any warm-side
active board that has been pulled down toward the setpoint temperature
(through the feedthrough thermal bridge, enclosure wall conduction, or
by being staged inside the chamber and taken out) becomes a condensation
trap the moment it re-enters warm humid lab air. The prior environmental
baseline (182d4755) established the numbers for exactly this geometry:
the coldest warm-side surface is **the setpoint itself** (-20 C at the
-20 C setpoint, -40 C at the -40 C setpoint — feedthrough spans
continuously from chamber wall to lab air); the RH threshold for
condensation on that surface is **RH > 5.4/4.8/4.0 % at -20 C and
RH > 0.8/0.7/0.6 % at -40 C** for ambient 20/22/25 C — every assumed
grid cell (30-60 % RH) exceeds these by **>6x**, so condensation is
certain at both setpoints under every assumed ambient. Condensate
arrives as **liquid** at the Td isotherm (+1.9..+16.7 C across the grid)
and freezes only where the surface is below 0 C (182d4755: no sub-zero
frost point in any cell — coldest cell 20 C/30 % has e = 700.0 Pa >
611.2 Pa triple point).

**What the film does to active circuitry** (mechanism, not mitigation):
a liquid water film on a powered or unpowered board is a shunt network
across bias nets, feedback dividers, high-impedance nodes, and RF pads.
Water: er ≈ 80, resistivity ~10^5-10^6 Ohm·m for pure water dropping to
~10^2-10^3 Ohm·m with ionic contamination (65c9c3df recorded ice
resistivity ~10^7-10^8 Ohm·m and er 3.2; liquid water is conductively
worse for circuits than ice). On a warm-side LNA/attenuator/bias-tee
chain this appears as: gain error and offset drift in the first seconds
of re-entry; if the film bridges a bias-tee DC path or an LNA gate
bias divider, the DC operating point moves — the RF chain remains
"on" but wrong. ESD/latch-up margins do not protect a wet board: the
LR2021's own ratings are JEDEC JS-001 Class 2 HBM (±2 kV), JS-002
Class 2a CDM (±500 V), latch-up 100 mA (Rev 2.1 datasheet Table 3-3) —
those are dry-device ratings.

**Re-entry window duration (COMPUTED, condensation_window.py, output.txt).**
Board surface warms from setpoint T_s toward ambient T_a with one time
constant tau: condensation persists until the surface crosses the
ambient dew point Td, i.e. window = tau·ln((T_a-T_s)/(T_a-Td)). At the
22 C/50 % cell: 1.35·tau from a -20 C soak vs 1.74·tau from a -40 C
soak; across the 12-cell grid the -40 C window is **1.22x-1.51x** the
-20 C window (ratio grows as RH falls — the drier the cell, the further
the surface must climb to cross the lower Td). Instantaneous flux driver
(e_ambient - es_ice(surface)) is nearly flat: 1.06-1.13x from -40 C vs
-20 C at re-entry (30/50/60 % RH at 22 C). **The -40 C setpoint therefore
differs from -20 C mainly in duration of exposure and frost inventory,
not in the mechanism.**

**Moisture ingress into enclosure.** Cooldown of a sealed gas volume
follows P/T: a volume sealed at 25 C draws an inward differential of
**0.151 atm at -20 C and 0.218 atm at -40 C** (COMPUTED, cross-checks
04db4fae FM-9's committed 0.15/0.22 atm). Across any imperfect seal or
vent path this actively pumps humid air in throughout the soak; the
ingested moisture condenses on the coldest interior surfaces (chamber
wall or the feedthrough body) and remains as liquid/frost inventory
available for re-distribution on warm-up. The enclosure-level protection
is the project's own: "O-ring groove in lid (2mm cord, AS568 compatible)
— IP65+ sealing" (balloon repo, tracker/hardware/enclosure/README.md:27)
— an ingress rating against rain/jets/dust, **not** against a pressure
cycling regime; IP ratings say nothing about condensation on the
interior side of a sealed enclosure when the enclosed air is loaded with
moisture. And the module that would sit inside has NO ingress rating at
all: the LoRa2021-868 module was certified with **IPX0** (CE-RED EN
62368-1 report 8427EU011624S, "IP protection class: IPX0 [SELECTED]"
— form line verified by pixel analysis this session, `ipx0_verify.py`,
output_ipx0.txt; the alternative write-in box is empty) — meaning zero
protection from water ingress at module level. IPX0 module inside an
IP65+ enclosure = protection only as good as the enclosure seal, and
only against external liquid, never against internally generated
condensate.

**Gain/offset drift or failure.** Two sub-modes. (1) **Drift sub-mode —
reversible physics**: a wet or cold active element drifts. The reference
TX crystal drift is already modelled on record (fork README d7ae93fa
bench/README.md:10-20: AT-cut parabolic drift drift_ppm(T) = -k·(T-T0)^2,
k = 0.02..0.06 ppm/C^2) and the protocol keeps the reference warm to
hold the model valid — but the drift that matters on the warm side here
is the **gain/offset drift of any sensor or instrument chain** that the
wet film or the thermal excursion induces. (2) **Failure sub-mode —
electrochemical**: a powered wet board is an electrolytic cell; dendrite
growth, corrosion of exposed metallization, and conductive-anodic-
filament risk are permanent mechanisms; an unpowered wet board only
corrodes slowly (surface oxidation) and dries out without permanent
electrical change at these timescales unless contaminants are present.
Electrolysis requires both voltage and ionic path — bias tees and LNA
bias nets are the powered nodes most at risk in the nominal chain.

### 1b. Likelihood at -20 C vs -40 C

The likelihood ordering is set by three committed/computed facts:

1. **Condensation onset is CERTAIN at both setpoints** (182d4755: every
   grid cell exceeds the condensation RH threshold by >6x at both -20 C
   and -40 C) — the setpoint does not change whether condensation
   happens, only how much and for how long.
2. **The -40 C window is longer**: 1.22x-1.51x the -20 C re-entry
   window across all 12 assumed ambient cells (COMPUTED,
   condensation_window.py). More window seconds = more deposited water
   = higher electrolyte inventory per event.
3. **The -40 C soak pumps in more moisture during cooldown**: 0.218 atm
   inward vs 0.151 atm at -20 C (COMPUTED, 04db4fae FM-9 concurs).

Per mode: **condensation-on-re-entry: HIGH at -20 C, HIGH (and longer
window, 1.22-1.51x) at -40 C** — certain onset at both, worse in degree
at -40 C. **Moisture ingress into enclosure: MEDIUM at -20 C, MEDIUM-
HIGH at -40 C** — driven by the 0.15 vs 0.22 atm pump differential plus
seal stiffness (nitrile-class TR-10 -26..-46 C per 04db4fae FM-8
analysis: at -40 C an elastomer seal may sit at/below its TR-10, where
it loses compressive follow) — not a step change, a worsening degree.
**Gain/offset drift: CERTAIN-small at both setpoints** (every re-entry
condenses; the drift magnitude while wet is bounded by film thickness
and bias impedance, and the dry-out is hours). **Permanent
electrochemical failure: LOW at -20 C, LOW-MEDIUM at -40 C** — needs
powered wet metallization plus contamination; the longer -40 C window
raises the dose but the requirement (ionic contamination + voltage)
keeps it low in a clean lab.

### 1c. Reversible vs permanent

- **Reversible (condensation dries)**: the condensation film itself is
  fully reversible — water evaporates once the board is above the
  ambient dew point and RH allows; no metallization change occurs if the
  board was unpowered or the film was clean. Gain/offset drift
  attributable to the film, to cold-soak transistor parameters, or to
  the AT-cut parabolic crystal law (d7ae93fa) reverts with dry-out and
  warm-up. The 04db4fae catalogue precedent (FM-1 frost film: reversible)
  applies class-for-class.
- **Permanent (corroded electronics)**: electrochemical corrosion,
  dendrites, conductive-anodic-filament, and contact-pad erosion on a
  powered wet board are permanent; severity scales with time-wet and
  bias voltage. Also permanent: any corrosion of mating surfaces or
  connector pins held wet through multiple cycles — each re-entry adds
  cumulative dose; campaign cycle counts (3-4 thermal cycles per
  session, 79ea692e) multiply the exposure. The dividing line is
  **powered + contaminated + time-wet**; an unpowered clean board that
  gets wet and dries is a reversible event with no permanent residue at
  these timescales.

### 1d. Consequence class

Per the campaign's consequence taxonomy (04db4fae): **DEGRADES
HARDWARE / CORRUPTS DATA**, split by sub-mode:

- The **drift sub-mode is a DATA class** effect: a wet reference TX or
  wet sensor chain shifts gain/offset between scan points — the
  between-scan-points edge-shift class that the >5 ppm RMS fit check
  cannot catch when the shift is uniform (04db4fae FM-1 class
  analysis). For a decode-count edgescan this is a low-residual WRONG-k
  hazard, not a lost measurement.
- The **electrochemical sub-mode is DEGRADES HARDWARE (permanent)**:
  corroded bias nets, dendrite-shorted LNA gate bias, contact-pad
  erosion — hardware damage, repairable only by replacement. Not
  destruction-class at these energies (contrast FM-4 USB-C VBUS short
  on thaw, the campaign's one destruction-class mode per 04db4fae).
- Enclosure ingress feeding condensate onto boards is the **indirect
  data-corruption precursor**: it does not corrupt anything itself, it
  supplies the moisture that makes WAE-1's direct modes possible
  (same indirect-supply class as 04db4fae FM-9).

**Corruption character**: time-varying between scan points (film
thickness changes minute-scale as the board warms) — the
"untrackable-by-averaging" class; a uniform slow gain error is instead
the low-residual WRONG-k class (04db4fae 2.1). Both classes are covered:
the re-entry window model shows the wet phase lasts 1.2-2.1·tau — many
minutes of scan time — so per-scan-point gain differences are expected
during a scan that straddles re-entry.

### 1e. What active element typically sits there — and what its own rating covers

The warm-side active element in this campaign is the **reference TX
MeshCore node (LR2021-class radio on an ESP32-C3-class carrier)** and the
**sensor chain (DUT die sensor + chamber air-temperature sensor)**. A
nominal bench warm-side instrument chain (LNA, step attenuator, power
sensor, bias tee) does not exist here (census, section 0), but each
maps to the same active-element classes:

- **LR2021 chip** (Rev 2.1 datasheet): operating range Table 3-2
  **Top -40..+85 C**; absolute maximum Table 3-1 **Tmr -55..+125 C**
  (extraction: "Tmr Temperature -55 - 125 °C" at datasheet p.36-37
  extraction lines 2799-2807); **zero occurrences of humidity, moisture,
  or condensation anywhere in the 243-page datasheet** (verified by
  text-layer search this session) — the chip datasheet guarantees
  NOTHING about moisture. ESD Table 3-3: HBM 2 kV, CDM 500 V, latch-up
  100 mA — dry-device ratings.
- **LoRa2021-868 module** (V1.3 module datasheet, git `cc92c869`,
  docs/assets/lr2021/LoRa2021-Module-Datasheet-V1.3.pdf): "Operating
  Temperature −40 [to] +85 ℃" (extraction lines 204-212); **zero
  humidity/moisture/storage-conditioning specs** (text-layer search
  this session) — same absence.
- **CE-RED EN 62368-1 report 8427EU011624S** (git `cc92c869`, EUT =
  LoRa2021-868 module, applicant NiceRF): "Product group: end product
  built-in component" (raw line 59); "Manufacturer's specified Tma:
  Outdoor: 40℃" (raw line 97) — i.e. the safety assessment covers a
  **40 C outdoor ambient ceiling, not -40 C cold**; "IP protection
  class: IPX0" (raw line 98, **selection verified by pixel analysis**,
  this session) — no ingress protection; "5.4.1.5 Pollution degrees:
  PD2" (raw line 376) — PD2 per IEC 60664-1 is dry/condensation-free
  indoor-class, allowing only non-conductive pollution with occasional
  temporary condensation (the module is certified against a PD2
  environment, i.e. one where condensation is not a persistent
  condition).
- **CE-RED EN 300 220 report 8427EU011624W1** (git `cc92c869`): test
  environment "Relative Humidity 30% to 60%", "NT (Normal Temperature)
  +15℃ to +35℃", "Extreme Temperature -10℃ ~ 50℃ Note 1"
  (manufacturer-declared; extraction lines 631-644). **Both campaign
  setpoints (-20 C, -40 C) lie OUTSIDE the -10..+50 C extremes under
  which the module was radio-tested** — -40 C is 4x further outside the
  tested envelope than -20 C. The environmental ratings cover exactly:
  dry PD2 air between -10 and +50 C at 30-60 % RH for radio performance,
  and -40..+85 C for chip survival/operation — **nothing covers
  condensation, frost, or wet operation**.
- **Enclosure** (balloon repo, tracker/hardware/enclosure/README.md:27):
  "O-ring groove in lid (2mm cord, AS568 compatible) — IP65+ sealing"
  — external liquid/dust ingress protection only; README.md:120
  "Thermal: ESP32-C3 + LR2021 TX draws 100+ mA. Direct sun + sealed
  case may need ventilation. Monitor temps." — the project's own doc
  acknowledges the sealed-case moisture/thermal regime is not solved.

**The gap this entry documents**: every rating in evidence covers dry
air. The chip survival rating (-55 C abs max) and the module operating
rating (-40 C) both hold in dry air only; no spec, standard clause, or
conformance report on host covers a board that is cold-soaked, wet,
cycling through dew point, or pressure-cycled. The PD2 certification
explicitly assumes an environment where condensation is occasional and
temporary — the campaign's re-entry events are precisely "occasional
and temporary", but the campaign also pressure-pumps moisture in during
every cooldown (FM-9 class), which PD2 does not model at all.

## 2. Reproducibility

- `python3 bench/warm-side-electronics-failure-modes/condensation_window.py`
  — stdlib `math` only; recomputes every COMPUTED number quoted above:
  ice saturation pressures at the setpoints (103.22 Pa / 12.84 Pa vs
  published ~103 / ~12.8), re-entry flux-driver ratios (1.06-1.13x),
  12-cell re-entry window table (1.22-1.51x), cooldown inflow
  (0.151/0.218 atm vs committed 04db4fae FM-9 0.15/0.22 — cross-check
  PASS). Output captured verbatim in `output.txt`; rerun byte-identical
  (diff clean).
- `python3 bench/warm-side-electronics-failure-modes/ipx0_verify.py <pdf>`
  — renders the EN 62368-1 form page at 300 dpi and measures checkbox
  interior ink, calibrated against the two known states (PD1 empty
  2.38 %, PD2 checked 7.04 %); IPX0 reads 9.42 % = checked class,
  IP___ 4.76 % = empty class. Output in `output_ipx0.txt`. Requires
  poppler-utils (pdftoppm), available on host.
- PDF sources recovered from balloon git `cc92c869` via Python
  subprocess (file names contain U+00A0 non-breaking spaces; shell
  `git show` fails exit 128, `-z` ls-tree + binary show used instead).

## 3. Sources (at least two with numbers, per acceptance)

1. **182d4755** — bench/warm-side-dewpoint: 12-cell dew/frost-point
   table (T=20/22/25 C × RH=30/40/50/60 %, all cells ASSUMED, no
   hygrometer on host); coldest warm-side surface = setpoint itself;
   condensation RH thresholds **RH > 5.4/4.8/4.0 % (-20 C) and
   0.8/0.7/0.6 % (-40 C)**; zero sub-zero frost points; condensate
   arrives liquid at Td +1.9..+16.7 C.
2. **65c9c3df** — bench/condensation-risk: frost/condensation risk
   HIGH at both setpoints; ice er ~3.2 / water er ~80; ice resistivity
   ~10^7-10^8 Ohm·m; +9 % ice expansion; no humidity sensor on host.
3. **04db4fae** — bench/cable-feedthrough-failure-modes: FM-9
   pressure-driven inflow **0.15 atm (-20 C) / 0.22 atm (-40 C)**
   (REPORT.md:137); FM-1 frost-film reversible-data-corruption class;
   >5 ppm RMS fit check blind spot; consequence-class taxonomy.
4. **Semtech LR2021/LR2022/LR2012 Final Datasheet Rev. 2.1** (balloon
   repo working tree, docs/LR2021_LR2022_LR2012_Datasheet_Rev2.1.pdf,
   pdftotext extraction): Table 3-2 operating **Top -40..+85 C**
   (extraction lines 2850-2860); Table 3-1 abs max **Tmr -55..+125 C**
   (extraction lines 2797-2807); Table 3-3 ESD HBM 2 kV / CDM 500 V /
   latch-up 100 mA; **zero humidity/moisture/condensation hits in 243
   pages** (this session's text-layer search).
5. **NiceRF LoRa2021 Module Datasheet V1.3** (balloon git `cc92c869`,
   docs/assets/lr2021/LoRa2021-Module-Datasheet-V1.3.pdf): "Operating
   Temperature −40 [to] +85 ℃" (extraction lines 204-212); zero
   humidity/moisture specs.
6. **CE-RED EN 62368-1 test report 8427EU011624S** (balloon git
   `cc92c869`, EUT LoRa2021-868 module, applicant NiceRF): Tma
   "Outdoor: 40℃" (form raw line 97); **IP protection class IPX0**
   (raw line 98, selection pixel-verified this session); pollution
   degree PD2 (raw line 376); humidity conditioning clause 5.4.8 row
   **N/A** (extraction line 1371) — note the report's own supplementary
   text (line 8558) claims electric-strength tests followed 5.4.8
   conditioning; the row itself is marked N/A with blank RH/temp/
   duration parameters — the tension is recorded, the row governs.
7. **CE-RED EN 300 220 test report 8427EU011624W1** (balloon git
   `cc92c869`): test environment **RH 30 % to 60 %** (line 633), **NT
   +15 C to +35 C** (line 640), **Extreme Temperature -10 C ~ +50 C**
   (line 644, manufacturer-declared Note 1) — both campaign setpoints
   outside the radio-tested extremes.
8. **balloon repo, tracker/hardware/enclosure/README.md:27** — "O-ring
   groove in lid (2mm cord, AS568 compatible) — **IP65+ sealing**";
   README.md:120 thermal/sealed-case caution.
9. **d7ae93fa** — fork bench README (examples/passive_mapper/bench/
   README.md): reference TX "keep it at room temperature" (line 50);
   AT-cut crystal drift law drift_ppm(T) = -k(T-T0)^2, k = 0.02..0.06
   ppm/C^2 (lines 12-20); die-sensor/PA self-heating note (line 182);
   "IPA/dry-ice bath plus a bare board equals condensation and ice on
   the RF path" (line 55) — the fork's own documentation of this exact
   failure mode.
10. **c5eb3c58 / 55585471** — instrument census: no RF instrument, LNA,
    attenuator, or bias tee on host or record; primary path needs zero
    RF components.
11. **79ea692e** — ramp-feasibility: 3-4 thermal cycles per session
    (cycle-count scaling for the permanent sub-mode).
12. **IEC 60664-1** (pollution-degree definitions, invoked by the EN
    62368-1 PD2 selection): PD2 = only non-conductive pollution
    normally, occasional temporary condensation — the standard's own
    words for what the module is certified against.

**No mitigation content** is included in this entry, per acceptance.
Nothing was measured this session; every ambient cell is ASSUMED
(182d4755), the chamber is unidentified, no run has occurred, and the
nominal LNA/attenuator/bias-tee chain does not exist on this bench —
the entry documents the failure modes for the active elements that do
exist (reference TX, die sensor, chamber electronics) and, in kind,
for any future warm-side instrument added to the chain.