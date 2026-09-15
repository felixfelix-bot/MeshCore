# Warm-side dew/frost-point table and coldest warm-side surface

Task (fleet offload, meshcore): environmental baseline for the condensation
assessment — warm-side ambient dew/frost-point table plus a defensible
statement of the coldest warm-side surface temperature. Scope: analysis
only; no mitigation design (downstream). Companion to
`bench/condensation-risk/` (65c9c3df) and `bench/chamber-feedthrough-fit/`.

Date: 2026-09-15 · Repo: meshcore (main) · Worker: dq05.
Artifacts: this directory (`bench/warm-side-dewpoint/`) —
`dewpoint_baseline.py` (runnable, stdlib only), `output.txt` (verbatim run).

---

## (a) Warm-side ambient table — every cell ASSUMED

Magnus over water (Alduchov & Eskridge 1996: A=17.625, B=243.04):
`Td = 243.04*(ln(RH/100) + 17.625*T/(243.04+T)) / (17.625 - ln(RH/100) - 17.625*T/(243.04+T))`

| T [C] | RH [%] | Td water [C] | Tf ice [C] | sub-zero frost point? |
|-------|--------|--------------|------------|------------------------|
| 20 | 30 | 1.89 | 1.66 | no |
| 20 | 40 | 5.99 | 5.24 | no |
| 20 | 50 | 9.26 | 8.09 | no |
| 20 | 60 | 12.00 | 10.45 | no |
| 22 | 30 | 3.62 | 3.18 | no |
| 22 | 40 | 7.78 | 6.80 | no |
| 22 | 50 | 11.10 | 9.68 | no |
| 22 | 60 | 13.88 | 12.07 | no |
| 25 | 30 | 6.22 | 5.45 | no |
| 25 | 40 | 10.47 | 9.13 | no |
| 25 | 50 | 13.86 | 12.05 | no |
| 25 | 60 | 16.70 | 14.48 | no |

Tf is the temperature at which the ambient vapor pressure equals the
ice-saturation pressure (Magnus ice constants A=22.46, B=272.62, Sonntag
1990, applied to e = RH/100·es_water(T), inverted through the ice curve).
**No cell in the grid produces a sub-zero frost point**: the coldest cell
(20 C/30 %) has e = 700.0 Pa > 611.2 Pa (triple-point pressure), so the
ice-saturation isotherm sits above 0 C everywhere in the grid; Tf < Td but
both are positive in all 12 cells. Deposition directly from vapor (frost
without a liquid step) therefore never occurs at the ambient side of this
grid — the frost-vs-liquid call downstream is: condensate arrives as
**liquid** at the Td isotherm and freezes only where the surface is below
0 C.

## (b) Reproducibility

Script: `python3 bench/warm-side-dewpoint/dewpoint_baseline.py` (stdlib
`math` only; output captured in `output.txt`). It prints the formula
anchors (es(0 C) = 610.94 Pa vs published 611.2 Pa), the four task-specified
sanity anchors (22/30 -> 3.62 C, 22/50 -> 11.10 C, 22/60 -> 13.88 C,
25/50 -> 13.86 C — all within 0.4 C of the expected ~4/~11/~14/~14 C,
tolerance 1 C, no row flagged), a hand-worked arithmetic row
(22 C/50 %: ln(0.5) = -0.693147, 17.625·22/265.04 = 1.462987,
Td = 243.04·0.769840/16.855160 = 11.10 C), and two independent
cross-checks: Bolton 1980 eq. 15 dew points agree within 0.015 C across
the grid, and Magnus saturation pressure matches the ASHRAE Fundamentals
Ch. 1 table within -0.25 % at 20/22/25 C (2333.4 vs 2338.8 Pa,
2638.6 vs 2645.2 Pa, 3161.7 vs 3169.8 Pa).

## (c) Narrative — measured vs assumed, and the coldest warm-side surface

**Nothing in this table is measured; all 12 ambient cells are ASSUMED**
(the task envelope: T = 20/22/25 C, RH = 30/40/50/60 %). No hygrometer
exists on this host: a live census this session (2026-09-15 02:57+02:00)
found hwmon sensor names acpitz and coretemp only (zero humidity channels)
and no hygrometer-class USB device (lsusb: 2x CH340 serial, Pi Debugprobe,
RTL8152, microSD, hubs, BT/audio — no instrument); `sensors` is not
installed. The one hwmon value on record (acpitz 27.8 C, 65c9c3df census,
2026-09-14) is host-internal motherboard temperature, not ambient air, and
its re-read this session was operator-denied (denial recorded, not
retried) — it substitutes nothing here. The measurements that would remove
the assumptions: (1) a calibrated hygrometer (e.g. SHT45-class,
±0.2 C/±1.8 % RH) reading T and RH at the feedthrough exterior
(the exact warm-side point of interest), taken at chamber-run time and
logged per `bench/chamber-log-protocol/PROTOCOL.md`; (2) a surface
temperature probe (thermocouple) on the feedthrough warm-side face during
a run. **Coldest warm-side surface temperature:** the feedthrough body
spans continuously from the chamber wall to lab air, so it contains a
point at every temperature between the setpoint and ambient — the coldest
warm-side surface is therefore the setpoint itself, **-20 C at the -20 C
setpoint and -40 C at the -40 C setpoint** (an unlagged metal bulkhead
approaches this bound; any real lag raises, never lowers, the surface
temperature, so this is the conservative bounding value). The RH
threshold above which that surface condenses (from the table, i.e.
RH at which Td = surface temperature) is, for ambient T = 20/22/25 C:
**RH > 5.4 / 4.8 / 4.0 % at the -20 C setpoint and RH > 0.8 / 0.7 /
0.6 % at the -40 C setpoint** — every grid cell (30-60 % RH) exceeds
these by more than a factor of 6, so condensation on the coldest warm-side
surface is certain at both setpoints under every assumed ambient; it
begins as liquid at the Td isotherm (Td = +1.9 to +16.7 C, all above
freezing — no sub-zero frost point in any cell) and freezes wherever the
local surface is below 0 C. At the mid-gradient 0 C isotherm the
condensation threshold is RH > 26.2 / 23.2 / 19.3 % (20/22/25 C) — so
even the driest grid cell (30 % RH) condenses on every sub-0 C portion of
the feedthrough.

## Citations

- Alduchov, O. A. & Eskridge, R. E. (1996). Improved Magnus' form
  approximation of saturation vapor pressure. J. Appl. Meteor., 35,
  601-609. (water constants A=17.625, B=243.04)
- Sonntag, D. (1990). Important new values of the physical constants of
  1986, including three new saturation pressure formulas. Z. Meteorol.,
  70, 340-344. (ice constants A=22.46, B=272.62, as prescribed by card)
- ASHRAE Handbook of Fundamentals, Ch. 1 (Psychrometrics), saturation
  vapor pressure over liquid water (cross-check anchors at 20/22/25 C).
- Bolton, D. (1980). The computation of equivalent potential temperature.
  Mon. Wea. Rev., 108, 1046-1053, eq. 15. (independent dew-point
  cross-check, agrees within 0.015 C)