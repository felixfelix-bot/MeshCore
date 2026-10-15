#!/usr/bin/env python3
"""Per-rev scan table for the report + explicit zero-hit enumeration."""
import os, subprocess, collections, re

OUT = "/home/c03rad0r/repos/meshcore-fork-fix/raw/esp32-recon/out"
REPO_DIR = {"esp32-mesh": "/home/c03rad0r/esp32-mesh",
            "esp32-tollgate": "/home/c03rad0r/repos/tollgate-esp32",
            "wisp-esp32": "/home/c03rad0r/wisp-esp32"}

cnt = collections.Counter()
sub = collections.Counter()
with open(os.path.join(OUT, "raw-hits.tsv")) as f:
    for line in f:
        p = line.rstrip("\n").split("\t")
        if len(p) < 4:
            continue
        text = "\t".join(p[3:])
        cnt[(p[0], p[1])] += 1
        st = re.sub(r"tollgate", "", text, flags=re.I)
        if re.search(r"shadow[\s_-]?card|human[\s_-]?gate|\bboard|\bgate", st, re.I):
            sub[(p[0], p[1])] += 1

with open(os.path.join(OUT, "revs.tsv"), "w") as f:
    f.write("repo\trev\traw_match_lines\tlines_without_tollgate_substring\n")
    for (repo, rev), n in sorted(cnt.items()):
        f.write(f"{repo}\t{rev}\t{n}\t{sub[(repo, rev)]}\n")

# enumerate every rev in each git root, using the SAME rev strings the scanner used
# (refs/heads/X -> X, refs/tags/X -> X, refs/remotes/X -> remotes/X), so zero-hit revs show up
# and counts line up with raw-hits.tsv keys.
def rev_strings(d):
    full = subprocess.run(["git", "-C", d, "for-each-ref", "--format=%(refname)",
                           "refs/heads", "refs/tags", "refs/remotes"],
                          capture_output=True, text=True).stdout.split()
    out = []
    for r in full:
        if r.endswith("/HEAD"):
            continue
        if r.startswith("refs/remotes/"):
            out.append("remotes/" + r[len("refs/remotes/"):])
        elif r.startswith("refs/heads/") or r.startswith("refs/tags/"):
            out.append(r.split("/", 2)[2])
    return out


planned = {label: rev_strings(d) for label, d in REPO_DIR.items()}

# scanner rev strings were given to `git grep` unqualified, so they may be aliases of the
# canonical ref names above. Match by resolved commit SHA, not by string.
sha_of_scanned = collections.defaultdict(dict)      # label -> sha -> scanned rev string
for (repo, rev) in cnt:
    d = REPO_DIR.get(repo)
    if not d:
        continue
    sha = subprocess.run(["git", "-C", d, "rev-parse", "--verify", f"{rev}^{{commit}}"],
                         capture_output=True, text=True).stdout.strip()
    if sha:
        sha_of_scanned[repo].setdefault(sha, rev)

with open(os.path.join(OUT, "revs.tsv"), "w") as f:
    f.write("repo\trev\traw_match_lines\tlines_without_tollgate_substring\tcount_source_rev\n")
    for label, revs in planned.items():
        d = REPO_DIR[label]
        for rev in revs:
            sha = subprocess.run(["git", "-C", d, "rev-parse", "--verify",
                                  f"refs/remotes/{rev[len('remotes/'):]}" if rev.startswith("remotes/")
                                  else f"refs/heads/{rev}"],
                                 capture_output=True, text=True).stdout.strip()
            if not sha:
                sha = subprocess.run(["git", "-C", d, "rev-parse", "--verify", f"refs/tags/{rev}"],
                                     capture_output=True, text=True).stdout.strip()
            src = sha_of_scanned.get(label, {}).get(sha, rev)
            f.write(f"{label}\t{rev}\t{cnt[(label, src)]}\t{sub[(label, src)]}\t{src}\n")

print("REPO / REV / raw_match_lines / substantive(excl. tollgate substring)")
zero = []
for label, revs in planned.items():
    for rev in revs:
        n = cnt[(label, rev)]
        s = sub[(label, rev)]
        print(f"{label:16s} {rev:55s} {n:6d} {s:6d}")
        if n == 0:
            zero.append((label, rev))
print("\nZERO-HIT (git) revs:")
for label, rev in zero:
    print(f"  {label} {rev}")
