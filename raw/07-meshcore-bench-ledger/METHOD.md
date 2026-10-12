# S7 meshcore-bench-ledger — METHOD note (access regression)

The access map (t_ea0d0e46) cited S7 as:
  command: git -C ~/repos/meshcore log --format='%H|%cI|%an|%s' -- bench/
  observed at mapping time (2026-10-01): 63 bench/ commits, raw sample
  git-history.txt 99,972 B, 63 shaped rows. The clone sat on branch `main`
  at 32dd3204 with 63 UNPUSHED bench/ commits (origin/main at 07a3ca9e).

As of 2026-10-12T23:5xZ (this run):
- /home/c03rad0r/repos/meshcore no longer exists (deleted; ls: No such file or directory).
- Those 63 bench/ commits were never pushed (access map recorded them as unpushed),
  and no bundle/backup of the clone was found (searched ~/backups, *.bundle, other
  clone dirs). The S7 raw sample from the map (git-history.txt) is therefore not
  re-retrievable on this host.
- The successor ledger available in this workspace repo (meshcore-fork-fix, all refs)
  contains exactly ONE bench/ commit:
  c4499c19b84c2a8809a67a5bce8245c2b1b14502|2026-10-12T22:29:12+02:00|worker-base|worker-base@local|bench(cal): full conversion inventory from CAL-CLI-SPEC parser contract (t_bb4bbf91)
  (captured verbatim in git-ledger-fork-all-refs.txt next to this note).

'calib' relevance of the surviving bench/ commit: it is a CONVERSION INVENTORY for
the atcut-fit parser contract (cal <k> <T0> model-fit CLI), i.e. a CERTIFICATE/DATA
record analysis, not a calibration-slot scheduling event. No calibration-slot
create/edit/reschedule/delete/approve event exists in this source.