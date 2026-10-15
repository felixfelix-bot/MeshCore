# PROGRESS — esp32-* repo family recon (shard: READ-ONLY raw-hit list)

Task: scan esp32-tollgate, esp32-mesh and other esp32-* repos for
shadow-card / human-gate / board-approval / gating-mechanism references.
Excluding esp32-balloon-integration (owned by another shard).
READ-ONLY on scanned repos: no edits, no checkouts, read-only git only.

findings -> status -> files touched

1. CWD `/home/c03rad0r/repos/meshcore-fork-fix` contains NO esp32-* dirs -> used the real
   locations: /home/c03rad0r/esp32-mesh, /home/c03rad0r/repos/tollgate-esp32,
   /home/c03rad0r/wisp-esp32, plus non-git dirs. -> DONE -> none
2. Branch worker-base/esp32-recon created at pushed tip dc5c8d6 (was on
   worker-heavy/t_a7558e8c). -> DONE
3. Rev enumeration: esp32-mesh 12 heads + 1 tag; esp32-tollgate 1 head + 3 origin
   balloon branches + master/upstream/master + v1.4.0 + v-balloon-pre-strip;
   wisp-esp32 main + fork/balloon-nostr-extraction. -> DONE -> raw/esp32-recon/scan.sh
4. Raw grep corpus: 15349 hit lines, 3668 unique (repo,path,line,text). -> DONE ->
   raw/esp32-recon/out/raw-hits.tsv
5. Mechanical narrowing pass 2: 89 candidates, 3579 dropped. -> DONE ->
   raw/esp32-recon/triage2.py, out/candidates2.tsv, out/dropped2.tsv
6. Paragraph contexts extracted for all 89 candidates. -> DONE ->
   raw/esp32-recon/out/contexts2.txt
7. Per-hit keep/drop reading of all 89 contexts. -> IN PROGRESS
8. Write REPORT.md (raw-hit list, ROOTS SCANNED, ZERO-HIT ROOTS, discarded-by-narrowing).
9. Commit + push. Final reply points at REPORT.md.

Key early facts (verified by grep, not inferred):
- `shadow card` / `shadow-card`: ZERO hits in every rev of every scanned repo.
- `human gate` / `human-gate`: ZERO hits in every rev of every scanned repo.
- raw hits are dominated by the substring "tollgate" matching /gate/.
- docs/adr/ADR-001-tollgate-over-lr2021.md exists ONLY on
  remotes/origin/balloon-tollgate-c3-port; docs/adr/ADR-XXX-balloon-stratum-relay.md
  ONLY on remotes/origin/balloon-pow-e-hash and remotes/origin/balloon-pow-extraction;
  tollgate-esp32 master has NO ADR/decision/rfc-named files.
