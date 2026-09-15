# Warm-side ambient (feedthrough exterior / lab air) — measurement status + assumption register

Task (fleet offload, meshcore): make the MEASURED-vs-ASSUMED status of
every warm-side ambient number unambiguous, and name the exact
measurement that would remove each assumption. Scope: analysis only; no
dew-point math here — `bench/warm-side-dewpoint/` (182d4755) owns the
psychrometric table.

Date: 2026-09-15 · Repo: meshcore (main @ e096bbad) · Worker: dq05.
Nothing measured this session (standing no-probe constraint respected);
nothing fabricated.

## (i) MEASURED — search result for warm-side feedthrough air

**No measurement available.** No hygrometer and no ambient-air T/RH
reading of the feedthrough exterior exists on any record. Census
evidence, MEASURED-negative: hwmon = acpitz + coretemp only (2 thermal
zones, 0 humidity inputs) — 65c9c3df `bench/condensation-risk/REPORT.md`
§1a (2026-09-14), re-swept live 182d4755
`bench/warm-side-dewpoint/REPORT.md`:64-72 (2026-09-15 02:57+02:00),
third census ec80c11e `bench/chamber-preflight/REPORT.md`:139-143;
repeated `lsusb` censuses (all sessions): zero instrument-class USB
devices. No operator-stated or fetched lab value exists on any record;
no chamber run has ever occurred (dry run t_da84afb3 FAIL, zero
samples; chamber-holds 72f3aab9: no chamber ever commanded, zero
air-temp data). The only readings that exist are HOST-INTERNAL and
substitute nothing:

| reading | value | timestamp | label |
|---|---|---|---|
| acpitz `/sys/class/hwmon/hwmon0` (motherboard ACPI zone) | 27.8 C | 2026-09-15T02:37+02:00 (ec80c11e:139; same value 2026-09-14 65c9c3df §1a, and d7b9107c routing-freeze) | MEASURED [host-internal proxy: biased high by motherboard self-heating; not ambient air; not at the feedthrough; no RH companion value] |
| coretemp hwmon1 (CPU package) | 98.0 C | same censuses | MEASURED [host-internal, irrelevant] |

**Warm-side air T and RH: NO MEASUREMENT AVAILABLE — both ASSUMED.**

## (ii) ASSUMED grid (whole grid)

| warm-side air T (ASSUMED) | warm-side air RH (ASSUMED) |
|---|---|
| 20 C · 22 C · 25 C | 30 % · 40 % · 50 % · 60 % |

12 cells (3x4), every cell ASSUMED. Envelope origin: fleet cards
t_1add22bc / t_09c431c2, as carried by 65c9c3df §1b and 182d4755 §(a).
Why the whole grid is ASSUMED: the censuses in (i) prove no T/RH
instrument exists at this bench; no run has ever happened; no operator
or external source ever supplied a value. It is a planning bracket over
typical conditioned-lab conditions — nothing in it is anchored to this
bench. (The RH span coinciding with the EN 300 220 manufacturer-declared
test conditions RH 30-60 % [DOCUMENTED], 8427EU011624W1 per 4a485f2b, is
documentation coincidence, not provenance.)

## (iii) Assumption register — the exact measurement that removes each

| assumed quantity | replacement measurement | instrument class [SPEC] | mounting location | sampling + when |
|---|---|---|---|---|
| T = 20/22/25 C (ASSUMED) | warm-side air T at run time | SHT45-class calibrated T+RH combo probe, datasheet ±0.2 C / ±1.8 % RH [SPEC]; none on bench — MUST-PROCURE | free air within ~50 mm [SPEC — mounting requirement set here] of the feedthrough warm-side connector face, at feedthrough height, out of chamber-exhaust and host-enclosure flows | at chamber-run time: reading at session start + continuous log through the whole window; cadence per chamber-log-protocol A.4 (10 s [PROTOCOL]), floor 1 sample / 10 min [SPEC] |
| RH = 30/40/50/60 % (ASSUMED) | warm-side air RH at run time | the same single probe — one instrument removes both assumptions | same | same |
| supporting (not an ambient quantity): warm-face surface T | feedthrough warm-end surface temperature | K-class thermocouple, ±1 C [SPEC] | bonded to the warm-side bulkhead/SMA face | same window (already on record, 182d4755:73-79) — the condensation verdict needs a surface temperature, not just air |

## (iv) Bias / uncertainty caveats on the replacement measurements

- Stratification: conditioned labs can stratify ~1-3 K vertically
  [TYPICAL, UNVERIFIED] — mount at feedthrough height; a single-point
  reading misses local gradients.
- Self-heating: probe self-heating < ~0.1 C at idle [TYPICAL, UNVERIFIED]
  — keep the probe in moving air and allow settling.
- RH drift: capacitive RH sensors drift ~0.5 %RH/yr [TYPICAL, UNVERIFIED]
  — verify against a salt-standard check or a second probe before
  trusting to spec.
- Sensor condensation: the probe stays in room air, NOT in the cold
  boundary layer at the bulkhead — a wet sensor pins RH toward
  saturation (and T toward wet-bulb) and is invalid until fully dried.
- Staleness: lab RH swings by tens of % with weather/HVAC/occupancy
  [TYPICAL] — a pre-run spot check alone is unrepresentative; hence
  run-time logging is required, not optional.
- The 27.8 C [MEASURED, host-internal] acpitz value must never be
  reused as an ambient anchor.