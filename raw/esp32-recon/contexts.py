#!/usr/bin/env python3
"""Paragraph + date extraction for pass-2 candidates; READ-ONLY w.r.t. scanned repos."""
import os, subprocess

OUT = "/home/c03rad0r/repos/meshcore-fork-fix/raw/esp32-recon/out"
REPO_DIR = {
    "esp32-mesh": "/home/c03rad0r/esp32-mesh",
    "esp32-tollgate": "/home/c03rad0r/repos/tollgate-esp32",
    "wisp-esp32": "/home/c03rad0r/wisp-esp32",
}


def git(args, cwd):
    return subprocess.run(["git"] + args, cwd=cwd, capture_output=True, text=True).stdout


def body(repo, path, rev):
    d = REPO_DIR.get(repo)
    if d:
        return git(["show", f"{rev}:{path}"], d).splitlines()
    try:
        with open(path, errors="replace") as f:
            return f.read().splitlines()
    except OSError:
        return []


recs = []
with open(os.path.join(OUT, "candidates2.tsv")) as f:
    for ln in f:
        p = ln.rstrip("\n").split("\t")
        recs.append(dict(repo=p[0], path=p[1], line=int(p[2]), rule=p[4], terms=p[5],
                         revs=p[6].split("|"), text="\t".join(p[7:])))

with open(os.path.join(OUT, "contexts2.txt"), "w") as f:
    for r in recs:
        rev = r["revs"][0]
        ls = body(r["repo"], r["path"], rev)
        i = r["line"] - 1
        lo, hi = max(0, i - 3), min(len(ls), i + 4)
        ctx = "\n".join(f"    {n+1}|{ls[n]}" for n in range(lo, hi))
        d = REPO_DIR.get(r["repo"])
        date = ""
        if d:
            date = git(["log", "-1", "--format=%ci", rev, "--", r["path"]], d).strip().splitlines()
            date = date[0] if date else "NO-GIT-HISTORY-FOR-PATH"
        f.write("=" * 96 + "\n")
        f.write(f"{r['repo']} | rev={rev} | {r['path']}:{r['line']} | date={date}\n")
        f.write(f"rule={r['rule']} | terms={r['terms']}\n")
        f.write(f"LINE: {r['text']}\n{ctx}\n")
print("done", len(recs))
