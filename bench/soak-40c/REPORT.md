# Die-temp soak evidence at -40 C — verdict & evidence

Task (fleet card `meshcore:t_e3bb0dba`): capture timestamped `calshow`
evidence that a thermally soaked die state (die temp stable within a
~0.5 C peak-to-peak band for >=15 consecutive minutes) is reachable at
setpoint -40 C.

Date: 2026-09-14, session 08:09-08:15 local (UTC+2) · Repo: meshcore ·
dispatch run_id `dq05-1789366088` (ownership ledger, this card status
`running`) · artifacts: this directory (`bench/soak-40c/`).

## VERDICT: SOAK UNVERIFIED for -40 C — no soak was started. Zero
## calshow log lines exist; no temperature number is reported as
## observed because none was measured. Nothing was fabricated.

Per the task PRECONDITION, the soak must NOT begin while any gate is
unmet. All three gates were checked with fresh tool evidence this
session; ALL THREE FAIL:

| gate | required | observed (fresh, this session) | met? |
|---|---|---|---|
| A | harness dry-run task completed with calshow reachable and die-temp field parseable | Dry-run card `meshcore:t_da84afb3` ("Validate calshow sampling harness at ambient") IS `done` (run_id `dq05-1789364476`, updated 2026-09-14 07:47:11, commit `ea8b9c8e`) — but its recorded verdict is **DRY RUN FAIL**: calshow reachable = **NO** (every serial-port touch was denied by the operator in that session; zero bytes of console output exist), die-temp parseable = YES offline only (7/7 SYNTHETIC self-test; never parsed from a real reply). The dry-run data log `bench/dryrun-ambient/calshow_ambient.log` DOES NOT EXIST (0 samples; verified by directory listing this session — the directory holds only REPORT.md + sample_calshow.py). The dry-run task's own acceptance rule records all four soaks UNVERIFIED with blocking reason "no calshow access". | NO → blocking reason **"no calshow access"** |
| B | parent chamber-stability task reports PASS for -40 C | Holds card `meshcore:t_0e98e408` ("Run chamber 10-min holds at +25/0/-20/-40 C and capture logs") shows ownership status `done` (run_id `dq05-1789357618`) but **no PASS verdict for -40 C exists anywhere**: the card schema in `~/.hermes/bot/fleet_queue_state.json` carries no result/status keys at all (only actor/assignee/board/body/created_ts/exclusions/id/private/repo/requires/resource_class/source_task/tags/title/type), no session matching the holds run_id exists in any profile DB (FTS for `dq05-1789357618`: 7 hits in worker-heavy, ALL of them report citations from the sibling soak/dry-run dispatches — zero real chamber data; 0 hits in worker-dq05/worker-base), no chamber log artifact on disk (repo-wide + home-wide find for `*chamber*log*`/`*hold*`/`*die*temp*` newer than 2026-09-10: zero real hits). -40 C is the hardest setpoint and is not confirmed held, so per the task body it must not be attempted. | NO → blocking reason **"parent stability task not PASS"** |
| C | the -20 C run finished and released the chamber | -20 C sibling card `meshcore:t_35c19845` ownership status is **`claimed`** (run_id: none, updated 2026-09-14 05:41:11) — it was never started, so it never ran and never released anything. No session with real -20 C work exists (FTS `"t_35c19845"` in worker-heavy: 6 hits, all board-state reads from sibling dispatches; `"-20 C soak"` / `"soak-20c"`: 0 hits everywhere). No `bench/soak-20c/` directory exists. (Moot anyway — no chamber exists to release, see root cause.) | NO (moot — no chamber exists to release) |

Root cause underneath all three gates: **there is no thermal chamber
under this host's control and no sanctioned serial access to the
module console.** Fresh USB census this session (lsusb +
`/dev/serial/by-id`): 2x QinHeng CH340 serial converters
(ttyUSB0/ttyUSB1), Raspberry Pi Debugprobe CMSIS-DAP (ttyACM0),
RTL8152 Ethernet, BT radio, audio-HID, microSD reader, hubs — **no
chamber controller, no instrument-class device**. The sibling
chamber-reservation report (commit `7d9227a1`) independently proves
NO BOOKING EXISTS and no chamber is present, located, or commandable;
the fork's own bench README (re-verified quoted in prior dispatch
sessions) states this is bench work for the operator (Felix), not for
an agent: "No agent host in this fleet has the module attached and
none can put a board in a freezer." The DUT (NiceRF LR2021 on the
felixfelix-bot fork, passive_mapper) is not attached to this host;
the fork clone at /tmp/mc-passive was re-verified this session at HEAD
`3fdfbc8e` — the `calshow` reply contract
(`cal valid=%s k=%.6g T0=%.2fC range=+/-%.0fC die_temp=%.1f off_hz=%.0f`,
MyMesh.cpp:178-181) is grounded, but a contract is not a measurement.

## Required deliverable fields, honestly filled

- SOAK verdict for -40 C: **UNVERIFIED**
- die-temp band observed (C, peak-to-peak): **none — 0 samples exist**
- dwell time (min): **0**
- timestamp range of soaked window: **N/A (no in-band samples;
  sampling never began)**
- dwell budget (>=15-20 min) met: **N/A — sampling never started**
- blocking reason(s): **"no calshow access"** (gate A: the dry run
  completed but its verdict is FAIL — calshow reachable = NO, zero
  console bytes, log file never created) AND **"parent stability task
  not PASS"** (gate B: no PASS verdict for -40 C exists anywhere) AND,
  underlying both, **"no chamber access"** (no thermal chamber is
  present, located, booked, or commandable on this host; the -20 C
  predecessor never ran, gate C).
- timestamped calshow log lines: **NONE EXIST.** The soak never began,
  so there is nothing to inline or attach. No inferred, extrapolated,
  or placeholder temperature appears anywhere in this report.

## Soak-criterion fields that WOULD have been recorded (left blank — never measured)

    achieved dwell time (min):            _not measured_
    die-temp min (C):                     _not measured_
    die-temp max (C):                     _not measured_
    die-temp peak-to-peak (C):            _not measured_
    in-band window first sample (ISO):    _not measured_
    in-band window last sample (ISO):     _not measured_
    >=15-20 min dwell budget met:         _not measured_
    chamber air temp during soak:         _not measured_
    chamber commanded to -40 C:           _never commanded_
    extra settling time for deep cold pull: _never reached (step 1 never started)_

## What was done instead of a soak (all fresh this session, 08:09-08:15)

1. **Hard-gate check BEFORE anything else, as ordered.** The task's
   step 1 ("Command the chamber to -40 C...") was never reached — no
   chamber was commanded, no setpoint was attempted, no serial port
   was opened by this session, no sampling loop was started, and no
   state was mutated. This report exists because the precondition
   gates failed, which per the task body means: report UNVERIFIED and
   stop.
2. **Fleet board + ownership ledger read** (`~/.hermes/bot/
   fleet_queue_state.json`, `~/.hermes/bot/ownership.json`): campaign
   cards enumerated — `t_da84afb3` (dry run, done → FAIL verdict),
   `t_0e98e408` (10-min holds, done with no result anywhere),
   `t_3a34bea7` (+25 C, done → UNVERIFIED, commit `114a397b`),
   `t_b0a5312a` (0 C, done → UNVERIFIED, commit `d16a2723`),
   `t_35c19845` (-20 C, claimed — never started), `t_e3bb0dba`
   (-40 C, this card), `t_6ece027b` (rollup, running). No card
   carries a result field; the meshcore card schema has no
   result/status keys at all. hold_denied: 0 entries.
3. **Dry-run outcome consumed** (the gate-A artifact): DRY RUN FAIL —
   calshow reachable NO (operator denied serial touch; zero console
   bytes), parser proven offline 7/7 against SYNTHETIC
   firmware-format strings only, log file `calshow_ambient.log` never
   created. Per the dry-run task's own acceptance rule, all four
   soaks stay UNVERIFIED with blocking reason "no calshow access"
   until a real run exists.
4. **Chamber-stability PASS searched for and not found**: fleet board
   (no result fields), all three profile session DBs (worker-heavy /
   worker-dq05 / worker-base — FTS for the holds run_id hits only
   report citations, never real chamber data; title scans for
   soak/calshow/chamber/holds/stability/dry-run in the last 4 days:
   zero real holds sessions), disk (repo-wide + home-wide artifact
   find: zero real chamber/soak logs). Sibling chamber-reservation
   report (commit `7d9227a1`) proves the chamber has never been
   located and NO BOOKING EXISTS — there is no parent-proven stable
   chamber condition to wait for, and the task forbids soaking at a
   setpoint the chamber is not confirmed to hold.
5. **-20 C predecessor checked** (gate C): card `claimed`, never
   started, no session, no artifacts, no `bench/soak-20c/` directory.
   The chamber was therefore never occupied or released by it — and
   there is no chamber to occupy in any case.
6. **Sibling verdict cross-check**: soak-0c (`d16a2723`) and soak-25c
   (`114a397b`) reached the same UNVERIFIED verdict on the same
   failing gates; their claims were spot-verified against live
   board/ledger/disk state this session rather than trusted blindly.
7. **Hardware ground truth**: `lsusb` + `/dev/serial` census (above) —
   no chamber controller, no LR2021 board. The `calshow` command
   belongs to the felixfelix-bot fork (passive_mapper,
   MyMesh.cpp:178-181 @ `3fdfbc8e`, clone re-verified on disk at
   `/tmp/mc-passive` this session); mainline MeshCore has no cal CLI.
   Even with serial access, no chamber exists to hold -40 C, so gate B
   would still fail.
8. **Orchestration-side false lead ruled out**: the only soak-named
   file outside the repo (`hermes-orchestration/scripts/fleet/
   fleet_soak_check.py`) is a 24h fleet storm-guard monitor
   (freeze/hard-kill/quarantine counter) — unrelated to thermal soak
   evidence; it carries no die-temp data.

## Evidence freshness

All board/ledger/DB/disk/USB reads above were performed this session
(2026-09-14, 08:09-08:15 local). Sibling reports cited
(dryrun-ambient `ea8b9c8e`, chamber-reservation `7d9227a1`, soak-0c
`d16a2723`, soak-25c `114a397b`) were committed 07:40-07:50 the same
morning and their claims were spot-verified against live state rather
than trusted blindly.

## What unblocks this setpoint (for the operator, not for agents)

1. A thermal chamber must actually exist, be located/identified, be
   confirmed to hold -40 C within tolerance for >=10 min with real
   logs (the parent holds card `t_0e98e408` re-run) — only then does
   the -40 C soak become permissible under this task's own rules.
   -40 C is the hardest setpoint; extra settling time for the deep
   cold pull is budgeted in the procedure but can only be spent once
   the chamber is real.
2. Serial access to the module console must be sanctioned; the
   dry-run harness (`bench/dryrun-ambient/sample_calshow.py`) then
   needs one real run of `--samples 3` to prove calshow reachability
   and flip its FAIL verdict, after which the soak sampling loop can
   start.
3. The DUT (NiceRF LR2021 module on the fork firmware) must be
   attached and powered for the whole soak window; per the fork's
   bench README this is operator bench work (Felix), not agent work.
4. The -20 C soak card `t_35c19845` must run to completion and
   release the chamber before this card re-dispatches (single-chamber
   serialization).