# Die-temp soak evidence at -20 C — verdict & evidence

Task (fleet card `meshcore:t_35c19845`): capture timestamped `calshow`
evidence that a thermally soaked die state (die temp within a ~0.5 C
peak-to-peak band for >=15 consecutive minutes) is reachable at setpoint
-20 C.

Date: 2026-09-14, session 08:11-08:14 local (UTC+2) · Repo: meshcore ·
dispatch run_id `dq05-1789366236` (ownership ledger, this card status
`running`) · artifacts: this directory (`bench/soak-20c/`).

## VERDICT: SOAK UNVERIFIED for -20 C — no soak was started. Zero
## calshow log lines exist; no temperature number is reported as
## observed because none was measured. Nothing was fabricated.

Per the task PRECONDITION, the soak must NOT begin while any gate is
unmet. All three gates were checked with fresh tool evidence this
session; two hard-fail and the third is moot:

| gate | required | observed (fresh, this session) | met? |
|---|---|---|---|
| A | harness dry-run task completed with calshow reachable and die-temp field parseable | Dry-run card `meshcore:t_da84afb3` ("Validate calshow sampling harness at ambient") IS done (ownership status `done`, run_id `dq05-1789364476`, commit `ea8b9c8e`, report `bench/dryrun-ambient/REPORT.md`) — but its verdict is **DRY RUN FAIL**: calshow reachable = **NO** (every attempt to open/touch a serial port was denied by the operator; zero bytes of console output exist), die-temp parseable = YES offline only (7/7 SYNTHETIC self-test, re-run this session exit 0; never parsed from a real reply). Log file `bench/dryrun-ambient/calshow_ambient.log` DOES NOT EXIST — re-confirmed fresh this session at 08:12 (0 samples; deliberately never created). Session-DB FTS sweep across all three profile DBs (worker-heavy, worker-dq05, worker-base): zero real `calshow` replies anywhere — every "cal valid=" hit is firmware source, spec text, or report citation, never a measured reply. | NO → blocking reason **"no calshow access"** |
| B | parent chamber-stability task reports PASS for -20 C | Holds card `meshcore:t_0e98e408` ("Run chamber 10-min holds at +25/0/-20/-40 C and capture logs") shows ownership status `done` (run_id `dq05-1789357618`) but **no PASS verdict exists anywhere**: the card schema carries NO result/verdict/status/outcome fields at all (verified fresh — keys are actor/assignee/board/body/created_ts/exclusions/id/private/repo/requires/resource_class/source_task/tags/title/type), no session matching run_id `dq05-1789357618` exists in any profile DB (FTS: 0 hits in worker-dq05 and worker-base; only report citations in worker-heavy), and no chamber log artifact exists on disk (filesystem sweep this session). The chamber was never located, identified, or commanded: chamber-locate/ID cards (`t_ffc911f6`, `t_a2f7f281`) are `decision: skip` (no-headroom); the sibling chamber-reservation report (commit `7d9227a1`) independently proves **NO BOOKING EXISTS** and no chamber is present, located, or commandable on this host. | NO → blocking reason **"parent stability task not PASS"** |
| C | the 0 C run finished and released the chamber — one chamber, no overlapping runs | 0 C sibling card `meshcore:t_b0a5312a` IS done (ownership `done`, run_id `dq05-1789364037`, updated 07:41 local, commit `d16a2723`, verdict UNVERIFIED with zero samples — it never touched any hardware). So no run overlaps this one. | lifecycle YES — but **moot** (no chamber exists to release or occupy) |

Root cause underneath the gates: **there is no thermal chamber under
this host's control and no sanctioned serial access to the module
console.** USB bus enumerated fresh this session (lsusb, 08:12): 2x
QinHeng CH340 serial, Raspberry Pi Debugprobe CMSIS-DAP, RTL8152
Ethernet, BT radio, audio-HID, microSD reader, hubs — **no chamber
controller, no instrument-class device, no LR2021 module attached**
(consistent with the fork's own bench README: "No agent host in this
fleet has the module attached and none can put a board in a freezer").
Prior dispatches (soak-0c `d16a2723`, dryrun-ambient `ea8b9c8e`,
soak-25c `114a397b`, soak-40c `76f6a129`) independently verified the
same absence on 2026-09-12/14.

## Required deliverable fields, honestly filled

- SOAK verdict for -20 C: **UNVERIFIED**
- die-temp band observed (C, peak-to-peak): **none — 0 samples exist**
- dwell time (min): **0**
- timestamp range of soaked window: **N/A (no in-band samples; no
  sampling began)**
- dwell budget (>=15-20 min) met: **N/A — sampling never started**
- blocking reasons: **"no calshow access"** (gate A: the dry run
  completed but FAILED — calshow reachable = NO, serial access
  operator-denied, zero console bytes) and **"parent stability task
  not PASS"** (gate B: no PASS verdict for -20 C exists anywhere).
  Deeper root cause: **no chamber access** — no thermal chamber is
  present, located, or commandable on this host, and the DUT is not
  attached. Per the task's FAILURE-HANDLING vocabulary this is the
  "no chamber access / no calshow access" branch.
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

## What was done instead of a soak (all fresh this session, 08:11-08:14)

1. **Hard-gate check BEFORE anything else**, as ordered. The task's
   step 1 ("Command the chamber to -20 C...") was never reached — no
   chamber was commanded (none exists), no setpoint was attempted, no
   serial port was opened by this session, no sample loop was started,
   and no state was mutated. This report exists because the
   precondition gates failed, which per the task body means: report
   UNVERIFIED and stop.
2. **Fleet board + ownership ledger read** (`~/.hermes/bot/fleet_queue_state.json`,
   `~/.hermes/bot/ownership.json`): this card `t_35c19845` `running`
   (run_id `dq05-1789366236`); dry-run `t_da84afb3` `done` → FAIL
   verdict; holds `t_0e98e408` `done` with no result; 0 C
   `t_b0a5312a` `done` (07:41) → UNVERIFIED; +25 C `t_3a34bea7`
   `done` → UNVERIFIED; -40 C `t_e3bb0dba` `running` (sibling session
   landed commit `76f6a129` during this session with the same
   gate-fail verdict); rollup `t_6ece027b` `running`. The card schema
   has no result/status keys at all (verified fresh on the holds card
   and this card).
3. **Dry-run outcome consumed** (commit `ea8b9c8e`): DRY RUN FAIL —
   calshow reachable NO (operator denied serial touch; zero console
   bytes), parser proven offline 7/7 against SYNTHETIC
   firmware-format strings only. The dry-run task's own acceptance
   rule records all four soaks UNVERIFIED with blocking reason
   "no calshow access". Re-verified fresh: log file
   `calshow_ambient.log` absent, self-test re-run 7/7 exit 0.
4. **Chamber-stability PASS searched for and not found**: card
   schema (no result fields), session DBs (FTS for run_id
   `dq05-1789357618` — 0 real hits; no holds/stability session in
   any profile), disk (no chamber log anywhere; the only
   thermal-shaped file on the host is the known SYNTHETIC
   `/tmp/hyst_refusal_demo_SYNTHETIC_dwell_only.csv`). Sibling
   chamber-reservation report (`7d9227a1`) proves NO BOOKING EXISTS —
   there is no parent-proven stable chamber condition to wait for,
   and the task forbids soaking at a setpoint the chamber is not
   confirmed to hold ("do not shortcut it" cuts both ways).
5. **Session-DB cross-check**: FTS sweep of all three profile DBs for
   real `calshow` replies ("cal valid=") — every hit is source/spec/
   report text, never a measured console reply; "chamber" AND "PASS"
   hits are all task prompts and report prose, never a verdict. No
   measured die-temp value exists anywhere on this fleet.
6. **Sibling verdict cross-check**: soak-0c (`d16a2723`), soak-25c
   (`114a397b`), and soak-40c (`76f6a129`, landed 08:12 during this
   session) all reached UNVERIFIED on the same gates for their
   setpoints.
7. **Hardware ground truth**: `lsusb` + `/dev/serial` census (above) —
   no chamber controller, no LR2021 board. The `calshow` command
   belongs to the felixfelix-bot fork (passive_mapper); fork clone at
   `/tmp/mc-passive` re-verified at HEAD `3fdfbc8e` this session, and
   the reply contract `cal valid=%s k=%.6g T0=%.2fC range=+/-%.0fC
   die_temp=%.1f off_hz=%.0f` re-read directly from
   `MyMesh.cpp:179`. Mainline MeshCore (this repo) has no cal CLI.
8. **No serial touch**: consistent with the operator's repeated
   denials (three prior sessions), no serial port was opened,
   written, or read by this session — zero bytes sent.

## Evidence trail freshness

All board/ledger/session-DB/filesystem/USB reads above were performed
this session (2026-09-14, 08:11-08:14 local). Sibling reports cited
(dryrun-ambient `ea8b9c8e`, soak-0c `d16a2723`, soak-25c `114a397b`,
soak-40c `76f6a129`, chamber-reservation `7d9227a1`) were
spot-verified against live board/ledger/disk state rather than
trusted blindly.

## What unblocks this setpoint (for the operator, not for agents)

1. A thermal chamber must actually exist, be located/identified, and
   be confirmed to hold -20 C within tolerance for >=10 min (the
   parent holds card `t_0e98e408` re-run with real logs) — only then
   does a -20 C soak become permissible under this task's own rules.
   Cold pulls take longer to settle, and that settling is exactly
   what the parent hold must prove first.
2. Serial access to the module console must be sanctioned; the
   dry-run harness (`bench/dryrun-ambient/sample_calshow.py`) then
   needs one run of `--samples 3` to prove calshow reachability, after
   which the soak sampling loop can start (30-60 s cadence, raw
   die-temp strings preserved verbatim).
3. The DUT (NiceRF LR2021 module on the fork firmware) must be
   attached and powered for the whole soak window; per the fork's
   bench README this is operator bench work (Felix), not agent work.
4. Sequence note for the re-run: the -40 C sibling card gates on THIS
   card finishing; this card gates on the 0 C card (done). Once
   chamber + serial access exist, the campaign order
   +25 → 0 → -20 → -40 C should be re-run front-to-back so each
   setpoint's log lines stay contiguous and the chamber gets its
   transition time between setpoints.