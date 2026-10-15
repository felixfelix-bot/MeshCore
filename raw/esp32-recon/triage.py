#!/usr/bin/env python3
"""Tighter mechanical pass 2 over the esp32-* raw hits.

READ-ONLY w.r.t. scanned repos; writes TSV into the recon worktree only.
Goal: shrink the candidate set to something a human can read line-by-line.
"""
import re, os, collections

OUT = "/home/c03rad0r/repos/meshcore-fork-fix/raw/esp32-recon/out"
RAW = os.path.join(OUT, "raw-hits.tsv")

# ---- KEEP predicates (target concept) ----------------------------------
KEEP_SHADOW = re.compile(r"shadow[\s_-]?card|human[\s_-]?gate|\bhuman-in-the-loop\b", re.I)

KEEP_BOARD_BODY = re.compile(
    r"((approval|review|design[\s-]?review|governance|steering|advisory|oversight|"
    r"change[\s-]?control|safety)\s+board)|"
    r"(board[\s-]?(approval|review|sign[\s-]?off|signoff|decision|quorum|meeting|oversight|"
    r"authoriz|authoris|gate))|"
    r"(board[\s-]level)|"
    r"(\bapprov\w*\s+by\s+the\s+board)|"
    r"(submit\w*\s+to\s+the\s+board)",
    re.I)

KEEP_GATE_MECH = re.compile(
    r"(human[\s-]?gate|\bgate[\s-]?keeper|approval[\s-]?gate|gate[\s-]?review|"
    r"review[\s-]?gate|sign[\s-]?off[\s-]?gate|decision[\s-]?gate|"
    r"gate[\s-]?approval|gate[\s-]?check|gated?\s+(on|behind|by)\s+(human|review|approval|sign)|"
    r"(approval|authoriz\w+|authoris\w+|sign[\s-]?off|signoff|waiver|quorum|"
    r"two[\s-]?person|four[\s-]?eyes|approver)\b.{0,80}\bgate|"
    r"\bgate\b.{0,80}\b(approval|authoriz\w+|authoris\w+|sign[\s-]?off|signoff|waiver|"
    r"quorum|approver|committee|human)|"
    r"\bgating\s+(mechanism|policy|approval|workflow|requirement|criteria|process)|"
    r"(requires?|pending|awaiting|subject\s+to)\s+(human|manual)?\s*"
    r"(approval|authoriz\w+|authoris\w+|sign[\s-]?off|review\s+by))",
    re.I)

# ---- explicit DROP predicates (narrowing) -------------------------------
DROP_HW_BOARD = re.compile(
    r"(flight[\s-]?board|board\s+(rev|revision|bring|layout|design|file|config|variant)|"
    r"bring[\s-]?up|bringup|\bPCB\b|schematic|footprint|kicad|solder|enclosure|\bBOM\b|"
    r"pinout|dev(elopment)?[\s-]?board|devkit|dev[\s-]?kit|daughterboard|breakout|"
    r"breadboard|mainboard|motherboard|on[\s-]?board|off[\s-]?board|\bBoard\s+[A-C]\b|"
    r"\bESP32[\s-]?S3\s+boards?\b|\bper[\s-]?board\b|\bboard\b.{0,30}\b(MAC|GPIO|pin|"
    r"port|flash|UART|USB|ttyACM)\b)",
    re.I)

DROP_HW_GATE = re.compile(
    r"(gate\s+(driver|voltage|charge|resistor|capacitor|current|oxide|threshold|leakage|"
    r"signal|pin|drive)|logic\s+gates?|\b(AND|OR|XOR|NAND|NOR)\s+gate|mosfet|transistor)",
    re.I)

DROP_SUBSTR = re.compile(r"tollgate", re.I)


def classify(text):
    stripped = DROP_SUBSTR.sub("", text)
    has_shadow = bool(KEEP_SHADOW.search(text))
    has_board = bool(re.search(r"\bboard", text, re.I))
    has_gate = bool(re.search(r"\bgate", stripped, re.I))
    if not (has_shadow or has_board or has_gate):
        return "dropped", "substring-only 'tollgate' project name", "none"
    terms = ",".join(t for t, b in (("shadow-card/human-gate", has_shadow),
                                    ("board", has_board), ("gate", has_gate)) if b)
    if has_shadow:
        return "candidate", "shadow-card / human-gate literal", terms
    if has_board and KEEP_BOARD_BODY.search(text):
        return "candidate", "board = approval/review body", terms
    if has_gate and KEEP_GATE_MECH.search(text):
        return "candidate", "gate = approval/gating mechanism wording", terms
    if has_board and DROP_HW_BOARD.search(text):
        return "dropped", "board = firmware/PCB/hardware mention", terms
    if has_gate and DROP_HW_GATE.search(text):
        return "dropped", "gate = electrical/logic gate", terms
    if has_gate:
        return "dropped", "gate = no approval/gating semantics on matched line", terms
    return "dropped", "board = hardware board mention (no approval wording)", terms


NAME_RE = re.compile(r"design[\s-]?review[\s-]?notes|(^|/)ADR[-_/]|\bADR[-_]|decision|\brfc\b", re.I)

rows = []
with open(RAW) as f:
    for line in f:
        p = line.rstrip("\n").split("\t")
        if len(p) < 4:
            continue
        rows.append((p[0], p[1], p[2], "\t".join(p[3:])))

grouped = collections.OrderedDict()
for repo, rev, pathline, text in rows:
    path, _, lineno = pathline.rpartition(":")
    grouped.setdefault((repo, path, lineno, text), []).append(rev)

cand, drop, nameonly = [], [], {}
for (repo, path, lineno, text), revs in grouped.items():
    verdict, rule, terms = classify(text)
    if NAME_RE.search(path):
        nameonly.setdefault((repo, path), set()).update(revs)
        if verdict == "dropped":
            verdict, rule = "candidate", "path matches ADR/decision/rfc (step 4)"
    rec = (repo, path, lineno, verdict, rule, terms, "|".join(sorted(revs)[:8]), text)
    (cand if verdict == "candidate" else drop).append(rec)

with open(os.path.join(OUT, "candidates2.tsv"), "w") as f:
    for r in cand:
        f.write("\t".join(r) + "\n")
with open(os.path.join(OUT, "dropped2.tsv"), "w") as f:
    for r in drop:
        f.write("\t".join(r) + "\n")
with open(os.path.join(OUT, "nameonly2.tsv"), "w") as f:
    for (repo, path), revs in sorted(nameonly.items()):
        f.write("\t".join([repo, path, "|".join(sorted(revs))]) + "\n")

print(f"unique raw lines: {len(grouped)}  candidates: {len(cand)}  dropped: {len(drop)}")
print(f"ADR/decision/rfc-named files touched: {len(nameonly)}")
print("--- candidates by file ---")
for (repo, path), n in collections.Counter((r[0], r[1]) for r in cand).most_common():
    print(f"{n:4d}  {repo}  {path}")
print("--- name-only keeps ---")
for (repo, path) in sorted(nameonly):
    print(f"      {repo}  {path}")
