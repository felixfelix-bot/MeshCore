# DUT thermal shock and rate-of-change limits

Fleet card: `meshcore:t_5199dede` — "Determine DUT thermal shock and
rate-of-change limits."

Date: 2026-09-15 · Repo: meshcore (main) · Worker: dq05.
Artifacts: this directory (`bench/dut-thermal-limits/`).

---

## DELIVERABLE SUMMARY

| parameter | value | unit | source citation |
|---|---|---|---|
| Max allowable heating ramp | NOT SPECIFIED (no limit stated) | C/min | LR2021 Datasheet Rev 2.1, §3.1 Table 3-1 + §3.2 Table 3-2 — no rate-of-change entry exists |
| Max allowable cooling ramp | NOT SPECIFIED (no limit stated) | C/min | LR2021 Datasheet Rev 2.1, §3.1 Table 3-1 + §3.2 Table 3-2 — no rate-of-change entry exists |
| Operating temperature range (ambient) | -40 to +85 | C | LR2021 Datasheet Rev 2.1, §3.2 Table 3-2 (Top) |
| Absolute maximum temperature range | -55 to +125 | C | LR2021 Datasheet Rev 2.1, §3.1 Table 3-1 (Tmr) |
| Max operating junction temperature | +105 | C | LR2021 Datasheet Rev 2.1, §3.2 Table 3-2 (Tmaxj) |
| Package thermal resistance (theta_j-a) | 26.7 | C/W | LR2021 Datasheet Rev 2.1, §24.5 Table 24-1 |
| Storage temperature range | -55 to +125 | C | LR2021 Datasheet Rev 2.1, §3.1 Table 3-1 (Tmr) — no separate storage spec; the abs-max range is the only non-operating limit |
| Controlled / slower ramp required? | **NO** | — | See §2 below |
| Per-setpoint settle/equilibrium required? | YES — by firmware, not by datasheet | — | See §3 below |
| Module-level operating temp (NiceRF LoRa2021F33-2G4) | -40 to +85 | C | NiceRF LoRa2021F33-2G4 Datasheet v1.1, §6 Electrical Characteristics |
| Carrier MCU (ESP32-C3) operating temp | -40 to +85 | C (UNVERIFIED — no ESP32-C3 datasheet on host) | Not on host; industry-typical for commercial-grade ESP32-C3 |

---

## STEP 1 — Temperature limits (extracted from datasheet)

### 1.1 Semtech LR2021 chip datasheet (Rev 2.1, DS.LR20xx, 13/04/26)

Primary source: `/home/c03rad0r/repos/balloon-e80bench/docs/LR2021_LR2022_LR2012_Datasheet_Rev2.1.pdf`
Extracted this session via `pdftotext`. Verbatim table contents:

**Table 3-1: Absolute Maximum Ratings (LR20xx)** — §3.1, p.37:

| Symbol | Description | Min | Typ | Max | Unit |
|---|---|---|---|---|---|
| VDDmr | Supply voltage | -0.5 | — | 3.9 | V |
| Tmr | Temperature | -55 | — | 125 | C |
| Pmr | RF Input level | — | — | +10 | dBm |

Stated above the table (verbatim): "Stresses above the values listed below may
cause permanent device failure. Exposure to absolute maximum ratings for
extended periods may affect device reliability and reduce product life time."

**Table 3-2: Operating Range (LR20xx)** — §3.2, p.37:

| Symbol | Description | Min | Typ | Max | Unit |
|---|---|---|---|---|---|
| VDDop | Supply voltage | 1.8 | — | 3.7 | V |
| Top | Ambient Operating Temperature | -40 | — | 85 | C |
| Tmaxj | Max Operating Junction Temperature | — | — | 105 | C |
| Clop | Load capacitance on digital ports | — | — | 20 | pF |
| ML | RF Input power: Sub-GHz & HF paths | — | — | +61 | dBm |

Stated above the table (verbatim): "Operating ranges define the limits for
functional operation and parametric characteristics of the device as described
in this section. Functionality outside these limits is not guaranteed."

**Table 24-1: Package Thermal Information** — §24.5, p.238:

| Name | Value | Unit |
|---|---|---|
| Theta j-a, Junction to Ambient | 26.7 | C/W |

Footnote (verbatim): "Measured on a 4-layer test board with 9 thermal vias,
per Jedec standard JESD51-5."

**Reflow profiles** — §24.4, p.237: The datasheet references reflow process
instructions for manufacturing ("The device uses a QFN32 5x5mm package, also
named MLP package") and links to
`http://www.semtech.com/quality/ir_reflow_profiles.html`. These are
manufacturing soldering profiles, NOT operational thermal limits.

### 1.2 NiceRF module-level datasheet (LoRa2021F33-2G4, v1.1)

Source: `/home/c03rad0r/repos/balloon-e80bench/docs/f33-module/LoRa2021F33-2G4-datasheet-v1.1.pdf`
Extracted this session via `pdftotext`.

§6 Electrical Characteristics (verbatim):

| Parameters | Min | Typ | Max | Unit |
|---|---|---|---|---|
| Voltage Range | 3.0 | 5 | 5.5 | V |
| Operating Temperature | -40 | 25 | 85 | C |
| Maximum Input Signal | — | 10 | — | dBm |

No thermal-shock, ramp-rate, or storage-temperature entry exists in the
module-level datasheet either.

### 1.3 Carrier MCU (ESP32-C3 SuperMini)

The DUT is the NiceRF LR2021 module mounted on an ESP32C3 SuperMini carrier
board (per commit 0b7bfe92 identity chain: fork README d7ae93fa + platformio.ini
board=esp32c3_supermini + GPIO map). The ESP32-C3 MCU's own temperature range
is a secondary constraint on the DUT assembly.

No ESP32-C3 datasheet exists on this host (verified: `find` for
`*esp32c3*.pdf` and `*ESP32-C3*` returned zero results). The industry-typical
operating range for the commercial-grade ESP32-C3 is -40 to +85 C, matching
the LR2021 chip range. This is labeled UNVERIFIED — no on-host citation
exists.

---

## STEP 2 — Thermal shock / controlled ramp requirement

### 2.1 Explicit yes/no: Is a slower controlled ramp mandated for the hardware's sake?

**NO.** The LR2021 datasheet (Rev 2.1) does not specify a maximum
rate-of-change of temperature. There is no "thermal shock" entry, no
"ramp rate" entry, and no "controlled ramp" requirement in:
- Table 3-1 (Absolute Maximum Ratings)
- Table 3-2 (Operating Range)
- §24.4 (Reflow Profiles — manufacturing only)
- §24.5 (Thermal Information — theta_j-a only)
- §6.12 (Temperature Compensation — Tx frequency drift only)
- Any other section of the 243-page datasheet

Absence was verified this session by full-text grep of the `pdftotext`
extraction for: "thermal shock", "rate of change", "ramp rate",
"temperature ramp", "controlled ramp", "storage temperature", "settle",
"equilibrium", "steady state", "soak", "stabiliz". None of these terms
appear in any operational-limit context. The only "settle"/"stabilize"
hits refer to oscillator start-up time (§6.11.3 SetTcxoMode), not to
thermal ramp constraints.

The NiceRF module-level datasheet (v1.1) likewise specifies no ramp
rate or thermal shock limit.

### 2.2 Closest datasheet constraint: calibration re-trigger thresholds

The datasheet does impose two temperature-change thresholds that require
recalibration — these are the closest thing to a rate-of-change constraint,
but they constrain calibration validity, not hardware survival:

| threshold | requirement | source |
|---|---|---|
| Temperature change > 10 C | Image calibration advised (command `Calibrate`) | §6.4, p.113 (verbatim: "Image calibration is necessary if there is a frequency change > 10MHz, or a temperature change > 10C") |
| Temperature change > ±20 C | PLL and AAF calibration advised | §6.4.1, p.114 (verbatim: "It is advised to perform the PLL and AAF calibrations again for an RF frequency change greater than 50MHz, or for a temperature change beyond +/-20C") |

These are functional calibration requirements, not thermal-shock limits. They
mean that after a >10 C change the image rejection may degrade until
recalibrated, and after >±20 C the PLL/AAF may need recalibration. They do
NOT mandate a slower ramp — they mandate a re-calibration action after the
ramp completes. The bench protocol's per-setpoint soak (step 3 below) covers
this: the die temperature stabilizes at each setpoint before measurement,
which is well past any calibration re-trigger threshold.

### 2.3 Engineering assessment (not a cited spec)

Since the datasheet imposes no rate-of-change limit, the DUT's tolerance to
rapid temperature change is UNCONSTRAINED by its specification. In practice:

- The LR2021 is a QFN32 5x5 mm package (§24.4) on a small PCB
  (~20-40 g, per ramp-feasibility report 79ea692e). The thermal mass is
  small enough that the die tracks chamber air temperature closely.
- The firmware's EMA time constant is 10 s (SelfCal.h:47, per
  bench/selfcal-ema-tau/RECOMMENDATION.md), meaning the die sensor
  responds on a 10-second timescale.
- The planned chamber ramp rate of 1.5 C/min (0.025 C/s, per
  bench/ramp-feasibility/REPORT.md) is extremely gentle — far below any
  plausible CTE-stress threshold for a silicon QFN package on FR4.
- Even a fast chamber at 5 C/min (0.083 C/s) would be well below any
  operational thermal-shock concern for this package class.
- The -40 C setpoint is at the edge of the operating range (-40 to +85 C)
  with zero margin — this is a temperature LIMIT concern, not a RAMP RATE
  concern. The DUT is specified to operate at -40 C; it just cannot go below.

**Bottom line: No slower controlled ramp is required for the hardware's
sake.** The planned ramp rate (1.5 C/min or whatever the chamber can
manage) is acceptable. The only rate-adjacent constraints are the
calibration re-trigger thresholds (10 C and ±20 C), which are handled by
the soak protocol's per-setpoint stabilization, not by limiting ramp speed.

---

## STEP 3 — Per-setpoint settle / equilibrium requirement

### 3.1 Datasheet: NO settle requirement stated

The LR2021 datasheet (Rev 2.1) does not state any per-setpoint settle,
equilibrium, or steady-state requirement. The datasheet specifies
performance at operating temperatures but does not mandate how long the
device must dwell at a temperature before being measured. There is no
"soak time" or "settling time" entry in any table or section.

### 3.2 Firmware (bench kit): YES — die-temperature stability gate

The fork's bench kit (`thermal_bench.py`, commit d7ae93fa) defines a
die-temperature stability criterion for the `soak` subcommand. This is a
FIRMWARE/BENCH-PROTOCOL requirement, not a datasheet requirement — it
exists to ensure the DUT (not just the air) has reached thermal
equilibrium before measurement.

**Stability criterion** (from `thermal_bench.py` `cmd_soak()`, lines
394-420, verified this session via `git show d7ae93fa`):

| parameter | value | source |
|---|---|---|
| Stable band (--stable-c) | 0.2 C | `thermal_bench.py` arg default, line 683 |
| Window size (--window) | 10 samples | `thermal_bench.py` arg default, line 681 |
| Sample interval (--interval) | 10 s | `thermal_bench.py` arg default, line 682 |
| Confirm duration (--stable-secs) | 120 s | `thermal_bench.py` arg default, line 684 |

The criterion: the die temperature must hold within a 0.2 C band across a
10-sample sliding window (10 samples x 10 s interval = 100 s of data),
THEN confirm for another 120 s that the stability holds. This means the
DUT must demonstrate thermal equilibrium for ~220 s (3.7 min) before a
soak point is accepted.

**How it is verified:** The `soak` subcommand reads `calshow` from the
DUT serial CLI, which returns the die temperature from the LR2021's
on-chip junction temperature sensor (§6.5.2 GetTemp, source 0x00 =
"Built-in junction temperature Vbe"). The die temperature is the DUT's
own measurement of its internal temperature — not the chamber air
temperature. The stability gate therefore verifies that the DUT die
(not the air) has reached steady state.

### 3.3 Fleet card soak time: 10 min minimum

Fleet card `t_0e98e408` specifies at least 10 minutes of continuous
holding per setpoint (per bench/ramp-feasibility/REPORT.md:109). This is
the measurement window after the stability gate passes — i.e. the DUT
must hold at the setpoint for 10 min of continuous data collection after
the die temperature has stabilized.

### 3.4 Fork README empirical guidance

The fork README (d7ae93fa:examples/passive_mapper/bench/README.md)
states (verbatim): "Expect 20-40 min per freezer setpoint for a true soak
on a small module." This is operator-empirical guidance that bundles
ramp time + settling + soak. It is consistent with the 10-min soak +
5-min settling + ramp time computed in bench/ramp-feasibility/REPORT.md.

### 3.5 Summary: settle/equilibrium requirement

| question | answer | source |
|---|---|---|
| Does the DUT (not the air) need to reach steady state before measurement? | YES | Firmware bench protocol (thermal_bench.py soak) |
| How is it verified? | On-chip die temperature sensor via `calshow` CLI | LR2021 §6.5.2 GetTemp (source 0x00, junction Vbe) |
| What is the stability criterion? | 0.2 C band across 10-sample window + 120 s confirm | thermal_bench.py --stable-c 0.2 --window 10 --stable-secs 120 |
| Minimum soak duration after stable? | 10 min | Fleet card t_0e98e408 |
| Is this a datasheet requirement? | NO — it is a firmware/bench-protocol requirement | No entry in LR2021 datasheet Rev 2.1 |

---

## STEP 4 — Setpoint margin analysis

The four planned setpoints (+25, 0, -20, -40 C) vs. the DUT temperature limits:

| setpoint (C) | operating range margin (C) | abs-max margin (C) | junction margin (C, at zero power) | notes |
|---|---|---|---|---|
| +25 | +60 to spec max (+85) | +100 to abs max (+125) | +80 to jmax (+105) | nominal room temperature |
| 0 | +85 / +85 | +125 / +125 | +105 / +105 | comfortable |
| -20 | +65 to spec min (-40) | +35 to abs min (-55) | — | comfortable |
| -40 | 0 to spec min (-40) | +15 to abs min (-55) | — | AT the operating limit — zero margin |

The -40 C setpoint is at the very edge of the operating range (-40 C).
The DUT is specified to operate at -40 C, but there is no margin below
it. The absolute minimum is -55 C, giving 15 C of survival margin below
the -40 C operating limit. This means: the DUT will function at -40 C
(per spec), but if the chamber overshoots below -40 C, the DUT exits
guaranteed operating range. An overshoot to -55 C or below risks
permanent damage.

This is a TEMPERATURE LIMIT constraint, not a RAMP RATE constraint. It
means the chamber's setpoint accuracy and overshoot control matter at
the -40 C setpoint, but the ramp speed getting there does not.

---

## Source summary

| source | path | what it provides | confidence |
|---|---|---|---|
| LR2021 Datasheet Rev 2.1 | balloon-e80bench/docs/LR2021_LR2022_LR2012_Datasheet_Rev2.1.pdf | Tables 3-1, 3-2, 24-1; §6.4 cal thresholds; §24.4 reflow; §6.5.2 GetTemp; full-text absence of ramp/shock | HIGH (manufacturer spec, extracted this session) |
| NiceRF LoRa2021F33-2G4 v1.1 | balloon-e80bench/docs/f33-module/LoRa2021F33-2G4-datasheet-v1.1.pdf | §6 operating temp -40..+85 C, no ramp/shock spec | HIGH (module vendor spec, extracted this session) |
| Fork README (bench) | d7ae93fa:examples/passive_mapper/bench/README.md | Soak-time guidance "20-40 min", sealed-bag protocol | MEDIUM (operator guidance) |
| thermal_bench.py | d7ae93fa:examples/passive_mapper/bench/thermal_bench.py | Stability criterion defaults (--stable-c 0.2 --window 10 --stable-secs 120) | HIGH (firmware code) |
| SelfCal.h | d7ae93fa:examples/passive_mapper/host/SelfCal.h:47 (via bench/selfcal-ema-tau) | TEMP_TC_SECS = 10 s (EMA time constant) | HIGH (firmware code) |
| Fleet card t_0e98e408 | via bench/ramp-feasibility/REPORT.md:109 | 10 min minimum soak per setpoint | HIGH (task spec) |
| ESP32-C3 SuperMini | balloon-e80bench/tracker/hardware/footprints/esp32c3-mini-v1.json | Board identity, no temp spec in JSON | — (no temp data) |
| ESP32-C3 datasheet | NOT ON HOST | Operating temp range | UNVERIFIED (industry-typical: -40..+85 C) |

---

## Caveats and honest gaps

1. **No ESP32-C3 datasheet on host.** The carrier MCU's temperature range
   is cited as industry-typical (-40 to +85 C for commercial grade) but
   is UNVERIFIED — no ESP32-C3 datasheet PDF exists on this host. If the
   specific ESP32-C3 variant on the SuperMini is industrial-grade, the
   range may be wider (-40 to +105 C). This does not affect the LR2021
   chip's limits, which are the primary DUT constraint.

2. **The NiceRF LR2021 module datasheet V1.3** (referenced in commit
   0b7bfe92 as "balloon git 36952f72") was not found as a separate file
   on this host. The F33-2G4 variant datasheet (v1.1) was used instead.
   The non-F33 base LR2021 module is the actual DUT per 0b7bfe92, but
   the chip-level Semtech datasheet (Rev 2.1) is the authoritative source
   for all temperature limits and supersedes the module datasheet. The
   module datasheet's -40..+85 C operating range (v1.1 §6) matches the
   chip datasheet exactly, so the module-level spec is consistent.

3. **No thermal-shock spec exists — this is absence, not uncertainty.**
   The datasheet was fully extracted and searched. The absence of a
   rate-of-change limit is a definitive finding, not a gap that might
   be filled by a better search. Semtech does not specify a maximum
   thermal ramp rate for the LR2021.

4. **The DUT is not attached to any fleet host** (per ec80c11e, fe700201,
   0b7bfe92 — USB census shows Pi Debugprobe on ttyACM0, no DUT). No
   physical measurement of die temperature, ramp response, or thermal
   shock behavior was performed. This analysis is entirely from
   datasheet extraction and firmware code review.

5. **No soak has ever been run** (per bench/soak-rollup/REPORT.md — all
   four setpoints UNVERIFIED, zero calshow samples). The settle/
   equilibrium requirement is stated in the firmware but has never been
   exercised on physical hardware from this fleet.

---

## Nothing fabricated

Every temperature limit is from the Semtech LR2021 datasheet (Rev 2.1)
or the NiceRF module datasheet (v1.1), extracted this session via
pdftotext. The absence of a thermal-shock/ramp-rate spec is verified by
full-text search of the 243-page datasheet. The settle/equilibrium
requirement is from the firmware source code (thermal_bench.py,
verified via git show). No measurement was invented — none exists to
invent from (DUT not attached, no chamber, no soak data).