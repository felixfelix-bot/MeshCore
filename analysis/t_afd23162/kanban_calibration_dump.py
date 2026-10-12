#!/usr/bin/env python3
"""t_afd23162 — read-only kanban DB probes for calibration-slot evidence.
Reuses the access-map (t_ea0d0e46) source list S1..S12+S2b+S9b.
Prints verbatim rows with stable line ids for the raw/ exports."""
import sqlite3, sys, os

DB = "/home/c03rad0r/.hermes/kanban/boards/meshcore/kanban.db"

def probe_kanban_calibration():
    con = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    # every task title/body mentioning calibration (the fleet's own scheduling surface)
    rows = list(cur.execute(
        "SELECT id,status,assignee,created_by,title FROM tasks "
        "WHERE lower(coalesce(title,'')) LIKE '%calib%' OR lower(coalesce(body,'')) LIKE '%calib%'"))
    print(f"### tasks mentioning calibration: {len(rows)}")
    for r in rows:
        print(f"KAL|{r['id']}|status={r['status']}|assignee={r['assignee']}|created_by={r['created_by']}|title={r['title']}")
    # events touching those tasks (the kanban DB's own audit trail)
    ids = [r['id'] for r in rows]
    if ids:
        qm = ",".join("?" * len(ids))
        ev = list(cur.execute(f"SELECT id,task_id,kind,payload,created_at FROM task_events WHERE task_id IN ({qm}) ORDER BY id", ids))
        print(f"### task_events on calibration tasks: {len(ev)}")
        for e in ev:
            print(f"KEV|{e['id']}|{e['task_id']}|{e['kind']}|at={e['created_at']}|payload={(e['payload'] or '')[:160]}")
    # comments on calibration tasks
    if ids:
        qm = ",".join("?" * len(ids))
        cs = list(cur.execute(f"SELECT id,task_id,author,body,created_at FROM task_comments WHERE task_id IN ({qm}) ORDER BY id", ids))
        print(f"### comments on calibration tasks: {len(cs)}")
        for c in cs:
            b = (c['body'] or '').replace("\n", " ")
            print(f"KCM|{c['id']}|{c['task_id']}|{c['author']}|at={c['created_at']}|{b[:180]}")

if __name__ == "__main__":
    probe_kanban_calibration()