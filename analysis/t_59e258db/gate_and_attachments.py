#!/usr/bin/env python3
"""Read-only: dump the location-gate cards + search ALL board DBs for commissioning docs."""
import sqlite3, glob, os

ids = ["t_a2f7f281","t_b09424f1","t_ffc911f6","t_4d87333a","t_e1408991","t_93217530"]
DB = "/home/c03rad0r/.hermes/kanban/boards/meshcore/kanban.db"
con = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)
con.row_factory = sqlite3.Row
cur = con.cursor()
for tid in ids:
    r = cur.execute("SELECT id,title,status,assignee,result FROM tasks WHERE id=?", (tid,)).fetchone()
    if not r:
        print(f"{tid}: NOT FOUND"); continue
    print(f"\n=== {r['id']} [{r['status']}] {r['title']}")
    print("RESULT:", (r['result'] or "(none)")[:1500])

# cross-board scan of ALL attachments for any doc
print("\n\n=== ALL task_attachments across ALL boards ===")
tot = 0
for db in glob.glob("/home/c03rad0r/.hermes/kanban/boards/*/kanban.db"):
    try:
        c = sqlite3.connect(f"file:{db}?mode=ro", uri=True)
        rows = list(c.execute("SELECT task_id,filename,content_type,size FROM task_attachments"))
        if rows:
            print(f"{os.path.basename(os.path.dirname(db))}: {len(rows)} attachments")
            for x in rows[:20]:
                print("   ", dict(zip(['task_id','filename','content_type','size'], x)))
        tot += len(rows)
        c.close()
    except Exception as e:
        pass
print("TOTAL attachments fleet-wide:", tot)
