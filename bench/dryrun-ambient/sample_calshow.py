#!/usr/bin/env python3
"""calshow ambient dry-run sampler (fleet card meshcore:t_da84afb3).

Invoke the firmware's read-only `calshow` serial command once per sample,
extract the die-temperature field, and append one line per sample to a
CSV log:

    iso8601_timestamp,setpoint,chamber_air_c,die_temp_raw

- die_temp_raw is RETAINED AS THE RAW STRING exactly as printed by the
  firmware (snprintf field `die_temp=%.1f`, MyMesh.cpp:179 @ 3fdfbc8e) —
  it is never converted, rounded, or inferred.
- setpoint is the literal AMBIENT for the dry run; chamber air is n/a
  (no chamber exists under this host's control — see bench/soak-0c/REPORT.md).
- Wire protocol per bench/atcut-fit/CAL-CLI-SPEC.md: 115200 8N1, DTR/RTS
  deasserted (no auto-reset), line terminator CR (0x0D); LF-only lines
  never execute. The firmware echoes the command and replies with
  `  -> cal valid=... die_temp=... off_hz=...`.
- Samples that produce no parseable reply are NEVER appended to the data
  log (no fabricated values); failures go to stdout events + nonzero exit.
- --self-test exercises the parser offline against SYNTHETIC,
  clearly-labeled reply strings and never touches a port or the data log.

NO temperature value is fabricated anywhere in this script: the data log
only ever contains bytes a port actually returned.
"""
from __future__ import annotations

import argparse
import datetime
import re
import sys
import time

BAUD = 115200
CMD = b"calshow\r"          # exact wire bytes: read-only calshow + CR terminator
REPLY_WINDOW_SECS = 3.0     # max wait for a reply per sample
SETPOINT = "AMBIENT"
CHAMBER_AIR = "n/a"
LOG_HEADER = "iso8601,setpoint,chamber_air_c,die_temp_raw"

# Firmware reply contract (MyMesh.cpp:179-181 @ 3fdfbc8e):
#   cal valid=%s k=%.6g T0=%.2fC range=+/-%.0fC die_temp=%.1f off_hz=%.0f
# All fields are space-separated and contain no spaces themselves.
REPLY_RE = re.compile(
    r"cal valid=(?P<valid>\S+)"
    r" k=(?P<k>\S+)"
    r" T0=(?P<t0>\S+)"
    r" range=(?P<range>\S+)"
    r" die_temp=(?P<die_temp>\S+)"
    r" off_hz=(?P<off_hz>\S+)"
)
# decimal grammar of a %.1f print (what a healthy die_temp raw looks like)
DECIMAL_RE = re.compile(r"^[-+]?[0-9]+(\.[0-9]+)?$")


def ts() -> str:
    """Local-time ISO-8601 with UTC offset, second resolution."""
    return (
        datetime.datetime.now(datetime.timezone.utc)
        .astimezone()
        .isoformat(timespec="seconds")
    )


def parse_die_temp(line: str):
    """Extract the raw die-temp string from one console line.

    Returns (die_temp_raw, match_dict) or (None, None). The returned
    string is the verbatim bytes between 'die_temp=' and the next space
    — preserved exactly as the firmware printed it, never re-formatted.
    """
    m = REPLY_RE.search(line)
    if not m:
        return None, None
    return m.group("die_temp"), m.groupdict()


def _split_lines(buf: bytes):
    """Split a raw RX buffer into text lines (handles \\r, \\n, \\r\\n)."""
    text = buf.decode("ascii", errors="replace")
    return [ln for ln in re.split(r"[\r\n]+", text) if ln.strip()]


def sample_once(ser) -> tuple:
    """Send `calshow\\r`, read the reply window, return the evidence.

    Returns (die_temp_raw, full_reply_line, raw_bytes_len).
    """
    ser.reset_input_buffer()
    n = ser.write(CMD)
    ser.flush()
    buf = b""
    deadline = time.monotonic() + REPLY_WINDOW_SECS
    reply_line = None
    die_raw = None
    while time.monotonic() < deadline:
        chunk = ser.read(256)
        if chunk:
            buf += chunk
            for ln in _split_lines(buf):
                raw, _ = parse_die_temp(ln)
                if raw is not None:
                    die_raw, reply_line = raw, ln.strip()  # keep LAST match
    return die_raw, reply_line, (n, len(buf))


def run(args) -> int:
    import serial  # lazy: only needed for a real run, not --self-test

    print(f"[{ts()}] opening {args.port} @ {BAUD} 8N1 (DTR/RTS off)")
    ser = serial.Serial(args.port, BAUD, timeout=0.2, write_timeout=1.0)
    ser.dtr = False
    ser.rts = False

    log_path = args.log
    fresh = not _file_exists(log_path)
    logf = open(log_path, "a", encoding="utf-8")
    if fresh:
        logf.write(LOG_HEADER + "\n")
    logf.flush()
    print(f"[{ts()}] log file: {log_path} ({'new' if fresh else 'append'})")

    ok = fail = 0
    for i in range(1, args.samples + 1):
        stamp = ts()
        try:
            die_raw, reply_line, (nsent, nrx) = sample_once(ser)
        except Exception as e:
            print(f"[{stamp}] sample {i}/{args.samples}: PORT ERROR: "
                  f"{type(e).__name__}: {e} -> NOT LOGGED")
            fail += 1
        else:
            if die_raw is None:
                print(f"[{stamp}] sample {i}/{args.samples}: NO PARSEABLE REPLY "
                      f"({nsent} bytes sent, {nrx} received) -> NOT LOGGED")
                fail += 1
            else:
                logf.write(f"{stamp},{SETPOINT},{CHAMBER_AIR},{die_raw}\n")
                logf.flush()
                print(f"[{stamp}] sample {i}/{args.samples}: OK "
                      f"die_temp raw='{die_raw}' full reply: {reply_line}")
                ok += 1
        if i < args.samples:
            time.sleep(args.interval_secs)

    logf.close()
    ser.close()
    print(f"[{ts()}] done: {ok} samples logged, {fail} failures "
          f"(>=3 logged samples required for the dry-run gate)")
    return 0 if (ok >= 3 and fail == 0) else 1


def _file_exists(p: str) -> bool:
    import os

    return os.path.exists(p)


def self_test() -> int:
    """Offline parser proof against SYNTHETIC firmware-format strings.

    These strings are machine-generated from the snprintf contract at
    MyMesh.cpp:179-181 @ 3fdfbc8e. They are NOT measurements and are
    never written to the data log. Numbers chosen are arbitrary shapes
    (including sign/format edge cases), not claimed temperatures.
    """
    cases = [
        # (synthetic reply line, expected die_temp raw or None)
        (
            "  -> cal valid=yes k=0.034021 T0=24.95C range=+/-60C "
            "die_temp=23.4 off_hz=79",
            "23.4",
        ),
        (
            "  -> cal valid=no k=0 T0=0.00C range=+/-60C "
            "die_temp=-0.0 off_hz=0",
            "-0.0",
        ),
        (
            "cal valid=yes k=0.05 T0=-20.00C range=+/-60C "
            "die_temp=-19.7 off_hz=1240",
            "-19.7",
        ),
        (
            "  -> cal valid=yes k=0.05 T0=25.00C range=+/-60C "
            "die_temp=nan off_hz=0",
            "nan",  # raw preserved verbatim; parser must NOT choke
        ),
        ("  -> commands: status, mode, flush, reset, erase, cal <k> <T0>, "
         "calshow", None),  # help line: no die_temp field
        ("calshow", None),  # echo of the command itself
        ("  -> usage: cal <k_ppm_per_C2> <T0_C>", None),
    ]
    fails = 0
    for i, (line, want) in enumerate(cases, 1):
        got, m = parse_die_temp(line)
        ok = got == want
        fails += 0 if ok else 1
        numeric = bool(got is not None and DECIMAL_RE.match(got))
        print(f"[self-test {i}/{len(cases)}] {'OK  ' if ok else 'FAIL'} "
              f"SYNTHETIC line={line!r} -> die_temp raw={got!r}"
              f"{' (decimal-grammar yes)' if numeric else ''}")
    print(f"[self-test] parser extracted the raw die-temp field verbatim "
          f"in {len(cases) - fails}/{len(cases)} SYNTHETIC cases "
          f"(strings are synthetic, NOT measurements)")
    return 0 if fails == 0 else 1


def main() -> int:
    ap = argparse.ArgumentParser(
        description="calshow ambient dry-run sampler "
                    "(fleet card meshcore:t_da84afb3)")
    ap.add_argument("--port", help="serial device, e.g. /dev/ttyUSB0")
    ap.add_argument("--samples", type=int, default=3,
                    help="number of calshow samples (default 3, gate needs >=3)")
    ap.add_argument("--interval-secs", type=int, default=30,
                    help="seconds between samples (allowed 30-60)")
    ap.add_argument("--log", default="bench/dryrun-ambient/calshow_ambient.log",
                    help="CSV log path (append; header added if new)")
    ap.add_argument("--self-test", action="store_true",
                    help="offline parser self-test (SYNTHETIC strings, "
                         "no port, no data log writes)")
    args = ap.parse_args()

    if args.self_test:
        return self_test()
    if not args.port:
        ap.error("--port required for a real run (or use --self-test)")
    if not (30 <= args.interval_secs <= 60):
        ap.error("--interval-secs must be within 30-60 per the campaign spec")
    if args.samples < 1:
        ap.error("--samples must be >= 1 (dry-run gate needs >=3)")
    return run(args)


if __name__ == "__main__":
    sys.exit(main())