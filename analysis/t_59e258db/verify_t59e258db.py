#!/usr/bin/env python3
"""Ad-hoc verification for t_59e258db deliverables (no canonical suite exists).

Asserts the REPORT's load-bearing claims against live, re-run evidence:
  1. the 5 analysis/ scripts parse clean and re-run without error (read-only)
  2. card_dump.txt contains the decisive NOT-FOUND quotes verbatim
  3. the exact-duplicate card t_c65abacb exists with no result
  4. the raw evidence file lines 35-36,42-43,54 match Q2/Q1/Q3 verbatim
  5. scrub check: no heating/cooling RATE value is asserted anywhere in the report
     (i.e. the report claims a negative, and does not smuggle in a number)
Not a green suite: it proves the report matches its own cited sources.
"""
import re, subprocess, sys, pathlib

REPO = pathlib.Path("/home/c03rad0r/repos/meshcore-fork-fix")
A = REPO / "analysis/t_59e258db"
REPORT = (REPO / "REPORT-t_59e258db.md").read_text()
RAW = pathlib.Path("/home/c03rad0r/reports/chamber-holds-t_0e98e408-2026-10-09/raw/60-kanban-prior-evidence.txt").read_text().splitlines()

fails, n = [], 0
def check(name, cond):
    global n
    n += 1
    print(("PASS " if cond else "FAIL ") + name)
    if not cond: fails.append(name)

# 1. scripts parse clean + re-run read-only without error
scripts = ["kanban_chamber_dump.py","kanban_comments_search.py","kanban_card_dump.py","gate_and_attachments.py"]
for s in scripts:
    p = A / s
    r = subprocess.run([sys.executable, "-c", f"import ast;ast.parse(open('{p}').read())"],
                       capture_output=True, text=True)
    check(f"{s} parses (ast)", r.returncode == 0)
    r = subprocess.run([sys.executable, str(p)], capture_output=True, text=True)
    check(f"{s} re-runs rc=0", r.returncode == 0)
    check(f"{s} produced output", len(r.stdout) > 0)

# 1b. bash sweep script parses
r = subprocess.run(["bash","-n",str(A/"pdf_sweep.sh")], capture_output=True, text=True)
check("pdf_sweep.sh passes bash -n", r.returncode == 0)

# 2. decisive NOT-FOUND quotes present verbatim in card_dump.txt
dump = (A / "card_dump.txt").read_text()
check("card_dump has Q1 commissioning-records NOT EXISTS",
      "Installation/commissioning records - NOT EXISTS (grep 'commissioning' = 0 hits; only software" in dump)
check("card_dump has equipment-binder NOT EXISTS",
      "Equipment binder - NOT EXISTS (keyword document scan" in dump)
check("card_dump has rate-spec NOT FOUND line",
      "rate-spec text (degC/min, heating/cooling, ramp, slew, pull-down, heat-up): NOT FOUND" in dump)
check("card_dump has t_c65abacb title",
      "Search install/commissioning report for chamber ramp-rate specs" in dump)
check("card_dump shows t_c65abacb result (none)",
      "ID: t_c65abacb" in dump and "(none)" in dump)

# 3. raw evidence line numbers cited in the report match verbatim
check("raw:42-43 == Q1", RAW[41].startswith("6. Installation/commissioning records - NOT EXISTS")
      and "installers on host). NOT FOUND." in RAW[42])
check("raw:35-36 == Q2", RAW[34].startswith("3. Equipment binder - NOT EXISTS")
      and "0 candidate documents). NOT FOUND." in RAW[35])
check("raw:54 == Q3", RAW[53] == "- rate-spec text (degC/min, heating/cooling, ramp, slew, pull-down, heat-up): NOT FOUND")

# 4. report structure: the 5 quotes + NOT FOUND list + negative verdict
check("report states negative finding", "negative finding" in REPORT.lower())
for q in ["Q1","Q2","Q3","Q4","Q5"]:
    check(f"report contains quote block {q} —", q + " —" in REPORT or f"{q} (" in REPORT)
check("report has 9-entry NOT FOUND list", REPORT.count("NOT FOUND —") >= 9)

# 5. scrub: no *rate value* asserted (a negative report must not carry a fabricated number)
# a rate value would look like a number followed by a temp-unit-per-time token, e.g. "3 degC/min"
rate_pat = re.compile(r"\d+(?:\.\d+)?\s*(?:degC|deg C|°C|K)/\s*(?:min|hour|h)\b", re.I)
hits = rate_pat.findall(REPORT)
check("report asserts no heating/cooling rate VALUE", not hits)

print(f"\n{n} assertions, {len(fails)} failed")
if fails:
    print("FAILED:", *fails, sep="\n  ")
    sys.exit(1)
print("AD-HOC VERIFICATION PASSED (not a canonical suite)")
