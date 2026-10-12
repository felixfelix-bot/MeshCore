# S9 kanban-db — METHOD note (the only source with calibration-session audit events)

Access map (t_ea0d0e46) cited S9 as the meshcore kanban board DB:
  path: /home/c03rad0r/.hermes/kanban/boards/meshcore/kanban.db (SQLite)
  with the kanban DB having its OWN audit tables: task_events (kind, payload,
  created_at), task_comments (author, body, created_at), task_runs
  (profile, status, outcome, started/ended, summary).

All queries this run used SQLite read-only URIs (file:...?mode=ro). No writes.

## What qualifies as a "calibration slot" here
The fleet has NO dedicated booking system (proven by sibling cards: thermal
chamber bookings t_8e264236 -> "0 confirmed thermal chamber bookings exist";
reservation cards t_0d0fe29c/t_9782fb4c/t_42141f77/t_681802a8 all empty). The
ONLY object in any audited source that IS a scheduled calibration session for
an instrument/asset is kanban card **t_e1408991** — "Bench-calibrate
passive_mapper LR2021 thermal model (freezer sweep: k, T0) + die-vs-crystal
lag" (asset: NiceRF LR2021 module / SkyMapper Board A; window: one ~2-3 h
operator bench session at +40/+25/0/-20/-40/-55 C; owner/assignee: manager,
operator Felix) — plus its 4 decomposed session steps:
  t_a132b6cd  Capture raw LR2021 thermal dataset (freezer dwell sweep + ramp)
  t_20f98f15 Fit AT-cut thermal model (k, T0) from freezer-sweep data
  t_380a431f Characterize die-vs-crystal thermal lag from ramp logs
  t_bef90304 Apply cal blob on module, verify, record per-module values

## Files captured (all verbatim, stable line ids = DB primary keys)
- calibration-session-events.txt — every task_events row (ev-<id>) and every
  task_comments row (cm-<id>) for the 5 cards, with created_at as unix AND UTC
  ISO, payload verbatim. RECON lines at the bottom give the per-card GROUP BY
  counts (167 events, 49 comments total) for reconciliation with the DB's own
  view.
- calibration-session-runs.txt   — every task_runs row (run-<id>) for the 5
  cards (16 runs), verbatim.
- calibration-tasks-events-comments.txt — the earlier broader probe: all 21
  cards whose TITLE mentions calib, with their non-heartbeat events and
  comments (proves none of the other 16 is a slot: they are analysis/audit
  work cards ABOUT calibration).

## Line-id convention
ev-<task_events.id> / cm-<task_comments.id> / run-<task_runs.id> — primary
keys, stable across re-dumps.

## Timezones
task_events.created_at and task_comments.created_at are unix epochs, stored
UTC; converted with datetime.fromtimestamp(ts, timezone.utc). No local-offset
timestamps exist in this source.