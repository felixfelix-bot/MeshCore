# Chamber penetration survey — field protocol, ID scheme, and table template

Repo: meshcore (fork checkout) · `bench/chamber-penetration-survey/`
Dispatch: "Prepare penetration survey protocol, ID scheme, and table
template" (fleet card family t_964d4469; downstream consumers are the
chamber walk t_57c1b9fd and the consolidation t_ad3aee13).

This file is the field protocol the surveyor carries to the chamber.
`TEMPLATE.md` and `template.csv` in this directory are the blank tables the
surveyor fills in on site.

Subject: every penetration of the thermal chamber boundary — dedicated
feedthrough ports, the door gasket pass-through, unused bulkhead holes,
cable boots/glands, spare flange holes, blank cutouts.

Related committed records (do not contradict or renumber them):
- `bench/chamber-penetrations-gasket/` (621a2e57) — the G1 + P1..P5 class-row
  skeleton whose conventions (clockwise-from-hinge order, G1 as a non-bore
  label outside the P series, estimates segregated to notes) are restated
  here as binding rules.
- `bench/feedthrough-survey-protocol/PROTOCOL.md` (abe0d36f, t_03954030) — the
  sibling feedthrough protocol with the FT-* region IDs; its calibration,
  repeatability and photo rules apply to feedthrough bores generally. The
  P/G rows of THIS survey are the penetration record; cross-reference FT-*
  entries by photo filename and location note, never by renumbering.

Language: MUST / always / never are binding. Every rule marked "verbatim" is
copied into the survey record unchanged. This file defines rules only — it
enumerates nothing, measures nothing, and contains no survey data.

---

## 1. ID scheme and traversal order — fixed before anyone touches the chamber

### 1.1 IDs

- `P1, P2, P3, …` — every physical penetration of the chamber wall, bulkhead,
  or door EXCEPT the door gasket pass-through, numbered in the traversal
  order of §1.2.
- `G1` — the door gasket pass-through. It is ALWAYS `G1`, it is NEVER
  numbered in the `P` series, and no other feature may take the ID `G1`
  (non-bore-label precedent: the G1 row of 621a2e57 — a G label consumes no
  P number).

IDs are permanent once assigned.

### 1.2 Traversal order (the one fixed pass that assigns the P numbers)

1. Stand OUTSIDE the chamber, facing the main door.
2. The **main door hinge** is the fixed origin landmark (position 0).
3. Walk **clockwise around the chamber as viewed from directly above it
   (plan view)**, one direction only, all the way back to the hinge.
   (Facing the closed door from outside, "clockwise from above" means you
   set off toward your left-hand side and keep the same sense the whole
   loop.)
4. Number each penetration `P1, P2, P3, …` **in the order you physically
   pass it** on that single loop.
5. For each row record the **clock position** of the penetration — a clock
   face superimposed on the plan view, 12 o'clock = the chamber-wall point
   diametrically opposite the hinge. Clock positions MUST increase
   monotonically around the loop; if they do not, the enumeration is wrong
   and MUST be redone before the table is accepted.
6. Complete the full loop back to the hinge before the numbering is final.

### 1.3 Late discovery — no renumbering (verbatim)

> Reserve IDs are not to be renumbered later — if an ID is discovered late,
> it gets the next unused number in traversal order and the table notes the
> out-of-order insertion.

Operationalized: if P1–P9 exist and a tenth penetration is found afterwards
(anywhere, in any pass), it becomes P10 — the next unused number — and its
Notes cell must say it was inserted out of order. Existing IDs never move,
never get reused, and never get reassigned.

### 1.4 Exhaustive enumeration

Do not stop at the obvious ports. Check every candidate class: dedicated
feedthrough ports, the door gasket pass-through (G1), unused bulkhead
holes, cable boots/glands, spare flange holes, blank cutouts. After the
first numbering pass, sweep the chamber a SECOND time; anything found on the
second sweep is numbered under §1.3.

---

## 2. Tagging method

- Tag every penetration with a physical label: **tape + marker, or numbered
  stickers** — large enough to read in a photo.
- **Character height ≥ 20 mm**, high contrast (black on light tape, white on
  dark), so the ID is legible in a phone/camera frame at working distance.
- Place the tag **physically adjacent to the penetration** — at or within
  ~20 mm of it, never covering the bore, and in the same plane as the
  penetration so tag and bore are both in focus.
- The tag MUST be **legible in frame** in BOTH required photos (§3). If a
  tag is unreadable in review, retake the photo — never rely on memory of
  which penetration it was.

---

## 3. Photo protocol (per penetration)

Exactly two photos per penetration, named by ID so they cross-reference the
table:

1. **Wide shot** — shows the penetration, the ID tag, and the chamber
   context (the surrounding wall/bulkhead/door frame that locates it).
   Filename: `<ID>_wide.jpg`
2. **Close shot** — shows the penetration and the ID tag **with a scale reference (ruler or calipers) visible in the same frame**.
   Filename: `<ID>_close.jpg`

Naming rules: ID in upper case, exactly two files per ID, no spaces, `.jpg`
extension.

Examples: `P1_wide.jpg`, `P1_close.jpg`, `G1_wide.jpg`, `G1_close.jpg`,
`P10_wide.jpg`, `P10_close.jpg`.

Both filenames are recorded in the Location column of the table (§6).

---

## 4. Measurement method — decision rule (verbatim)

> Use calipers on the inner bore wherever the bore is directly reachable;
> otherwise measure outer circumference with flexible tape and report
> ID = C/pi; if the port is occupied and cannot be measured without
> disturbing the setup, record UNKNOWN and state the reason. No method may
> be silently substituted — the method must appear in the Measurement source
> column.

Applied in order, each row produces exactly one outcome:

1. Inner bore directly reachable → measure with **calipers** → Measurement
   source `calipers`.
2. Otherwise → outer circumference with **flexible tape** → report inner
   diameter as **ID = C/π** → Measurement source `tape (ID = C/pi)`.
3. Port occupied and not measurable without disturbing the setup → Inner
   diameter `UNKNOWN`, the specific reason in Notes, Measurement source
   `UNKNOWN`.

A documented value read off a datasheet or vendor spec MAY be recorded with
source `datasheet` or `vendor spec — <which>` (§5) instead of a field
measurement.

---

## 5. Allowed values for the Measurement source column (verbatim)

The Measurement source cell must be exactly one of:

> - `calipers`
> - `tape (ID = C/pi)`
> - `datasheet`
> - `vendor spec — <which>`

(e.g. `vendor spec — Conflat CF flange catalogue`). For UNKNOWN rows the
source cell records `UNKNOWN` and the reason goes in Notes. No other value
is accepted; the method used MUST appear on every row.

**ESTIMATED rule (verbatim):**

> Estimated or eyeballed numbers are forbidden in the Inner diameter
> column; if a value is estimated it goes in a separate ESTIMATED notes
> column, never in the measurement column.

Operationalized: the Notes column is that ESTIMATED notes column — a soft
number is written only there, explicitly labelled `ESTIMATED`, and the
Inner diameter cell for that row stays `UNKNOWN` (with reason) or carries
the properly measured value, never the estimate.

---

## 6. Table columns

The table has exactly these five required columns plus the extra Notes
column:

`ID | Location (photo ref + free-text) | Inner diameter (mm) | Occupied? | Measurement source | Notes`

- **ID** — `P1…Pn` or `G1`.
- **Location (photo ref + free-text)** — both photo filenames plus a
  plain-language location, e.g. `P3_wide.jpg, P3_close.jpg — left bulkhead,
  2 o'clock, above the cable boot`.
- **Inner diameter (mm)** — a measured number, or `UNKNOWN`. Never blank,
  never an estimate.
- **Occupied?** — exactly `empty`, or `used by <cable / conduit / blanking
  plug, with description>`. Vague entries ("yes", "in use") are forbidden.
- **Measurement source** — one of the §5 allowed values (or `UNKNOWN`).
- **Notes** — UNKNOWN reasons, `ESTIMATED` flags, out-of-order insertion
  notes, and any other remark. The ONLY column where an estimate may appear.

Blank tables: `TEMPLATE.md` (markdown) and `template.csv` (CSV), same six
columns, in this directory. Add P rows as penetrations are found — the blank
row count is not a prediction of the penetration count.

---

## 7. Acceptance of a filled table

- One row per penetration found; enumeration includes the documented second
  sweep (§1.4).
- IDs unique and stable, in the documented clockwise-from-hinge order; `G1`
  present and never in the P series; no renumbering (§1.3).
- Every row has an ID, location/photo refs, an occupancy value, and a
  source; no cell left blank.
- Every number in Inner diameter carries one of the allowed §5 sources.
- Every `UNKNOWN` carries a specific reason in Notes; every estimate is
  `ESTIMATED` in Notes only and absent from the measurement column.

---

## Status (nothing fabricated)

This is a rules document: zero penetrations enumerated, zero bores measured,
zero photos taken. No chamber has been located on any record or host (fleet
locate/identify cards resultless; sibling bench reports concur), so the
tables ship blank. When the chamber is named, one site visit executes this
protocol verbatim and the filled rows feed the downstream walk (t_57c1b9fd)
and consolidation (t_ad3aee13).