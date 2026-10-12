#!/usr/bin/env python3
"""Read-only: dump full card bodies/results/comments for the specific chamber-doc cards."""
import sqlite3, json

DB = "/home/c03rad0r/.hermes/kanban/boards/meshcore/kanban.db"
con = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)
con.row_factory = sqlite3.Row
cur = con.cursor()

ids = ["t_c65abacb","t_f00a0085","t_f39c2c17","t_0e98e408","t_23e2f894","t_ed6c996b",
       "t_135fbd0e","t_8e264236","t_fbfead68","t_4e41856d","t_5a61e979","t_59e258db",
       "t_42dadf86","t_80950496","t_59e80a86"]

for tid in ids:
    r = cur.execute("SELECT * FROM tasks WHERE id=?", (tid,)).fetchone()
    print("="*100)
    if not r:
        print(f"{tid}: NOT FOUND in DB")
        continue
    d = dict(r)
    print(f"ID: {tid}  STATUS: {d['status']}  assignee: {d['assignee']}")
    print(f"TITLE: {d['title']}")
    print(f"created_by: {d['created_by']}  created_at: {d['created_at']}  completed_at: {d['completed_at']}")
    print(f"branch: {d['branch_name']}  workspace: {d['workspace_path']}")
    print("BODY:")
    print(d.get('body') or "(none)")
    print("RESULT:")
    print(d.get('result') or "(none)")
    # parent/child links
    parents = [x[0] for x in cur.execute("SELECT parent_id FROM task_links WHERE child_id=?", (tid,))]
    children = [x[0] for x in cur.execute("SELECT child_id FROM task_links WHERE parent_id=?", (tid,))]
    print(f"PARENTS: {parents}")
    print(f"CHILDREN: {children}")
    cs = list(cur.execute("SELECT id,author,body FROM task_comments WHERE task_id=? ORDER BY id", (tid,)))
    print(f"COMMENTS: {len(cs)}")
    for c in cs:
        print(f"  -- comment {c['id']} by {c['author']}:")
        print("     " + (c['body'] or '').replace("\n","\n     "))
