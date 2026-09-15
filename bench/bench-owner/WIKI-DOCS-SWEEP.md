# Lab wiki / docs sweep: test-bench ownership records

Task: Search lab wiki and documentation spaces for any record naming the
custodian/owner of the TEST BENCH itself (not the lab room or building).
Cold start — nothing taken from memory or prior reports without independent
re-verification against raw sources.

Session: 2026-09-15, host `c03rad0r-DQ05proplus`, worker profile worker-heavy.
Bench in scope: the **meshcore thermal bench** (SkyMapper Board A, NiceRF
LR2021, balloon lock resource `c3-a` + reference TX node), per the campaign
convention in `bench/*/REPORT.md`.

---

## VERDICT

**One individual is named as bench custodian: Felix** (HIGH). No wiki, booking
system, or logbook exists anywhere reachable — the "lab documentation space"
is the repos themselves (meshcore `docs/` + `bench/`, balloon `docs/` +
`docs/coordination/`, e80-bench), and the naming lives in the fork's bench
README. Control is split three ways; the only new individual-level evidence
this sweep found beyond the prior record is a **named approver cell —
"felix (orchestrator)" — in the e80-bench FLASH-QUEUE.md**, which also
**corrects the prior bench-owner REPORT.md** (it claimed FLASH-QUEUE.md does
not exist on this host; it exists in three repos).

---

## Documentation spaces enumerated (all reached this session)

| Space | Contents checked | Bench-ownership result |
|---|---|---|
| meshcore `docs/` (16 files) | full grep: bench/custodian/owner/booking/reservation | nothing — `owner.info` is radio-node config text, unrelated |
| meshcore `bench/` (44 worker dirs) | prior reports re-verified by raw source | verdicts converge: Felix operator, no wiki/booking/logbook exists |
| meshcore git (all refs + dangling d7ae93fa) | `git show d7ae93fa:examples/passive_mapper/bench/README.md` re-read verbatim | **PRIMARY SOURCE — names Felix** (below) |
| balloon `docs/` (~170 files, incl. handover/ops/status) | grep bench/test bench/custodian/owner/approver | no bench-ownership statement; `mcu-assessment` line 99 "Both devices are on the bench" is a test note, no owner |
| balloon `docs/coordination/` (60 files) | AGENTS.md, FLASH-QUEUE.md, HARDWARE_MUTEX.md, TRACKS-REGISTRY.yaml, INDEX.md, HIERARCHY-* | group authority named (balloon-hermes), no individual for the meshcore bench |
| e80-bench / balloon-e80bench | FLASH-QUEUE.md read in full | **named approver cell "felix (orchestrator)"** — different bench (see candidate 2) |
| Host-wide wiki search | `find /home /var /srv /opt /etc -iname '*wiki*'` | zero wikis; only unrelated hermes `wiki-health-check.sh` scripts |
| Host-wide logbook/labbook | find | zero; only this campaign's own inspection note |
| Evolution calendar | full content re-read | 6 lines, zero VEVENTs, mtime 2026-03-11 — no booking records |
| kanban-boards `ownership.json` | read | `{}` — empty |
| buzz/nostr bridge + events log | grep bench | zero "bench" mentions in `events-cobrador.jsonl` (re-verified, count = 0) |

---

## CANDIDATES (evidence-record format)

### 1. Felix — bench operator/custodian — HIGH

- (i) **Full name:** Felix (mononym; no surname exists on any record on this
  host). Git identity, verified fresh via `git cat-file -p d7ae93fa` and
  `4a25db04`: `Felix <301398501+felixfelix-bot@users.noreply.github.com>`.
- (ii) **Group/team:** passive_mapper / MeshCore fork maintainer
  (GitHub `felixfelix-bot`); author of the balloon hardware-lock tooling
  (`tools/balloon-board-lock.py`) that governs the bench boards.
- (iii) **Exact sources** (every one re-read this session):
  - meshcore commit `d7ae93fa` (reachable only as a dangling object;
    `git for-each-ref --contains` is empty — cite the SHA, not a ref),
    file `examples/passive_mapper/bench/README.md`, section
    **"What has to be measured, and by whom"**, verbatim:
    > "This is **bench work for the operator** (Felix), not for an agent: it
    > needs a NiceRF LR2021 module, a way to hold it at temperature for hours,
    > and a second MeshCore node as a reference transmitter."
    Retrieved via `git show d7ae93fa:examples/passive_mapper/bench/README.md`.
  - Corroboration: commit `4a25db04` ("feat(passive_mapper): bench calibration
    kit") — author AND committer Felix; the entire bench kit
    (`thermal_bench.py`, `calib.py`, `test_calib.py`, `RESULTS.md` with an
    `operator` column) is his authorship.
  - Corroboration: `~/repos/balloon/tools/balloon-board-lock.py` lines 37-38
    (re-read this session): `c3-a — ESP32-C3 + LR2021 board A (MAC
    b0:a6:04:00:96:dc, /dev/ttyACM0)`; git authorship via `git log --follow`:
    commits by Felix (35b292c3, ef60a51b, ba4582b0, 9b740aa7, 99b94ca2, ...),
    one initial commit by c03rad0r (8581ec0e).
  - Corroboration (general authority, not bench-specific): peer event log
    `~/.hermes/bot/peers/events-cobrador.jsonl` carries FELIX-GATE /
    "Felix directives" lines (e.g. fleet-task bodies citing "Felix Q1",
    "Felix directives 2026-08-29"); grep-verified ZERO occurrences of
    "bench" in that same log.
- (iv) **Confidence: HIGH** — named explicitly, in writing, as the operator
  of the bench in a section literally titled "and by whom", in the document
  that defines the bench.

### 2. felix (orchestrator) — named APPROVER in a flash-queue approval table — MEDIUM (different bench)

- (i) **Full name:** "felix (orchestrator)" — the string in the `approved_by`
  column; same mononym as candidate 1.
- (ii) **Group/team:** balloon-hermes orchestrator (the approval authority
  that FLASH-QUEUE.md rules require).
- (iii) **Exact source:** `~/repos/e80-bench/docs/coordination/FLASH-QUEUE.md`
  (identical copy at `~/repos/balloon-e80bench/docs/...`), "Active Queue"
  table, row 1, verbatim:
  `| balloon-range-tests | E80 #1+#2 | PRBS-15 harmonization: ... | 2026-08-20T09:00Z | felix (orchestrator) | 8m | DONE (PARTIAL) |`
  File last committed 8f3f63bd / beeb38de (authors verified: Felix).
- (iv) **Confidence: MEDIUM for the approver role — and explicitly NOT for
  the meshcore bench.** This is the only place on this host where an
  `approved_by` cell is filled with a name. It names the approver for the
  **E80 range-test bench** (`~/repos/e80-bench`, a different bench — README
  line 1: "Pico-Balloon Tracker & E80 Range Test Bench"). The FLASH-QUEUE.md
  that governs the meshcore bench boards (balloon repo copy, whose lock
  resources are c3-a/c3-b) has an **empty queue** — no filled approver cell.
  Gap: no equivalent filled approver row exists anywhere for the meshcore
  thermal bench itself.

### 3. balloon-hermes orchestrator GROUP — flashing-approval authority — MEDIUM (group only, no individual)

- (i) **Full name:** balloon-hermes (a GROUP; no individual member is named
  on this host).
- (ii) **Group/team:** balloon-track orchestrator group.
- (iii) **Exact sources:**
  - `~/repos/balloon/AGENTS.md` (read fresh, lines ~45-49): "**NO flashing
    without orchestrator (balloon-hermes) approval.** Before flashing ANY
    board, add a row to `~/repos/balloon-fresh/docs/coordination/FLASH-QUEUE.md`
    and wait for approval."
  - `~/repos/balloon/docs/coordination/TRACKS-REGISTRY.yaml` (read fresh):
    `orchestrator_group: balloon-hermes` — "This file is the SINGLE SOURCE OF
    TRUTH for orchestrator scope."
  - `~/repos/balloon/docs/coordination/FLASH-QUEUE.md` (read fresh, full):
    "NO flashing without orchestrator (balloon-hermes) approval. Sub-managers
    escalate flash requests to the orchestrator." Active Queue: empty.
- (iv) **Confidence: MEDIUM** — the group's authority over the bench boards
  (c3-a/c3-b) is written and unambiguous, but membership is unnamed, so no
  individual can be cited for this role. Candidate 2 shows the group's
  approver seat is de facto Felix, but only on the E80 bench's record.

### 4. cobrador — fleet scheduling authority — HIGH (for scheduling only, NOT custody)

- (i) **Full name:** cobrador (fleet node/actor name; peer machine
  CobradorWave).
- (ii) **Group/team:** fleet operator peer node (dispatches all bench-cluster
  work cards).
- (iii) **Exact source:** `~/.hermes/bot/peers/events-cobrador.jsonl` —
  every fleet-task record carries `"actor":"cobrador"` (verified across the
  merchant-routing / net4sats / plebeian task bodies read this session).
- (iv) **Confidence: HIGH for the scheduling role only** — cobrador controls
  WHEN fleet workers may attempt bench work. Nobody on either node has the
  LR2021 bench module attached (fork README states it in writing; USB
  censuses in sibling reports concur), so cobrador is not a bench custodian.

---

## Cases where only a group (no individual) is named

- **balloon-hermes orchestrator group** (candidate 3): the flashing-approval
  authority for the bench boards is a named group with zero named members.
  TRACKS-REGISTRY.yaml and AGENTS.md name the group; no file on this host
  names who is in it.

## If-nothing-named-an-individual clause

An individual IS named (Felix, candidate 1, HIGH), so this clause does not
trigger — but the strongest PARTIAL candidates and their gaps are recorded
for completeness:
- balloon-hermes group — written authority, unnamed membership (gap: no
  individual).
- e80-bench approver cell "felix (orchestrator)" — a filled approver field,
  but for the wrong bench (gap: no filled approver row for the meshcore
  thermal bench; its queue is empty).

---

## CORRECTIONS to the committed fleet record (new findings this sweep)

1. **FLASH-QUEUE.md DOES exist.** `bench/bench-owner/REPORT.md:102-103`
   claims "The FLASH-QUEUE.md file itself does not exist on this host
   (`~/repos/balloon-fresh` absent; host-wide find for FLASH-QUEUE: no
   match)." That is wrong on the second half: `~/repos/balloon-fresh` is
   indeed absent, but FLASH-QUEUE.md exists at
   `~/repos/balloon/docs/coordination/FLASH-QUEUE.md`,
   `~/repos/balloon-e80bench/docs/coordination/FLASH-QUEUE.md`, and
   `~/repos/e80-bench/docs/coordination/FLASH-QUEUE.md` (find this session:
   three matches; balloon copy mtime 2026-09-11). The AGENTS.md instruction
   points at the absent `balloon-fresh` path — the document is reachable via
   the balloon/e80-bench repos instead.
2. **A filled `approved_by` cell exists** ("felix (orchestrator)",
   e80-bench FLASH-QUEUE.md) — the first approver-form evidence on this host.
   It was previously reported that no approval record exists at all.
3. Prior reports' candidate list is otherwise REPRODUCED, not extended:
   Felix (operator, HIGH — re-verified verbatim), cobrador (scheduling, HIGH
   — re-verified via events log actor fields), balloon-hermes group (flashing
   approval, MEDIUM — re-verified in AGENTS.md + TRACKS-REGISTRY.yaml).
4. Re-verified negatives: no wiki host-wide; calendar has zero VEVENTs
   (content re-read: 6 lines); kanban-boards/ownership.json is empty (`{}`);
   events log contains zero "bench" strings.

## Constraints honored

No outbound probes (no network fetch, no messages sent, no Slack/Matrix
contact). Nothing posted anywhere. One fleet.json read was operator-denied
mid-session; not retried; cobrador's scheduling-role evidence rests on the
events log read instead (which succeeded and is cited above).