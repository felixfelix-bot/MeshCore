#!/usr/bin/env python3
"""Rebuild out/contexts.txt: (a) ±3-line context for every §4 row, (b) full body of every
step-4 filename-kept file. READ-ONLY w.r.t. scanned repos."""
import os, subprocess

OUT = "/home/c03rad0r/repos/meshcore-fork-fix/raw/esp32-recon/out"
REPO_DIR = {"esp32-mesh": "/home/c03rad0r/esp32-mesh",
            "esp32-tollgate": "/home/c03rad0r/repos/tollgate-esp32",
            "wisp-esp32": "/home/c03rad0r/wisp-esp32"}


def git(a, cwd):
    return subprocess.run(["git"] + a, cwd=cwd, capture_output=True, text=True).stdout


def body(repo, path, rev):
    d = REPO_DIR.get(repo)
    if d and not path.startswith("/"):
        return git(["show", f"{rev}:{path}"], d).splitlines(), rev
    try:
        with open(path, errors="replace") as f:
            return f.read().splitlines(), "WORKTREE-ASIS"
    except OSError:
        return [], "UNREADABLE"


# resolve the rev each row's text actually appears on (rows carry a canonical rev already)
rows = []
for name in ("rows-kept.tsv", "rows-ambiguous.tsv"):
    p = os.path.join(OUT, name)
    if not os.path.exists(p):
        continue
    for l in open(p):
        f = l.rstrip("\n").split("\t")
        if len(f) >= 7:
            rows.append(f)

# canonical rev per repo = the rev the scanner counted first
CANON = {"esp32-tollgate": "master", "esp32-mesh": "feature/redeem-ecash", "wisp-esp32": "main"}

blocks = 0
with open(os.path.join(OUT, "contexts.txt"), "w") as f:
    for repo, path, line, date, text, cls, why in rows:
        rev = CANON.get(repo, "master")
        ls, used = body(repo, path, rev)
        i = int(line) - 1
        if not (0 <= i < len(ls)) or ls[i] != text:
            cand = [n + 1 for n, b in enumerate(ls) if b == text]
            if cand:
                i = cand[0] - 1
        lo, hi = max(0, i - 3), min(len(ls), i + 4)
        f.write("=" * 96 + "\n")
        f.write(f"[CONTEXT] {cls} | {repo} | {path}:{line} | date={date} | rev_used={used}\n")
        f.write(f"why={why}\n")
        f.write("\n".join(f"    {n+1}|{ls[n]}" for n in range(lo, hi)) + "\n")
        blocks += 1

    # full bodies of step-4 filename keeps
    for l in open(os.path.join(OUT, "nameonly.tsv")):
        p = l.rstrip("\n").split("\t")
        if len(p) < 3:
            continue
        repo, path, rv = p[0], p[1], p[2]
        rev = rv.split("|")[0]
        ls, used = body(repo, path, rev)
        f.write("=" * 96 + "\n")
        f.write(f"[STEP4-FILE-KEEP] {repo} | {path} | revs={rv} | rev_used={used} | "
                f"lines={len(ls)}\n")
        f.write("\n".join(f"    {n+1}|{b}" for n, b in enumerate(ls)) + "\n")
        blocks += 1

print(f"contexts.txt rebuilt: {blocks} blocks")
