# S2 fleet-queue-state — METHOD note

Access map cited S2 with: python3 -c "...len(json.load(open(fleet_queue_state.json))['claims'])"
Live count this run: 3703 claims. Full probe captured in calib-task-entries.json.txt:
- all 1779 'tasks' entries scanned; 43 whose title/body mention 'calib' exported verbatim
  (TASKKEY= lines; 7 by title). Every one is a fleet work-card ABOUT calibration (e.g. our own card
  meshcore:t_afd23162, calibration evidence hunts, model-fit tasks) — none is a
  calibration slot booking.
- claims/advertised/hold_denied/running/hold_skipped sections: 'calib' mentions = 0.

VERDICT: the fleet queue state is a task-dispatch ledger, not a calibration
scheduling system. It carries task metadata (actor, created_ts) but no
calibration-slot events, and its own history is not an audit log of lab
calibration edits.
