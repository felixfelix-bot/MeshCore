# Die-temp soak evidence at 0 C — verdict & evidence

Task (fleet card `meshcore:t_b0a5312a`): capture timestamped `calshow`
evidence that a thermally soaked die state (die temp within a ~0.5 C
peak-to-peak band for >=15 consecutive minutes) is reachable at setpoint
0 C.

Date: 2026-09-14 (session ~07:35 local, UTC+2) · Repo: meshcore ·
artifacts: this directory (`bench/soak-0c/`).

## VERDICT: UNVERIFIED for 0 C — no soak was started. Zero calshow
## log lines exist; no temperature number is reported because none was
## measured. Nothing was fabricated.

Per the task PRECONDITION, the soak must NOT start while any gate is
unmet. All three gates were checked with fresh tool evidence and all
three fail:

| gate | required | observed (fresh, this session) | met? |
|---|---|---|---|
| A | harness dry-run task completed: calshow reachable, die-temp field parseable | dry-run card `meshcore:t_da84afb3` "Validate calshow sampling harness at ambient (dry run)" — ownership status **`claimed`** (never advanced to done; no run_id). No session for it exists in the session DB (title search: 0 hits). No dry-run log file exists on disk (host-wide find for `*calshow*`/`*soak*`/`*die*temp*`/`*dwell*` newer than 2026-09-10: 0 real hits). | NO → blocking reason **"no calshow access"** |
| B | parent chamber-stability task reports PASS for 0 C | holds card `meshcore:t_0e98e408` "Run chamber 10-min holds at +25/0/-20/-40 C and capture logs" — ownership lifecycle flag `done` (run_id `dq05-1789357618`), but **no PASS verdict exists anywhere**: no matching session in the DB, no `result` field on the card (the meshcore card schema in `~/.hermes/bot/fleet_queue_state.json` carries no result/status keys at all), no chamber log artifact on disk. The sibling atcut-fit fourth-dispatch report (a9d72654) already documented the entire physical-bench prerequisite cluster as `decision: skip` (no-headroom) / assigned-no-result — including `t_ffc911f6` "Physically locate thermal chamber" (skip) and `t_a2f7f281` "Physically identify thermal chamber" (skip). | NO → blocking reason **"parent stability task not PASS"** |
| C | previous setpoint run (+25 C) finished and released the chamber | +25 C sibling card `meshcore:t_3a34bea7` ownership status **`running`** (run_id `dq05-1789364113`, updated this morning). It has not finished. | NO (moot — no chamber exists to release) |

Root cause underneath all three gates: **there is no thermal chamber
under this host's control.** No chamber-control interface exists on the
USB bus (re-enumerated this session: 2x CH340 serial, Pi Debugprobe,
RTL8152 Ethernet, BT/audio-HID/microSD/hubs only — no instrument-class
or chamber-controller device), the chamber-locate/identify/hold cluster
was skipped by the scheduler with no result ever produced, and the
prior bench reports (atcut-fit REPORT.md, thermal-lag REPORT.md)
independently re-verified the same absence on 2026-09-12/14.

## Required deliverable fields, honestly filled

- SOAK verdict for 0 C: **UNVERIFIED**
- die-temp band observed (C, peak-to-peak): **none — 0 samples exist**
- dwell time (min): **0**
- timestamp range of soaked window: **N/A (no in-band samples)**
- dwell budget (>=15-20 min) met: **N/A**
- blocking reason(s): **"no calshow access"** (gate A: the dry-run task
  never completed, so calshow reachability and die-temp parseability are
  undemonstrated) and **"parent stability task not PASS"** (gate B: no
  PASS verdict for 0 C exists). Deeper root cause: no chamber access —
  no thermal chamber is present, located, or commandable on this host.
- timestamped calshow log lines: **none exist.** No sample was taken, so
  there is nothing to inline. No inferred or extrapolated temperature
  appears anywhere in this report.

## Evidence trail (all gathered fresh this session, 2026-09-14)

1. **Fleet queue state** (`~/.hermes/bot/fleet_queue_state.json`, read
   directly): the six campaign cards exist — `t_da84afb3` (dry run),
   `t_0e98e408` (10-min holds), `t_3a34bea7` (+25 C), `t_b0a5312a`
   (0 C, this task), `t_35c19845` (-20 C), `t_e3bb0dba` (-40 C),
   `t_6ece027b` (rollup) — and none carries a result field; the card
   schema has no result/status keys at all.
2. **Ownership ledger** (`~/.hermes/bot/ownership.json`): dry-run card
   `claimed` (never done); holds card `done` with no result record
   anywhere (no session, no log, no PASS verdict); +25 C card
   `running` (not finished); -20 C / -40 C / rollup cards `claimed`.
3. **Session DB**: every soak-campaign session dispatched to this host
   (2026-09-14 05:01, 06:45, 06:53, 06:53, 06:55, 07:00, 07:00, 07:00,
   07:35) contains the task prompt and **nothing else** — no sampling
   loop, no chamber command, no calshow output, no assistant work. There
   is no session matching the holds run_id `dq05-1789357618`.
4. **Filesystem**: repo-wide and home-wide finds for soak/calshow/
   chamber/die-temp/dwell artifacts newer than 2026-09-10 → only the 5
   known SYNTHETIC self-test CSVs in /tmp (labeled synthetic, produced
   by the sibling fit/lag/hyst tool self-tests; none is a calshow log).
   Zero real soak logs.
5. **USB bus** (re-enumerated this session): no chamber controller, no
   instrument-class devices — unchanged from the 2026-09-11/12/14
   guard-trip reports.
6. **Live serial probe**: a read-only reachability probe
   (`probe_calshow_reach.py`, this directory) was prepared to ground
   gate A in fresh physical evidence (open 115200 8N1, DTR/RTS off, send
   the firmware's read-only `calshow\r` per CAL-CLI-SPEC.md, capture raw
   bytes). **Its execution was denied by the operator**, so it provides
   no evidence either way; the script is retained, unexecuted, for the
   future dry-run session. The archival record above is what the
   verdict stands on.

## What remains ready for the unblock

- `probe_calshow_reach.py` (this directory): read-only calshow
  reachability probe — prints ISO-8601 timestamps and raw bytes per
  port, never infers a temperature. Run it as step 1 of the dry-run task
  (`t_da84afb3`) once serial access is sanctioned.
- The full `calshow` output contract is already machine-verified in
  `bench/atcut-fit/CAL-CLI-SPEC.md` (readback line:
  `cal valid=%s k=%.6g T0=%.2fC range=+/-60C die_temp=... off_hz=...`,
  MyMesh.cpp:178-181 @ 3fdfbc8e) — the die-temp field of a real reply
  can be parsed verbatim with no further reverse-engineering.

## Unblock path (unchanged from the parent cluster)

1. Human bench session: physically locate/provision a thermal chamber
   reachable from this host, with a controller interface on the bus.
2. Run the dry-run card `t_da84afb3` (ambient, module powered,
   `probe_calshow_reach.py` then the 30-60 s sampling loop) and record
   calshow reachable YES/NO with the raw log.
3. Run the parent holds card `t_0e98e408` and record an explicit
   per-setpoint PASS/FAIL verdict for 0 C with chamber air-temp logs.
4. Only then re-dispatch this card: command 0 C, wait for the
   parent-proven stable condition, sample calshow every 30-60 s,
   >=15 min in-band dwell, <=0.5 C peak-to-peak, log lines contiguous
   with raw die-temp strings preserved.