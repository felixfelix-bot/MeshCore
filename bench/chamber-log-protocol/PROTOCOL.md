# Chamber 10-minute stability logging protocol + blank capture template

## Section A — Logging protocol specification (normative)

**A.1 Scope and integrity.** This document specifies how chamber
stability data at the four commanded setpoints (+25 C, 0 C, -20 C,
-40 C) SHALL be logged, and provides the blank capture template in
Section B. MUST and SHALL are binding; MAY marks an allowed choice.
This file contains no test run, no sample data, and no measurement,
observation, or estimate of any physical quantity. The only numeric
quantities anywhere in this file are normative rule parameters (the
four commanded setpoint designations, the 10-second sampling
interval, the 10-minute minimum window duration), structural labels
(rule and entry numbering), and one explicitly labelled ISO-8601
timestamp format illustration in rule A.7. No value cell in Section B
is pre-filled, and none may be.

**A.2 Command step (per setpoint).** For each setpoint entry the
operator MUST command the chamber to that setpoint. The operator
SHALL record:

- `setpoint_value_C` — the commanded setpoint for this entry, in C.
- `command_accepted` — Y if the chamber accepted or acknowledged the
  command, N if it did not. If N, the operator records N, aborts the
  attempt, and retries as a fresh fill of the same entry with the
  structure unchanged; values from a failed attempt MUST NOT be
  reused.
- `displayed_setpoint_C` — the setpoint exactly as shown on the
  chamber's own display/readout, transcribed verbatim with no
  rounding and no unit conversion.

**A.3 Temperature source.** Every air-temperature value in this
capture — the sampled series and every field derived from it — MUST
be read from the chamber's OWN built-in air-temperature
sensor/readout. Use of an external probe, thermocouple, DUT-side
sensor, or any other secondary instrument for any temperature field
is FORBIDDEN. The chamber's own sensor used MUST be identified in
the run metadata (`sensor id`).

**A.4 Sampling cadence.** The sampling interval MUST be fixed at
exactly one sample every 10 seconds. The cadence MUST NOT be changed
during a window.

**A.5 Window duration and continuity.** The logging window for each
setpoint MUST span at least 10 CONTINUOUS minutes with no gaps. A
window is continuous if and only if every consecutive pair of
accepted samples in it is separated by the fixed sampling interval
of A.4. A sample that is missing, late beyond that cadence,
unreadable, or otherwise rejected constitutes a GAP. On a gap the
window ends at the last accepted sample before the gap, a new window
starts at the next accepted sample, and the 10-continuous-minute
minimum applies anew to the new window; the gap itself MUST also be
recorded in `alarms_faults` with its timestamp. An accepted sample is
one successfully read from the chamber's own readout and timestamped,
at the moment of reading, from the single clock designated under
A.7.

**A.6 Window boundary timestamps.** `window_start_timestamp` is the
timestamp of the FIRST accepted sample of the continuous window.
`window_end_timestamp` is the timestamp of the LAST accepted sample
of that same continuous window. Every derived field
(`min_air_temp_C`, `max_air_temp_C`, `peak_to_peak_spread_C`,
`mean_air_temp_C`, `observed_offset_C`) MUST be computed from
exactly the accepted samples lying within [window_start_timestamp,
window_end_timestamp] inclusive — never from samples before the
window, after it, or across a gap.

**A.7 Clock policy (binding).** Every timestamp in this capture MUST
come from ONE SINGLE clock source: one designated device, one
timezone, used for all timestamps in all four entries. The operator
MUST designate the single clock device before issuing the first
command. The host clock and the chamber clock MUST NEVER be mixed:
timestamps read from the chamber's internal clock MUST NOT appear in
this capture. All timestamps MUST be written in ISO-8601 with an
explicit timezone offset, in exactly the shape shown here — FORMAT
ILLUSTRATION ONLY, NOT A MEASUREMENT: `2025-01-01T14:03:00+01:00`.
Every timestamp recorded in Section B MUST follow this shape.

**A.8 Recording-window rule (binding choice).** Of the two permitted
conventions — (a) begin the logging window only after the chamber
reports the setpoint as reached, or (b) a fixed soak/stabilisation
rule — this protocol adopts (a). The window MUST begin only after
the chamber reports the setpoint as reached; the first accepted
sample MUST be taken at or after that report, and no sample taken
before it may be part of the window. Justification: the chamber's
own "setpoint reached" report is a device-native, unambiguous
trigger, so the window start needs no separately defined
stabilisation criterion; and the window then records stability at
the setpoint, while approach dynamics are captured separately by
`time_to_first_reach_setpoint_from_ambient` and `overshoot_C`.

**A.9 Alarms and faults.** Every alarm, fault, warning, error,
sampling gap, or failed read observed during a setpoint's capture
MUST be recorded in `alarms_faults`, verbatim, each with its own
timestamp from the single clock. If none occurred, the operator MUST
record the explicit value `none`; the field MUST never be left blank,
and the absence of alarms MUST NOT be expressed by omission.

**A.10 Duration unit (stated once, used consistently).**
`time_to_first_reach_setpoint_from_ambient` MUST be recorded in
mm:ss (elapsed minutes and seconds, colon-separated). This unit
choice is made exactly once, here, and MUST be used consistently
everywhere the field appears, including its Section B field label.
The quantity is the elapsed time, per the single clock, from the
timestamp at which the setpoint command is issued (chamber air at
its pre-command ambient state) to the timestamp of the chamber's own
"setpoint reached" report for that setpoint (rule A.8).

**A.11 Derived fields.** `min_air_temp_C` and `max_air_temp_C` are
the minimum and maximum of the window's accepted samples.
`peak_to_peak_spread_C` = `max_air_temp_C` - `min_air_temp_C`.
`mean_air_temp_C` is the arithmetic mean of the window's accepted
samples. `observed_offset_C` = `mean_air_temp_C` - `setpoint_value_C`
(mean observed air temp minus setpoint). All derived values MUST be
computed only from the window series defined by A.5 and A.6.

**A.12 Overshoot.** `overshoot_C` is the magnitude of the largest
excursion of the chamber's own air-temperature readout beyond the
commanded setpoint value — in the direction of travel from ambient
toward the setpoint — observed at any time from the issue of the
setpoint command until `window_end_timestamp`. If no excursion
beyond the setpoint occurs in that span, the operator MUST record
the explicit value `none`; the cell MUST never be left blank.

**A.13 Series recording format.** `sampled_air_temp_series` is an
ordered array of `{timestamp ISO-8601, air_temp_C}`. It MUST be
recorded in the labelled blank block of its entry, one sample per
line, in sampling order, each line of the shape
`<ISO-8601 timestamp>,<air_temp_C in C>`, with every timestamp from
the single clock.

**A.14 Template integrity and entry independence.** Section B MUST
be usable with zero edits to its structure: the operator fills value
cells and the series blocks only. Every value cell MUST be filled
from a real observation; guessing, estimating, simulating, or copying
a value from another entry is FORBIDDEN. The four setpoint entries
are distinct and self-contained — no grouping, no aliasing, no "same
as above": every field of every entry carries its own recorded
value. If a field genuinely cannot be captured, the operator MUST
record the reason as free text in that cell rather than leave it
blank.

## Section B — Capture template (entirely blank — fill every value cell)

Every value cell below is intentionally empty. Nothing has been
pre-filled, invented, or estimated. Do not edit the structure — fill
value cells and the per-entry series block only.

### B.1 Run metadata

| field | value |
|---|---|
| operator | |
| date (ISO-8601 calendar date) | |
| chamber make/model | |
| sensor id (the chamber's OWN air-temperature sensor/readout) | |

### B.2 Setpoint entry 1 of 4 — commanded setpoint +25 C

| field | unit / domain | value |
|---|---|---|
| setpoint_value_C | C | |
| command_accepted | Y/N | |
| displayed_setpoint_C | C | |
| window_start_timestamp | ISO-8601 | |
| window_end_timestamp | ISO-8601 | |
| sampled_air_temp_series | ordered array of {timestamp ISO-8601, air_temp_C} — record in the block immediately below this table | |
| min_air_temp_C | C | |
| max_air_temp_C | C | |
| peak_to_peak_spread_C | C — defined as max - min | |
| mean_air_temp_C | C | |
| observed_offset_C | C — defined as mean observed air temp minus setpoint | |
| time_to_first_reach_setpoint_from_ambient | duration (mm:ss) | |
| overshoot_C | C — peak excursion beyond setpoint before stabilising | |
| alarms_faults | free text — 'none' if no alarms | |

sampled_air_temp_series (ordered array of {timestamp ISO-8601,
air_temp_C}) — record one sample per line, in sampling order:

```text

```

### B.3 Setpoint entry 2 of 4 — commanded setpoint 0 C

| field | unit / domain | value |
|---|---|---|
| setpoint_value_C | C | |
| command_accepted | Y/N | |
| displayed_setpoint_C | C | |
| window_start_timestamp | ISO-8601 | |
| window_end_timestamp | ISO-8601 | |
| sampled_air_temp_series | ordered array of {timestamp ISO-8601, air_temp_C} — record in the block immediately below this table | |
| min_air_temp_C | C | |
| max_air_temp_C | C | |
| peak_to_peak_spread_C | C — defined as max - min | |
| mean_air_temp_C | C | |
| observed_offset_C | C — defined as mean observed air temp minus setpoint | |
| time_to_first_reach_setpoint_from_ambient | duration (mm:ss) | |
| overshoot_C | C — peak excursion beyond setpoint before stabilising | |
| alarms_faults | free text — 'none' if no alarms | |

sampled_air_temp_series (ordered array of {timestamp ISO-8601,
air_temp_C}) — record one sample per line, in sampling order:

```text

```

### B.4 Setpoint entry 3 of 4 — commanded setpoint -20 C

| field | unit / domain | value |
|---|---|---|
| setpoint_value_C | C | |
| command_accepted | Y/N | |
| displayed_setpoint_C | C | |
| window_start_timestamp | ISO-8601 | |
| window_end_timestamp | ISO-8601 | |
| sampled_air_temp_series | ordered array of {timestamp ISO-8601, air_temp_C} — record in the block immediately below this table | |
| min_air_temp_C | C | |
| max_air_temp_C | C | |
| peak_to_peak_spread_C | C — defined as max - min | |
| mean_air_temp_C | C | |
| observed_offset_C | C — defined as mean observed air temp minus setpoint | |
| time_to_first_reach_setpoint_from_ambient | duration (mm:ss) | |
| overshoot_C | C — peak excursion beyond setpoint before stabilising | |
| alarms_faults | free text — 'none' if no alarms | |

sampled_air_temp_series (ordered array of {timestamp ISO-8601,
air_temp_C}) — record one sample per line, in sampling order:

```text

```

### B.5 Setpoint entry 4 of 4 — commanded setpoint -40 C

| field | unit / domain | value |
|---|---|---|
| setpoint_value_C | C | |
| command_accepted | Y/N | |
| displayed_setpoint_C | C | |
| window_start_timestamp | ISO-8601 | |
| window_end_timestamp | ISO-8601 | |
| sampled_air_temp_series | ordered array of {timestamp ISO-8601, air_temp_C} — record in the block immediately below this table | |
| min_air_temp_C | C | |
| max_air_temp_C | C | |
| peak_to_peak_spread_C | C — defined as max - min | |
| mean_air_temp_C | C | |
| observed_offset_C | C — defined as mean observed air temp minus setpoint | |
| time_to_first_reach_setpoint_from_ambient | duration (mm:ss) | |
| overshoot_C | C — peak excursion beyond setpoint before stabilising | |
| alarms_faults | free text — 'none' if no alarms | |

sampled_air_temp_series (ordered array of {timestamp ISO-8601,
air_temp_C}) — record one sample per line, in sampling order:

```text

```