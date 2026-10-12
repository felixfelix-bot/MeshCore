#!/usr/bin/env python3
"""Read-only dump of meshcore kanban cards matching chamber/commissioning terms."""
import sqlite3, sys

DB = "/home/c03rad0r/.hermes/kanban/boards/meshcore/kanban.db"
con = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)
con.row_factory = sqlite3.Row
cur = con.cursor()

# discover schema
tabs = [r[0] for r in cur.execute("SELECT name FROM sqlite_master WHERE type='table'")]
print("TABLES:", tabs)
for t in tabs:
    cols = [r[1] for r in cur.execute(f"PRAGMA table_info({t})")]
    print(f"  {t}: {cols}")

terms = ["chamber","commission","ramp","heat","cool","rate","thermal","install",
         "SAT","FAT","IQ/OQ","qualif","nameplate","freezer","cryo","soak","dwell"]
q = " OR ".join([f"lower(coalesce(title,'')) LIKE '%{t.lower()}%'" for t in terms])
q += " OR " + " OR ".join([f"lower(coalesce(body,'')) LIKE '%{t.lower()}%'" for t in terms])

print("\n=== CARDS matching terms ===")
try:
    rows = list(cur.execute(f"SELECT * FROM tasks WHERE {q}"))
except Exception as e:
    print("query error:", e)
    rows = []

for r in rows:
    d = dict(r)
    tid = d.get('id') or d.get('task_id')
    title = d.get('title','')
    status = d.get('status','')
    print(f"\n--- {tid} [{status}] {title}")
    for k in ('assignee','created_at','updated_at'):
        if k in d: print(f"    {k}: {d[k]}")
    res = d.get('result')
    if res:
        print("    RESULT:")
        for line in str(res).splitlines():
            print("      |", line)
print(f"\nTOTAL CARDS MATCHED: {len(rows)}")
