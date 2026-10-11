#!/usr/bin/env python3
"""Tests for the frozen-setup acceptance gate (validate_setup_record.py).

Two claims are being proven, and they are different claims:

  * the shipped template is BLOCKED, not COMPLETE -- i.e. the gate cannot be
    satisfied by a record nobody measured; and
  * every acceptance criterion the card states is actually ENFORCED -- proven by
    a mutant per criterion, each mutant differing from the passing fixture in
    exactly one field, so a passing test cannot be credited to another rule.

Run:  python3 test_validate_setup_record.py
"""
from __future__ import annotations

import copy
import importlib.util
import json
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
TEMPLATE = HERE / "setup_state.json"

_spec = importlib.util.spec_from_file_location("vsr", HERE / "validate_setup_record.py")
V = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(V)

UNSET = V.UNSET


def load_template() -> dict:
    return json.loads(TEMPLATE.read_text())


def fixture() -> dict:
    """A fully-observed setup: every field carries a value a person could have
    written down at the bench. Raw numbers are chosen so the derived values are
    exactly reproducible (pitch 250/10 = 25.0; radius for c=60, s=5 -> 92.5)."""
    s = load_template()
    s.pop("_readme", None)
    r = s["routing"]
    r["frozen"] = True
    r["reference_frame"] = (
        "arc length measured along the run from the bulkhead face, increasing outward "
        "toward the instrument; bundle order counted left-to-right looking into the chamber"
    )
    r["bundle_entry_point"] = "SMA bulkhead feedthrough, lower-right chamber-wall port"
    r["placement_description"] = (
        "The bundle leaves the DUT on the sled, runs 180 mm along the sled lip to the "
        "first P-clip, turns toward the chamber wall and passes 8 mm clear of it before "
        "crossing the lower-right bulkhead feedthrough, then continues to the instrument."
    )
    r["placement_steps"] = [
        f"Step {i}: place and verify anchor {i} before moving on. checkpoint: "
        f"tie T{i-1} is tight against its mount and does not pinch the jacket."
        for i in range(1, 8)
    ]
    r["tie_points"] = [
        {"id": "T0", "arc_from_reference_mm": "0.0 mm", "type": "P-clip",
         "anchors_to": "chamber frame rail", "note": "first anchor at the wall"},
        {"id": "T1", "arc_from_reference_mm": "120.0 mm", "type": "adhesive mount",
         "anchors_to": "sled lid edge", "note": "start of the take-up loop"},
    ]
    r["tape_pitch"] = {"method": "span_over_wrap_count", "wrap_count": 10,
                       "span_mm": "250.0 mm", "derived_pitch_mm": "25.0 mm"}
    r["loom_or_jacket"] = {"type": "spiral wrap", "material": "PTFE",
                           "id": "LOOM-A", "coverage_pct": 60}
    r["chamber_wall_segment"] = {
        "description": "the run passes within 8 mm of the chamber wall between T0 and T1",
        "crossing": "bulkhead SMA feedthrough port 2",
        "clearance_mm": "8.0 mm",
        "bend": {"method": "chord_sagitta", "chord_mm": "60.0 mm",
                 "sagitta_mm": "5.0 mm", "derived_radius_mm": "92.5 mm"},
    }
    r["routing_changed_mid_documentation"] = False
    r["change_log"] = []
    r["placed_by"] = "operator initials and date line in the bench log"
    r["placed_on"] = "2026-10-11"
    s["caliper"] = {"make_model": "Mitutoyo 500-196-30 digital", "resolution_mm": "0.01 mm"}
    s["tape"] = {"make_model": "Stanley PowerLock 5 m", "resolution_mm": "1 mm"}
    s["bench"] = {"ambient_temp_c": "21.5 C", "jacket_state": "ambient",
                  "tension": "none", "notes": "bench at rest, no load on the run"}
    s["cable_ids"] = [
        {"id": "C1", "label_state": "pre_existing", "applied_on_cable": False,
         "note": "legend printed on jacket"},
        {"id": "C2", "label_state": "newly_applied", "applied_on_cable": True,
         "note": "heatshrink applied this session"},
    ]
    return s


def record_text_for(state: dict) -> str:
    return ("# setup record\n"
            f"caliper resolution: {state['caliper']['resolution_mm']}\n"
            f"tape resolution: {state['tape']['resolution_mm']}\n")


class GateTests(unittest.TestCase):
    def check(self, state, code, record="auto"):
        text = record_text_for(state) if record == "auto" else record
        got, findings, constants = V.validate(state, text)
        msgs = " | ".join(str(x) for x in findings)
        self.assertEqual(got, code, f"expected exit {code}, got {got}: {msgs}")
        return findings, constants

    def mutant(self, **changes):
        """Fixture with one changed field; key 'path' is 'a.b.c' dotted."""
        s = copy.deepcopy(FIXTURE)
        for path, value in changes.items():
            node = s
            parts = path.split("__")
            for p in parts[:-1]:
                node = node[p]
            node[parts[-1]] = value
        return s

    # ---------------------------------------------------------------- template
    def test_shipped_template_is_blocked_not_complete(self):
        findings, constants = self.check(load_template(), 2)
        self.assertTrue(any(x.rule == "R2" for x in findings))
        unset = constants["unset_fields"]
        # The unset list IS the operator's to-do list, so it must be complete.
        self.assertGreater(len(unset), 20)
        for must in ("$.caliper.resolution_mm", "$.tape.resolution_mm",
                     "$.bench.ambient_temp_c", "$.routing.chamber_wall_segment.bend.chord_mm"):
            self.assertIn(must, unset, "the blocked report must name this field")

    def test_template_contains_no_invented_measurement(self):
        """Nothing numeric may ship pre-filled: every leaf is UNSET or structural."""
        allowed = {UNSET, False, "T0", "span_over_wrap_count", "chord_sagitta"}
        leaves = []

        def walk(node):
            if isinstance(node, dict):
                for k, v in node.items():
                    if not k.startswith("_"):
                        walk(v)
            elif isinstance(node, list):
                for v in node:
                    walk(v)
            else:
                leaves.append(node)

        for key in ("routing", "caliper", "tape", "bench", "cable_ids"):
            walk(load_template()[key])
        self.assertTrue(leaves)
        for leaf in leaves:
            self.assertIn(leaf, allowed, f"template ships a value that was not observed: {leaf!r}")

    def test_template_matches_the_gates_contract(self):
        t = load_template()
        self.assertEqual(set(t) - {"_readme"}, set(V.TOP_LEVEL))
        self.assertEqual(set(t["routing"]), set(V.ROUTING_KEYS))

    # ---------------------------------------------------------------- complete
    def test_complete_record_passes(self):
        self.check(FIXTURE, 0)

    def test_constants_cascade_resolution_to_uncertainty(self):
        _, constants = self.check(FIXTURE, 0)
        self.assertEqual(constants["caliper_uncertainty_mm"], 0.01)
        self.assertEqual(constants["tape_uncertainty_mm"], 1.0)
        self.assertEqual(constants["cable_ids"], ["C1", "C2"])
        self.assertEqual(constants["tightest_forced_bend_radius_mm"], 92.5)
        self.assertEqual(constants["tape_pitch_mm"], 25.0)
        self.assertTrue(constants["routing_frozen"])

    def test_missing_top_level_key_is_invalid(self):
        s = copy.deepcopy(FIXTURE)
        del s["tape"]
        self.check(s, 1, record="# record\ncaliper resolution: 0.01 mm\ntape resolution: 1 mm\n")

    def test_resolution_match_is_not_a_substring_match(self):
        """Regression for a real hole this suite found: '1 mm' is a substring of
        '0.01 mm', so a naive check credited the tape resolution from the
        caliper's number."""
        self.assertTrue(V.mentions("caliper resolution: 0.01 mm", "0.01 mm"))
        self.assertFalse(V.mentions("caliper resolution: 0.01 mm", "1 mm"))
        self.assertTrue(V.mentions("tape resolution: 1 mm", "1 mm"))
        self.assertFalse(V.mentions("tape resolution: 0.5 mm", "1 mm"))

    # ---------------------------------------------------- tool resolution units
    def test_caliper_resolution_without_unit_rejected(self):
        self.check(self.mutant(caliper__resolution_mm="0.02"), 1)

    def test_caliper_resolution_in_centimetres_rejected(self):
        self.check(self.mutant(caliper__resolution_mm="0.002 cm"), 1)

    def test_caliper_resolution_in_micrometres_rejected(self):
        self.check(self.mutant(caliper__resolution_mm="20 um"), 1)

    def test_tape_resolution_without_unit_rejected(self):
        self.check(self.mutant(tape__resolution_mm="1"), 1)

    def test_caliper_model_still_blocked_until_observed(self):
        self.check(self.mutant(caliper__make_model=UNSET), 2)

    # ------------------------------------------------------------ tape pitch
    def test_pitch_must_equal_span_over_wrap_count(self):
        self.check(self.mutant(routing__tape_pitch={"method": "span_over_wrap_count",
                                                    "wrap_count": 10,
                                                    "span_mm": "250.0 mm",
                                                    "derived_pitch_mm": "30.0 mm"}), 1)

    def test_pitch_derived_from_other_wrap_count_passes(self):
        self.check(self.mutant(routing__tape_pitch={"method": "span_over_wrap_count",
                                                    "wrap_count": 5,
                                                    "span_mm": "250.0 mm",
                                                    "derived_pitch_mm": "50.0 mm"}), 0)

    # ------------------------------------------------------------ bend radius
    def test_bend_radius_formula_is_the_standard_chord_relation(self):
        # independent of the implementation's own arithmetic
        self.assertAlmostEqual(V.bend_radius_mm(60.0, 5.0), 3600 / 40 + 2.5, places=9)

    def test_estimated_bend_radius_rejected(self):
        self.check(self.mutant(routing__chamber_wall_segment={
            "description": "passes near the wall", "crossing": "feedthrough port 2",
            "clearance_mm": "8.0 mm",
            "bend": {"method": "chord_sagitta", "chord_mm": "60.0 mm",
                     "sagitta_mm": "5.0 mm", "derived_radius_mm": "30.0 mm"}}), 1)

    def test_radius_that_contradicts_a_changed_chord_rejected(self):
        """The raw inputs and the derived value are bound together."""
        self.check(self.mutant(routing__chamber_wall_segment={
            "description": "passes near the wall", "crossing": "feedthrough port 2",
            "clearance_mm": "8.0 mm",
            "bend": {"method": "chord_sagitta", "chord_mm": "61.0 mm",
                     "sagitta_mm": "5.0 mm", "derived_radius_mm": "92.5 mm"}}), 1)

    def test_zero_sagitta_rejected(self):
        self.check(self.mutant(routing__chamber_wall_segment={
            "description": "passes near the wall", "crossing": "feedthrough port 2",
            "clearance_mm": "8.0 mm",
            "bend": {"method": "chord_sagitta", "chord_mm": "60.0 mm",
                     "sagitta_mm": "0.0 mm", "derived_radius_mm": "92.5 mm"}}), 1)

    def test_bend_measured_by_ruler_rejected(self):
        self.check(self.mutant(routing__chamber_wall_segment={
            "description": "passes near the wall", "crossing": "feedthrough port 2",
            "clearance_mm": "8.0 mm",
            "bend": {"method": "ruler", "chord_mm": "60.0 mm",
                     "sagitta_mm": "5.0 mm", "derived_radius_mm": "92.5 mm"}}), 1)

    def test_wall_clearance_without_unit_rejected(self):
        seg = copy.deepcopy(FIXTURE["routing"]["chamber_wall_segment"])
        seg["clearance_mm"] = "8"
        self.check(self.mutant(routing__chamber_wall_segment=seg), 1)

    # ------------------------------------------------------------- routing shape
    def test_unfrozen_routing_rejected(self):
        self.check(self.mutant(routing__frozen=False), 1)

    def test_no_tie_points_rejected(self):
        self.check(self.mutant(routing__tie_points=[]), 1)

    def test_loom_material_missing_is_blocked(self):
        loom = dict(FIXTURE["routing"]["loom_or_jacket"], material=UNSET)
        self.check(self.mutant(routing__loom_or_jacket=loom), 2)

    def test_too_few_placement_steps_rejected(self):
        self.check(self.mutant(routing__placement_steps=FIXTURE["routing"]["placement_steps"][:5]), 1)

    def test_step_without_a_checkpoint_rejected(self):
        steps = list(FIXTURE["routing"]["placement_steps"])
        steps[2] = "Step 3: put the third tie somewhere along the run, roughly where it looks right"
        self.check(self.mutant(routing__placement_steps=steps), 1)

    # ------------------------------------------------------- mid-doc change flag
    def test_unlogged_routing_change_rejected(self):
        self.check(self.mutant(routing__routing_changed_mid_documentation=True,
                               routing__change_log=[]), 1)

    def test_logged_routing_change_is_accepted_and_flagged(self):
        self.check(self.mutant(routing__routing_changed_mid_documentation=True,
                               routing__change_log=[{"when": "2026-10-11 09:40Z",
                                                     "what_changed": "T1 moved 15 mm outboard",
                                                     "why": "original site pinched the jacket"}]), 0)

    def test_partial_change_log_entry_rejected(self):
        self.check(self.mutant(routing__routing_changed_mid_documentation=True,
                               routing__change_log=[{"when": "2026-10-11 09:40Z",
                                                     "what_changed": "T1 moved",
                                                     "why": UNSET}]), 2)

    # ------------------------------------------------------------ bench
    def test_ambient_temp_in_fahrenheit_rejected(self):
        bench = dict(FIXTURE["bench"], ambient_temp_c="70 F")
        self.check(self.mutant(bench=bench), 1)

    def test_unrecognised_jacket_state_rejected(self):
        bench = dict(FIXTURE["bench"], jacket_state="cold")
        self.check(self.mutant(bench=bench), 1)

    def test_cold_stiff_jacket_is_a_legal_observation(self):
        bench = dict(FIXTURE["bench"], jacket_state="cold_stiff", tension="light",
                     ambient_temp_c="-10.0 C")
        self.check(self.mutant(bench=bench), 0)

    # ------------------------------------------------------------ cable IDs
    def test_duplicate_cable_ids_rejected(self):
        cables = copy.deepcopy(FIXTURE["cable_ids"])
        cables[1]["id"] = "C1"
        self.check(self.mutant(cable_ids=cables), 1)

    def test_new_label_without_physical_attestation_rejected(self):
        cables = copy.deepcopy(FIXTURE["cable_ids"])
        cables[1]["applied_on_cable"] = False
        self.check(self.mutant(cable_ids=cables), 1)

    def test_unlabelled_cable_id_rejected(self):
        cables = copy.deepcopy(FIXTURE["cable_ids"])
        cables[0]["id"] = "the one with the red tie"
        self.check(self.mutant(cable_ids=cables), 1)

    # ------------------------------------------------------------ no false claim
    def test_agent_may_not_claim_it_did_the_physical_work(self):
        self.check(self.mutant(physical_work_performed_by_agent=True), 1)

    # ------------------------------------------------------------ record agreement
    def test_written_record_holding_unset_token_rejected(self):
        self.check(FIXTURE, 1, record="# record\ncaliper resolution: 0.01 mm\n"
                                     "tape resolution: 1 mm\nroute: <<UNSET>>\n")

    def test_written_record_missing_a_resolution_rejected(self):
        self.check(FIXTURE, 1, record="# record\ncaliper resolution: 0.01 mm\n")

    def test_written_record_absent_rejected(self):
        findings, _ = self.check(FIXTURE, 1, record=None)
        self.assertTrue(any(x.rule == "R15" for x in findings))

    # ------------------------------------------------------------ CLI surface
    def test_cli_exits_two_on_the_shipped_template(self):
        import subprocess
        import sys
        r = subprocess.run([sys.executable, str(HERE / "validate_setup_record.py"),
                            str(TEMPLATE)], capture_output=True, text=True, cwd=HERE)
        self.assertEqual(r.returncode, 2, r.stdout + r.stderr)
        self.assertIn("VERDICT: BLOCKED", r.stdout)

    def test_cli_json_shape(self):
        import subprocess
        import sys
        r = subprocess.run([sys.executable, str(HERE / "validate_setup_record.py"),
                            str(TEMPLATE), "--json"],
                           capture_output=True, text=True, cwd=HERE)
        payload = json.loads(r.stdout)
        self.assertEqual(payload["verdict"], "BLOCKED")
        self.assertEqual(payload["exit"], 2)
        self.assertIn("unset_fields", payload["frozen_constants"] or {})


FIXTURE = fixture()

if __name__ == "__main__":
    unittest.main(verbosity=2)
