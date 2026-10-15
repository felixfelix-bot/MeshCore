#!/usr/bin/env python3
"""Enumerate hits where the matched term survives removal of the 'tollgate' substring.

That set is the substantive raw-hit list; everything else is project-name noise.
READ-ONLY w.r.t. scanned repos.
"""
import os, re, collections

OUT = "/home/c03rad0r/repos/meshcore-fork-fix/raw/esp32-recon/out"

rows = []
with open(os.path.join(OUT, "raw-hits.tsv")) as f:
    for line in f:
        p = line.rstrip("\n").split("\t")
        if len(p) < 4:
            continue
        rows.append((p[0], p[1], p[2], "\t".join(p[3:])))

substantive = {}
noise = collections.Counter()
for repo, rev, pathline, text in rows:
    path, _, lineno = pathline.rpartition(":")
    stripped = re.sub(r"tollgate", "", text, flags=re.I)
    sub = bool(re.search(r"shadow[\s_-]?card|human[\s_-]?gate", text, re.I))
    has_board = bool(re.search(r"\bboard", stripped, re.I))
    has_gate = bool(re.search(r"\bgate", stripped, re.I))
    key = (repo, path, lineno, text)
    if sub or has_board or has_gate:
        substantive.setdefault(key, set()).add(rev)
    else:
        noise[repo] += 1

with open(os.path.join(OUT, "substantive.tsv"), "w") as f:
    for (repo, path, lineno, text), revs in sorted(substantive.items()):
        f.write("\t".join([repo, path, lineno, "|".join(sorted(revs)[:10]), text]) + "\n")

print(f"substantive unique lines: {len(substantive)}")
print("substring-only noise counts by repo:", dict(noise))
print("--- by repo/path ---")
for (repo, path), n in collections.Counter((k[0], k[1]) for k in substantive).most_common(80):
    print(f"{n:4d}  {repo}  {path}")
