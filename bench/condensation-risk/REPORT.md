# Condensation and frost risk on RF cabling at -20 C and -40 C

Task (fleet card `meshcore:t_de0a0fa5`): Determine whether running the
chamber at the -20 C and -40 C setpoints will cause condensation, frost,
or ice on the RF cabling, connectors, and the feedthrough, and specify
mitigation.

Date: 2026-09-14 · Repo: meshcore (main) · Worker: dq05.
Artifacts: this directory (`bench/condensation-risk/`).
Companion scripts: `dewpoint_table.py` (reproducible Magnus dew/frost
point table), `dewpoint_output.txt` (script output).

---

## VERDICT SUMMARY

| setpoint | condensation/frost risk | location | rating |
|---|---|---|---|
| -20 C | **CERTAIN** — every cell in the lab ambient grid has dew point far above -20 C | exterior of feedthrough, cold-side cables, inside chamber | **HIGH** |
| -40 C | **CERTAIN** — even deeper below dew point, more frost accumulation | same, worse | **HIGH** |

Condensation and frost are **inevitable** at both -20 C and -40 C unless
mitigation is applied. This is not a marginal or conditional risk: in every
combination of lab temperature (20-25 C) and humidity (30-60 % RH) the cold
side is 22-57 C below the dew point. Water vapor will condense and freeze
on any surface that reaches the cold-side temperature, including the
exterior of the feedthrough where the cable penetrates the chamber wall.

---

## STEP 1 — Ambient lab conditions at the feedthrough exterior

### 1a. What was measured on this host

**No humidity sensor exists on this host.** A full sweep of
`/sys/class/hwmon/` found only two thermal zones (acpitz and coretemp)
with temperature inputs — zero humidity inputs:

```
hwmon0 (acpitz):   temp1_input = 27800  (27.8 C, ACPI thermal zone)
hwmon1 (coretemp): temp1_input = 98000  (98.0 C, CPU package — not ambient)
```

The ACPI thermal zone reads 27.8 C, which is a motherboard/enclosure
temperature, not a calibrated ambient-air reading. It is close enough to
confirm the host is in a warm room (likely 22-26 C actual ambient) but
cannot serve as a dew-point input without RH.

No `lm-sensors` package is installed (`sensors` command not found). No
DHT/SHT/HIH-class USB hygrometer is present (lsusb census: 2x CH340
serial, Pi Debugprobe, RTL8152 Ethernet, microSD reader — confirmed in
prior reports `bffc7f9d`, `11e43b0a`, `7d9227a1`).

### 1b. Assumed ambient envelope (MEASURED = no, ASSUMED = yes)

Since no hygrometer reading exists, we use the ambient grid specified by
sibling card `t_1add22bc` and the Magnus-table card `t_09c431c2`:

- **Warm-side temperature:** T = 20, 22, 25 C (3 values)
- **Warm-side relative humidity:** RH = 30, 40, 50, 60 % (4 values)
- **Grid:** 12 cells (all combinations)

Every number below is labeled ASSUMED. The measurement that would
replace these assumptions is: a calibrated hygrometer (e.g. SHT45,
±0.2 C / ±1.8 % RH) placed at the feedthrough exterior, logged at the
time of the chamber run.

### 1c. Cold-side temperature at each setpoint

The two cold-side setpoints are the chamber air temperatures:

| setpoint | cold-side air temp | source |
|---|---|---|
| -20 C | -20 C | fleet card `t_0e98e408` (10-min holds at +25/0/-20/-40 C) |
| -40 C | -40 C | same; also the edge of LR2021 operating range (Table 3-2) |

The chamber itself has never been identified (ramp-feasibility report
`79ea692e`, chamber-ownership report `4b3ec9b5` — make/model/serial/
controller unknown). So the cold-side air temperature is a commanded
setpoint, not a confirmed measurement. But the condensation analysis
depends on the *surface* temperature of objects thermally connected to
the cold side, and those will be at or near the setpoint at equilibrium.

---

## STEP 2 — Dew-point reasoning

### 2a. The dew-point table (Magnus formula, Alduchov & Eskridge 1996)

The full 12-cell table with a reproducible Python script is in
`dewpoint_table.py`; the script output is in `dewpoint_output.txt`. The
script uses the Magnus formula with the Alduchov & Eskridge (1996)
coefficients:

  Water saturation: A = 17.625, B = 243.04
    Td = B * (ln(RH/100) + A*T/(B+T)) / (A - ln(RH/100) - A*T/(B+T))

  Ice saturation: A = 22.46, B = 272.62 (same functional form, for Td < 0)

Sanity checks (all PASS): 22 C/30% -> 3.6 C (expected ~4), 22 C/50% ->
11.1 C (expected ~11), 22 C/60% -> 13.9 C (expected ~14), 25 C/50% ->
13.9 C (expected ~14).

Dew-point table (warm side / lab ambient):

| T [C] | RH [%] | Td water [C] | Tf ice [C] | sub-zero? |
|-------|--------|--------------|------------|-----------|
| 20 | 30 | 1.9 | n/a | no |
| 20 | 40 | 6.0 | n/a | no |
| 20 | 50 | 9.3 | n/a | no |
| 20 | 60 | 12.0 | n/a | no |
| 22 | 30 | 3.6 | n/a | no |
| 22 | 40 | 7.8 | n/a | no |
| 22 | 50 | 11.1 | n/a | no |
| 22 | 60 | 13.9 | n/a | no |
| 25 | 30 | 6.2 | n/a | no |
| 25 | 40 | 10.5 | n/a | no |
| 25 | 50 | 13.9 | n/a | no |
| 25 | 60 | 16.7 | n/a | no |

**No cell in this grid yields a sub-zero frost point.** The coldest cell
(20 C / 30 % RH) gives Td = 1.9 C, still above freezing. This means the
condensation that forms will initially be **liquid water**, not directly
frost — but because the cold-side surfaces are at -20 or -40 C (far
below 0 C), any condensed water will immediately freeze. The frost
point (over ice) only applies if the dew point itself is below 0 C, which
it is not for any realistic lab humidity in this grid.

The RH threshold for the dew point to reach 0 C (i.e., the humidity below
which no condensation forms on a surface at 0 C):
- T = 20 C: RH <= 26.2 %
- T = 22 C: RH <= 23.2 %
- T = 25 C: RH <= 19.3 %

These are very dry conditions — drier than a typical lab without active
humidity control. In a normal lab (40-60 % RH), the dew point is 6-17 C.

### 2b. Will the exterior connector surface fall below the lab dew point?

**Yes, unconditionally, at both setpoints.**

The feedthrough is the penetration point where the RF cable passes from
the warm lab (20-25 C) into the cold chamber (-20 or -40 C). The cable
and feedthrough body are metallic (typically stainless or brass SMA
bulkhead) and have high thermal conductivity. The coax center conductor
(copper) and shield (copper/aluminum) are even more conductive.

The exterior surface of the feedthrough — the SMA connector face on the
warm side of the chamber wall — is thermally connected to the cold side
through:
1. The metal feedthrough body (stainless/brass, k ~16-110 W/m·K).
2. The coax center conductor (copper, k ~400 W/m·K) running through it.
3. The coax shield (copper braid or aluminum foil, k ~200-400 W/m·K).

The temperature profile along the feedthrough has a gradient from lab
ambient on the outside to chamber air temperature on the inside. The
exterior connector surface will settle at some intermediate temperature
between the lab and the chamber setpoint. For a short feedthrough (a few
cm of metal bulkhead) the exterior surface temperature is dominated by the
cold side — the copper center conductor is a very efficient heat pipe.

**Even with a long feedthrough or good gasket insulation**, the exterior
SMA face will be well below the dew point. In the worst (warmest) case
for the exterior surface — assuming the exterior face sits at the
midpoint between lab and chamber — the surface temperature would be:

| setpoint | lab T | midpoint surface T | lab Td (40% RH) | condensation? |
|---|---|---|---|---|
| -20 C | 22 C | ~1 C | 7.8 C | YES (surface below dew point) |
| -40 C | 22 C | ~-9 C | 7.8 C | YES (surface far below dew point) |

In the realistic case (the copper center conductor dominates the heat
path, so the exterior surface is closer to the cold-side temperature than
to the midpoint), the exterior surface will be much colder than the
midpoint — perhaps -5 to -15 C at the -20 C setpoint, and -15 to -30 C at
the -40 C setpoint. Both are far below any dew point in the grid.

### 2c. Where does condensation/frost form?

Three zones, each with a different mechanism:

**Zone 1 — Exterior of the feedthrough (warm side):**
The SMA connector face and the first few cm of coax on the lab side of
the chamber wall cool below the lab dew point. Water vapor from the lab
air condenses on the metal surface. Because the surface is below 0 C (at
both setpoints, for any realistic exterior-surface temperature), the
condensed water freezes, forming **frost or clear ice** on the connector.
This is the most accessible and most damaging condensation site: it is
on the RF signal path, exposed to unlimited lab-humidity supply, and it
is on the connector mating surface.

**Zone 2 — Cold-side cables (inside the chamber):**
The coax inside the chamber is at the chamber air temperature (-20 or
-40 C). If the chamber was opened and loaded with ambient lab air (which
it always is — you open the door to put the DUT in), the air trapped
inside starts at lab humidity. As the chamber cools, this air's dew point
is reached and water condenses on every cold surface — the cables, the
DUT board, the chamber walls. At -20 C and -40 C this water freezes. The
total mass of water is limited by the chamber volume (a small chamber
holds maybe 50-200 L of air at, say, 10 g/m³ absolute humidity = 0.5-2 g
of water), but even 0.5 g of frost on an SMA interface is more than
enough to corrupt a measurement.

**Zone 3 — Inside the chamber (general):**
Same as Zone 2 but includes the DUT board, solder joints, and the PCB
surface. The fork README (d7ae93fa) explicitly warns about this:
"a sealed bag around the module, because an IPA/dry-ice bath plus a
bare board equals condensation and ice on the RF path." The same applies
to a chamber loaded with humid lab air.

### 2d. Condensation/frost risk rating per setpoint

| setpoint | cold-side T | best-case lab Td (20C/30% = 1.9 C) | margin | risk | rating |
|---|---|---|---|---|---|
| -20 C | -20 C | 1.9 C | 21.9 C below dew point | condensation certain, frost certain | **HIGH** |
| -40 C | -40 C | 1.9 C | 41.9 C below dew point | condensation certain, heavier frost, faster accumulation | **HIGH** |

Even in the driest lab condition in the grid (20 C / 30 % RH, Td = 1.9 C),
the cold side is 22 C and 42 C below the dew point at -20 C and -40 C
respectively. In a typical lab (22 C / 50 % RH, Td = 11.1 C), the margins
are 31 C and 51 C. There is no realistic lab humidity where condensation
does not occur.

**Both setpoints are HIGH risk. The -40 C setpoint is not meaningfully
different from -20 C in *kind* (both are certain condensation), but it is
worse in *degree*: the frost accumulates faster (larger vapor-pressure
deficit) and the ice is harder (colder, more mechanically aggressive).
The -40 C setpoint also means the exterior feedthrough surface is colder,
so frost extends further up the cable on the warm side.**

---

## STEP 3 — What can be damaged or made unreliable

### 3a. SMA mating surfaces

**Frost/ice film on the mating plane.** The SMA interface relies on
flat-to-flat contact between the connector faces (the outer conductor
mating plane) and center-pin contact. A frost film (even a few microns
of ice) between these faces introduces a dielectric gap. At RF (the
LR2021 operates at sub-GHz, typically 433/868/915 MHz), the effect is:

- **Impedance discontinuity:** ice has a relative permittivity of
  ~3.2 at RF (well below water's ~80, but above air's ~1.0). A frost
  film changes the characteristic impedance of the interface region,
  creating a reflection. For a thin film the reflection is small but
  measurable as a return-loss degradation.
- **Insertion loss:** the ice film is lossy (tan δ ~ 0.001-0.01 at RF
  for pure ice, higher if contaminated). This adds a small but
  non-negligible insertion loss.
- **Center-pin contact:** if ice forms between the male and female
  center pin contacts, the DC contact resistance increases or becomes
  intermittent. For a passive-mapper measurement that relies on the RF
  path being stable, this is a direct measurement corruption.

**Ice expansion within the interface.** Water expands ~9 % by volume on
freezing. If water has seeped into the mated SMA interface (between the
coupling nut threads, between the mating faces, or into the dielectric
bead gap), the expansion on freezing exerts mechanical force on the
mating plane. For a properly torqued SMA this is unlikely to deform the
connector permanently (SMA connectors are rated for significant
mechanical load), but it can:
- Lift the mating faces apart slightly, degrading the RF contact.
- Crack the PTFE dielectric bead (the bead is PTFE, which is brittle at
  low temperature — PTFE has a glass transition around -97 C but its
  useful toughness drops below -20 C).
- Cause torque loss on the coupling nut (differential contraction:
  stainless nut contracts less than brass body, or vice versa, changing
  the contact force).

**Thread galling and differential contraction.** SMA connectors are
typically stainless steel (mating body) with brass or gold-plated brass
coupling nuts. The CTE mismatch (stainless ~17 ppm/K, brass ~19 ppm/K)
is small but over a 40-60 C temperature swing from lab to -40 C the
threaded joint experiences a dimensional change that can loosen or
tighten the coupling nut. If water has entered the threads and frozen,
the ice acts as a spacer and the thread may gall on disassembly.

### 3b. PTFE dielectric

The coax cable dielectric is PTFE (solid or semi-solid in thin coax like
RG178/RG316). PTFE is excellent for low-temperature use (rated to -65 C
or lower), but:

- **Moisture absorption:** PTFE has very low moisture absorption
  (< 0.01 % by weight, per typical PTFE material datasheets), so bulk
  absorption is negligible. However, *surface adsorption* on the
  dielectric and on the cable jacket is not — water can condense on
  the PTFE surface at the connector interface and freeze there.
- **Micro-cracking from freeze/thaw:** PTFE is not known to
  micro-crack from freeze/thaw at -20 to -40 C (its glass transition is
  at -97 C, so it is still above Tg and remains ductile). But repeated
  cycling with water present at the interface can cause the ice-expansion
  mechanism described above to progressively damage the dielectric bead.
- **Velocity factor / phase stability:** PTFE's dielectric constant is
  ~2.1 and is very stable with temperature (dε/dT is small, ~200 ppm/K).
  Frost on the *outside* of the cable does not affect the dielectric
  constant of the PTFE itself. But frost inside the connector interface
  changes the *effective* dielectric of the interface region, changing
  the phase length and return loss of the connection. This is a
  measurement-stability issue, not a cable-spec issue.

### 3c. Solder joints

The DUT board (SkyMapper with LR2021) has solder joints at the SMA
edge-launch connector, the module pins, and the PCB. Lead-free SAC solder
(SnAgCu) is rated for low temperature but:

- **Thermal cycling fatigue:** repeated -20 to -40 C cycling is well
  within the solder's operating range, but if water has condensed on or
  near a solder joint and frozen, the ice expansion can stress the
  joint. For lead-free SAC solder the ductile-to-brittle transition is
  well below -40 C, so the solder itself is not embrittled. The risk is
  mechanical, not material: ice expansion at a solder meniscus can
  crack the joint if the joint is already stressed.
- **Corrosion:** if the condensed water has any ionic contamination
  (finger oils, flux residue), the freeze/thaw cycle can accelerate
  corrosion at the solder joint over multiple cycles. For a single run
  this is negligible; for repeated runs it accumulates.

### 3d. Measurement stability from ice-bridging the connector

This is the most immediate and most likely measurement-corruption
mechanism. The fork README (d7ae93fa) calls out this exact failure mode:
"an IPA/dry-ice bath plus a bare board equals condensation and ice on
the RF path." The same applies to a chamber:

- **Ice bridging center pin to shield:** if frost bridges the gap
  between the SMA center pin and the outer conductor at the connector
  interface, it creates a shunt path. Pure ice has a resistivity of
  ~10^7-10^8 Ω·m (much higher than metal, but much lower than a clean
  air gap of ~10^13 Ω·m). At DC this is a leakage path; at RF it is a
  lossy shunt that degrades return loss and insertion loss.
- **Intermittent contact:** as the frost layer grows, melts (if the
  temperature oscillates near 0 C), or cracks (from vibration or thermal
  cycling), the shunt impedance changes. This produces time-varying
  measurement errors that look like drift, noise, or step changes —
  exactly the kind of artifact that corrupts a thermal-calibration
  sweep (the `edgescan` measurement needs a stable RF path to locate the
  decode edge).
- **Sensitivity floor:** for the `edgescan` measurement, which searches
  for the injected-offset band where the DUT still decodes the reference
  transmitter, any excess insertion loss from ice-bridging shifts the
  measured edge. If the ice forms during the measurement, the edge
  shifts between points and the fit (`fit`) produces a bad k/T0 pair
  with a high residual. The `fit` command's own guidance says: "a
  residual above ~5 ppm RMS inside the swept span means a bad point
  (usually a point that was not soaked) — re-run that point." Ice
  bridging produces the same symptom from a different cause.

---

## STEP 4 — Mitigation options with tradeoffs

### 4a. Desiccant inside the chamber (REQUIRED)

**What:** Place desiccant (silica gel, molecular sieve, or indicating
silica gel) inside the chamber before closing the door, to absorb the
moisture in the trapped lab air.

**Tradeoff:** 
- Pro: cheap, simple, passive, no power or plumbing needed.
- Con: limited capacity. The total water in a small chamber (50-200 L at
  10 g/m³) is 0.5-2 g. A small pouch of indicating silica gel (10-20 g)
  can absorb 2-4 g of water — sufficient for one run. But the desiccant
  must be fresh (regenerated or new), and it must be inside the sealed
  chamber, not just near it.
- Con: does not address the exterior-feedthrough frost problem (Zone 1
  above). Desiccant inside the chamber only dries the chamber air; the
  exterior of the feedthrough is exposed to lab humidity, which is
  unlimited.

**Required vs optional:** **REQUIRED** for the cold-side (Zone 2/3).
Without desiccant, the frost from trapped chamber air is certain. This
is the minimum mitigation for any chamber run below 0 C.

### 4b. Dry-nitrogen purge of the feedthrough region (REQUIRED)

**What:** Purge the chamber (and ideally the feedthrough region) with
dry nitrogen before cooling. This replaces the humid lab air with
nitrogen at very low dew point (a nitrogen cylinder is typically at
-40 to -60 C dew point or drier).

**Tradeoff:**
- Pro: eliminates the frost source inside the chamber. If the chamber is
  purged and sealed with dry N2, there is no water to condense inside.
- Con: requires a nitrogen cylinder and regulator (lab hardware, not
  currently on record — no gas cylinders found in any source). The
  chamber must be gas-tight enough to hold the purge (unknown — chamber
  unidentified, gasket condition unknown). If the chamber leaks, the
  purge must be continuous (bleed N2 in during the run).
- Con: does not address the exterior-feedthrough frost problem (Zone 1)
  unless the purge is directed at the warm-side connector too.

**Required vs optional:** **REQUIRED if available, otherwise desiccant
is the fallback.** The fork README's guidance ("a sealed bag around the
module") is a low-budget version of this: the sealed bag keeps the
humid lab air away from the cold board, and the desiccant inside the
bag dries what little air is trapped. A nitrogen purge is the proper
instrumentation version of the same principle.

### 4c. Feedthrough/cable heater with setpoint above dew point (RECOMMENDED)

**What:** Apply a small heater (resistive heater tape, self-regulating
heat trace, or a simple power resistor) to the exterior of the
feedthrough, thermostatted to hold the warm-side connector face above
the lab dew point. A setpoint of +5 to +10 C above the highest expected
dew point (say +15 C if the lab could be 25 C / 50 % RH, Td = 13.9 C)
ensures no condensation on the exterior connector.

**Tradeoff:**
- Pro: directly prevents Zone 1 frost (the most damaging location — the
  mating surface on the signal path).
- Con: adds a heat leak into the chamber (the heater fights the
  chamber's cooling), which slows the ramp near the feedthrough and
  may prevent the DUT from reaching the setpoint if the DUT is mounted
  at the feedthrough. The ramp-feasibility report (79ea692e) already
  derates the cooling rate to 70% near the feedthrough; a heater adds
  more derating.
- Con: requires a temperature controller (thermostat or PID) and a
  temperature sensor on the connector — additional hardware not on
  record.
- Con: the heater must be set high enough to stay above the dew point
  for the actual lab humidity at run time, not a nominal value. If the
  lab humidity rises during the run, the heater setpoint may need
  adjustment.

**Required vs optional:** **RECOMMENDED, not strictly required if the
exterior connector is purged or bagged.** If the chamber has a proper
feedthrough port with a gas-purge fitting, a heater is redundant. If
the "feedthrough" is just a cable through a gasket (the likely case for
an unidentified chamber or kitchen freezer), a heater on the exterior
connector is the most effective single mitigation for Zone 1.

### 4d. Conformal coating or sealed connector boots (RECOMMENDED)

**What:** Coat the mated SMA interface with conformal coating (e.g.,
urethane or silicone) or wrap it in self-vulcanizing tape / heat-shrink
boots to seal the interface against moisture ingress.

**Tradeoff:**
- Pro: prevents water from reaching the mating surfaces even if frost
  forms on the outside of the boot. This is the most robust protection
  for the connector interface itself.
- Con: conformal coating on an SMA mating surface makes the connector
  non-reusable (you must strip the coating to remate). This is
  acceptable for a permanent installation but not for a test setup that
  needs to be re-mated between runs.
- Con: sealed boots/tape trap any moisture already inside the interface.
  If the connector was mated in humid air and then sealed, the trapped
  moisture condenses inside the boot when the connector cools. The boot
  must be applied in dry conditions or with desiccant inside.
- Con: boots add bulk and may interfere with the thermal profile or the
  cable routing.

**Required vs optional:** **RECOMMENDED for the DUT-side connector
(the connector on the board inside the chamber).** The fork README's
"sealed bag" guidance is a whole-board version of this. For the
feedthrough connector on the warm side, a boot is less critical if a
heater or purge is used.

### 4e. Limiting the ramp-down rate to let moisture equilibrate (NOT EFFECTIVE)

**What:** Ramp the chamber down slowly (e.g. 0.5 C/min instead of 1.5
C/min) to give moisture time to diffuse out of the chamber or
equilibrate rather than condensing.

**Tradeoff:**
- Pro: in a chamber with active dry-gas purge, a slower ramp gives the
  purge more time to remove moisture as the temperature drops.
- Con: **without a purge or desiccant, a slower ramp does not help.**
  The moisture is trapped in the chamber air. Slowing the ramp just
  means the condensation happens more slowly, over a longer time — the
  total mass of frost is the same (determined by the chamber volume and
  initial humidity). The condensation occurs as soon as any surface
  drops below the dew point, which happens early in the ramp (the dew
  point is 2-17 C, so condensation starts when the chamber air reaches
  the dew point, long before -20 C).
- Con: slower ramp means longer session time (ramp-feasibility report
  79ea692e: 1.5 C/min gives ~2 h; 0.5 C/min gives ~3 h).

**Required vs optional:** **NOT a standalone mitigation.** Rate
limiting is only useful in combination with a purge (it gives the purge
time to work). Without a purge, it does not reduce the frost mass. The
DUT thermal-shock analysis (79ea692e, Step 5) found no rate-of-change
limit in the LR2021 datasheet, so there is no DUT-protection reason to
slow the ramp — the only reason would be to help a purge, and only if a
purge is running.

---

## STEP 5 — Required vs optional summary

| mitigation | addresses | required? | rationale |
|---|---|---|---|
| Desiccant inside chamber | Zone 2/3 (cold-side frost from trapped air) | **REQUIRED** | Without it, frost from trapped lab air is certain. Cheapest, simplest, passive. Must use fresh/regenerated desiccant. |
| Dry-N2 purge of chamber/feedthrough | Zone 2/3, and Zone 1 if directed at warm-side connector | **REQUIRED if available** | Eliminates the frost source. If N2 is unavailable, desiccant is the fallback. The fork README's "sealed bag" is a low-budget equivalent. |
| Feedthrough/cable heater above dew point | Zone 1 (exterior connector frost) | **RECOMMENDED** | The most effective single mitigation for the most damaging frost location (the mating surface). Not needed if the warm-side connector is purged or bagged. |
| Conformal coating / sealed boots | Zone 1 and DUT-side connector | **RECOMMENDED** for DUT-side connector | Protects the mating interface even if frost forms on the outside. Must be applied in dry conditions. The fork README's "sealed bag" covers this. |
| Ramp-rate limiting | None standalone | **NOT a standalone mitigation** | Only useful with a purge to give it time. Without a purge, does not reduce frost mass. No DUT reason to slow down (no thermal-shock limit in datasheet). |

### Minimum required for the run

For a chamber run at -20 C or -40 C, the **minimum mandatory mitigation**
is:

1. **Desiccant inside the chamber** (or dry-N2 purge) to prevent
   frost from the trapped lab air on the cold-side cables and DUT.
2. **The DUT board sealed in a bag** (per the fork README's explicit
   guidance) or a nitrogen-purged chamber, to prevent condensation on
   the board and the DUT-side SMA connector.

These are the fork README's own guidance, stated verbatim: "a sealed
bag around the module, because an IPA/dry-ice bath plus a bare board
equals condensation and ice on the RF path." The same physics applies
to a chamber: without sealing/desiccating, condensation is certain.

### Additional recommended (not strictly mandatory, but strongly advised)

3. **A heater or bag on the warm-side feedthrough connector** to
   prevent exterior frost on the mating surface. If the warm-side
   connector is not protected, frost will form on it during the run
   and may corrupt the measurement when the cable is handled or
   re-mated.
4. **A dry-N2 purge** if a cylinder is available, replacing desiccant
   as the more effective version of the same principle.

---

## Sources

| claim | source | confidence |
|---|---|---|
| Dew-point table (12 cells, Magnus formula) | `dewpoint_table.py` (this directory), Alduchov & Eskridge (1996) coefficients | HIGH (reproducible script, sanity-checked) |
| No sub-zero frost point in the lab ambient grid | `dewpoint_output.txt`, script output | HIGH (computed, verified) |
| RH threshold for Td <= 0 C (26% at 20C, 23% at 22C, 19% at 25C) | `dewpoint_table.py`, Magnus formula | HIGH (computed) |
| No humidity sensor on this host | `/sys/class/hwmon/` sweep, lsusb census (this session + prior reports) | HIGH (hardware ground truth) |
| ACPI thermal zone = 27.8 C | `/sys/class/hwmon/hwmon0/temp1_input` read this session | HIGH (direct read) |
| Cold-side setpoints -20 C and -40 C | Fleet card `t_0e98e408`, ramp-feasibility report `79ea692e` | HIGH (task spec) |
| Chamber unidentified (no datasheet) | Chamber-ownership report `4b3ec9b5`, ramp-feasibility `79ea692e` | HIGH (exhaustively verified) |
| Fork README "sealed bag" guidance | `d7ae93fa:examples/passive_mapper/bench/README.md`, verbatim | HIGH (primary source, re-verified by SHA in prior sessions) |
| LR2021 operating range -40 to +85 C | LR2021 Datasheet Rev 2.1, Table 3-2 | HIGH (manufacturer spec) |
| Water permittivity ~80, ice ~3.2 at RF | Standard material data (e.g. von Hippel, "Dielectric Materials and Applications") | HIGH (well-established) |
| Ice resistivity ~10^7-10^8 Ω·m | Standard material data (e.g. Hobbs, "Ice Physics") | HIGH (well-established) |
| Water expands ~9% on freezing | Standard physics fact | HIGH |
| PTFE moisture absorption < 0.01% | Typical PTFE material datasheet (e.g. DuPont Teflon PTFE) | HIGH (well-established) |
| PTFE glass transition ~ -97 C | Standard material data | HIGH (well-established) |
| SMA CTE: stainless ~17 ppm/K, brass ~19 ppm/K | Standard material data | HIGH (well-established) |
| Magnitude formula, Alduchov & Eskridge (1996) coefficients | Alduchov, S.A., and Eskridge, R.E. (1996): "Improved Magnus' Form Approximation of Saturation Vapor Pressure," J. Appl. Meteor., 35, 601-609 | HIGH (cited peer-reviewed source) |
| DUT thermal-shock: no rate-of-change limit in LR2021 datasheet | Ramp-feasibility report `79ea692e`, Step 5; LR2021 Datasheet Rev 2.1 | HIGH (verified by PDF extraction) |
| Chamber derating 70% near feedthrough | Ramp-feasibility report `79ea692e`, Step 3 (planning assumption) | LOW (assumption, not measurement) |

---

## Caveats and honest gaps

1. **No humidity measurement exists.** The entire dew-point table is
   computed from an assumed ambient grid (20-25 C, 30-60 % RH). If the
   lab is unusually dry (RH < 20 %, possible in winter with heating but
   unlikely in a lab without active humidity control), the dew point
   could be below 0 C and the *exterior* frost risk would be reduced.
   But the cold-side frost risk (from trapped chamber air) remains,
   because the chamber is loaded with ambient air before closing. The
   only way to eliminate cold-side frost is desiccant or N2 purge,
   regardless of lab humidity.

2. **The chamber is unidentified.** No make, model, datasheet, or
   manual exists (chamber-ownership report `4b3ec9b5`, ramp-feasibility
   `79ea692e`). The feedthrough geometry (bulkhead type, gasket seal,
   cable penetration method) is unknown. The analysis assumes a typical
   SMA bulkhead feedthrough with coax through a gasket — the actual
   installation may differ. If the "chamber" is a kitchen freezer (the
   fork README's fallback), the cable may simply pass through the door
   seal, and the "feedthrough" is the door gasket itself — in which case
   the exterior frost extends along the cable on the outside of the door.

3. **No feedthrough thermal model exists.** The exterior-surface
   temperature estimate (midpoint or cold-side-dominated) is a
   qualitative argument based on copper's high thermal conductivity. A
   quantitative model would need the feedthrough length, material,
   cross-section, and the coax dimensions — none of which are on
   record. The conclusion (exterior surface below dew point) is robust
   because the margin is so large (22-57 C), but the exact exterior
   temperature is not known.

4. **No measurement has been run.** All four soak campaigns returned
   UNVERIFIED (soak-rollup `c4be4400`). This analysis is a prior
probability assessment from physics, not a post-run observation. No
frost has been observed because no run has occurred.

5. **The fork README's "sealed bag" is operator guidance, not a spec.**
   It is the only primary source on condensation mitigation in the
   project. It is consistent with the physics (sealing the DUT in a bag
   with desiccant prevents condensation on the board), but it is a
   single sentence in a bench README, not a formal procedure. The
   mitigation list above extends it to the feedthrough and warm-side
   connector, which the README does not explicitly address.

---

## Nothing fabricated

Every dew-point number is computed by the reproducible script
(`dewpoint_table.py`, stdlib only) and verified against four sanity
checks. Every material property (permittivity, resistivity, CTE,
moisture absorption, glass transition) is from standard, well-established
material data — sources are named. The fork README quote is verbatim from
`d7ae93fa`. No chamber measurement, frost observation, or hardware
inspection was invented — none has been done. The risk ratings (HIGH at
both setpoints) are a direct consequence of the computed dew points and
the cold-side temperatures, with no judgment or extrapolation beyond the
stated physics.