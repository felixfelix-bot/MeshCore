#!/usr/bin/env python3
"""Acceptance-criteria gate for the frozen coax measurement setup (t_e5d5eaae).

The deliverable is a *setup record*: the frozen routing of the RF coax run plus
the tool resolutions, bench conditions and cable identifiers that every later
measurement depends on. This program is the gate for that record.

It exists because the natural failure mode of such a record is not a wrong
number -- it is a *plausible* number nobody measured. So the gate does three
things a human skim cannot:

  1. refuses to call the setup frozen while any field is still unset
     (an unfilled record exits BLOCKED, never COMPLETE);
  2. requires every measured value to be a NUMBER WITH UNITS ('0.01 mm'),
     because the acceptance criterion is stated that way and a bare '0.01' is
     ambiguous between mm and inches;
  3. RECOMPUTES the two derived quantities from their raw inputs --
     tape pitch from (span over N wraps) and the tightest forced bend radius
     from (chord, sagitta) -- and rejects a record whose stated derived value
     disagrees with its own raw measurements. A radius that was estimated
     rather than measured fails this check.

Exit codes
  0  setup is COMPLETE and satisfies every acceptance criterion
  1  record content is INVALID (a field is malformed or self-inconsistent)
  2  setup is BLOCKED -- fields are unset; nothing physical is established yet

This program never invents data and never fills a field.

Usage
  python3 validate_setup_record.py [setup_state.json] [--record SETUP_FREEZE_RECORD.md]
                                   [--json] [--emit frozen_constants.json]
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

# ------------------------------------------------------------------ contract --
UNSET = "<<UNSET>>"

TOP_LEVEL = [
    "record_id", "task", "physical_work_performed_by_agent",
    "routing", "caliper", "tape", "bench", "cable_ids",
]

# Every routing key the acceptance criterion names explicitly: tie points,
# tape pitch, loom/jacket, and the path near the chamber wall.
ROUTING_KEYS = [
    "frozen", "reference_frame", "bundle_entry_point",
    "placement_description", "placement_steps",
    "tie_points", "tape_pitch", "loom_or_jacket", "chamber_wall_segment",
    "routing_changed_mid_documentation", "change_log",
    "placed_by", "placed_on",
]

JACKET_STATES = ("warm_flexible", "cold_stiff", "ambient", "unknown")
TENSION_STATES = ("none", "light", "taut", "unknown")
LABEL_STATES = ("pre_existing", "newly_applied")

NUM_MM_RE = re.compile(r"^\s*(\d+(?:\.\d+)?)\s*mm\s*$", re.IGNORECASE)
NUM_C_RE = re.compile(r"^\s*(-?\d+(?:\.\d+)?)\s*(?:°|deg(?:rees?)?)?\s*C\s*$", re.IGNORECASE)
CABLE_ID_RE = re.compile(r"^[A-Z0-9][A-Z0-9._-]{0,23}$")

MIN_PLACEMENT_CHARS = 200
MIN_PLACEMENT_STEPS = 6
CHECKPOINT_MARKER = "checkpoint:"
# Rounding tolerance: pitch is an exact derivation, the radius allows the
# operator to have rounded the printed radius to 0.1 mm.
PITCH_REL_TOL = 1e-3
RADIUS_ABS_TOL = 0.5  # mm
RADIUS_REL_TOL = 1e-2

RULE_IDS = {
    "R1": "record parses and carries the canonical top-level keys",
    "R2": "no unset fields remain (setup is actually frozen, not pending)",
    "R3": "caliper make/model present and resolution stated as a number with mm",
    "R4": "tape make/model present and resolution stated as a number with mm",
    "R5": "routing is frozen, has a substantive placement description and provenance",
    "R6": "every tie point has an id, a distance in mm, a type and an anchor",
    "R7": "tape pitch is recomputed from (span over wrap count) and must match",
    "R8": "loom/jacket type, material and coverage are recorded",
    "R9": "chamber-wall segment recorded, with bend radius recomputed from chord+sagitta",
    "R10": "placement is a step-by-step sequence with a checkpoint per step",
    "R11": "a mid-documentation routing change is explicitly logged",
    "R12": "bench conditions recorded (ambient temp, jacket stiffness, tension)",
    "R13": "cable IDs unique, well-formed and their labels' physical state attested",
    "R14": "the record does not claim the agent performed physical work",
    "R15": "markdown record agrees with the machine record and carries no unset token",
    "R16": "cable IDs agree with the sibling bundle inventory when it has rows",
}


class Finding:
    __slots__ = ("rule", "loc", "message")

    def __init__(self, rule: str, loc: str, message: str):
        self.rule, self.loc, self.message = rule, loc, message

    def __str__(self) -> str:
        return f"{self.rule} {self.loc}: {self.message}"


# ------------------------------------------------------------------ helpers --
def is_unset(value) -> bool:
    """True when a leaf still awaits a physical observation."""
    if value is None:
        return True
    if isinstance(value, str) and value.strip() in (UNSET, "", "<UNSET>", "UNSET"):
        return True
    return False


def mm_of(value, f: list[Finding], rule: str, loc: str):
    """Return the mm magnitude of a 'N mm' string, else record a finding."""
    if not isinstance(value, str) or not NUM_MM_RE.match(value or ""):
        f.append(Finding(rule, loc,
                         f"expected a number with the unit 'mm' (e.g. '0.01 mm'), got {value!r}"))
        return None
    return float(NUM_MM_RE.match(value).group(1))


def count_of(value, f: list[Finding], rule: str, loc: str):
    if isinstance(value, bool):
        f.append(Finding(rule, loc, f"expected a count, got a boolean {value!r}"))
        return None
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str) and value.strip().isdigit():
        return float(value.strip())
    f.append(Finding(rule, loc, f"expected an integer count, got {value!r}"))
    return None


def mentions(text: str, token: str) -> bool:
    """True when `token` occurs in `text` as a standalone value.

    Plain substring matching is not sufficient here and the difference is a real
    hole: '1 mm' IS a substring of '0.01 mm', so a written record that stated
    only the caliper's resolution would have silently satisfied the tape's too.
    Require the token not to be flanked by digits or a decimal point.
    """
    return re.search(r"(?<![\d.])" + re.escape(token.strip()) + r"(?![\d])", text) is not None


def walk_unset(node, path="$"):
    """Yield dotted paths of every leaf still marked UNSET."""
    if is_unset(node):
        yield path
    elif isinstance(node, dict):
        for k, v in node.items():
            yield from walk_unset(v, f"{path}.{k}")
    elif isinstance(node, list):
        for i, v in enumerate(node):
            yield from walk_unset(v, f"{path}[{i}]")


def bend_radius_mm(chord_mm: float, sagitta_mm: float) -> float:
    """Circle radius from a chord and its sagitta: R = c^2/(8s) + s/2.

    This is the standard three-point (chord/offset) relation. The record stores
    the two measured numbers, so the radius is reproducible by anyone from the
    record alone -- and recomputable by this gate, which is why an estimated
    radius cannot survive validation.
    """
    return (chord_mm ** 2) / (8.0 * sagitta_mm) + sagitta_mm / 2.0


# ---------------------------------------------------------------- validation --
def validate(state: dict, record_text: str | None) -> tuple[int, list[Finding], dict]:
    f: list[Finding] = []

    for key in TOP_LEVEL:
        if key not in state:
            f.append(Finding("R1", "$", f"missing top-level key {key!r}"))
    if f:
        return 1, f, {}

    # ---- R2: is anything established at all? -----------------------------
    unset = sorted(walk_unset(state))
    if unset:
        shown = ", ".join(unset[:12]) + (" ..." if len(unset) > 12 else "")
        f.append(Finding("R2", "$",
                         f"{len(unset)} field(s) still unset -> setup is NOT frozen: {shown}"))
        return 2, f, {"unset_fields": unset, "unset_count": len(unset)}

    # ---- R14: no false claim of physical work by the agent ---------------
    if state.get("physical_work_performed_by_agent") is not False:
        f.append(Finding("R14", "$.physical_work_performed_by_agent",
                         "must be false: a machine that cannot touch the bundle may not "
                         "claim it performed the physical placement"))

    # ---- R3 / R4: tool resolutions as numbers with units -----------------
    caliper = state.get("caliper") or {}
    tape = state.get("tape") or {}
    if is_unset(caliper.get("make_model")):
        f.append(Finding("R3", "$.caliper.make_model", "caliper make/model not recorded"))
    cal_res = mm_of(caliper.get("resolution_mm"), f, "R3", "$.caliper.resolution_mm")
    if is_unset(tape.get("make_model")):
        f.append(Finding("R4", "$.tape.make_model", "tape make/model not recorded"))
    tape_res = mm_of(tape.get("resolution_mm"), f, "R4", "$.tape.resolution_mm")

    routing = state.get("routing") or {}

    # ---- R5: frozen + substantive description + provenance ---------------
    if routing.get("frozen") is not True:
        f.append(Finding("R5", "$.routing.frozen",
                         "must be true: the router must declare this the final placement"))
    desc = routing.get("placement_description")
    if is_unset(desc) or not isinstance(desc, str) or len(desc.strip()) < MIN_PLACEMENT_CHARS:
        f.append(Finding("R5", "$.routing.placement_description",
                         f"needs >= {MIN_PLACEMENT_CHARS} chars so a second person can "
                         f"reproduce the placement without seeing the photos"))
    for k in ("reference_frame", "bundle_entry_point", "placed_by", "placed_on"):
        if is_unset(routing.get(k)):
            f.append(Finding("R5", f"$.routing.{k}",
                             "required so the placement and its distances are interpretable"))

    # ---- R6: tie points --------------------------------------------------
    ties = routing.get("tie_points")
    if not isinstance(ties, list) or not ties:
        f.append(Finding("R6", "$.routing.tie_points",
                         "at least one tie point is required for a reproducible route"))
    else:
        for i, t in enumerate(ties):
            loc = f"$.routing.tie_points[{i}]"
            if not isinstance(t, dict):
                f.append(Finding("R6", loc, "tie point must be an object"))
                continue
            for k in ("id", "type", "anchors_to"):
                if is_unset(t.get(k)):
                    f.append(Finding("R6", f"{loc}.{k}", "required"))
            mm_of(t.get("arc_from_reference_mm"), f, "R6", f"{loc}.arc_from_reference_mm")

    # ---- R7: tape pitch, recomputed --------------------------------------
    pitch = routing.get("tape_pitch") or {}
    wraps = count_of(pitch.get("wrap_count"), f, "R7", "$.routing.tape_pitch.wrap_count")
    span = mm_of(pitch.get("span_mm"), f, "R7", "$.routing.tape_pitch.span_mm")
    stated_pitch = mm_of(pitch.get("derived_pitch_mm"), f, "R7",
                         "$.routing.tape_pitch.derived_pitch_mm")
    if wraps and span is not None and stated_pitch is not None:
        if wraps <= 0:
            f.append(Finding("R7", "$.routing.tape_pitch.wrap_count", "must be > 0"))
        else:
            expect = span / wraps
            if abs(stated_pitch - expect) > PITCH_REL_TOL * max(1.0, expect):
                f.append(Finding("R7", "$.routing.tape_pitch.derived_pitch_mm",
                                 f"stated {stated_pitch:g} mm but span/wraps = "
                                 f"{span:g}/{wraps:g} = {expect:.4f} mm; record the raw span "
                                 f"and let the pitch follow from it"))

    # ---- R8: loom / jacket ----------------------------------------------
    loom = routing.get("loom_or_jacket") or {}
    for k in ("type", "material"):
        if is_unset(loom.get(k)):
            f.append(Finding("R8", f"$.routing.loom_or_jacket.{k}",
                             "loom/jacket must be named (a bare 'taped' is not reproducible)"))
    cov = count_of(loom.get("coverage_pct"), f, "R8", "$.routing.loom_or_jacket.coverage_pct")
    if cov is not None and not (0 <= cov <= 100):
        f.append(Finding("R8", "$.routing.loom_or_jacket.coverage_pct", "must be within 0..100"))

    # ---- R9: chamber-wall segment + recomputed bend radius ---------------
    wall = routing.get("chamber_wall_segment") or {}
    if is_unset(wall.get("description")):
        f.append(Finding("R9", "$.routing.chamber_wall_segment.description",
                         "the segment passing near the chamber wall must be described"))
    if is_unset(wall.get("crossing")):
        f.append(Finding("R9", "$.routing.chamber_wall_segment.crossing",
                         "state how the run crosses the wall (port / gasket / bulkhead)"))
    mm_of(wall.get("clearance_mm"), f, "R9", "$.routing.chamber_wall_segment.clearance_mm")
    bend = wall.get("bend") or {}
    if bend.get("method") != "chord_sagitta":
        f.append(Finding("R9", "$.routing.chamber_wall_segment.bend.method",
                         "must be 'chord_sagitta' so the radius is reproducible from raw numbers"))
    chord = mm_of(bend.get("chord_mm"), f, "R9", "$.routing.chamber_wall_segment.bend.chord_mm")
    sag = mm_of(bend.get("sagitta_mm"), f, "R9", "$.routing.chamber_wall_segment.bend.sagitta_mm")
    stated_r = mm_of(bend.get("derived_radius_mm"), f, "R9",
                     "$.routing.chamber_wall_segment.bend.derived_radius_mm")
    if chord is not None and sag is not None and stated_r is not None:
        if sag <= 0:
            f.append(Finding("R9", "$.routing.chamber_wall_segment.bend.sagitta_mm",
                             "must be > 0"))
        else:
            expect = bend_radius_mm(chord, sag)
            if abs(stated_r - expect) > max(RADIUS_ABS_TOL, RADIUS_REL_TOL * expect):
                f.append(Finding("R9", "$.routing.chamber_wall_segment.bend.derived_radius_mm",
                                 f"stated {stated_r:g} mm but chord^2/(8*sagitta)+sagitta/2 = "
                                 f"{chord:g}^2/(8*{sag:g})+{sag:g}/2 = {expect:.3f} mm; a radius "
                                 f"that disagrees with its own raw measurements is rejected"))

    # ---- R10: step-by-step placement -------------------------------------
    steps = routing.get("placement_steps")
    if not isinstance(steps, list) or len(steps) < MIN_PLACEMENT_STEPS:
        f.append(Finding("R10", "$.routing.placement_steps",
                         f"needs >= {MIN_PLACEMENT_STEPS} ordered steps"))
    else:
        for i, s in enumerate(steps, 1):
            if not isinstance(s, str) or len(s.strip()) < 20:
                f.append(Finding("R10", f"$.routing.placement_steps[{i-1}]",
                                 "step is too short to be reproducible"))
            elif CHECKPOINT_MARKER not in s.lower():
                f.append(Finding("R10", f"$.routing.placement_steps[{i-1}]",
                                 f"step must end with a '{CHECKPOINT_MARKER}' a second person "
                                 f"can verify"))

    # ---- R11: explicit mid-documentation change --------------------------
    changed = routing.get("routing_changed_mid_documentation")
    log = routing.get("change_log")
    if not isinstance(changed, bool):
        f.append(Finding("R11", "$.routing.routing_changed_mid_documentation",
                         "must be a boolean (true/false)"))
    elif changed:
        if not isinstance(log, list) or not log:
            f.append(Finding("R11", "$.routing.change_log",
                             "routing changed mid-documentation but no entry records what "
                             "changed and why -- earlier readings would silently be stale"))
        else:
            for i, e in enumerate(log):
                for k in ("when", "what_changed", "why"):
                    if is_unset((e or {}).get(k)):
                        f.append(Finding("R11", f"$.routing.change_log[{i}].{k}", "required"))

    # ---- R12: bench conditions -------------------------------------------
    bench = state.get("bench") or {}
    temp = bench.get("ambient_temp_c")
    if not isinstance(temp, str) or not NUM_C_RE.match(temp or ""):
        f.append(Finding("R12", "$.bench.ambient_temp_c",
                         f"ambient temperature must be a number with the unit 'C' "
                         f"(e.g. '21.5 C'), got {temp!r}"))
    if bench.get("jacket_state") not in JACKET_STATES:
        f.append(Finding("R12", "$.bench.jacket_state",
                         f"must be one of {JACKET_STATES}; a cold/stiff jacket forces a "
                         f"larger bend than a warm/flexible one, so this biases every reading"))
    if bench.get("tension") not in TENSION_STATES:
        f.append(Finding("R12", "$.bench.tension", f"must be one of {TENSION_STATES}"))
    if is_unset(bench.get("notes")):
        f.append(Finding("R12", "$.bench.notes",
                         "record anything else that could bias a reading"))

    # ---- R13: cable IDs ---------------------------------------------------
    cables = state.get("cable_ids")
    ids: list[str] = []
    if not isinstance(cables, list) or not cables:
        f.append(Finding("R13", "$.cable_ids",
                         "the run must list every cable; an empty list cannot be told apart "
                         "from 'I did not look'"))
    else:
        for i, c in enumerate(cables):
            loc = f"$.cable_ids[{i}]"
            if not isinstance(c, dict):
                f.append(Finding("R13", loc, "cable entry must be an object"))
                continue
            cid = c.get("id")
            if not isinstance(cid, str) or not CABLE_ID_RE.match(cid):
                f.append(Finding("R13", f"{loc}.id",
                                 f"identifier must match {CABLE_ID_RE.pattern} so every "
                                 f"downstream pass refers to the identical key, got {cid!r}"))
            else:
                ids.append(cid)
            state_label = c.get("label_state")
            if state_label not in LABEL_STATES:
                f.append(Finding("R13", f"{loc}.label_state", f"must be one of {LABEL_STATES}"))
            elif state_label == "newly_applied" and c.get("applied_on_cable") is not True:
                f.append(Finding("R13", f"{loc}.applied_on_cable",
                                 "a label recorded as newly applied must be attested as "
                                 "physically on the cable (applied_on_cable: true)"))
        dupes = sorted({x for x in ids if ids.count(x) > 1})
        if dupes:
            f.append(Finding("R13", "$.cable_ids",
                             f"duplicate identifiers {dupes}: two cables sharing a key cannot "
                             f"be referred to unambiguously downstream"))

    # ---- R16: agreement with the sibling inventory -----------------------
    inv = Path(__file__).resolve().parent.parent / "coax-bundle-inventory" / "inventory.csv"
    if inv.exists():
        rows = [ln for ln in inv.read_text(errors="replace").splitlines()
                if ln.strip() and not ln.lstrip().startswith("#")]
        if len(rows) > 1:
            f.append(Finding("R16", str(inv.name),
                             f"inventory has {len(rows) - 1} data row(s); reconcile the cable "
                             f"IDs here with its bundle_position values before calling the "
                             f"setup frozen"))

    # ---- R15: the markdown record must agree -----------------------------
    if record_text is None:
        f.append(Finding("R15", "SETUP_FREEZE_RECORD.md", "record file not supplied"))
    else:
        if UNSET in record_text:
            f.append(Finding("R15", "SETUP_FREEZE_RECORD.md",
                             f"the human-readable record still carries the {UNSET} token"))
        for name, val in (("caliper", caliper.get("resolution_mm")),
                          ("tape", tape.get("resolution_mm"))):
            if isinstance(val, str) and val.strip() and not mentions(record_text, val):
                f.append(Finding("R15", "SETUP_FREEZE_RECORD.md",
                                 f"{name} resolution {val!r} appears in the machine record but "
                                 f"not in the written record"))

    code = 1 if f else 0
    constants = {}
    if code == 0:
        constants = {
            # The contract downstream cards consume. Resolution IS the
            # per-measurement uncertainty: that is the whole point of freezing it.
            "record_id": state.get("record_id"),
            "caliper_uncertainty_mm": float(NUM_MM_RE.match(caliper["resolution_mm"]).group(1)),
            "tape_uncertainty_mm": float(NUM_MM_RE.match(tape["resolution_mm"]).group(1)),
            "cable_ids": ids,
            "tightest_forced_bend_radius_mm": float(
                NUM_MM_RE.match(routing["chamber_wall_segment"]["bend"]["derived_radius_mm"]).group(1)),
            "tape_pitch_mm": float(
                NUM_MM_RE.match(routing["tape_pitch"]["derived_pitch_mm"]).group(1)),
            "routing_frozen": True,
        }
    return code, f, constants


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("state", nargs="?", default="setup_state.json")
    ap.add_argument("--record", default="SETUP_FREEZE_RECORD.md")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--emit", default=None,
                    help="write the frozen constants JSON here when COMPLETE")
    args = ap.parse_args(argv)

    state_path = Path(args.state)
    if not state_path.exists():
        print(f"VERDICT: BLOCKED (2) -- {state_path} not found")
        return 2
    try:
        state = json.loads(state_path.read_text())
    except json.JSONDecodeError as exc:
        print(f"VERDICT: INVALID (1) -- {state_path} is not valid JSON: {exc}")
        return 1

    record_path = Path(args.record)
    record_text = record_path.read_text() if record_path.exists() else None

    code, findings, constants = validate(state, record_text)
    verdict = {0: "COMPLETE", 1: "INVALID", 2: "BLOCKED"}[code]

    if args.json:
        print(json.dumps({
            "verdict": verdict, "exit": code,
            "findings": [{"rule": x.rule, "loc": x.loc, "message": x.message}
                         for x in findings],
            "frozen_constants": constants,
        }, indent=1))
    else:
        print(f"record: {state_path}  written record: {record_path}"
              f"{'' if record_text is not None else ' (absent)'}")
        print()
        for x in findings:
            print(f"  {x}")
        if code == 2:
            # The unset list is the operator's to-do list: print all of it, not
            # a truncated preview, because each line is a physical observation
            # somebody has to go and make.
            unset = constants.get("unset_fields", [])
            print()
            print(f"  --- {len(unset)} field(s) awaiting a physical observation ---")
            for path in unset:
                print(f"  unset {path}")
        if not findings:
            print("  every acceptance criterion satisfied")
            for k, v in constants.items():
                print(f"  frozen {k} = {v}")
        print()
        print(f"VERDICT: {verdict} ({code})")

    if code == 0 and args.emit:
        Path(args.emit).write_text(json.dumps(constants, indent=1) + "\n")
        print(f"frozen constants written to {args.emit}")
    return code


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
