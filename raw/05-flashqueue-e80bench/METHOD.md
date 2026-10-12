# S5 flashqueue-e80bench — METHOD note

Access map (t_ea0d0e46) cited S5 as:
  path: /home/c03rad0r/repos/balloon-e80bench/docs/coordination/FLASH-QUEUE.md
  command: git -C ~/repos/balloon-e80bench log --format='%H|%cI|%an|%aE|%s' -- docs/coordination/FLASH-QUEUE.md

Both re-run this run (2026-10-12) — source still live on disk:
- FLASH-QUEUE.md  — verbatim byte copy of the file (2,739 bytes).
- git-ledger.txt  — verbatim output of the map's git-log command over the file's history
  (commit|author-date ISO +0530|author name|author email|subject).

Content: board FLASH access coordination queue ("NO flashing without orchestrator
(balloon-hermes) approval"), with board-hold rows (E80 boards, C3, RP2040).
'calib' grep: 0 hits. All rows are flash/hold sessions, not calibration windows.

VERDICT: S5 is an audit ledger of board flash access. It contains NO calibration-slot
create/edit/reschedule/delete/approve events and does not manage instrument
calibration scheduling at all. Kept for completeness because the access map flagged
it as a live audit-bearing source.