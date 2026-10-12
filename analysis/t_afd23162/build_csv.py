#!/usr/bin/env python3
"""t_afd23162 — build records/calibration_slots.csv from the captured raw exports.

Row policy (per task rules):
- One row per create / edit / reschedule / delete / approve/complete event on a
  calibration slot, with: slot identifier (instrument/asset, scheduled window,
  assignee/owner), editor account, UTC datetime (original timezone noted),
  action type, and a VERBATIM audit-log line + raw file path + line id.
- Distinction enforced: only SCHEDULING/EDIT events on the calibration session
  cards land here. The resulting certificate/data record (bench/RESULTS.md
  per-module cal row) is noted separately, never as a slot event.
- The kanban DB is the only source with an audit log over the calibration
  session. Every other mapped source gets an explicit NO AUDIT LOG row with the
  reason (read the raw/<source>/METHOD.md for the full evidence).
- fleet-done writeback comments are downstream records of status EDITS: each
  lands as an 'approve/complete (writeback)' row AND, where the owning
  task_events row is absent, in the gaps note.
"""
import csv, datetime, os, sqlite3

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))          # repo root
RAW9 = os.path.join(ROOT, "raw", "09-kanban-db")
OUT = os.path.join(ROOT, "records", "calibration_slots.csv")
os.makedirs(os.path.dirname(OUT), exist_ok=True)

EVFILE = os.path.join(RAW9, "calibration-session-events.txt")
RUNFILE = os.path.join(RAW9, "calibration-session-runs.txt")

def load(path, prefix):
    m = {}
    for l in open(path):
        l = l.rstrip("\n")
        if l.startswith(prefix):
            m[l.split("|", 2)[0]] = l
    return m

ev_lines = load(EVFILE, "ev-")
cm_lines = load(EVFILE, "cm-")
run_lines = load(RUNFILE, "run-")

def iso(ts):
    return datetime.datetime.fromtimestamp(ts, datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ") + " (unix epoch, stored UTC; source stores no local offset)"

CARDS = {
    # id: (instrument/asset, scheduled window, assignee/owner)
    "t_e1408991": ("NiceRF LR2021 module (SkyMapper Board A / spare) — passive_mapper thermal calibration",
                   "one operator bench session (~2-3 h) at +40/+25/0/-20/-40/-55 C (freezer sweep), never executed; runbook /home/c03rad0r/t_e1408991-bench-runbook.md",
                   "assignee manager; operator Felix (c03rad0r)"),
    "t_a132b6cd": ("NiceRF LR2021 module — raw thermal dataset capture (freezer dwell sweep + ramp telemetry)",
                   "session step 1 of the t_e1408991 calibration session (data capture leg)",
                   "assignee manager; operator Felix (c03rad0r)"),
    "t_20f98f15": ("NiceRF LR2021 module — AT-cut model fit (k, T0) from sweep data",
                   "session step 2 of the t_e1408991 calibration session (fit leg)",
                   "assignee manager; operator Felix (c03rad0r)"),
    "t_380a431f": ("NiceRF LR2021 module — die-vs-crystal thermal lag characterization",
                   "session step 3 of the t_e1408991 calibration session (lag leg)",
                   "assignee manager; operator Felix (c03rad0r)"),
    "t_bef90304": ("NiceRF LR2021 module — apply cal blob, verify, record per-module values",
                   "session step 4 of the t_e1408991 calibration session (apply/record leg)",
                   "assignee esp32-balloon-integration-hardware-flight; operator Felix (c03rad0r)"),
}

# editor account resolution for events: kanban task_events have no author column;
# the acting account is the dispatch/automation layer of the profile named in the
# payload (lock owner / run profile) or, for comments, task_comments.author.
# For 'specified'/'decomposed' events the author is in the payload or is auto-decomposer.
def editor_for(ev):
    p = ev["payload"] or ""
    if '"by": "auto-decomposer"' in p:
        return "auto-decomposer (kanban automation)"
    if '"author":' in p:
        import json
        try:
            return json.loads(p).get("author", "unknown")
        except Exception:
            pass
    return None  # resolved per-kind below

KIND_ACTION = {
    "created":             "create",
    "specified":           "edit (title/body fields changed)",
    "promoted":            "edit (status transition todo->ready)",
    "claimed":             "edit (session claimed/locked for a run)",
    "spawned":             "edit (worker process spawned on the session card)",
    "reclaimed":           "edit (run reclaimed, lock released)",
    "timed_out":           "reschedule (run budget exhausted, card returned to ready for re-dispatch)",
    "gave_up":             "reschedule (dispatcher gave up after limit; card returned to ready)",
    "blocked":             "reschedule (session parked: window requires operator action)",
    "unblocked":           "reschedule (park cleared — circuit-breaker/provider recovery)",
    "block_loop_detected": "reschedule (block-loop guard tripped: card parked after repeated block)",
    "decomposed":          "edit (session split into child session-step cards)",
    "linked":              "edit (parent/child dependency link added)",
    "commented":           "comment (scheduling discussion / decision, not a state edit)",
    "heartbeat":           None,  # excluded: run liveness, not a slot edit
}

# Events that are EDIT/SCHEDULING actions on the slot -> CSV rows.
# 'commented' events are captured as rows only when they carry a scheduling
# decision or writeback (approved via author + content); we include ALL
# comments because the task asks for the full audit/edit timeline, with the
# verbatim line allowing the reader to see the kind.
rows = []
gaps = []

con = sqlite3.connect("file:/home/c03rad0r/.hermes/kanban/boards/meshcore/kanban.db?mode=ro", uri=True)
con.row_factory = sqlite3.Row
cur = con.cursor()

for tid, (asset, window, owner) in CARDS.items():
    t = cur.execute("SELECT assignee, created_by FROM tasks WHERE id=?", (tid,)).fetchone()
    evs = list(cur.execute("SELECT id, kind, payload, created_at FROM task_events WHERE task_id=? ORDER BY id", (tid,)))
    for e in evs:
        kind = e["kind"]
        if kind == "heartbeat":
            continue  # run-liveness telemetry, not a slot edit
        action = KIND_ACTION.get(kind, kind)
        key = f"ev-{e['id']}"
        raw_line = ev_lines.get(key, "")
        assert raw_line, f"missing raw line {key}"
        ed = editor_for(e)
        if ed is None:
            # claim lock names the host profile: CobradorWave:<pid> => dispatcher on host
            p = e["payload"] or ""
            if '"lock"' in p or '"pid"' in p:
                ed = "hermes kanban dispatcher (CobridorWave host, run payload carries lock/pid)"
            elif kind in ("blocked",):
                ed = "manager (hermes kanban automation)"
            elif kind in ("unblocked",):
                ed = "provider-exhaustion-recovery cron (manager automation)"
            elif kind in ("promoted", "linked", "decomposed"):
                ed = "kanban core (automation)"
            else:
                ed = "kanban automation (no author column on task_events)"
        rows.append({
            "slot_identifier": f"{tid}: {asset}",
            "scheduled_window": window,
            "assignee_owner": owner,
            "editor_account": ed,
            "utc_datetime": iso(e["created_at"]),
            "action_type": action,
            "verbatim_ref": f"raw/09-kanban-db/calibration-session-events.txt :: {key} :: {raw_line}",
        })

    cms = list(cur.execute("SELECT id, author, body, created_at FROM task_comments WHERE task_id=? ORDER BY id", (tid,)))
    for c in cms:
        key = f"cm-{c['id']}"
        raw_line = cm_lines.get(key, "")
        assert raw_line, f"missing raw line {key}"
        body = c["body"] or ""
        if c["author"] == "fleet-writeback":
            action = "approve/complete (fleet writeback claims a status edit)"
        elif body.startswith("BLOCKED:"):
            action = "reschedule (operator-gate block recorded in comment)"
        elif body.startswith("UNBLOCK:"):
            action = "reschedule (park cleared in comment)"
        elif body.startswith("Decomposed into"):
            action = "edit (session split recorded in comment)"
        elif body.startswith("Specified"):
            action = "edit (title/body update recorded in comment)"
        elif body.startswith("gate-tick:"):
            action = "edit (gate-tick advisory/blocked notice)"
        else:
            action = "comment (scheduling decision/discussion)"
        rows.append({
            "slot_identifier": f"{tid}: {asset}",
            "scheduled_window": window,
            "assignee_owner": owner,
            "editor_account": c["author"],
            "utc_datetime": iso(c["created_at"]),
            "action_type": action,
            "verbatim_ref": f"raw/09-kanban-db/calibration-session-events.txt :: {key} :: {raw_line}",
        })

    runs = list(cur.execute("SELECT id, profile, status, outcome, started_at, ended_at, summary, claim_lock FROM task_runs WHERE task_id=? ORDER BY id", (tid,)))
    for r in runs:
        key = f"run-{r['id']}"
        raw_line = run_lines.get(key, "")
        assert raw_line, f"missing raw line {key}"
        rows.append({
            "slot_identifier": f"{tid}: {asset}",
            "scheduled_window": window,
            "assignee_owner": owner,
            "editor_account": f"worker profile {r['profile']} (run {r['id']}, claim {r['claim_lock']})",
            "utc_datetime": iso(r["started_at"]),
            "action_type": f"edit (run attempt on session card: status={r['status']}, outcome={r['outcome']})",
            "verbatim_ref": f"raw/09-kanban-db/calibration-session-runs.txt :: {key} :: {raw_line}",
        })

# GAP detection: fleet-writeback comments claim status edits; the owning
# task_events 'completed' row must exist for a done-writeback, else it's a
# downstream record with no owning audit entry.
for tid in CARDS:
    has_done_event = cur.execute("SELECT count(*) FROM task_events WHERE task_id=? AND kind='completed'", (tid,)).fetchone()[0]
    t = cur.execute("SELECT status, completed_at FROM tasks WHERE id=?", (tid,)).fetchone()
    wb_done = list(cur.execute("SELECT id, body, created_at FROM task_comments WHERE task_id=? AND author='fleet-writeback' AND body LIKE '%status -> done%'", (tid,)))
    for w in wb_done:
        if has_done_event == 0 and t["status"] != "done":
            gaps.append(f"{tid}: comment cm-{w['id']} ({w['body']}) claims 'status -> done' but NO 'completed' task_event exists and the card is now '{t['status']}' with completed_at={t['completed_at']} — the done transition exists only as this downstream writeback record, with no owning audit entry in task_events.")
        elif has_done_event == 0:
            gaps.append(f"{tid}: comment cm-{w['id']} ({w['body']}) claims 'status -> done'; card status is '{t['status']}' but NO 'completed' task_event exists in the audit log (status field edited without an audit event).")

# sort by time
def ts_of(ref):
    import re as _re
    m = _re.search(r"\|(\d{10})\|", ref)
    return int(m.group(1)) if m else 0
rows.sort(key=lambda r: ts_of(r["verbatim_ref"]))

FIELDS = ["slot_identifier", "scheduled_window", "assignee_owner", "editor_account", "utc_datetime", "action_type", "verbatim_ref"]
with open(OUT, "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=FIELDS)
    w.writeheader()
    w.writerows(rows)

with open(os.path.join(ROOT, "records", "calibration_slots_gaps.md"), "w") as f:
    f.write("# Gaps note — calibration slot edits with no owning audit entry\n\n")
    f.write("Rule: list any slot edits that appear only in a downstream record with no owning\n")
    f.write("audit entry. Scanned: all fleet-writeback comments claiming status edits on the\n")
    f.write("five calibration-session cards vs the task_events audit log.\n\n")
    if gaps:
        for g in gaps:
            f.write(f"- {g}\n")
    else:
        f.write("- none\n")
    f.write("\nAdditional downstream-only records noted (not slot edits):\n")
    f.write("- Certificate/data record: examples/passive_mapper/bench/RESULTS.md is the\n")
    f.write("  per-module calibration RESULT table (module id, k, T0, span, residual, tau, blob hex).\n")
    f.write("  As of this extraction it contains an EMPTY row header only — no certificate data\n")
    f.write("  has ever been recorded, because the calibration session itself never ran\n")
    f.write("  (t_e1408991 blocked on operator bench action since 2026-09-11).\n")
    f.write("  Verbatim: raw/08-fork-results-md/RESULTS.md\n")

print(f"rows: {len(rows)}; gaps: {len(gaps)}")
for g in gaps:
    print("GAP:", g)