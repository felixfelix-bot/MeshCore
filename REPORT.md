# REPORT — t_afd23162: Extract audit/edit history for calibration slots

**Repo:** meshcore-fork-fix · **Branch:** `worker-heavy/t_afd23162` (pushed to `bot` remote =
felixfelix-bot/MeshCore, every commit verified via `git ls-remote`) · **Host:** CobridorWave ·
**Date:** 2026-10-12

## Deliverables

- `records/calibration_slots.csv` — 156 rows: 143 audit/edit rows + 13 explicit NO AUDIT LOG rows
- `records/calibration_slots_gaps.md` — gaps note (4 downstream-only edits) + slot-vs-certificate distinction
- `raw/01..12`, `raw/02b`, `raw/09b` — verbatim raw exports + METHOD notes for every mapped source (26 files)
- `analysis/t_afd23162/` — reproducible read-only dump scripts (SQLite `mode=ro`, no writes anywhere)

## Access map reconstruction (parent task t_ea0d0e46, index 0)

The map's deliverable dir `~/reports/audit-log-access-map-t_ea0d0e46-2026-10-01/` is GONE from
disk. The 15-source list (S1..S12 + S2b + S9b) was reconstructed verbatim from the parent
card's `result` text in the meshcore kanban DB, and every source was re-probed live this run.
Three access regressions vs the map were found and documented:
- `~/repos/meshcore` GONE with 63 unpushed bench commits (map noted local main 32dd3204 vs
  origin 07a3ca9e) — S7 ledger unrecoverable, METHOD note records it.
- `~/repos/balloon` GONE — S4's FLASH-QUEUE survives identically in `balloon-fresh` (same
  SHAs), captured there.
- fleet event journal MOVED from `~/.hermes/bot/` to `~/.hermes/state/fleet-private/` —
  re-located and captured.
- S8's dangling blob `d7ae93fa` was recovered from the `bot` remote via a fresh partial clone.

## What a "calibration slot" turned out to be

This fleet has NO booking/scheduling system for lab instruments (proven by sibling cards:
`t_8e264236` → "0 confirmed thermal chamber bookings exist"; reservation cards
`t_0d0fe29c/t_9782fb4c/t_42141f77/t_681802a8` all empty; the "thermal chamber" is a domestic
freezer). The ONLY object in any audited source that IS a scheduled calibration session for an
instrument is kanban card **t_e1408991** — "Bench-calibrate passive_mapper LR2021 thermal
model (freezer sweep: k, T0) + die-vs-crystal lag" — plus its 4 decomposed session steps
(t_a132b6cd, t_20f98f15, t_380a431f, t_bef90304). Asset: NiceRF LR2021 module (SkyMapper
Board A / spare). Window: one ~2–3 h operator bench session at +40/+25/0/-20/-40/-55 °C.
Owner: assignee manager, operator Felix (c03rad0r). The session NEVER ran — it has been
parked on an operator-action capability block since 2026-09-11.

## S9 kanban DB — the only source with an audit log over the slot

Exported verbatim (line ids = DB primary keys, stable):
- 167 task_events (89 heartbeats excluded from rows), 49 task_comments, 16 task_runs across
  the 5 cards → 143 CSV rows, each carrying: slot id (asset+window+owner), editor account,
  UTC datetime (unix epochs stored UTC; the source holds no local-offset timestamps), action
  type (create / edit / reschedule / comment / approve-complete-writeback), and the byte-exact
  raw line + path + line id.
- Reconciliation: per-card CSV counts (43/29/27/27/17) match the source's own RECON GROUP BY
  lines exactly.

## The other 13 sources — explicit NO AUDIT LOG rows

Each CSV row carries the reason; each `raw/<source>/METHOD.md` carries the evidence:
- S1 evolution-calendar: the only ICS is an EMPTY VCALENDAR — zero events, no history.
- S2 fleet-queue-state: dispatch ledger; 43 calib mentions are all work-cards ABOUT
  calibration, none a slot.
- S2b fleet-event-journal: 16 calib lines exported verbatim — all dispatch events, no slot ops.
- S3 peripheral-locks: board FLASH locks (tx/rx/board-a/b/c), 0 calib hits.
- S4 flashqueue-balloon (regression): balloon repo gone; twin captured from balloon-fresh;
  flash queue, 0 calib hits.
- S5 flashqueue-e80bench: flash access queue, 0 calib hits.
- S6 balloon-fresh-canonical: git history holds no calibration-slot records.
- S7 meshcore-bench-ledger (regression): repo gone, 63 unpushed bench commits lost; fork
  refs carry 0 bench commits.
- S8 fork-results-md: this is the CERTIFICATE record (per-module cal table), noted
  separately per task rules — and it is EMPTY (header only): no calibration ever recorded.
- S9b stackstr-schedule: the stackstr board's only task is an nsite dashboard job.
- S10 nostr-strfry-relay: full 500-event window (server cap) fetched, 0 calib mentions.
- S11 docs-wiki-spreadsheets: wiki (246 files) 0 calibration hits; no booking spreadsheet
  exists on the host.
- S12 physical-site: no logbook/sign-up sheet/nameplate ever located; headless host.

## Gaps — slot edits appearing only in downstream records (4)

1. `t_a132b6cd` cm-69 "fleet-done rc=0 (offloaded); status -> done" (2026-09-12T09:22:19Z) —
   no `completed` task_event exists; card is now `blocked`, completed_at=None. The done
   transition exists ONLY as this writeback record.
2. `t_20f98f15` cm-3352 "fleet-done rc=0 verified=True; status -> done" — card status is
   done but NO `completed` audit event exists.
3. `t_380a431f` cm-3351 — same shape as #2.
4. `t_bef90304` cm-3595 — same shape as #2.

Full text in `records/calibration_slots_gaps.md`, including the slot-vs-certificate
distinction (rows mentioning bench/RESULTS.md are scheduling events quoting the runbook; the
certificate table itself is empty and captured at raw/08-fork-results-md/RESULTS.md; cm-52's
k=0.04174/T0=21.92 C is a SIMULATED kit self-test, not a recorded calibration).

## Verification (all observed in tool output)

- 156 CSV rows; every row cites a raw path + content (0 missing refs).
- S9 quoted lines are byte-exact against the raw export (0 mismatches, programmatically
  asserted for all 143).
- Per-card counts reconcile with the DB's own GROUP BY view (RECON lines).
- 13 sources × 1 NO AUDIT LOG row each, with reasons.
- 4 gaps enumerated from an exhaustive fleet-writeback-vs-task_events scan.

## Push log (all verified via git ls-remote on `bot`)

7e57acc → 7b145bc → b915ff8 → d410665 → 458736b → final commit (REPORT + PROGRESS).
Remote ref: `refs/heads/worker-heavy/t_afd23162` on felixfelix-bot/MeshCore.