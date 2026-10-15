# PROGRESS — esp32-* repo family raw-hit recon (shard)

Task: READ-ONLY RECON. Raw-hit list for the `esp32-*` repo family (excluding
`esp32-balloon-integration`, owned by another shard). No file in any scanned repo was
created/edited/deleted; no branch checked out or switched; read-only git only.

Branch: `worker-base/esp32-recon`  ·  Deliverable: `raw/esp32-recon/REPORT.md`

## Log (finding -> status -> files touched)

- Workspace `/home/c03rad0r/repos/meshcore-fork-fix` has NO `esp32-*` dir -> found the family
  on the host: `/home/c03rad0r/esp32-mesh`, `/home/c03rad0r/repos/tollgate-esp32` (= the
  `esp32-tollgate` repo), `wisp-esp32`; non-git: `esp32-tollgate-relay`,
  `esp32-mesh/esp32-repeater-captive-portal`, `esp32-balloon-integration-meshcore-pr`. DONE.
- All revs enumerated (`git for-each-ref` heads/tags/remotes): 13 esp32-mesh, 16 esp32-tollgate,
  5 wisp-esp32, + non-git trees as-is. Aliases (`origin/master` == `master`) matched by commit SHA. DONE.
- Raw scan (18603 matching lines) -> `out/raw-hits.tsv`; substantive after dropping the
  `tollgate` substring (1303) -> `out/substantive.tsv`. DONE.
- Narrowing: 1095 hardware/PCB `board` discards, 196 non-approval `gate` discards,
  0 substring-only. Kept 1 (`gatekeeper`, out-of-shard balloon worktree) + 11 `ambiguous`
  (payment/access gating, one Nostr-approval path). DONE.
- `shadow card` / `human gate`: ZERO hits across every rev of every git root and all non-git
  dirs. Supplementary approval-vocabulary probe: 1 hit total (the same `gatekeeper` line). DONE.
- Step-4 filename rule (ADR-*/decision/rfc/design-review-notes): 13 files, all git; 9 balloon
  ADRs are hardware/radio decisions, 4 tollgate balloon ADRs carry the `ambiguous` rows. DONE.
- verify.py asserts every S4 quote is verbatim at the stated line: 12/12 OK, 0 problems. DONE.
- Branch created + milestone 1 committed `05991ba` and pushed. DONE.
- Milestone 2 committed `4f2711a` and pushed; `git ls-remote bot` == local HEAD (verified). DONE.

## Milestones (pushed)

| commit | contents |
|---|---|
| `05991ba` | raw-hit corpus (`scan.sh`, `triage.py`, `out/raw-hits.tsv`) + first `PROGRESS.md` |
| `4f2711a` | REPORT.md, per-rev table, zero-hit roots, rows-*.tsv, contexts, verify.py, README |

## Status: COMPLETE

All task steps (1-4) executed and the OUTPUT deliverable produced. No REMAINING steps.
No cross-repo narrowing/merge conclusions drawn (left to the downstream task).

Pipeline note: `rows-*.md` intermediates were removed because the global pre-commit secret
hook false-positived on hash-like columns in them; `build_md.py` renders the report directly
from the `rows-*.tsv` artifacts.
