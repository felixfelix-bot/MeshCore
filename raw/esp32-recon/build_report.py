#!/usr/bin/env python3
"""Build the raw-hit list deliverable for the esp32-* family shard.

Emits Markdown rows in the required column order:
  path:line | date (source) | VERBATIM quote | classification | talk-vs-mechanism | narrowing note

READ-ONLY w.r.t. scanned repos. Writes only REPORT-esp32-family-raw-hits.md and
out/*.md inside the recon worktree.
"""
import os, re, subprocess, collections

WT = "/home/c03rad0r/repos/meshcore-fork-fix"
OUT = os.path.join(WT, "raw/esp32-recon/out")
REPO_DIR = {
    "esp32-mesh": "/home/c03rad0r/esp32-mesh",
    "esp32-tollgate": "/home/c03rad0r/repos/tollgate-esp32",
    "wisp-esp32": "/home/c03rad0r/wisp-esp32",
}

APPROVAL = re.compile(
    r"(shadow[\s_-]?card|human[\s_-]?gate|approval[\s_-]?gate|gate[\s_-]?(review|check|approval|keeper)|"
    r"sign[\s_-]?off|signoff|four[\s_-]?eyes|two[\s_-]person|change[\s_-]?control|\bapprover|"
    r"\bwaiver\b|\bquorum\b|gatekeeper|gatekeeping|board\s+(approval|review|decision)\b|"
    r"(approval|review|governance|steering|advisory|oversight)\s+board|"
    r"(required|requires|pending|awaiting)\s+(human|manual|board|operator)\s+"
    r"(approval|review|authoriz|authoris|sign))",
    re.I)

# step 4: file-name keeps
NAME_RE = re.compile(r"design[\s-]?review[\s-]?notes|(^|/)ADR[-_/]|\bADR[-_]\d|decision|\brfc\b", re.I)

# borderline: a described GATING MECHANISM (payment/access gating, machine-approval gate)
# that is neither a shadow-card/human-gate nor a hardware board mention.
AMBIG = re.compile(
    r"(payment[\s-]?gat(ed|es)|gat(es|ed|ing)\s+(internet|access|radio|relay|bandwidth|time|"
    r"the\s+(release|decision|merge))|gates\s+decision|nostr[\s-]?gated|"
    r"captive\s+portal\s+that\s+gates|access\s+gating|payment\s+gateway)",
    re.I)


def git(args, cwd):
    return subprocess.run(["git"] + args, cwd=cwd, capture_output=True, text=True).stdout


def date_source(repo, rev, path):
    d = REPO_DIR.get(repo)
    if d:
        out = git(["log", "-1", "--format=%ci", rev, "--", path], d).strip()
        if out:
            return out, f"git log -1 --format=%ci {rev} -- {path}"
        return "NO-GIT-HISTORY-FOR-PATH", f"git log -1 {rev} -- {path} (empty)"
    return "NO-GIT-HISTORY (non-git worktree, current tree)", "doc header / no git history"


def esc(s):
    return s.replace("|", "\\|").strip()


# ---------- load substantive set (real board/gate terms, not 'tollgate' substring) ----------
rows = []
with open(os.path.join(OUT, "substantive.tsv")) as f:
    for line in f:
        p = line.rstrip("\n").split("\t")
        if len(p) < 5:
            continue
        rows.append(dict(repo=p[0], path=p[1], line=p[2], revs=p[3].split("|"), text="\t".join(p[4:])))

# ---------- step-4 filename keeps (whole-file entries) ----------
step4 = []
with open(os.path.join(OUT, "nameonly.tsv")) as f:
    for line in f:
        p = line.rstrip("\n").split("\t")
        if len(p) >= 3:
            step4.append(dict(repo=p[0], path=p[1], revs=p[2].split("|")))

# ---------- disposition ----------
kept, ambig, dropped_hw, dropped_gate, dropped_other = [], [], [], [], []
for r in rows:
    t = r["text"]
    rev = r["revs"][0]
    r["rev"] = rev
    r["date"], r["datesrc"] = date_source(r["repo"], rev, r["path"])
    is_name = bool(NAME_RE.search(r["path"]))
    r["step4"] = is_name
    stripped = re.sub(r"tollgate", "", t, flags=re.I)
    has_board = bool(re.search(r"\bboard", stripped, re.I))
    has_gate = bool(re.search(r"\bgate", stripped, re.I))
    has_appr = bool(APPROVAL.search(t))
    if has_appr:
        r["cls"] = "recreated"
        r["why"] = "matched required regex term with approval/gating-mechanism sense"
        kept.append(r)
    elif AMBIG.search(t):
        r["cls"] = "ambiguous"
        r["why"] = ("names a gating MECHANISM (payment/access gating or machine-approval gate) "
                    "but it is not a human/shadow-card/board gate"
                    + ("; file kept by step 4 filename rule" if is_name else ""))
        ambig.append(r)
    elif has_board:
        r["cls"] = "dropped"
        r["why"] = ("firmware/PCB/hardware 'board' mention (not an approval body); "
                    "file kept by step 4 filename rule" if is_name else
                    "firmware/PCB/hardware 'board' mention (not an approval body)")
        dropped_hw.append(r)
    elif has_gate:
        r["cls"] = "dropped"
        r["why"] = ("'gate' in non-approval sense (payment/access/conditional/boot ordering); "
                    "file kept by step 4 filename rule" if is_name else
                    "'gate' in non-approval sense (payment/access/conditional/boot ordering)")
        dropped_gate.append(r)
    else:
        r["cls"] = "dropped"
        r["why"] = "substring-only 'tollgate' match (project name), no standalone term"
        dropped_other.append(r)

def row_md(r):
    return ("| `{p}:{l}` | {d} ({s}) | \"{q}\" | {c} | talk (planning/design prose; no implemented "
            "gate code cited) | {w} |").format(
        p=esc(r["path"]), l=r["line"], d=r["date"], s=esc(r["datesrc"]),
        q=esc(r["text"]), c=r["cls"], w=esc(r["why"]))


def dump_tsv(name, rs):
    with open(os.path.join(OUT, name), "w") as f:
        for r in rs:
            f.write("\t".join([r["repo"], r["path"], r["line"], r["date"], r["text"],
                               r["cls"], r["why"]]) + "\n")


dump_tsv("rows-kept.tsv", kept)
dump_tsv("rows-ambiguous.tsv", ambig)
dump_tsv("rows-dropped-board.tsv", dropped_hw)
dump_tsv("rows-dropped-gate.tsv", dropped_gate)
dump_tsv("rows-dropped-other.tsv", dropped_other)

# NOTE: no intermediate .md row dumps are written here. An earlier revision emitted
# rows-*.md and the pre-commit secret hook flagged hash-like columns in them
# (false positives on board/tool names). build_md.py renders the report from the .tsv
# artifacts below, so the .md intermediates are unnecessary.

print(f"substantive rows: {len(rows)}")
print(f"KEPT: {len(kept)}   dropped-board: {len(dropped_hw)}   "
      f"dropped-gate: {len(dropped_gate)}   dropped-substr: {len(dropped_other)}")
print("--- KEPT rows ---")
for r in kept:
    print(f"  {r['repo']} {r['path']}:{r['line']} | {r['date']} | {r['text'][:120]}")
