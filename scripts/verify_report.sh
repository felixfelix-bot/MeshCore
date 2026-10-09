#!/usr/bin/env bash
# verify_report.sh — ad-hoc fidelity check for this task's deliverable (t_0e98e408).
# NOT a project test suite. Read-only. Asserts the load-bearing claims in REPORT.md
# against the raw/ captures, and that neither script drifts.
#
# Usage: bash scripts/verify_report.sh    (run from anywhere; resolves its own root)
set -u
WT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$WT" || exit 2
fail=0
ck(){ if [ "$2" = "$3" ]; then echo "PASS  $1  ($3)"; else echo "FAIL  $1  expected=[$2] got=[$3]"; fail=$((fail+1)); fi; }
ckge(){ if [ "${3:-x}" -ge "${2}" ] 2>/dev/null; then echo "PASS  $1  ($3 >= $2)"; else echo "FAIL  $1  expected>=$2 got=$3"; fail=$((fail+1)); fi; }

echo "--- 1. script syntax (no bytecode artifacts) ---"
bash -n scripts/attach_probe.sh && echo "PASS  attach_probe.sh: bash -n clean" || { echo "FAIL attach_probe.sh syntax"; fail=$((fail+1)); }
python3 -c "import ast; ast.parse(open('scripts/kanban_evidence.py').read())" && echo "PASS  kanban_evidence.py: parses clean" || { echo "FAIL kanban_evidence.py parse"; fail=$((fail+1)); }

echo "--- 2. raw captures exist and are non-empty ---"
for f in 00-environment 10-serial-devices 11-usb-devices 12-dmesg 20-serial-identity 30-localhost-listeners 40-nmap-lan 50-chamber-software 60-kanban-prior-evidence; do
  if [ -s "raw/$f.txt" ]; then echo "PASS  raw/$f.txt non-empty ($(wc -c < "raw/$f.txt") B)"; else echo "FAIL  raw/$f.txt missing/empty"; fail=$((fail+1)); fi
done

echo "--- 3. report load-bearing claims vs raw ---"
ckge "serial by-id: EM7455 links"                1   "$(grep -c 'Sierra_Wireless_EM7455' raw/10-serial-devices.txt)"
ck   "serial by-id: exactly 3 links"             3   "$(grep -c '^lrwxrwxrwx' raw/10-serial-devices.txt)"
ckge "serial id: EM7455 identity reply"          1   "$(grep -c 'Model: EM7455' raw/20-serial-identity.txt)"
ck   "serial id: EVERY *IDN? probe got empty recv" "$(grep -c 'IDN?' raw/20-serial-identity.txt)" "$(grep -c "IDN?.*recv=b''" raw/20-serial-identity.txt)"
ckge "usb: no usb-serial bridge"                 1   "$(grep -c 'no match' raw/11-usb-devices.txt)"
ck   "nmap: 512 hosts reported"                  512 "$(grep -c 'Nmap scan report' raw/40-nmap-lan.txt)"
ck   "nmap: ZERO open ports"                     0   "$(grep -cE '^[0-9]+/tcp[[:space:]]+open' raw/40-nmap-lan.txt)"
ckge "nmap: scan completed"                      1   "$(grep -c 'Nmap done' raw/40-nmap-lan.txt)"
ckge "sw: pymodbus ABSENT"                       1   "$(grep -c 'pymodbus: ABSENT' raw/50-chamber-software.txt)"
ckge "prior evidence cites t_8d1cf920"           1   "$(grep -c 't_8d1cf920' raw/60-kanban-prior-evidence.txt)"

echo "--- 4. kanban_evidence.py reproduces raw/60 (frozen snapshot) ---"
T="$(mktemp "${TMPDIR:-/tmp}/hermes-verify-60.XXXXXX")"
python3 scripts/kanban_evidence.py "$T" >/dev/null 2>&1
tail -n +2 "$T" > "$T.cmp"; tail -n +2 raw/60-kanban-prior-evidence.txt > "$T.orig"
removed=$(diff "$T.orig" "$T.cmp" | grep -c '^<')
added=$(diff "$T.orig" "$T.cmp" | grep -c '^>')
ck "every snapshot line still reproduced (0 removed/changed)" 0 "$removed"
echo "     (added lines = $added; DB may gain comments after the snapshot)"
rm -f "$T" "$T.cmp" "$T.orig"

echo "--- 5. report states UNVERIFIED for all four setpoints ---"
ckge "REPORT.md has acceptance table"            1   "$(grep -c 'Acceptance table' REPORT.md)"
ck   "REPORT.md: acceptance-table row-start lines = 4" 4 "$(grep -cE '^\| \*\*' REPORT.md)"
ck   "REPORT.md: 4 rows, each UNVERIFIED"        4   "$(grep -cE '^\| \*\*.*UNVERIFIED' REPORT.md)"

echo "--- 6. cleanliness ---"
ck   "working tree clean"                        "" "$(git status --short --untracked-files=all | grep -v '^?? ' || true)"
echo "     (untracked files, if any: $(git status --porcelain | grep -c '^??'))"

echo
if [ $fail -eq 0 ]; then echo "RESULT: ALL CHECKS PASSED"; else echo "RESULT: $fail CHECK(S) FAILED"; fi
exit $fail
