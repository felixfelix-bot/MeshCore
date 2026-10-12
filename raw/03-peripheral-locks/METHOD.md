# S3 peripheral-locks — METHOD note

Access map (t_ea0d0e46) cited S3 with command: ls -la $HOME/.hermes/peripheral_locks/
Retrieved this run: peripheral-locks-dump.txt (verbatim content of all 4 files:
THEFT-LOG, balloon-tx.lock, board-lock-monitor.json, board-lock-theft.log).

Content: board resource locks (tx/rx/board-a/board-b/board-c) for balloon flash
coordination; one stale-lock simulation (holder "test-stale", 2026-07-24) and two
SIGTHEFT log lines (2026-07-23). 'calib' grep: 0 hits.

VERDICT: this source is an audit log of BOARD FLASH ACCESS, not calibration
scheduling. No calibration-slot create/edit/reschedule/delete/approve events.
It does not manage instrument calibration windows at all.
