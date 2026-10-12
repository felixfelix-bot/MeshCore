# PROGRESS - bench frequency-instrument inventory

task: on-bench inventory of frequency-measurement / generation / reference instruments
workspace: /home/c03rad0r/repos/meshcore-fork-fix
branch: worker-base/bench-freq-instrument-inventory
status: DONE (deliverable = blocked-work report; 0 real instrument rows, 0 fabricated values)
last commit: 17a0545  (pushed to bot -> felixfelix-bot/MeshCore, remote sha verified == local)

## Log
- finding: task demands PHYSICAL reading of labels at a bench; this worker is a shell agent with no camera/operator.
  status: confirmed on-box; verified no instrument connectivity (`/dev/usbtmc*` / `/dev/gpib*` absent; only serial devs = laptop's own Sierra EM7455 LTE modem; lsusb shows no test gear)
  -> files: none
- finding: `~/bench-images/` is a misnomer (OpenWrt .bin/.apk only). No bench photos, no prior inventory doc, no kanban card with instrument text.
  status: exhausted legitimate data sources -> files: none
- decision: DO NOT fabricate rows/serials. Produce schema-complete blocked report + human fill-in worksheet.
  status: written -> files: REPORT-bench-frequency-instrument-inventory.md
- push: origin (c03rad0r/MeshCore) returned 403 for the active felixfelix-bot credential; pushed to `bot` remote instead.
  status: SUCCESS - git ls-remote bot refs/heads/worker-base/bench-freq-instrument-inventory == 17a05456cde5ab9a001d1a6c52322bff9e9113ad
- commit hygiene: only my 2 files committed (explicit pathspec); pre-existing working-tree deletions left untouched.
  status: verified via git show --stat

## Remaining steps (for the human at the bench)
1. Walk the bench rack by rack, shelf by shelf, L->R, one full pass; second pass for serials + rear ref ports.
2. Fill the worksheet in REPORT-bench-frequency-instrument-inventory.md section 5 (one block per instrument).
3. Replace the two §1 placeholder rows with the real table (or re-request this task with the raw data / instrument photos).
4. Record any pure ref source (rubidium/GPSDO/OCXO) as a single line only; log unknown-identity devices in §2 UNIDENTIFIED.
5. Recompute the closing count = real table rows + UNIDENTIFIED entries, and list inaccessible areas.
