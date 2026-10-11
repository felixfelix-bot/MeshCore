# PROGRESS — t_e5d5eaae coax routing freeze + tool resolutions

task:  Freeze coax routing and record caliper/tape resolutions, bench
       conditions, and cable IDs (board `meshcore`).
type:  physical bench/field task + short written record.

worktree: /home/c03rad0r/worktrees/t_e5d5eaae
branch:   worker-base/t_e5d5eaae-coax-routing-freeze
base:     c8eb3c8 (repos/meshcore-fork-fix @ main)
push:     bot (felixfelix-bot/MeshCore)

## Blocker found before any writing (finding -> status)

- finding: this card asks for physical work (route/tie a coax bundle, read a
  caliper, read a tape measure, read ambient temperature, read/label cables).
  The assigned host is a headless server with no hands and no metrology.
- status:  VERIFIED, not assumed — measured this run, raw output kept at
  analysis/coax-routing-freeze/evidence/HOST_CAPABILITY.txt:
    * /dev/video0 frame: 307200 bytes captured, YAVG 0.21/255, YMAX 3,
      4 distinct grey levels => sensor sees no scene (lens covered/shuttered).
    * /dev/video1: VIDIOC_G_INPUT "Inappropriate ioctl for device" (metadata
      node, not a camera).
    * no VNA / SDR / power meter / DMM on USB; the only serial ports are three
      Sierra Wireless EM7455 LTE modem AT ports.
    * no operator photos or measurement notes on disk.
    * fleet-wide scan for an existing reading: 182 boards x 8862 task records,
      ZERO carrying a measured caliper/tape value for this run. There is no
      attachment store at all (0 files under ~/hermes-kanban/**/attachments/).
      The only '0.01 mm' strings in the fleet are TOOL REQUIREMENTS written into
      sibling card instructions (t_778c1e09, t_f5f3fe8a), i.e. a spec for what
      the bench should use - not an observation of what it did use.
      (An earlier draft cited '183 boards / 1238 attachments'; that number was
      not reproducible and has been replaced by the counts above.)
- consequence: every physical field in the setup record stays UNSET rather than
  guessed. The deliverable therefore ships as (a) the setup record with a strict
  UNSET-token contract, (b) a reproducible placement procedure + recording
  scheme, (c) a machine gate that refuses to call the setup frozen until each
  acceptance criterion is satisfied, (d) the operator hand-off.

## Log

1. recon of the card family (t_e5d5eaae, t_7a16e421, t_2a16c491, t_48e048a1,
   t_54865987) + sibling deliverable `~/worktrees/coax-bundle-inventory`
   (CAPTURE_PROTOCOL.md, validate_inventory.py) to align ID conventions and
   exit-code contract.
   -> files touched: (none yet)
2. host capability probe written + run; raw output frozen as evidence.
   -> files touched: analysis/coax-routing-freeze/scripts/probe_host_capability.sh,
      analysis/coax-routing-freeze/scripts/frame_luma.py,
      analysis/coax-routing-freeze/evidence/HOST_CAPABILITY.txt
   -> note: first probe run mislabelled a SUCCESSFUL sudo frame grab as
      "SUDO_GRAB_FAIL" (pipeline exit status vs grab exit status). Fixed to test
      the byte count; re-ran. Evidence file is the corrected run.
3. acceptance gate written: 33-field UNSET contract, units-required rule, and
   RECOMPUTED derived values (tape pitch = span/wraps; bend radius =
   chord^2/(8*sagitta) + sagitta/2) so an estimated radius cannot pass as measured.
   -> files touched: analysis/coax-routing-freeze/validate_setup_record.py,
      analysis/coax-routing-freeze/setup_state.json
   -> gate bug found by the tests and fixed in the GATE (not the test): a naive
      substring check credited tape resolution "1 mm" from caliper "0.01 mm";
      replaced with boundary-aware match (?<![\d.])TOKEN(?![\d]).
   -> committed 365c2f7, pushed to bot, remote ref re-read == local HEAD.
4. test suite: 40 tests, one mutant per acceptance criterion. `Ran 40 tests OK`.
   -> files touched: analysis/coax-routing-freeze/test_validate_setup_record.py
5. real CLI differential (in-process is not proof): fully-observed record ->
   COMPLETE (0) + frozen constants; estimated radius -> INVALID (1) with the
   recomputation named; unitless "0.01" -> INVALID (1); shipped template ->
   BLOCKED (2) naming all 33 unset fields.
6. the deliverable written: SETUP_FREEZE_RECORD.md (routing S1-S8 with a
   checkpoint per step, reference frame, tie-point table, tape pitch, loom/jacket,
   chamber-wall bend, caliper/tape resolution, bench conditions, cable IDs,
   mid-documentation change rule) + README.md.
   -> committed f94e288, pushed, remote ref re-read == local HEAD.
   -> corrections while cross-checking the fleet: EM7450->EM7455 (read back from
      evidence); dropped an unreproducible scan claim; cable-identity authority
      t_a288ac99 -> t_c1e285bd; disambiguated measuring tape vs label tape.
7. full report written to REPORT.md at the worktree root; task shipped BLOCKED
   with the bench checklist as REMAINING STEPS (no physical value fabricated).

## Handoff (if I stop here)

setup_state.json + SETUP_FREEZE_RECORD.md are complete except the physical
observations. Next worker: do NOT fill any <<UNSET>> from inference. The
remaining work is 15 numbered steps in REPORT.md section 5, all of which need a
person with a caliper, a tape measure and a thermometer at the bench.
