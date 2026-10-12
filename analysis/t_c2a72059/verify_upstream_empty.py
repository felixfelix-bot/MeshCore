#!/usr/bin/env python3
"""
In-repo verification for t_c2a72059.

Proves the two upstream outputs are EMPTY (not merely unfound): every candidate
upstream task has an empty `result` column, zero `task_attachments` rows, and no
on-disk deliverable. Read-only. Reproducible.

Run:  python3 analysis/t_c2a72059/verify_upstream_empty.py
Test: python3 analysis/t_c2a72059/test_verify_upstream_empty.py
Exit: 0 = upstream confirmed empty (the blocked/negative deliverable is correct)
      1 = upstream output EXISTS (this task should have merged it instead)
"""
import os
import sqlite3
import subprocess
import sys

BOARD_DB = "/home/c03rad0r/.hermes/kanban/boards/meshcore/kanban.db"
ATTACH_DIR = "/home/c03rad0r/.hermes/kanban/boards/meshcore/attachments"

# The two upstream investigations this task consumes, plus their known siblings.
LOGBOOK_TASKS = ["t_43a2de9b", "t_47c20593", "t_c086a169"]
CHAT_TASKS = ["t_edec6674", "t_10fc09c8", "t_88006d69", "t_d4f21d6a", "t_4c2d42fe"]
SUPPORT_TASKS = ["t_f089005b", "t_196899e3", "t_9dc97260"]
ALL_UPSTREAM = LOGBOOK_TASKS + CHAT_TASKS + SUPPORT_TASKS

ARTIFACT_ROOTS = ["/home/c03rad0r/reports", "/home/c03rad0r/scratch"]
ARTIFACT_PATTERNS = [
    "*logbook*", "*slack*custodian*", "*matrix*custodian*",
    "*t_43a2de9b*", "*t_edec6674*",
]

# Comment classes that are status/meta, never a deliverable.
META_COMMENTS = [
    "BLOCKED:%", "fleet-done%", "gate-tick:%", "Decomposed into%",
    "Specified —%", "auto: looped%", "urgency-triage:%",
]


def _in(ids):
    """SQL IN-list literal for a fixed, trusted id set."""
    return ",".join("'%s'" % i for i in ids)


def evaluate(cur, attach_dir=ATTACH_DIR, artifact_roots=ARTIFACT_ROOTS, emit=print):
    """Run all five emptiness checks. Return failure strings; [] means confirmed empty."""
    failures = []

    # -- 1. result column empty. Two SQLite traps guarded here:
    #    * coalesce(result, 0) coerces NULL -> integer 0 -> '0' -> length 1 (false NON-EMPTY).
    #    * bare trim(X) strips SPACE (0x20) only, so a newline/tab result reads NON-EMPTY.
    emit("== 1. upstream result columns must be empty (whitespace-only counts as empty) ==")
    ws = "char(32)||char(9)||char(10)||char(13)"
    rows = cur.execute(
        "SELECT id,status,length(coalesce(result,'')),"
        "length(trim(coalesce(result,''),%s)) FROM tasks WHERE id IN (%s)"
        % (ws, _in(ALL_UPSTREAM))
    ).fetchall()
    seen = {r[0] for r in rows}
    for tid in ALL_UPSTREAM:
        if tid not in seen:
            failures.append("task %s not present in board DB" % tid)
    emit("rows: %d" % len(rows))
    for tid, status, rawlen, trlen in rows:
        ok = trlen == 0
        emit("  %-12s status=%-9s raw_len=%d trim_len=%d  %s"
             % (tid, status, rawlen, trlen, "EMPTY" if ok else "NON-EMPTY"))
        if not ok:
            failures.append("upstream %s has NON-EMPTY result (trim_len=%d)" % (tid, trlen))

    # -- 2. no attachments
    emit("== 2. zero task_attachments for every upstream task ==")
    natt = cur.execute(
        "SELECT count(*) FROM task_attachments WHERE task_id IN (%s)" % _in(ALL_UPSTREAM)
    ).fetchone()[0]
    emit("attachment rows: %d" % natt)
    if natt:
        failures.append("upstream tasks carry %d attachment(s)" % natt)

    # -- 3. no deliverable-bearing comment (output could have been posted as one)
    emit("== 3. zero comments delivering upstream output under those ids ==")
    ncomments = cur.execute(
        "SELECT count(*) FROM task_comments WHERE task_id IN (%s) AND %s"
        % (_in(ALL_UPSTREAM),
           " AND ".join("body NOT LIKE '%s'" % m for m in META_COMMENTS))
    ).fetchone()[0]
    emit("substantive (deliverable-bearing) comments: %d" % ncomments)
    if ncomments:
        failures.append("upstream tasks carry %d deliverable-bearing comment(s)" % ncomments)

    # -- 4. no on-disk attachment dir
    emit("== 4. no on-disk attachment directory for any upstream task ==")
    for tid in ALL_UPSTREAM:
        exists = os.path.isdir(os.path.join(attach_dir, tid))
        emit("  %-12s %s" % (tid, "DIR EXISTS" if exists else "absent"))
        if exists:
            failures.append("attachment dir exists for %s" % tid)

    # -- 5. no on-disk report/raw artifact
    emit("== 5. no on-disk report/raw artifact naming a logbook review or chat search ==")
    hits = []
    for root in artifact_roots:
        if not os.path.isdir(root):
            continue
        for pat in ARTIFACT_PATTERNS:
            try:
                out = subprocess.run(
                    ["find", root, "-maxdepth", "4", "-iname", pat],
                    capture_output=True, text=True, timeout=60,
                ).stdout.strip()
            except Exception as e:  # noqa: BLE001
                emit("  find error %s: %s" % (pat, e))
                continue
            hits += out.splitlines()
    for h in hits:
        emit("  HIT: %s" % h)
    emit("artifact hits: %d" % len(hits))
    if hits:
        failures.append("%d on-disk artifact(s) match the upstream deliverable names" % len(hits))

    return failures


def main():
    con = sqlite3.connect("file:%s?mode=ro" % BOARD_DB, uri=True)
    failures = evaluate(con.cursor())
    print("\n=== RESULT ===")
    if failures:
        print("UPSTREAM NOT EMPTY — this task should have merged the input(s):")
        for f in failures:
            print("  -", f)
        return 1
    print("CONFIRMED: both upstream outputs are empty (no result, no attachment, no artifact).")
    print("The blocked/negative deliverable for t_c2a72059 is correct.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
