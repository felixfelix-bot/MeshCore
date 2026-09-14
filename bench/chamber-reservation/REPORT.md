# Bench + thermal chamber: ownership, occupancy, and reservation request

Task: `meshcore:t_0d0fe29c` — "Identify bench/chamber owner and secure a named,
attributable reservation for the session."
Dispatch session: node `dq05`, run_id `dq05-1789363387`, PID 2641304
(lock file `~/.hermes/bot/.locks/meshcore:t_0d0fe29c.json`, verbatim:
`{"node": "dq05", "run_id": "dq05-1789363387", "ts": 1789363387.197096, "pid": 2641304}`
= 2026-09-14T07:23:07+02:00).
Host: `c03rad0r-DQ05proplus`. Worker profile: worker-heavy. Report compiled
2026-09-14 07:40+02:00.

---

## (a) Owners / custodians

### Bench — Felix (GitHub `felixfelix-bot`, commits as
`Felix <30139850+felixfelix-bot@users.noreply.github.com>`) — confidence HIGH

- Source 1 (primary, verbatim quote): firmware fork
  `felixfelix-bot/MeshCore` branch `feat/passive-mapper` @ `d7ae93fa`,
  `examples/passive_mapper/bench/README.md`, section "What has to be measured,
  and by whom" (read fresh this session via `git show origin/feat/passive-mapper`):
  > "This is **bench work for the operator (Felix), not for an agent**: it needs a
  > NiceRF LR2021 module, a way to hold it at temperature for hours, and a second
  > MeshCore node as a reference transmitter. No agent host in this fleet has the
  > module attached and none can put a board in a freezer."
  The bench kit (`thermal_bench.py`, `RESULTS.md` ledger with an `operator`
  column) was authored entirely by Felix (`4a25db04` and `d7ae93fa`, both
  2026-09-11, author Felix).
- Source 2 (corroboration): the OS-enforced bench-hardware mutex for the same
  LR2021 boards, `~/repos/balloon/tools/balloon-board-lock.py` (v3), resource map
  verbatim: `c3-a — ESP32-C3 + LR2021 board A (MAC b0:a6:04:00:96:dc,
  /dev/ttyACM0)`, `c3-b — ... board B`. Git authorship of that tool:
  9 commits Felix, 1 c03rad0r. The balloon AGENTS.md additionally names the
  `balloon-hermes` orchestrator group as approval authority for *flashing* those
  boards ("NO flashing without orchestrator (balloon-hermes) approval").
- Source 3 (corroboration): peer event log `~/.hermes/bot/peers/events-cobrador.jsonl`
  (plain grep) shows Felix as the standing gate authority in this fleet:
  "FELIX-GATE: task starts only after Felix merges #356", "FELIX-GATE to be
  opened only after pitch approval...", etc.

### Thermal chamber — Felix (same person) — confidence MEDIUM

- No chamber owner/custodian is on record ANYWHERE: the fleet's own ownership
  cards `t_c1c07af9` ("Identify the thermal chamber owner/custodian with named
  source and confidence") and `t_d601da74` ("Identify the bench owner/custodian")
  are both **undispatched** (`fleet_queue_state.json`, read 07:30-07:40 today).
  The chamber-identification cards (`t_ffc911f6` physically locate, `t_a2f7f281`
  make/model/serial, `t_fbfead68` controller, `t_a8b9d449` manual) all carry
  `decision: skip` — the chamber has never even been located or identified.
- Attribution to Felix is by operator-scoping, not a named record: the only
  chamber-consuming protocol on record (the freezer/dry-ice sweep that the bench
  kit's `RESULTS.md` row marks "pending: needs the freezer/dry-ice sweep, see
  the card") is the one the fork README reserves to Felix, and the README
  explicitly states no agent "can put a board in a freezer". Confidence MEDIUM
  because it is inference from authorship + absence of any other candidate.

### Fleet-board scheduling authority (who can dispatch/authorize bench-cluster
work on the board) — cobrador — confidence HIGH

- `meshcore:t_0d0fe29c` card created by actor **cobrador** (card record,
  `fleet_queue_state.json`); `~/.hermes/bot/peers/cobrador.json` peer record;
  `fleet.json` shows cobrador as the only peer node (hosts 192.168.2.9 /
  cobradorwave.local, user c03rad0r). The lease record
  `~/.hermes/bot/.fleet_lease/cobrador.json` (ts 2026-09-11T13:12:52) names
  cobrador as fleet operator. Note: cobrador is a *node/actor*, the same human
  (c03rad0r) on the other machine — not a second bench owner.

## (b) Occupancy status

- **Bench (this host): FREE right now, but vacuously so — the meshcore bench
  DUT is not attached to any fleet host.**
  - `~/.hermes/peripheral_locks/` (the balloon v3 lock registry, the only
    hardware-occupancy system of record on this host) is **EMPTY** — zero
    `.lock` files, no theft log (`ls -la` 07:32 and 07:40 today).
  - `lsof /dev/ttyUSB0 /dev/ttyUSB1 /dev/ttyACM0` at 07:31 and 07:40: no
    holders. No minicom/screen/picocom/serial processes (`ps` sweep).
  - BUT the USB bus census (udevadm/lsusb, this session) shows only
    2x CH340 USB-serial (`1a86:7523`), a Raspberry Pi Debugprobe on
    `/dev/ttyACM0`, RTL8152 Ethernet, microSD reader — **no ESP32-C3 /
    Espressif / CP210x device, no LR2021 board attached**. This matches the
    fork README: "No agent host in this fleet has the module attached".
- **Chamber: occupancy UNKNOWN — no occupancy record exists at all.** There is
  no chamber calendar, logbook, or controller feed anywhere on this host
  (host-wide find for *calendar/booking/reserv/logbook/schedule* systems found
  only the empty Evolution calendar; see (e)). Chamber-locate cards were all
  skipped, so even its location is unknown — occupancy cannot be assessed.

## (c) Booking status: **NO BOOKING EXISTS**

The exact statement required: **NO BOOKING EXISTS** — neither for the bench nor
for the chamber, for this or any other window.

Proof that no booking system of record exists (all checked this session):
1. Local calendar `~/.local/share/evolution/calendar/system/calendar.ics` —
   6 lines, **0 VEVENTs**, untouched since 2026-03-10 (verbatim full content:
   `BEGIN:VCALENDAR / CALSCALE:GREGORIAN /
   PRODID:-//Ximian//NONSGML Evolution Calendar//EN / VERSION:2.0 /
   X-EVOLUTION-DATA-REVISION:2026-03-10T23:01:44.455802Z(1) / END:VCALENDAR`).
   GNOME Online Accounts absent (`~/.config/goa-1.0/` missing). No other
   calendar/WebDAC/CalDAV config found.
2. Fleet board `~/.hermes/bot/fleet_queue_state.json` — programmatic recursive
   walk of all 400 cards + running/claims/advertised/hold_denied maps: **zero
   time-like keys** (no start/end/window/duration/book/reserv/schedule/slot
   fields exist anywhere in the schema). The board is a work-queue, not a
   booking system; it cannot hold a reservation.
3. `~/.hermes/peripheral_locks/` — empty (see (b)); the only session-scoped
   hardware claim system holds nothing.
4. No wiki/logbook/labbook directory exists host-wide (find across /home,
   /var, /srv, /opt).
5. The balloon flash-approval queue (`FLASH-QUEUE.md`, cited in balloon
   AGENTS.md as the written approval record) does **not exist on this host**
   (find across all repos: no match; `~/repos/balloon-fresh` absent).

### Who must authorize a booking

- **Felix (`felixfelix-bot`)** — bench + chamber operator (see (a)). He is the
  only party who can perform or authorize the physical bench/chamber work, and
  the only party who could confirm a chamber slot. No reachable confirmation
  channel exists from this host for this session: the buzz/nostr bridge
  (`buzz_responder.json`: relay wss://relay.orangesync.tech, operator_pubkey
  1a31189f…) is receive/echo infrastructure, and this worker is prohibited
  from outbound probes (standing constraint, honored).
- **cobrador** — fleet operator/peer node; authorizes *scheduling* (dispatch of
  the bench-cluster cards) on the fleet board.

### Named, attributable reservation REQUEST (recorded here; UNCONFIRMED)

This file is the attributable artifact, committed to the meshcore bench campaign
record (the same system of record as the four prior bench dispatch REPORTs,
`bench/atcut-fit|thermal-lag|thermal-hysteresis|selfcal-ema-tau/REPORT.md`).

```
RESERVATION REQUEST — meshcore thermal bench + chamber (UNCONFIRMED)
resource:   meshcore thermal bench — SkyMapper Board A (NiceRF LR2021,
            balloon lock resource c3-a) + reference TX node;
            thermal chamber (make/model unknown — see anomaly 3)
requester:  dq05 dispatch session dq05-1789363387 (PID 2641304),
            on behalf of fleet operator cobrador (card meshcore:t_0d0fe29c)
window:     start 2026-09-14T07:23:07+02:00 (task-lock acquisition);
            end = dispatch session completion — session-scoped, whole-session,
            no partial window (same semantics as the balloon v3 lock sentinel:
            held for the session's lifetime, auto-released on session death)
purpose:    owner/occupancy verification + bench/chamber session for the
            passive_mapper calibration campaign (freezer/dry-ice sweep
            prerequisites recorded in bench/*/REPORT.md)
authorizer: Felix (operator) — confirmation outstanding;
            fleet-side scheduling: cobrador
status:     REQUESTED, NOT CONFIRMED — no booking channel exists (see (c) 1-5);
            no verbal assurance of any kind was offered or received
```

## (d) Interruption risks

- **Sibling soak-evidence cards dispatched into the same void, mid-session** —
  `meshcore:t_b0a5312a` ("Capture die-temp soak evidence at 0 C") and
  `meshcore:t_3a34bea7` ("... at +25 C") entered `running[]` on dq05 at
  07:30:18+02:00, i.e. DURING this session, alongside this card
  (`fleet_queue_state.json` 07:40). Likelihood: certain (already observed);
  impact: medium — they cannot occupy the bench (no hardware attached) but they
  multiply UNVERIFIED/no-result outcomes and compete for dq05 worker slots.
- **c3-a lock-node collision (documented device node is the WRONG device)** —
  `balloon-board-lock.py` maps c3-a to `/dev/ttyACM0`, but `/dev/ttyACM0` is
  currently the Raspberry Pi Debugprobe (udevadm ID_SERIAL verified this
  session). Anyone running the documented `acquire c3-a` would hard-lock
  (chmod 000) the debug probe, not an LR2021 board. Likelihood: medium
  (triggers whenever bench work starts from the docs); impact: high (breaks the
  debug probe; phantom lock on an absent board).
- **Bench DUT not attached to any fleet host** (USB census + fork README).
  Likelihood: certain blocker; impact: total for any physical soak/measure work
  this session.
- **Chamber unidentified and unevidenced** — locate/ID cards skipped
  (`t_ffc911f6`, `t_a2f7f281` decision: skip); controller type undocumented
  (`t_4e41856d` undispatched); **no calibration record exists** for the chamber
  or any bench instrument (cal-audit cards `t_71af23c2` skip, `t_0fc2adec`
  undispatched) — a calibration-lapsed chamber cannot be ruled out.
  Likelihood: unknown; impact: high (any soak evidence would be inadmissible).
- **Fleet deadman flapping** — `fleet_interventions.jsonl` shows hourly
  deadman-notify for an unreachable peer ("?", ssh_nudge=unreachable), latest
  ~07:39 today; arbiter state shows dq05 `bad_streak: 25` (vs cobrador
  clean_streak 1). Likelihood: ongoing; impact: medium — arbiter pressure on
  dq05 could freeze/quarantine this node mid-session.
- **Weekend/holiday/access policy** — today is Monday 2026-09-14 (verified via
  `date`). No badge-access, HVAC, or power-maintenance calendar exists anywhere
  on record (see (c)), so these risks cannot be assessed — flagged as UNKNOWN
  rather than assumed absent.

## (e) Anomalies

1. **Two divergent copies of the fleet board (candidate systems of record).**
   dq05's `fleet_queue_state.json` (mtime 07:40 today) vs cobrador's copy;
   `fleet_plan_cobrador.md` records "state-sync failed" and
   "resource-monitor flapping" for dq05. The board I read may diverge from
   cobrador's authoritative copy. Reconciled as far as possible from dq05;
   cobrador-side state not readable this session (no outbound probes).
2. **Board self-inconsistency:** this task `meshcore:t_0d0fe29c` appears in
   `running[]` (07:30:18) while its card in `tasks{}` shows no
   decision/assignee fields — undispatched-vs-running discrepancy.
3. **Chamber scheduled against phantom identity:** ~25 chamber cards exist on
   the board targeting a chamber whose make/model/serial/location have never
   been captured (all locate/ID cards skipped). Booking an unlocated resource
   is structurally impossible.
4. **Empty calendar ≠ free:** the only calendar on the host has had 0 events
   since March 2026 — absence of entries was treated as absence of a booking
   *system*, not evidence of availability.
5. **Lock-map vs physical bus mismatch** (risk 2 above, also an anomaly):
   documented c3-a device node currently hosts an unrelated debug probe.
6. **The fleet has never established chamber/bench ownership before this
   report:** the sibling ownership cards (`t_c1c07af9`, `t_d601da74`) are
   undispatched; this file is the first named answer on record.
7. **Authorizer-operator duality:** Felix is both the authorizing gate
   ("FELIX-GATE", events log) and the performing operator ("bench work for the
   operator (Felix)") — no delegation path for bench/chamber work exists on
   record, which is why no agent-side booking can ever be *confirmed* here,
   only requested.