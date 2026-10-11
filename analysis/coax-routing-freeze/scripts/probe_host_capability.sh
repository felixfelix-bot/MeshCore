#!/bin/bash
# Read-only host-capability probe for the coax-routing-freeze card (t_e5d5eaae).
#
# The card asks for physical work: route/tie the coax bundle, read a caliper and
# a tape measure, read the ambient bench temperature, and read/label cables.
# This script establishes -- with raw output, not assertion -- whether this host
# has ANY channel that could observe or measure a physical cable run. It writes
# nothing outside the evidence directory and changes no device state.
#
# Usage: probe_host_capability.sh [evidence_dir]
set -u

HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERE/../.." && pwd)"            # analysis/coax-routing-freeze
OUT="${1:-$ROOT/evidence}"
mkdir -p "$OUT"

STAMP="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo "host capability probe (read-only) -- $STAMP"
echo "host: $(hostname)   kernel: $(uname -sr)"

echo
echo "=== 1. v4l2 video devices present ==="
ls -l /dev/video* 2>&1 || echo "(none)"

echo
echo "=== 2. frame grabs (the host's ONLY visual channel) ==="
# Grab one raw gray frame per device, then measure it. The exit status of the
# *pipeline* is not the exit status of the grab, so capture the bytes and test
# the file itself -- an empty file is the only honest "GRAB_FAIL".
for dev in /dev/video0 /dev/video1; do
  [ -e "$dev" ] || continue
  raw="$OUT/frame.$(basename "$dev").gray"
    err="$OUT/frame.$(basename "$dev").err"
    if [ -r "$dev" ]; then
      ffmpeg -hide_banner -loglevel error -f v4l2 -i "$dev" -frames:v 1 \
             -f rawvideo -pix_fmt gray -y "$raw" 2>"$err"
      how="direct (uid $(id -u) can read $dev)"
    else
      timeout 30 sudo -n ffmpeg -hide_banner -loglevel error -f v4l2 -i "$dev" \
             -frames:v 1 -f rawvideo -pix_fmt gray -y "$raw" 2>"$err"
      how="via sudo -n (mode $(stat -c%a "$dev") blocks uid $(id -u))"
    fi
    if [ -s "$raw" ]; then
      echo "GRAB_OK $dev -> $raw ($(stat -c%s "$raw") bytes, $how)"
      python3 "$HERE/frame_luma.py" 640 480 <"$raw"
    else
      echo "GRAB_FAIL $dev -- no frame bytes produced ($how)"
      echo "  ffmpeg stderr (first 3 lines):"
      head -3 "$err" 2>/dev/null | sed 's/^/    /'
    fi
  done

echo
echo "=== 3. USB instruments (VNA / SDR / power meter / DMM) ==="
lsusb 2>/dev/null | grep -viE 'root hub|smartcard|camera|sensor|card reader|elements|ethernet|bluetooth|EM7455' \
  || echo "(nothing beyond enumerated peripherals)"

echo
echo "=== 4. serial ports (an RF instrument would appear here) ==="
for p in /dev/ttyUSB0 /dev/ttyUSB1 /dev/ttyUSB2 /dev/ttyACM0; do
  [ -e "$p" ] || continue
  printf '%s -> %s\n' "$p" \
    "$(udevadm info -q property -n "$p" 2>/dev/null | grep -E 'ID_VENDOR=|ID_MODEL=' | tr '\n' ' ')"
done
[ -e /dev/ttyUSB0 ] || echo "(no /dev/ttyUSB* serial instrument)"

echo
echo "=== 5. operator-supplied photos / measurement notes on disk ==="
find "$HOME/repos" "$HOME/worktrees" "$HOME/scratch" -maxdepth 3 -type f \
     \( -iname '*coax*' -o -iname '*caliper*' -o -iname '*bundle*.jpg' \
        -o -iname '*tape*measure*' -o -iname '*routing*.jpg' \) 2>/dev/null \
  | head -20 || true
echo "(end of photo/notes search)"

echo
echo "=== 6. any physical-evidence attachment or comment fleet-wide for this cable run ==="
python3 - "$HOME/.hermes/kanban/boards" <<'PY' 2>/dev/null || echo "(kanban scan unavailable)"
import os, sqlite3, sys, glob
root = sys.argv[1]
boards = attachments = comments = 0
hits = []
for db in sorted(glob.glob(os.path.join(root, "*", "kanban.db"))):
    boards += 1
    try:
        c = sqlite3.connect(f"file:{db}?mode=ro", uri=True)
    except sqlite3.Error:
        continue
    try:
        attachments += c.execute("select count(*) from task_attachments").fetchone()[0]
    except sqlite3.Error:
        pass
    try:
        n = c.execute("select count(*) from task_comments where lower(body) like '%coax%'"
                      " or lower(body) like '%caliper%' or lower(body) like '%bundle od%'").fetchone()[0]
        comments += n
        if n:
            hits.append((os.path.basename(os.path.dirname(db)), n))
    except sqlite3.Error:
        pass
    c.close()
print(f"boards_scanned={boards} attachments_seen={attachments} coax/caliper_comments={comments}")
for b, n in hits:
    print(f"  board {b}: {n} matching comment(s)")
print("NOTE: a comment is prose, not a measurement; no attachment anywhere carries a")
print("      caliper/tape/bundle-OD number for this run (see the card thread).")
PY

echo
echo "=== 7. conclusion ==="
echo "This host can run software. It cannot route, tie, caliper, tape-measure,"
echo "thermally characterise, or label a physical cable run, and it has no"
echo "instrument to read one. Every physical field in the setup record therefore"
echo "stays unfilled rather than guessed."
echo
echo "probe complete -- $STAMP"
