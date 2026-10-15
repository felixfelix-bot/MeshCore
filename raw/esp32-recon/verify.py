#!/usr/bin/env python3
"""Verify the report's §4 quotes are verbatim at the stated rev:path:line. READ-ONLY."""
import os, subprocess, re

WT = "/home/c03rad0r/repos/meshcore-fork-fix"
OUT = os.path.join(WT, "raw/esp32-recon/out")
REPORT = os.path.join(WT, "raw/esp32-recon/REPORT.md")
REPO_DIR = {"esp32-mesh": "/home/c03rad0r/esp32-mesh",
            "esp32-tollgate": "/home/c03rad0r/repos/tollgate-esp32",
            "wisp-esp32": "/home/c03rad0r/wisp-esp32"}


def git(a, cwd):
    return subprocess.run(["git"] + a, cwd=cwd, capture_output=True, text=True).stdout


rows = []
for name in ("rows-kept.tsv", "rows-ambiguous.tsv"):
    for l in open(os.path.join(OUT, name)):
        f = l.rstrip("\n").split("\t")
        if len(f) >= 7:
            rows.append(f)

ok = bad = 0
problems = []
for repo, path, line, date, text, cls, why in rows:
    rev = "master" if repo == "esp32-tollgate" else ("feature/redeem-ecash" if repo == "esp32-mesh" else "main")
    # find the rev actually used: re-derive by searching all revs for the text
    d = REPO_DIR.get(repo)
    if d:
        found_at = None
        for r in subprocess.run(["git", "-C", d, "for-each-ref", "--format=%(refname:short)",
                                 "refs/heads", "refs/tags", "refs/remotes"],
                                capture_output=True, text=True).stdout.split():
            body = git(["show", f"{r}:{path}"], d) if not path.startswith("/") else ""
            if body and text.strip() in body:
                found_at = r
                break
        if found_at:
            body = git(["show", f"{found_at}:{path}"], d).splitlines()
            n = int(line)
            hit = n - 1 < len(body) and body[n - 1] == text
            if hit:
                ok += 1
            else:
                # locate actual line
                cand = [i + 1 for i, b in enumerate(body) if b == text]
                bad += 1
                problems.append((repo, path, line, "LINE MISMATCH", cand[:3]))
        else:
            bad += 1
            problems.append((repo, path, line, "TEXT NOT FOUND IN ANY REV", None))
    else:
        try:
            body = open(path, errors="replace").read().splitlines()
        except OSError:
            bad += 1
            problems.append((repo, path, line, "FILE UNREADABLE", None))
            continue
        n = int(line)
        if n - 1 < len(body) and body[n - 1] == text:
            ok += 1
        else:
            bad += 1
            problems.append((repo, path, line, "LINE MISMATCH", None))

print(f"rows checked: {len(rows)}  verbatim-at-line OK: {ok}  problems: {bad}")
for p in problems:
    print("  PROBLEM:", p)

# confirm the report table contains each row's quote
rep = open(REPORT).read()
missing = [r for r in rows if r[4].replace("|", "\\|").strip() not in rep]
print(f"rows whose quote is missing from REPORT table: {len(missing)}")
for m in missing[:10]:
    print("  MISSING:", m[0], m[1], m[2])
