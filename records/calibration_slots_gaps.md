# Gaps note — calibration slot edits with no owning audit entry

Rule: list any slot edits that appear only in a downstream record with no owning
audit entry. Scanned: all fleet-writeback comments claiming status edits on the
five calibration-session cards vs the task_events audit log.

- t_a132b6cd: comment cm-69 (fleet-done rc=0 (offloaded); status -> done) claims 'status -> done' but NO 'completed' task_event exists and the card is now 'blocked' with completed_at=None — the done transition exists only as this downstream writeback record, with no owning audit entry in task_events.
- t_20f98f15: comment cm-3352 (fleet-done rc=0 verified=True (offloaded); status -> done) claims 'status -> done'; card status is 'done' but NO 'completed' task_event exists in the audit log (status field edited without an audit event).
- t_380a431f: comment cm-3351 (fleet-done rc=0 verified=True (offloaded); status -> done) claims 'status -> done'; card status is 'done' but NO 'completed' task_event exists in the audit log (status field edited without an audit event).
- t_bef90304: comment cm-3595 (fleet-done rc=0 verified=True (offloaded); status -> done) claims 'status -> done'; card status is 'done' but NO 'completed' task_event exists in the audit log (status field edited without an audit event).

Additional downstream-only records noted (not slot edits):
- Certificate/data record: examples/passive_mapper/bench/RESULTS.md is the
  per-module calibration RESULT table (module id, k, T0, span, residual, tau, blob hex).
  As of this extraction it contains an EMPTY row header only — no certificate data
  has ever been recorded, because the calibration session itself never ran
  (t_e1408991 blocked on operator bench action since 2026-09-11).
  Verbatim: raw/08-fork-results-md/RESULTS.md
