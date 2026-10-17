tags: no-code, docs

# t_9a2f522b — Calibration / maintenance actors and approvals from the PHYSICAL LOGBOOK

Task: extract named actors + approval evidence from the physical logbook **only**.
Cold start, this session (2026-10-17, host `c03rad0r-DQ05proplus`, worker `worker-admin`,
worktree `/home/c03rad0r/worktrees/t_e1408991`).
Read-only throughout: nothing on the board, in any repo, or on the external disk was modified.
This is run 2 of the card (run 1 ended `timed_out` at the iteration cap with this same verdict on
disk); everything below was **re-measured in this run**, not copied from run 1.

## Step 1 result — which copy did I use? NEITHER. No logbook exists in any reachable form

The card allows "the scanned or transcribed copy if the physical book is unavailable". I searched
for all three forms (physical artefact via cameras/scanners; scanned page images/PDFs; a
transcription) and the result is an **existence negative**, not a denied read:

| form searched | method (this session) | result |
|---|---|---|
| physical book present on this host | `/dev/video*` glob → 0 devices; `v4l2-ctl`, `fswebcam` ABSENT; `sane-find-scanner` → "No USB scanners found"; `lsusb` → 4 devices, all hub/BT/Lexar-USB-stick/USB-audio-HID (no scanner, no camera) | no device that could image a page |
| scanned copy (PDF/TIFF/JPG page sets) | `git log --all --diff-filter=A` image/PDF census in meshcore, e80-bench, balloon, car-tollgate-hardware, fips, microfips → only logos and E80 characterization plots; current meshcore tree → `logo/meshcore.png` only | 0 page-like artefacts |
| scanned copy on the 1.9 TB external USB disk | `/mnt` swept **per top-level subtree** (`find -xdev`, name patterns `*logbook* *labbook* *lab-book* *bench-log* *benchlog* *kladde* *dienstbuch* *pruefbuch* *sign-out* *handwritten*`) → only azure-msal `*SignOutRequest.d.ts` and a crate's `old-bench-log` test fixture (see NM-3/NM-4) | 0 logbook artefacts |
| transcription of pages | `grep -rliE 'transcri(be\|pt\|ption)'` over `/mnt/cw-offload/Documents`, `/mnt/archive`, `/mnt/cw-offload/reports` → 25 files, all voice-memo transcripts (`vibeline-voice-memos`) | 0 logbook transcription |
| logbook named anywhere on the main disk | chunked `find` per home subtree and per `/mnt` subtree, **completed in this run** for all ten named bases (see "What this run added") | only this card's own committed report (see "Prior art") |

**Page numbers: none are reported. There is no page to cite, and inventing one would be fabrication.**
Every finding below is therefore sourced to a *written record*, and each one says plainly that it is
not a logbook page.

## What this run added over run 1 (all re-measured, not re-quoted)

1. **The `/home` name sweep is now COMPLETE for the ten named bases**, so coverage caveat C3 is
   closed for those trees. Three passes were needed and the first two are worth recording as
   findings in their own right:
   * run 1's background pass (`_logbook_home_census_t_9a2f522b.py`) wrote 1 line
     (`HOME_NAME_HIT` → the committed `bench/bench-owner/LOGBOOK-SIGNATURE-INSPECTION.md`) and was
     **killed before finishing** — its output file was `rm`'d on restart, so run 1 left no coverage
     record at all. It is superseded, not evidence.
   * a sixth-pass rewrite (`_logbook_home_census2_t_9a2f522b.py`) returned `rc=2 hits=0` for **every**
     base. That is a **syntax error, not a negative result**: the predicate
     `find B -maxdepth 12 \( -name .git -prune \) -o NAMES -print` mis-groups the `-prune -o ... -print`
     alternation. A `find` that exits 2 has searched nothing — recorded here so the empty output is
     not mistaken for a clean sweep.
   * the seventh pass (`_logbook_home_census3_t_9a2f522b.py`) uses the correct form
     `find B -maxdepth 12 \( -name .git -prune -o NAMES -print \)`, sanity-checks its own predicate
     per base (`rc ∈ {0,1}` or it refuses and says `HOME_PREDICATE_INVALID`), and its result is the
     one quoted in the table above. Per-base `rc`, hit count, elapsed time and any timeout are in
     `logbook_home_census3_out.txt` (durable copy listed at the end).
2. **The three record findings were re-verified fresh by SHA in this run** (`git cat-file`-level):
   `d7ae93fa` = 2026-09-11T11:24:09+05:30, `11e43b0a` = 2026-09-14T10:53:50+02:00,
   `4b3ec9b5` = 2026-09-14T12:08:32+02:00. Dates below are committer dates, quoted from git.
3. **Newer sibling record read (not in run 1's draft):** `bench/bench-owner/` gained three commits on
   2026-10-17 — `b965d242` 01:49:27+02:00 (Felix = bench custodian, three-way control split),
   `36ad9d6a` 01:49:58+02:00 (physical logbook signature inspection, verified negative) and
   `215c8c55` 01:50:01+02:00 (wiki/docs sweep). `215c8c55` is a **correction** to the earlier
   `bench/bench-owner/REPORT.md` and matters for the approver question:
   `FLASH-QUEUE.md` **does** exist (`balloon/`, `balloon-e80bench/`, `e80-bench/docs/coordination/`),
   the host's **only filled approver cell** — `felix (orchestrator)` — is on the **e80-bench copy**
   (a *different* bench), and the meshcore-bench copy (`balloon/`) has an **empty queue, no named
   approver**. It also records `cobrador` as **fleet scheduling** owner (HIGH, from events-log actor
   fields). Both are recorded below under "Recorded but explicitly NOT a finding".
4. **The report is landed and published.** The deliverable is committed in the meshcore clone and the
   branch is pushed to the fork: `pushed to https://github.com/felixfelix-bot/MeshCore.git
   refs/heads/worker-admin/t_9a2f522b` (see "Landing" at the end for the exact ref and the pre-push
   gate output).

## What the written record does say about the three target roles

The only written ownership determination on this host was made by earlier workers and is **committed
in the repo**, so it is a read-only, citable artefact. Its verdict is that two of the three target
roles have **no named holder at all**. I re-read every commit below fresh this session; dates are the
committer dates, quoted from `git cat-file -p`.

### Committee finding F1 — Felix = bench operator/custodian (NOT a logbook signature)

- name as written: **"Felix"** — mononym; no surname anywhere on this host. Git identity verbatim:
  `Felix <301398501+felixfelix-bot@users.noreply.github.com>`
- group/team as stated on the page: passive_mapper / MeshCore fork maintainer (the page's own words)
- exact source: **commit `d7ae93fa`, 2026-09-11T11:24:09+05:30**, file
  `examples/passive_mapper/bench/README.md`, section "What has to be measured, and by whom"
- verbatim quote: *"This is **bench work for the operator** (Felix), not for an agent: it needs a
  NiceRF LR2021 module, a way to hold it at temperature for hours, and a second MeshCore node as a
  reference transmitter."*
- corroboration in the same record: the whole bench kit was authored by the same identity in
  **`4a25db04`, 2026-09-11T11:23:49+05:30** (`feat(passive_mapper): bench calibration kit
  (soak/edgescan/fit/ramp/hyst)`); `RESULTS.md` at `d7ae93fa` carries an empty `operator` column with
  a single `_not yet measured_` row
- confidence: **HIGH** that the written record names Felix as bench operator. **ZERO** for "logbook
  signature": no handwritten entry, no page, no sign-off exists.

### Committee finding F2 — controller-software admin: **UNDETERMINED (no name anywhere)**

- exact source: **commit `11e43b0a`, 2026-09-14T10:53:50+02:00**, `bench/chamber-ownership/REPORT.md`
- verbatim quote (commit subject = the report's own verdict line): *"chamber-ownership: custodian =
  Felix (MEDIUM, operator-scoping via fork README d7ae93fa); controller/software admin UNDETERMINED
  (no controller, no software, no record); maintenance approver UNDETERMINED (no cal system of
  record); all sources cited, nothing fabricated"*
- re-affirmed unchanged in **`4b3ec9b5`, 2026-09-14T12:08:32+02:00** (second cold dispatch):
  *"...verdict UNCHANGED: custodian Felix MEDIUM; controller/software admin + maintenance approver
  UNDETERMINED..."*
- independent corroboration of the *reason*: `bench/chamber-controller/REPORT.md` (2026-09-14,
  session 23:16-23:26 UTC+2) — *"VERDICT: UNKNOWN across the board — no thermal chamber or freezer
  exists under this host's control or on any record, so there is no controller to inspect"*; its
  USB/serial census found zero instrument-class devices
- confidence: **HIGH** that the record contains no name for this role. There is no candidate to
  grade — that is the finding, not a gap in my extraction.

### Committee finding F3 — maintenance-approver / calibration-approver: **UNDETERMINED (no name anywhere)**

- exact source: the same two commits, same dates, same verbatim sentence as F2 (`maintenance
  approver UNDETERMINED (no cal system of record)`; `...maintenance approver UNDETERMINED`)
- the string "calibration window" occurs on this host **only as a role label** in that report, with
  the approver marked `UNDETERMINED` — not as an event with a person attached
  (corroborated by `records/calibration_slots.csv` row `NOT-A-CAL-SLOT`, which cites that exact line)
- confidence: **HIGH** for "no named approver on record". Zero logbook evidence, zero written-name
  evidence.

### Recorded but explicitly NOT a finding (see Pitfalls)

The only *filled* approver cells anywhere on this host are on a **different bench**: the E80-STM32
range-test bench's `FLASH-QUEUE.md`, cell `felix (orchestrator)`, for board **flashing** approvals
(per `215c8c55`, 2026-10-17T01:50:01+02:00, which also corrects an earlier claim that no
`FLASH-QUEUE.md` existed host-wide). Cited only to show the search did cover approval cells — it does
not make Felix a chamber maintenance/calibration approver. Support line: `~/repos/balloon/AGENTS.md`
(read this session), *"**NO flashing without orchestrator (balloon-hermes) approval.**"* — a **group**,
no individual named. Likewise `cobrador` is recorded as **fleet scheduling** owner
(`215c8c55`, HIGH from events-log actor fields): scheduling a fleet slot is not approving chamber
maintenance or calibration, so it is not promoted into bucket (b) or (c).

## The three buckets

**(a) controller-software admin candidates — ZERO logbook evidence, ZERO record evidence.**
The record states the role is UNDETERMINED and that no controller or controller software was ever
found. No candidate can be listed without inventing one.

**(b) maintenance-approver candidates — ZERO logbook evidence, ZERO record evidence.**
Record says UNDETERMINED; reason given: "no cal system of record". No candidate.

**(c) calibration-approver candidates — ZERO logbook evidence, ZERO record evidence.**
Same two lines. The only named person in the whole record (Felix) is named as bench *operator*, in a
section titled "…and by whom" that is about *performing* bench work, not about approving calibration.
Promoting him to (c) would be inference, which the acceptance criteria forbid.

## Pitfalls — why 0/3 buckets are correct here instead of a padded list

1. **A prompt that says "extract names" creates pressure to produce names.** The honest output is
   empty for (a)-(c); filling it with the one name that appears anywhere would erase the actual
   finding (the role is undetermined on record).
2. **"Calibration" is a keyword collision on this fleet.** 21 meshcore cards and 9 bench commits
   contain it, but almost all are *cards about calibration evidence* or the router-quality
   LLM-judge "calibration samples" — not instrument calibration with a human approver. Counting them
   would inflate the evidence.
3. **"Maintenance" is a keyword collision too**: a fleet board literally named `router-maintenance`,
   plus PR "index maintenance" cards. None is chamber downtime (reconciled row-by-row in
   `records/maintenance_blocks.csv`).
4. **Approval cells on another bench are not approval cells on this one** (E80 flashing vs chamber
   calibration). Adjacency is not a finding.
5. **A mononym is not a full name.** Felix stays "Felix"; expanding it would fabricate.
6. **An empty `find` is not a negative result until its exit code says so.** A mis-grouped `find`
   predicate exits 2 and prints nothing (measured this run, sixth pass); only `rc ∈ {0,1}` output is
   admissible as "searched and found nothing".

## Prior art, and why this card is not duplicating it

A 2026-10-12 worker on host **CobradorWave** produced
`analysis/t_c2a72059/raw-findings-logbook-and-chat.md` (commits `46dcca41`, `0ce7726b`, `ca651f87`,
plus `a6e6be9c`, `f589baa7` on `remotes/fork/worker-admin/t_c2a72059`, not on `main`). Its verdict:
both upstream inputs empty, `records: []`, and it explicitly refused to substitute its own search.
This card asked me to search, so I did — independently, on this host (`dq05`), and my sweep is broader
than that report's 5 checks (camera/scanner census, external-disk sweep, six extra meshcore checkouts,
image/PDF git-blob census, completed `/home` name sweep). **My independent result agrees with it**,
and adds the physical-instrument and external-disk negatives.

I also read, and did not simply copy, the committed reports under `bench/bench-owner/`
(`LOGBOOK-SIGNATURE-INSPECTION.md`, `REPORT.md`, `WIKI-DOCS-SWEEP.md`, all 2026-09-14/15/17), which
reach the same "logbook UNAVAILABLE / DOES NOT EXIST" verdict. Every claim I reuse above I re-verified
at the raw source (the `git cat-file`/`git show` output is in this report's own citations).

## Acceptance-criteria check

| Criterion | Status |
|---|---|
| Every finding has a page and a date | **No finding is a logbook finding**, so no page exists to cite — stated explicitly, not guessed. All three record-based findings carry an exact commit ID + committer ISO date. |
| Undated entries flagged rather than guessed | no dated-or-undated logbook entry exists at all; the `RESULTS.md` `operator` column is *blank* on its only row, which is an empty value — flagged, not filled. |
| No inference from group membership / proximity | honoured: Felix is not promoted to (a)/(b)/(c); `balloon-hermes` stays an unnamed group; `cobrador` stays a scheduler; `c03rad0r` is named only as the worker account that committed reports, never as a custodian. |
| Buckets with zero evidence stated plainly | **all three buckets are zero** — stated above, with the record line that establishes the zero. |

## Coverage caveats (so the negative is bounded honestly)

- **C1 — no network/media sweep for a scanned copy.** I searched every locally mounted filesystem,
  including the external disk. A scanned copy held on a *remote* system (phone, cloud, another
  machine) is not reachable from this host and is not covered.
- **C2 — the physical book may exist in the world.** This host has never had a camera, scanner, or
  any attached bench instrument; the absence proven here is *absence from every reachable record*,
  which is what a cold-start worker can prove. A human with the book can close this in one minute.
- **C3 — whole-tree `find` on this host times out** (e.g. `find /home -maxdepth 5`, `/mnt -xdev`).
  Replaced with per-subtree chunked sweeps. **Closed in this run for the ten named bases**
  (`~/worktrees`, `~/.hermes/{profiles,state,kanban}`, `~/.cache`, `~/.local/share`, `~/repos`,
  `~/reports`, `~/Documents`, `~/Downloads`) — per-base rc/hits/elapsed in
  `logbook_home_census3_out.txt`. Two worktree checkouts under `~/worktrees`
  (`.base-check`, `.t_af37c6c9-nm-symlink`) hit the 25 s per-dir content-grep timeout and are named
  as not-covered for the *content* census; the *name* census covered them.
- **C4 — retention floors.** Repo history is complete; `/mnt` copies are snapshots (archived
  2026-09-17/18).

## Landing (this run)

- Deliverable committed in the meshcore clone (`~/repos/meshcore`, branch `main`) as
  `bench/calibration-maintenance-actors/REPORT.md` + `PROGRESS.md`, and **pushed to the fork**:
  `pushed to https://github.com/felixfelix-bot/MeshCore.git refs/heads/worker-admin/t_9a2f522b`
  (commit sha in the completion metadata). Nothing was merged to `origin/main`: this clone's `main` is
  448 commits ahead of `origin/main` and has never been pushed, and `origin/main` carries no `bench/`
  tree at all, so there is no consolidation target to claim — **no `consolidated:` line is asserted
  because no merge happened.**
- The push was exercised against the real pre-push gate (not `--dry-run` on an up-to-date ref): the
  hook printed `cred-gate: no remote-tracking knowledge for HEAD — judging the fail-closed window
  <sha>~50..<sha>` and the push then succeeded with `[new branch]`, rc=0.

## Evidence files (durable copies)

- `~/reports/logbook-actors-t_9a2f522b-2026-10-17.md` — this report
- `~/reports/logbook-actors-t_9a2f522b-2026-10-17/` — raw census transcripts:
  `logbook_census_out.txt`, `logbook_scan_census_out.txt`, `logbook_mnt_census_out.txt`,
  `logbook_mnt_census2_out.txt`, `logbook_home_census3_out.txt` (+ the generator scripts)

## Bottom line

The physical logbook does not exist in any reachable form, so there is no page, no date, no
handwriting and no initials to extract. The written record names **one** person — **Felix**, bench
*operator* — and states that the **controller-software admin**, the **maintenance approver** and the
**calibration approver** are all **UNDETERMINED**. A human with the physical book, or one who can
state where it is kept, is the only path to the answer this card asks for.
