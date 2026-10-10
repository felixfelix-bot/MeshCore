# PROGRESS — FM-FT-MOUNT-01 (feedthrough mechanical mount, cold-loosening)

task: author ONE structured failure-mode entry for the feedthrough mechanical mount
      (feedthrough body vs panel differential contraction at −20 °C / −40 °C),
      four labelled attributes (a)-(d), >= 2 cited sources each carrying a number,
      ZERO mitigation / corrective-action content
worktree: /home/c03rad0r/worktrees/fe-feedthrough
branch: worker-base/t_feedthrough-mount-cold-loosening
base commit: 0679dbeffc504d562d2f09eb072fdc223f8ffc2a (felixfelix-bot/MeshCore main)
requested workspace: /home/c03rad0r/repos/meshcore-fork-fix (CORRUPT — see finding 1)

- finding: requested workspace is the same damaged clone the sibling task hit
  (git fetch -> "pack has 50 unresolved deltas"; 90 tracked files deleted in worktree;
  local main is 4 commits ahead of c03rad0r/MeshCore origin/main with the sibling
  failure-mode doc committed but UNPUSHED)
  -> status: worked around; fresh clone --reference/--dissociate of
     felixfelix-bot/MeshCore into ~/worktrees/fe-feedthrough at 0679dbe
  -> files touched: (none in the requested workspace yet)

- finding: worker branches for this profile live on the `bot` remote
  (felixfelix-bot/MeshCore), e.g. worker-base/t_* branches exist there
  -> status: push target = bot, branch worker-base/t_feedthrough-mount-cold-loosening

- finding: evidence gathered and each number read from the fetched document, not recalled:
  RF-LAMBDA RFCARASFSFP01A feedthrough bulkhead adapter datasheet (-55..+165 C op,
  45000 ft, 100% RH, 10 g rms, 20 G/11 ms, body SU303 stainless),
  Centric RF bulkhead JAMB NUT torque table (SMA stainless 12-15 in-lbs, brass 8-10 in-lbs),
  Engineering ToolBox CTE table (SS304 17.3, brass 18-19, Al 23, Al alloys 21-24,
  PTFE 112-135, alumina 8.1 ppm/K; unit printed "10^-6 m/m oC = 1 um/m oC"),
  Angst+Pfister O-Rings Technical Guide (compression set = permanent deformation,
  DIN 53517/ASTM D395 B, 25% compression, 24 h at +100 C; groove-depth table 1.50 mm cord
  at 20% -> D=1.20 mm; seal-force data quoted "at +20 C" only),
  CeramTec Ceramaseal catalogue (2500 psig @ 20 C, single pin 3500 psig, -269..+450 C, alumina),
  Kurt J. Lesker SMA CF feedthrough (cable connectors -65..+165 C, UHV, stainless pin + alumina),
  ERIKS VMQ silicone compound 714177 (70 IRHD, -55..+230 C)
  -> status: all raw fetches kept in ~/worktrees/fe-feedthrough-ev/ (outside git)
  -> files touched: (evidence dir only)

- finding: the preload arithmetic has to be stated as a model, because the *length* of the
  differential (~0.46/0.68 um over a 2 mm stack) is tiny while the *force* change is not:
  dF = d_alpha*dT / (1/(A_b E_b) + 1/(A_p E_p)) is length-independent for a metal path
  => 392 N (37% of F0) at -20 C, 589 N (55%) at -40 C for SS body in Al panel
  -> status: implemented as a deterministic companion calculator, output frozen
  -> files touched: analysis/failure-modes/feedthrough_mount_thermal_calc.py,
     analysis/failure-modes/feedthrough_mount_thermal_calc.out

- finding: the squeeze route is weak, the preload route is not, and the permanent paths
  (compression set, embedment, PTFE cold flow, nut position) are what make it irreversible
  -> status: reported honestly in §A/§B/§C rather than overstating the mechanism
  -> files touched: analysis/failure-modes/feedthrough-mount-cold-loosening.md

- finding: acceptance gate written and PASSING — attributes (a)-(d) present, template fields
  present, 7 sources each carrying a number, 35 quoted numbers cross-checked against the
  calculator transcript, mitigation lexicon empty in the entry body
  -> status: verify_entry.py exit 0, transcript in verify_entry.out
  -> files touched: analysis/failure-modes/verify_entry.py,
     analysis/failure-modes/verify_entry.out

commit 1: (this commit) analysis/failure-modes/{feedthrough-mount-cold-loosening.md,
  feedthrough_mount_thermal_calc.py, feedthrough_mount_thermal_calc.out,
  verify_entry.py, verify_entry.out} + PROGRESS.md
copies for the requested workspace: REPORT.md, PROGRESS.md and the entry itself are copied to
  /home/c03rad0r/repos/meshcore-fork-fix/ (untracked there — that clone cannot be pushed from)

REMAINING: none; push verification recorded in REPORT.md.
