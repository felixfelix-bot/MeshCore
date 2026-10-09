#!/usr/bin/env python3
"""kanban_evidence.py — dump the prior meshcore-board evidence that bears on
task t_0e98e408 (chamber attachment / no-chamber verdicts) as raw citation text.

Read-only. Reproduces raw/60-kanban-prior-evidence.txt.
"""
import sqlite3, sys, os, datetime

DB = "/home/c03rad0r/.hermes/kanban/boards/meshcore/kanban.db"
TASKS = ["t_8d1cf920", "t_135fbd0e", "t_23e2f894", "t_ed6c996b", "t_0e98e408"]

def main(out):
    c = sqlite3.connect(DB)
    with open(out, "w") as f:
        def w(s=""):
            print(s); f.write(s + "\n")
        w(f"# meshcore kanban evidence dump — generated {datetime.datetime.utcnow():%Y-%m-%dT%H:%M:%SZ}")
        w(f"# source DB: {DB} (read-only)")
        for tid in TASKS:
            r = c.execute("select title,status,assignee,result from tasks where id=?",
                          (tid,)).fetchone()
            w("\n" + "=" * 78)
            if not r:
                w(f"{tid}: MISSING"); continue
            title, status, assignee, result = r
            w(f"{tid} | status={status} | assignee={assignee}")
            w(f"title: {title}")
            w(f"result: {result or '<none>'}")
            for i, a, ts, b in c.execute(
                    "select id,author,created_at,body from task_comments "
                    "where task_id=? order by id", (tid,)).fetchall():
                tsu = datetime.datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S")
                w(f"  [comment {i} by {a} @ {tsu}] {(b or '').strip()[:900]}")
    print(f"wrote {out}")

if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "raw/60-kanban-prior-evidence.txt"
    os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
    main(out)
