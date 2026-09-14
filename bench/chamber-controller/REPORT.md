# Chamber controller type + setpoint commanding method — verdict & evidence

Task (fleet card `meshcore:t_4e41856d`): "Document chamber controller type
and setpoint commanding method ... by direct physical inspection (and
manual cross-check if available). Do NOT assume a method works without
evidence."

Date: 2026-09-14, session 23:16-23:26 local (UTC+2) · Repo: meshcore ·
host: `c03rad0r-DQ05proplus` (worker profile dq05) · dispatch
running[] ts 1789420443 (3rd dispatch of this card to dq05; prior
dispatches ts 1789354599, 1789357622 — none produced a result) ·
artifacts: this directory (`bench/chamber-controller/`).

---

## VERDICT: UNKNOWN across the board — no thermal chamber or freezer
## exists under this host's control or on any record, so there is no
## controller to inspect, no interface to photograph, and no command
## path to document.

This card's steps 1-3 require direct physical inspection of a chamber
control interface. **That inspection could not be performed because no
chamber was found to inspect.** Everything below is either a
this-session observation (marked [MEASURED] with the command that
produced it), a citation of a committed prior report, or an explicit
UNKNOWN. Nothing was assumed, inferred-as-fact, or fabricated. No
photograph exists because (a) there is no chamber to photograph and
(b) this host has no camera device ([MEASURED — `ls /dev/video*`:
"No such file or directory"]).

---

## Step 1 — Controller type: UNKNOWN (no controller exists to classify)

None of the task's candidate classes (integrated front-panel,
standalone PID/PLC, PC/software, remote/SCADA, network API, other)
could be confirmed or excluded, because the controller-bearing
instrument does not exist on any record or on this host.

Controller make/model: **UNKNOWN — no separate controller unit was
found, and the chamber itself has never been located or identified.**

Evidence, all gathered fresh this session (23:16-23:26):

1. **USB bus census** ([MEASURED — `lsusb`, 23:16]): 2x QinHeng CH340
   serial converters (1a86:7523), Raspberry Pi Debugprobe CMSIS-DAP
   (2e8a:000c), Realtek RTL8152 Fast Ethernet, Realtek Bluetooth,
   Super Top microSD reader, 2 USB hubs, USB audio/HID. **Zero
   instrument-class or controller-interface devices** (no
   USB-RS232/GPIB/LXI adapter beyond the CH340s, no vendor PID
   associated with any chamber/oven/temperature-controller maker).
2. **Serial-port identity** ([MEASURED — `udevadm info` on
   /dev/ttyUSB0, /dev/ttyUSB1, /dev/ttyACM0]): both CH340s enumerate
   as generic "USB Serial" (driver ch341); the ACM port is the Pi
   Debugprobe. These are the Meshtastic device console/debug ports and
   an RP2040 debug probe — none is a chamber controller. Kernel log
   ([MEASURED — `journalctl -k`]): both CH340s and the Debugprobe
   attached 2026-09-14 11:05:25, i.e. bench consoles, not chamber
   wiring.
3. **Legacy RS-232/PCI** ([MEASURED — `lspci`]): no serial/RS-232 PCI
   card exists; only Intel PCH I2C/HECI/SPI controllers (onboard,
   not chamber interfaces). `/dev/ttyS0..31` are 8250 legacy node
   placeholders ([MEASURED — `dmesg` shows no live 8250 port]);
   `/dev/gpib*` absent.
4. **No chamber-control software process** ([MEASURED — `ps aux`
   sweep for chamber/watlow/eurotherm/labview/scpi/modbus/oven/freezer]):
   zero hits; the only matches were the concurrent hermes dispatch
   sessions for this card and two sibling chamber cards.
5. **No chamber ever located** (committed prior reports, absence
   re-verified this session): chamber-ownership `4b3ec9b5` — "no
   chamber controller and no chamber-control/scheduling software
   exists on any record or on this host"; chamber-locate/identify/
   nameplate/manual cards all resultless (see Step 3).
6. **No chamber artifacts on disk** ([MEASURED — host-wide `find` for
   *chamber*/*controller* 23:16-23:18, plus repo/Docs/Downloads image
   sweep]): the only chamber-named paths are this repo's own bench
   REPORT directories and unrelated library/skill files (pip
   cachecontrol, boost odeint, zig headers, ESP32 bootsel-controller
   firmware — none a thermal-chamber controller). No chamber
   datasheet, manual, photo, config, or log exists anywhere.

## Step 2 — Setpoint command path: UNKNOWN (no interface exists)

There is no front panel, knob, menu, software, port, or protocol to
document, because no chamber exists to host one.

- **Physical path**: no chamber located (Step 1, items 5-6). Nothing
  was photographed — no interface exists and this host has no camera
  ([MEASURED — no /dev/video*]). PHOTOGRAPHS: NONE, reason: no subject
  + no camera.
- **Software path**: no chamber-command code exists anywhere. The only
  chamber-adjacent software on record, the fork's own
  `thermal_bench.py` (commit `d7ae93fa`), contains zero chamber-command
  surface ([MEASURED — `git show d7ae93fa:examples/passive_mapper/
  bench/thermal_bench.py` grepped for chamber/scpi/modbus/freezer:
  only the `--setpoints` argument labels appear]). Its `--setpoints
  "+25,+40,0,-20,-40,-55"` values are labels for the operator to
  realize physically ("Hardware is optional: every device-touching
  command accepts --simulate"); the script's serial class talks only
  to the DUT module (calshow/status/reset/cal/benchtx). **No SCPI, no
  Modbus, no register map, no setpoint-command path to any chamber
  exists on any record.**
- **Network path**: no network API evidence. This session's live
  network probe was DENIED by the operator mid-session and was not
  retried or routed around (standing constraint). Secondary evidence,
  from the committed chamber-holds report `72f3aab9` (its own session,
  verified then): ping sweep of 192.168.21.0/24 found one live host
  (192.168.21.200, SSH only), SCPI raw-TCP 5025 / VXI-11 1394 /
  7777 / 1234 closed on all reachable hosts. Treated as committed
  secondary evidence, not a fresh observation by this session.
- **No chamber-control/SCADA/scheduling software exists on the host**
  (chamber-ownership `4b3ec9b5` section B, absence re-verified this
  session via the ps/find sweeps in Step 1).

## Step 3 — Controller UI setpoint range + ramp programmability: UNKNOWN

- No controller UI exists (Step 1) and no chamber manual exists
  ([MEASURED — fleet state re-read this session: manual card
  `meshcore:t_a8b9d449` "Find chamber manual and cite setpoint range
  and ramp procedure" has decision `claim`, no result fields; zero
  `"result"` keys exist anywhere in `fleet_queue_state.json`]). No
  manual PDF is on disk (Step 1 item 6; the only datasheet PDF on any
  bench repo is the LR2021 module datasheet).
- Therefore: **enterable setpoint range: UNKNOWN. Ramp/rate
  programmability: UNKNOWN.** Whether the controller accepts only a
  target setpoint or programs ramps cannot be determined — there is
  no controller and no manual.
- Plan-side context (NOT controller evidence, scoping only): the fork
  README (`d7ae93fa`, verbatim) treats the cold side as "freezer
  (-18..-20 C), dry-ice + IPA bath (~-78 C), or a chamber" and warns
  "a kitchen freezer alone is not enough for a stratospheric
  profile", expecting "20-40 min per freezer setpoint for a true
  soak". This implies the protocol authors did NOT assume a
  programmable-ramp chamber either — but it says nothing about any
  real controller's UI. The chamber-ownership report (ambiguity 2)
  explicitly flags that "the chamber" may in practice be a kitchen
  freezer or dry-ice bath with no separate controller at all. That
  hypothesis remains unconfirmed: no freezer/chamber unit has been
  located by any dispatch.

## Step 4 — Per-setpoint selectability table (exactly four rows)

| target setpoint | selectable/enterable? | reason |
|---|---|---|
| +25 C | UNKNOWN | no chamber or controller interface exists on which the setpoint could be attempted; no manual stating an enterable range |
| 0 C | UNKNOWN | same — no interface, no manual |
| -20 C | UNKNOWN | same — no interface, no manual |
| -40 C | UNKNOWN | same — no interface, no manual |

No setpoint was commanded, entered, displayed, or reached this
session. Marking any row POSSIBLE or NOT POSSIBLE would violate the
task's "Do NOT assume a method works without evidence" rule — there is
no evidence in either direction.

## Step 5 — Source note for every claim

| claim | source |
|---|---|
| no controller/chamber exists on any record or host | this-session USB census + find sweep [MEASURED]; chamber-ownership reports `11e43b0a`/`4b3ec9b5` (committed, absence re-verified) |
| controller make/model | UNKNOWN — never captured; identify cards `t_a2f7f281`/`t_ffc911f6`/`t_b09424f1` resultless, controller card `t_fbfead68` decision cleared, no result [MEASURED — fleet state re-read] |
| serial devices are CH340 consoles + Pi Debugprobe | observed on host: lsusb + udevadm + journalctl [MEASURED] |
| no RS-232/GPIB hardware path | observed on host: lspci, dmesg, /dev sweep [MEASURED] |
| no chamber-control software/process | observed on host: ps sweep [MEASURED]; chamber-ownership `4b3ec9b5` §B |
| thermal_bench.py has no chamber-command surface | read at commit `d7ae93fa` this session [MEASURED — git show] |
| network: no SCPI/LXI instrument on LAN | committed chamber-holds report `72f3aab9` (secondary); fresh probe DENIED by operator this session — flagged as a gap, not routed around |
| no manual on record; manual card resultless | fleet state re-read [MEASURED]; `t_a8b9d449` decision `claim`, zero result keys in fleet state |
| enterable range / ramp programmability | UNKNOWN — no controller UI observed, no manual page exists ("manual page N" citations: NONE, manual never found) |
| per-setpoint selectability (all 4 rows) | UNKNOWN — no interface exists to test against |
| photos of interface | NONE — no interface exists AND no camera device on host [MEASURED — no /dev/video*] |
| fork README freezer/chamber scoping quotes | vendor fork commit `d7ae93fa`, read by SHA this session |

## Honesty / gap section

1. No chamber was located, so the required direct physical inspection
   was impossible. No data was invented to fill the gap.
2. No photograph could be taken: no subject, and this host has no
   camera device.
3. This session's live network instrument sweep was denied by the
   operator; the network claims above rest on the committed
   chamber-holds report `72f3aab9` as written secondary evidence, and
   are labelled as such.
4. No outbound channel exists (standing no-outbound-probe
   constraint), so the operator (Felix) could not be asked to point
   at a chamber. Per the fork README (`d7ae93fa`, verbatim): "This is
   bench work for the operator (Felix), not for an agent... No agent
   host in this fleet has the module attached and none can put a
   board in a freezer."
5. Board churn this session: `t_a2f7f281` (identify) and `t_a8b9d449`
   (manual) hold decision `claim`; `t_fbfead68` (controller
   inspection) decision field cleared; zero result fields exist for
   any of them in `fleet_queue_state.json` [MEASURED].

## What unblocks this task (operator-side, not agent-side)

1. Physically locate the chamber/freezer and produce the nameplate
   survey (cards `t_ffc911f6` / `t_a2f7f281` / `t_b09424f1`, all
   resultless today). Its controller make/model and front-panel
   photo then fall out of the same visit.
2. Obtain the chamber manual (card `t_a8b9d449`): enterable
   setpoint range and ramp programmability are manual/UI questions.
3. Connect the chamber to a fleet host (USB serial, RS-232, GPIB, or
   LXI/ethernet) and document its command interface (SCPI commands,
   register map, or proprietary protocol).
4. Then re-run this card: classify the controller, photograph the
   interface, walk the setpoint command path, and fill the
   four-row selectability table with POSSIBLE / NOT POSSIBLE backed
   by observation.

## Evidence freshness

All host-side reads (lsusb, udevadm, journalctl, dmesg, lspci, ps,
find, fleet-state re-read, git show d7ae93fa) were performed this
session, 2026-09-14 23:16-23:26 local. Prior reports cited
(chamber-ownership `4b3ec9b5`/`11e43b0a`, chamber-holds `72f3aab9`,
chamber-reservation `7d9227a1`, ramp-feasibility `79ea692e`,
condensation-risk `65c9c3df`) were spot-verified against live
board/disk state rather than trusted blindly.