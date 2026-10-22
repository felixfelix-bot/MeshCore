# PROGRESS — t_9a2f522b (calibration/maintenance actors from the physical logbook)

Run 1: 2026-10-17, worker-admin, host dq05, worktree /home/c03rad0r/worktrees/t_e1408991 — ended
`timed_out` at the iteration cap with the report already drafted on disk.

- Card read; scope = physical logbook ONLY (no chat search on this card; sibling t_6806d82c does chat).
- LOG-1 finding: no physical logbook, no scanned copy, no transcription exists in any reachable
  source. Existence negative, not a denied read. Files: _logbook_census_t_9a2f522b.py,
  _logbook_scan_census_t_9a2f522b.py, _logbook_mnt_census*_t_9a2f522b.py, logbook_*_census*_out.txt
- LOG-2 finding: the only written role determination is committed in meshcore:
  Felix = bench operator/custodian (d7ae93fa 2026-09-11); controller-software admin, maintenance
  approver and calibration approver all UNDETERMINED (11e43b0a 2026-09-14T10:53:50+02:00,
  re-affirmed 4b3ec9b5 2026-09-14T12:08:32+02:00). All three target buckets = ZERO evidence.
- LOG-3 finding: prior art on another host (CobradorWave, t_c2a72059, 2026-10-12) reached the same
  empty-input verdict; read and independently re-derived here (broader sweep, not copied).
- Gate dry-run vs DEPLOYED engine: tier=docs, verdict=warn, missing=['pushed_or_consolidated'],
  secrets=[]. Fixed in run 2 by an actual push (below), not by writing a line without a landing.

Run 2 (this commit), same worktree:

- Re-measured all three record findings fresh by SHA (d7ae93fa / 11e43b0a / 4b3ec9b5, committer
  dates re-quoted from `git cat-file`).
- NEW sibling record read: bench/bench-owner/ gained b965d242 / 36ad9d6a / 215c8c55 on 2026-10-17;
  215c8c55 corrects an earlier claim and establishes that FLASH-QUEUE.md DOES exist (3 copies), the
  host's only filled approver cell `felix (orchestrator)` is on the e80-bench copy (a DIFFERENT
  bench), the meshcore-bench copy's queue is EMPTY, and `cobrador` = fleet scheduling (HIGH).
  Neither is promoted into buckets (b)/(c).
- Coverage C3 CLOSED for the ten named bases. Three passes were needed:
  * run 1's background pass wrote 1 line and was killed before finishing (no coverage record left);
  * sixth-pass rewrite returned rc=2 for EVERY base — a mis-grouped `find` predicate
    (`\( -name .git -prune \) -o NAMES -print`), i.e. a syntax error, NOT a negative result;
  * seventh pass (_logbook_home_census3_t_9a2f522b.py) uses the correct grouping, sanity-checks its
    own predicate per base (rc ∈ {0,1} else HOME_PREDICATE_INVALID), and its per-base rc/hits/elapsed
    output is logbook_home_census3_out.txt.
- LANDED: bench/calibration-maintenance-actors/{REPORT.md,PROGRESS.md} committed in this clone and
  PUSHED to the fork as refs/heads/worker-admin/t_9a2f522b. No `consolidated:` line is claimed — this
  clone's main is 448 commits ahead of origin/main and origin/main has no bench/ tree, so no merge
  target exists.
- PUSH note for future workers: meshcore `main` is ~448 commits ahead of origin/main and has never
  been pushed; bench reports are published as fork branches `worker-<profile>/t_<card>`.

Run 3 (run 2130, this dispatch) — re-verification close, nothing re-authored:

- The card was re-dispatched after run 2 capped out at the iteration budget AFTER its commit had
  already landed and been pushed. Run 3 therefore re-measured the DoD read-only instead of redoing
  the search, and added a Run-3 section to the report.
- Re-measured unchanged: `/dev/video*` NONE; `v4l2-ctl`/`fswebcam` ABSENT; `lsusb` = 4 hubs + BT
  radio + Lexar ES4 + Zoran USB-audio-HID, no scanner/camera; cited commits d7ae93fa
  (2026-09-11T11:24:09+05:30), 11e43b0a (2026-09-14T10:53:50+02:00) and 4b3ec9b5
  (2026-09-14T12:08:32+02:00) all present with the quoted lines intact; fork ref
  `worker-admin/t_9a2f522b` = bdbe1f4f…; committed REPORT == worktree copy (cmp IDENTICAL).
- Two deltas recorded: (a) `sane-find-scanner`/`scanimage` are now INSTALLED (run 2 measured them
  absent) yet still enumerate NO scanner-class device — a stronger, measured negative;
  (b) the host's only filled approver cell now has an exact date: e80-bench/docs/coordination/
  FLASH-QUEUE.md line 10, 2026-08-20T09:00Z, `felix (orchestrator)`, E80 FLASHING — different bench,
  still not a finding for buckets (a)-(c).
- Run-3 census caveat: the bounded name re-census timed out (rc=124) on ~/repos and ~/worktrees;
  those two bases rest on run 2's completed per-base census. A timed-out `find` is not a negative.
- Transcripts: verify_out_t_9a2f522b_run2130.txt, verify2_out_t_9a2f522b_run2130.txt — durable copies
  under ~/reports/logbook-actors-t_9a2f522b-2026-10-17/.
