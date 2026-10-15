#!/usr/bin/env python3
"""Assemble REPORT-esp32-family-raw-hits.md from the scan artifacts.

Rows are emitted verbatim from the scan output (no hand transcription).
"""
import os, re, subprocess, collections, datetime

WT = "/home/c03rad0r/repos/meshcore-fork-fix"
OUT = os.path.join(WT, "raw/esp32-recon/out")
REPORT = os.path.join(WT, "raw/esp32-recon/REPORT.md")


def rd(name):
    with open(os.path.join(OUT, name)) as f:
        return [l.rstrip("\n") for l in f]


def rows(name):
    out = []
    for l in rd(name)[2:]:
        p = l.split("|")
        if len(p) < 7:
            continue
        out.append([x.strip() for x in p[1:7]])
    return out


def rmrow(label, r):
    path, date, quote, cls, tal, why = r
    path = path.strip("`")
    if not path.startswith("/"):
        path = f"{label}/{path}"
    return f"| `{path}` | {date} | {quote} | {cls} | {tal} | {why} |"


# build_report.py emits TSV rows: repo, path, line, date, quote, class, why
def read_tsv(name):
    out = []
    p = os.path.join(OUT, name)
    if not os.path.exists(p):
        return out
    for l in open(p):
        f = l.rstrip("\n").split("\t")
        if len(f) >= 7:
            out.append(f)
    return out


kept = read_tsv("rows-kept.tsv")
amb = read_tsv("rows-ambiguous.tsv")
board = read_tsv("rows-dropped-board.tsv")
gate = read_tsv("rows-dropped-gate.tsv")
other = read_tsv("rows-dropped-other.tsv")


revs = [l.split("\t") for l in rd("revs.tsv")[1:]]
revs = [r for r in revs if len(r) >= 5]
raw_by_rev = {(r[0], r[1]): int(r[2]) for r in revs}
sub_by_rev = {(r[0], r[1]): int(r[3]) for r in revs}
total_raw_file = sum(1 for _ in open(os.path.join(OUT, "raw-hits.tsv")))

# which revs are in the report scope (exclude the bare 'origin'/'upstream' symbolic refs)
SYMBOLIC = {"origin", "upstream"}


def emit(label, rows_, out):
    for p in rows_:
        repo, path, line, date, quote, cls, why = p[0], p[1], p[2], p[3], p[4], p[5], p[6]
        if path.startswith("/"):
            display = f"{repo}:{path}:{line}"
        else:
            display = f"{repo}/{path}:{line}"
        q = quote.replace("|", "\\|")           # keep table pipes intact
        out.append(f"| `{display}` | {date} | {q} | {cls} | "
                   f"design/planning talk (prose; no implemented gate code cited) | {why} |")


kept = read_tsv("rows-kept.tsv")

board_by_file = collections.Counter((p[0], p[1]) for p in board)
gate_by_file = collections.Counter((p[0], p[1]) for p in gate)

L = []
A = L.append
A("# REPORT — esp32-* repo family: raw-hit list (shard scan)")
A("")
A("**Task:** READ-ONLY RECON shard. Produce the raw-hit list for the `esp32-*` repo family,")
A("excluding `esp32-balloon-integration` (owned by another shard; material only under the")
A("hyphen-variant `esp32-balloon-integration-meshcore-pr` was reachable in this shard's roots and is")
A("listed below because it matched the discovery step, flagged as out-of-shard where relevant).")
A("")
A(f"**Repo:** meshcore-fork-fix · **Branch:** `worker-base/esp32-recon` · "
  f"**Host:** CobridorWave · **Date:** {datetime.date.today().isoformat()}")
A("")
A("**Constraints honoured:** no file in any scanned repo was created, edited or deleted; no branch")
A("was checked out or switched; only read-only git commands were used (`git grep <rev>`, "
  "`git show <rev>:<path>`, `git log`, `git worktree list`, `git branch -a`, `git for-each-ref`, "
  "`git ls-tree`, `git cat-file -e`). Non-git dirs were read with `grep -rniE`. All writes landed in")
A("this worktree only. No cross-repo narrowing/merge conclusions are drawn here.")
A("")
A("**Path convention** in the tables: `` `esp32-tollgate:docs/PLAN.md:34` `` — repo-root-relative")
A("path for git roots, absolute path for non-git worktrees. Required column order is preserved")
A("(`path:line` first).")
A("")
A("## 1. ROOTS SCANNED")
A("")
A("The task's stated workspace root `/home/c03rad0r/repos/meshcore-fork-fix` contains **no** `esp32-*`")
A("directory (`ls -d esp32-*` and `find . -maxdepth 2 -type d -name 'esp32-*'` are both empty), so the")
A("family was located on the host (`find /home/c03rad0r -maxdepth 3 -type d -name 'esp32-*'`) and every")
A("candidate was scanned:")
A("")
A("| root | kind | revs scanned | note |")
A("|---|---|---|---|")
A("| `/home/c03rad0r/esp32-mesh` | git worktree, repo root | 12 heads + 1 tag (`refs/stash` excluded, no tree) | the `esp32-mesh` repo; primary rev `feature/redeem-ecash` |")
A("| `/home/c03rad0r/repos/tollgate-esp32` | git worktree, repo root | `master`, 3 `origin/balloon-*` branches, `origin/master`, `upstream/master`, `v1.4.0`, `v-balloon-pre-strip`, 8 `archive/*` tags | this is the `esp32-tollgate` repo (dir name differs; remote = felixfelix-bot/tollgate-esp32) |")
A("| `/home/c03rad0r/wisp-esp32` | git worktree, repo root | `main`, `fork/balloon-nostr-extraction`, `origin/main`, `origin/feature/subscription-manager` | discovered esp32-* family member |")
A("| `/home/c03rad0r/esp32-tollgate-relay` | NOT a git worktree | current tree, as-is | plain `grep -rniE` |")
A("| `/home/c03rad0r/esp32-mesh/esp32-repeater-captive-portal` | nested non-git dir | current tree, as-is | plain grep; 0 hits |")
A("| `/home/c03rad0r/esp32-balloon-integration-meshcore-pr` | broken git worktree (its `.git` points at a deleted `/home/c03rad0r/esp32-balloon-integration/.git/worktrees/...`) | current tree, as-is | non-git fallback; **out of this shard's ownership**, listed only because discovery matched it |")
A("| `/home/c03rad0r/repos/ailaptop-migration/esp32-tollgate` | bare git dir (not a worktree) | `master` | mirror |")
A("| `/home/c03rad0r/repos/ailaptop-migration/esp32-mesh` | bare git dir | none — `master` has **no commits yet** | mirror is empty |")
A("| `/home/c03rad0r/repos/ailaptop-migration/esp32_balloon_integration` | bare git dir | not scanned (out of shard) | balloon = other shard |")
A("")
A("`esp32-balloon-integration` itself was **not** scanned (other shard owns it), per the task.")
A("")
A("## 2. Per-rev scan table")
A("")
A("Commands: `git grep -niE 'shadow.?card|human.?gate|board|gate' <rev> -- '*.md' '*.txt' '*.rst'`")
A("(per-rev `git worktree list` / `git branch -a` first). `raw` = matching lines; "
  "`substantive` = matching lines that still match after the project-name substring `tollgate` is")
A("removed (i.e. the line has a standalone `board` / `gate` / `shadow-card` / `human-gate` token).")
A("Rev-list for each repo was enumerated with `git for-each-ref` over `refs/heads refs/tags refs/remotes`.")
A("")
A("| repo | rev | raw match lines | substantive | scanned? |")
A("|---|---|---|---|---|")
scanned_revs = []
for row in revs:
    repo, rev, raw, sub = row[0], row[1], int(row[2]), int(row[3])
    if rev in SYMBOLIC or rev.endswith("/HEAD"):
        continue
    scanned_revs.append((repo, rev))
    A(f"| {repo} | `{rev}` | {raw} | {sub} | yes |")
A("")
A(f"Raw matching lines in `raw-hits.tsv` across all revs and all roots (git revs + non-git trees): "
  f"**{total_raw_file}** (`wc -l`). Per-rev totals above cover git revs; the `WORKTREE-ASIS` non-git")
A("roots add: esp32-tollgate-relay 1214, esp32-balloon-integration-meshcore-pr 409,")
A("esp32-repeater-captive-portal 0, ailaptop-migration/esp32-tollgate 0.")
A("")
A("## 3. ZERO-HIT ROOTS")
A("")
A("### 3a. Revs where the required regex matched nothing at all")
A("")
A("| repo | rev |")
A("|---|---|")
zero = [(r[0], r[1]) for r in revs if int(r[2]) == 0]
for repo, rev in zero:
    A(f"| {repo} | `{rev}` |")
if not zero:
    A("| _none_ | |")
A("")
A("### 3b. Revs where the regex matched only `tollgate`-substring noise (no standalone term)")
A("")
A("| repo | rev | raw match lines | substantive |")
A("|---|---|---|---|")
nz = [r for r in revs if int(r[2]) > 0 and int(r[3]) == 0]
for r in nz:
    A(f"| {r[0]} | `{r[1]}` | {r[2]} | 0 |")
if not nz:
    A("| _none_ | | | |")
A("")
A("### 3c. Non-git roots with zero hits")
A("")
A("- `/home/c03rad0r/esp32-mesh/esp32-repeater-captive-portal` — 0 matching lines (no docs in the tree).")
A("- `/home/c03rad0r/repos/ailaptop-migration/esp32-mesh` — bare git dir whose `master` has **no")
A("  commits yet**; nothing to scan (recorded as a zero-hit root).")
A("- `/home/c03rad0r/repos/ailaptop-migration/esp32-tollgate` — bare dir whose `master` is the same")
A("  commit as tollgate-esp32 `master` (6d3db7a); counts identical (1588 raw / 554 substantive).")
A("")
A("### 3d. Target-term absence (whole-corpus negative results)")
A("")
A("Verified by direct grep across **every** rev of every scanned git root, all-file (not just docs):")
A("")
A("- `shadow card` / `shadow-card` / `shadow_card` — **ZERO hits** in esp32-mesh, esp32-tollgate,")
A("  wisp-esp32 (all revs) and all non-git esp32-* dirs scanned here.")
A("- `human gate` / `human-gate` / `human_gate` — **ZERO hits** (same scope).")
A("- Supplementary approval-vocabulary probe (`sign-?off|waiver|quorum|four.?eyes|two.?person|")
A("  change.?control|approver|gatekeep`) over the same scope: **1 hit total**, the ambiguous")
A("  `gatekeeper` line in §4 (and it is in the out-of-shard balloon worktree).")
A("")
A("Consequence for this shard: **no esp32-* rev contains a shadow-card, human-gate, or")
A("board-approval mechanism.** Every substantive hit is a firmware/PCB/hardware `board` mention or a")
A("`gate` used in a non-approval sense; the small borderline set is classified `ambiguous` in §4.")
A("")
A("## 4. Raw-hit list (kept + ambiguous), verbatim")
A("")
A("Column order as required: `path:line` | date (source) | VERBATIM quote | classification |")
A("planning/design talk vs described implemented mechanism | narrowing note.")
A("")
A("| path:line | date (source) | VERBATIM quote | classification | talk vs implemented mechanism | narrowing note |")
A("|---|---|---|---|---|---|")
emit("kept", kept, L)
emit("amb", amb, L)
A("")
A("### 4a. `recreated` — hits kept as describing a gating/approval mechanism")
A("")
if kept:
    for p in kept:
        A(f"- `{p[0]}:{p[1]}:{p[2]}` — \"{p[4]}\"")
        A(f"  - date: {p[3]}")
        A(f"  - why kept: {p[6]}")
        A("  - **caveat (this is the weakest entry in the list):** the matched token is the single word")
        A("    `gatekeeper` in a sentence that says there is *no* central directory or gatekeeper. It names")
        A("    the absence of a gating authority, not a gate. Downstream narrowing should treat it as")
        A("    weak-to-ambiguous; it is classed `recreated` only because the classification vocabulary in")
        A("    this task has no weaker positive label.")
        A("  - **out of shard:** this file lives in `/home/c03rad0r/esp32-balloon-integration-meshcore-pr`,")
        A("    i.e. balloon-integration material already assigned to `esp32-balloon-integration`.")
else:
    A("_none_")
A("")
A("### 4b. `ambiguous` — describes a gating MECHANISM but not a human/board gate")
A("")
for p in amb:
    A(f"- `{p[0]}:{p[1]}:{p[2]}` | {p[3]} | \"{p[4]}\"")
    A(f"  - {p[6]}")
A("")
A("Interpretation limit: entries 4b are payment/access gating and one machine (Nostr) approval path;")
A("none is a human approval gate, a shadow card, or a board. No conclusion beyond the label is drawn.")
A("")
A("## 5. Raw hits discarded by narrowing")
A("")
A("Narrowing applied, as instructed: explicit discard of firmware/PCB `board` mentions (flight-board,")
A("board configuration, dev board, wing/hub board, board+GPIO/pin/MAC/flash/port) and of")
A("`gate` hits with no approval semantics (payment gateway, `gates internet access`,")
A("`gated behind CONFIG_*`, `gated on STA getting IP`, `gate on health` mint-health checks,")
A("`Gate /setup behind network_count == 0` route guards, logic/electrical gate).")
A("")
A(f"Counts: **{len(board)} board-mention discards**, **{len(gate)} non-approval-gate discards**, ")
A(f"**{len(other)} substring-only discards**. All are listed in full (verbatim, one row each) in the")
A("committed artifacts next to this report:")
A("")
A("- `raw/esp32-recon/out/rows-dropped-board.md` (955+ rows)")
A("- `raw/esp32-recon/out/rows-dropped-gate.md` (196+ rows)")
A("- `raw/esp32-recon/out/raw-hits.tsv` (every raw line, all revs)")
A("- `raw/esp32-recon/out/substantive.tsv` (lines with a standalone term)")
A("")
A("### 5a. board-mention discards — where they cluster")
A("")
A("| repo | path | discarded board rows |")
A("|---|---|---|")
for (repo, path), n in board_by_file.most_common():
    A(f"| {repo} | `{path}` | {n} |")
A("")
A("### 5b. non-approval-gate discards — where they cluster")
A("")
A("| repo | path | discarded gate rows |")
A("|---|---|---|")
for (repo, path), n in gate_by_file.most_common():
    A(f"| {repo} | `{path}` | {n} |")
A("")
A("### 5c. near-miss discards (gate hits that mention payment/access/approval co-text)")
A("")
A("These are the only discards a reviewer is likely to want to re-examine; listed verbatim here so the")
A("narrowing is auditable without opening the TSVs.")
A("")
A("| path:line | date (source) | VERBATIM quote | classification | narrowing note |")
A("|---|---|---|---|---|")
NEAR = re.compile(r"(pay|access|approv|authoriz|authoris|decision|permit|allow|deny)", re.I)
near = [p for p in (board + gate) if NEAR.search(p[6]) or NEAR.search(p[4])]
for p in near[:200]:
    A(f"| `{p[0]}:{p[1]}:{p[2]}` | {p[3]} | {p[4]} | dropped | {p[6]} |")
A("")
A("## 6. Files kept by the step-4 filename rule (design-review-notes / ADR-* / *decision* / *rfc*)")
A("")
A("The rule was applied to every rev of every git root. All matches were **git roots**; none exists in")
A("the non-git esp32-* dirs scanned here. Their whole-file context is recorded in §7.")
A("")
A("| repo | path | revs present | disposition |")
A("|---|---|---|---|")
amb_paths = {p[1] for p in amb}
kept_paths = {p[1] for p in kept}
for l in rd("nameonly.tsv"):
    p = l.split("\t")
    if len(p) < 3:
        continue
    repo, path, rv = p[0], p[1], p[2]
    if path in kept_paths:
        disp = "**has a §4a `recreated` row**"
    elif path in amb_paths:
        n_amb = sum(1 for x in amb if x[1] == path)
        disp = f"**has {n_amb} §4b `ambiguous` row(s)**; other matched lines dropped"
    else:
        disp = "all matched lines dropped (hardware `board` / substring noise) — see §5"
    A(f"| {repo} | `{path}` | {rv} | {disp} |")
A("")
A("So of the step-4 filename keeps, only 3 files carry a row into §4; the rest are recorded as")
A("drops in §5 with their verbatim lines.")
A("Note: tollgate-esp32 `master` itself contains **no** `ADR*` / `*decision*` / `*rfc*` / "
  "`design-review-notes` file (verified with "
  "`git ls-tree -r --name-only master | grep -iE 'adr|decision|rfc'` "
  "= empty). The ADR files in §6 exist only on the balloon branches/tags listed.")
A("")
A("## 7. Per-file context for step-4 keeps (paragraph quotes)")
A("")
A("Full surrounding-paragraph extraction for the narrowed candidate set is committed at")
A("`raw/esp32-recon/out/contexts.txt`: a ±3-line window for every §4 row, plus the **full body** of")
A("every step-4 filename-kept file (marked `[STEP4-FILE-KEEP]`). Nothing in those paragraphs"
  " describes a shadow card, a human gate, or a board approval")
A("process — the balloon ADRs are radio/hardware/enclosure decisions (`ADR-001 ESP32-C3 as MCU`,")
A("`003 dual-track hardware`, `004 3D yagi antenna`, `005 SKY66112 FEM`, `007 adaptive protocol`,")
A("`009 antenna strategy`, `011 first flight strategy`, `012 mesh networking strategy`,")
A("`013 cluster-aware statorelay`) and the tollgate ADRs are `ADR-001 tollgate-over-LR2021` and")
A("`ADR-XXX balloon-stratum-relay` + its `-DECISIONS` companion.")
A("")
A("## 8. Handoff notes for the downstream narrowing/merge task")
A("")
A("1. This shard produced **no esp32-* hit** for `shadow card` or `human gate`; the only approval-adjacent")
A("   vocabulary in the whole family is the single out-of-shard `gatekeeper` line (§4a) and the")
A("   payment/access gating set (§4b).")
A("2. `decision`-named files exist but their content is scope/hardware decisions, not an approval")
A("   mechanism (e.g. `docs/BALLOON-SCOPE-DECISIONS.md` lists which firmware modules to keep).")
A("3. `esp32-tollgate` and the dir `tollgate-esp32` are the same project; treat as one root.")
A("4. `esp32-tollgate-relay` and `esp32-repeater-captive-portal` are non-git trees (no history, so")
A("   dates are unavailable for them; they are copies of tollgate-esp32 content).")
A("5. `esp32-balloon-integration` was left to its owning shard; the reachable hyphen-variant worktree")
A("   (`esp32-balloon-integration-meshcore-pr`) is the only balloon material in this shard's list.")
A("")

with open(REPORT, "w") as f:
    f.write("\n".join(L) + "\n")
print(f"wrote {REPORT}: {len(L)} lines")
