# REPORT — `t_e5d5eaae` "Freeze routing and record caliper/tape tool resolutions"

**Verdict: `BLOCKED` — honestly, not as a failure of tooling.**
The setup record, the placement procedure and a machine gate that enforces every
acceptance criterion are **written, tested, committed and pushed**. The one thing
that cannot be done from this host is the physical part: nobody here can route a
coax bundle or read a caliper. So the record ships with every physical value
marked `<<UNSET>>`, and a gate that **refuses** to call the setup frozen until a
person fills them in — which is the only correct output for a measurement-setup
task whose measurements do not exist yet.

**Physical work performed by the agent: NONE.** No bundle was routed, no cable
was labelled, no tool was read. Nothing in this repository claims otherwise.

---

## 1. What was delivered

| # | Artifact | Path (worktree `/home/c03rad0r/worktrees/t_e5d5eaae`) |
|---|---|---|
| 1 | **The frozen-setup record** (the deliverable) | `analysis/coax-routing-freeze/SETUP_FREEZE_RECORD.md` |
| 2 | Machine-readable half of the record | `analysis/coax-routing-freeze/setup_state.json` |
| 3 | Acceptance gate (exit 0/1/2) | `analysis/coax-routing-freeze/validate_setup_record.py` |
| 4 | Gate's own tests — **40, all green** | `analysis/coax-routing-freeze/test_validate_setup_record.py` |
| 5 | Host-capability evidence (re-runnable probe) | `analysis/coax-routing-freeze/evidence/HOST_CAPABILITY.txt` + `scripts/probe_host_capability.sh` |
| 6 | Frame statistics (why the camera is not an instrument) | `analysis/coax-routing-freeze/scripts/frame_luma.py` |
| 7 | How to run it | `analysis/coax-routing-freeze/README.md` |
| 8 | Progress log | `PROGRESS.md` |

The record covers exactly what the card asked for: **(a)** frozen routing
(§2 — reference frame, ordered placement steps S1–S8 each with a
second-person-verifiable checkpoint, tie-point table, tape pitch, loom/jacket,
chamber-wall segment and forced bend), **(b)** caliper model + resolution in mm
(§3), **(c)** tape model + resolution in mm (§4), **(d)** bench conditions
(§5 — ambient temperature, jacket state, tension, biasing notes), **(e)** cable
IDs (§7 — scheme, uniqueness, labelling rules).

---

## 2. Why the gate exists (a record is easy to fake, so the gate is the artifact)

A setup record's natural failure mode is not a wrong number — it is **a plausible
number nobody measured**. Three traps are closed mechanically:

1. **Unset is refused.** While any field is unset the gate exits `2 BLOCKED` and
   prints the **full** to-do list with JSON paths (not a truncated preview),
   because each line is a physical observation a human must make.
2. **Bare numbers are refused.** Every measured value must be a **number with
   units** (`"0.01 mm"`); `0.01` alone is ambiguous between mm and inch, and this
   record exists to remove exactly that ambiguity.
3. **Derived values are recomputed.** The gate recomputes
   `tape_pitch = span / wraps` and `bend_radius = chord²/(8·sagitta) + sagitta/2`
   and rejects a record that contradicts its own raw measurements — so an
   *estimated* radius cannot pass as a *measured* one.

The suite found a real bug in the gate, which was fixed in the gate rather than
papered over in the test: a naive substring check credited the tape resolution
`"1 mm"` from the caliper's `"0.01 mm"`. Replaced with a boundary-aware match
(`(?<![\d.])TOKEN(?![\d])`); regression test
`test_resolution_match_is_not_a_substring_match`.

### Real-run proof (driven through the CLI, not in-process)

```
fully observed record     -> exit 0  VERDICT: COMPLETE (0)
                             frozen constants emitted:
                             {caliper_uncertainty_mm: 0.01, tape_uncertainty_mm: 1.0,
                              cable_ids: ["C1","C2"], tape_pitch_mm: 25.0,
                              tightest_forced_bend_radius_mm: 92.5, routing_frozen: true}
radius estimated at 30 mm -> exit 1  R9 ...chord^2/(8*sagitta)+sagitta/2 = 92.500 mm;
                                     a radius that disagrees with its own raw
                                     measurements is rejected
resolution "0.01"         -> exit 1  R3 expected a number with the unit 'mm'
shipped template          -> exit 2  VERDICT: BLOCKED (2), 33 fields unset
```

Gate on the shipped record: `VERDICT: BLOCKED (2)` with all 33 unset fields named.
Suite: `Ran 40 tests ... OK`.

---

## 3. Why BLOCKED is the honest answer — measured, not assumed

From `evidence/HOST_CAPABILITY.txt` (raw probe output kept in the repo):

| Channel that could have observed the bundle | What it actually returned |
|---|---|
| `/dev/video0`, the only camera node | 307 200-byte frame, **YAVG 0.21/255, YMAX 3, 4 grey levels** — the sensor sees no scene |
| `/dev/video1` | `VIDIOC_G_INPUT: Inappropriate ioctl for device` — metadata node |
| USB instruments (VNA / SDR / power meter / DMM) | none attached |
| Serial ports | 3× Sierra Wireless EM7455 LTE modem AT ports |
| Operator photos / measurement notes on disk | none |
| Fleet-wide reading for this run | **182** boards × **8 862** task records searched; **zero** measured caliper/tape values; no attachment store exists |

I also cross-checked the fleet for a shortcut and found one that *looks* like an
answer but is not: sibling card instructions (`t_778c1e09`, `t_f5f3fe8a`) specify
*"digital caliper (0.01 mm / 0.001 in resolution)"*. That is a **requirement for
the tool**, not an observation of the tool on the bench — so it sets a floor in
the record (§3: a coarser caliper fails the family's spec and must be raised with
the manager) **without filling the field**. Deriving `caliper.resolution_mm` from
it would have produced a fabricated measurement wearing a citation.

Likewise the cable list: the identity authority `t_c1e285bd` ("Identify all RF
coax cables in the bundle") is itself `blocked`, and its
`inventory.csv` still reads `STATE: EVIDENCE_PENDING`. **No cable list exists
yet**, which is why §7 says to reconcile rather than to guess part numbers.

---

## 4. Acceptance criteria — status

| Criterion | Status |
|---|---|
| Caliper resolution stated as a number with units (mm) | **Contract enforced & tested**; value `<<UNSET>>` (§3) — gate field `caliper.resolution_mm`, must be `0.01 mm` or finer |
| Tape resolution stated as a number with units (mm) | **Contract enforced & tested**; value `<<UNSET>>` (§4) — gate field `tape.resolution_mm` |
| Routing description reproducible by a second person (tie points, tape pitch, loom/jacket, path near chamber wall) | **Method, ordering, checkpoint-per-step and data slots delivered and gate-checked**; the actual anchors/pitch/loom are `<<UNSET>>` (§2) because no bundle has been routed |
| Bench conditions present | Slots + allowed vocabularies delivered (§5); values `<<UNSET>>` |
| Cable ID list present, newly applied labels physically on the cables | Scheme + uniqueness + `applied_on_cable` attestation delivered (§7); list `<<UNSET>>` — **no cable was labelled** |
| Flag if routing changed mid-documentation | **Not applicable yet: no routing was ever established, so nothing changed.** Flag is `false`, log empty; §6 defines the rule and the gate refuses `true` with an empty log |

---

## 5. REMAINING STEPS (the part that needs a person at the bench)

1. **Route and tie the bundle exactly as it will be installed** — do not measure
   anything before this is final (record §2.2, steps S1–S8).
2. Photograph or sketch the routed path, annotated with every tie point, the tape
   pitch, the loom/jacket, and the segment near the chamber wall.
3. Write the **reference frame** (§2.1): origin, direction of increasing
   distance, bundle-order convention.
4. Read the **caliper**: make/model + resolution as a number with `mm`
   (must be `0.01 mm` or finer; flag a deviation to the manager).
5. Read the **tape measure**: make/model + resolution as a number with `mm`.
6. Record **bench conditions** (§5): ambient temperature (number with `C`),
   jacket state (`warm_flexible`/`cold_stiff`/`ambient`/`unknown`), tension
   (`none`/`light`/`taut`/`unknown`), and any biasing note.
7. Record **every tie point**: id, `arc_from_reference_mm` (number with `mm`),
   type, `anchors_to`, note.
8. Measure **tape pitch** as the span of 10 wraps (number with `mm`); the pitch
   is derived, never estimated.
9. Measure the **chamber-wall bend** as chord + sagitta (numbers with `mm`); the
   radius is derived by the gate.
10. **Label any unlabelled cable now**, then list every cable: id,
    `label_state`, `applied_on_cable`, note.
11. Reconcile those IDs with `t_c1e285bd` / `coax-bundle-inventory/inventory.csv`.
12. Fill `setup_state.json` **and** update the matching slots in
    `SETUP_FREEZE_RECORD.md`.
13. Run `python3 validate_setup_record.py` until it returns `COMPLETE (0)`, then
    `--emit frozen_constants.json` and `python3 test_validate_setup_record.py`.
14. If any tie point moved **after** a reading was taken, set
    `routing.routing_changed_mid_documentation = true` and log the change.
15. Commit and push the filled record so downstream cards quote one uncertainty
    and one set of cable names.

Everything in steps 1–11 requires hands, a caliper, a tape and a thermometric
reading. That is the entire remaining cost of this card.

---

## 6. Verification — fresh run (ad-hoc + canonical suite)

Re-run on the final tree. Two layers, and they are different kinds of evidence:

**(a) Canonical suite** — `test_validate_setup_record.py`, the committed test file:

```
$ python3 test_validate_setup_record.py
Ran 40 tests in 0.341s
OK
```

**(b) Ad-hoc CLI differential** — a throwaway harness (not committed; deleted after
the run) that drives `validate_setup_record.py` as a *subprocess* and asserts the
observed **exit codes**, so the claims below rest on process behaviour rather than
on reading the code. 11/11 checks, 0 failures:

```
  PASS  gate on shipped record exits BLOCKED (2)                    [exit=2]
  PASS  BLOCKED output enumerates the unset fields                [33 named]
  PASS  verdict line is BLOCKED
  PASS  fully-observed record reaches COMPLETE (0)                  [exit=0]
  PASS  COMPLETE emits the downstream constants contract
  PASS  radius that contradicts its own chord+sagitta is INVALID (1) [exit=1]
  PASS  rejection names the recomputation                    [92.5 ... sagitta]
  PASS  resolution without a unit is INVALID (1)                    [exit=1]
  PASS  rejection asks for the unit 'mm'
  PASS  a single unset field re-blocks the record (2)               [exit=2]
  PASS  unit-aware match: '0.01 mm' does not satisfy '1 mm'
AD-HOC RESULT: 0 failure(s)
```

**(c) Static checks** on every changed file: `bash -n` clean on
`probe_host_capability.sh`; `py_compile` clean on all three `.py` files;
`setup_state.json` parses as JSON.

Scope of this evidence: it proves the **gate and record contract** — that the
record cannot be marked frozen while unmeasured, that a value without units is
rejected, and that a radius contradicting its own raw chord+sagitta is rejected.
It proves nothing about the physical setup, because no physical measurement was
taken (see §3, §5).

---

## 7. Ship record — commits and push verification

Branch `worker-base/t_e5d5eaae-coax-routing-freeze` on remote **`bot`**
(`felixfelix-bot/MeshCore`):

| Commit | Content |
|---|---|
| `d5efd9c` | host-capability probe + raw evidence |
| `365c2f7` | acceptance gate + 40 tests (the three traps above) |
| `f94e288` | the frozen-setup record + README + route/fleet corrections |

Both pushes were verified by reading the remote ref back and comparing with
local `HEAD` (not by trusting the push exit code):

```
$ git ls-remote --heads bot refs/heads/worker-base/t_e5d5eaae-coax-routing-freeze
f94e288e221f5095c114d68c1400c5eb41e22d22   <- == local HEAD after milestone 3
```

The report itself is committed in the commit that follows `f94e288`; its SHA is
in `git log` on the branch (`docs(coax-routing-freeze): task report`).

---

## 8. Corrections made while cross-checking (recorded so they are not repeated)

* Modem model `EM7450` → `EM7455` — **read back from the probe evidence**, not
  recalled.
* An unverifiable *"183 boards / 1 238 attachments"* scan claim was replaced by
  the reproducible *"182 boards × 8 862 task records, 0 attachment files"*.
* Cable-identity authority corrected from `t_a288ac99` (a datasheet card) to
  `t_c1e285bd` ("Identify all RF coax cables in the bundle", `blocked`).
* Disambiguated "tape": the **measuring tape** (§4 resolution) vs the painter's
  tape used only for labels in `t_964d4469` — never a resolution.

---

## 9. Hand-off

The record is self-contained: hand `SETUP_FREEZE_RECORD.md` plus a caliper, a
tape measure and a thermometer to the person at the bench; §5 above is their
checklist. When step 13 returns `COMPLETE (0)`, the emitted
`frozen_constants.json` becomes the single source of uncertainty and cable
identity for `t_7a16e421` (per-cable OD), `t_54865987` (bundle OD + slack/bend),
`t_2a16c491` (characterisation) and `t_48e048a1` (port fit).

### Escalation — for the manager or a dispatched card worker

This session is **not** a dispatched kanban worker (no `HERMES_KANBAN_TASK`, and
no `kanban_block`/`kanban_comment` tools), so it cannot itself move the card to
the human-gate state. A session that has those tools should run:

```
kanban_block(kind="capability",
             reason="human-gate: route/tie the coax bundle, then read caliper + tape "
                    "resolutions, bench conditions and cable IDs — see "
                    "analysis/coax-routing-freeze/SETUP_FREEZE_RECORD.md")
kanban_comment(<card t_e5d5eaae>, <raw gate output: VERDICT: BLOCKED (2) + the 33 unset fields>)
```

Do **not** create the `human-gate` shadow card: per the `request-human-action`
skill's own verified pitfall (2026-10-02) that board is archived on this host
(`boards/_archived/human-gate-*`), so the resolver has no DB to read and the
shadow would never be seen. The blocked-capability card is the surface that
appears in the manager's blocked sweeps.

