#!/usr/bin/env python3
"""
In-repo verification for t_c2a72059.

Proves the two upstream outputs are EMPTY (not merely unfound): every candidate
upstream task has an empty `result` column, zero `task_attachments` rows, and no
on-disk deliverable. Read-only. Reproducible.

Run:  python3 analysis/t_c2a72059/verify_upstream_empty.py
Exit: 0 = upstream confirmed empty (the blocked/negative deliverable is correct)
      1 = upstream output EXISTS (this task should have merged it instead)
"""
import os
import sqlite3
import sys
import subprocess

BOARD_DB = "/home/c03rad0r/.hermes/kanban/boards/meshcore/kanban.db"
ATTACH_DIR = "/home/c03rad0r/.hermes/kanban/boards/meshcore/attachments"

# The two upstream investigations this task consumes, plus their known siblings.
LOGBOOK_TASKS = ["t_43a2de9b", "t_47c20593", "t_c086a169"]
CHAT_TASKS = ["t_edec6674", "t_10fc09c8", "t_88006d69", "t_d4f21d6a", "t_4c2d42fe"]
SUPPORT_TASKS = ["t_f089005b", "t_196899e3", "t_9dc97260"]
ALL_UPSTREAM = LOGBOOK_TASKS + CHAT_TASKS + SUPPORT_TASKS

failures = []


def sec(t):
    print("\n== %s ==" % t)


# 1. DB reachable + read-only
con = sqlite3.connect("file:%s?mode=ro" % BOARD_DB, uri=True)
cur = con.cursor()

sec("1. upstream result columns must be empty (whitespace-only counts as empty)")
# NOTE: on this board some rows carry a single newline/space in `result`; that is
# semantically empty. Compare the STRIPPED value, and report the raw length too so
# the distinction is visible rather than hidden.
rows = cur.execute(
    "SELECT id,status,length(coalesce(result,'')),"
    "length(trim(coalesce(result,''))) FROM tasks WHERE id IN (%s)"
    % ",".join("'%s'" % i for i in ALL_UPSTREAM)
).fetchall()
seen = {r[0] for r in rows}
for tid in ALL_UPSTREAM:
    if tid not in seen:
        failures.append("task %s not present in board DB" % tid)
print("rows:", len(rows))
for tid, status, rawlen, trlen in rows:
    ok = (trlen == 0)
    print("  %-12s status=%-9s raw_len=%d trim_len=%d  %s"
          % (tid, status, rawlen, trlen, "EMPTY" if ok else "NON-EMPTY"))
    if not ok:
        failures.append("upstream %s has NON-EMPTY result (trim_len=%d)" % (tid, trlen))

sec("2. zero task_attachments for every upstream task")
natt = cur.execute(
    "SELECT count(*) FROM task_attachments WHERE task_id IN (%s)"
    % ",".join("'%s'" % i for i in ALL_UPSTREAM)
).fetchone()[0]
print("attachment rows:", natt)
if natt != 0:
    failures.append("upstream tasks carry %d attachment(s)" % natt)

sec("3. zero comments delivering upstream output under those ids")
# Upstream output *could* have been posted as a comment instead of the result column.
# Exclude every observed status/meta comment class; anything left would be a real
# deliverable and must be reported.
ncomments = cur.execute(
    "SELECT count(*) FROM task_comments WHERE task_id IN (%s) "
    "AND body NOT LIKE 'BLOCKED:%%' AND body NOT LIKE 'fleet-done%%' "
    "AND body NOT LIKE 'gate-tick:%%' AND body NOT LIKE 'Decomposed into%%' "
    "AND body NOT LIKE 'Specified —%%' "
    "AND body NOT LIKE 'auto: looped%%' "
    "AND body NOT LIKE 'urgency-triage:%%'"
    % ",".join("'%s'" % i for i in ALL_UPSTREAM)
).fetchone()[0]
print("substantive (deliverable-bearing) comments:", ncomments)
if ncomments != 0:
    failures.append("upstream tasks carry %d deliverable-bearing comment(s)" % ncomments)

sec("4. no on-disk attachment directory for any upstream task")
for tid in ALL_UPSTREAM:
    p = os.path.join(ATTACH_DIR, tid)
    exists = os.path.isdir(p)
    print("  %-12s %s" % (tid, "DIR EXISTS" if exists else "absent"))
    if exists:
        failures.append("attachment dir exists for %s" % tid)

sec("5. no on-disk report/raw artifact naming a logbook review or chat search")
search_roots = ["/home/c03rad0r/reports", "/home/c03rad0r/scratch"]
patterns = [
    "*logbook*", "*slack*custodian*", "*matrix*custodian*",
    "*t_43a2de9b*", "*t_edec6674*",
]
hits = []
for root in search_roots:
    if not os.path.isdir(root):
        continue
    for pat in patterns:
        try:
            out = subprocess.run(
                ["find", root, "-maxdepth", "4", "-iname", pat],
                capture_output=True, text=True, timeout=60,
            ).stdout.strip()
        except Exception as e:  # noqa: BLE001
            out = ""
            print("  find error %s: %s" % (pat, e))
        for line in out.splitlines():
            hits.append(line)
for h in hits:
    print("  HIT:", h)
print("artifact hits:", len(hits))
if hits:
    failures.append("%d on-disk artifact(s) match the upstream deliverable names" % len(hits))

print("\n=== RESULT ===")
if failures:
    print("UPSTREAM NOT EMPTY — this task should have merged the input(s):")
    for f in failures:
        print("  -", f)
    sys.exit(1)
print("CONFIRMED: both upstream outputs are empty (no result, no attachment, no artifact).")
print("The blocked/negative deliverable for t_c2a72059 is correct.")
sys.exit(0)
