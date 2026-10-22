#!/usr/bin/env python3
"""Read-only: search meshcore kanban task_comments + task_events + attachments for
chamber/commissioning/ramp-rate document references."""
import sqlite3, re

DB = "/home/c03rad0r/.hermes/kanban/boards/meshcore/kanban.db"
con = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)
con.row_factory = sqlite3.Row
cur = con.cursor()

pats = [r"commissio", r"install", r"SAT\b", r"FAT\b", r"IQ/?OQ", r"qualif",
        r"nameplate", r"ramp.?rate", r"heating rate", r"cooling rate",
        r"environmental chamber", r"thermal chamber", r"\bchamber\b",
        r"handover", r"OEM", r"vendor portal", r"equipment binder", r"revision"]

def hits(text):
    t = text or ""
    out = []
    for p in pats:
        for m in re.finditer(p, t, re.I):
            s = max(0, m.start()-90); e = min(len(t), m.end()+90)
            out.append(t[s:e].replace("\n"," "))
    return out

print("=== COMMENTS maching document/commissioning terms ===")
seen = 0
for r in cur.execute("SELECT id,task_id,author,body,created_at FROM task_comments"):
    h = hits(r["body"])
    if h:
        seen += 1
        print(f"\n--- comment {r['id']} on {r['task_id']} by {r['author']}")
        # dedupe snippets
        for s in dict.fromkeys(h):
            print("   >", s)
print(f"\nCOMMENTS WITH HITS: {seen}")

print("\n\n=== ATTACHMENTS ===")
for r in cur.execute("SELECT * FROM task_attachments"):
    print(dict(r))
