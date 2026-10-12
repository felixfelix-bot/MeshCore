# PROGRESS — t_afd23162: extract audit/edit history for calibration slots

repo: meshcore-fork-fix
branch: worker-heavy/t_afd23162
workspace: /home/c03rad0r/repos/meshcore-fork-fix

## Log
- finding: card t_afd23162 (triage, worker-heavy) = extract edit/audit timeline for
  CALIBRATION SLOTS from every source the access map (parent index 0) flagged.
  status: read from kanban DB read-only (t_afd23162 body, comments 7482/8112/8217).
  files: analysis/t_afd23162/ (planned)
- finding: access map = card t_ea0d0e46 (done, worker-admin). Its deliverable
  ~/reports/audit-log-access-map-t_ea0d0e46-2026-10-01/ NO LONGER EXISTS on this host;
  scratch workspace /home/c03rad0r/worktrees/t_e1408991 contains only
  added-insertion-loss-analysis.md. Source list reconstructed from t_ea0d0e46 RESULT:
  15 sources S1,S2,S2b,S3,S4,S5,S6,S7,S8,S9,S9b,S10,S11,S12 (S4/S5 both flashqueues,
  3 negatives S6/S11/S12), raw/ 18 files, all cited paths re-checked this run.
  status: confirmed (DB read + filesystem probes)
  files: analysis/t_afd23162/kanban_dump.py
- finding: S2b raw journal events-cobrador.jsonl is GONE from
  /home/c03rad0r/.hermes/bot/peers/ (only dq05/hermes-nvme/t440/testserver2/x240/x280
  remain). S7 clone ~/repos/meshcore is GONE. This host = cobrador worker node.
  status: confirmed; recorded as access regressions in gaps note.
  files: raw/*/ (planned)

## Remaining
1. Probe all 15 sources for calibration-slot create/edit/reschedule/delete/approve events.
2. Capture raw exports; write records/calibration_slots.csv + gaps.md.
3. Verify reconciliation, commit + push.