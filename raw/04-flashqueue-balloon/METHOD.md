# S4 flashqueue-balloon — METHOD note (access regression)

The access map (t_ea0d0e46) cited S4 as /home/c03rad0r/repos/balloon/docs/coordination/FLASH-QUEUE.md
with git ledger command: git -C ~/repos/balloon log --format='%H|%cI|%an|%s' -- docs/coordination/FLASH-QUEUE.md

As of 2026-10-12T23:4xZ this path no longer exists: /home/c03rad0r/repos/balloon is GONE
(ls: No such file or directory). The canonical successor with identical FLASH-QUEUE.md content
and identical commit SHAs (same git history) is /home/c03rad0r/repos/balloon-fresh
(access-map S6 target, formerly 'ABSENT-balloon-fresh-canonical').

Captured this run:
- FLASH-QUEUE-balloon-fresh.md  (verbatim file, byte copy)
- git-ledger-all-refs.txt       (git log --all -- docs/coordination/FLASH-QUEUE.md, verbatim)

'calib' grep on the file: 0 hits. No calibration-slot create/edit/reschedule/delete/approve
event exists in this source. FLASH-QUEUE rows are board-flash access requests (track, board,
purpose, requested_time, approved_by, duration, status) — board flashing, NOT instrument
calibration scheduling.
