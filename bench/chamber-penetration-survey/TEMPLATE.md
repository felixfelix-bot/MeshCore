# Chamber penetration survey — blank table template

One row per penetration found. Fill on site following
`bench/chamber-penetration-survey/PROTOCOL.md` (binding sections: §1 ID
scheme and traversal order, §2 tagging, §3 photos, §4 measurement decision
rule, §5 source vocabulary). The blank P-row count below is NOT a
prediction — add rows as penetrations are found; late finds take the next
unused number and are noted as out-of-order insertions (PROTOCOL §1.3).

Columns (exactly the five required plus Notes):

`ID | Location (photo ref + free-text) | Inner diameter (mm) | Occupied? | Measurement source | Notes`

Cell rules:
- **ID** — `P1…Pn` in clockwise-from-hinge traversal order (PROTOCOL §1.2),
  or `G1` for the door gasket pass-through (never in the P series).
- **Location (photo ref + free-text)** — both photo filenames + plain
  language, e.g. `P3_wide.jpg, P3_close.jpg — left bulkhead, 2 o'clock,
  above the cable boot`.
- **Inner diameter (mm)** — a measured number or `UNKNOWN`. Never blank.
  Never an estimate.
- **Occupied?** — exactly `empty` or `used by <description>`. Vague
  entries ("yes", "in use") are forbidden.
- **Measurement source** — exactly one of: `calipers` | `tape (ID = C/pi)` |
  `datasheet` | `vendor spec — <which>`; `UNKNOWN` for unmeasured rows.
  No silent substitution.
- **Notes** — UNKNOWN reasons, `ESTIMATED` flags, out-of-order insertion
  notes, anything else. The ONLY column where an estimate may appear.

| ID | Location (photo ref + free-text) | Inner diameter (mm) | Occupied? | Measurement source | Notes |
|----|----------------------------------|---------------------|-----------|--------------------|-------|
| P1 |  |  |  |  |  |
| P2 |  |  |  |  |  |
| P3 |  |  |  |  |  |
| P4 |  |  |  |  |  |
| P5 |  |  |  |  |  |
| G1 |  |  |  |  |  |

## Example rows (illustrative only — NOT survey data)

| ID | Location (photo ref + free-text) | Inner diameter (mm) | Occupied? | Measurement source | Notes |
|----|----------------------------------|---------------------|-----------|--------------------|-------|
| P1 | P1_wide.jpg, P1_close.jpg — left bulkhead, 1 o'clock, above door hinge | 25.4 | empty | calipers | — |
| P2 | P2_wide.jpg, P2_close.jpg — rear wall, 5 o'clock, cable boot | UNKNOWN | used by 12-way thermocouple loom in potted boot | UNKNOWN | UNKNOWN: loom potted in place, cannot reach bore or circumference without breaking the seal; ESTIMATED ~8 mm bore (NOT a measured value) |
| G1 | G1_wide.jpg, G1_close.jpg — door gasket pass-through, bottom of door | UNKNOWN | used by thermocouple loom through gasket | UNKNOWN | UNKNOWN: gasket sealed; no bore to measure |