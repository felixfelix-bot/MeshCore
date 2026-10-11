# SETUP FREEZE RECORD — RF coax run (cartridge task `t_e5d5eaae`)

**This document is the single record every later coax measurement depends on.**
It freezes the routing, and it fixes the tool resolutions, bench conditions and
cable identifiers that convert a raw reading into a value with an uncertainty.

---

## 0. Status: **NOT FROZEN — awaiting physical observation**

```
$ python3 validate_setup_record.py
VERDICT: BLOCKED (2)
  R2 $: 33 field(s) still unset -> setup is NOT frozen
```

**Every physical value in this record reads `<<UNSET>>`. Nothing here has been
measured, and nothing here may be filled in from inference.** The machine that
prepared this record has no hands, no caliper, no tape measure and no working
camera; that is not an assumption, it is measured in
[`evidence/HOST_CAPABILITY.txt`](evidence/HOST_CAPABILITY.txt):

| Channel that could have observed the bundle | What it actually returned |
|---|---|
| `/dev/video0` (the only camera node) | 307 200-byte frame captured, **YAVG 0.21/255, YMAX 3, 4 distinct grey levels** — the sensor sees no scene |
| `/dev/video1` | `VIDIOC_G_INPUT: Inappropriate ioctl for device` — metadata node, not a camera |
| USB instruments (VNA / SDR / power meter / DMM) | none attached |
| Serial ports | 3× Sierra Wireless EM7455 LTE modem AT ports — not an instrument |
| Operator photos / measurement notes on disk | none |
| Fleet-wide scan for an existing reading | **182** boards × **8 862** task records searched: **zero** carry a measured caliper/tape value for this run. There is no attachment store at all (0 files under `~/hermes-kanban/**/attachments/`), and the only `0.01 mm` strings in the fleet are **tool requirements written into sibling card instructions** (e.g. `t_778c1e09`, `t_f5f3fe8a`: *"Tools: digital caliper (0.01 mm / 0.001 in resolution)"*) — a spec for what the bench *should* use, which is not an observation of what it *did* use. The sibling bundle inventory (`t_c1e285bd`) still reads `STATE: EVIDENCE_PENDING`. |

So the deliverable ships as: **the record and the procedure** (this file), **a
machine-readable half** ([`setup_state.json`](setup_state.json)), and **a gate
that refuses to call the setup frozen until every acceptance criterion is
satisfied** ([`validate_setup_record.py`](validate_setup_record.py), 40 tests).
The physical observations are the one thing left, and they need a person at the
bench. The hand-off is in [`../../REPORT.md`](../../REPORT.md).

**Filling this in:** edit `setup_state.json`, update the matching slot in this
document, then run the gate. The gate names every remaining field with its JSON
path, so the to-do list is mechanical.

---

## 1. Why the routing is frozen *first*

Bundle outer diameter, tape pitch and the tightest forced bend radius are all
properties **of the installed routing**, not of a cable on a bench. Measuring
them on an un-routed bundle produces numbers that describe nothing: re-route the
run and the bundle OD changes, the forced bend moves, and every earlier reading
silently becomes wrong. So:

* Route → tie → loom **exactly** as the run will be installed. Then measure.
* **The routing described below is final.** Per §6, if it later has to change,
  the change is logged and the affected readings are re-taken — the flag exists
  precisely so a stale number cannot sit in the record unnoticed.

**Routing frozen:** `<<UNSET>>` (must end as `true` in `routing.frozen`)

---

## 2. Frozen routing description (§a)

### 2.1 Reference frame — record this *before* any distance

A distance is meaningless without a stated origin and direction. Record all three:

| Field (`setup_state.json`) | Meaning | Value |
|---|---|---|
| `routing.reference_frame` | origin, direction of increasing distance, and the bundle-order convention | `<<UNSET>>` |
| `routing.bundle_entry_point` | the physical place the run leaves/enters (bulkhead port, grommet, door gasket) | `<<UNSET>>` |

Required convention (write it out in your own words, do not just leave the
default): *"arc length measured along the run from `<<origin>>`, increasing
toward `<<direction>>`; bundle order counted `<<left-to-right looking into the
chamber from outside / ...>>`."*

### 2.2 Required placement procedure — ordered steps, each with a checkpoint

Each step must end with a `checkpoint:` clause that a **second person can verify
without seeing your photos**. This is the acceptance criterion for "reproducible
placement", made checkable. Record the filled steps in
`routing.placement_steps` (≥ 6 entries, each containing `checkpoint:`).

| # | Step (fill in the actual anchor / landmark) | Checkpoint a second person verifies |
|---|---|---|
| S1 | Start at `<<UNSET>>` (the DUT connector end). Leave a service loop of `<<UNSET>>` mm before the first anchor. | checkpoint: the loop is present and slack, not a kink |
| S2 | Fit the loom/jacket (`<<UNSET>>`, §2.4) from `<<UNSET>>` to `<<UNSET>>`. | checkpoint: coverage is continuous with no jacket pinched under a tie |
| S3 | Anchor **T0** at `<<UNSET>>` using `<<UNSET>>`, `<<UNSET>>` mm from the reference. | checkpoint: T0 does not crush the jacket; the run cannot slide |
| S4 | Run the bundle toward the chamber wall, anchor **T1** at `<<UNSET>>` (`<<UNSET>>` mm). | checkpoint: the run between T0 and T1 is straight and untwisted |
| S5 | Cross the wall at `<<UNSET>>` (§2.5) — record the crossing hardware. | checkpoint: the crossing point is not compressed and the seal is intact |
| S6 | Continue outside to the instrument, anchor **T2** at `<<UNSET>>` (`<<UNSET>>` mm). | checkpoint: no tension on the instrument connector |
| S7 | Anchor **T3** … every remaining tie point, in order. | checkpoint: ties are at the recorded arc positions, none between them unrecorded |
| S8 | Measure and record the tape pitch (§2.3) and the tightest forced bend (§2.5). | checkpoint: raw span and chord/sagitta are written down before the derived value |

### 2.3 Tie points — every one recorded

`routing.tie_points[]`: `id`, `arc_from_reference_mm` (**number with `mm`**),
`type` (P-clip / lacing cord / adhesive mount / cable tie …), `anchors_to`, plus
anything distinctive in `note`.

```
     DUT                                                      instrument
      |                                                            |
      |   S1 loop                                                  |
      v                                                            v
   [T0]------ straight run ------[T1]  ... wall ...  [T2] --------[T3]
    ^                             ^        ^
    <<UNSET>> mm            <<UNSET>> mm   crossing: <<UNSET>>
   (arc distances measured from the reference frame in §2.1)
```

Tie-point table to fill (these are the identifiers downstream passes will quote):

| id | arc from reference (mm) | type | anchors to | note |
|---|---|---|---|---|
| T0 | `<<UNSET>>` | `<<UNSET>>` | `<<UNSET>>` | `<<UNSET>>` |
| T1 | `<<UNSET>>` | `<<UNSET>>` | `<<UNSET>>` | `<<UNSET>>` |

### 2.4 Loom / jacket — `routing.loom_or_jacket`

`type` (`<<UNSET>>`), `material` (`<<UNSET>>`), `id`/part number
(`<<UNSET>>`), `coverage_pct` (`<<UNSET>>`). "Taped" alone is not reproducible:
name the tape or loom product, its material, and how much of the run it covers.

### 2.5 Tape pitch — measured, never estimated

Tape pitch is the **span of N wraps divided by N**. Measure the span and the
count; the pitch *follows*. Recording a pitch with no span behind it is what the
gate rejects.

* `routing.tape_pitch.wrap_count` — `<<UNSET>>` (use **10** wraps: a 1 mm tape
  then gives a 0.1 mm pitch, ten times better than one wrap)
* `routing.tape_pitch.span_mm` — `<<UNSET>>` (number with `mm`, tape resolution
  is the uncertainty on this span)
* `routing.tape_pitch.derived_pitch_mm` — `<<UNSET>>`, i.e. `span ÷ wraps`

### 2.6 The chamber-wall segment and the tightest forced bend

This is the segment the card singles out, because it is where the run is forced
by the enclosure rather than by choice.

| Field | Meaning | Value |
|---|---|---|
| `chamber_wall_segment.description` | where the run passes near the wall, and how close | `<<UNSET>>` |
| `chamber_wall_segment.crossing` | port / gasket / bulkhead the run actually crosses | `<<UNSET>>` |
| `chamber_wall_segment.clearance_mm` | closest approach to the wall, number with `mm` | `<<UNSET>>` |
| `...bend.method` | must stay `chord_sagitta` | `chord_sagitta` |
| `...bend.chord_mm` | chord across the bend, number with `mm` | `<<UNSET>>` |
| `...bend.sagitta_mm` | offset from chord to curve, number with `mm` | `<<UNSET>>` |
| `...bend.derived_radius_mm` | the radius that follows from the two above | `<<UNSET>>` |

Measure the bend as a **chord and its sagitta** (the standard three-point
method), so the radius is reproducible from the record alone:
`R = chord² / (8 · sagitta) + sagitta / 2`.

> **Illustrative arithmetic only — these are not measurements of this run.**
> chord 60.0 mm, sagitta 5.0 mm → `60²/(8·5) + 5/2` = **92.5 mm**.
> The gate recomputes this from your two raw numbers and rejects a stated radius
> that disagrees with them, which is how an *estimated* radius is caught.

### 2.7 Placement description (§a, prose)

`routing.placement_description` — ≥ 200 characters, `<<UNSET>>`. Written so that
somebody who has never seen your photos can walk up to the bench, follow §2.2 and
place the run identically. Then `placed_by` (`<<UNSET>>`) and `placed_on`
(`<<UNSET>>`).

---

## 3. Caliper — make/model and resolution (§b)

| Field | Value |
|---|---|
| `caliper.make_model` | `<<UNSET>>` |
| `caliper.resolution_mm` | `<<UNSET>>` — **must be a number with the unit `mm`**, e.g. `0.01 mm` |

The resolution is the **least count**: the smallest change the tool can show.
It becomes the **per-measurement uncertainty for every caliper reading
downstream** (§9) — a jacket OD, a connector body OD, a bundle OD. `0.01` on its
own is refused by the gate, because it is ambiguous between mm and inch and this
record exists to remove exactly that ambiguity.

**Required tool spec (from the family's own cards, not from a measurement):** the
sibling cards `t_778c1e09` and `t_f5f3fe8a` specify *"digital caliper (0.01 mm /
0.001 in resolution)"*. So a recorded `caliper.resolution_mm` **coarser than
`0.01 mm` fails the family's requirement** and must be raised with the manager —
either the bench needs a better caliper, or every downstream caliper reading
carries a worse uncertainty than the plan assumes. Record the actual tool's
make/model anyway: the plan's assumption is not evidence of the tool on the
bench.

---

## 4. Tape measure — make/model and resolution (§c)

| Field | Value |
|---|---|
| `tape.make_model` | `<<UNSET>>` |
| `tape.resolution_mm` | `<<UNSET>>` — **number with the unit `mm`**, e.g. `1 mm` |

This becomes the **uncertainty for every length reading** downstream: in-chamber
free length, free length out to the instrument, the tape-pitch span. The gate
will not accept the string `0.01 mm` as evidence of a `1 mm` tape resolution —
those differ (test `test_resolution_match_is_not_a_substring_match`).

**Disambiguation — two different "tapes" appear in this card family, do not
conflate them:**

| "tape" | What it is | Belongs in |
|---|---|---|
| **measuring tape / steel rule** | the length instrument | `tape.make_model`, `tape.resolution_mm` (§4) |
| painter's tape / masking tape + marker | the *labelling* consumable in `t_964d4469` (*"physical tags/labels (tape + marker, or numbered stickers)"*) | §7 cable labels only — never a resolution |

---

## 5. Bench conditions that could bias a reading (§d)

| Field | Allowed values | Value |
|---|---|---|
| `bench.ambient_temp_c` | number with the unit `C` (e.g. `21.5 C`, `-10.0 C`) | `<<UNSET>>` |
| `bench.jacket_state` | `warm_flexible` \| `cold_stiff` \| `ambient` \| `unknown` | `<<UNSET>>` |
| `bench.tension` | `none` \| `light` \| `taut` \| `unknown` | `<<UNSET>>` |
| `bench.notes` | anything else that could bias a reading | `<<UNSET>>` |

Why these three in particular:

* **Temperature** — a cold jacket stiffens; the same routing then forces a larger
  bend radius than it did warm, so the "tightest forced bend" is
  temperature-dependent unless it is stated.
* **Jacket state** — warm/flexible vs cold/stiff changes how tightly the run
  follows the intended path and how much the jacket compresses under a tie.
* **Tension** — a run under tension is not the routing anyone measured slack on,
  and it biases every length and every diameter read near the anchor.

---

## 6. Routing changed mid-documentation? Flag it — `routing.routing_changed_mid_documentation`

Set this to `true` and add one `routing.change_log[]` entry per change
(`when`, `what_changed`, `why`). The gate then **refuses to accept a `true` flag
with an empty log**, because an unlogged move invalidates every reading taken
before it. If the routing never changed, the flag is `false` and no entry is
needed.

> **Current state of this run: no routing has been established at all**, so this
> flag is `false` and the log is empty. The moment the operator moves an anchor
> after taking a reading, that changes.

---

## 7. Cable IDs — the identifiers every later pass must reuse (§e)

`cable_ids[]`: `id`, `label_state` (`pre_existing` \| `newly_applied`),
`applied_on_cable`, `note`.

**Rules:**

1. List **every** cable in the run. An empty list is indistinguishable from "I
   did not look", so the gate treats it as a failure.
2. If a cable is unlabelled, **label it now** and use that exact identifier, so
   that every downstream pass (OD, connector, slack, bend) refers to the
   identical key.
3. Identifiers must match `^[A-Z0-9][A-Z0-9._-]{0,23}$` and be **unique** — the
   natural scheme is `C1…Cn` in bundle order from §2.1.
4. A cable recorded `newly_applied` must be attested as **physically on the
   cable** (`applied_on_cable: true`). The gate refuses a claimed-but-unapplied
   label.

| id | label_state | applied_on_cable | note |
|---|---|---|---|
| `<<UNSET>>` | `<<UNSET>>` | `false` | `<<UNSET>>` |

The authority for **which cables exist** is the sibling card `t_c1e285bd`
("Identify all RF coax cables in the bundle" — currently `blocked`) and its
worktree `/home/c03rad0r/worktrees/coax-bundle-inventory`, whose
`analysis/coax-bundle-inventory/inventory.csv` is still a 33-line template
marked `STATE: EVIDENCE_PENDING`. So **the cable list does not exist yet
anywhere**: reconcile these IDs with that inventory before declaring the setup
frozen, and do not invent part numbers to fill this table.

---

## 8. Verifying this record

```sh
cd analysis/coax-routing-freeze
python3 validate_setup_record.py          # the record
python3 test_validate_setup_record.py     # the gate's own 40 tests
```

| Exit | Verdict | Meaning |
|---|---|---|
| `0` | `COMPLETE` | every acceptance criterion satisfied; frozen constants emitted |
| `1` | `INVALID` | a field is malformed or a derived value contradicts its raw measurement |
| `2` | `BLOCKED` | fields are unset — the setup is not frozen yet (current state) |

On success the gate emits the contract downstream cards consume:

```json
{
 "caliper_uncertainty_mm": <caliper resolution>,
 "tape_uncertainty_mm":    <tape resolution>,
 "cable_ids":              [ ... the identifiers ... ],
 "tightest_forced_bend_radius_mm": <from chord+sagitta>,
 "tape_pitch_mm":          <from span+wraps>,
 "routing_frozen":         true
}
```

---

## 9. What these numbers unlock

| Depends on | Card |
|---|---|
| Per-cable jacket OD + connector body OD, matched to cable ID, ± caliper resolution | `t_7a16e421` (measure coax/connector/bundle OD with calipers) |
| Bundle OD + bundling description, slack, tightest forced bend as a number | `t_54865987` (bundle OD and routing slack/bend radius) |
| Full bundle characterisation, forced bend vs minimum bend spec | `t_2a16c491` |
| Port-vs-bundle mechanical fit through the chamber penetration | `t_48e048a1` |

Because the resolutions and identifiers live here, those cards quote **one**
uncertainty and **one** set of cable names instead of inventing their own — which
is the entire point of freezing the setup first.

---

## 10. Provenance — what is machine-measured and what is not

| Claim | Source |
|---|---|
| Camera sees no scene; no instrument attached; no prior evidence fleet-wide | `evidence/HOST_CAPABILITY.txt`, produced by `scripts/probe_host_capability.sh` (re-runnable, read-only) |
| Frame statistics YAVG 0.21/255, YMAX 3, 4 levels | `scripts/frame_luma.py` over the captured raw frame |
| Gate behaviour (BLOCKED / COMPLETE / INVALID) and 40 tests | `validate_setup_record.py`, `test_validate_setup_record.py` |
| **Every per-cable, per-tool and per-routing number** | **Nobody. `<<UNSET>>` until a person observes it with the tool named in §3–§4.** |
