# REPORT — esp32-* repo family: raw-hit list (shard scan)

**Task:** READ-ONLY RECON shard. Produce the raw-hit list for the `esp32-*` repo family,
excluding `esp32-balloon-integration` (owned by another shard; material only under the
hyphen-variant `esp32-balloon-integration-meshcore-pr` was reachable in this shard's roots and is
listed below because it matched the discovery step, flagged as out-of-shard where relevant).

**Repo:** meshcore-fork-fix · **Branch:** `worker-base/esp32-recon` · **Host:** CobridorWave · **Date:** 2026-10-15

**Constraints honoured:** no file in any scanned repo was created, edited or deleted; no branch
was checked out or switched; only read-only git commands were used (`git grep <rev>`, `git show <rev>:<path>`, `git log`, `git worktree list`, `git branch -a`, `git for-each-ref`, `git ls-tree`, `git cat-file -e`). Non-git dirs were read with `grep -rniE`. All writes landed in
this worktree only. No cross-repo narrowing/merge conclusions are drawn here.

**Path convention** in the tables: `` `esp32-tollgate:docs/PLAN.md:34` `` — repo-root-relative
path for git roots, absolute path for non-git worktrees. Required column order is preserved
(`path:line` first).

## 1. ROOTS SCANNED

The task's stated workspace root `/home/c03rad0r/repos/meshcore-fork-fix` contains **no** `esp32-*`
directory (`ls -d esp32-*` and `find . -maxdepth 2 -type d -name 'esp32-*'` are both empty), so the
family was located on the host (`find /home/c03rad0r -maxdepth 3 -type d -name 'esp32-*'`) and every
candidate was scanned:

| root | kind | revs scanned | note |
|---|---|---|---|
| `/home/c03rad0r/esp32-mesh` | git worktree, repo root | 12 heads + 1 tag (`refs/stash` excluded, no tree) | the `esp32-mesh` repo; primary rev `feature/redeem-ecash` |
| `/home/c03rad0r/repos/tollgate-esp32` | git worktree, repo root | `master`, 3 `origin/balloon-*` branches, `origin/master`, `upstream/master`, `v1.4.0`, `v-balloon-pre-strip`, 8 `archive/*` tags | this is the `esp32-tollgate` repo (dir name differs; remote = felixfelix-bot/tollgate-esp32) |
| `/home/c03rad0r/wisp-esp32` | git worktree, repo root | `main`, `fork/balloon-nostr-extraction`, `origin/main`, `origin/feature/subscription-manager` | discovered esp32-* family member |
| `/home/c03rad0r/esp32-tollgate-relay` | NOT a git worktree | current tree, as-is | plain `grep -rniE` |
| `/home/c03rad0r/esp32-mesh/esp32-repeater-captive-portal` | nested non-git dir | current tree, as-is | plain grep; 0 hits |
| `/home/c03rad0r/esp32-balloon-integration-meshcore-pr` | broken git worktree (its `.git` points at a deleted `/home/c03rad0r/esp32-balloon-integration/.git/worktrees/...`) | current tree, as-is | non-git fallback; **out of this shard's ownership**, listed only because discovery matched it |
| `/home/c03rad0r/repos/ailaptop-migration/esp32-tollgate` | bare git dir (not a worktree) | `master` | mirror |
| `/home/c03rad0r/repos/ailaptop-migration/esp32-mesh` | bare git dir | none — `master` has **no commits yet** | mirror is empty |
| `/home/c03rad0r/repos/ailaptop-migration/esp32_balloon_integration` | bare git dir | not scanned (out of shard) | balloon = other shard |

`esp32-balloon-integration` itself was **not** scanned (other shard owns it), per the task.

## 2. Per-rev scan table

Commands: `git grep -niE 'shadow.?card|human.?gate|board|gate' <rev> -- '*.md' '*.txt' '*.rst'`
(per-rev `git worktree list` / `git branch -a` first). `raw` = matching lines; `substantive` = matching lines that still match after the project-name substring `tollgate` is
removed (i.e. the line has a standalone `board` / `gate` / `shadow-card` / `human-gate` token).
Rev-list for each repo was enumerated with `git for-each-ref` over `refs/heads refs/tags refs/remotes`.

| repo | rev | raw match lines | substantive | scanned? |
|---|---|---|---|---|
| esp32-mesh | `captive-portal-opens-in-browser` | 69 | 63 | yes |
| esp32-mesh | `config-json-refactor` | 71 | 63 | yes |
| esp32-mesh | `feature/ecash-redemption` | 80 | 65 | yes |
| esp32-mesh | `feature/ecash-redemption-backup` | 80 | 65 | yes |
| esp32-mesh | `feature/ecash-redemption-before-merge` | 80 | 65 | yes |
| esp32-mesh | `feature/introduce-captive-portal` | 69 | 63 | yes |
| esp32-mesh | `feature/redeem-ecash` | 80 | 65 | yes |
| esp32-mesh | `individual-authentication` | 73 | 63 | yes |
| esp32-mesh | `internet-passthrough-works` | 69 | 64 | yes |
| esp32-mesh | `mutex-worked` | 68 | 63 | yes |
| esp32-mesh | `pretty-captive-portal` | 73 | 63 | yes |
| esp32-mesh | `with-delay` | 82 | 65 | yes |
| esp32-mesh | `v0.1.0` | 69 | 63 | yes |
| esp32-tollgate | `master` | 1588 | 554 | yes |
| esp32-tollgate | `remotes/origin/balloon-pow-e-hash` | 1663 | 580 | yes |
| esp32-tollgate | `remotes/origin/balloon-pow-extraction` | 1663 | 580 | yes |
| esp32-tollgate | `remotes/origin/balloon-tollgate-c3-port` | 1664 | 586 | yes |
| esp32-tollgate | `remotes/origin/master` | 1588 | 554 | yes |
| esp32-tollgate | `remotes/upstream/master` | 1588 | 554 | yes |
| esp32-tollgate | `archive/cvm-integration` | 181 | 81 | yes |
| esp32-tollgate | `archive/display-fix` | 187 | 65 | yes |
| esp32-tollgate | `archive/local-relay` | 199 | 81 | yes |
| esp32-tollgate | `archive/miner-integration` | 557 | 245 | yes |
| esp32-tollgate | `archive/mining-payment` | 227 | 98 | yes |
| esp32-tollgate | `archive/multi-mint-support-pre-rebase` | 232 | 95 | yes |
| esp32-tollgate | `archive/tollgate-core-component` | 302 | 72 | yes |
| esp32-tollgate | `archive/tollgate-core-v2` | 1369 | 476 | yes |
| esp32-tollgate | `v-balloon-pre-strip` | 1639 | 583 | yes |
| esp32-tollgate | `v1.4.0` | 1364 | 476 | yes |
| wisp-esp32 | `balloon-nostr-extraction` | 6 | 5 | yes |
| wisp-esp32 | `main` | 0 | 0 | yes |
| wisp-esp32 | `remotes/fork/balloon-nostr-extraction` | 6 | 5 | yes |
| wisp-esp32 | `remotes/origin/feature/subscription-manager` | 0 | 0 | yes |
| wisp-esp32 | `remotes/origin/main` | 0 | 0 | yes |

Raw matching lines in `raw-hits.tsv` across all revs and all roots (git revs + non-git trees): **18603** (`wc -l`). Per-rev totals above cover git revs; the `WORKTREE-ASIS` non-git
roots add: esp32-tollgate-relay 1214, esp32-balloon-integration-meshcore-pr 409,
esp32-repeater-captive-portal 0, ailaptop-migration/esp32-tollgate 0.

## 3. ZERO-HIT ROOTS

### 3a. Revs where the required regex matched nothing at all

| repo | rev |
|---|---|
| wisp-esp32 | `main` |
| wisp-esp32 | `remotes/origin/feature/subscription-manager` |
| wisp-esp32 | `remotes/origin/main` |

### 3b. Revs where the regex matched only `tollgate`-substring noise (no standalone term)

| repo | rev | raw match lines | substantive |
|---|---|---|---|
| _none_ | | | |

### 3c. Non-git roots with zero hits

- `/home/c03rad0r/esp32-mesh/esp32-repeater-captive-portal` — 0 matching lines (no docs in the tree).
- `/home/c03rad0r/repos/ailaptop-migration/esp32-mesh` — bare git dir whose `master` has **no
  commits yet**; nothing to scan (recorded as a zero-hit root).
- `/home/c03rad0r/repos/ailaptop-migration/esp32-tollgate` — bare dir whose `master` is the same
  commit as tollgate-esp32 `master` (6d3db7a); counts identical (1588 raw / 554 substantive).

### 3d. Target-term absence (whole-corpus negative results)

Verified by direct grep across **every** rev of every scanned git root, all-file (not just docs):

- `shadow card` / `shadow-card` / `shadow_card` — **ZERO hits** in esp32-mesh, esp32-tollgate,
  wisp-esp32 (all revs) and all non-git esp32-* dirs scanned here.
- `human gate` / `human-gate` / `human_gate` — **ZERO hits** (same scope).
- Supplementary approval-vocabulary probe (`sign-?off|waiver|quorum|four.?eyes|two.?person|
  change.?control|approver|gatekeep`) over the same scope: **1 hit total**, the ambiguous
  `gatekeeper` line in §4 (and it is in the out-of-shard balloon worktree).

Consequence for this shard: **no esp32-* rev contains a shadow-card, human-gate, or
board-approval mechanism.** Every substantive hit is a firmware/PCB/hardware `board` mention or a
`gate` used in a non-approval sense; the small borderline set is classified `ambiguous` in §4.

## 4. Raw-hit list (kept + ambiguous), verbatim

Column order as required: `path:line` | date (source) | VERBATIM quote | classification |
planning/design talk vs described implemented mechanism | narrowing note.

| path:line | date (source) | VERBATIM quote | classification | talk vs implemented mechanism | narrowing note |
|---|---|---|---|---|---|
| `esp32-balloon-integration-meshcore-pr:/home/c03rad0r/esp32-balloon-integration-meshcore-pr/tracker/ground-station/antenna-tracker/ts/.agents/skills/concepts/SKILL.md:45` | NO-GIT-HISTORY (non-git worktree, current tree) | - No central directory or gatekeeper | recreated | design/planning talk (prose; no implemented gate code cited) | matched required regex term with approval/gating-mechanism sense |
| `esp32-balloon-integration-meshcore-pr:/home/c03rad0r/esp32-balloon-integration-meshcore-pr/IMPLEMENTATION-PLAN.md:346` | NO-GIT-HISTORY (non-git worktree, current tree) | - [ ] Payment-gated internet access via balloon mesh | ambiguous | design/planning talk (prose; no implemented gate code cited) | names a gating MECHANISM (payment/access gating or machine-approval gate) but it is not a human/shadow-card/board gate |
| `esp32-tollgate/PLAN.md:34` | 2026-05-18 23:39:04 +0530 | **Goal:** WiFi repeater with captive portal that gates internet access. Validates DNS hijack, NAT, DHCP, firewall. | ambiguous | design/planning talk (prose; no implemented gate code cited) | names a gating MECHANISM (payment/access gating or machine-approval gate) but it is not a human/shadow-card/board gate |
| `esp32-tollgate/PLAN_MINING_INTERNET.md:537` | 2026-06-10 12:04:26 +0530 | \| mint-orchestrator \| (inside infra-kit) \| Nostr-gated mint quote approval via gRPC to CDK mintd \| | ambiguous | design/planning talk (prose; no implemented gate code cited) | names a gating MECHANISM (payment/access gating or machine-approval gate) but it is not a human/shadow-card/board gate |
| `esp32-tollgate/docs/ADR-001-tollgate-over-lr2021.md:66` | 2026-07-29 20:15:06 +0530 | 3. **"Internet access" concept changes.** Over WiFi, NAPT shares the STA uplink. Over radio, the balloon might relay messages to/from ground — payment gates radio relay time or bandwidth. | ambiguous | design/planning talk (prose; no implemented gate code cited) | names a gating MECHANISM (payment/access gating or machine-approval gate) but it is not a human/shadow-card/board gate; file kept by step 4 filename rule |
| `esp32-tollgate/docs/ADR-001-tollgate-over-lr2021.md:68` | 2026-07-29 20:15:06 +0530 | 4. **Local Nostr relay still valuable.** Clients within radio range can publish/read events via the balloon's local relay, even without internet. Payment gates access to this relay. | ambiguous | design/planning talk (prose; no implemented gate code cited) | names a gating MECHANISM (payment/access gating or machine-approval gate) but it is not a human/shadow-card/board gate; file kept by step 4 filename rule |
| `esp32-tollgate/docs/adr/ADR-XXX-balloon-stratum-relay.md:105` | 2026-07-29 20:29:09 +0530 | ### 3. Cashu Payment Gateway (E-Hash) | ambiguous | design/planning talk (prose; no implemented gate code cited) | names a gating MECHANISM (payment/access gating or machine-approval gate) but it is not a human/shadow-card/board gate; file kept by step 4 filename rule |
| `esp32-tollgate/docs/adr/ADR-XXX-balloon-stratum-relay.md:22` | 2026-07-29 20:29:09 +0530 | engine — it never computes SHA256. It is a thin relay + payment gateway. | ambiguous | design/planning talk (prose; no implemented gate code cited) | names a gating MECHANISM (payment/access gating or machine-approval gate) but it is not a human/shadow-card/board gate; file kept by step 4 filename rule |
| `esp32-tollgate/docs/adr/ADR-XXX-balloon-stratum-relay.md:40` | 2026-07-29 20:29:09 +0530 |     │  - Cashu payment gateway (metered access) | ambiguous | design/planning talk (prose; no implemented gate code cited) | names a gating MECHANISM (payment/access gating or machine-approval gate) but it is not a human/shadow-card/board gate; file kept by step 4 filename rule |
| `esp32-tollgate/docs/adr/adr-balloon-stratum-relay-DECISIONS.md:6` | 2026-07-29 20:29:09 +0530 | Balloon never computes SHA256. Pure stratum relay + Ecash payment gateway. | ambiguous | design/planning talk (prose; no implemented gate code cited) | names a gating MECHANISM (payment/access gating or machine-approval gate) but it is not a human/shadow-card/board gate; file kept by step 4 filename rule |
| `esp32-tollgate-relay:/home/c03rad0r/esp32-tollgate-relay/PLAN.md:34` | NO-GIT-HISTORY (non-git worktree, current tree) | **Goal:** WiFi repeater with captive portal that gates internet access. Validates DNS hijack, NAT, DHCP, firewall. | ambiguous | design/planning talk (prose; no implemented gate code cited) | names a gating MECHANISM (payment/access gating or machine-approval gate) but it is not a human/shadow-card/board gate |
| `wisp-esp32/docs/STATUS-balloon-nostr.md:27` | 2026-07-30 16:47:28 +0530 | 4. **secp256k1 flash measurement** — gates decision on full Schnorr vs ground-station-deferred validation | ambiguous | design/planning talk (prose; no implemented gate code cited) | names a gating MECHANISM (payment/access gating or machine-approval gate) but it is not a human/shadow-card/board gate |

### 4a. `recreated` — hits kept as describing a gating/approval mechanism

- `esp32-balloon-integration-meshcore-pr:/home/c03rad0r/esp32-balloon-integration-meshcore-pr/tracker/ground-station/antenna-tracker/ts/.agents/skills/concepts/SKILL.md:45` — "- No central directory or gatekeeper"
  - date: NO-GIT-HISTORY (non-git worktree, current tree)
  - why kept: matched required regex term with approval/gating-mechanism sense
  - **caveat (this is the weakest entry in the list):** the matched token is the single word
    `gatekeeper` in a sentence that says there is *no* central directory or gatekeeper. It names
    the absence of a gating authority, not a gate. Downstream narrowing should treat it as
    weak-to-ambiguous; it is classed `recreated` only because the classification vocabulary in
    this task has no weaker positive label.
  - **out of shard:** this file lives in `/home/c03rad0r/esp32-balloon-integration-meshcore-pr`,
    i.e. balloon-integration material already assigned to `esp32-balloon-integration`.

### 4b. `ambiguous` — describes a gating MECHANISM but not a human/board gate

- `esp32-balloon-integration-meshcore-pr:/home/c03rad0r/esp32-balloon-integration-meshcore-pr/IMPLEMENTATION-PLAN.md:346` | NO-GIT-HISTORY (non-git worktree, current tree) | "- [ ] Payment-gated internet access via balloon mesh"
  - names a gating MECHANISM (payment/access gating or machine-approval gate) but it is not a human/shadow-card/board gate
- `esp32-tollgate:PLAN.md:34` | 2026-05-18 23:39:04 +0530 | "**Goal:** WiFi repeater with captive portal that gates internet access. Validates DNS hijack, NAT, DHCP, firewall."
  - names a gating MECHANISM (payment/access gating or machine-approval gate) but it is not a human/shadow-card/board gate
- `esp32-tollgate:PLAN_MINING_INTERNET.md:537` | 2026-06-10 12:04:26 +0530 | "| mint-orchestrator | (inside infra-kit) | Nostr-gated mint quote approval via gRPC to CDK mintd |"
  - names a gating MECHANISM (payment/access gating or machine-approval gate) but it is not a human/shadow-card/board gate
- `esp32-tollgate:docs/ADR-001-tollgate-over-lr2021.md:66` | 2026-07-29 20:15:06 +0530 | "3. **"Internet access" concept changes.** Over WiFi, NAPT shares the STA uplink. Over radio, the balloon might relay messages to/from ground — payment gates radio relay time or bandwidth."
  - names a gating MECHANISM (payment/access gating or machine-approval gate) but it is not a human/shadow-card/board gate; file kept by step 4 filename rule
- `esp32-tollgate:docs/ADR-001-tollgate-over-lr2021.md:68` | 2026-07-29 20:15:06 +0530 | "4. **Local Nostr relay still valuable.** Clients within radio range can publish/read events via the balloon's local relay, even without internet. Payment gates access to this relay."
  - names a gating MECHANISM (payment/access gating or machine-approval gate) but it is not a human/shadow-card/board gate; file kept by step 4 filename rule
- `esp32-tollgate:docs/adr/ADR-XXX-balloon-stratum-relay.md:105` | 2026-07-29 20:29:09 +0530 | "### 3. Cashu Payment Gateway (E-Hash)"
  - names a gating MECHANISM (payment/access gating or machine-approval gate) but it is not a human/shadow-card/board gate; file kept by step 4 filename rule
- `esp32-tollgate:docs/adr/ADR-XXX-balloon-stratum-relay.md:22` | 2026-07-29 20:29:09 +0530 | "engine — it never computes SHA256. It is a thin relay + payment gateway."
  - names a gating MECHANISM (payment/access gating or machine-approval gate) but it is not a human/shadow-card/board gate; file kept by step 4 filename rule
- `esp32-tollgate:docs/adr/ADR-XXX-balloon-stratum-relay.md:40` | 2026-07-29 20:29:09 +0530 | "    │  - Cashu payment gateway (metered access)"
  - names a gating MECHANISM (payment/access gating or machine-approval gate) but it is not a human/shadow-card/board gate; file kept by step 4 filename rule
- `esp32-tollgate:docs/adr/adr-balloon-stratum-relay-DECISIONS.md:6` | 2026-07-29 20:29:09 +0530 | "Balloon never computes SHA256. Pure stratum relay + Ecash payment gateway."
  - names a gating MECHANISM (payment/access gating or machine-approval gate) but it is not a human/shadow-card/board gate; file kept by step 4 filename rule
- `esp32-tollgate-relay:/home/c03rad0r/esp32-tollgate-relay/PLAN.md:34` | NO-GIT-HISTORY (non-git worktree, current tree) | "**Goal:** WiFi repeater with captive portal that gates internet access. Validates DNS hijack, NAT, DHCP, firewall."
  - names a gating MECHANISM (payment/access gating or machine-approval gate) but it is not a human/shadow-card/board gate
- `wisp-esp32:docs/STATUS-balloon-nostr.md:27` | 2026-07-30 16:47:28 +0530 | "4. **secp256k1 flash measurement** — gates decision on full Schnorr vs ground-station-deferred validation"
  - names a gating MECHANISM (payment/access gating or machine-approval gate) but it is not a human/shadow-card/board gate

Interpretation limit: entries 4b are payment/access gating and one machine (Nostr) approval path;
none is a human approval gate, a shadow card, or a board. No conclusion beyond the label is drawn.

## 5. Raw hits discarded by narrowing

Narrowing applied, as instructed: explicit discard of firmware/PCB `board` mentions (flight-board,
board configuration, dev board, wing/hub board, board+GPIO/pin/MAC/flash/port) and of
`gate` hits with no approval semantics (payment gateway, `gates internet access`,
`gated behind CONFIG_*`, `gated on STA getting IP`, `gate on health` mint-health checks,
`Gate /setup behind network_count == 0` route guards, logic/electrical gate).

Counts: **1095 board-mention discards**, **196 non-approval-gate discards**, 
**0 substring-only discards**. All are listed in full (verbatim, one row each) in the
committed artifacts next to this report:

- `raw/esp32-recon/out/rows-dropped-board.md` (955+ rows)
- `raw/esp32-recon/out/rows-dropped-gate.md` (196+ rows)
- `raw/esp32-recon/out/raw-hits.tsv` (every raw line, all revs)
- `raw/esp32-recon/out/substantive.tsv` (lines with a standalone term)

### 5a. board-mention discards — where they cluster

| repo | path | discarded board rows |
|---|---|---|
| esp32-tollgate | `AGENTS.md` | 132 |
| esp32-tollgate | `CHECKLIST.md` | 125 |
| esp32-tollgate | `PLAN_pytest_migration.md` | 53 |
| esp32-tollgate | `PLAN.md` | 41 |
| esp32-tollgate | `RELAY_HARDENING_PLAN.md` | 39 |
| esp32-tollgate | `TEST_COVERAGE_PLAN.md` | 38 |
| esp32-tollgate | `PLAN_B2B_SETTLEMENT.md` | 37 |
| esp32-balloon-integration-meshcore-pr | `/home/c03rad0r/esp32-balloon-integration-meshcore-pr/tracker/hardware/hub_board_diy/implementation-plan.md` | 29 |
| esp32-tollgate | `docs/E2E_FIX_PLAN.md` | 29 |
| esp32-tollgate-relay | `/home/c03rad0r/esp32-tollgate-relay/CHECKLIST.md` | 29 |
| esp32-tollgate | `SESSION_NOTES.md` | 26 |
| esp32-tollgate | `PLAN_MINING_INTERNET.md` | 24 |
| esp32-tollgate | `tests/integration/MULTI-MINT-TEST-REPORT.md` | 22 |
| esp32-balloon-integration-meshcore-pr | `/home/c03rad0r/esp32-balloon-integration-meshcore-pr/docs/hardware-design.md` | 21 |
| esp32-tollgate | `PRICING_DISCOVERY_PLAN.md` | 21 |
| esp32-tollgate | `docs/INTEGRATION-ASSESSMENT.md` | 21 |
| esp32-tollgate-relay | `/home/c03rad0r/esp32-tollgate-relay/AGENTS.md` | 19 |
| esp32-tollgate-relay | `/home/c03rad0r/esp32-tollgate-relay/PLAN.md` | 17 |
| esp32-balloon-integration-meshcore-pr | `/home/c03rad0r/esp32-balloon-integration-meshcore-pr/tracker/hardware/hub_board_diy/plan.md` | 14 |
| esp32-tollgate | `MINER_INTEGRATION_PLAN.md` | 14 |
| esp32-tollgate | `PLAN_EXECUTION.md` | 14 |
| esp32-balloon-integration-meshcore-pr | `/home/c03rad0r/esp32-balloon-integration-meshcore-pr/AGENTS.md` | 13 |
| esp32-tollgate | `docs/PCB-DESIGN-PLAN.md` | 12 |
| esp32-balloon-integration-meshcore-pr | `/home/c03rad0r/esp32-balloon-integration-meshcore-pr/docs/component-guide.md` | 11 |
| esp32-tollgate | `PLAN_remaining_tests.md` | 11 |
| esp32-balloon-integration-meshcore-pr | `/home/c03rad0r/esp32-balloon-integration-meshcore-pr/docs/adr/003-dual-track-hardware.md` | 10 |
| esp32-balloon-integration-meshcore-pr | `/home/c03rad0r/esp32-balloon-integration-meshcore-pr/docs/plan.md` | 10 |
| esp32-tollgate | `DESIGN.md` | 10 |
| esp32-tollgate | `PLAN_BITAXE_FIXES.md` | 9 |
| esp32-tollgate | `interop/INTEROP_PLAN.md` | 9 |
| esp32-tollgate-relay | `/home/c03rad0r/esp32-tollgate-relay/interop/INTEROP_PLAN.md` | 9 |
| esp32-balloon-integration-meshcore-pr | `/home/c03rad0r/esp32-balloon-integration-meshcore-pr/docs/esp32c3-supermini-bringup.md` | 8 |
| esp32-balloon-integration-meshcore-pr | `/home/c03rad0r/esp32-balloon-integration-meshcore-pr/mesh-stack/meshcore-lr2021/README.md` | 8 |
| esp32-tollgate | `docs/HARDWARE-INVENTORY.md` | 8 |
| esp32-tollgate | `docs/TOLLGATE_CORE_DESIGN.md` | 8 |
| esp32-tollgate | `docs/WPA-AUTO-DETECT-PLAN.md` | 7 |
| esp32-balloon-integration-meshcore-pr | `/home/c03rad0r/esp32-balloon-integration-meshcore-pr/docs/adr/004-3d-yagi-antenna-structure.md` | 6 |
| esp32-balloon-integration-meshcore-pr | `/home/c03rad0r/esp32-balloon-integration-meshcore-pr/docs/execution-checklist.md` | 6 |
| esp32-balloon-integration-meshcore-pr | `/home/c03rad0r/esp32-balloon-integration-meshcore-pr/docs/plan-variants.md` | 6 |
| esp32-balloon-integration-meshcore-pr | `/home/c03rad0r/esp32-balloon-integration-meshcore-pr/mesh-stack/meshcore-lr2021/UPSTREAM-PR-PLAN.md` | 6 |
| esp32-tollgate | `CHECKLIST-CVM-RELAY.md` | 6 |
| esp32-tollgate | `ROADMAP.md` | 6 |
| esp32-tollgate | `SESSION_PROGRESS.md` | 6 |
| esp32-balloon-integration-meshcore-pr | `/home/c03rad0r/esp32-balloon-integration-meshcore-pr/IMPLEMENTATION-PLAN.md` | 5 |
| esp32-balloon-integration-meshcore-pr | `/home/c03rad0r/esp32-balloon-integration-meshcore-pr/docs/adr/009-antenna-strategy-v1-v2.md` | 5 |
| esp32-balloon-integration-meshcore-pr | `/home/c03rad0r/esp32-balloon-integration-meshcore-pr/docs/antenna-strategy.md` | 5 |
| esp32-balloon-integration-meshcore-pr | `/home/c03rad0r/esp32-balloon-integration-meshcore-pr/mesh-stack/ROADMAP.md` | 5 |
| esp32-tollgate | `docs/STATUS-balloon-tollgate.md` | 5 |
| esp32-tollgate | `interop/PROGRESS.md` | 5 |
| esp32-tollgate-relay | `/home/c03rad0r/esp32-tollgate-relay/interop/PROGRESS.md` | 5 |
| esp32-balloon-integration-meshcore-pr | `/home/c03rad0r/esp32-balloon-integration-meshcore-pr/README.md` | 4 |
| esp32-mesh | `docs/mesh-how.md` | 4 |
| esp32-mesh | `docs/setup.md` | 4 |
| esp32-mesh | `mesh-how.md` | 4 |
| esp32-mesh | `setup.md` | 4 |
| esp32-tollgate | `PLAN_TOLLGATE_CORE_EXTRACTION.md` | 4 |
| esp32-tollgate | `REMAINING_PLAN.md` | 4 |
| esp32-tollgate | `REMOTES.md` | 4 |
| esp32-tollgate | `docs/ARCHITECTURE-CAR-TOLLGATE.md` | 4 |
| esp32-balloon-integration-meshcore-pr | `/home/c03rad0r/esp32-balloon-integration-meshcore-pr/FINISH-PLAN.md` | 3 |
| esp32-balloon-integration-meshcore-pr | `/home/c03rad0r/esp32-balloon-integration-meshcore-pr/docs/adr/001-esp32-c3-as-mcu.md` | 3 |
| esp32-balloon-integration-meshcore-pr | `/home/c03rad0r/esp32-balloon-integration-meshcore-pr/docs/breadboard-wiring-guide.md` | 3 |
| esp32-balloon-integration-meshcore-pr | `/home/c03rad0r/esp32-balloon-integration-meshcore-pr/docs/sx1280-repos-reference.md` | 3 |
| esp32-tollgate | `DISPLAY_FIX_PLAN.md` | 3 |
| esp32-tollgate | `RELAY_HARDENING_MERGE.md` | 3 |
| esp32-tollgate | `WEB_WIFI_SETUP_PLAN.md` | 3 |
| esp32-tollgate | `docs/MULTI_MINT_DESIGN.md` | 3 |
| esp32-tollgate | `docs/REBASE-SQUASH-MERGE-PLAN.md` | 3 |
| esp32-tollgate | `docs/WPA_AUTODETECT_PLAN.md` | 3 |
| esp32-tollgate | `interop/AGENTS.md` | 3 |
| esp32-tollgate-relay | `/home/c03rad0r/esp32-tollgate-relay/interop/AGENTS.md` | 3 |
| esp32-balloon-integration-meshcore-pr | `/home/c03rad0r/esp32-balloon-integration-meshcore-pr/blog/001-introduction.md` | 2 |
| esp32-balloon-integration-meshcore-pr | `/home/c03rad0r/esp32-balloon-integration-meshcore-pr/bom/BOM.md` | 2 |
| esp32-balloon-integration-meshcore-pr | `/home/c03rad0r/esp32-balloon-integration-meshcore-pr/docs/inventory.md` | 2 |
| esp32-balloon-integration-meshcore-pr | `/home/c03rad0r/esp32-balloon-integration-meshcore-pr/mesh-stack/research/meshcore-radiolib-wrapper-study.md` | 2 |
| esp32-balloon-integration-meshcore-pr | `/home/c03rad0r/esp32-balloon-integration-meshcore-pr/mesh-stack/research/routing/meshcore-study.md` | 2 |
| esp32-balloon-integration-meshcore-pr | `/home/c03rad0r/esp32-balloon-integration-meshcore-pr/tracker/ground-station/antenna-tracker/docs/WIRING_DIAGRAMS.md` | 2 |
| esp32-mesh | `docs/esp32-device-info.md` | 2 |
| esp32-mesh | `esp32-device-info.md` | 2 |
| esp32-tollgate | `PLAN-SQUASH-MERGE.md` | 2 |
| esp32-tollgate | `docs/STATUS-balloon-pow.md` | 2 |
| wisp-esp32 | `AGENTS.md` | 2 |
| wisp-esp32 | `docs/STATUS-balloon-nostr.md` | 2 |
| esp32-balloon-integration-meshcore-pr | `/home/c03rad0r/esp32-balloon-integration-meshcore-pr/docs/adr/005-sky66112-fem.md` | 1 |
| esp32-balloon-integration-meshcore-pr | `/home/c03rad0r/esp32-balloon-integration-meshcore-pr/docs/adr/011-first-flight-strategy.md` | 1 |
| esp32-balloon-integration-meshcore-pr | `/home/c03rad0r/esp32-balloon-integration-meshcore-pr/docs/balloon-flight-lessons.md` | 1 |
| esp32-balloon-integration-meshcore-pr | `/home/c03rad0r/esp32-balloon-integration-meshcore-pr/docs/first-flight-checklist.md` | 1 |
| esp32-balloon-integration-meshcore-pr | `/home/c03rad0r/esp32-balloon-integration-meshcore-pr/tracker/ground-station/antenna-tracker/docs/ESP32_DEVKIT_V1_PINOUT.md` | 1 |
| esp32-balloon-integration-meshcore-pr | `/home/c03rad0r/esp32-balloon-integration-meshcore-pr/tracker/ground-station/antenna-tracker/docs/PROJECT_STATUS.md` | 1 |
| esp32-tollgate | `CONSOLIDATION.md` | 1 |
| esp32-tollgate | `PLAN_lazy_keysets.md` | 1 |
| esp32-tollgate | `TOUCH_WIFI_SETUP_PLAN.md` | 1 |
| esp32-tollgate | `docs/ADR-001-tollgate-over-lr2021.md` | 1 |
| esp32-tollgate | `docs/BALLOON-SCOPE-DECISIONS.md` | 1 |
| esp32-tollgate | `docs/MINING-BUILD-REPORT.md` | 1 |
| esp32-tollgate-relay | `/home/c03rad0r/esp32-tollgate-relay/nucula_src/components/secp256k1/libsecp256k1/CONTRIBUTING.md` | 1 |
| esp32-tollgate-relay | `/home/c03rad0r/esp32-tollgate-relay/nucula_src/managed_components/espressif__cbor/examples/cbor/README.md` | 1 |

### 5b. non-approval-gate discards — where they cluster

| repo | path | discarded gate rows |
|---|---|---|
| esp32-mesh | `README.md` | 30 |
| esp32-mesh | `High-Level-Design.md` | 21 |
| esp32-mesh | `docs/High-Level-Design.md` | 21 |
| esp32-mesh | `Low-Level-Design.md` | 15 |
| esp32-mesh | `docs/Low-Level-Design.md` | 15 |
| esp32-balloon-integration-meshcore-pr | `/home/c03rad0r/esp32-balloon-integration-meshcore-pr/tracker/ground-station/antenna-tracker/docs/MCP_GATEWAY_SETUP_LEARNINGS.md` | 11 |
| esp32-balloon-integration-meshcore-pr | `/home/c03rad0r/esp32-balloon-integration-meshcore-pr/tracker/ground-station/antenna-tracker/docs/WEBSOCKET_RUNTIME_LEARNINGS.md` | 7 |
| esp32-balloon-integration-meshcore-pr | `/home/c03rad0r/esp32-balloon-integration-meshcore-pr/tracker/ground-station/antenna-tracker/ts/.agents/skills/server-dev/references/gateway-pattern.md` | 7 |
| esp32-balloon-integration-meshcore-pr | `/home/c03rad0r/esp32-balloon-integration-meshcore-pr/tracker/ground-station/antenna-tracker/docs/MCP_OPERATOR_RUNBOOK.md` | 5 |
| esp32-balloon-integration-meshcore-pr | `/home/c03rad0r/esp32-balloon-integration-meshcore-pr/tracker/ground-station/antenna-tracker/ts/.agents/skills/concepts/SKILL.md` | 5 |
| esp32-tollgate | `MINING_PLAN.md` | 5 |
| esp32-tollgate | `docs/ARCHITECTURE-CAR-TOLLGATE.md` | 5 |
| esp32-balloon-integration-meshcore-pr | `/home/c03rad0r/esp32-balloon-integration-meshcore-pr/tracker/ground-station/antenna-tracker/docs/MCP_CURRENT_STATE_AND_LEARNINGS.md` | 4 |
| esp32-tollgate | `docs/HARDWARE-INVENTORY.md` | 4 |
| esp32-tollgate | `docs/MULTI_MINT_DESIGN.md` | 4 |
| esp32-mesh | `docs/setup.md` | 3 |
| esp32-mesh | `setup.md` | 3 |
| esp32-balloon-integration-meshcore-pr | `/home/c03rad0r/esp32-balloon-integration-meshcore-pr/docs/adr/007-adaptive-protocol.md` | 2 |
| esp32-balloon-integration-meshcore-pr | `/home/c03rad0r/esp32-balloon-integration-meshcore-pr/tracker/ground-station/antenna-tracker/MCP_BUILD_AND_TEST_RESULTS.md` | 2 |
| esp32-balloon-integration-meshcore-pr | `/home/c03rad0r/esp32-balloon-integration-meshcore-pr/tracker/ground-station/antenna-tracker/mcp-antenna/MCP_BUILD_AND_TEST_RESULTS.md` | 2 |
| esp32-mesh | `docs/gateway-ping-plan.md` | 2 |
| esp32-tollgate | `PLAN.md` | 2 |
| esp32-tollgate-relay | `/home/c03rad0r/esp32-tollgate-relay/PLAN.md` | 2 |
| esp32-balloon-integration-meshcore-pr | `/home/c03rad0r/esp32-balloon-integration-meshcore-pr/docs/adr/013-cluster-aware-stratorelay.md` | 1 |
| esp32-balloon-integration-meshcore-pr | `/home/c03rad0r/esp32-balloon-integration-meshcore-pr/docs/sx1280-repos-reference.md` | 1 |
| esp32-balloon-integration-meshcore-pr | `/home/c03rad0r/esp32-balloon-integration-meshcore-pr/tracker/ground-station/README.md` | 1 |
| esp32-balloon-integration-meshcore-pr | `/home/c03rad0r/esp32-balloon-integration-meshcore-pr/tracker/ground-station/antenna-tracker/README.md` | 1 |
| esp32-balloon-integration-meshcore-pr | `/home/c03rad0r/esp32-balloon-integration-meshcore-pr/tracker/ground-station/antenna-tracker/docs/MCP_TOOLS_LIST_TIMEOUT_ANALYSIS.md` | 1 |
| esp32-balloon-integration-meshcore-pr | `/home/c03rad0r/esp32-balloon-integration-meshcore-pr/tracker/ground-station/antenna-tracker/docs/TYPESCRIPT_MCP_SERVER.md` | 1 |
| esp32-balloon-integration-meshcore-pr | `/home/c03rad0r/esp32-balloon-integration-meshcore-pr/tracker/ground-station/antenna-tracker/ts/.agents/skills/overview/SKILL.md` | 1 |
| esp32-balloon-integration-meshcore-pr | `/home/c03rad0r/esp32-balloon-integration-meshcore-pr/tracker/ground-station/antenna-tracker/ts/.agents/skills/server-dev/SKILL.md` | 1 |
| esp32-mesh | `DNS-fix.md` | 1 |
| esp32-mesh | `access-point-docs.md` | 1 |
| esp32-mesh | `diagnostic_plan.md` | 1 |
| esp32-mesh | `docs/DNS-fix.md` | 1 |
| esp32-mesh | `docs/access-point-docs.md` | 1 |
| esp32-tollgate | `PLAN_BITAXE_FIXES.md` | 1 |
| esp32-tollgate | `SESSION_PROGRESS.md` | 1 |
| esp32-tollgate | `TOUCH_WIFI_SETUP_PLAN.md` | 1 |
| esp32-tollgate | `WEB_WIFI_SETUP_PLAN.md` | 1 |
| esp32-tollgate | `docs/MINING-BUILD-REPORT.md` | 1 |
| esp32-tollgate | `docs/adr/ADR-XXX-balloon-stratum-relay.md` | 1 |

### 5c. near-miss discards (gate hits that mention payment/access/approval co-text)

These are the only discards a reviewer is likely to want to re-examine; listed verbatim here so the
narrowing is auditable without opening the TSVs.

| path:line | date (source) | VERBATIM quote | classification | narrowing note |
|---|---|---|---|---|
| `esp32-balloon-integration-meshcore-pr:/home/c03rad0r/esp32-balloon-integration-meshcore-pr/AGENTS.md:107` | NO-GIT-HISTORY (non-git worktree, current tree) | ## NiceRF LoRa2021 Pin Mapping (ESP32-C3_Mini_V1 Dev Board) | dropped | firmware/PCB/hardware 'board' mention (not an approval body) |
| `esp32-balloon-integration-meshcore-pr:/home/c03rad0r/esp32-balloon-integration-meshcore-pr/AGENTS.md:132` | NO-GIT-HISTORY (non-git worktree, current tree) | ## Pin Assignment (ESP32-C3 bare, Flight Board) | dropped | firmware/PCB/hardware 'board' mention (not an approval body) |
| `esp32-balloon-integration-meshcore-pr:/home/c03rad0r/esp32-balloon-integration-meshcore-pr/AGENTS.md:151` | NO-GIT-HISTORY (non-git worktree, current tree) | - The dev board (SuperMini) has an onboard LED on GPIO8 that causes this exact issue | dropped | firmware/PCB/hardware 'board' mention (not an approval body) |
| `esp32-balloon-integration-meshcore-pr:/home/c03rad0r/esp32-balloon-integration-meshcore-pr/AGENTS.md:152` | NO-GIT-HISTORY (non-git worktree, current tree) | - Flight board uses GPIO20/GPIO21 for I2C instead (safe, non-strapping) | dropped | firmware/PCB/hardware 'board' mention (not an approval body) |
| `esp32-balloon-integration-meshcore-pr:/home/c03rad0r/esp32-balloon-integration-meshcore-pr/AGENTS.md:156` | NO-GIT-HISTORY (non-git worktree, current tree) | - 2.4 GHz: PCB Yagis on wing boards (Komfort) or wire dipole (Minimal) | dropped | firmware/PCB/hardware 'board' mention (not an approval body) |
| `esp32-balloon-integration-meshcore-pr:/home/c03rad0r/esp32-balloon-integration-meshcore-pr/AGENTS.md:166` | NO-GIT-HISTORY (non-git worktree, current tree) | - All wing boards are IDENTICAL (same PCB, same components) | dropped | firmware/PCB/hardware 'board' mention (not an approval body) |
| `esp32-balloon-integration-meshcore-pr:/home/c03rad0r/esp32-balloon-integration-meshcore-pr/AGENTS.md:167` | NO-GIT-HISTORY (non-git worktree, current tree) | - Solder joints connect wing boards to hub board (no connectors on flight board) | dropped | firmware/PCB/hardware 'board' mention (not an approval body) |
| `esp32-balloon-integration-meshcore-pr:/home/c03rad0r/esp32-balloon-integration-meshcore-pr/AGENTS.md:170` | NO-GIT-HISTORY (non-git worktree, current tree) | - **Flight board uses GPIO20/GPIO21 for I2C (NOT GPIO8/GPIO9)** — see strapping pin warning above | dropped | firmware/PCB/hardware 'board' mention (not an approval body) |
| `esp32-balloon-integration-meshcore-pr:/home/c03rad0r/esp32-balloon-integration-meshcore-pr/AGENTS.md:31` | NO-GIT-HISTORY (non-git worktree, current tree) | - Double-sided copper clad FR4 boards (for toner transfer PCB fab) | dropped | firmware/PCB/hardware 'board' mention (not an approval body) |
| `esp32-balloon-integration-meshcore-pr:/home/c03rad0r/esp32-balloon-integration-meshcore-pr/AGENTS.md:60` | NO-GIT-HISTORY (non-git worktree, current tree) | tracker/hardware/hub_board/    - Central electronics board (SKiDL + KiCad) | dropped | firmware/PCB/hardware 'board' mention (not an approval body) |
| `esp32-balloon-integration-meshcore-pr:/home/c03rad0r/esp32-balloon-integration-meshcore-pr/AGENTS.md:61` | NO-GIT-HISTORY (non-git worktree, current tree) | tracker/hardware/hub_board_diy/- DIY v0.1 development hub board (toner transfer) | dropped | firmware/PCB/hardware 'board' mention (not an approval body) |
| `esp32-balloon-integration-meshcore-pr:/home/c03rad0r/esp32-balloon-integration-meshcore-pr/AGENTS.md:62` | NO-GIT-HISTORY (non-git worktree, current tree) | tracker/hardware/wing_board/   - 4x identical antenna+solar boards | dropped | firmware/PCB/hardware 'board' mention (not an approval body) |
| `esp32-balloon-integration-meshcore-pr:/home/c03rad0r/esp32-balloon-integration-meshcore-pr/AGENTS.md:97` | NO-GIT-HISTORY (non-git worktree, current tree) | 3. Dual-track hardware: Dev board (ESP32-C3_Mini_V1) + Flight board (bare chip) (ADR-003) | dropped | firmware/PCB/hardware 'board' mention (not an approval body) |
| `esp32-balloon-integration-meshcore-pr:/home/c03rad0r/esp32-balloon-integration-meshcore-pr/FINISH-PLAN.md:149` | NO-GIT-HISTORY (non-git worktree, current tree) | - [x] Fix board name "XIAO" → "ESP32-C3_Mini_V1" in execution-checklist.md | dropped | firmware/PCB/hardware 'board' mention (not an approval body) |
| `esp32-balloon-integration-meshcore-pr:/home/c03rad0r/esp32-balloon-integration-meshcore-pr/FINISH-PLAN.md:176` | NO-GIT-HISTORY (non-git worktree, current tree) | **Note**: Bench boards at /dev/ttyACM0,1 are ESP32-S3 TollGate routers. Need ESP32-C3 + LR2021 hardware for actual radio testing. | dropped | firmware/PCB/hardware 'board' mention (not an approval body) |
| `esp32-balloon-integration-meshcore-pr:/home/c03rad0r/esp32-balloon-integration-meshcore-pr/FINISH-PLAN.md:21` | NO-GIT-HISTORY (non-git worktree, current tree) | - **No on-target testing has happened** — bench boards are ESP32-S3 TollGate routers, need ESP32-C3 + LR2021 hardware | dropped | firmware/PCB/hardware 'board' mention (not an approval body) |
| `esp32-balloon-integration-meshcore-pr:/home/c03rad0r/esp32-balloon-integration-meshcore-pr/IMPLEMENTATION-PLAN.md:83` | NO-GIT-HISTORY (non-git worktree, current tree) | - [x] `NiceRFLR2021Board.h` — Board class (deep sleep, battery ADC, GPIO5 wakeup) | dropped | firmware/PCB/hardware 'board' mention (not an approval body) |
| `esp32-balloon-integration-meshcore-pr:/home/c03rad0r/esp32-balloon-integration-meshcore-pr/IMPLEMENTATION-PLAN.md:89` | NO-GIT-HISTORY (non-git worktree, current tree) | **Custom board definition** (commit `540a8d6`+): | dropped | firmware/PCB/hardware 'board' mention (not an approval body) |
| `esp32-balloon-integration-meshcore-pr:/home/c03rad0r/esp32-balloon-integration-meshcore-pr/IMPLEMENTATION-PLAN.md:90` | NO-GIT-HISTORY (non-git worktree, current tree) | - [x] `boards/esp32c3_supermini.json` — Board JSON with correct flash config (4MB, DIO) | dropped | firmware/PCB/hardware 'board' mention (not an approval body) |
| `esp32-balloon-integration-meshcore-pr:/home/c03rad0r/esp32-balloon-integration-meshcore-pr/IMPLEMENTATION-PLAN.md:92` | NO-GIT-HISTORY (non-git worktree, current tree) |   - Fixes XIAO board D-pin conflict (D6=GPIO21, D7=GPIO20 vs our GPIO6/GPIO7) | dropped | firmware/PCB/hardware 'board' mention (not an approval body) |
| `esp32-balloon-integration-meshcore-pr:/home/c03rad0r/esp32-balloon-integration-meshcore-pr/IMPLEMENTATION-PLAN.md:95` | NO-GIT-HISTORY (non-git worktree, current tree) | - [x] `platformio.ini` updated to `board = esp32c3_supermini` | dropped | firmware/PCB/hardware 'board' mention (not an approval body) |
| `esp32-balloon-integration-meshcore-pr:/home/c03rad0r/esp32-balloon-integration-meshcore-pr/README.md:14` | NO-GIT-HISTORY (non-git worktree, current tree) | - **Dual-Track Hardware**: Dev-Board (XIAO) + Flight-Board (Bare-Chip) | dropped | firmware/PCB/hardware 'board' mention (not an approval body) |
| `esp32-balloon-integration-meshcore-pr:/home/c03rad0r/esp32-balloon-integration-meshcore-pr/README.md:31` | NO-GIT-HISTORY (non-git worktree, current tree) | - [Hardware-Design](docs/hardware-design.md) - 3D Board-Design (Hub + Wings) | dropped | firmware/PCB/hardware 'board' mention (not an approval body) |
| `esp32-balloon-integration-meshcore-pr:/home/c03rad0r/esp32-balloon-integration-meshcore-pr/README.md:42` | NO-GIT-HISTORY (non-git worktree, current tree) | | [003](docs/adr/003-dual-track-hardware.md) | Dual-Track: Dev + Flight Board | | dropped | firmware/PCB/hardware 'board' mention (not an approval body) |
| `esp32-balloon-integration-meshcore-pr:/home/c03rad0r/esp32-balloon-integration-meshcore-pr/README.md:55` | NO-GIT-HISTORY (non-git worktree, current tree) | │   ├── hub_board/             # Zentrales Elektronik-Board | dropped | firmware/PCB/hardware 'board' mention (not an approval body) |
| `esp32-balloon-integration-meshcore-pr:/home/c03rad0r/esp32-balloon-integration-meshcore-pr/blog/001-introduction.md:108` | NO-GIT-HISTORY (non-git worktree, current tree) | - 20x XIAO ESP32C3 boards | dropped | firmware/PCB/hardware 'board' mention (not an approval body) |
| `esp32-balloon-integration-meshcore-pr:/home/c03rad0r/esp32-balloon-integration-meshcore-pr/blog/001-introduction.md:114` | NO-GIT-HISTORY (non-git worktree, current tree) | Step 2: First LoRa TX/RX test between two boards. | dropped | firmware/PCB/hardware 'board' mention (not an approval body) |
| `esp32-balloon-integration-meshcore-pr:/home/c03rad0r/esp32-balloon-integration-meshcore-pr/bom/BOM.md:36` | NO-GIT-HISTORY (non-git worktree, current tree) | ### Prioritaet 3: Flight-Board (Minimal) | dropped | firmware/PCB/hardware 'board' mention (not an approval body) |
| `esp32-balloon-integration-meshcore-pr:/home/c03rad0r/esp32-balloon-integration-meshcore-pr/bom/BOM.md:46` | NO-GIT-HISTORY (non-git worktree, current tree) | ### Prioritaet 4: Flight-Board (Komfort-Optionen) | dropped | firmware/PCB/hardware 'board' mention (not an approval body) |
| `esp32-balloon-integration-meshcore-pr:/home/c03rad0r/esp32-balloon-integration-meshcore-pr/docs/adr/001-esp32-c3-as-mcu.md:10` | NO-GIT-HISTORY (non-git worktree, current tree) | Wir verwenden den **ESP32-C3** (konkret: ESP-C3-12F Bare Module fuer Flight-Board, XIAO ESP32C3 fuer Prototyping). | dropped | firmware/PCB/hardware 'board' mention (not an approval body); file kept by step 4 filename rule |
| `esp32-balloon-integration-meshcore-pr:/home/c03rad0r/esp32-balloon-integration-meshcore-pr/docs/adr/001-esp32-c3-as-mcu.md:38` | NO-GIT-HISTORY (non-git worktree, current tree) | - 1x XIAO ESP32C3 (Seeed Studio) - fuer Dev-Board Prototyping | dropped | firmware/PCB/hardware 'board' mention (not an approval body); file kept by step 4 filename rule |
| `esp32-balloon-integration-meshcore-pr:/home/c03rad0r/esp32-balloon-integration-meshcore-pr/docs/adr/001-esp32-c3-as-mcu.md:39` | NO-GIT-HISTORY (non-git worktree, current tree) | - 1x ESP32-C5 Board - fuer Bodenstation (WiFi 6) | dropped | firmware/PCB/hardware 'board' mention (not an approval body); file kept by step 4 filename rule |
| `esp32-balloon-integration-meshcore-pr:/home/c03rad0r/esp32-balloon-integration-meshcore-pr/docs/adr/003-dual-track-hardware.md:12` | NO-GIT-HISTORY (non-git worktree, current tree) | ### Track A: Entwickler-Board (XIAO Carrier) | dropped | firmware/PCB/hardware 'board' mention (not an approval body); file kept by step 4 filename rule |
| `esp32-balloon-integration-meshcore-pr:/home/c03rad0r/esp32-balloon-integration-meshcore-pr/docs/adr/003-dual-track-hardware.md:21` | NO-GIT-HISTORY (non-git worktree, current tree) | ### Track B: Flug-Board (Bare-Chip, 3D-Struktur) | dropped | firmware/PCB/hardware 'board' mention (not an approval body); file kept by step 4 filename rule |
| `esp32-balloon-integration-meshcore-pr:/home/c03rad0r/esp32-balloon-integration-meshcore-pr/docs/adr/003-dual-track-hardware.md:23` | NO-GIT-HISTORY (non-git worktree, current tree) | - 52x19mm Solarzellen auf Wing-Boards | dropped | firmware/PCB/hardware 'board' mention (not an approval body); file kept by step 4 filename rule |
| `esp32-balloon-integration-meshcore-pr:/home/c03rad0r/esp32-balloon-integration-meshcore-pr/docs/adr/003-dual-track-hardware.md:25` | NO-GIT-HISTORY (non-git worktree, current tree) | - Hub-Board + 4 Wing-Boards als 3D-Struktur | dropped | firmware/PCB/hardware 'board' mention (not an approval body); file kept by step 4 filename rule |
| `esp32-balloon-integration-meshcore-pr:/home/c03rad0r/esp32-balloon-integration-meshcore-pr/docs/adr/003-dual-track-hardware.md:32` | NO-GIT-HISTORY (non-git worktree, current tree) | 2. **Gleiche Pin-Belegung**: Beide Boards nutzen identische GPIO-Zuordnung | dropped | firmware/PCB/hardware 'board' mention (not an approval body); file kept by step 4 filename rule |
| `esp32-balloon-integration-meshcore-pr:/home/c03rad0r/esp32-balloon-integration-meshcore-pr/docs/adr/003-dual-track-hardware.md:34` | NO-GIT-HISTORY (non-git worktree, current tree) | 4. **Risikominimierung**: Fehler auf dem Dev-Board kosten keine Flug-Hardware | dropped | firmware/PCB/hardware 'board' mention (not an approval body); file kept by step 4 filename rule |
| `esp32-balloon-integration-meshcore-pr:/home/c03rad0r/esp32-balloon-integration-meshcore-pr/docs/adr/003-dual-track-hardware.md:38` | NO-GIT-HISTORY (non-git worktree, current tree) | - Pin-Belegung muss auf beiden Boards identisch sein (fuer gleiche Firmware) | dropped | firmware/PCB/hardware 'board' mention (not an approval body); file kept by step 4 filename rule |
| `esp32-balloon-integration-meshcore-pr:/home/c03rad0r/esp32-balloon-integration-meshcore-pr/docs/adr/003-dual-track-hardware.md:39` | NO-GIT-HISTORY (non-git worktree, current tree) | - Dev-Board dient als Referenz fuer elektrische Tests vor dem Flug-Board-Loeten | dropped | firmware/PCB/hardware 'board' mention (not an approval body); file kept by step 4 filename rule |
| `esp32-balloon-integration-meshcore-pr:/home/c03rad0r/esp32-balloon-integration-meshcore-pr/docs/adr/003-dual-track-hardware.md:40` | NO-GIT-HISTORY (non-git worktree, current tree) | - Flug-Board wird erst gebaut wenn Firmware auf Dev-Board validiert ist | dropped | firmware/PCB/hardware 'board' mention (not an approval body); file kept by step 4 filename rule |
| `esp32-balloon-integration-meshcore-pr:/home/c03rad0r/esp32-balloon-integration-meshcore-pr/docs/adr/003-dual-track-hardware.md:7` | NO-GIT-HISTORY (non-git worktree, current tree) | Wir brauchen eine Plattform zum Entwickeln und Testen der Firmware UND ein minimales Flug-Board unter 15g. Die Anforderungen an Prototyping (einfaches Flashen, Debug, USB) und Flug (minimalgewicht, keine Stecker) widersprechen sich. | dropped | firmware/PCB/hardware 'board' mention (not an approval body); file kept by step 4 filename rule |
| `esp32-balloon-integration-meshcore-pr:/home/c03rad0r/esp32-balloon-integration-meshcore-pr/docs/adr/004-3d-yagi-antenna-structure.md:10` | NO-GIT-HISTORY (non-git worktree, current tree) | **4 identische Wing-Boards** mit je einer PCB-Yagi-Antenne, die orthogonal in verschiedene Raumrichtungen zeigen. Verbunden durch ein zentrales Hub-Board ueber Loetstellen. SP4T RF-Switch fuer "Leuchtturm-Modus" (Round-Robin TX). | dropped | firmware/PCB/hardware 'board' mention (not an approval body); file kept by step 4 filename rule |
| `esp32-balloon-integration-meshcore-pr:/home/c03rad0r/esp32-balloon-integration-meshcore-pr/docs/adr/004-3d-yagi-antenna-structure.md:26` | NO-GIT-HISTORY (non-git worktree, current tree) | 3. **Dual-Purpose PCBs**: Wing-Boards tragen gleichzeitig Solarzellen | dropped | firmware/PCB/hardware 'board' mention (not an approval body); file kept by step 4 filename rule |
| `esp32-balloon-integration-meshcore-pr:/home/c03rad0r/esp32-balloon-integration-meshcore-pr/docs/adr/004-3d-yagi-antenna-structure.md:28` | NO-GIT-HISTORY (non-git worktree, current tree) | 5. **Identische Boards**: 4x das gleiche Wing-Board = einfachere Fertigung | dropped | firmware/PCB/hardware 'board' mention (not an approval body); file kept by step 4 filename rule |
| `esp32-balloon-integration-meshcore-pr:/home/c03rad0r/esp32-balloon-integration-meshcore-pr/docs/adr/004-3d-yagi-antenna-structure.md:36` | NO-GIT-HISTORY (non-git worktree, current tree) | - Die Kombination aus Antennen und Solar auf denselben Boards | dropped | firmware/PCB/hardware 'board' mention (not an approval body); file kept by step 4 filename rule |
| `esp32-balloon-integration-meshcore-pr:/home/c03rad0r/esp32-balloon-integration-meshcore-pr/docs/adr/004-3d-yagi-antenna-structure.md:49` | NO-GIT-HISTORY (non-git worktree, current tree) | - 4 Wing-Boards stecken durch Slots im zentralen Hub-Board | dropped | firmware/PCB/hardware 'board' mention (not an approval body); file kept by step 4 filename rule |
| `esp32-balloon-integration-meshcore-pr:/home/c03rad0r/esp32-balloon-integration-meshcore-pr/docs/adr/004-3d-yagi-antenna-structure.md:52` | NO-GIT-HISTORY (non-git worktree, current tree) | - Hub-Board sitzt oben (nahe am Ballon), Wings breiten sich nach unten/ausen aus | dropped | firmware/PCB/hardware 'board' mention (not an approval body); file kept by step 4 filename rule |
| `esp32-balloon-integration-meshcore-pr:/home/c03rad0r/esp32-balloon-integration-meshcore-pr/docs/adr/005-sky66112-fem.md:37` | NO-GIT-HISTORY (non-git worktree, current tree) | 1. **PA + LNA + Switch in einem IC**: Spart Gewicht und Board-Flaeche | dropped | firmware/PCB/hardware 'board' mention (not an approval body); file kept by step 4 filename rule |
| `esp32-balloon-integration-meshcore-pr:/home/c03rad0r/esp32-balloon-integration-meshcore-pr/docs/adr/009-antenna-strategy-v1-v2.md:47` | NO-GIT-HISTORY (non-git worktree, current tree) | - No SP4T switch, no antenna switching firmware, no wing board antenna design | dropped | firmware/PCB/hardware 'board' mention (not an approval body); file kept by step 4 filename rule |
| `esp32-balloon-integration-meshcore-pr:/home/c03rad0r/esp32-balloon-integration-meshcore-pr/docs/adr/009-antenna-strategy-v1-v2.md:51` | NO-GIT-HISTORY (non-git worktree, current tree) | - PCB Yagis on wing boards (current design in tracker/hardware/docs/hardware-design.md) | dropped | firmware/PCB/hardware 'board' mention (not an approval body); file kept by step 4 filename rule |
| `esp32-balloon-integration-meshcore-pr:/home/c03rad0r/esp32-balloon-integration-meshcore-pr/docs/adr/009-antenna-strategy-v1-v2.md:55` | NO-GIT-HISTORY (non-git worktree, current tree) | - PCB designed to accommodate SP4T footprint and wing board connectors | dropped | firmware/PCB/hardware 'board' mention (not an approval body); file kept by step 4 filename rule |
| `esp32-balloon-integration-meshcore-pr:/home/c03rad0r/esp32-balloon-integration-meshcore-pr/docs/adr/009-antenna-strategy-v1-v2.md:86` | NO-GIT-HISTORY (non-git worktree, current tree) | - V1 hardware is simpler: no SP4T, no wing board antenna design, no switching firmware | dropped | firmware/PCB/hardware 'board' mention (not an approval body); file kept by step 4 filename rule |
| `esp32-balloon-integration-meshcore-pr:/home/c03rad0r/esp32-balloon-integration-meshcore-pr/docs/adr/009-antenna-strategy-v1-v2.md:88` | NO-GIT-HISTORY (non-git worktree, current tree) | - V2 upgrade path preserved in PCB layout (SP4T footprint, wing board connectors) | dropped | firmware/PCB/hardware 'board' mention (not an approval body); file kept by step 4 filename rule |
| `esp32-balloon-integration-meshcore-pr:/home/c03rad0r/esp32-balloon-integration-meshcore-pr/docs/adr/011-first-flight-strategy.md:48` | NO-GIT-HISTORY (non-git worktree, current tree) | | DIY v0.1 | ~15g | Yes (dev board) | Heavy but easy to assemble | | dropped | firmware/PCB/hardware 'board' mention (not an approval body); file kept by step 4 filename rule |
| `esp32-balloon-integration-meshcore-pr:/home/c03rad0r/esp32-balloon-integration-meshcore-pr/docs/antenna-strategy.md:175` | NO-GIT-HISTORY (non-git worktree, current tree) | Kein SP4T Switch, keine Antennen-Umschaltung, keine Wing-Board Antennen-Design. | dropped | firmware/PCB/hardware 'board' mention (not an approval body) |
| `esp32-balloon-integration-meshcore-pr:/home/c03rad0r/esp32-balloon-integration-meshcore-pr/docs/antenna-strategy.md:20` | NO-GIT-HISTORY (non-git worktree, current tree) | - Nutzt Laenge des Wing-Boards, Solarzellen daneben platzierbar | dropped | firmware/PCB/hardware 'board' mention (not an approval body) |
| `esp32-balloon-integration-meshcore-pr:/home/c03rad0r/esp32-balloon-integration-meshcore-pr/docs/antenna-strategy.md:215` | NO-GIT-HISTORY (non-git worktree, current tree) | | PCB Yagis auf Wing-Boards (ADR-004) | 6-9 dBi | +0g (geaetzt) + SP4T (+0.1g) | Mittel | | dropped | firmware/PCB/hardware 'board' mention (not an approval body) |
| `esp32-balloon-integration-meshcore-pr:/home/c03rad0r/esp32-balloon-integration-meshcore-pr/docs/antenna-strategy.md:221` | NO-GIT-HISTORY (non-git worktree, current tree) | Das PCB ist bereits mit SP4T-Footprint und Wing-Board Connectors designt — | dropped | firmware/PCB/hardware 'board' mention (not an approval body) |
| `esp32-balloon-integration-meshcore-pr:/home/c03rad0r/esp32-balloon-integration-meshcore-pr/docs/antenna-strategy.md:48` | NO-GIT-HISTORY (non-git worktree, current tree) | - Platzkonflikt mit Solarzellen auf Wing-Board | dropped | firmware/PCB/hardware 'board' mention (not an approval body) |
| `esp32-balloon-integration-meshcore-pr:/home/c03rad0r/esp32-balloon-integration-meshcore-pr/docs/balloon-flight-lessons.md:487` | NO-GIT-HISTORY (non-git worktree, current tree) | - Jetpack boards: $39 (5x from JLCPCB including shipping/tariffs) | dropped | firmware/PCB/hardware 'board' mention (not an approval body) |
| `esp32-balloon-integration-meshcore-pr:/home/c03rad0r/esp32-balloon-integration-meshcore-pr/docs/breadboard-wiring-guide.md:5` | NO-GIT-HISTORY (non-git worktree, current tree) | Wiring guide for the DIY v0.1 development setup on ESP32-C3_Mini_V1 dev board | dropped | firmware/PCB/hardware 'board' mention (not an approval body) |
| `esp32-balloon-integration-meshcore-pr:/home/c03rad0r/esp32-balloon-integration-meshcore-pr/docs/breadboard-wiring-guide.md:97` | NO-GIT-HISTORY (non-git worktree, current tree) | | GPIO20 | - | - | - | SP4T_CTRL_2 | Flight board only | | dropped | firmware/PCB/hardware 'board' mention (not an approval body) |
| `esp32-balloon-integration-meshcore-pr:/home/c03rad0r/esp32-balloon-integration-meshcore-pr/docs/breadboard-wiring-guide.md:98` | NO-GIT-HISTORY (non-git worktree, current tree) | | GPIO21 | - | - | - | SP4T_CTRL_1 | Flight board only | | dropped | firmware/PCB/hardware 'board' mention (not an approval body) |
| `esp32-balloon-integration-meshcore-pr:/home/c03rad0r/esp32-balloon-integration-meshcore-pr/docs/component-guide.md:15` | NO-GIT-HISTORY (non-git worktree, current tree) | | XIAO ESP32C3 | ~4g (Board) | 0 EUR | 20x da | Perfekt fuer Dev/DIY, USB onboard, zu schwer fuer Flight | | dropped | firmware/PCB/hardware 'board' mention (not an approval body) |
| `esp32-balloon-integration-meshcore-pr:/home/c03rad0r/esp32-balloon-integration-meshcore-pr/docs/component-guide.md:150` | NO-GIT-HISTORY (non-git worktree, current tree) | **Empfehlung**: Weglassen fuer DIY/Prototyp. Fuer Flight-Board: P-MOSFET statt | dropped | firmware/PCB/hardware 'board' mention (not an approval body) |
| `esp32-balloon-integration-meshcore-pr:/home/c03rad0r/esp32-balloon-integration-meshcore-pr/docs/component-guide.md:16` | NO-GIT-HISTORY (non-git worktree, current tree) | | ESP-C3-12F bare | ~1.0g | ~2 EUR | Nein | Flight-Board Standard. Flash integriert | | dropped | firmware/PCB/hardware 'board' mention (not an approval body) |
| `esp32-balloon-integration-meshcore-pr:/home/c03rad0r/esp32-balloon-integration-meshcore-pr/docs/component-guide.md:164` | NO-GIT-HISTORY (non-git worktree, current tree) | | BMP280 bare chip | ~0.05g | ~0.50 EUR | Auf Flight-Board geloetet | | dropped | firmware/PCB/hardware 'board' mention (not an approval body) |
| `esp32-balloon-integration-meshcore-pr:/home/c03rad0r/esp32-balloon-integration-meshcore-pr/docs/component-guide.md:171` | NO-GIT-HISTORY (non-git worktree, current tree) | **Empfehlung**: BMP280 fuer Flight-Board (0.5g, guenstig, bewaehrt). Fuer Minimal: | dropped | firmware/PCB/hardware 'board' mention (not an approval body) |
| `esp32-balloon-integration-meshcore-pr:/home/c03rad0r/esp32-balloon-integration-meshcore-pr/docs/component-guide.md:21` | NO-GIT-HISTORY (non-git worktree, current tree) | **Empfehlung**: XIAO C3 fuer Entwicklung, ESP-C3-12F fuer Flight-Board. | dropped | firmware/PCB/hardware 'board' mention (not an approval body) |
| `esp32-balloon-integration-meshcore-pr:/home/c03rad0r/esp32-balloon-integration-meshcore-pr/docs/component-guide.md:251` | NO-GIT-HISTORY (non-git worktree, current tree) | Flight-Board. | dropped | firmware/PCB/hardware 'board' mention (not an approval body) |
| `esp32-balloon-integration-meshcore-pr:/home/c03rad0r/esp32-balloon-integration-meshcore-pr/docs/component-guide.md:313` | NO-GIT-HISTORY (non-git worktree, current tree) | **Warum noetig**: Auf dem Flight-Board verlaufen Solarleitungen und | dropped | firmware/PCB/hardware 'board' mention (not an approval body) |
| `esp32-balloon-integration-meshcore-pr:/home/c03rad0r/esp32-balloon-integration-meshcore-pr/docs/component-guide.md:319` | NO-GIT-HISTORY (non-git worktree, current tree) | | 4x Ferrite Bead 0402 | Standard fuer Flight-Board | | dropped | firmware/PCB/hardware 'board' mention (not an approval body) |
| `esp32-balloon-integration-meshcore-pr:/home/c03rad0r/esp32-balloon-integration-meshcore-pr/docs/component-guide.md:323` | NO-GIT-HISTORY (non-git worktree, current tree) | **Empfehlung**: Nur fuer Flight-Board mit PCB-Yagi relevant. | dropped | firmware/PCB/hardware 'board' mention (not an approval body) |
| `esp32-balloon-integration-meshcore-pr:/home/c03rad0r/esp32-balloon-integration-meshcore-pr/docs/component-guide.md:76` | NO-GIT-HISTORY (non-git worktree, current tree) | **Empfehlung**: Start mit Draht-Dipol (kostenlos). PCB-Yagi fuer Flight-Board als | dropped | firmware/PCB/hardware 'board' mention (not an approval body) |
| `esp32-balloon-integration-meshcore-pr:/home/c03rad0r/esp32-balloon-integration-meshcore-pr/docs/esp32c3-supermini-bringup.md:14` | NO-GIT-HISTORY (non-git worktree, current tree) | - **Long-term fix (HARDWARE)**: Solder a **10k pull-down resistor between GPIO8 and GND** on the dev board. This overrides the LED pull-up at reset, ensuring GPIO8=LOW → SPI boot mode even after USB-initiated resets. Place the resistor close to the GPIO8 pin. | dropped | firmware/PCB/hardware 'board' mention (not an approval body) |
| `esp32-balloon-integration-meshcore-pr:/home/c03rad0r/esp32-balloon-integration-meshcore-pr/docs/esp32c3-supermini-bringup.md:15` | NO-GIT-HISTORY (non-git worktree, current tree) | - **Alternative fix (SOFTWARE)**: Move I2C SDA from GPIO8 to a non-strapping pin (e.g., GPIO1, GPIO19, GPIO20). This would require PCB respin for flight boards but is viable for the dev board with jumper wires. | dropped | firmware/PCB/hardware 'board' mention (not an approval body) |
| `esp32-balloon-integration-meshcore-pr:/home/c03rad0r/esp32-balloon-integration-meshcore-pr/docs/esp32c3-supermini-bringup.md:27` | NO-GIT-HISTORY (non-git worktree, current tree) | - **Cause**: `CONFIG_PM_ENABLE=y` but PM config not fully supported on this board variant | dropped | firmware/PCB/hardware 'board' mention (not an approval body) |
| `esp32-balloon-integration-meshcore-pr:/home/c03rad0r/esp32-balloon-integration-meshcore-pr/docs/esp32c3-supermini-bringup.md:3` | NO-GIT-HISTORY (non-git worktree, current tree) | **Board**: ESP32-C3 SuperMini V1 (4MB XMC flash, detected at `/dev/ttyACM1`) | dropped | firmware/PCB/hardware 'board' mention (not an approval body) |
| `esp32-balloon-integration-meshcore-pr:/home/c03rad0r/esp32-balloon-integration-meshcore-pr/docs/esp32c3-supermini-bringup.md:45` | NO-GIT-HISTORY (non-git worktree, current tree) | - **Cause**: ADC on GPIO0 reads ~1530 mV on USB power (not a real supercap). The 3300 mV threshold is designed for supercap-powered flight boards. | dropped | firmware/PCB/hardware 'board' mention (not an approval body) |
| `esp32-balloon-integration-meshcore-pr:/home/c03rad0r/esp32-balloon-integration-meshcore-pr/docs/esp32c3-supermini-bringup.md:47` | NO-GIT-HISTORY (non-git worktree, current tree) | - **Status**: Temporary workaround for dev board | dropped | firmware/PCB/hardware 'board' mention (not an approval body) |
| `esp32-balloon-integration-meshcore-pr:/home/c03rad0r/esp32-balloon-integration-meshcore-pr/docs/esp32c3-supermini-bringup.md:55` | NO-GIT-HISTORY (non-git worktree, current tree) | ## Board Detection | dropped | firmware/PCB/hardware 'board' mention (not an approval body) |
| `esp32-balloon-integration-meshcore-pr:/home/c03rad0r/esp32-balloon-integration-meshcore-pr/docs/esp32c3-supermini-bringup.md:60` | NO-GIT-HISTORY (non-git worktree, current tree) | | `/dev/ttyACM1` | ESP32-C3 (v0.4) | 4MB XMC | `b0:a6:04:00:96:dc` | LoRa2021 test board | | dropped | firmware/PCB/hardware 'board' mention (not an approval body) |
| `esp32-balloon-integration-meshcore-pr:/home/c03rad0r/esp32-balloon-integration-meshcore-pr/docs/execution-checklist.md:109` | NO-GIT-HISTORY (non-git worktree, current tree) | - [ ] Beide Boards nebeneinander platzieren | dropped | firmware/PCB/hardware 'board' mention (not an approval body) |
| `esp32-balloon-integration-meshcore-pr:/home/c03rad0r/esp32-balloon-integration-meshcore-pr/docs/execution-checklist.md:112` | NO-GIT-HISTORY (non-git worktree, current tree) | - [ ] Board 1: TX-Modus flashen | dropped | firmware/PCB/hardware 'board' mention (not an approval body) |
| `esp32-balloon-integration-meshcore-pr:/home/c03rad0r/esp32-balloon-integration-meshcore-pr/docs/execution-checklist.md:113` | NO-GIT-HISTORY (non-git worktree, current tree) | - [ ] Board 2: RX-Modus flashen | dropped | firmware/PCB/hardware 'board' mention (not an approval body) |
| `esp32-balloon-integration-meshcore-pr:/home/c03rad0r/esp32-balloon-integration-meshcore-pr/docs/execution-checklist.md:114` | NO-GIT-HISTORY (non-git worktree, current tree) | - [ ] Pruefen: Empfängt Board 2 die Nachricht? | dropped | firmware/PCB/hardware 'board' mention (not an approval body) |
| `esp32-balloon-integration-meshcore-pr:/home/c03rad0r/esp32-balloon-integration-meshcore-pr/docs/execution-checklist.md:132` | NO-GIT-HISTORY (non-git worktree, current tree) | - [ ] ESP32-C3_Mini_V1 (3. Board) + Drucksensor verkabeln | dropped | firmware/PCB/hardware 'board' mention (not an approval body) |
| `esp32-balloon-integration-meshcore-pr:/home/c03rad0r/esp32-balloon-integration-meshcore-pr/docs/execution-checklist.md:183` | NO-GIT-HISTORY (non-git worktree, current tree) | - [ ] Abstand zwischen 2 Boards messen | dropped | firmware/PCB/hardware 'board' mention (not an approval body) |
| `esp32-balloon-integration-meshcore-pr:/home/c03rad0r/esp32-balloon-integration-meshcore-pr/docs/first-flight-checklist.md:7` | NO-GIT-HISTORY (non-git worktree, current tree) | - [ ] ESP32-C3_Mini_V1 dev board flashed with `CONFIG_ENABLE_GPS=y` | dropped | firmware/PCB/hardware 'board' mention (not an approval body) |
| `esp32-balloon-integration-meshcore-pr:/home/c03rad0r/esp32-balloon-integration-meshcore-pr/docs/hardware-design.md:1` | NO-GIT-HISTORY (non-git worktree, current tree) | # 3D Hardware-Design: Hub + Wing Boards | dropped | firmware/PCB/hardware 'board' mention (not an approval body) |
| `esp32-balloon-integration-meshcore-pr:/home/c03rad0r/esp32-balloon-integration-meshcore-pr/docs/hardware-design.md:10` | NO-GIT-HISTORY (non-git worktree, current tree) | ## Hub-Board | dropped | firmware/PCB/hardware 'board' mention (not an approval body) |
| `esp32-balloon-integration-meshcore-pr:/home/c03rad0r/esp32-balloon-integration-meshcore-pr/docs/hardware-design.md:111` | NO-GIT-HISTORY (non-git worktree, current tree) | Gesamtlaenge: ~60-65mm (passt auf das Wing-Board) | dropped | firmware/PCB/hardware 'board' mention (not an approval body) |
| `esp32-balloon-integration-meshcore-pr:/home/c03rad0r/esp32-balloon-integration-meshcore-pr/docs/hardware-design.md:116` | NO-GIT-HISTORY (non-git worktree, current tree) | Driven Element → 50 Ohm CPW → TAB-Pin (RF_IN) → Hub-Board → SP4T → FEM → LR2021 | dropped | firmware/PCB/hardware 'board' mention (not an approval body) |
| `esp32-balloon-integration-meshcore-pr:/home/c03rad0r/esp32-balloon-integration-meshcore-pr/docs/hardware-design.md:140` | NO-GIT-HISTORY (non-git worktree, current tree) | Schritt 1: Hub-Board waagerecht halten | dropped | firmware/PCB/hardware 'board' mention (not an approval body) |
| `esp32-balloon-integration-meshcore-pr:/home/c03rad0r/esp32-balloon-integration-meshcore-pr/docs/hardware-design.md:164` | NO-GIT-HISTORY (non-git worktree, current tree) | - Hub-Board oben → waechst in der Mitte des Ballons | dropped | firmware/PCB/hardware 'board' mention (not an approval body) |
| `esp32-balloon-integration-meshcore-pr:/home/c03rad0r/esp32-balloon-integration-meshcore-pr/docs/hardware-design.md:165` | NO-GIT-HISTORY (non-git worktree, current tree) | - Aufhaengung: 30AWG Draht vom Hub-Board zum Ballon | dropped | firmware/PCB/hardware 'board' mention (not an approval body) |
| `esp32-balloon-integration-meshcore-pr:/home/c03rad0r/esp32-balloon-integration-meshcore-pr/docs/hardware-design.md:167` | NO-GIT-HISTORY (non-git worktree, current tree) | ## Dev-Board (Track A) | dropped | firmware/PCB/hardware 'board' mention (not an approval body) |
| `esp32-balloon-integration-meshcore-pr:/home/c03rad0r/esp32-balloon-integration-meshcore-pr/docs/hardware-design.md:169` | NO-GIT-HISTORY (non-git worktree, current tree) | ### XIAO Carrier Board | dropped | firmware/PCB/hardware 'board' mention (not an approval body) |
| `esp32-balloon-integration-meshcore-pr:/home/c03rad0r/esp32-balloon-integration-meshcore-pr/docs/hardware-design.md:191` | NO-GIT-HISTORY (non-git worktree, current tree) | ### Unterschiede zum Flight-Board | dropped | firmware/PCB/hardware 'board' mention (not an approval body) |
| `esp32-balloon-integration-meshcore-pr:/home/c03rad0r/esp32-balloon-integration-meshcore-pr/docs/hardware-design.md:193` | NO-GIT-HISTORY (non-git worktree, current tree) | | Aspekt | Dev-Board | Flight-Board | | dropped | firmware/PCB/hardware 'board' mention (not an approval body) |
| `esp32-balloon-integration-meshcore-pr:/home/c03rad0r/esp32-balloon-integration-meshcore-pr/docs/hardware-design.md:21` | NO-GIT-HISTORY (non-git worktree, current tree) | Hub-Board Top-Ansicht (22x22mm): | dropped | firmware/PCB/hardware 'board' mention (not an approval body) |
| `esp32-balloon-integration-meshcore-pr:/home/c03rad0r/esp32-balloon-integration-meshcore-pr/docs/hardware-design.md:24` | NO-GIT-HISTORY (non-git worktree, current tree) | │ Slot  Slot  Slot  Slot   │ ← 4 Slots fuer Wing-Boards | dropped | firmware/PCB/hardware 'board' mention (not an approval body) |
| `esp32-balloon-integration-meshcore-pr:/home/c03rad0r/esp32-balloon-integration-meshcore-pr/docs/hardware-design.md:44` | NO-GIT-HISTORY (non-git worktree, current tree) | ### Slots fuer Wing-Boards | dropped | firmware/PCB/hardware 'board' mention (not an approval body) |
| `esp32-balloon-integration-meshcore-pr:/home/c03rad0r/esp32-balloon-integration-meshcore-pr/docs/hardware-design.md:46` | NO-GIT-HISTORY (non-git worktree, current tree) | Jeder Slot ist ein ~1mm breiter Schlitz in der Kante des Hub-Boards: | dropped | firmware/PCB/hardware 'board' mention (not an approval body) |
| `esp32-balloon-integration-meshcore-pr:/home/c03rad0r/esp32-balloon-integration-meshcore-pr/docs/hardware-design.md:48` | NO-GIT-HISTORY (non-git worktree, current tree) | - Wing-Board-Tab passt hinein und wird verloetet | dropped | firmware/PCB/hardware 'board' mention (not an approval body) |
| `esp32-balloon-integration-meshcore-pr:/home/c03rad0r/esp32-balloon-integration-meshcore-pr/docs/hardware-design.md:5` | NO-GIT-HISTORY (non-git worktree, current tree) | Das Flug-Board besteht aus 5 PCBs die zu einer 3D-Struktur zusammengeloetet werden: | dropped | firmware/PCB/hardware 'board' mention (not an approval body) |
| `esp32-balloon-integration-meshcore-pr:/home/c03rad0r/esp32-balloon-integration-meshcore-pr/docs/hardware-design.md:59` | NO-GIT-HISTORY (non-git worktree, current tree) | ## Wing-Board | dropped | firmware/PCB/hardware 'board' mention (not an approval body) |
| `esp32-balloon-integration-meshcore-pr:/home/c03rad0r/esp32-balloon-integration-meshcore-pr/docs/hardware-design.md:7` | NO-GIT-HISTORY (non-git worktree, current tree) | - **1x Hub-Board** (zentral): Alle aktiven Elektronik-Komponenten | dropped | firmware/PCB/hardware 'board' mention (not an approval body) |
| `esp32-balloon-integration-meshcore-pr:/home/c03rad0r/esp32-balloon-integration-meshcore-pr/docs/hardware-design.md:70` | NO-GIT-HISTORY (non-git worktree, current tree) | Wing-Board (65x28mm, identisch x4): | dropped | firmware/PCB/hardware 'board' mention (not an approval body) |
| `esp32-balloon-integration-meshcore-pr:/home/c03rad0r/esp32-balloon-integration-meshcore-pr/docs/hardware-design.md:8` | NO-GIT-HISTORY (non-git worktree, current tree) | - **4x Wing-Board** (identisch): PCB-Yagi Antennen + Solarzellen | dropped | firmware/PCB/hardware 'board' mention (not an approval body) |
| `esp32-balloon-integration-meshcore-pr:/home/c03rad0r/esp32-balloon-integration-meshcore-pr/docs/inventory.md:87` | NO-GIT-HISTORY (non-git worktree, current tree) | | Verfuegbare MCU Boards | 22 (20x C3, 2x C5) | | dropped | firmware/PCB/hardware 'board' mention (not an approval body) |
| `esp32-balloon-integration-meshcore-pr:/home/c03rad0r/esp32-balloon-integration-meshcore-pr/docs/inventory.md:98` | NO-GIT-HISTORY (non-git worktree, current tree) | | 1 | ESP-C3-12F bare | Flight-Board | Mittel | ~2 EUR | AliExpress | | dropped | firmware/PCB/hardware 'board' mention (not an approval body) |
| `esp32-balloon-integration-meshcore-pr:/home/c03rad0r/esp32-balloon-integration-meshcore-pr/docs/plan-variants.md:114` | NO-GIT-HISTORY (non-git worktree, current tree) | - Keine Wing-Boards / Yagis: -2.3g | dropped | firmware/PCB/hardware 'board' mention (not an approval body) |
| `esp32-balloon-integration-meshcore-pr:/home/c03rad0r/esp32-balloon-integration-meshcore-pr/docs/plan-variants.md:14` | NO-GIT-HISTORY (non-git worktree, current tree) | | Gewicht | ~15g (mit Board) | ~8-9g | ~12-13g | ~16.6g | | dropped | firmware/PCB/hardware 'board' mention (not an approval body) |
| `esp32-balloon-integration-meshcore-pr:/home/c03rad0r/esp32-balloon-integration-meshcore-pr/docs/plan-variants.md:331` | NO-GIT-HISTORY (non-git worktree, current tree) |   → LoRa TX/RX zwischen 2 Boards | dropped | firmware/PCB/hardware 'board' mention (not an approval body) |
| `esp32-balloon-integration-meshcore-pr:/home/c03rad0r/esp32-balloon-integration-meshcore-pr/docs/plan-variants.md:346` | NO-GIT-HISTORY (non-git worktree, current tree) | Phase 3: Flight-Board bauen + testen (Woche 5-6) | dropped | firmware/PCB/hardware 'board' mention (not an approval body) |
| `esp32-balloon-integration-meshcore-pr:/home/c03rad0r/esp32-balloon-integration-meshcore-pr/docs/plan-variants.md:365` | NO-GIT-HISTORY (non-git worktree, current tree) |   → PCB-Yagis auf Wing-Boards | dropped | firmware/PCB/hardware 'board' mention (not an approval body) |
| `esp32-balloon-integration-meshcore-pr:/home/c03rad0r/esp32-balloon-integration-meshcore-pr/docs/plan-variants.md:78` | NO-GIT-HISTORY (non-git worktree, current tree) | 4. LoRa TX/RX zwischen 2 Boards testen | dropped | firmware/PCB/hardware 'board' mention (not an approval body) |
| `esp32-balloon-integration-meshcore-pr:/home/c03rad0r/esp32-balloon-integration-meshcore-pr/docs/plan.md:109` | NO-GIT-HISTORY (non-git worktree, current tree) | | XIAO ESP32C3 | AliExpress | Dev Board, WiFi/BLE, USB-C | | dropped | firmware/PCB/hardware 'board' mention (not an approval body) |
| `esp32-balloon-integration-meshcore-pr:/home/c03rad0r/esp32-balloon-integration-meshcore-pr/docs/plan.md:110` | NO-GIT-HISTORY (non-git worktree, current tree) | | ESP32-C5 Board | AliExpress | WiFi 6, BT5, Zigbee → Bodenstation | | dropped | firmware/PCB/hardware 'board' mention (not an approval body) |
| `esp32-balloon-integration-meshcore-pr:/home/c03rad0r/esp32-balloon-integration-meshcore-pr/docs/plan.md:131` | NO-GIT-HISTORY (non-git worktree, current tree) | │   ├── hub_board/             # Zentrales Elektronik-Board | dropped | firmware/PCB/hardware 'board' mention (not an approval body) |
| `esp32-balloon-integration-meshcore-pr:/home/c03rad0r/esp32-balloon-integration-meshcore-pr/docs/plan.md:149` | NO-GIT-HISTORY (non-git worktree, current tree) | 5. Dev-Board (XIAO Carrier) schematic in SKiDL | dropped | firmware/PCB/hardware 'board' mention (not an approval body) |
| `esp32-balloon-integration-meshcore-pr:/home/c03rad0r/esp32-balloon-integration-meshcore-pr/docs/plan.md:15` | NO-GIT-HISTORY (non-git worktree, current tree) | | [003](adr/003-dual-track-hardware.md) | Hardware-Strategie | Dual-Track: Dev-Board + Flight-Board | | dropped | firmware/PCB/hardware 'board' mention (not an approval body) |
| `esp32-balloon-integration-meshcore-pr:/home/c03rad0r/esp32-balloon-integration-meshcore-pr/docs/plan.md:164` | NO-GIT-HISTORY (non-git worktree, current tree) | 14. SKiDL Hub-Board Schematic | dropped | firmware/PCB/hardware 'board' mention (not an approval body) |
| `esp32-balloon-integration-meshcore-pr:/home/c03rad0r/esp32-balloon-integration-meshcore-pr/docs/plan.md:165` | NO-GIT-HISTORY (non-git worktree, current tree) | 15. SKiDL Wing-Board Schematic (Yagi + Solar) | dropped | firmware/PCB/hardware 'board' mention (not an approval body) |
| `esp32-balloon-integration-meshcore-pr:/home/c03rad0r/esp32-balloon-integration-meshcore-pr/docs/plan.md:24` | NO-GIT-HISTORY (non-git worktree, current tree) | ### Flug-Board (3D-Struktur, <15g) | dropped | firmware/PCB/hardware 'board' mention (not an approval body) |
| `esp32-balloon-integration-meshcore-pr:/home/c03rad0r/esp32-balloon-integration-meshcore-pr/docs/plan.md:32` | NO-GIT-HISTORY (non-git worktree, current tree) |           ║  HUB-BOARD ║ 22x22mm, 0.6mm FR4 | dropped | firmware/PCB/hardware 'board' mention (not an approval body) |
| `esp32-balloon-integration-meshcore-pr:/home/c03rad0r/esp32-balloon-integration-meshcore-pr/docs/plan.md:39` | NO-GIT-HISTORY (non-git worktree, current tree) |      4x WING BOARDS (je 65x28mm) | dropped | firmware/PCB/hardware 'board' mention (not an approval body) |
| `esp32-balloon-integration-meshcore-pr:/home/c03rad0r/esp32-balloon-integration-meshcore-pr/docs/sx1280-repos-reference.md:18` | NO-GIT-HISTORY (non-git worktree, current tree) | - **Interface**: USB dev board (E28-2G4TBH-01) with CH341 USB-serial adapter | dropped | firmware/PCB/hardware 'board' mention (not an approval body) |
| `esp32-balloon-integration-meshcore-pr:/home/c03rad0r/esp32-balloon-integration-meshcore-pr/docs/sx1280-repos-reference.md:21` | NO-GIT-HISTORY (non-git worktree, current tree) | - **No custom PCBs** — all use commercial USB dev boards | dropped | firmware/PCB/hardware 'board' mention (not an approval body) |
| `esp32-balloon-integration-meshcore-pr:/home/c03rad0r/esp32-balloon-integration-meshcore-pr/docs/sx1280-repos-reference.md:214` | NO-GIT-HISTORY (non-git worktree, current tree) | - No PCB design (all use commercial USB dev boards) | dropped | firmware/PCB/hardware 'board' mention (not an approval body) |
| `esp32-balloon-integration-meshcore-pr:/home/c03rad0r/esp32-balloon-integration-meshcore-pr/mesh-stack/ROADMAP.md:184` | NO-GIT-HISTORY (non-git worktree, current tree) | **SX1280 USB dongle bottleneck:** The Ebyte E28-2G4T27SX USB dev boards use a CH341 USB-serial chip that bottlenecks throughput at ~9600-115200 baud serial. The dongles are useful for range testing and protocol prototyping but **cannot** measure actual radio throughput. Our LR2021 on ESP32-C3 with direct SPI does not have this bottleneck. | dropped | firmware/PCB/hardware 'board' mention (not an approval body) |
| `esp32-balloon-integration-meshcore-pr:/home/c03rad0r/esp32-balloon-integration-meshcore-pr/mesh-stack/ROADMAP.md:329` | NO-GIT-HISTORY (non-git worktree, current tree) | - [x] Create custom `esp32c3_supermini` board definition (fixes XIAO D-pin/GPIO conflict) | dropped | firmware/PCB/hardware 'board' mention (not an approval body) |
| `esp32-balloon-integration-meshcore-pr:/home/c03rad0r/esp32-balloon-integration-meshcore-pr/mesh-stack/ROADMAP.md:334` | NO-GIT-HISTORY (non-git worktree, current tree) | - [x] Flash to ESP32-C3 SuperMini + LR2021 dev board — companion on `/dev/ttyACM2` | dropped | firmware/PCB/hardware 'board' mention (not an approval body) |
| `esp32-balloon-integration-meshcore-pr:/home/c03rad0r/esp32-balloon-integration-meshcore-pr/mesh-stack/ROADMAP.md:633` | NO-GIT-HISTORY (non-git worktree, current tree) | - No SP4T, no switching firmware, no wing board antenna design | dropped | firmware/PCB/hardware 'board' mention (not an approval body) |
| `esp32-balloon-integration-meshcore-pr:/home/c03rad0r/esp32-balloon-integration-meshcore-pr/mesh-stack/ROADMAP.md:638` | NO-GIT-HISTORY (non-git worktree, current tree) | - PCB Yagis on wing boards (current design) or custom CP patches | dropped | firmware/PCB/hardware 'board' mention (not an approval body) |
| `esp32-balloon-integration-meshcore-pr:/home/c03rad0r/esp32-balloon-integration-meshcore-pr/mesh-stack/meshcore-lr2021/README.md:114` | NO-GIT-HISTORY (non-git worktree, current tree) | | 7 | `variants/nicerf_lr2021/NiceRFLR2021Board.h` | 65 | Board: deep sleep on GPIO5 (DIO9), battery ADC | | dropped | firmware/PCB/hardware 'board' mention (not an approval body) |
| `esp32-balloon-integration-meshcore-pr:/home/c03rad0r/esp32-balloon-integration-meshcore-pr/mesh-stack/meshcore-lr2021/README.md:115` | NO-GIT-HISTORY (non-git worktree, current tree) | | 8 | `boards/esp32c3_supermini.json` | 30 | Board JSON: 4MB flash, DIO, USB CDC | | dropped | firmware/PCB/hardware 'board' mention (not an approval body) |
| `esp32-balloon-integration-meshcore-pr:/home/c03rad0r/esp32-balloon-integration-meshcore-pr/mesh-stack/meshcore-lr2021/README.md:191` | NO-GIT-HISTORY (non-git worktree, current tree) | ### Tier 2: Single-Device Hardware Tests (needs wired LR2021 board) | dropped | firmware/PCB/hardware 'board' mention (not an approval body) |
| `esp32-balloon-integration-meshcore-pr:/home/c03rad0r/esp32-balloon-integration-meshcore-pr/mesh-stack/meshcore-lr2021/README.md:280` | NO-GIT-HISTORY (non-git worktree, current tree) | ### Tier 4: Two-Device Integration Tests (our board + friend's device) | dropped | firmware/PCB/hardware 'board' mention (not an approval body) |
| `esp32-balloon-integration-meshcore-pr:/home/c03rad0r/esp32-balloon-integration-meshcore-pr/mesh-stack/meshcore-lr2021/README.md:334` | NO-GIT-HISTORY (non-git worktree, current tree) | │   ├── boards/ | dropped | firmware/PCB/hardware 'board' mention (not an approval body) |
| `esp32-balloon-integration-meshcore-pr:/home/c03rad0r/esp32-balloon-integration-meshcore-pr/mesh-stack/meshcore-lr2021/README.md:335` | NO-GIT-HISTORY (non-git worktree, current tree) | │   │   └── esp32c3_supermini.json  # Board definition (4MB, DIO, USB CDC) | dropped | firmware/PCB/hardware 'board' mention (not an approval body) |
| `esp32-balloon-integration-meshcore-pr:/home/c03rad0r/esp32-balloon-integration-meshcore-pr/mesh-stack/meshcore-lr2021/README.md:340` | NO-GIT-HISTORY (non-git worktree, current tree) | │       ├── NiceRFLR2021Board.h # Board class (deep sleep, battery) | dropped | firmware/PCB/hardware 'board' mention (not an approval body) |
| `esp32-balloon-integration-meshcore-pr:/home/c03rad0r/esp32-balloon-integration-meshcore-pr/mesh-stack/meshcore-lr2021/README.md:46` | NO-GIT-HISTORY (non-git worktree, current tree) | **Root cause**: The XIAO ESP32-C3 board definition (which PlatformIO uses for `board = xiao_esp32c3`) maps `MOSI=GPIO10`, which conflicts with our CS pin on GPIO10. Even with our custom board definition fixing `MOSI=GPIO7`, the Arduino SPI layer still returned zeros — likely a deeper issue with `SPIClass` initialization or DMA configuration. | dropped | firmware/PCB/hardware 'board' mention (not an approval body) |
| `esp32-balloon-integration-meshcore-pr:/home/c03rad0r/esp32-balloon-integration-meshcore-pr/mesh-stack/meshcore-lr2021/UPSTREAM-PR-PLAN.md:114` | NO-GIT-HISTORY (non-git worktree, current tree) |   - [ ] Try PlatformIO `board_build.spi` override | dropped | firmware/PCB/hardware 'board' mention (not an approval body) |
| `esp32-balloon-integration-meshcore-pr:/home/c03rad0r/esp32-balloon-integration-meshcore-pr/mesh-stack/meshcore-lr2021/UPSTREAM-PR-PLAN.md:145` | NO-GIT-HISTORY (non-git worktree, current tree) | - [ ] **1.7** Verify `boards/esp32c3_supermini.json` and `pins_arduino.h` are clean | dropped | firmware/PCB/hardware 'board' mention (not an approval body) |
| `esp32-balloon-integration-meshcore-pr:/home/c03rad0r/esp32-balloon-integration-meshcore-pr/mesh-stack/meshcore-lr2021/UPSTREAM-PR-PLAN.md:15` | NO-GIT-HISTORY (non-git worktree, current tree) | - **EspIdfHal**: Kept as documented workaround (Arduino SPIClass returns zeros on this board) | dropped | firmware/PCB/hardware 'board' mention (not an approval body) |
| `esp32-balloon-integration-meshcore-pr:/home/c03rad0r/esp32-balloon-integration-meshcore-pr/mesh-stack/meshcore-lr2021/UPSTREAM-PR-PLAN.md:209` | NO-GIT-HISTORY (non-git worktree, current tree) | | Custom board definition rejected | Medium | Use devkitm-1 | Offer both options | | dropped | firmware/PCB/hardware 'board' mention (not an approval body) |
| `esp32-balloon-integration-meshcore-pr:/home/c03rad0r/esp32-balloon-integration-meshcore-pr/mesh-stack/meshcore-lr2021/UPSTREAM-PR-PLAN.md:43` | NO-GIT-HISTORY (non-git worktree, current tree) | | Board definition | Custom `esp32c3_supermini.json` | Accurate pin mapping, already working | | dropped | firmware/PCB/hardware 'board' mention (not an approval body) |
| `esp32-balloon-integration-meshcore-pr:/home/c03rad0r/esp32-balloon-integration-meshcore-pr/mesh-stack/meshcore-lr2021/UPSTREAM-PR-PLAN.md:67` | NO-GIT-HISTORY (non-git worktree, current tree) | | 8 | `boards/esp32c3_supermini.json` | ~30 | OK | | dropped | firmware/PCB/hardware 'board' mention (not an approval body) |
| `esp32-balloon-integration-meshcore-pr:/home/c03rad0r/esp32-balloon-integration-meshcore-pr/mesh-stack/research/meshcore-radiolib-wrapper-study.md:138` | NO-GIT-HISTORY (non-git worktree, current tree) |     LR1121Wrapper(LR1121& radio, mesh::MainBoard& board) | dropped | firmware/PCB/hardware 'board' mention (not an approval body) |
| `esp32-balloon-integration-meshcore-pr:/home/c03rad0r/esp32-balloon-integration-meshcore-pr/mesh-stack/research/meshcore-radiolib-wrapper-study.md:139` | NO-GIT-HISTORY (non-git worktree, current tree) |         : RadioLibWrapper(radio, board), _lr1121(&radio) {} | dropped | firmware/PCB/hardware 'board' mention (not an approval body) |
| `esp32-balloon-integration-meshcore-pr:/home/c03rad0r/esp32-balloon-integration-meshcore-pr/mesh-stack/research/routing/meshcore-study.md:184` | NO-GIT-HISTORY (non-git worktree, current tree) | board = esp32-c3-devkitm-1 | dropped | firmware/PCB/hardware 'board' mention (not an approval body) |
| `esp32-balloon-integration-meshcore-pr:/home/c03rad0r/esp32-balloon-integration-meshcore-pr/mesh-stack/research/routing/meshcore-study.md:248` | NO-GIT-HISTORY (non-git worktree, current tree) | - Most relevant reference for our dev boards | dropped | firmware/PCB/hardware 'board' mention (not an approval body) |
| `esp32-balloon-integration-meshcore-pr:/home/c03rad0r/esp32-balloon-integration-meshcore-pr/tracker/ground-station/antenna-tracker/docs/ESP32_DEVKIT_V1_PINOUT.md:3` | NO-GIT-HISTORY (non-git worktree, current tree) | Board identified: | dropped | firmware/PCB/hardware 'board' mention (not an approval body) |
| `esp32-balloon-integration-meshcore-pr:/home/c03rad0r/esp32-balloon-integration-meshcore-pr/tracker/ground-station/antenna-tracker/docs/PROJECT_STATUS.md:4` | NO-GIT-HISTORY (non-git worktree, current tree) | - Board: ESP32-WROOM-32 (rev v3.1) | dropped | firmware/PCB/hardware 'board' mention (not an approval body) |
| `esp32-balloon-integration-meshcore-pr:/home/c03rad0r/esp32-balloon-integration-meshcore-pr/tracker/ground-station/antenna-tracker/docs/WIRING_DIAGRAMS.md:146` | NO-GIT-HISTORY (non-git worktree, current tree) | - ❌ Using only one driver board for two motors | dropped | firmware/PCB/hardware 'board' mention (not an approval body) |
| `esp32-balloon-integration-meshcore-pr:/home/c03rad0r/esp32-balloon-integration-meshcore-pr/tracker/ground-station/antenna-tracker/docs/WIRING_DIAGRAMS.md:6` | NO-GIT-HISTORY (non-git worktree, current tree) | - 2× SBT0811 driver boards (Darlington array) | dropped | firmware/PCB/hardware 'board' mention (not an approval body) |
| `esp32-balloon-integration-meshcore-pr:/home/c03rad0r/esp32-balloon-integration-meshcore-pr/tracker/hardware/hub_board_diy/implementation-plan.md:1` | NO-GIT-HISTORY (non-git worktree, current tree) | # Implementation Plan — DIY v0.1 Dev Board | dropped | firmware/PCB/hardware 'board' mention (not an approval body) |
| `esp32-balloon-integration-meshcore-pr:/home/c03rad0r/esp32-balloon-integration-meshcore-pr/tracker/hardware/hub_board_diy/implementation-plan.md:10` | NO-GIT-HISTORY (non-git worktree, current tree) | - [x] ESP32-C3_Mini_V1 dev board pinout verified (see `hardware/footprints/esp32c3-mini-v1.json`) | dropped | firmware/PCB/hardware 'board' mention (not an approval body) |
| `esp32-balloon-integration-meshcore-pr:/home/c03rad0r/esp32-balloon-integration-meshcore-pr/tracker/hardware/hub_board_diy/implementation-plan.md:118` | NO-GIT-HISTORY (non-git worktree, current tree) | - [ ] Board outline: 45 x 38 mm rectangle with rounded corners | dropped | firmware/PCB/hardware 'board' mention (not an approval body) |
| `esp32-balloon-integration-meshcore-pr:/home/c03rad0r/esp32-balloon-integration-meshcore-pr/tracker/hardware/hub_board_diy/implementation-plan.md:12` | NO-GIT-HISTORY (non-git worktree, current tree) | - [x] GPIO pin mapping verified: all 9 firmware GPIOs accessible on dev board header | dropped | firmware/PCB/hardware 'board' mention (not an approval body) |
| `esp32-balloon-integration-meshcore-pr:/home/c03rad0r/esp32-balloon-integration-meshcore-pr/tracker/hardware/hub_board_diy/implementation-plan.md:120` | NO-GIT-HISTORY (non-git worktree, current tree) |   - ESP32-C3_Mini_V1: left side, oriented with USB-C toward board edge | dropped | firmware/PCB/hardware 'board' mention (not an approval body) |
| `esp32-balloon-integration-meshcore-pr:/home/c03rad0r/esp32-balloon-integration-meshcore-pr/tracker/hardware/hub_board_diy/implementation-plan.md:121` | NO-GIT-HISTORY (non-git worktree, current tree) |   - LoRa2021: right side, ANT pad toward board edge for antenna wire | dropped | firmware/PCB/hardware 'board' mention (not an approval body) |
| `esp32-balloon-integration-meshcore-pr:/home/c03rad0r/esp32-balloon-integration-meshcore-pr/tracker/hardware/hub_board_diy/implementation-plan.md:124` | NO-GIT-HISTORY (non-git worktree, current tree) |   - Antenna pads: right edge of board, accessible for soldering wires | dropped | firmware/PCB/hardware 'board' mention (not an approval body) |
| `esp32-balloon-integration-meshcore-pr:/home/c03rad0r/esp32-balloon-integration-meshcore-pr/tracker/hardware/hub_board_diy/implementation-plan.md:136` | NO-GIT-HISTORY (non-git worktree, current tree) | - [ ] Add silkscreen labels: component references, pin functions, board name "DIY v0.1" | dropped | firmware/PCB/hardware 'board' mention (not an approval body) |
| `esp32-balloon-integration-meshcore-pr:/home/c03rad0r/esp32-balloon-integration-meshcore-pr/tracker/hardware/hub_board_diy/implementation-plan.md:14` | NO-GIT-HISTORY (non-git worktree, current tree) | - [x] Wiring reference CSV created (see `hardware/footprints/wiring-dev-board.csv`) | dropped | firmware/PCB/hardware 'board' mention (not an approval body) |
| `esp32-balloon-integration-meshcore-pr:/home/c03rad0r/esp32-balloon-integration-meshcore-pr/tracker/hardware/hub_board_diy/implementation-plan.md:142` | NO-GIT-HISTORY (non-git worktree, current tree) | - [ ] Export board outline as **SVG** (for FR4 cutting guide) | dropped | firmware/PCB/hardware 'board' mention (not an approval body) |
| `esp32-balloon-integration-meshcore-pr:/home/c03rad0r/esp32-balloon-integration-meshcore-pr/tracker/hardware/hub_board_diy/implementation-plan.md:150` | NO-GIT-HISTORY (non-git worktree, current tree) | **Goal**: Fabricate the board using toner transfer method at c-base workshop. | dropped | firmware/PCB/hardware 'board' mention (not an approval body) |
| `esp32-balloon-integration-meshcore-pr:/home/c03rad0r/esp32-balloon-integration-meshcore-pr/tracker/hardware/hub_board_diy/implementation-plan.md:153` | NO-GIT-HISTORY (non-git worktree, current tree) | - [ ] Cut FR4 board to 45 x 38 mm (using c-base shear or saw) | dropped | firmware/PCB/hardware 'board' mention (not an approval body) |
| `esp32-balloon-integration-meshcore-pr:/home/c03rad0r/esp32-balloon-integration-meshcore-pr/tracker/hardware/hub_board_diy/implementation-plan.md:161` | NO-GIT-HISTORY (non-git worktree, current tree) | - [ ] Let board cool for 5 minutes | dropped | firmware/PCB/hardware 'board' mention (not an approval body) |
| `esp32-balloon-integration-meshcore-pr:/home/c03rad0r/esp32-balloon-integration-meshcore-pr/tracker/hardware/hub_board_diy/implementation-plan.md:167` | NO-GIT-HISTORY (non-git worktree, current tree) | - [ ] Immerse board, agitate gently | dropped | firmware/PCB/hardware 'board' mention (not an approval body) |
| `esp32-balloon-integration-meshcore-pr:/home/c03rad0r/esp32-balloon-integration-meshcore-pr/tracker/hardware/hub_board_diy/implementation-plan.md:169` | NO-GIT-HISTORY (non-git worktree, current tree) | - [ ] Remove board, rinse thoroughly with water | dropped | firmware/PCB/hardware 'board' mention (not an approval body) |
| `esp32-balloon-integration-meshcore-pr:/home/c03rad0r/esp32-balloon-integration-meshcore-pr/tracker/hardware/hub_board_diy/implementation-plan.md:183` | NO-GIT-HISTORY (non-git worktree, current tree) | - [ ] Solder female header sockets for ESP32-C3_Mini_V1 (board plugs in from top) | dropped | firmware/PCB/hardware 'board' mention (not an approval body) |
| `esp32-balloon-integration-meshcore-pr:/home/c03rad0r/esp32-balloon-integration-meshcore-pr/tracker/hardware/hub_board_diy/implementation-plan.md:184` | NO-GIT-HISTORY (non-git worktree, current tree) | - [ ] Solder LoRa2021 castellated pads flat on board surface | dropped | firmware/PCB/hardware 'board' mention (not an approval body) |
| `esp32-balloon-integration-meshcore-pr:/home/c03rad0r/esp32-balloon-integration-meshcore-pr/tracker/hardware/hub_board_diy/implementation-plan.md:20` | NO-GIT-HISTORY (non-git worktree, current tree) | ### Step 1.1: Prepare Dev Board | dropped | firmware/PCB/hardware 'board' mention (not an approval body) |
| `esp32-balloon-integration-meshcore-pr:/home/c03rad0r/esp32-balloon-integration-meshcore-pr/tracker/hardware/hub_board_diy/implementation-plan.md:203` | NO-GIT-HISTORY (non-git worktree, current tree) | - [ ] Plug ESP32-C3_Mini_V1 into the socket on hub board | dropped | firmware/PCB/hardware 'board' mention (not an approval body) |
| `esp32-balloon-integration-meshcore-pr:/home/c03rad0r/esp32-balloon-integration-meshcore-pr/tracker/hardware/hub_board_diy/implementation-plan.md:217` | NO-GIT-HISTORY (non-git worktree, current tree) | - [ ] Use second LoRa2021 board or SDR to verify 868 MHz transmission | dropped | firmware/PCB/hardware 'board' mention (not an approval body) |
| `esp32-balloon-integration-meshcore-pr:/home/c03rad0r/esp32-balloon-integration-meshcore-pr/tracker/hardware/hub_board_diy/implementation-plan.md:242` | NO-GIT-HISTORY (non-git worktree, current tree) | | `hardware/footprints/wiring-dev-board.csv` | Complete firmware-to-hardware wiring reference | | dropped | firmware/PCB/hardware 'board' mention (not an approval body) |
| `esp32-balloon-integration-meshcore-pr:/home/c03rad0r/esp32-balloon-integration-meshcore-pr/tracker/hardware/hub_board_diy/implementation-plan.md:246` | NO-GIT-HISTORY (non-git worktree, current tree) | | `AGENTS.md` | Updated with correct dev board info | | dropped | firmware/PCB/hardware 'board' mention (not an approval body) |
| `esp32-balloon-integration-meshcore-pr:/home/c03rad0r/esp32-balloon-integration-meshcore-pr/tracker/hardware/hub_board_diy/implementation-plan.md:258` | NO-GIT-HISTORY (non-git worktree, current tree) | | U.FL antenna switch not configured | Low | Low | Some boards need solder bridge; check with continuity tester | | dropped | firmware/PCB/hardware 'board' mention (not an approval body) |
| `esp32-balloon-integration-meshcore-pr:/home/c03rad0r/esp32-balloon-integration-meshcore-pr/tracker/hardware/hub_board_diy/implementation-plan.md:268` | NO-GIT-HISTORY (non-git worktree, current tree) | | Phase 4: Integration Test | 1-2 days | Assembled board | | dropped | firmware/PCB/hardware 'board' mention (not an approval body) |
| `esp32-balloon-integration-meshcore-pr:/home/c03rad0r/esp32-balloon-integration-meshcore-pr/tracker/hardware/hub_board_diy/implementation-plan.md:28` | NO-GIT-HISTORY (non-git worktree, current tree) | - [ ] Wire connections per `hardware/footprints/wiring-dev-board.csv`: | dropped | firmware/PCB/hardware 'board' mention (not an approval body) |
| `esp32-balloon-integration-meshcore-pr:/home/c03rad0r/esp32-balloon-integration-meshcore-pr/tracker/hardware/hub_board_diy/implementation-plan.md:5` | NO-GIT-HISTORY (non-git worktree, current tree) | This plan covers all steps from current state (working firmware, verified pin mapping) through to a fully tested hardware prototype on the DIY v0.1 hub board. The board will be fabricated using toner transfer at c-base Berlin. | dropped | firmware/PCB/hardware 'board' mention (not an approval body) |
| `esp32-balloon-integration-meshcore-pr:/home/c03rad0r/esp32-balloon-integration-meshcore-pr/tracker/hardware/hub_board_diy/implementation-plan.md:72` | NO-GIT-HISTORY (non-git worktree, current tree) | **Goal**: Design the DIY v0.1 hub board in KiCad, ready for toner transfer fabrication. | dropped | firmware/PCB/hardware 'board' mention (not an approval body) |
| `esp32-balloon-integration-meshcore-pr:/home/c03rad0r/esp32-balloon-integration-meshcore-pr/tracker/hardware/hub_board_diy/implementation-plan.md:90` | NO-GIT-HISTORY (non-git worktree, current tree) |   - Pad size: 1.0mm x 1.5mm (castellated, extending to board edge) | dropped | firmware/PCB/hardware 'board' mention (not an approval body) |
| `esp32-balloon-integration-meshcore-pr:/home/c03rad0r/esp32-balloon-integration-meshcore-pr/tracker/hardware/hub_board_diy/implementation-plan.md:92` | NO-GIT-HISTORY (non-git worktree, current tree) |   - 22.52 x 18mm board outline (reference, not copper) | dropped | firmware/PCB/hardware 'board' mention (not an approval body) |
| `esp32-balloon-integration-meshcore-pr:/home/c03rad0r/esp32-balloon-integration-meshcore-pr/tracker/hardware/hub_board_diy/plan.md:1` | NO-GIT-HISTORY (non-git worktree, current tree) | # DIY v0.1 Hub Board — PCB Design Plan | dropped | firmware/PCB/hardware 'board' mention (not an approval body) |
| `esp32-balloon-integration-meshcore-pr:/home/c03rad0r/esp32-balloon-integration-meshcore-pr/tracker/hardware/hub_board_diy/plan.md:181` | NO-GIT-HISTORY (non-git worktree, current tree) | ## Board Layout (ASCII, bottom copper view) | dropped | firmware/PCB/hardware 'board' mention (not an approval body) |
| `esp32-balloon-integration-meshcore-pr:/home/c03rad0r/esp32-balloon-integration-meshcore-pr/tracker/hardware/hub_board_diy/plan.md:206` | NO-GIT-HISTORY (non-git worktree, current tree) | Complete wiring table saved as CSV: `hardware/footprints/wiring-dev-board.csv` | dropped | firmware/PCB/hardware 'board' mention (not an approval body) |
| `esp32-balloon-integration-meshcore-pr:/home/c03rad0r/esp32-balloon-integration-meshcore-pr/tracker/hardware/hub_board_diy/plan.md:22` | NO-GIT-HISTORY (non-git worktree, current tree) | | U1 | ESP32-C3_Mini_V1 (Maker go) | Through-hole 2x8 pin header 2.54mm | 1 | Dev board, USB-C, U.FL antenna | | dropped | firmware/PCB/hardware 'board' mention (not an approval body) |
| `esp32-balloon-integration-meshcore-pr:/home/c03rad0r/esp32-balloon-integration-meshcore-pr/tracker/hardware/hub_board_diy/plan.md:250` | NO-GIT-HISTORY (non-git worktree, current tree) | 9. Export **board outline** as SVG -> for cutting FR4 | dropped | firmware/PCB/hardware 'board' mention (not an approval body) |
| `esp32-balloon-integration-meshcore-pr:/home/c03rad0r/esp32-balloon-integration-meshcore-pr/tracker/hardware/hub_board_diy/plan.md:255` | NO-GIT-HISTORY (non-git worktree, current tree) | 12. Cut FR4 board to ~45x38mm using shear or saw | dropped | firmware/PCB/hardware 'board' mention (not an approval body) |
| `esp32-balloon-integration-meshcore-pr:/home/c03rad0r/esp32-balloon-integration-meshcore-pr/tracker/hardware/hub_board_diy/plan.md:262` | NO-GIT-HISTORY (non-git worktree, current tree) |     - ESP32-C3_Mini_V1: through-hole headers, board plugs in from top | dropped | firmware/PCB/hardware 'board' mention (not an approval body) |
| `esp32-balloon-integration-meshcore-pr:/home/c03rad0r/esp32-balloon-integration-meshcore-pr/tracker/hardware/hub_board_diy/plan.md:263` | NO-GIT-HISTORY (non-git worktree, current tree) |     - LoRa2021: solder castellated pads flat on board surface | dropped | firmware/PCB/hardware 'board' mention (not an approval body) |
| `esp32-balloon-integration-meshcore-pr:/home/c03rad0r/esp32-balloon-integration-meshcore-pr/tracker/hardware/hub_board_diy/plan.md:273` | NO-GIT-HISTORY (non-git worktree, current tree) | 21. Test LoRa TX/RX between 2 boards | dropped | firmware/PCB/hardware 'board' mention (not an approval body) |
| `esp32-balloon-integration-meshcore-pr:/home/c03rad0r/esp32-balloon-integration-meshcore-pr/tracker/hardware/hub_board_diy/plan.md:285` | NO-GIT-HISTORY (non-git worktree, current tree) |     ├── hub_board_diy_outline.svg           (board cutting) | dropped | firmware/PCB/hardware 'board' mention (not an approval body) |
| `esp32-balloon-integration-meshcore-pr:/home/c03rad0r/esp32-balloon-integration-meshcore-pr/tracker/hardware/hub_board_diy/plan.md:3` | NO-GIT-HISTORY (non-git worktree, current tree) | ## Board Specification | dropped | firmware/PCB/hardware 'board' mention (not an approval body) |
| `esp32-balloon-integration-meshcore-pr:/home/c03rad0r/esp32-balloon-integration-meshcore-pr/tracker/hardware/hub_board_diy/plan.md:35` | NO-GIT-HISTORY (non-git worktree, current tree) | ## ESP32-C3_Mini_V1 Dev Board | dropped | firmware/PCB/hardware 'board' mention (not an approval body) |

## 6. Files kept by the step-4 filename rule (design-review-notes / ADR-* / *decision* / *rfc*)

The rule was applied to every rev of every git root. All matches were **git roots**; none exists in
the non-git esp32-* dirs scanned here. Their whole-file context is recorded in §7.

| repo | path | revs present | disposition |
|---|---|---|---|
| esp32-balloon-integration-meshcore-pr | `/home/c03rad0r/esp32-balloon-integration-meshcore-pr/docs/adr/001-esp32-c3-as-mcu.md` | WORKTREE-ASIS | all matched lines dropped (hardware `board` / substring noise) — see §5 |
| esp32-balloon-integration-meshcore-pr | `/home/c03rad0r/esp32-balloon-integration-meshcore-pr/docs/adr/003-dual-track-hardware.md` | WORKTREE-ASIS | all matched lines dropped (hardware `board` / substring noise) — see §5 |
| esp32-balloon-integration-meshcore-pr | `/home/c03rad0r/esp32-balloon-integration-meshcore-pr/docs/adr/004-3d-yagi-antenna-structure.md` | WORKTREE-ASIS | all matched lines dropped (hardware `board` / substring noise) — see §5 |
| esp32-balloon-integration-meshcore-pr | `/home/c03rad0r/esp32-balloon-integration-meshcore-pr/docs/adr/005-sky66112-fem.md` | WORKTREE-ASIS | all matched lines dropped (hardware `board` / substring noise) — see §5 |
| esp32-balloon-integration-meshcore-pr | `/home/c03rad0r/esp32-balloon-integration-meshcore-pr/docs/adr/007-adaptive-protocol.md` | WORKTREE-ASIS | all matched lines dropped (hardware `board` / substring noise) — see §5 |
| esp32-balloon-integration-meshcore-pr | `/home/c03rad0r/esp32-balloon-integration-meshcore-pr/docs/adr/009-antenna-strategy-v1-v2.md` | WORKTREE-ASIS | all matched lines dropped (hardware `board` / substring noise) — see §5 |
| esp32-balloon-integration-meshcore-pr | `/home/c03rad0r/esp32-balloon-integration-meshcore-pr/docs/adr/011-first-flight-strategy.md` | WORKTREE-ASIS | all matched lines dropped (hardware `board` / substring noise) — see §5 |
| esp32-balloon-integration-meshcore-pr | `/home/c03rad0r/esp32-balloon-integration-meshcore-pr/docs/adr/012-mesh-networking-strategy.md` | WORKTREE-ASIS | all matched lines dropped (hardware `board` / substring noise) — see §5 |
| esp32-balloon-integration-meshcore-pr | `/home/c03rad0r/esp32-balloon-integration-meshcore-pr/docs/adr/013-cluster-aware-stratorelay.md` | WORKTREE-ASIS | all matched lines dropped (hardware `board` / substring noise) — see §5 |
| esp32-tollgate | `docs/ADR-001-tollgate-over-lr2021.md` | remotes/origin/balloon-tollgate-c3-port | **has 2 §4b `ambiguous` row(s)**; other matched lines dropped |
| esp32-tollgate | `docs/BALLOON-SCOPE-DECISIONS.md` | remotes/origin/balloon-tollgate-c3-port | all matched lines dropped (hardware `board` / substring noise) — see §5 |
| esp32-tollgate | `docs/adr/ADR-XXX-balloon-stratum-relay.md` | remotes/origin/balloon-pow-e-hash|remotes/origin/balloon-pow-extraction | **has 3 §4b `ambiguous` row(s)**; other matched lines dropped |
| esp32-tollgate | `docs/adr/adr-balloon-stratum-relay-DECISIONS.md` | remotes/origin/balloon-pow-e-hash|remotes/origin/balloon-pow-extraction | **has 1 §4b `ambiguous` row(s)**; other matched lines dropped |

So of the step-4 filename keeps, only 3 files carry a row into §4; the rest are recorded as
drops in §5 with their verbatim lines.
Note: tollgate-esp32 `master` itself contains **no** `ADR*` / `*decision*` / `*rfc*` / `design-review-notes` file (verified with `git ls-tree -r --name-only master | grep -iE 'adr|decision|rfc'` = empty). The ADR files in §6 exist only on the balloon branches/tags listed.

## 7. Per-file context for step-4 keeps (paragraph quotes)

Full surrounding-paragraph extraction for the narrowed candidate set is committed at
`raw/esp32-recon/out/contexts.txt`: a ±3-line window for every §4 row, plus the **full body** of
every step-4 filename-kept file (marked `[STEP4-FILE-KEEP]`). Nothing in those paragraphs describes a shadow card, a human gate, or a board approval
process — the balloon ADRs are radio/hardware/enclosure decisions (`ADR-001 ESP32-C3 as MCU`,
`003 dual-track hardware`, `004 3D yagi antenna`, `005 SKY66112 FEM`, `007 adaptive protocol`,
`009 antenna strategy`, `011 first flight strategy`, `012 mesh networking strategy`,
`013 cluster-aware statorelay`) and the tollgate ADRs are `ADR-001 tollgate-over-LR2021` and
`ADR-XXX balloon-stratum-relay` + its `-DECISIONS` companion.

## 8. Handoff notes for the downstream narrowing/merge task

1. This shard produced **no esp32-* hit** for `shadow card` or `human gate`; the only approval-adjacent
   vocabulary in the whole family is the single out-of-shard `gatekeeper` line (§4a) and the
   payment/access gating set (§4b).
2. `decision`-named files exist but their content is scope/hardware decisions, not an approval
   mechanism (e.g. `docs/BALLOON-SCOPE-DECISIONS.md` lists which firmware modules to keep).
3. `esp32-tollgate` and the dir `tollgate-esp32` are the same project; treat as one root.
4. `esp32-tollgate-relay` and `esp32-repeater-captive-portal` are non-git trees (no history, so
   dates are unavailable for them; they are copies of tollgate-esp32 content).
5. `esp32-balloon-integration` was left to its owning shard; the reachable hyphen-variant worktree
   (`esp32-balloon-integration-meshcore-pr`) is the only balloon material in this shard's list.

