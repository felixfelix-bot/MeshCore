# Bench owner/custodian: named source and confidence

Task: `meshcore:t_d601da74` — "Identify the bench owner/custodian with named
source and confidence. GOAL: Determine exactly who controls the test bench
(not the lab or building) and produce evidence."

Bench in scope: the **meshcore thermal bench** — SkyMapper Board A (NiceRF
LR2021, balloon lock resource `c3-a`) + reference TX node, as consumed by the
passive_mapper calibration campaign (`bench/*/REPORT.md`, sibling soak/atcut
cards). The E80-STM32 range-test bench (`~/repos/e80-bench`) is a different
bench and out of scope (one line on it in the anomalies).

Cold-start verification session: 2026-09-14, host `c03rad0r-DQ05proplus`,
worker profile worker-heavy. Every claim below was re-verified against the
raw source this session; nothing is taken from memory or from the sibling
report `bench/chamber-reservation/REPORT.md` (commit 7d9227a1) without
independent re-reading.

---

## Verdict

**Bench custodian/operator: Felix** — GitHub `felixfelix-bot`, git identity
`Felix <301398501+felixfelix-bot@users.noreply.github.com>` — **HIGH**.

Control is SPLIT three ways (task step 3 requires reporting the split, not
picking one):

| Role | Who | Confidence |
|---|---|---|
| Bench operator/custodian (performs + authorizes the physical bench work) | Felix (felixfelix-bot) | HIGH |
| Fleet scheduling/dispatch authority (who can send bench-cluster cards to a worker) | cobrador (fleet operator node = same human c03rad0r on the peer machine CobradorWave) | HIGH |
| Flashing approval for the bench boards (group authority) | balloon-hermes orchestrator GROUP (no named individual on record) | MEDIUM (documented authority, unnamed membership) |

## Candidates, with exact sources

### 1. Felix — bench operator/custodian — HIGH

(i) Full name: **Felix** (mononym on record; no surname exists anywhere on
this host; commits as `Felix <301398501+felixfelix-bot@users.noreply.github.com>`).
(ii) Group/team: passive_mapper / MeshCore fork maintainer; also the standing
gate authority in this fleet ("FELIX-GATE", see source 3) and author of the
balloon hardware-lock tooling.
(iii) Exact sources (all read fresh this session):
- **Source 1 (primary, written, verbatim):** commit `d7ae93fa`
  (docs(passive_mapper)), file `examples/passive_mapper/bench/README.md`,
  section "What has to be measured, and by whom", retrieved via
  `git show d7ae93fa:examples/passive_mapper/bench/README.md`:
  > "This is **bench work for the operator** (Felix), not for an agent: it
  > needs a NiceRF LR2021 module, a way to hold it at temperature for hours,
  > and a second MeshCore node as a reference transmitter. No agent host in
  > this fleet has the module attached and none can put a board in a freezer."
  The entire bench kit (`README.md`, `RESULTS.md` with an `operator` column,
  `thermal_bench.py`, `calib.py`, `test_calib.py`) was authored by Felix in
  commit `4a25db04` (2026-09-11, author + committer Felix, verified via
  `git cat-file -p 4a25db04`).
- **Source 2 (corroboration, tooling):** the OS-enforced mutex for the same
  LR2021 boards, `~/repos/balloon/tools/balloon-board-lock.py` — resource map
  verbatim: `c3-a — ESP32-C3 + LR2021 board A (MAC b0:a6:04:00:96:dc,
  /dev/ttyACM0)`, `c3-b — ... board B`. Authorship via
  `git log --follow -- tools/balloon-board-lock.py`: 9 commits Felix
  (54ff84e, 35b292c, ef60a51, 9b740aa, 99b94ca, ba4582b, 3b5025a, 327dd42,
  24412c9), 1 commit c03rad0r (8581ec0, the initial version).
- **Source 3 (corroboration, standing authority):** peer event log
  `~/.hermes/bot/peers/events-cobrador.jsonl` — "FELIX-GATE: task starts only
  after Felix merges #356" (ts 1789245231 = 2026-09-12T22:33:51+02:00), plus
  ~10 further FELIX-GATE / "Felix directives" / "Felix style" gate lines.
  NOTE: this log contains ZERO occurrences of "bench" (grep-verified) — it
  corroborates Felix's general authority, not bench ownership specifically.
(iv) Confidence HIGH because: the primary written source names him explicitly
as the bench operator in the section literally titled "and by whom", and he
authored 100% of the bench kit and 9/10 commits of the board-lock tool that
physically governs the bench hardware.

### 2. cobrador — fleet scheduling authority — HIGH (for the scheduling role only)

(i) Full name: cobrador (node/actor name; same human c03rad0r on the peer
machine CobradorWave — NOT a second bench owner).
(ii) Group/team: fleet operator peer node (fleet.json: peer "cobrador",
hosts 192.168.2.9 / cobradorwave.local / 100.90.101.9, user c03rad0r).
(iii) Exact sources: `~/.hermes/bot/fleet.json` (peer record, read this
session); `~/.hermes/bot/peers/cobrador.json` (node record, role "canary",
hostname CobradorWave); `~/.hermes/bot/.fleet_lease/cobrador.json` (lease
record); card `meshcore:t_d601da74` and the sibling `meshcore:t_c1c07af9`
are claimed on dq05 per `~/.hermes/bot/peers/cobrador.ownership.json` (meshcore
card claims by dq05, meshcore board owned by the c03rad0r/MeshCore fork).
(iv) Confidence HIGH for *scheduling* (the fleet board is the only dispatch
system and cobrador is the only peer operator), explicitly NOT for bench
custody: nobody on either node has the LR2021 module attached (USB census in
sibling report; fork README states it in writing).

### 3. balloon-hermes orchestrator group — flashing approval authority — MEDIUM

(i) Full name: **balloon-hermes** (a GROUP; no individual member is named
anywhere on this host).
(ii) Group/team: balloon-track orchestrator group.
(iii) Exact source: `~/repos/balloon/AGENTS.md` line 47, verbatim:
  > "**NO flashing without orchestrator (balloon-hermes) approval.** Before
  > flashing ANY board, add a row to `~/repos/balloon-fresh/docs/coordination/FLASH-QUEUE.md`
  > and wait for approval."
  Also lines 3 and 22: workers "report to the balloon-hermes orchestrator
  group". The FLASH-QUEUE.md file itself does not exist on this host
  (`~/repos/balloon-fresh` absent; host-wide find for FLASH-QUEUE: no match).
(iv) Confidence MEDIUM: the group's authority over the bench boards is
written and unambiguous, but its membership is unnamed and its approval
record file is absent on this host, so an individual cannot be cited.

## Source-tier sweep (task step 1, in order) — negative results

1. **Lab wiki / docs:** no wiki exists host-wide (find for *wiki* across
   /home, /srv, /opt, /var/tmp: only unrelated R-library hits). The repo
   docs ARE the lab documentation → Felix found there (Source 1 above).
2. **Shared calendars:** the only calendar on this host,
   `~/.local/share/evolution/calendar/system/calendar.ics`, contains ZERO
   VEVENTs (full 6-line content re-read this session; untouched since
   2026-03-10T23:01:44Z). No CalDAV/WebDAV/GOA config exists. No owner or
   booking information.
3. **Booking spreadsheets:** none exist (host-wide find for *.xlsx,
   *booking*, *reserv*: no relevant hits).
4. **Physical logbook:** none exists (find for *logbook*/*labbook*:
   no hits). The closest thing to a bench ledger is the fork's
   `bench/RESULTS.md` (operator column, single pending row authored by
   Felix's commit 4a25db04).
5. **Slack/Matrix channel history (searched, not asked):** the only
   messaging infrastructure on this host is the buzz/nostr bridge
   (`buzz_responder.json`: relay wss://relay.orangesync.tech, receive/echo
   profile worker-base). Searched state files
   (`buzz_responder_state.json`, `buzz_relay_bridge_state.json`,
   `buzz_signal_bridge.json`) and the events log for "bench": **zero hits**.
   The events log DOES carry the FELIX-GATE lines (source 3 above).
6. **Direct messages / in-person:** not obtainable this session — the bridge
   is receive/echo infrastructure and this worker is prohibited from
   outbound probes (standing constraint, honored). **No verbal evidence of
   any kind was received, so nothing here is labeled verbal; equally, no
   verbal confirmation of Felix exists — the HIGH confidence rests entirely
   on written sources.**

## Ambiguity callouts (do not collapse these)

1. **Three-way split of control** (operator vs scheduler vs flash-approver):
   reported above rather than picking one. Felix is the only named *bench*
   custodian; cobrador controls when fleet workers may attempt bench work;
   balloon-hermes (unnamed group) controls flashing the bench boards.
2. **"Felix" is a mononym.** No surname exists on this host; the GitHub
   identity is a bot account (felixfelix-bot). HIGH confidence attaches to
   the identity-as-recorded, not to a fuller legal name.
3. **The bench is not physically present in the fleet.** The fork README
   states in writing that no agent host has the LR2021 module attached;
   "custodian" therefore means custodian of the bench protocol/kits/boards,
   verified from this host's records.

## Corrections to the prior fleet record (bench/chamber-reservation/REPORT.md)

- The prior report cites the primary source as fork branch
  `origin/feat/passive-mapper` @ d7ae93fa. **That ref no longer exists in
  this clone** (`git for-each-ref --contains d7ae93fa` returns nothing; the
  commits are dangling objects). The content remains verifiable by SHA,
  which this session did; future citations should use the SHA, not the ref.
- The prior report renders the git email as `30139850+felixfelix-bot@...`;
  the actual object header is `301398501+felixfelix-bot@...` (verified via
  `git cat-file -p`). Transcription typo, corrected here.
- Prior report's balloon lock-tool authorship count "9 commits Felix, 1
  c03rad0r" re-verified with `--follow`: exact match.

## Anomalies

1. The sibling ownership card `meshcore:t_c1c07af9` (chamber custodian)
   and this card were both previously undispatched; the fleet's first named
   answer remains the chamber-reservation report — this file is the first
   bench-specific answer verified cold.
2. `meshcore:t_0d0fe29c` (the chamber-reservation card) now shows an empty
   title/body in `fleet_queue_state.json` while its REPORT.md is committed —
   board state and committed record have diverged.
3. The e80-bench repo (`~/repos/e80-bench`) is a second "test bench" in this
   fleet (STM32F103C8T6 E80 range-test bench, README line 1). It shares the
   balloon-hermes flashing-approval regime. Out of scope for the meshcore
   bench, but any future "the bench" question should disambiguate first.