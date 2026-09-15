# Feedthrough survey protocol — ID scheme, measurement rules, provenance, photo log

Fleet card: `meshcore:t_03954030` — "Define feedthrough ID scheme, measurement
protocol, and photo log." This is the shared protocol every surveyor follows
so the door and wall inventories merge cleanly.

Date: 2026-09-15, session 14:0x local (UTC+2) · Repo: meshcore (main) ·
Worker: dq05 (profile worker-heavy) · Host: `c03rad0r-DQ05proplus`.
Artifacts: this file (`bench/feedthrough-survey-protocol/PROTOCOL.md`).

Consumers (this protocol is their required input): door survey
`t_cad6b6e8`, wall survey `t_ad3aee13`, penetration/gasket survey
`t_f2b50f53` (already frozen against this card's body in commit `621a2e57`).

Language: MUST and SHALL are binding; MAY marks an allowed choice. This file
is normative only — it contains no measurement, no run, and no sample data.
The only numeric quantities in this file are normative rule parameters taken
from the card body itself (the 5-150 mm caliper range, the 0.05 mm zero
exclusion limit, the 0.2 mm ellipticity threshold, the 90° separation) plus
explicitly labeled cross-references. No diameter of any real bore appears
here.

---

## 1. Feedthrough ID scheme

Every feedthrough (any bore, port, gland, boot, blanked hole, or pass-through
crossing the chamber boundary) receives exactly one ID from the prefix table
below. IDs are permanent once assigned.

### 1.1 ID prefix table

| Region | Prefix | SIDE values | Example | Numbering |
|---|---|---|---|---|
| Door region (door leaf, frame, gasket line, and the wall surface the door is mounted in) | `FT-DOOR-n` | — | `FT-DOOR-1` | one sequence for the whole door region, n = 1, 2, ... |
| Wall regions | `FT-WALL-<SIDE>-n` | `TOP`, `BOTTOM`, `LEFT`, `RIGHT`, `REAR` | `FT-WALL-LEFT-1` | one independent sequence per SIDE, n = 1, 2, ... |
| Late finds (reserve) | `FT-WALL-UNASSIGNED` | — | `FT-WALL-UNASSIGNED` | none — see 1.4 |

Side orientation: the surveyor stands OUTSIDE the chamber facing the closed
door. `LEFT` and `RIGHT` are the surveyor's left and right in that stance;
`REAR` is the wall opposite the door wall; `TOP` and `BOTTOM` are above and
below. The door wall carries no `FT-WALL-*` entries — everything on it
belongs to the `FT-DOOR-n` region, so the two inventories are exhaustive and
disjoint and merge without overlap arbitration.

### 1.2 Assignment order (binding)

IDs are assigned in the order encountered walking clockwise from the door
hinge. Procedure: stand outside facing the closed door; start at the hinge
edge; walk clockwise around the chamber exterior; each feedthrough first
encountered takes the next number in its region's sequence. Within one
region sequence, numbers must never be skipped, reused, or reassigned.

### 1.3 Non-bore features

A feature that is not a bore (e.g. the door gasket itself) may carry a
descriptive suffix instead of a number — `FT-DOOR-GASKET` is the committed
precedent (sibling `t_f2b50f53` G1 row, `621a2e57`). Such labels never
consume numbers from any bore sequence.

### 1.4 Reserved label `FT-WALL-UNASSIGNED`

Anything found after the initial clockwise pass (hidden behind a rack,
visible only from inside, discovered on re-inspection) is recorded
immediately under the reserved label `FT-WALL-UNASSIGNED`, with a free-text
location note and photos per section 5. Late finds are NEVER renumbered into
the frozen clockwise sequences (renumbering breaks cross-references); if
more than one late find exists, each keeps the same reserved label and is
distinguished by its location note and photo filename. A survey lead MAY
later promote an `FT-WALL-UNASSIGNED` entry to a permanent
`FT-WALL-<SIDE>-n` ID only by appending it as the next unused number of that
side's sequence and noting the promotion in the record.

---

## 2. Measurement protocol — instrument per bore, and calibration

### 2.1 Instrument assignment (binding)

| Bore condition | Instrument | Provenance method token (see 4) |
|---|---|---|
| Inner diameter 5-150 mm, accessible at the surface | digital calipers (internal measuring jaws) | `measured (calipers)` |
| Small bores below the 5 mm caliper floor | pin gauge set | `measured (pin gauge)` |
| Deep recesses — jaw depth of standard calipers cannot reach the bore | internal-jaw calipers (extended internal jaws) | `measured (internal-jaw calipers)` |

Boundary rules: at 5.0 mm and above use calipers; below 5.0 mm use the pin
gauge set. A deep recess of ANY diameter goes to internal-jaw calipers
regardless of size. Where only the outer circumference is accessible, the
sibling-survey method is retained as an allowed addition (sibling
`t_f2b50f53` `621a2e57`): flexible tape, ID = C/π, recorded as
`measured (tape, ID = C/π)`. Bores above 150 mm are outside the named
caliper range: if measured, name the instrument actually used in the tag
(the tape method is the norm); if no instrument can reach, the field is
UNKNOWN with reason — an estimate is never a substitute (see 4.3).

The instrument used MUST be recorded on every row; no row may be ambiguous
about which instrument produced its numbers.

### 2.2 Calibration step (binding, before the first measurement of the visit)

Zero the calipers on the closed jaws and record the reading — the actual
displayed zero value (e.g. 0.00 mm) is logged for each caliper (standard and
internal-jaw) in the survey run metadata, even when it reads exactly zero.
Any gauge whose zero is off by more than 0.05 mm MUST be noted in the run
metadata (instrument identity + its zero reading) and EXCLUDED from use in
the survey. Excluded gauges produce no survey rows. Pin gauges have no zero
step; their set identity is recorded in the run metadata instead.

---

## 3. Repeatability rule (binding)

Each bore MUST be measured twice, the two measurements taken 90 degrees
apart in the bore plane (rotate the measurement axis a quarter turn between
readings). BOTH readings MUST be recorded in the entry — always, whether
they agree or not; never record only one.

If the two readings differ by more than 0.2 mm, the entry MUST be marked
ELLIPTICAL, with both numbers kept side by side in the record. ELLIPTICAL
entries are never averaged, never collapsed to one number, and never
"corrected" — both readings stand. The ELLIPTICAL mark occupies its own
field (see 5.4) so downstream fit math sees the ovality explicitly.

---

## 4. Data-provenance tags (exact vocabulary)

### 4.1 The three tags

| Tag | Exact meaning |
|---|---|
| `documented` | the value was read off a datasheet, nameplate, or silkscreen — the source MUST be named in the record |
| `measured (<instrument>)` | the value was taken this survey with the named instrument and is included in the record — the parenthetical names the instrument from 2.1: `measured (calipers)`, `measured (pin gauge)`, `measured (internal-jaw calipers)`, `measured (tape, ID = C/π)` |
| `UNVERIFIED` | anything else — a value that was neither read from an authoritative surface nor taken with a named instrument this survey |

The sibling survey's part-level labels `datasheet` / `vendor spec — <which>`
are `documented` sub-forms (they name the surface read) and merge into
`documented` in the combined inventory.

### 4.2 Unfillable fields

A field that cannot be captured records UNKNOWN with the concrete reason.
That is a cell status, not a provenance tag, and it never coexists with a
number in the same cell.

### 4.3 Estimates are FORBIDDEN

Estimated or interpolated diameters are FORBIDDEN as recorded values. A
soft number may never occupy a diameter value cell and may never carry a
`measured` or `documented` tag. If a soft number is unavoidable, it goes to
the notes column only, labeled ESTIMATED, and the diameter cell stays
UNKNOWN with reason. (Operationalization as already committed by sibling
`t_f2b50f53` `621a2e57`; identical rule, stated here as the shared
vocabulary's normative source.)

---

## 5. Photo convention and photo log

### 5.1 Photos per feedthrough (binding)

Two photos per feedthrough, minimum:

1. One establishing photo — the feedthrough whole, in its surroundings.
2. One close-up — the caliper jaws (or the gauge actually used) IN FRAME,
   engaged on the bore.

In BOTH frames the ID label MUST be visible: before photographing, write
the assigned ID on tape/label stock and place it beside the feedthrough so
it appears in both photos. Every photo contains a visible scale reference —
the caliper jaws make this automatic in the close-up; the establishing photo
includes the gauge or a rule in frame.

### 5.2 Filenames (binding)

Every photo filename MUST contain the feedthrough ID as an exact substring.
Recommended shape: `<ID>_establishing.<ext>` and `<ID>_closeup.<ext>`
(e.g. `FT-DOOR-1_establishing.jpg`, `FT-DOOR-1_closeup.jpg`,
`FT-WALL-REAR-2_closeup.jpg`). `FT-WALL-UNASSIGNED` entries carry the
location note in the filename after the ID (e.g.
`FT-WALL-UNASSIGNED_behind-rack_closeup.jpg`).

### 5.3 Photo log (the deliverable's log component)

The survey maintains one photo log keyed by feedthrough ID, one row per
feedthrough: ID | establishing-photo filename | close-up filename |
status. A photo not yet taken is recorded as NONE with the reason — never
left blank. The photo log is part of the survey record and merges with the
inventory rows by ID.

### 5.4 Per-feedthrough record fields (the merge interface)

Door and wall survey rows MUST use the same field list so the inventories
merge by ID without mapping:

| Field | Vocabulary / shape |
|---|---|
| id | exact ID per section 1 |
| region_side | `DOOR` or `TOP`/`BOTTOM`/`LEFT`/`RIGHT`/`REAR` |
| location | free text |
| reading_a_mm, reading_b_mm | both readings per section 3, mm |
| elliptical | `Y`/`N` (Y when readings differ by > 0.2 mm) |
| instrument | `calipers` / `pin gauge` / `internal-jaw calipers` / `tape` |
| zero_reading_mm | the recorded zero of the instrument used (2.2) |
| provenance | one tag from 4.1 |
| occupied | exactly `empty` or `used by <description>` (occupancy vocabulary per sibling `t_f2b50f53`); if unobservable, UNKNOWN with reason |
| photo_establishing, photo_closeup | filenames per 5.2, or NONE with reason |
| notes | free text — the ONLY column where an ESTIMATED soft number may appear (4.3) |

---

## Status of this protocol (nothing fabricated)

This file defines rules; it measures nothing. Zero feedthroughs have been
enumerated, zero bores measured, zero photos taken: no thermal chamber
exists on any record or host (fleet locate/identify cards resultless; five
prior bench reports concur), so there is no subject, and this host has no
camera device (fresh census this session 14:01+02:00: `/dev/video*` absent,
`/sys/class/video4linux` absent, `v4l2-ctl` absent) and no measurement
instruments attached (no usbtmc/gpib nodes; prior session USB censuses
concur). The photo log is therefore defined (5.3) and empty. When a human
names the chamber, this protocol executes verbatim on the one site visit
and the measured rows drop directly into the fit-decision table of
`bench/chamber-feedthrough-fit` (`fe700201` §3d) for instant PASS/FAIL.

Downstream compatibility note: sibling `t_f2b50f53` (commit `621a2e57`)
froze its conventions against this card's body before this file existed;
this file matches that committed adoption term-for-term (prefixes,
clockwise-from-hinge order, UNASSIGNED reserve, instrument assignment,
0.05 mm zero exclusion, 90°-apart double measure, 0.2 mm ELLIPTICAL mark,
documented/measured/UNVERIFIED vocabulary, forbidden estimates,
establishing+close-up photo pair with ID in filename) and adds only the
explicit merge-interface field list (5.4).