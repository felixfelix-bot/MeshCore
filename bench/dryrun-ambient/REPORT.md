# calshow sampling harness dry run at ambient — verdict & evidence

Task (fleet card `meshcore:t_da84afb3`): validate the calshow sampling
harness at ambient with the module powered and instrumented as it will
be for the soaks. Prove the evidence-capture tooling works before any
chamber soak is attempted, and give the requester an early hard-gate
answer. Nothing else in the campaign may start until this dry run
passes.

Date: 2026-09-14 · Repo: meshcore · artifacts: this directory
(`bench/dryrun-ambient/`).

## VERDICT: DRY RUN FAIL — no calshow samples exist. Hard gate NOT
## passed. Blocking reason: **"no calshow access"**. Nothing was
## fabricated.

## Hard-gate answer (the short note the task demands)

- **calshow reachable: NO** (not demonstrated — every attempt to touch
  a serial port this session was denied by the operator, so zero bytes
  of console output exist; reachability is undemonstrated, and under
  this campaign's rules undemonstrated = blocked)
- **die-temp field parseable: YES — parser proven offline 7/7**
  (`--self-test`, SYNTHETIC firmware-format strings, clearly labeled,
  not measurements). The parser logic is grounded in the firmware
  source itself (reply contract at MyMesh.cpp:178-181 @ 3fdfbc8e, read
  this session from the on-disk fork clone at /tmp/mc-passive, HEAD
  verified 3fdfbc8e). But "parseable" for the gate means parsed from a
  REAL calshow reply, and no real reply was ever received.
- **log path: bench/dryrun-ambient/calshow_ambient.log — DOES NOT
  EXIST** (0 sample lines; it is only ever created by a real run, and
  no real run was possible; no empty or fake log was created)
- **exact invocation command**:
  `python3 bench/dryrun-ambient/sample_calshow.py --port /dev/ttyUSB0 --samples 3 --interval-secs 30 --log bench/dryrun-ambient/calshow_ambient.log`
  (wire bytes sent per sample: `calshow\r` — read-only calshow command,
  CR terminator per CAL-CLI-SPEC.md; 115200 8N1, DTR/RTS deasserted)
- **raw sample lines: NONE.** No sample was taken, so there is nothing
  to inline. No inferred or extrapolated temperature appears anywhere
  in this report.

## Consequence for the four soak tasks (recorded as instructed)

The four chamber soaks (+25 C, 0 C, -20 C, -40 C) must NOT start. All
four are recorded **UNVERIFIED, blocking reason "no calshow access"**:

| setpoint | soak verdict | blocking reason |
|---|---|---|
| +25 C (`t_3a34bea7`) | UNVERIFIED | no calshow access |
| 0 C (`t_b0a5312a`) | UNVERIFIED | no calshow access |
| -20 C (`t_35c19845`) | UNVERIFIED | no calshow access |
| -40 C (`t_e3bb0dba`) | UNVERIFIED | no calshow access |

## What was actually done (fresh evidence, this session)

1. **Serial bus enumerated**: 2x QinHeng CH340 serial converters
   (/dev/ttyUSB0, /dev/ttyUSB1), Raspberry Pi Debugprobe CMSIS-DAP
   (/dev/ttyACM0), RTL8152 Ethernet, BT/audio-HID/microSD/hub — **no
   chamber controller, no instrument-class devices** (consistent with
   the 2026-09-11/12/14 guard-trip reports and bench/soak-0c/REPORT.md).
2. **Attempt to open serial ports for the reachability probe was DENIED
   by the operator** (same outcome as the prior soak-0c dispatch,
   d16a2723, where probe execution was also denied). Under the
   campaign rule "no fabrication", a denied serial touch means zero
   samples and the loud blocked verdict above. The denial is the
   reason calshow reachable = NO (undemonstrated), NOT evidence that
   the module is absent or unpowered — the CH340 debug-probe pair
   remains enumerated, so the module's console interface is plausibly
   live, but plausibly-live is not evidence; only a real probe can
   settle it, and none was permitted.
3. **Harness authored & parser proven offline**: the complete sampling
   loop exists and runs — `sample_calshow.py --self-test` passes 7/7
   (exit 0, fresh run this session). The self-test exercises
   invoke→parse→append logic against SYNTHETIC firmware-format strings
   (including sign edge cases `-0.0`/`-19.7` and a `nan` raw, plus help/
   echo/usage lines that must NOT match). The strings are labeled
   SYNTHETIC and never touch the data log.
4. **Firmware ground truth re-verified**: the `calshow` reply contract
   `cal valid=%s k=%.6g T0=%.2fC range=+/-%.0fC die_temp=%.1f
   off_hz=%.0f` was read directly from the fork source
   (MyMesh.cpp:178-181 @ 3fdfbc8e) — so when a real reply arrives, the
   die-temp field extraction is deterministic with no further
   reverse-engineering. Note this repo (mainline MeshCore) carries no
   cal CLI at all; the soak campaign targets the felixfelix-bot fork
   (passive_mapper), whose clone survives on disk at /tmp/mc-passive.

## Log-file format (the format the soaks will use)

    iso8601,setpoint,chamber_air_c,die_temp_raw

- `iso8601` — local-time ISO-8601 with UTC offset, second resolution.
- `setpoint` — literal `AMBIENT` for the dry run; the setpoint under
  soak for the campaign runs.
- `chamber_air_c` — `n/a` for the dry run (no chamber exists under
  this host's control).
- `die_temp_raw` — **the RAW STRING exactly as printed by calshow**
  (e.g. what follows `die_temp=` up to the next space, byte-for-byte,
  e.g. `23.4`, `-0.0`), never converted or rounded by the harness.

Append-only; header written only when the file is new. Failures
(no reply, port error) are printed to stdout and counted, and the
process exits nonzero — a failed sample is NEVER appended to the data
log (that is the anti-fabrication guarantee).

## Parser logic (recorded for the requester)

One regex, anchored on the firmware's own reply shape
(MyMesh.cpp:179-181 @ 3fdfbc8e):

    cal valid=(?P<valid>\S+) k=(?P<k>\S+) T0=(?P<t0>\S+)
    range=(?P<range>\S+) die_temp=(?P<die_temp>\S+) off_hz=(?P<off_hz>\S+)

`die_temp=(?P<die_temp>\S+)` captures verbatim the non-space run after
`die_temp=`, preserving the raw string exactly as printed (including
`-0.0`, `nan`, or any precision the firmware emits). A secondary
`^[-+]?[0-9]+(\.[0-9]+)?$` check classifies whether the raw string has
normal decimal grammar (used only for reporting, never rewrites the
stored value). The reply line is found by scanning the CR/LF-split RX
buffer after sending `calshow\r` (CR terminator is mandatory — LF-only
lines never execute per CAL-CLI-SPEC.md §2); the LAST matching line in
the window wins; echo/help/usage lines do not match and are discarded.
Full code: `bench/dryrun-ambient/sample_calshow.py`.

## What remains ready for the unblock

Everything is now one sanctioned serial touch away:

1. Sanction serial access (or run the probe at the bench), then:
   `python3 bench/dryrun-ambient/sample_calshow.py --port <port>
   --samples 3 --interval-secs 30` — that single command produces the
   gate evidence: >=3 timestamped log lines with raw die-temp strings,
   and the log file at the documented path.
2. If >=3 samples parse clean, the dry-run gate PASSES and the four
   soaks unblock (each still gated on its own parent chamber-stability
   PASS — see bench/soak-0c/REPORT.md gate B, and on chamber
   provisioning, gate C root cause).
3. `probe_calshow_reach.py` (bench/soak-0c/) remains available for a
   first read-only which-port check before sampling.