#!/usr/bin/env python3
"""t_afd23162 — S9 kanban DB: full-verbatim export of every audit event on the
calibration-session cards (t_e1408991 + its 4 decomposed children), plus the
per-card counts used for per-source reconciliation. Read-only.

Output goes to raw/09-kanban-db/calibration-session-events.txt (verbatim lines,
stable line ids) — this script reproduces it deterministically."""
import sqlite3, datetime, sys

DB = "/home/c03rad0r/.hermes/kanban/boards/meshcore/kanban.db"
OUT = sys.argv[1] if len(sys.argv) > 1 else "raw/09-kanban-db/calibration-session-events.txt"

CARDS = {
    "t_e1408991": "Bench-calibrate passive_mapper LR2021 thermal model (freezer sweep: k, T0) + die-vs-crystal lag",
    "t_a132b6cd": "Capture raw LR2021 thermal dataset: freezer dwell sweep + ramp telemetry",
    "t_20f98f15": "Fit AT-cut thermal model (k, T0) from freezer-sweep data",
    "t_380a431f": "Characterize die-vs-crystal thermal lag from ramp logs",
    "t_bef90304": "Apply cal blob on module, verify, and record per-module values",
}

def iso(ts):
    return datetime.datetime.fromtimestamp(ts, datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')

con = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)
con.row_factory = sqlite3.Row
cur = con.cursor()

lines = []
lines.append(f"# S9 kanban DB export — calibration-session cards, full verbatim audit trail")
lines.append(f"# DB: {DB} (read-only URI)")
lines.append(f"# generated: {iso(datetime.datetime.now(datetime.timezone.utc).timestamp())} by kanban_session_events.py (deterministic SQL, no edits)")
lines.append(f"# line id convention: TASK_EVENTS.id (ev-N) / TASK_COMMENTS.id (cm-N) — primary keys of the DB tables")
lines.append("")
total_ev = 0
total_cm = 0
for tid, title in CARDS.items():
    t = cur.execute("SELECT id,status,assignee,created_by,created_at,completed_at,block_kind,block_recurrences FROM tasks WHERE id=?", (tid,)).fetchone()
    lines.append(f"===== CARD {tid} [{t['status']}] assignee={t['assignee']} created_by={t['created_by']}")
    lines.append(f"      title: {title}")
    lines.append(f"      created_at: {t['created_at']} ({iso(t['created_at'])})  completed_at: {t['completed_at']}")
    lines.append(f"      block_kind: {t['block_kind']}  block_recurrences: {t['block_recurrences']}")
    ev = list(cur.execute("SELECT id,kind,payload,created_at FROM task_events WHERE task_id=? ORDER BY id", (tid,)))
    nevhb = sum(1 for e in ev if e['kind'] != 'heartbeat')
    lines.append(f"      task_events: {len(ev)} total, {nevhb} non-heartbeat")
    for e in ev:
        lines.append(f"ev-{e['id']}|{tid}|{e['kind']}|created_at={e['created_at']}|{iso(e['created_at'])}|payload={e['payload'] if e['payload'] is not None else ''}")
    cs = list(cur.execute("SELECT id,author,body,created_at FROM task_comments WHERE task_id=? ORDER BY id", (tid,)))
    lines.append(f"      task_comments: {len(cs)}")
    for c in cs:
        body = (c['body'] or '').replace('\n', '\\n')
        lines.append(f"cm-{c['id']}|{tid}|author={c['author']}|created_at={c['created_at']}|{iso(c['created_at'])}|body={body}")
    total_ev += len(ev)
    total_cm += len(cs)
    lines.append("")

lines.append("===== RECONCILIATION COUNTS (source-of-truth = SQL GROUP BY on this DB)")
for tid in CARDS:
    ev = cur.execute("SELECT count(*) FROM task_events WHERE task_id=?", (tid,)).fetchone()[0]
    cs = cur.execute("SELECT count(*) FROM task_comments WHERE task_id=?", (tid,)).fetchone()[0]
    kinds = cur.execute("SELECT kind, count(*) c FROM task_events WHERE task_id=? GROUP BY kind ORDER BY kind", (tid,)).fetchall()
    ks = ";".join(f"{k['kind']}={k['c']}" for k in kinds)
    lines.append(f"RECON|{tid}|events_total={ev}|comments={cs}|{ks}")
lines.append(f"RECON|TOTAL|events_total={total_ev}|comments={total_cm}")

with open(OUT, "w") as f:
    f.write("\n".join(lines) + "\n")
print(f"wrote {OUT}: {len(lines)} lines; events={total_ev}, comments={total_cm}")