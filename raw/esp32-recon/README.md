# esp32-* repo family — read-only recon pipeline

Task: raw-hit list for the `esp32-*` family (shard scan; see
`../REPORT-esp32-family-raw-hits.md`). **Read-only w.r.t. all scanned repos** — every
script only runs `git grep` / `git show` / `git log` / `git for-each-ref` or opens files
for reading. Nothing is written outside this directory.

## Reproduce

    cd /home/c03rad0r/repos/meshcore-fork-fix
    bash  raw/esp32-recon/scan.sh  raw/esp32-recon/out     # 1. raw hits, all revs + non-git trees
    python3 raw/esp32-recon/triage.py                      # 2. mechanical split
    python3 raw/esp32-recon/substantive.py                 # 3. drop 'tollgate'-substring noise
    python3 raw/esp32-recon/build_report.py                # 4. classify -> rows-*.tsv
    python3 raw/esp32-recon/revs.py                        # 5. per-rev counts + zero-hit revs
    python3 raw/esp32-recon/contexts.py                    # 6. paragraph + full-file context
    python3 raw/esp32-recon/build_md.py                    # 7. assemble the report
    python3 raw/esp32-recon/verify.py                      # 8. assert every quote is verbatim

Scripts still contain the absolute output path (`raw/esp32-recon/out`) used at run time;
step 2 is superseded by step 4 for classification (triage.py kept for the raw mechanical
split record).

## Roots

| label | path | kind |
|---|---|---|
| esp32-mesh | `/home/c03rad0r/esp32-mesh` | git (13 branches + tag `v0.1.0`) |
| esp32-tollgate | `/home/c03rad0r/repos/tollgate-esp32` | git (master + 3 origin branches + 9 `archive/*` tags + `v1.4.0`, `v-balloon-pre-strip`) |
| wisp-esp32 | `/home/c03rad0r/wisp-esp32` | git (matches the `esp32-*` discovery glob via `wisp-esp32`) |
| esp32-tollgate-relay | `/home/c03rad0r/esp32-tollgate-relay` | non-git tree (no history → no dates) |
| esp32-repeater-captive-portal | `/home/c03rad0r/esp32-mesh/esp32-repeater-captive-portal` | non-git tree, zero hits |
| esp32-balloon-integration-meshcore-pr | `/home/c03rad0r/esp32-balloon-integration-meshcore-pr` | non-git worktree (balloon material; owned shard) |
| ailaptop-migration/esp32-tollgate | `/home/c03rad0r/repos/ailaptop-migration/esp32-tollgate` | git, master = tollgate-esp32 master |
| ailaptop-migration/esp32-mesh | `/home/c03rad0r/repos/ailaptop-migration/esp32-mesh` | git, master has no commits |

## Artifacts

| file | contents |
|---|---|
| `out/raw-hits.tsv` | every matching line: repo, path, line, rev, text |
| `out/substantive.tsv` | hits whose term survives removal of the `tollgate` substring |
| `out/rows-kept.tsv` | §4a `recreated` rows |
| `out/rows-ambiguous.tsv` | §4b `ambiguous` rows |
| `out/rows-dropped-{board,gate,other}.tsv` | §5 narrowing discards |
| `out/revs.tsv` | per-rev raw/substantive counts + which scanned rev string produced them |
| `out/contexts.txt` | ±3-line window per §4 row + full body of each step-4 filename keep |
| `out/candidates.tsv`, `out/dropped.tsv`, `out/nameonly.tsv` | step-2 mechanical split |
