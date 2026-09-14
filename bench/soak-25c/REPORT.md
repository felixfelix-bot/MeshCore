# Die-temp soak evidence at +25 C — verdict & evidence

Task (fleet card `meshcore:t_3a34bea7`): capture timestamped `calshow`
evidence that a thermally soaked die state (die temp within a ~0.5 C
peak-to-peak band for >=15 consecutive minutes) is reachable at setpoint
+25 C.

Date: 2026-09-14, session 07:38-07:50 local (UTC+2) · Repo: meshcore ·
dispatch run_id `dq05-1789364113` (ownership ledger, this card status
`running`) · artifacts: this directory (`bench/soak-25c/`).

## VERDICT: SOAK UNVERIFIED for +25 C — no soak was started. Zero
## calshow log lines exist; no temperature number is reported as
## observed because none was measured. Nothing was fabricated.

Per the task PRECONDITION, the soak must NOT begin while any gate is
unmet. Both hard gates were checked with fresh tool evidence this
session; BOTH FAIL:

| gate | required | observed (fresh, this session) | met? |
|---|---|---|---|
| A | harness dry-run task completed with calshow reachable and die-temp field parseable | Dry-run card `meshcore:t_da84afb3` ("Validate calshow sampling harness at ambient") completed DURING this session (ownership status `done`, run_id `dq05-1789364476`, commit `ea8b9c8e`, report `bench/dryrun-ambient/REPORT.md`) — but its verdict is **DRY RUN FAIL**: calshow reachable = **NO** (every attempt to open/touch a serial port was denied by the operator; zero bytes of console output exist), die-temp parseable = YES offline only (7/7 SYNTHETIC self-test; never parsed from a real reply). Log file `bench/dryrun-ambient/calshow_ambient.log` DOES NOT EXIST (0 samples). | NO → blocking reason **"no calshow access"** |
| B | parent chamber-stability task reports PASS for +25 C | Holds card `meshcore:t_0e98e408` ("Run chamber 10-min holds at +25/0/-20/-40 C and capture logs") shows ownership status `done` (run_id `dq05-1789357618`) but **no PASS verdict exists anywhere**: no result/status field on the card (meshcore card schema carries none), no matching session in the session DB, no chamber log artifact on disk. The chamber was never located, identified, or commanded: chamber-locate/ID/controller/manual cards (`t_ffc911f6`, `t_a2f7f281`, `t_fbfead68`, `t_a8b9d449`, `t_deaaa866`) all `decision: skip` ("light no-headroom"); the sibling chamber-reservation report (commit `7d9227a1`) independently proves **NO BOOKING EXISTS** and that no chamber is present, located, or commandable on this host. | NO → blocking reason **"parent stability task not PASS"** |

Root cause underneath both gates: **there is no thermal chamber under
this host's control and no sanctioned serial access to the module
console.** USB bus re-enumerated this session (lsusb): 2x QinHeng CH340
serial, Raspberry Pi Debugprobe CMSIS-DAP, RTL8152 Ethernet, BT radio,
audio-HID, microSD reader, hubs — **no chamber controller, no
instrument-class device, no LR2021 module attached** (consistent with
the fork's own bench README: "No agent host in this fleet has the
module attached and none can put a board in a freezer"). Prior bench
dispatches (atcut-fit a9d72654, thermal-lag 9b9fb897, soak-0c d16a2723,
dryrun-ambient ea8b9c8e) independently re-verified the same absence on
2026-09-12/14.

## Required deliverable fields, honestly filled

- SOAK verdict for +25 C: **UNVERIFIED**
- die-temp band observed (C, peak-to-peak): **none — 0 samples exist**
- dwell time (min): **0**
- timestamp range of soaked window: **N/A (no in-band samples; no
  sampling began)**
- dwell budget (>=15-20 min) met: **N/A — sampling never started**
- blocking reasons: **"no calshow access"** (gate A: the dry run
  completed but FAILED — calshow reachable = NO, serial access denied,
  zero console bytes) and **"parent stability task not PASS"** (gate B:
  no PASS verdict for +25 C exists anywhere). Deeper root cause: **no
  chamber access** — no thermal chamber is present, located, or
  commandable on this host, and the DUT is not attached.
- timestamped calshow log lines: **NONE EXIST.** The soak never began,
  so there is nothing to inline or attach. No inferred, extrapolated, or
  placeholder temperature appears anywhere in this report.

## Soak-criterion fields that WOULD have been recorded (left blank — never measured)

    achieved dwell time (min):            _not measured_
    die-temp min (C):                     _not measured_
    die-temp max (C):                     _not measured_
    die-temp peak-to-peak (C):            _not measured_
    in-band window first sample (ISO):    _not measured_
    in-band window last sample (ISO):     _not measured_
    >=15-20 min dwell budget met:         _not measured_

## What was done instead of a soak (all fresh this session)

1. **Hard-gate check BEFORE anything else**, as ordered. The task's
   step 1 ("Command the chamber to +25 C...") was never reached — no
   chamber was commanded, no setpoint was attempted, no serial port was
   opened by this session, no sample loop was started, and no state was
   mutated. This report exists because the precondition gates failed,
   which per the task body means: report UNVERIFIED and stop.
2. **Fleet board + ownership ledger read** (`~/.hermes/bot/fleet_queue_state.json`,
   `~/.hermes/bot/ownership.json`): campaign cards enumerated —
   `t_da84afb3` (dry run, done → FAIL verdict), `t_0e98e408` (10-min
   holds, done with no result), `t_3a34bea7` (+25 C, this card),
   `t_b0a5312a` (0 C, done → UNVERIFIED), `t_35c19845` (-20 C),
   `t_e3bb0dba` (-40 C), `t_6ece027b` (rollup), `t_e80e80cb` (soak
   campaign parent) — none carries a result field; the card schema has
   no result/status keys at all.
3. **Dry-run outcome consumed** (it completed mid-session at 07:46,
   commit `ea8b9c8e`): DRY RUN FAIL — calshow reachable NO (operator
   denied serial touch; zero console bytes), parser proven offline 7/7
   against SYNTHETIC firmware-format strings only. Per the dry-run
   task's own acceptance rule, that means all four soaks are recorded
   UNVERIFIED with blocking reason "no calshow access".
4. **Chamber-stability PASS searched for and not found**: fleet board
   (no result fields), session DB (no stability/holds session), disk
   (no chamber log anywhere; only SYNTHETIC self-test leftovers from
   prior dispatches), chamber-ID cluster (all skipped). Sibling
   chamber-reservation report (commit `7d9227a1`) proves the chamber
   has never been located and NO BOOKING EXISTS — there is no
   parent-proven stable chamber condition to wait for, and the task
   forbids soaking at a setpoint the chamber is not confirmed to hold.
5. **Sibling verdict cross-check**: soak-0c (commit `d16a2723`) reached
   the same UNVERIFIED verdict on the same two gates for 0 C.
6. **Hardware ground truth**: `lsusb` + `/dev/serial` census (above) —
   no chamber controller, no LR2021 board. The `calshow` command itself
   belongs to the felixfelix-bot fork (passive_mapper,
   `MyMesh.cpp:178-181` @ `3fdfbc8e`, clone verified on disk at
   `/tmp/mc-passive`, HEAD 3fdfbc8e this session); mainline MeshCore
   has no cal CLI. Even with serial access, no chamber exists to hold
   +25 C, so gate B would still fail.
7. **Port contention check**: `fuser`/`lsof` on `/dev/ttyUSB0`,
   `/dev/ttyUSB1`, `/dev/ttyACM0` — no holders; ports left untouched by
   this session (zero bytes sent).

## Evidence trail freshness

All file/ledger/board reads above were performed this session
(2026-09-14, 07:38-07:50 local). Sibling reports cited
(dryrun-ambient `ea8b9c8e`, chamber-reservation `7d9227a1`,
soak-0c `d16a2723`) were committed 07:40-07:46 the same morning and
their claims were spot-verified against the live board/ledger/disk
state rather than trusted blindly.

## What unblocks this setpoint (for the operator, not for agents)

1. A thermal chamber must actually exist, be located/identified, be
   confirmed to hold +25 C within tolerance for >=10 min (the parent
   holds card `t_0e98e408` re-run with real logs) — only then does a
   +25 C soak become permissible under this task's own rules.
2. Serial access to the module console must be sanctioned; the
   dry-run harness (`bench/dryrun-ambient/sample_calshow.py`) then
   needs one run of `--samples 3` to prove calshow reachability, after
   which the soak sampling loop can start.
3. The DUT (NiceRF LR2021 module on the fork firmware) must be attached
   and powered for the whole soak window; per the fork's bench README
   this is operator bench work (Felix), not agent work.