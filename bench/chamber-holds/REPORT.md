# Chamber 10-min holds at +25/0/-20/-40 C — verdict & evidence

Task (fleet card `meshcore:t_0e98e408`): "Run chamber 10-min holds at
+25/0/-20/-40 C and capture logs." Physically command and HOLD the
chamber at each setpoint, log chamber air temp for >=10 continuous
minutes per setpoint, note ramp time / overshoot / alarms, attach raw
logs.

Date: 2026-09-14, session 23:11 local (UTC+2) · Repo: meshcore ·
host: `c03rad0r-DQ05proplus` (worker profile dq05) ·
dispatch run_id `dq05-1789420047` (ownership ledger, this card status
`running`) · artifacts: this directory (`bench/chamber-holds/`).

---

## VERDICT: ALL FOUR SETPOINTS UNVERIFIED — no chamber was commanded,
no setpoint was reached or held, zero air-temp data exists.

No temperature value in this report was measured, observed, inferred,
interpolated, or extrapolated. Every number below is either an
equipment-status fact or a cross-reference to a prior report. No
chamber air-temperature log exists because no chamber exists under
this host's control.

---

## Per-setpoint evidence table (exactly four rows)

| setpoint C | HOLD verdict | command accepted? | displayed setpoint | air-temp log duration | log start timestamp | log end timestamp | time to reach from ambient | overshoot | alarms/faults | raw log attached | blocking reason |
|---|---|---|---|---|---|---|---|---|---|---|---|
| +25 | UNVERIFIED | never commanded (no chamber) | N/A | 0 min | N/A | N/A | N/A | N/A | N/A | NONE — no log exists | no chamber access |
| 0 | UNVERIFIED | never commanded (no chamber) | N/A | 0 min | N/A | N/A | N/A | N/A | N/A | NONE — no log exists | no chamber access |
| -20 | UNVERIFIED | never commanded (no chamber) | N/A | 0 min | N/A | N/A | N/A | N/A | N/A | NONE — no log exists | no chamber access |
| -40 | UNVERIFIED | never commanded (no chamber) | N/A | 0 min | N/A | N/A | N/A | N/A | N/A | NONE — no log exists | no chamber access |

Every "N/A" means the action was never performed. Per the task
RULES: "If you did not physically run the chamber, do NOT report
PASS — mark each unrun setpoint UNVERIFIED and state exactly what
evidence you have." That is what this table does. No setpoint was
physically run.

---

## What evidence exists (all gathered fresh this session, 23:11-23:14)

### 1. No thermal chamber exists under this host's control

**USB bus** (lsusb + lsusb -t + /dev/serial/by-id, enumerated fresh
at 23:11):

```
Bus 001 Dev 001: 1d6b:0002 Linux Foundation 2.0 root hub
Bus 002 Dev 001: 1d6b:0003 Linux Foundation 3.0 root hub
Bus 003 Dev 001: 1d6b:0002 Linux Foundation 2.0 root hub
Bus 003 Dev 002: 0bda:b850 Realtek Bluetooth Radio
Bus 003 Dev 003: 0573:1573 Zoran USB Audio and HID
Bus 003 Dev 004: 1a40:0801 Terminus Technology USB 2.0 Hub
Bus 003 Dev 005: 0bda:8152 Realtek RTL8152 Fast Ethernet Adapter
Bus 003 Dev 006: 067b:2586 Prolific USB 2.0 Hub
Bus 003 Dev 007: 14cd:1212 Super Top microSD card reader (SY-T18)
Bus 003 Dev 008: 1a86:7523 QinHeng CH340 serial converter  → /dev/ttyUSB0
Bus 003 Dev 009: 2e8a:000c Raspberry Pi Debugprobe (CMSIS-DAP)  → /dev/ttyACM0
Bus 003 Dev 010: 1a86:7523 QinHeng CH340 serial converter  → /dev/ttyUSB1
Bus 004 Dev 001: 1d6b:0003 Linux Foundation 3.0 root hub
```

No chamber controller. No instrument-class device (no VNA, no DMM,
no SCPI/LXI instrument). The two CH340 serial converters are generic
USB-to-serial adapters (QinHeng CH340, VID 1a86 PID 7523) — these
are the Meshtastic device console/debug ports, not chamber
controllers. The Raspberry Pi Debugprobe (2e8a:000c) is a
CMSIS-DAP debug probe for an RP2040 — also not a chamber
controller.

**Network**: no LXI/VISA/SCPI instrument discovered. Ping sweep of
the wired LAN (192.168.21.0/24) found one live host
(192.168.21.200, port 22 open — SSH only, not an instrument).
Common SCPI raw-TCP port 5025 is closed on all reachable hosts.
Port 1394 (VXI-11), 7777, 1234 also closed. No HTTP on .200.

**I2C/SPI/GPIO**: /dev/i2c-0 through /dev/i2c-13 exist (SMBus
backplane, root-only access) — these are motherboard sensors, not
chamber interfaces. /dev/gpiochip0 is the onboard GPIO controller.
None is connected to a chamber.

### 2. No chamber has ever been located or identified

The chamber-ownership reports (commit `4b3ec9b5`,
bench/chamber-ownership/REPORT.md) state: "no chamber controller and
no chamber-control/scheduling software exists on any record or on
this host." The chamber-locate card (`t_ffc911f6`) and
chamber-identify card (`t_a2f7f281`) were both `decision: skip`
(no-headroom) with no result ever produced. The chamber-reservation
report (commit `7d9227a1`) independently proves NO BOOKING EXISTS.
This session re-verified: no chamber config file, no chamber
datasheet, no chamber manual exists anywhere on this host
(find across /home/c03rad0r for files matching chamber/thermal/
SCPI/VISA/GPIB/watlow/eurotherm — zero relevant hits).

### 3. The DUT is not attached to this host

The fork's own bench README (commit `d7ae93fa`) states verbatim:
"No agent host in this fleet has the module attached and none can
put a board in a freezer." This was re-verified in prior dispatches
(65c9c3df, 79ea692e, 4b3ec9b5) and remains true — the USB census
shows no LR2021 module, only Meshtastic debug consoles.

### 4. This card's own prior "done" status has no PASS verdict

The ownership ledger (`~/.hermes/bot/ownership.json`, read fresh
this session) shows this card (`meshcore:t_0e98e408`) with status
`running`, run_id `dq05-1789420047`, updated ts 1789420047. A prior
run (run_id `dq05-1789357618`) was marked `done` but produced no
result — no PASS verdict, no chamber log, no session with real
chamber data (verified by session-DB FTS in prior dispatches: zero
hits matching the run_id in any profile DB). The fleet card schema
in `fleet_queue_state.json` carries no result/status/verdict keys
at all (only actor/assignee/board/body/created_ts/exclusions/id/
private/repo/requires/resource_class/source_task/tags/title/type).

### 5. Prior dispatches all reached the same verdict

The four downstream soak cards (+25 C `t_3a34bea7`, 0 C
`t_b0a5312a`, -20 C `t_35c19845`, -40 C `t_e3bb0dba`) each
gate on THIS card reporting PASS. All four were previously
dispatched and all four reached UNVERIFIED with the same root cause:
no chamber access, no calshow access. Their reports are at:
- bench/soak-25c/REPORT.md (commit 114a397b) — UNVERIFIED
- bench/soak-0c/REPORT.md (commit d16a2723) — UNVERIFIED
- bench/soak-20c/REPORT.md (commit 866d59cd) — UNVERIFIED
- bench/soak-40c/REPORT.md (commit 76f6a129) — UNVERIFIED
- bench/soak-rollup/REPORT.md — all four UNVERIFIED
- bench/dryrun-ambient/REPORT.md (commit ea8b9c8e) — DRY RUN FAIL

### 6. No serial port was opened by this session

Consistent with prior dispatches where serial access was
operator-denied, this session did not open, write to, or read from
any serial port. Zero bytes were sent to any device. The USB
enumeration above is read-only (lsusb, udevadm, stty — all
non-invasive). No state was mutated on any hardware.

---

## Raw log / export

**No raw log exists.** No chamber was commanded, so no chamber
output was produced. Per the task ACCEPTANCE criterion: "For every
setpoint, either raw timestamped >=10-min data or an explicit
UNVERIFIED with a statement of what evidence exists." This report
provides the latter for all four setpoints — explicit UNVERIFIED
with the evidence statement above (no chamber present, located, or
commandable on this host; USB bus enumerated; no chamber controller
found).

No file was created, fabricated, or placeholder-filled. No
temperature value appears as a measurement anywhere in this report.

---

## Ambient temperature (for context only — NOT a chamber reading)

The only temperature sensor on this host is the ACPI thermal zone:
- /sys/class/hwmon/hwmon0 (acpitz): 27800 millidegrees C = 27.8 C
  (read at 23:11:35 local)

This is the motherboard thermal zone, not a chamber air sensor. It
is reported here only to document ambient lab conditions, not as a
substitute for chamber air temperature. No chamber air-temperature
sensor exists on this host.

---

## What unblocks this task (for the operator, not for agents)

1. A thermal chamber must physically exist, be located, identified
   (make/model/serial), and connected to this host or a host under
   fleet control — via USB serial, RS-232 adapter, GPIB, or
   LXI/ethernet. The chamber-locate (`t_ffc911f6`) and
   chamber-identify (`t_a2f7f281`) cards must produce results.
2. The chamber controller's command interface must be documented
   (SCPI commands, register map, or proprietary protocol) so a
   setpoint command can be issued and an air-temp reading can be
   polled from the chamber's own sensor.
3. The DUT (NiceRF LR2021 module on the fork firmware) must be
   attached and placed inside the chamber.
4. Per the fork's bench README (d7ae93fa), this is bench work for
   the operator (Felix), not for an agent: "This is bench work for
   the operator (Felix), not for an agent: it needs a NiceRF LR2021
   module, a way to hold it at temperature for hours, and a second
   MeshCore node as a reference transmitter."

Once a real chamber is provisioned and its controller interface is
available, this task can be re-run: command each setpoint in turn
(+25 → 0 → -20 → -40 C), wait for the controller to report
at-setpoint/settled, then log chamber air temp at 10-30 s cadence
for >=10 min per setpoint, recording start/end timestamps, ramp
time, overshoot, and any alarms.

---

## Evidence trail freshness

All board/ledger/USB/filesystem reads above were performed this
session (2026-09-14, 23:11-23:14 local). Prior reports cited
(chamber-ownership `4b3ec9b5`, chamber-reservation `7d9227a1`,
soak reports `114a397b`/`d16a2723`/`866d59cd`/`76f6a129`,
dryrun-ambient `ea8b9c8e`, condensation-risk `65c9c3df`,
ramp-feasibility `79ea692e`) were spot-verified against live
board/ledger/disk state rather than trusted blindly.