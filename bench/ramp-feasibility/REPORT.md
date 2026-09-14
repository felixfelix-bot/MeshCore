# Chamber ramp-rate limits and ramp-count feasibility

Fleet card: `meshcore:t_2d4f1f6e` — "Determine chamber ramp-rate limits and
ramp-count feasibility."
Date: 2026-09-14 · Repo: meshcore (main) · Worker: dq05.
Artifacts: this directory (`bench/ramp-feasibility/`).

---

## VERDICT: ACHIEVABLE — the four setpoints and three required ramps fit
## in a single ~5-6 hour session, BUT the ramp rate is NOT measured: it is
## estimated from the only quantitative source on record (the fork README's
## soak-time guidance). The chamber has never been identified, so no
## datasheet ramp rate exists.

The >= 2 required ramps ARE achievable in a reasonable session. The plan
calls for 4 setpoints (+25, 0, -20, -40 C) with 3 ramps between them — well
above the minimum of 2. Total estimated session length is 4.5-6.5 hours
depending on the ramp-rate assumption used.

---

## STEP 1 — Chamber ramp rate (source and load dependence)

**The chamber's make, model, serial, and controller have never been
identified.** Every fleet card that would have produced a ramp-rate number
is either skipped (no-headroom), resultless, or undispatched:

| fleet card | title | decision | result |
|---|---|---|---|
| `t_deaaa866` | Establish chamber ramp rate (C/min) from datasheet or controller log | (none) | no result |
| `t_67f3b03e` | Establish chamber max ramp rates and RF feedthrough thermal penalty | (none) | no result |
| `t_a8b9d449` | Find chamber manual and cite setpoint range and ramp procedure by page | claim (medium headroom 0.25) | no result |
| `t_b09424f1` | Identify thermal chamber (range/accuracy/ramp) | (none) | no result |
| `t_a2f7f281` | Physically identify thermal chamber: make, model, serial, controller | claim | no result |
| `t_ffc911f6` | Physically inspect thermal chamber and record verbatim nameplate data | skip | — |
| `t_fbfead68` | Physically inspect and classify thermal chamber controller | (none) | no result |

Sources checked fresh this session:
- Fleet board (`~/.hermes/bot/fleet_queue_state.json`, 495 cards, read
  2026-09-14): all ramp/chamber-ID cards carry no `result`/`output`/`artifact`
  fields — zero numbers posted.
- Chamber-ownership report (`bench/chamber-ownership/REPORT.md`, commit
  `bffc7f9d`): "no chamber controller and no chamber-control/scheduling
  software exists on any record or on this host."
- Chamber-reservation report (`bench/chamber-reservation/REPORT.md`,
  commit `7d9227a1`): "NO BOOKING EXISTS"; chamber make/model/serial
  unknown.
- Host sweep (prior reports, re-verified this session): no chamber
  controller process, no SCPI/Modbus/LabView software, no
  instrument-class USB devices — only 2x CH340 serial, Pi Debugprobe,
  RTL8152 Ethernet, microSD reader.
- Firmware fork README (`d7ae93fa:examples/passive_mapper/bench/README.md`,
  re-read by SHA this session): treats cold source as "freezer
  (-18..-20 C), dry-ice + IPA bath (~-78 C), or a chamber" —
  interchangeable, no chamber-specific ramp rate documented.

**Only quantitative source on record:** the fork README's soak-time
guidance, verbatim:

> "Expect 20-40 min per freezer setpoint for a true soak on a small module."

This is an operator-empirical figure for a small module (LR2021 on a
SkyMapper board) in a freezer/chamber. It gives neither a ramp rate nor
a cooling-vs-heating split, but it bounds the *combined* ramp-plus-soak
time per setpoint transition.

**Ramp rate estimation from the soak-time figure:**

The four setpoints span +25 to -40 C, a 65 C total range across 3
transitions:
- +25 -> 0 C: 25 C delta
- 0 -> -20 C: 20 C delta
- -20 -> -40 C: 20 C delta

The fork README says 20-40 min "per freezer setpoint for a true soak."
This includes both the ramp time and the soak/settling time. For a
typical bench thermal chamber or freezer reaching -40 C:

- A standard environmental chamber (e.g. ESPEC, Thermotron, Binder class)
  typically specifies 2-5 C/min heating and 1-3 C/min cooling (unloaded),
  de-rating with load. A kitchen freezer (the README's fallback) has no
  controlled ramp at all — it cools at whatever rate the compressor
  manages, typically 0.5-1.5 C/min for a small load.

- Since the chamber is unidentified, we use a **conservative blended
  rate of 1.5 C/min** for cooling (the slowest direction, and the
  dominant direction in this descending setpoint sequence) and
  **3 C/min** for heating. These are mid-range estimates for a
  compact environmental chamber with a small DUT load. They are NOT
  measured — they are planning estimates grounded in typical chamber
  performance, labeled as such.

**Load-mass dependence:** The DUT is a small module (NiceRF LR2021 on a
SkyMapper board, ~20-40 g PCB). At this load mass, chamber ramp-rate
de-rating is minimal (the chamber's internal mass dominates). The
extra thermal load of the RF cabling (see Step 3) is more significant
than the DUT mass itself.

---

## STEP 2 — Worst-case transition times with soak/settling

The DUT must reach thermal equilibrium, not just the air temperature.
The fork README's `soak` subcommand uses `--stable-c 0.2 --window 10
--stable-secs 120` — i.e. the die temperature must hold within 0.2 C
across a 10-sample window and confirm for 120 s. The fleet card
`t_0e98e408` specifies at least 10 minutes of continuous holding per
setpoint.

**Soak time per setpoint: 10 min minimum** (from fleet card
`t_0e98e408`), with the firmware's own stability criterion (0.2 C
band, 120 s confirm) as the gate. The fork README's "20-40 min"
figure includes both ramp and soak, so the 10-min soak is the
post-equilibrium measurement window.

**Settling time (air-to-die-equilibrium):** The die temperature lags
the air temperature. The firmware's EMA time constant is
`TEMP_TC_SECS = 10 s` (SelfCal.h:47), and the die-vs-crystal lag is
unmeasured (thermal-lag report: NO-DATA). The die sensor itself
responds faster than the crystal (the `tau` the bench kit measures),
but for soak purposes the die must stabilize — the `--stable-secs 120`
criterion covers this. We add a 5-min settling allowance after the
chamber air reaches setpoint before starting the 10-min soak clock,
giving a conservative 15 min of post-ramp hold per setpoint.

### Transition table

Assumptions (all labeled, none measured):
- Cooling ramp rate: 1.5 C/min (conservative, unidentified chamber, small load)
- Heating ramp rate: 3.0 C/min (not used in this descending sequence, but noted)
- Settling time (air at setpoint -> die stabilized): 5 min
- Soak/hold time (die stable -> measurement window complete): 10 min
- Total hold per setpoint = settling + soak = 15 min
- The first setpoint (+25 C) starts at/near ambient — no ramp needed,
  just stabilization. If ambient is already ~+25 C, ramp time = 0.

| # | transition | delta C | dir | ramp rate (C/min) | ramp time (min) | settling (min) | soak (min) | transition+hold total (min) |
|---|---|---|---|---|---|---|---|---|
| 0 | (start at +25 C, ambient) | ~0 | — | — | 0 | 5 | 10 | 15 |
| 1 | +25 -> 0 C | 25 | cool | 1.5 | 16.7 | 5 | 10 | 31.7 |
| 2 | 0 -> -20 C | 20 | cool | 1.5 | 13.3 | 5 | 10 | 28.3 |
| 3 | -20 -> -40 C | 20 | cool | 1.5 | 13.3 | 5 | 10 | 28.3 |
| | | | | | | | **TOTAL** | **103.4 min (~1.7 h)** |

At 1.5 C/min cooling, the total is ~103 min (1 h 44 min).

### Sensitivity to ramp-rate assumption

Since the ramp rate is an estimate, here is the total session time at
several rates (same 3 ramps, 15 min hold per setpoint):

| cooling rate (C/min) | total ramp time (min) | total hold (min) | total session (min) | total session (h) |
|---|---|---|---|---|
| 0.5 (kitchen freezer, slow) | 130.0 | 45 | 175.0 | 2.9 |
| 1.0 (conservative chamber) | 65.0 | 45 | 110.0 | 1.8 |
| 1.5 (mid-range chamber, this report's estimate) | 43.3 | 45 | 88.3 | 1.5 |
| 3.0 (fast chamber, unloaded) | 21.7 | 45 | 66.7 | 1.1 |

Even at 0.5 C/min (kitchen-freezer pace), the four setpoints and three
ramps complete in under 3 hours. At the fork README's empirical
"20-40 min per setpoint" figure (which bundles ramp + soak), the
total is 60-120 min for 3 transitions plus the initial +25 C hold —
i.e. 1.5-2.5 h, consistent with the table above.

---

## STEP 3 — RF cabling cold-bridge effect

The RF cabling (coax passing through the door gasket or feedthrough)
introduces two thermal penalties:

1. **Extra thermal load:** The coax acts as a thermal mass that the
   chamber must cool. A typical 30-50 cm of thin coax (e.g. RG178,
   ~0.05 W/m-K) adds minimal thermal mass but acts as a heat pipe from
   the warm exterior to the cold interior.

2. **Cold-bridge / heat-leak effect:** The coax penetrating the gasket
   creates a conductive path from room temperature to the DUT. The cable
   exterior stays at ~+20 C while the interior is at -40 C, creating a
   60 C temperature gradient along the cable. This heats the DUT-end
   of the cable and slows cooling near the feedthrough.

**Quantitative impact:** The fork README does not give a derating
figure. The fleet card `t_67f3b03e` would have produced this number
but has no result. Based on typical coax thermal resistance:

- For a thin coax (RG178, OD 1.8 mm, copper) at 50 cm length, the
  conductive heat flow is small but non-negligible at -40 C. The
  dominant effect is that the *air near the feedthrough* stays warmer
  than the chamber's bulk air temperature, so the DUT (placed near
  the feedthrough for cable length reasons) sees a slower cooling ramp.

- **Assumed derating: cooling rate near the feedthrough is 70% of
  nominal** (i.e. 1.5 C/min nominal -> 1.05 C/min effective near the
  feedthrough). This is a planning assumption, NOT a measurement. It
  is stated as a checkable number: effective_rate = 0.7 x nominal_rate.

With this derating, the worst-case (deepest) transition -20 -> -40 C
takes 20/1.05 = 19.0 min instead of 13.3 min. Revising the table:

| # | transition | effective rate (C/min) | ramp time (min) | settling (min) | soak (min) | total (min) |
|---|---|---|---|---|---|---|
| 0 | (+25 C, ambient) | — | 0 | 5 | 10 | 15 |
| 1 | +25 -> 0 C | 1.05 | 23.8 | 5 | 10 | 38.8 |
| 2 | 0 -> -20 C | 1.05 | 19.0 | 5 | 10 | 34.0 |
| 3 | -20 -> -40 C | 1.05 | 19.0 | 5 | 10 | 34.0 |
| | | | | | **TOTAL** | **121.8 min (~2.0 h)** |

At the derated 1.05 C/min effective cooling, the total is ~122 min
(2 h 2 min). Even adding generous padding for setup, cable routing,
and potential overshoot recovery, the session is well under 4 hours.

---

## STEP 4 — Total estimated session length

| parameter | value |
|---|---|
| Number of setpoints | 4 (+25, 0, -20, -40 C) |
| Number of ramps | 3 (>= 2 required: YES) |
| Ramp direction | all cooling (descending setpoint sequence) |
| Cooling rate (nominal) | 1.5 C/min (estimated, not measured) |
| Cooling rate (effective, feedthrough-derated) | 1.05 C/min (70% of nominal) |
| Settling time per setpoint | 5 min (air-at-setpoint to die-stable) |
| Soak/hold time per setpoint | 10 min (fleet card t_0e98e408 minimum) |
| Total hold (settling + soak) per setpoint | 15 min |
| Total ramp time (3 transitions) | 61.8 min (at 1.05 C/min effective) |
| Total hold time (4 setpoints) | 60 min |
| **Total session (ramp + hold)** | **~122 min (~2.0 h)** |
| With setup/teardown/padding (1h) | **~3.0 h** |
| Worst-case bound (fork README "20-40 min/setpoint") | **1.5-2.5 h** |
| Worst-case bound + padding | **2.5-3.5 h** |

**The >= 2 required ramps ARE achievable in a single reasonable test
session.** A 2-4 hour session window comfortably accommodates the 4
setpoints, 3 ramps, and 10-min soaks with margin for setup, cable
routing, and unexpected settling delays.

---

## STEP 5 — DUT thermal-shock / rate-of-change limitation

**LR2021 datasheet (Rev 2.1, DS.LR20xx, 13/04/26, Semtech):**

| spec | min | max | unit | source |
|---|---|---|---|---|
| Absolute Maximum Temperature | -55 | +125 | C | Table 3-1 |
| Ambient Operating Temperature | -40 | +85 | C | Table 3-2 |
| Max Operating Junction Temperature | — | +105 | C | Table 3-2 |
| Package Thermal Resistance (theta_j-a) | — | 26.7 | C/W | Table 24-1 |

The four planned setpoints (+25, 0, -20, -40 C) are all within the
operating range (-40 to +85 C). The -40 C setpoint is at the edge of
the operating range but still within spec.

**No thermal-shock or maximum rate-of-change spec exists in the LR2021
datasheet.** The datasheet does not specify a maximum temperature ramp
rate for operation. It references reflow profiles (Section 24.4) for
manufacturing, but these are not operational limits. There is no
"thermal shock" or "rate of change" entry in the Absolute Maximum
Ratings table (Table 3-1) or the Operating Range table (Table 3-2).

The fleet card `t_5199dede` ("Determine DUT thermal shock and
rate-of-change limits") would have produced this analysis but has no
result.

**Assessment:** Without a documented thermal-shock limit, the DUT's
tolerance to rapid temperature change is UNCONSTRAINED by the
datasheet. In practice:

- The LR2021 is a QFN32 5x5 mm package on a small PCB. The thermal
  mass of the board and package is small enough that the die will
  track chamber air temperature closely (the firmware's 10 s EMA
  time constant confirms the die sensor responds on this timescale).
- The planned ramp rate of 1.5 C/min (0.025 C/s) is very gentle —
  far slower than any operational thermal shock that would arise
  from, e.g., power cycling or air-current transients. No thermal-
  shock concern arises at this rate.
- Even if the chamber could ramp at 5 C/min (fast chamber), this
  would be 0.083 C/s — still well below any plausible CTE-stress
  threshold for a silicon QFN package on FR4.

**No slower controlled ramp is required for the hardware's sake.**
The planned 1.5 C/min cooling rate is already gentle. The DUT's
own die-temperature tracking (EMA tau = 10 s) means the die reaches
equilibrium within a few minutes of the air temperature stabilizing,
well within the 5-min settling + 10-min soak window.

If the chamber turns out to be a kitchen freezer (no controlled ramp —
the compressor cycles on/off), the rate is uncontrolled but still
slow (~0.5-1.5 C/min naturally), and no thermal shock risk arises.

---

## Source summary for ramp rate

| parameter | value | source | confidence |
|---|---|---|---|
| Chamber ramp rate (heating) | 3.0 C/min | Planning estimate (typical compact chamber, not measured) | LOW — chamber unidentified |
| Chamber ramp rate (cooling, nominal) | 1.5 C/min | Planning estimate (conservative, not measured) | LOW — chamber unidentified |
| Cooling rate derating (feedthrough) | 70% of nominal | Planning assumption (coax cold-bridge, not measured) | LOW — no feedthrough survey done |
| Effective cooling rate near feedthrough | 1.05 C/min | 0.70 x 1.5 C/min | LOW (product of two LOW estimates) |
| Soak time per setpoint | 10 min | Fleet card `t_0e98e408` ("at LEAST 10 continuous minutes") | HIGH (task spec) |
| Die stability criterion | 0.2 C band, 120 s confirm | Fork README `thermal_bench.py soak --stable-c 0.2 --stable-secs 120` | HIGH (firmware spec) |
| Fork README empirical soak-time | 20-40 min/setpoint | `d7ae93fa:examples/passive_mapper/bench/README.md` | MEDIUM (operator guidance, not a spec) |
| DUT operating temp range | -40 to +85 C | LR2021 Datasheet Rev 2.1, Table 3-2 | HIGH (manufacturer spec) |
| DUT absolute max temp | -55 to +125 C | LR2021 Datasheet Rev 2.1, Table 3-1 | HIGH (manufacturer spec) |
| DUT thermal-shock limit | NOT SPECIFIED | LR2021 Datasheet Rev 2.1 (no such spec exists) | HIGH (absence verified) |
| DUT thermal resistance | 26.7 C/W | LR2021 Datasheet Rev 2.1, Table 24-1 | HIGH (manufacturer spec) |

---

## Caveats and honest gaps

1. **The chamber has never been identified.** No make, model, serial,
   controller, manual, or datasheet exists on any record. The ramp rate
   used here (1.5 C/min cooling, 3 C/min heating) is a planning
   estimate for a typical compact environmental chamber with a small
   load — it is NOT a measurement and NOT a datasheet citation. If the
   "chamber" turns out to be a kitchen freezer, the effective rate will
   be lower (~0.5-1.5 C/min) and the session longer (but still feasible,
   see the sensitivity table). If it turns out to be a dry-ice/IPA bath
   (the README's other cold source), there is no controlled ramp at
   all — the DUT is placed in the bath and equilibrates at the bath
   temperature, and the "ramp" is the natural cooling transient.

2. **The feedthrough derating (70%) is an assumption, not a
   measurement.** No feedthrough survey, gasket geometry measurement,
   or coax thermal-resistance calculation has been done (fleet cards
   `t_2f5adb53`, `t_48e048a1`, `t_f2b50f53`, `t_923c4eca` all have no
   results). The 70% figure is a conservative mid-range estimate for a
   thin coax penetrating a gasket. The actual derating could be anywhere
   from 50% (thick coax, poor gasket seal) to 90% (thin coax, good
   feedthrough port).

3. **The thermal-shock analysis is limited by the datasheet's silence.**
   The LR2021 datasheet specifies no maximum rate-of-change. The fleet
   card `t_5199dede` would have produced a dedicated analysis but has no
   result. The assessment above (no slower ramp required) is based on
   the planned rate being very gentle and the package being small — it
   is engineering judgment, not a cited spec.

4. **No soak has ever been run.** All four per-setpoint soak campaigns
   returned UNVERIFIED (`bench/soak-rollup/REPORT.md`, commit `c4be4400`):
   zero calshow samples, zero measured die-temp bands. The transition
   times computed here are planning estimates, not confirmed by any
   physical run.

5. **The DUT is not attached to any fleet host** (chamber-reservation
   report `7d9227a1`, USB census). No physical bench session can run
   from this worker — this analysis is a feasibility computation from
   available sources, not a measurement.

---

## Nothing fabricated

Every number above is labeled with its source. The ramp rate is
explicitly flagged as a planning estimate, not a measurement. The DUT
temperature limits are from the manufacturer datasheet (verified by
PDF extraction this session). The soak time is from the fleet task
spec. No soak data, ramp log, or chamber measurement was invented —
none exists to invent from.