#!/usr/bin/env python3
"""Read-only calshow reachability probe (gate A evidence) for the 0 C soak task.

For each candidate serial port: open 115200 8N1 with DTR/RTS deasserted
(no auto-reset), passive-listen briefly, send the firmware's read-only
`calshow\\r` line (per bench/atcut-fit/CAL-CLI-SPEC.md the calshow command
only prints cal state; it never mutates), and log every raw byte received.
Prints ISO-8601 timestamps. NO temperature values are inferred or
fabricated anywhere: only what the port actually returns is recorded.
"""
import datetime
import sys
import time

PORTS = ["/dev/ttyUSB0", "/dev/ttyUSB1", "/dev/ttyACM0"]
BAUD = 115200
PASSIVE_SECS = 3.0
REPLY_SECS = 3.0
CMDS = [b"calshow\r", b"?\r"]  # calshow = read-only readback; '?' = help line


def ts():
    return datetime.datetime.now(datetime.timezone.utc).astimezone().isoformat(timespec="seconds")


def probe(port):
    print(f"[{ts()}] === probing {port} @ {BAUD} 8N1 (DTR/RTS off) ===")
    try:
        import serial  # pyserial
    except ImportError:
        print(f"[{ts()}] pyserial not available -> cannot probe {port}")
        return None
    try:
        ser = serial.Serial(port, BAUD, timeout=0.2, write_timeout=1.0)
        ser.dtr = False
        ser.rts = False
        ser.reset_input_buffer()
        ser.reset_output_buffer()
    except Exception as e:
        print(f"[{ts()}] {port}: OPEN FAILED: {type(e).__name__}: {e}")
        return None

    got = b""
    # 1) passive listen (boot banner or chatter if a console is live)
    t0 = time.monotonic()
    while time.monotonic() - t0 < PASSIVE_SECS:
        chunk = ser.read(256)
        if chunk:
            got += chunk
            print(f"[{ts()}] {port} passive: {chunk!r}")
    # 2) send read-only commands and listen
    for cmd in CMDS:
        try:
            n = ser.write(cmd)
            ser.flush()
            print(f"[{ts()}] {port} sent ({n} bytes): {cmd!r}")
        except Exception as e:
            print(f"[{ts()}] {port} WRITE FAILED: {type(e).__name__}: {e}")
            break
        t0 = time.monotonic()
        while time.monotonic() - t0 < REPLY_SECS:
            chunk = ser.read(256)
            if chunk:
                got += chunk
                print(f"[{ts()}] {port} reply: {chunk!r}")
    ser.close()
    total = len(got)
    print(f"[{ts()}] {port}: closed. total bytes received = {total}")
    if total == 0:
        print(f"[{ts()}] {port}: NO RESPONSE -> calshow unreachable on this port")
    return total


def main():
    print(f"[{ts()}] calshow reachability probe start (read-only; no state mutation)")
    totals = {}
    for p in PORTS:
        totals[p] = probe(p)
    print(f"[{ts()}] === probe summary ===")
    for p, n in totals.items():
        print(f"  {p}: bytes_rx={n if n is not None else 'open-failed'}")
    print(f"[{ts()}] probe done")


if __name__ == "__main__":
    sys.exit(main())