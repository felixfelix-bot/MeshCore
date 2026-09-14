# Bench + chamber occupancy audit and booking-system-of-record reconciliation

Task: `meshcore:t_9782fb4c` — "Establish current occupancy and locate/reconcile
the booking system of record." Dispatch session: node `dq05`, run_id
`dq05-1789372448`, PID 2900406 (lock file
`~/.hermes/bot/.locks/meshcore:t_9782fb4c.json`, verbatim:
`{"node": "dq05", "run_id": "dq05-1789372448", "ts": 1789372448.9145417,
"pid": 2900406}` = 2026-09-14T09:54:08+02:00; `ps` lstart 09:54).
Host: `c03rad0r-DQ05proplus`. Audit executed 09:58-10:26 local (UTC+2),
Monday 2026-09-14 (`date -Is` = 2026-09-14T09:58:45+02:00).

Session window: **start 2026-09-14T09:54:08+02:00 (lock acquisition), end =
session completion** — session-scoped, same semantics as every prior bench
card (auto-release on session death; no fixed end time exists to overlap with).

---

## (a) Current occupancy

### Bench — FREE (nobody, no run) — but vacuously: the DUT is not attached

- Who: **nobody**. What run: **none**. Start/end: none. Evidence source:
  in-person observation of this host (the only fleet host on this desk),
  fresh this session:
  - `~/.hermes/peripheral_locks/` — the OS-enforced bench-hardware mutex
    registry (balloon v3, the only hardware-occupancy system on the host,
    documented at `~/repos/balloon/tools/balloon-board-lock.py:29-30,83`:
    "LOCK FILES: ~/.hermes/peripheral_locks/balloon-{tx,rx,board-a,board-b,
    board-c}.lock") is **EMPTY — 0 files, no theft log ever created**
    (`ls` 09:58 and again after write-up; `wc -l` = 0; THEFT-LOG and
    board-lock-theft.log both nonexistent).
  - `lsof /dev/ttyUSB0 /dev/ttyUSB1 /dev/ttyACM0` 09:58: **no holders**.
    `ps` sweep for minicom/screen/picocom/serial/soak/calshow: only an
    unrelated 2026-09-04 qemu `startos-test` VM and an idle `screen`.
  - USB bus census (`lsusb` 09:58): 2x CH340 serial (`1a86:7523`), Raspberry
    Pi Debugprobe (`2e8a:000c`, on `/dev/ttyACM0`), RTL8152 Ethernet, microSD
    reader, hubs — **no ESP32-C3/Espressif/CP210x, no LR2021 module**. The
    meshcore bench DUT is attached to no fleet host (matches the fork README
    quote preserved in `bench/chamber-reservation/REPORT.md`, commit
    `7d9227a1`: "No agent host in this fleet has the module attached").
- Expected end: N/A — nothing running to end.

### Chamber — occupancy UNKNOWN; no occupancy record exists anywhere

- Who/what run/start/end: **no record exists** in any candidate system
  (calendar: 0 events; board: no occupancy semantics — see (b); locks:
  empty; no logbook; no controller process). The chamber has never been
  located or identified on record: `t_ffc911f6` (physically inspect
  nameplate) has claims from earlier today but `decision=none` and no worker
  session; `t_a2f7f281` (make/model/serial) and `t_fbfead68` (controller
  classification) were claimed by the scheduler for dq05 only at
  10:12:31+02:00 (claims ts 1789373551.46, `decision_reason`: "light
  headroom 0.25") with **no lock file and no worker session started** as of
  10:26 — so no inspection result exists yet. No chamber-controller process
  is running (`ps` sweep for watlow/testequity/tenney/espec/cascade/labview:
  zero hits), and no candidate chamber serial device beyond the two CH340s
  and the debug probe is on the bus.
- Evidence source: absence of any record, verified by fresh sweeps this
  session (host-wide find for booking/calendar/logbook systems, process
  sweep, USB census, board card states). Occupancy is UNKNOWN, not "free".

## (b) Candidate systems of record — inventory and reconciliation

All candidates found, with maintainer, currency, and authority assessment
(every candidate checked fresh this session, 09:58-10:26):

1. **Local Evolution calendar** —
   `~/.local/share/evolution/calendar/system/calendar.ics`.
   Maintainer: the desktop user (c03rad0r) via GNOME/Evolution. Currency:
   **stale — 0 VEVENTs, untouched since 2026-03-10**
   (`X-EVOLUTION-DATA-REVISION:2026-03-10T23:01:44`, mtime 2026-03-11
   00:01:44; full content is just the 6-line VCALENDAR shell). No GNOME
   Online Accounts (`~/.config/goa-1.0/` absent), no other .ics/CalDAV
   config host-wide. Authoritative? **No** — empty for 6+ months, never used
   for lab resources.
2. **Fleet board** — `~/.hermes/bot/fleet_queue_state.json` (mtime 10:00:08
   today, live). Maintainer: `hermes-orchestration` fleet scheduler
   (`scripts/fleet/fleet_scheduler.py`) + actor cobrador as card creator
   (every meshcore card carries `"actor": "cobrador"`). Currency: **current**
   (claims written as recently as 10:12:31). Authoritative for *work
   dispatch* — but **structurally NOT a booking system**: programmatic
   `jq paths(scalars)` walk of all keys finds only `{node, ts}` (plus
   `headroom` on some claims) in `running[]`/`claims[]`; **zero keys matching
   start/end/window/duration/book/reserv/schedule/slot anywhere in the
   schema** (only hits are `.ts` timestamps and the unrelated
   `headroom` field). A card cannot express a time window, so no
   reservation can be recorded there — only work claims.
3. **Balloon v3 peripheral lock registry** — `~/.hermes/peripheral_locks/`.
   Maintainer: balloon tooling (v3 hard device lock; docs also in
   `~/repos/e80-bench/AGENTS.md`: "All 3 ESP32-S3 boards are shared
   resources... enforced by a **hard device lock** (chmod 000 on
   /dev/ttyACMx)"). Currency: live but **EMPTY** (0 lock files). Semantics:
   session-scoped mutex, auto-release — not windowed reservations.
   Authoritative? **Yes, for live hardware occupancy while held** — it is
   the only OS-enforced occupancy mechanism. It currently holds nothing,
   and it cannot represent future windows.
4. **Task lock files** — `~/.hermes/bot/.locks/*.json` +
   `.fleet_slots/*.slot`. Maintainer: scheduler/bot. Live (my own lock is
   one). Session markers only, `{node, run_id, ts, pid}` — no windows. Not
   a booking system.
5. **meshcore bench/ campaign record (this repo)** — git-committed
   `bench/*/REPORT.md`, 10 reports, latest commit `c4be4400` 08:18 today.
   Maintainer: the fleet workers themselves (this campaign). Currency:
   current. This is the **only place a reservation-like artifact has ever
   been recorded on this host**: `bench/chamber-reservation/REPORT.md`
   (commit `7d9227a1`, 07:40 today) holds the named REQUESTED/UNCONFIRMED
   reservation block for the prior session. It is a written record of
   claims, not a booking system (no scheduler enforces it).
6. **buzz/nostr bridge** — `~/.hermes/bot/buzz_responder_state.json` (mtime
   10:18) / `buzz_relay_bridge_state.json`. Maintainer: the bot. State holds
   only event hashes and a relay cursor — **no message content, no booking
   chatter**. Receive/echo infrastructure, not a booking system.
7. **stackstr SCHEDULE.md** (`~/hermes-orchestration/state/kanban/boards/
   stackstr/SCHEDULE.md`) — surfaced by the sweep, examined and excluded:
   another board's work-DAG ("SCHEDULING ONLY — all tasks blocked +
   unassigned"; a dependency table, no time slots). Not a booking system,
   not for meshcore resources.
8. **FLASH-QUEUE.md** — cited by balloon/e80 AGENTS.md as the flash
   approval record; `~/repos/balloon-fresh` **does not exist** on this host
   and no FLASH-QUEUE file exists anywhere (find across ~/repos,
   ~/worktrees, ~). Nonexistent here.
9. **Not found at all**: no spreadsheet (.ods/.xlsx/booking CSV), no wiki
   directory, no physical logbook file, no Matrix/Slack configs
   (`~/.config/matrix*`, `slack*`, `.element` all absent), no chamber
   controller software (process sweep zero hits).

**Recommendation — system(s) of record.** There is no single booking
system; the landscape is a **void with fragments**, and the honest
reconciliation is a split one:

- For **live hardware occupancy**: the balloon v3 registry
  (`~/.hermes/peripheral_locks/`) is authoritative — it is the only
  OS-enforced mechanism, and its emptiness is real evidence the bench is
  unclaimed right now. Treat its lock files (not calendar entries) as the
  occupancy signal.
- For **work claiming/scheduling**: the fleet board is authoritative (it
  is what actually dispatches bench-cluster work), with the explicit
  caveat that it cannot hold time windows.
- For **written reservations**: no system exists. The closest thing is this
  repo's `bench/` campaign record, which should be treated as the interim
  written ledger (precedent: 7d9227a1), with confirmation necessarily
  out-of-band from Felix (operator) — the only party who can perform or
  authorize physical bench/chamber work (ownership attribution and the
  authorizer-operator duality are documented in `bench/chamber-reservation/
  REPORT.md` (a)/(c); sibling ownership cards t_c1c07af9/t_d601da74 are
  running right now and may supersede — no result from them is on record
  yet).

## (c) Conflicting reservations overlapping our window

**NONE FOUND — in any candidate system.** Specifically:

- Calendar: 0 VEVENTs — nothing to conflict.
- Fleet board: no window semantics exist, so no reservation can be
  recorded; the concurrently-running meshcore cards (t_c1c07af9 chamber
  owner-ID, t_d601da74 bench owner-ID — both `running[]` on dq05 since
  ~09:58, locks at 09:54:16/09:58:25) and the 10:12:31-claimed physical-ID
  cards (t_a2f7f281, t_fbfead68) are **read-only investigative cards that
  claim no physical resource window**. They compete for worker slots, not
  for the bench. The 4th live worker slot (PID 2926314, started 10:12) is
  on an unrelated board (`cvm_tx_listener` stubs, different repo).
- Lock registry: empty.
- bench/ record: the only reservation-like entry is our own campaign's
  REQUESTED/UNCONFIRMED block (7d9227a1) whose session is **dead** — its
  lock file `~/.hermes/bot/.locks/meshcore:t_0d0fe29c.json` is gone and
  PID 2641304 no longer exists (`ps` checked). No live holder.
- No logbook/wiki/Slack/channel record exists to hold a conflict.

Owner/start/end/source table for the only adjacent claims:

| claim | owner | start | end | source |
|---|---|---|---|---|
| prior reservation REQUEST (bench+chamber) | dq05 session dq05-1789363387 (dead) | 2026-09-14T07:23:07+02:00 | session-scoped (session ended; lock file removed) | bench/chamber-reservation/REPORT.md commit 7d9227a1 |
| chamber owner-ID card t_c1c07af9 (investigative, no resource claim) | dq05 worker PID 2900523 | 2026-09-14T09:54:16+02:00 | session-scoped | running[] ts 1789372456/1789372705 + .locks |
| bench owner-ID card t_d601da74 (investigative, no resource claim) | dq05 worker PID 2906308 | 2026-09-14T09:58:25+02:00 | session-scoped | running[] ts 1789372705 + .locks |
| chamber physical-ID t_a2f7f281 / controller t_fbfead68 | claimed by scheduler for dq05, **no worker started** | claimed 2026-09-14T10:12:31+02:00 | unbounded (undispatched) | claims[] ts 1789373551.46, decision_reason "light headroom 0.25", no .locks entry |

## (d) Reconciliation anomalies

1. **Multiple candidates, none a booking system (the core anomaly).** Six
   live candidate systems were found (calendar, fleet board, lock registry,
   task locks, bench/ git record, buzz bridge) — but not one of them can
   record a time-windowed reservation. Disagreement between them is
   impossible because none of them says anything about time windows at all.
   Verbatim statement of the disagreement-avoidance rule applied: empty
   calendar + empty locks + windowless board were treated as "no booking
   exists in any system", NOT as "resources are free" (occupancy of the
   chamber remains UNKNOWN because no record of any kind exists).
2. **Board state changed mid-audit, reversing prior recorded decisions.**
   The 07:40 report (7d9227a1) recorded the chamber locate/ID cards as
   `decision: skip` ("the chamber has never even been located or
   identified"). Fresh reads today show `t_ffc911f6` decision=**none**
   (skip cleared; stale claims from ~04:56 and ~05:47 remain in claims[]),
   and `t_a2f7f281`/`t_fbfead68` decision=**claim** (10:12:31). The skip
   verdicts were silently reversed on the board — the chamber-identity
   picture is in flux during our window and no inspection result exists yet.
3. **Board self-inconsistency persists**: our card and both ownership cards
   sit in `running[]` (with node+ts) while their `tasks{}` entries carry no
   decision/status fields (decision=none) — running-vs-undispatched
   discrepancy, same class as anomaly 2 in 7d9227a1, still unfixed.
4. **Evidence decay on the fork-side ledger (blind spot).** The prior
   session (07:23-07:40 today) read the bench kit and RESULTS.md ledger
   (author column) from `felixfelix-bot/MeshCore` branch
   `feat/passive-mapper` via git. This session, that fork is **no longer
   reachable from this host**: no clone exists (find across ~/repos,
   ~/mirrors, ~/worktrees), this repo's remote is
   `github.com/c03rad0r/MeshCore.git` with no passive-mapper ref, and no
   packed-ref holds it. If Felix records bench occupancy/results in that
   fork's RESULTS.md, this host cannot see it — the verbatim README quotes
   survive only in the committed report 7d9227a1. Any reconciliation
   against the fork ledger is impossible from here right now.
5. **Lock-map vs physical bus mismatch (carried forward, re-verified).**
   `balloon-board-lock.py` maps resource c3-a to `/dev/ttyACM0`, but
   `/dev/ttyACM0` is the Raspberry Pi Debugprobe (lsusb 2e8a:000c this
   session). Anyone acquiring c3-a per the docs would hard-lock the debug
   probe. Also `~/repos/balloon-fresh` (the path the AGENTS.md mutex docs
   cite) does not exist on this host; the tool actually present is
   `~/repos/balloon/tools/balloon-board-lock.py`.
6. **Deadman flapping continues**: hourly deadman-notify for an
   unreachable peer ("?", ssh_nudge=unreachable), latest 1789372916 =
   10:21:56+02:00 today (`fleet_interventions.jsonl`).
7. **Empty registry ≠ free bench forever**: the bench reads FREE only
   because no DUT is attached; the chamber reads UNKNOWN. Neither verdict
   would change if someone booked a window in a system this host cannot see
   (see anomaly 4) — flagged rather than resolved.

## Verbatim evidence appendix (commands run this session, all 2026-09-14)

- `date -Is` → `2026-09-14T09:58:45+02:00`; host `c03rad0r-DQ05proplus`.
- `ls -la ~/.hermes/peripheral_locks/` → empty dir (total 8; `.` Aug 28).
  `ls ... | wc -l` → 0. THEFT-LOG / board-lock-theft.log → nonexistent.
- `lsof /dev/ttyUSB0 /dev/ttyUSB1 /dev/ttyACM0` → no holders (only
  fuse.portal/docker stat warnings, unrelated).
- `lsusb` → no Espressif/CP210x; `2e8a:000c` RP Debugprobe, 2x `1a86:7523`
  CH340, `0bda:8152` RTL8152, `14cd:1212` microSD.
- `cat ~/.local/share/evolution/calendar/system/calendar.ics` → 6-line
  shell, 0 VEVENTs, `X-EVOLUTION-DATA-REVISION:2026-03-10T23:01:44.458802Z(1)`;
  mtime 2026-03-11 00:01:44.457880886 +0100.
- `jq paths(scalars)` over `fleet_queue_state.json` → running/claims entries
  are `{node, ts[, headroom]}` only; regex `start|end|window|dur|book|reserv|
  sched|slot|time` → only `.ts` and `headroom` hits.
- `jq '.running'` → 9 cards; meshcore: t_c1c07af9, t_9782fb4c, t_d601da74
  all node dq05 ts 1789372456/1789372705 (= 09:54/09:58 local).
- locks dir: meshcore:t_9782fb4c.json (ts 1789372448.9145417, pid 2900406),
  t_c1c07af9.json (1789372456.1975026, pid 2900523), t_d601da74.json
  (1789372705.0269132, pid 2906308); plebeian-my-prs:t_0240be0f.json.
  No t_0d0fe29c lock; PID 2641304 absent from ps.
- `jq '.claims'` → t_a2f7f281 and t_fbfead68 each
  `[{"node":"dq05","ts":1789373551.4564211,"headroom":0.25}]` (=10:12:31);
  card records show `decision: "claim"`, `decision_reason: "light headroom
  0.25"`; t_ffc911f6 claims ts 1789354599.37/1789357623.88, decision none;
  t_a8b9d449 decision "skip".
- `ps` → PIDs 2900406/2900523 (09:54), 2906308 (09:58:24) = this + two
  sibling meshcore workers; 2926314 (10:12) = cvm_tx_listener (unrelated).
- find sweeps (60s-bounded, /home /var /srv /opt + ~ for
  *.ods/*.xlsx/*book*.csv/*bench*.csv/*chamber*.csv): zero booking systems;
  wiki dirs: none. FLASH-QUEUE: nonexistent host-wide.
- `cat buzz_responder_state.json / buzz_relay_bridge_state.json` → hashes,
  seen/answered lists, cursor `orange:all` 1789369804; no message content.
- `grep -n LOCK_DIR ~/repos/balloon/tools/balloon-board-lock.py` → line 83
  `LOCK_DIR = Path.home()/".hermes"/"peripheral_locks"`; lines 29-30 lock
  file paths; e80-bench/AGENTS.md "BOARD ACCESS — HARD MUTEX LOCK (v3)".
- `tail fleet_interventions.jsonl` → deadman-notify entries, latest ts
  1789372916.13 (=10:21:56+02:00).
- Prior-record citations: bench/chamber-reservation/REPORT.md (commit
  7d9227a1, 07:40), bench/soak-rollup/REPORT.md (commit c4be4400, 08:18),
  git log this repo, branch main, not pushed.