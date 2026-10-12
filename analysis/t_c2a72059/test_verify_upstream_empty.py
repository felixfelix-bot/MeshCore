#!/usr/bin/env python3
"""
Canonical regression test for verify_upstream_empty.py.

Run: python3 analysis/t_c2a72059/test_verify_upstream_empty.py   (exit 0 = all pass)

The proof script is itself the evidence for the t_c2a72059 blocked deliverable, so
this test asserts it DISCRIMINATES rather than always passing: exit 0 only when the
upstream tasks are genuinely empty, exit 1 when any real upstream output exists.

No third-party deps; no network; builds synthetic board DBs in a tempdir.
"""
import importlib.util
import os
import shutil
import sqlite3
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.path.join(HERE, "verify_upstream_empty.py")

spec = importlib.util.spec_from_file_location("vut", SCRIPT)
assert spec and spec.loader, "cannot load %s" % SCRIPT
vut = importlib.util.module_from_spec(spec)
spec.loader.exec_module(vut)

IDS = vut.ALL_UPSTREAM
assert len(IDS) == 11, IDS

SCHEMA = """
    CREATE TABLE tasks(id TEXT PRIMARY KEY, title TEXT, body TEXT, status TEXT, result TEXT);
    CREATE TABLE task_attachments(id INTEGER PRIMARY KEY, task_id TEXT, filename TEXT,
                                  stored_path TEXT, size INTEGER);
    CREATE TABLE task_comments(id INTEGER PRIMARY KEY, task_id TEXT, author TEXT,
                               body TEXT, created_at INTEGER);
"""


def board(result=None, ws_ids=(), meta_comment=False, deliverable_comment=False):
    """Build a synthetic board carrying all 11 upstream ids. Returns (conn, tmpdir)."""
    d = tempfile.mkdtemp(prefix="hermes-verify-board-")
    con = sqlite3.connect(os.path.join(d, "kanban.db"))
    con.executescript(SCHEMA)
    con.executemany("INSERT INTO tasks VALUES(?,?,'','triage','')",
                    [(t, "title " + t) for t in IDS])
    if result:
        con.execute("UPDATE tasks SET result=? WHERE id=?", (result[1], result[0]))
    for t in ws_ids:
        con.execute("UPDATE tasks SET result=char(10) WHERE id=?", (t,))
    if meta_comment:
        con.execute("INSERT INTO task_comments VALUES(1,?,?,'BLOCKED: fleet-offload',0)",
                    (IDS[0], "manager"))
    if deliverable_comment:
        con.execute("INSERT INTO task_comments VALUES(2,?,?,'Found: logbook p.12 signed by F.',0)",
                    (IDS[0], "worker"))
    con.commit()
    return con, d


# (label, kwargs for board(), expected_exit, why)
CASES = [
    ("all upstream EMPTY", {}, 0, "the shipped deliverable's claim"),
    ("logbook task has a real result",
     {"result": ("t_43a2de9b", "Found: logbook p.12, 2026-09-01, signed by F.")}, 1,
     "genuine upstream output must be flagged"),
    ("chat task has a real result",
     {"result": ("t_edec6674", "#ops 2026-09-02: chamber booked by X")}, 1,
     "genuine upstream output must be flagged"),
    ("newline-only result counts EMPTY", {"ws_ids": ("t_edec6674",)}, 0,
     "regression: bare trim() strips space only"),
    ("tab/space-only result counts EMPTY", {"ws_ids": ("t_c086a169",)}, 0,
     "regression: whitespace-only is empty"),
    ("status meta comment is not a deliverable", {"meta_comment": True}, 0,
     "BLOCKED:/fleet-done must not be read as output"),
    ("deliverable-bearing comment IS flagged", {"deliverable_comment": True}, 1,
     "a real comment deliverable must be flagged"),
]


def main():
    failures = []
    try:
        for label, kwargs, want, why in CASES:
            con, d = board(**kwargs)
            got = 1 if vut.evaluate(con.cursor(), attach_dir="/nonexistent",
                                    artifact_roots=[], emit=lambda *a: None) else 0
            con.close()
            shutil.rmtree(d, ignore_errors=True)
            ok = got == want
            print("%-46s exit=%d want=%d  %s  (%s)"
                  % (label, got, want, "OK" if ok else "FAIL", why))
            if not ok:
                failures.append(label)
    finally:
        # sweep any synthetic board dirs the cases created
        for name in os.listdir(tempfile.gettempdir()):
            if name.startswith("hermes-verify-board-"):
                shutil.rmtree(os.path.join(tempfile.gettempdir(), name), ignore_errors=True)

    # real board, as shipped
    rc = os.system("python3 %s >/dev/null 2>&1" % SCRIPT)
    got = os.waitstatus_to_exitcode(rc)
    ok = got == 0
    print("%-46s exit=%d want=%d  %s  (real meshcore board)"
          % ("real board, script as shipped", got, 0, "OK" if ok else "FAIL"))
    if not ok:
        failures.append("real board")

    print()
    if failures:
        print("FAIL: %d/%d case(s): %s" % (len(failures), len(CASES) + 1, ", ".join(failures)))
        return 1
    print("PASS: %d/%d cases — script discriminates empty vs non-empty upstream"
          % (len(CASES) + 1, len(CASES) + 1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
