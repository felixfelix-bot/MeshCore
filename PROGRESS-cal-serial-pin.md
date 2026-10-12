# PROGRESS — pin `cal <k> <T0>` serial CLI syntax (meshcore passive_mapper)

task: pin byte-exact `cal <k> <T0>` grammar at commit 3fdfbc8e (feat/passive-mapper)
worktree: /home/c03rad0r/worktrees/cal-serial-pin
pin: 3fdfbc8e120e13d7543fe224c380e27533e720aa (git rev-parse HEAD, detached)
branch: worker-heavy/t_cal-serial-pin
commit 1: e4d8430985cc8baa224b4852baea26100e2c9a5c — PUSHED and verified
          (`git ls-remote … refs/heads/worker-heavy/t_cal-serial-pin` = same SHA)
artifacts: REPORT.md (repo root), PROGRESS.md (repo root),
           analysis/passive-mapper-cal-cli/{verify_citations.py,verify_citations.out}
copies for the requested workspace:
  /home/c03rad0r/repos/meshcore-fork-fix/REPORT-cal-serial-pin.md
  /home/c03rad0r/repos/meshcore-fork-fix/PROGRESS-cal-serial-pin.md

- finding: requested workspace /home/c03rad0r/repos/meshcore-fork-fix is CORRUPT
  (fetch -> "pack has 50 unresolved deltas"/"Could not read <oid>", 90 tracked
  files deleted in worktree, `git rev-parse 3fdfbc8e` -> malformed object name)
  -> status: worked around, fresh clone of felixfelix-bot/MeshCore at 3fdfbc8e
  -> files touched: (none in that repo)

- finding: remote feat/passive-mapper tip is now d7ae93fa (pin must be explicit)
  -> status: recorded in REPORT.md §0

- finding: no command TABLE; `cal` is an else-if branch of MyMesh::handleCommand
  (examples/passive_mapper/MyMesh.cpp:166), dispatched from main.cpp:88
  -> status: chain (a)-(e) located with file:line
  -> files touched: REPORT.md

- finding: parser = custom static parseFloat (MyMesh.cpp:128-143), called :170;
  order `cal <k> <T0>`; k ppm/C^2 positive magnitude only (k>=0.0f); T0 degC
  signed; no scaling, raw float32 memcpy into /selfcal.dat
  -> status: grammar pinned; model negates k at SelfCal.h:89
  -> files touched: REPORT.md

- finding: terminator MUST be CR (main.cpp:77 breaks only on '\r'); LF-only never
  dispatches; CRLF ok ('\n' swallowed at main.cpp:72); buffer 160B (main.cpp:15)
  -> status: pinned

- finding: persistence is IMMEDIATE in the `cal` branch (writeCalBlob MyMesh.cpp:270-281);
  no save/commit command exists (:183 lists all commands); no NVS/prefs in example
  -> status: answered YES-immediate; caveat: no flush() before close() -> platform SDK
  -> files touched: REPORT.md

- finding: citation verifier written -> analysis/passive-mapper-cal-cli/verify_citations.py
  -> status: run against `git show 3fdfbc8e:<path>`; 75 citations checked, 0 failures
     ("ALL CITATIONS VERIFIED AT PIN"), transcript in verify_citations.out
  -> files touched: analysis/passive-mapper-cal-cli/{verify_citations.py,verify_citations.out}

REMAINING: none. Task complete at commit e4d84309 (pushed).
