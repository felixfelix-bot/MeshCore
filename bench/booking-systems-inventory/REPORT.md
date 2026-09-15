# Booking-system candidate inventory: bench + thermal chamber

Task: cold-start inventory of EVERY system that could plausibly hold a
reservation for the meshcore thermal bench (SkyMapper Board A, NiceRF
LR2021, balloon lock resource c3-a + reference TX node) or the thermal
chamber. No occupancy or conflict analysis — inventory only.

Session: 2026-09-15T15:05:56+02:00, host `c03rad0r-DQ05proplus`, worker
profile worker-heavy. Cold start: every positive claim re-verified
against raw source this session; prior-session claims cited only as
committed artifacts with their evidence quoted.

---

## HEADLINE: no booking system exists for the bench or chamber; 12 candidate systems inventoried

Twelve candidates were found and inspected. **NONE can record a
time-windowed reservation for the bench or chamber.** Zero hold any
bench/chamber reservation. Several are authoritative for adjacent
concerns (live board occupancy, flash approval, work dispatch,
completed-run ledger) — recorded below because they are the systems a
reservation could plausibly live in, per the task.

**MULTIPLICITY ANOMALY (explicit flag, per task instructions):** there
is no multiplicity of booking systems, but there IS a multiplicity of
*flash-approval queues* — three copies of FLASH-QUEUE.md exist
(balloon, balloon-e80bench, e80-bench). They are near-duplicates but
NOT identical: the balloon copy's queue is EMPTY (and is the one whose
resource map governs the meshcore bench boards c3-a/c3-b); the two E80
copies carry three completed flash-approval rows for a DIFFERENT bench
(the E80 range-test bench). Additionally the balloon AGENTS.md
(:47-48,54) still points at `~/repos/balloon-fresh/.../FLASH-QUEUE.md`,
which does not exist on this host — a dangling pointer. Do not silently
resolve these into one; reconcile later.

---

## Candidate 1 — Evolution local calendar (the only calendar on the host)

- **Name:** GNOME/Evolution local calendar (system calendar)
- **Maintainer/owner:** the desktop user (c03rad0r) via GNOME/Evolution;
  no shared/lab account exists — `~/.config/goa-1.0/` is absent (checked
  2026-09-15, fresh `ls ~/.config` this session shows no CalDAV/WebDAV/
  nextcloud config anywhere)
- **Access path:** `~/.local/share/evolution/calendar/system/calendar.ics`
  (+ tasks shell `~/.local/share/evolution/tasks/system/tasks.ics`)
- **Currency:** STALE — 0 VEVENTs (grep -c BEGIN:VEVENT = 0, this
  session), 0 VTODOs; file is a 6-line VCALENDAR shell; mtime
  **2026-03-11 00:01:44 +0100** (stat this session). X-EVOLUTION-DATA-
  REVISION:2026-03-10T23:01:44Z (quoted in committed
  bench/calendar-booking-mining/REPORT.md:40-49).
- **Judgement:** NOT authoritative — the only calendar host-wide is
  6+ months stale and empty; no lab resource has ever been booked here.
- Source: file read + `grep -c` + `stat -c '%y'` this session.

## Candidate 2 — Fleet board (`fleet_queue_state.json`) — work dispatch queue

- **Name:** Hermes fleet task queue (fleet scheduler state)
- **Maintainer/owner:** hermes-orchestration fleet scheduler
  (`scripts/fleet/fleet_scheduler.py`) + actor **cobrador** as card
  creator (every meshcore card carries `"actor": "cobridor"`);
  fleet.json names cobrador as the only peer node (hosts
  192.168.2.9 / cobradorwave.local, user c03rad0r)
- **Access path:** `~/.hermes/bot/fleet_queue_state.json` — **ACCESS
  DENIED THIS SESSION** (operator denied a fresh read 2026-09-15
  15:0x +02:00; also denied 2026-09-15 earlier per commit 5da7bef2
  message "fleet.json read operator-denied mid-session"). Structure
  documented in committed
  bench/occupancy-booking/REPORT.md:102-105 (commit before 930a67cb):
  programmatic jq walk of all 400 cards found only `{node, ts}` (+
  `headroom`) in running[]/claims[] — **zero time-window keys** (no
  start/end/window/duration/book/reserv/schedule/slot anywhere in the
  schema).
- **Currency:** LIVE — mtime **2026-09-15 15:05:00 +0200** (stat this
  session), scheduler writes continuously.
- **Judgement:** authoritative for WORK DISPATCH (it is what actually
  sends bench-cluster cards to workers), but structurally NOT a
  booking system — a card cannot express a time window, so no
  reservation can live there. Also: fresh reads denied this session —
  treat its current contents as unverifiable from this worker.
- Source: stat this session; committed occupancy-booking/REPORT.md
  :102-105; calendar-booking-mining/REPORT.md:100 (candidate table row 2).

## Candidate 3 — Balloon v3 peripheral-lock registry (live hardware mutex)

- **Name:** balloon-board-lock.py hard device lock registry
- **Maintainer/owner:** balloon track tooling — authorship 9 commits
  Felix, 1 c03rad0r (`git log --follow -- tools/balloon-board-lock.py`
  in balloon repo, re-verified in committed
  calendar-booking-mining/REPORT.md:158-166); docs in
  balloon/AGENTS.md:43 ("Tool: .../balloon-board-lock.py (v3)")
- **Access path:** `~/.hermes/peripheral_locks/` — LOCK FILES:
  `balloon-{tx,rx,board-a,board-b,board-c}.lock` (tool source lines
  29-30, read this session); resource map verbatim tool line 37:
  `c3-a — ESP32-C3 + LR2021 board A (MAC b0:a6:04:00:96:dc,
  /dev/ttyACM0)` — the meshcore bench DUT
- **Currency:** live but EMPTY — 0 lock files, no theft log ever
  created (`ls -la ~/.hermes/peripheral_locks/` this session: only
  `. ..` entries; dir mtime 2026-08-28 12:38). Registry holds nothing
  right now.
- **Judgement:** authoritative FOR LIVE OCCUPANCY ONLY — the only
  OS-enforced mutex (chmod 000 hard lock), but session-scoped with
  auto-release; cannot represent future windows, so not a booking
  system.
- Source: ls + tool source read this session; balloon/AGENTS.md:43.

## Candidate 4 — FLASH-QUEUE.md, balloon copy (flash-approval ledger — governs the bench boards)

- **Name:** "Flash Queue — Board Access Coordination" (balloon repo)
- **Maintainer/owner:** balloon-hermes orchestrator GROUP (unnamed
  membership) per repo-wide banner; introduced by commit **35b292c3**
  2026-07-24 21:27:47 +0530, author **Felix** ("fix(tools): Phase 2 —
  hard board locking + flash queue")
- **Access path:** `~/repos/balloon/docs/coordination/FLASH-QUEUE.md`
  (2216 bytes)
- **Currency:** queue EMPTY — Active Queue table row verbatim:
  `| _(empty — no pending flash requests)_ | | | | | | |`. File mtime
  **2026-09-11 17:34:49 +0200** (stat this session). This is the copy
  whose tool resource map governs c3-a/c3-b (the meshcore bench
  boards). No named approver cell is filled anywhere in it.
- **Judgement:** authoritative as an APPROVAL LEDGER for flashing the
  bench boards (the only written approval mechanism), but it is a
  flash-approval queue, not a time-slot booking system — it has no
  occupancy/window semantics for bench or chamber use, and its queue
  is empty anyway.
- Source: file read + stat + `git log -1 35b292c3` this session.

## Candidate 5 — FLASH-QUEUE.md, E80 copies (2x, different bench — recorded for reconciliation)

- **Name:** same title, in balloon-e80bench and e80-bench repos
- **Maintainer/owner:** same balloon-hermes orchestrator banner; last
  doc touch by commits 8f3f63bd / beeb38de ("docs: add wave4 task
  cards + e2e playwright plan + update flash queue") in both repos
- **Access path:** `~/repos/balloon-e80bench/docs/coordination/
  FLASH-QUEUE.md` (mtime 2026-08-28 12:38, 2753 bytes) and
  `~/repos/e80-bench/docs/coordination/FLASH-QUEUE.md` (mtime
  2026-09-11 19:15:31 +0200, 2753 bytes)
- **Currency:** both carry the host's ONLY filled approver cells,
  verbatim row 1: `| balloon-range-tests | E80 #1+#2 | PRBS-15
  harmonization: E80 flashed+verified, C3 not connected |
  2026-08-20T09:00Z | felix (orchestrator) | 8m | DONE (PARTIAL) |`
  (+2 more DONE rows approved via kanban cards t_dd4e516b/t_a2949a8d).
  Last queue activity: 2026-08-21T16:00Z (row 3 requested_time).
- **Judgement:** NOT authoritative for the meshcore bench/chamber —
  these govern the E80 range-test bench, a DIFFERENT bench. Recorded
  because the task-3-flash queue multiplicity is an anomaly to
  reconcile, and because "felix (orchestrator)" is the only named
  approver in any queue on this host.
- Source: both files read + stat + git log this session.

## Candidate 6 — AGENTS.md flash-queue pointer (dangling — inaccessible candidate)

- **Name:** balloon-fresh FLASH-QUEUE.md (the canonical per AGENTS.md)
- **Maintainer/owner:** balloon-hermes orchestrator group
- **Access path:** `~/repos/balloon-fresh/docs/coordination/FLASH-QUEUE.md`
  — **DOES NOT EXIST**: `ls -d ~/repos/balloon-fresh` → "No such file
  or directory" (this session). balloon/AGENTS.md:47-48 points there
  verbatim: "Before flashing ANY board, add a row to
  `~/repos/balloon-fresh/docs/coordination/FLASH-QUEUE.md` and wait
  for approval."
- **Currency:** N/A — unreachable pointer; the balloon repo's remote is
  named `balloon-fresh` (origin github.com/felixfelix-bot/balloon-fresh)
  but the directory is absent locally.
- **Judgement:** recorded as an ACCESS FAILURE candidate — the
  documented canonical queue is not accessible from this host; the
  balloon-repo copy (candidate 4) is the locally reachable stand-in.
- Source: ls + AGENTS.md read this session.

## Candidate 7 — meshcore bench/ git record (this campaign's own ledger)

- **Name:** meshcore `bench/` report directory (52 subdirectories)
- **Maintainer/owner:** the fleet workers themselves (this campaign)
- **Access path:** `/home/c03rad0r/repos/meshcore/bench/` — committed
  REPORT.md artifacts, one per task
- **Currency:** CURRENT — latest commit f14f6a92 (2026-09-15,
  bench/coax-cable-inventory); this repo is the only place a
  reservation-like artifact has ever been recorded:
  bench/chamber-reservation/REPORT.md (commit 7d9227a1) holds a
  REQUESTED/UNCONFIRMED reservation block, and
  bench/occupancy-booking/REPORT.md:153-173 recommends treating
  bench/ as the interim written ledger.
- **Judgement:** the de facto interim ledger — precedent exists
  (7d9227a1), but it is not a booking system (no scheduler enforces
  it; it is prose). Not authoritative as a system of record until the
  fleet designates one.
- Source: git log + committed occupancy-booking/REPORT.md:153-173,
  chamber-reservation/REPORT.md:89-120 this session.

## Candidate 8 — Fork-side bench ledger (RESULTS.md, dangling commit d7ae93fa)

- **Name:** `examples/passive_mapper/bench/RESULTS.md` — Felix's fork
- **Maintainer/owner:** Felix (sole author; `git cat-file -p d7ae93fa`
  this session: author Felix <301398501+felixfelix-bot@users.noreply.
  github.com>, 2026-09-11)
- **Access path:** meshcore repo, dangling commit `d7ae93fa` — readable
  by SHA only (`git show d7ae93fa:examples/passive_mapper/bench/
  RESULTS.md`); the branch ref is gone from this clone
- **Currency:** snapshot 2026-09-11; exactly one row, verbatim:
  `| _not yet measured_ | SkyMapper Board A (LR2021) | | | | | | | 10
  | | | pending: needs the freezer/dry-ice sweep, see the card |`
  — the fork records the bench as never having been used.
- **Judgement:** authoritative as a COMPLETED-RUN ledger (calibration
  records per module), not a reservation system. Stale by design: no
  outbound probes allowed (standing dq05 constraint), so anything
  Felix pushed after 2026-09-11 is invisible here.
- Source: git cat-file + git show this session.

## Candidate 9 — Hermes kanban DB + boards (ticketing)

- **Name:** local kanban database + public board export
- **Maintainer/owner:** hermes-orchestration kanban stack; meshcore
  board created 2026-09-09 (board.json created_at 1783550915 =
  2026-09-09); public export generated by
  `scripts/fleet/export_public_boards.py` (kanban-boards/README.md:11)
- **Access path:** `~/.hermes/kanban.db` (read-only query this session)
  + `~/kanban-boards/boards/<slug>/` (25 public boards, 752 tasks per
  README) + `~/hermes-orchestration/state/kanban/boards/` (live stack)
- **Currency:** kanban.db last write 2026-09-12 14:06 (+0200, stat);
  public meshcore tasks.json frozen 2026-09-11 17:33; the DB holds 11
  tasks total, and the only bench-related tasks are investigative
  worker cards (e.g. "Run LR2021 bench session: freezer sweep + ramp
  telemetry capture", t_a132b6cd, status ready — read this session in
  kanban-boards/boards/meshcore/tasks.json). Live-board reads were not
  re-attempted this session beyond the public export (live board state
  file read was operator-denied).
- **Judgement:** NOT a booking system — kanban is work ticketing: tasks
  carry status/assignee, no time-window semantics; no bench/chamber
  reservation has ever been a task. The board IS the closest thing to
  an "issue tracker used for bench scheduling" (the task's channel
  list): bench session cards exist (4 bench-session tasks on the
  meshcore board), but they dispatch work, not resource windows.
- Source: sqlite read-only query + tasks.json read + stat this session.

## Candidate 9b — stackstr SCHEDULE.md (surfaced by sweep, excluded)

- **Name:** stackstr board schedule
- **Maintainer:** manager-scheduler, created 2026-08-27T17:56:40
  (header line 1)
- **Access path:**
  `~/hermes-orchestration/state/kanban/boards/stackstr/SCHEDULE.md`
- **Currency:** header states "SCHEDULING ONLY — all tasks blocked +
  unassigned" — a dependency DAG table, no time slots.
- **Judgement:** NOT a booking system, wrong board (stackstr, not
  meshcore/bench resources); listed for completeness.
- Source: file head read this session.

## Candidate 10 — Nostr NIP-29 Buzz groups (the workspace chat)

- **Name:** hermes-fleet + operator-alerts Buzz groups (Nostr kind-9 chat)
- **Maintainer/owner:** fleet operator pair — Felix (self-ID "Felix
  here — CobradorWave (canary node)", event c3ebb48e…, 2026-09-11
  11:27:56 UTC) + dq05/cobrador machinery; local strfry relay on
  127.0.0.1:7780 (strfry landing page reachable, this session) bridged
  to wss://relay.orangesync.tech (auth-gated)
- **Access path:** local relay ws://127.0.0.1:7780; documented full
  history in committed bench/bench-owner-chat-history/REPORT.md
  (16,094 hermes-fleet events mined 2026-09-11→15)
- **Currency:** LIVE channel (bridge state file mtime 2026-09-15
  15:05:03, stat this session) — but a fresh relay re-sweep was
  **operator-denied this session** (two read attempts blocked). The
  committed prior sweep is the evidence of record: zero bench/chamber
  booking chatter, zero pinned topics (zero kind-11 events), no
  booking bot.
- **Judgement:** NOT a booking system — chat is the notification
  channel (human-gate notices), and the mined history contains no
  reservation semantics; prior sweep found no booking mentions.
  Fresh verification denied — recorded as an access failure for live
  re-check.
- Source: committed bench-owner-chat-history/REPORT.md:31-45 (channel
  table, pinned-topic negative); stat this session; relay landing page
  curl this session.

## Candidate 11 — Shared spreadsheets / drive / wiki / Notion / Confluence

- **Result: NONE EXIST (verified negative, this session).**
- Search method (fresh, this session): host-wide `find /` for
  `*.xlsx *.ods *.csv *.gnumeric` excluding node_modules/.git → only
  test-data CSVs (R package extdata, balloon-e80bench sweep/result
  logs, hardware BOMs) — zero booking spreadsheets. Host-wide wiki
  search (`find /home /var /srv /opt /etc -iname '*wiki*'`) → zero
  wikis (committed 930a67cb report WIKI-DOCS-SWEEP.md, re-verified
  this session by direct ls of repos): only hermes
  wiki-health-check.sh scripts, unrelated. No Notion/Confluence
  client or config anywhere under ~/.config. No Google Drive /
  Nextcloud sync config. The lab docs space IS the repos (meshcore
  docs/ + bench/, balloon docs/, e80-bench) — none contain booking
  pages: `grep -rniE 'book|reserv' meshcore/docs/` → only radio-protocol
  "reserved" byte ranges (docs/number_allocations.md:9, cli_commands.md:444),
  nothing about resource booking.
- **Judgement:** negative — no spreadsheet, drive, wiki, Notion, or
  Confluence candidate exists host-wide. This is an existence negative,
  not an access failure.
- Source: find + grep sweeps this session; committed WIKI-DOCS-SWEEP.md.

## Candidate 12 — Physical logbook / QR codes / signage / camera

- **Result: NONE EXIST (verified negative).**
- No physical logbook, labbook, or handwritten record exists on any
  record: exhaustive find for logbook/labbook/lab-log/bench-log
  artifacts → zero hits (committed
  bench/bench-owner/LOGBOOK-SIGNATURE-INSPECTION.md, method §1).
  No camera exists on this host (`/dev/video*` absent, exit 2 —
  LOGBOOK report §3), so no photo of pages could be taken even if a
  book existed. No QR/signage/sticker candidates: the only QR assets
  are meshcore protocol QR formats (docs/qr_codes.md — meshcore://
  channel/contact sharing, unrelated to lab signage) and unrelated
  web-app scanner components. The chamber itself has never been
  located (chamber-nameplate REPORT.md: "no chamber was located... no
  photo could be taken"), so there is no nameplate/signage to inspect.
- **Judgement:** negative — no physical-world candidate channel exists
  on any record reachable from this host.
- Source: committed LOGBOOK-SIGNATURE-INSPECTION.md §1-4;
  chamber-nameplate/REPORT.md verdict; find for qr/signage/sticker/
  nameplate this session.

---

## Channel coverage table (task's required channels)

| Task-listed channel | Corresponding candidate(s) | Outcome |
|---|---|---|
| Shared calendar(s) | 1 (Evolution) | exists, empty+stale, no lab content |
| Spreadsheets / drive / docs | 11 | NONE exist (verified negative) |
| Wiki / Notion / Confluence | 11 | NONE exist; lab docs space = the repos |
| Physical logbook | 12 | NONE exists; no camera to photo pages |
| Slack/Matrix/IRC + pins + booking bots | 10 (Nostr Buzz groups) | platform exists, history mined (committed), no booking chatter/pins/bot; live re-sweep denied this session |
| QR codes / signage / stickers | 12 | NONE exist; chamber never located |
| Ticketing / issue tracker | 9, 9b | kanban exists (work ticketing), never used for windows; 4 bench-session dispatch cards exist |

Plus candidates found beyond the task's list: fleet board (2),
hardware lock registry (3), flash queues (4-6), bench/ git ledger (7),
fork RESULTS.md (8).

---

## Access failures this session (recorded per task instructions)

1. **Fleet board state file** `~/.hermes/bot/fleet_queue_state.json` —
   fresh read operator-DENIED (2026-09-15 ~15:05). Its structural
   non-booking finding rests on the committed prior audit
   (occupancy-booking/REPORT.md:102-105), not a fresh read.
2. **Live chat relay re-sweep** (two nak read attempts) —
   operator-DENIED. Chat-history findings rest on the committed prior
   full-retention sweep (bench-owner-chat-history/REPORT.md).
3. **Bot-config JSON reads** (alerts_channel.json, buzz state files)
   — operator-DENIED. Not retried; nothing in this report depends on
   them.
4. **FLASH-MANIFEST.csv + fleet lease records** — the read batch was
   operator-DENIED. Not retried; the E80 queue evidence stands on
   FLASH-QUEUE.md itself (candidate 5).
5. **balloon-fresh canonical queue** (candidate 6) — directory absent
   host-wide; unreachable by design of this host's layout.
6. **Outbound probes** (GitHub issues on felixfelix-bot/MeshCore etc.)
   — standing dq05 constraint: no outbound network contact. GitHub
   issue-tracker candidates cannot be checked from this node; the
   gh CLI is configured (user felixfelix-bot) but no outbound query
   was made. This is an access failure by policy, recorded as such.

Per standing operator rules, denied reads are recorded and NOT
retried, and nothing in this report was fabricated to fill the gaps.

---

## Nothing fabricated

No candidate system was invented. Every positive claim above cites a
file path + mtime/line, a git SHA, or a committed report. Every
negative (no wiki, no spreadsheets, no logbook, no QR, no Slack/
Matrix) is reported as an existence negative with the search command
that established it. Denied accesses are reported as access failures,
not as negatives.