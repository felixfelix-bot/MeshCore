# Bundle OD, slack, and forced bend at the routing path — MEASUREMENT-READY / NO-DATA

Card: meshcore `t_93afb6e2` — "Measure bundle OD, slack, and forced bend at the
routing path."
Date: 2026-10-17 (01:4x local, UTC+2). Host: `c03rad0r-DQ05proplus`. Worker: `default`.
Board: meshcore (repo `~/repos/meshcore`, HEAD `7b2cfa3b`, `main`, ahead 69 of `origin/main`).
Workspace: `/home/c03rad0r/worktrees/t_e1408991` (scratch, not a git clone).

tags: no-code, docs, read-only
tier: docs (declared) — this card ships no code and changes no source file; the
deliverable is a written measurement-readiness record plus one stdlib check
script and its verbatim output. The physical measurement it asks for cannot be
performed on this host (see §2) and **no number is invented to fill the gap**.

---

## VERDICT SUMMARY

**No physical measurement was taken, because there is nothing on this host to
measure and no instrument to measure it with.** The routing this card is asked to
characterize — a bundle of coax, its free slack, and the tightest bend the path
forces — is a **procurement/routing plan, not an installed artifact**:

- **No RF coax cable of any type exists** on this host or in any project record.
  The plan calls for two RG316 SMA-m/m assemblies (0.15 m interior, 0.50 m
  exterior), MPN TBD, status MUST-PROCURE (`bench/coax-cable-inventory`,
  `bench/coax-bundle-dimensions`, `bench/connector-adapter-bom` B1/B4).
- **No chamber exists** on any record — re-verified again in this campaign
  (`bench/chamber-feedthrough-fit`, `bench/chamber-rf-feedthrough-list`
  FT-1..FT-5 all `NON-EXISTENT`, `~/reports/chamber-penetration-survey-NEGATIVE-*`).
  There is therefore no "routing path" in physical space, no chamber wall, no
  feedthrough, and **no tightest bend that the path forces**.
- **No caliper and no tape measure exist** on this host or on any record
  (`bench/routing-freeze` §1, §3 — both are MUST-PROCURE).
- **No camera exists** (`/dev/video*`, `/dev/media*` absent; V4L2 absent) — so the
  card's own method for the bend ("trace the inside curve onto paper **or photo**")
  is unavailable in both forms.
- **No DUT is attached** (`/dev/ttyACM*`, `/dev/ttyUSB*` absent; `usb-Raspberry_Pi_
  Debugprobe` not present, `CH340` serial adapters not present in this census).

So the three acceptance quantities — bundle OD, slack summary, forced-bend summary
— are **UNKNOWN with reason** for every field that requires a physical reading.
That is not a gap in the work; it is the correct, sourced answer, and it is the
same answer the four sibling cards in this family reached independently.

**What this card DOES deliver** (all sourced, all reproducible):

1. **A fresh physical census on this host, run this session** (§2), re-confirming
   the absence of cable, chamber, caliper, tape, camera and attached DUT — so the
   NO-DATA verdict is anchored to evidence taken now, not inherited.
2. **A per-quantity answer table** (§3): for each of bundle OD (per-point + mean +
   cross-section shape + cable count), the three slack lengths, and the
   tightest/second-tightest bend radius, the honest value is `UNKNOWN` with the
   single specific reason and the concrete action that would resolve it.
3. **The planning-level numbers that ARE on record**, recomputed and labelled as
   arithmetic rather than measurements (§4): the taped bundle equivalent OD
   (8.82 mm), the slack budget and free margins (45.7 mm interior / 345.7 mm
   exterior), and the swept envelopes at the two candidate bend radii.
4. **The static-vs-dynamic determination for step 4** (§5), answered from the
   frozen routing spec — the forced bend is **STATIC**; the governing spec is the
   static minimum bend radius.
5. **The step-5 second-bend answer, determined rather than guessed** (§5.3): the
   frozen path defines exactly one deliberate bend (B1), so no second bend exists
   to compare against a 20 % window.
6. **The exact capture sheet** (§6) that turns this record into real measurements
   the moment the parts and the chamber exist — every field the card names, with
   its required tool and resolution floor, ready to be filled in.

A future dispatcher must read this as a **NO-DATA census + verified-blocker**
record, not as a completed measurement. Nothing here supersedes a measured value.

---

## 1. What this card asked for, and the acceptance test applied

The card body (verbatim intent) requires:

| # | Card step | Requires a physical reading? |
|---|-----------|------------------------------|
| 1 | Bundle OD: group the coax exactly as routed (same tape/lacing/heat-shrink, same cable order); measure bundle OD with calipers or a tape wrap at 3 points; report each + mean; state cross-section shape (round / oval with both axes / flat ribbon) and cable count | **Yes** — needs cable, tape/heat-shrink, calipers or tape, and a routed bundle |
| 2 | Slack survey: usable free length inside the chamber (last tie-down/exit to connector face) along the centerline; free length outside to the instrument connector; the length tied down / not free | **Yes** — needs the chamber, the routed cable, and a tape measure |
| 3 | Forced bend: identify the tightest bend the path imposes (feedthrough / clamp); measure the cable-centerline bend radius by tracing the inside curve onto paper or photo with a scale, fitting a circle; document the method | **Yes** — needs the physical path and either paper+tracing or a camera |
| 4 | State whether that bend is static (installed, not moving) or dynamic (moves in operation) | **No** — a property of the design/installation intent, answerable from the spec |
| 5 | Repeat for the second-tightest bend if within 20 % of the tightest | **Yes**, conditional on a measured tightest bend |
| 6 | Every number gets a source ("measured with X tool on Y date" or "traced from photo Z"); flag anything unmeasurable as UNKNOWN with what would resolve it | **No** — a metarequirement, applied to every row below |

Applying step 6 as the governing rule: an unmeasurable quantity is recorded as
`UNKNOWN` with the specific reason and the resolution action. **Estimated or
eyeballed numbers are forbidden in the measurement column** — the same rule the
chamber penetration survey protocol fixes verbatim for the sibling campaign
(`~/reports/chamber-penetration-survey-protocol-t_964d4469-2026-10-01.md` §5,
"ESTIMATED rule"; allowed sources `calipers` / `tape (ID = C/pi)` / `datasheet` /
`vendor spec — <which>`). This record obeys that vocabulary.

---

## 2. Fresh physical census (this session, 2026-10-17 ~01:40 local)

Run on this host to anchor the NO-DATA verdict to evidence taken now rather than
inherited from the 2026-09-15 sibling reports.

| Check | Command | Result | Consequence for this card |
|-------|---------|--------|---------------------------|
| USB devices (instrument-class?) | `lsusb` | root hubs; Realtek BT radio `0bda:b850`; Lexar ES4 `21c4:0004`; Zoran USB Audio/HID `0573:1573`. **Zero instrument-class, zero coax-connected** | No RF instrument to terminate, no USB-TMC measuring device |
| USB-TMC / GPIB | `ls /dev/usbtmc*`, `ls /dev/gpib*` | **absent** | No bus-instrument measurement path |
| Serial adapters / DUT | `ls /dev/ttyACM* /dev/ttyUSB*`; `ls /dev/serial/by-id/` | **absent** (device dir not present) | **DUT not attached**; nothing inline to characterize |
| Camera | `ls /dev/video*`, `ls /dev/media*` | **absent** | The card's photo-trace method (§3) is unavailable; no `*_wide.jpg`/`*_close.jpg` can exist |
| Caliper / tape / ruler assets on disk | bounded `find` for `*caliper*`, `*micrometer*`, `*tape-measure*`, `*tapescan*` under `$HOME` | **zero hits** | No measuring instrument on this host |
| Chamber / routed-path photographs | bounded `find` for `*chamber*.jpg|png`, `*_wide.jpg`, `*_close.jpg` under `~/reports`, `~/.hermes/kanban`, `~/repos/meshcore` | **zero hits** | No photograph exists to trace a bend from |
| Photo assets anywhere in kanban | `find ~/.hermes/kanban -iname '*.jpg' -o -name '*.png'` | only 3 unrelated PNGs on board `net4sats-mvp-v2`/`tollgate` (web keyframes) | No survey photo was ever attached to this board |
| Bench ambient proxy | `/sys/class/thermal/thermal_zone0` | read as a **host motherboard proxy only** (not bench air) | Not used as a measurement; recorded for completeness only |

**Census verdict:** this host is a headless Linux server. It has no coax, no
chamber, no caliper, no tape measure, no camera and no attached DUT. Every
quantity in §3 that requires touching or photographing the physical routing is
therefore not merely unmeasured — it is **not measurable here**, and the honest
source cell is `UNKNOWN` (§3), never an estimate.

This agrees with, and independently re-confirms, the standing absence recorded by
the sibling bench reports `coax-bundle-dimensions`, `coax-cable-inventory`,
`routing-freeze`, `chamber-feedthrough-fit`, `cable-feedthrough-failure-modes`,
`rf-feedthrough-bom`, `chamber-rf-feedthroughs`, `chamber-rf-feedthrough-list`,
plus `~/reports/chamber-penetration-survey-NEGATIVE-blocked-t_57c1b9fd-2026-10-01.md`
(itself a NEGATIVE record: "no thermal chamber to walk, no camera, no calipers").

---

## 3. The card's three deliverables — per-quantity answer table

Every row's value is either a sourced number or `UNKNOWN` with one specific
reason and one resolution action. No blank cells, no estimates in a measurement
column.

### 3.1 Bundle OD (card step 1)

| Field | Value | Source / reason |
|-------|-------|-----------------|
| Bundle composition as it will be routed | 2 cables (per plan): C-RF-INT-1 RG316 coax + C-SER-1 USB-C serial, taped side-by-side on the parallel run only; RF (`C-RF-INT-1`/`C-RF-EXT-1`) and serial are never taped together across the feedthrough | `bench/routing-freeze` §2.2 rule 1, §5 (frozen IDs) — **PLAN**, not an observation |
| Number of cables actually in the as-built bundle | **UNKNOWN** | Nothing is assembled; the plan says 2 on the parallel run, but the as-built count is a property of the installed routing (chamber unlocated → no routing). Resolve: count cables at first physical assembly. |
| OD at point 1 along the run (calipers) | **UNKNOWN** | No cable exists; no caliper exists. Source would be `calipers`, floor ±0.01 mm. Resolve: procure C-RF-INT-1/C-SER-1 + caliper, measure at the first tie point T1. |
| OD at point 2 along the run (calipers) | **UNKNOWN** | as above. Resolve: measure mid-run (parallel-run segment). |
| OD at point 3 along the run (calipers) | **UNKNOWN** | as above. Resolve: measure at the last tie point before the crossing. |
| Mean of the 3 readings | **UNKNOWN** | followed automatically once points 1–3 exist; no mean may be published from fewer than the 3 required readings, and never from a single reading (a mean of one is not a measurement of variation). |
| Cross-section shape: round / oval (both axes) / flat ribbon | **UNKNOWN** | Requires the taped bundle in hand. Note the geometry that makes this non-trivial here: two round cables of unequal OD (2.50 + ~4.50 mm) taped side-by-side are **not** round — the cross-section is an oval/lens, so *both* axes would have to be reported, not one OD. Two axes are named in the capture sheet (§6) precisely for this reason. Resolve: caliper both axes at each of the 3 points once assembled. |
| Tape / lacing / heat-shrink actually used | **UNKNOWN** (class only is specified) | `bench/routing-freeze` §2.2 fixes the *class*: anchors at T1/T3 + one per 100 mm parallel run, polyimide or glass-cloth tape; 0.5 mm-wall loom over the parallel run only; no spiral wrap; no zip ties; no tape within 15 mm of the jam nut. Brand and exact pitch of the as-built run: **UNKNOWN** — resolve at assembly. |

**Single-source caveat on the only on-record OD number:** the taped-bundle
equivalent OD of **8.82 mm** is **planning arithmetic**, not a measurement — see
§4.1. It must never be entered in a measurement column.

### 3.2 Slack survey (card step 2)

| Field | Value | Source / reason |
|-------|-------|-----------------|
| Usable free length **inside the chamber** (last tie-down/exit → connector face), along the centerline | **UNKNOWN** | There is no chamber, therefore no interior run, no last tie-down, no connector face. The frozen *plan* is: 15 mm free behind the J1 back-shell → T1 → bend B1 → 50 mm service loop → bulkhead (`bench/routing-freeze` §2.1). The **measured** free length is `(planned length) − (length consumed by the actual routing)`, and the consumption depends on the unlocated chamber's interior geometry. Resolve: locate the chamber, lay the run, measure free length with a 1 mm tape. |
| Free length **outside the chamber** up to the instrument connector | **UNKNOWN** | No chamber, no defined reference-TX position relative to a (non-existent) wall. Frozen plan: 15 mm standoff from the jam nut → T3 → 100 mm exterior loop → REF-TX J1, over a planned 0.50 m assembly. Measure: tape, floor ±1 mm. Resolve: locate chamber + reference TX placement. |
| Length **tied down / not free to move** | **UNKNOWN** | Tie points are defined as *positions* (T1 interior, T3 exterior, +1 anchor per 100 mm parallel run) but no taped length can be measured without an installed cable. Resolve: measure between anchors after assembly. |
| **Budget check that IS on record** (planning arithmetic, NOT a measurement) | interior 104.3 mm minimum vs 150.0 mm planned → **45.7 mm free margin (30 % spare)**; exterior 154.3 mm minimum vs 500.0 mm planned → **345.7 mm free margin (69 % spare)** | Recomputed this session by `routing_measure_check_t_93afb6e2.py` (§4.2); reproduces `bench/routing-freeze` §6 (which reports the interior margin as "46 %" — see the disclosed discrepancy in §7.2). |

Reference for the two loose-number bands the card uses: the **exact** reading is
the tape-measure job (1 mm floor); the **usable free length** is what a tape
measures between the last anchor and the connector face. Neither exists yet.

### 3.3 Forced bend (card steps 3 and 5)

| Field | Value | Source / reason |
|-------|-------|-----------------|
| Location of the tightest bend the path imposes | **UNKNOWN as a physical location** (planned as `B1`) | The card anticipates "typically at the chamber wall feedthrough or cable clamp". The frozen path instead places the *single deliberate* bend **B1 on the interior floor run**, not at the wall: the freeze explicitly keeps "no bend within 15 mm of the bulkhead face" (`bench/routing-freeze` §2.2 rule 4). Which point is physically tightest cannot be known without the installed path. |
| Measured bend radius of the **cable centerline** at that point | **UNKNOWN** | No path exists; no camera and no paper tracing possible. Method that *would* be used (documented per step 6): trace the inside curve onto paper, or photograph it with a scale in frame, then fit a circle and report radius R; source recorded as `traced from photo <ref>` or `paper trace, fitted circle`. |
| Method actually used | **NONE — not performed** | Stated plainly so no downstream reader assumes a trace exists. |
| Second-tightest bend radius (step 5, if within 20 % of tightest) | **UNKNOWN — and NOT DEFINED** | The frozen path specifies exactly one deliberate bend (B1) and requires the exterior drape to carry no bend below R = 25.0 mm anywhere (§2.1 leg 4). No distinct second bend is defined, so there is nothing to compare inside a 20 % window. This is a *determination from the spec*, not a guess — see §5.3. |
| Swept envelope at the two candidate radii (planning arithmetic, for fit-decision use only) | at R = 12.7 mm: swept Ø **27.9 mm**, clearance from port face **13.95 mm**; at R = 25.0 mm: swept Ø **52.5 mm**, clearance **26.25 mm** | Recomputed this session (§4.3); reproduces `fe700201` §2d as carried by `bench/routing-freeze` §6. |

---

## 4. Planning-level numbers on record (recomputed, never measurements)

These are the only numeric outputs available, and each is labelled as arithmetic
over industry-nominal/UNVERIFIED inputs. Recomputed this session by
`routing_measure_check_t_93afb6e2.py` — rerun is **byte-identical** (`diff` clean
against `routing_measure_check_out.txt`).

### 4.1 Bundle OD — planning arithmetic

Two round cables of OD a and b taped side-by-side, plus a 0.5 mm loom wall:

```
sqrt((2.50 + 4.50)^2 + 4.50^2) + 0.50 = 8.82 mm
```

- RG316 OD 2.50 mm — **INDUSTRY-NOMINAL, UNVERIFIED** (`fe700201` §2b; `55585471` §3b).
- USB-C OD 4.50 mm (range 4.0–5.0, mid taken) — **INDUSTRY-TYPICAL, UNVERIFIED**.
- Loom 0.50 mm wall — **[SPEC]** (`bench/routing-freeze` §2.2 rule 3).
- **Published on record as ~8.8 mm**; recomputed here 8.82 mm. It is an
  *equivalent* OD of an oval section, not a caliper reading, and it varies with
  the USB-C OD actually procured (4.0 mm → ~8.3 mm; 5.0 mm → ~9.5 mm).
- **Do not enter this in a measurement column.** The measured bundle OD is
  `UNKNOWN` (§3.1).

### 4.2 Slack — budget check and free margins

| Assembly | Planned length | Frozen minimum budget | Free margin | Spare |
|----------|---------------|-----------------------|-------------|-------|
| C-RF-INT-1 (interior) | 150.0 mm | 15.0 tie-off + 39.3 arc + 50.0 loop = **104.3 mm** | **45.7 mm** | 30 % |
| C-RF-EXT-1 (exterior) | 500.0 mm | 15.0 + 39.3 + 100.0 = **154.3 mm** | **345.7 mm** | 69 % |

The 90° arc length at the frozen bend radius is `(π/2)·25.0 = 39.3 mm`; at the
static minimum radius it is `(π/2)·12.7 = 19.9 mm`. **This is a length budget, not
a slack survey** — the card's "usable free length" is the budget minus the length
the *actual* routing consumes, which needs the chamber.

### 4.3 Forced bend — swept envelope at the two candidate radii

| Radius basis | Value | Swept diameter `2R + t` | Clearance from port face `R + t/2` |
|--------------|-------|-------------------------|-------------------------------------|
| Static minimum (industry-nominal) | 12.7 mm | **27.9 mm** | **13.95 mm** |
| Frozen conservative rule (10×OD) | 25.0 mm | **52.5 mm** | **26.25 mm** |

These are the thresholds a physical fit decision uses once a real bend exists; on
their own they say nothing about whether the installed path *achieves* them, which
is exactly the unmeasured quantity.

---

## 5. Forced-bend classification (card step 4) and the second-bend question (step 5)

### 5.1 Static or dynamic — the determination

The card asks whether the forced bend is **static** (installed, not moving) or
**dynamic** (moves during operation), because that selects which bend spec applies.

**Determination: the forced bend is STATIC.** Basis, all from the frozen routing
spec (`bench/routing-freeze`, card `t_e5d5eaae`), which is on record:

- B1 is a bend in the **interior floor run**, formed **at install time**, confined
  to **one plane**, anchored at tie point T1 (§2.1, §2.3 step 2).
- The path contains **no moving joint and no articulation** — the DUT is a
  stationary board inside a setpoint-held chamber; the reference TX is stationary
  outside (§2.1).
- The freeze **bans tension**: "cables lie slack, loops carry the slack, nothing
  suspends weight" (§4, "Cable under tension?"). Nothing flexes in operation.

**Governing spec once a radius is measured: the STATIC minimum bend radius**
(= 12.7 mm, industry-nominal, UNVERIFIED), **not** a dynamic value. A dynamic
(repeated-flex) minimum bend radius is **UNKNOWN** — it appears in no on-host
source (a 10×OD ≈ 25 mm figure exists only as engineering knowledge, UNVERIFIED,
and the frozen spec adopts 25.0 mm as its conservative rule regardless).

**Explicit limit of this claim:** the classification is a property of the *frozen
design intent*, not of an observed installation. If the as-built routing later
introduces movement at the crossing (e.g. a door that swings, a cable pulled
during access), the classification must be revisited against the installation
record. As specified, nothing moves.

### 5.2 Why this matters for the comparison step

Because the bend is static, the downstream consolidation card (`t_5d69dfb5`) must
compare the measured radius against the **static** limit (12.7 mm industry-nominal,
UNVERIFIED) and may treat the conservative 25.0 mm rule as an additional, stricter
self-imposed gate adopted by the freeze. It must **not** apply a dynamic limit — no
dynamic limit is on record.

### 5.3 Second-tightest bend (step 5, the 20 % window rule)

**Answer: there is no second bend to measure — the frozen path defines exactly one
deliberate bend.** Step 5's conditional ("repeat for the second-tightest bend if it
is within 20 % of the tightest") therefore has no subject: with a single defined
bend, the second-tightest defined bend does not exist, and the 20 % window is not
applicable. Recording it as `UNKNOWN` without saying this would falsely imply a
second bend exists somewhere. When the path is physically laid, any incidental
second bend (e.g. in the exterior drape) that measures inside a 20 % window of B1
must then be measured and reported — that is the trigger, and it is unmeasured now
only because no cable is installed.

---

## 6. Capture sheet — the fields to fill the moment parts + chamber exist

This is the sheet §3 becomes measurable on. Tool floors are from
`bench/routing-freeze` §3 (**caliper least count 0.01 mm; tape least count 1 mm**).

| # | Field | Required tool | Resolution floor | Value now |
|---|-------|---------------|------------------|-----------|
| B1 | Bundle OD, point 1 (at T1) | calipers | ±0.01 mm | UNKNOWN |
| B2 | Bundle OD, point 2 (mid parallel run) | calipers | ±0.01 mm | UNKNOWN |
| B3 | Bundle OD, point 3 (last anchor before crossing) | calipers | ±0.01 mm | UNKNOWN |
| B4 | Bundle OD mean of B1–B3 | (computed) | — | UNKNOWN |
| B5 | Cross-section shape + both oval axes | calipers | ±0.01 mm | UNKNOWN |
| B6 | Cable count in as-built bundle | visual | — | UNKNOWN |
| S1 | Usable free length, inside chamber (centerline) | steel tape | ±1 mm | UNKNOWN |
| S2 | Free length outside, to instrument connector | steel tape | ±1 mm | UNKNOWN |
| S3 | Tied-down (non-free) length | steel tape | ±1 mm | UNKNOWN |
| R1 | Tightest bend: radius of cable centerline | paper trace or photo-with-scale → fitted circle | trace-scale floor | UNKNOWN |
| R2 | Tightest bend: location + method used | note + photo ref | — | UNKNOWN |
| R3 | Second-tightest bend radius (only if within 20 % of R1) | as R1 | trace-scale floor | NOT DEFINED (§5.3) |
| R4 | Static or dynamic (confirm against as-built) | observation | — | STATIC per spec (§5.1) |

Method note to record at R1: "trace the inside curve onto paper (or photograph it
with a scale in frame), fit a circle to the traced arc, report the fitted radius as
R; record the source as `traced from photo <ref>` or `paper trace, fitted circle`."
This is the card's own prescribed method, restated so the field is unambiguous.

---

## 7. Reproduction and verification

### 7.1 Commands run this session

```
# physical census (full output summarised in §2)
lsusb
ls /dev/usbtmc* /dev/gpib* /dev/video* /dev/media* /dev/ttyACM* /dev/ttyUSB* /dev/serial/by-id/
find $HOME -maxdepth 4 -iname '*caliper*' -o -iname '*micrometer*' -o -iname '*tape-measure*'
find ~/reports ~/.hermes/kanban ~/repos/meshcore -name '*_wide.jpg' -o -name '*_close.jpg'

# this card's arithmetic check (stdlib only, byte-identical rerun)
cd /home/c03rad0r/worktrees/t_e1408991
python3 routing_measure_check_t_93afb6e2.py > routing_measure_check_out.txt
python3 routing_measure_check_t_93afb6e2.py > /tmp/rerun.txt && diff routing_measure_check_out.txt /tmp/rerun.txt   # -> identical

# independent reproduction of the sibling freeze's own arithmetic
cd ~/repos/meshcore/bench/routing-freeze
python3 routing_length_check.py > /tmp/reflen.txt && diff output.txt /tmp/reflen.txt   # -> identical
```

Both diff checks returned clean (byte-identical), so every planning number quoted
here is reproducible from a committed script.

### 7.2 Disclosed discrepancy — interior margin reported as two different percentages

`bench/routing-freeze` §6 reports "C-RF-INT-1 length budget … **PASSES (46% margin)**",
while the same arithmetic gives `104.3 / 150.0 = 69.5 %` of plan,
`45.7 / 104.3 = 43.8 %` over the *minimum budget*, and `45.7 / 150.0 = 30.4 %` of
the planned length. Those are three different, defensible readings of "margin":

- **30.4 %** = free margin as a fraction of the **planned length** (what this report
  publishes in §4.2).
- **43.8 %** = free margin as a fraction of the **minimum budget**.
- **46 %** (the freeze's figure) ≈ 45.7 / 104.3 = 43.8 % rounded up, or
  ≈ 160/345-style slip; the freeze does not state its denominator.

**This is a reporting inconsistency in the sibling artifact, disclosed not
silently corrected.** The underlying length numbers agree exactly (104.3 mm budget,
45.7 mm margin); only the percentage's denominator differs. A downstream reader
should quote the **margin in mm** (45.7 mm) and its denominator explicitly, never a
bare percentage. This report uses "30 % of planned length".

### 7.3 What did NOT happen (so no reader over-reads this file)

- No cable was handled, taped, bent, or measured. No caliper, tape or rule was read.
- No chamber was located; no feedthrough, gasket or clamp was measured.
- No photograph, trace or drawing of a physical layout was produced — no camera
  exists on this host.
- No outbound network fetch was attempted (standing constraint on this host);
  no vendor datasheet was retrieved, so every industry value keeps its UNVERIFIED
  label.
- No number was estimated, interpolated or invented to fill an `UNKNOWN` cell.
- The deliverable touches no source file under test: the check script is a
  standalone stdlib analysis in the scratch workspace, and the report is prose.

---

## 8. Open items consolidated, each with the action that closes it

Ordered by what unblocks the most fields (this is the same unblock spine the
sibling cards identified, re-confirmed here):

1. **Locate the physical chamber** (or record that there is none). Closes: S1, S2,
   S3, R1, R2, R3; makes "the routing path" physically meaningful. Owner: the
   chamber-location lane (all locate cards resultless to date).
2. **Procure the two RG316 assemblies** — C-RF-INT-1 (0.15 m) and C-RF-EXT-1
   (0.50 m), MPN TBD (`bench/connector-adapter-bom` B1/B4). Closes: B1–B6, S3, and
   the coarseness of every OD field.
3. **Procure the measuring tools** to spec — digital caliper (0.01 mm least count)
   and ≥1 m steel tape (1 mm graduation). Closes: the ability to take B1–B6, S1–S3,
   R1. Both are MUST-PROCURE today.
4. **Procure or borrow a camera** and execute the card's trace method for R1/R2.
   Closes: R1's method and R2's photo reference.
5. **Obtain the vendor datasheet** with the procured assembly (no outbound fetch
   from this host). Closes: the UNVERIFIED status of RG316 OD 2.50 mm, the static
   12.7 mm bend radius, the connector body length, and the **dynamic** bend radius
   (absent from every record).
6. **After assembly, measure and confirm the V-groove shape assumption.** A
   two-cable bundle of unequal OD is an oval; confirm both axes and the actual
   taped OD rather than carrying the 8.82 mm equivalent-OD arithmetic forward as if
   it were a measurement.

---

## 9. Provenance

| Artifact | Location | Role |
|----------|----------|------|
| This report | `~/reports/routing-path-measurements-t_93afb6e2-2026-10-17.md` (durable); `~/repos/meshcore/bench/routing-measurements/REPORT.md` (board copy) | deliverable |
| Check script | `~/repos/meshcore/bench/routing-measurements/routing_measure_check_t_93afb6e2.py` | reproducible arithmetic (byte-identical rerun) |
| Verbatim output | `~/repos/meshcore/bench/routing-measurements/output.txt` | recorded stdout |
| `bench/coax-bundle-dimensions/REPORT.md` (2026-09-15) | meshcore repo | prior report on the same question; NO-COAX verdict |
| `bench/coax-cable-inventory/REPORT.md` (2026-09-15) | meshcore repo | cable identification; NO-COAX verdict |
| `bench/routing-freeze/REPORT.md` + `routing_length_check.py` (2026-09-15) | meshcore repo | frozen routing spec (B1, T1/T3, loops, IDs, tool floors) |
| `bench/chamber-feedthrough-fit/REPORT.md` (2026-09-14) | meshcore repo | chamber absent; fit-decision thresholds |
| `bench/chamber-rf-feedthrough-list/feedthrough_list.csv` + `FEEDTHROUGH-LIST.md` | meshcore repo | FT-1..FT-5 all `NON-EXISTENT` |
| `bench/cable-feedthrough-failure-modes/REPORT.md` (2026-09-15) | meshcore repo | cold-bend / jacket-stiffening failure modes |
| `~/reports/chamber-penetration-survey-NEGATIVE-blocked-t_57c1b9fd-2026-10-01.md` | reports tree | NEGATIVE: no chamber, no camera, no calipers |
| `~/reports/chamber-penetration-survey-protocol-t_964d4469-2026-10-01.md` | reports tree | UNKNOWN/ESTIMATED rule vocabulary reused here |
| Board HEAD (at authoring) | `~/repos/meshcore` @ `7b2cfa3b` (`main`, ahead 69 of `origin/main`) | repository state when written; a concurrent worker rebased `main` mid-run and this commit was replayed cleanly onto it |
| Landing commit | `e8c1b6df` on `~/repos/meshcore` `main` — adds `bench/routing-measurements/{REPORT.md,routing_measure_check_t_93afb6e2.py,output.txt}` | committed, not pushed (the bench campaign is intentionally unpushed: no push/consolidate card exists for it) |
| Artifact hashes (sha256) | REPORT.md `24db6ea5d91a1617c612d2b2defeae797f480500deb5ce3bfaa501b78f0d76a2`; script `dda8565829a283f04a18ac6128938e3c00df50150c987c6b199f52a9dea14840`; output.txt `8d90a4f725f1d6fdf3caa2922ad1c87eead9bb00399a8dd2e2dd4d920a7bdcc4` | identity of the landed deliverable |

**Board ID cross-reference.** The bench report series refers to its own cards by
the *pre-2026-10 fleet IDs* (`t_e5d5eaae` routing-freeze, `fe700201`, `55585471`,
`t_0d86117f`, `t_48e048a1`, `t_2f5adb53`, `t_03954030`). Those IDs live in the old
fleet index the bench reports cite; they are **not** resolvable as cards on this
board (`~/.hermes/kanban/boards/meshcore/kanban.db`). The mapping between the old
fleet IDs and today's board cards was not re-derived here (it needs the old fleet
state), and is left as a noted open item rather than guessed. What *is* on this
board and confirmed: this card `t_93afb6e2`, its parent `t_2a16c491`, its children
`t_5d69dfb5` (consolidation + bend pass/fail) and the sibling measurement cards,
plus `~/reports/chamber-penetration-survey-*` for `t_964d4469`/`t_57c1b9fd`.

---

## NOTHING FABRICATED

No physical measurement was performed: no cable, caliper, tape, chamber, camera or
attached DUT exists on this host (fresh census, §2). No bundle OD, slack length or
bend radius was invented; each is `UNKNOWN` with its reason and its resolution
action (§3). Every number that *does* appear is either (a) an on-record value
labelled with its source and confidence, or (b) arithmetic over such values,
reproducible byte-identically by `routing_measure_check_t_93afb6e2.py` (§4, §7.1).
The static-vs-dynamic classification (§5.1) is derived from the frozen spec and
labelled as design intent, not observation. The two percentage discrepancies found
in the sibling artifact are disclosed, not silently corrected (§7.2). No outbound
fetch was attempted. No source file under test was modified.
