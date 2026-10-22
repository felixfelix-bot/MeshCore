#!/usr/bin/env python3
"""passive_mapper thermal-calibration bench CLI (stdlib only).

    soak      record die-temp-soaked points from the module's `calshow` CLI
    edgescan  measured required compensation per soak point, using the module's
              own injected offset (no extra firmware needed)
    refsweep  measured required compensation per soak point from a swept
              reference transmitter ("benchtx" contract, see bench/README.md)
    fit       fit k/T0 from measured.csv, emit /selfcal.dat + the `cal` line
    lag       die-vs-crystal time constant from a steady-point ramp log
    ramp      log die temp + reception ratio at a fixed rate during a sweep
    hyst      die-vs-crystal time constant from an up/down ramp PAIR (the bench
              method: needs no soak and no model, only a reception edge)

Hardware is optional: every device-touching command accepts --simulate, which
substitutes a synthetic module with a known drift curve. That is how the whole
pipeline is tested here (see test_calib.py) - the serial paths themselves are
untested until the bench run.

Serial framing: MyMesh's CLI is line-oriented ('\n' terminated, 115200 8N1),
so no pyserial dependency is needed.
"""

import argparse
import csv
import json
import math
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import calib  # noqa: E402

DEFAULT_NOMINAL_HZ = 869_618_000.0
# SF8 LoRa capture half-window in ppm: ~BW/2. 62.5 kHz -> +/-35.9 ppm,
# 125 kHz -> +/-71.8 ppm.
BW62_5_PPM = 35.9
BW125_PPM = 71.8
BEACON_TELEMETRY_NOTE = "mapper fallback (BW125) engages when no cal blob is loaded"


# ---------------------------------------------------------------------------
# serial (stdlib termios, no pyserial)
# ---------------------------------------------------------------------------

class SerialError(RuntimeError):
    pass


class RawSerial:
    """Minimal 8N1 line-oriented serial port."""

    def __init__(self, path, baud=115200, timeout=2.0):
        import termios
        import tty  # noqa: F401  (imported for parity with tty semantics)
        self.path = path
        self.timeout = timeout
        self.fd = os.open(path, os.O_RDWR | os.O_NOCTTY | os.O_NONBLOCK)
        attrs = termios.tcgetattr(self.fd)
        attrs[0] = attrs[1] = attrs[3] = 0
        attrs[2] = termios.CS8 | termios.CREAD | termios.CLOCAL
        attrs[4] = attrs[5] = getattr(termios, "B%d" % baud)
        attrs[6][termios.VMIN] = 0
        attrs[6][termios.VTIME] = 0
        termios.tcsetattr(self.fd, termios.TCSANOW, attrs)
        termios.tcflush(self.fd, termios.TCIOFLUSH)
        self._buf = b""

    def close(self):
        try:
            os.close(self.fd)
        except OSError:
            pass

    def write_line(self, line):
        os.write(self.fd, (line + "\n").encode())

    def read_line(self, timeout=None):
        import select
        deadline = time.monotonic() + (self.timeout if timeout is None else timeout)
        while True:
            if b"\n" in self._buf:
                line, self._buf = self._buf.split(b"\n", 1)
                return line.decode(errors="replace").strip()
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                return None
            r, _, _ = select.select([self.fd], [], [], min(0.2, remaining))
            if r:
                try:
                    chunk = os.read(self.fd, 4096)
                except BlockingIOError:
                    continue
                if not chunk:
                    return None
                self._buf += chunk

    def command(self, line, timeout=3.0):
        """Send a command and return the first reply line (None on timeout)."""
        self.write_line(line)
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            reply = self.read_line(timeout=deadline - time.monotonic())
            if reply:
                return reply
        return None


# ---------------------------------------------------------------------------
# devices
# ---------------------------------------------------------------------------

class Dut:
    """The NiceRF LR2021 module under calibration (mapper firmware CLI)."""

    def __init__(self, port, baud=115200, dry=False):
        self.dry = dry
        self.ser = None if dry else RawSerial(port, baud)

    def close(self):
        if self.ser:
            self.ser.close()

    def calshow(self):
        reply = self.ser.command("calshow")
        if not reply:
            raise SerialError("no reply to calshow (is the mapper running?)")
        return calib.parse_calshow(reply)

    def status(self):
        reply = self.ser.command("status")
        if not reply:
            raise SerialError("no reply to status")
        return calib.parse_status(reply)

    def reset_counter(self):
        self.ser.command("reset")

    def set_cal(self, k, t0):
        reply = self.ser.command(calib.cal_command(k, t0))
        if not reply or not reply.startswith("cal "):
            raise SerialError("cal command rejected: %r" % (reply,))
        return reply

    def window_count(self, capture_s, telemetry_period_s=60.0):
        """Packets the DUT logged in a capture window.

        The mapper has no per-packet RX counter other than the record counter, so
        we reset it, wait, and read it back. Periodic telemetry records
        (MAP_TELEMETRY_SECS = 60 s) inflate the count by ~capture/60, so that is
        subtracted here; values are normalised against the zero-offset baseline
        measured at the start of each scan.
        """
        self.reset_counter()
        time.sleep(capture_s)
        logged = self.status()["logged"]
        telemetry = int(round(capture_s / telemetry_period_s))
        return max(0, logged - telemetry)


class RefTx:
    """Reference transmitter running the same image with the `benchtx` CLI.

    Contract (NOT part of the mapper image - the swept-reference path is
    optional and needs a second board flashed with a frequency-agile test TX):
        benchtx <freq_hz> <n> <gap_ms>
          -> "benchtx f=<hz> n=<n> gap=<ms> ..." once the burst is queued
        The burst transmits n MeshCore-parseable packets at freq_hz with the
        build's SF/BW, then stops. Its own die temp is reportable via calshow.
    """

    def __init__(self, port, baud=115200, dry=False):
        self.dry = dry
        self.ser = None if dry else RawSerial(port, baud)

    def close(self):
        if self.ser:
            self.ser.close()

    def burst(self, freq_hz, n, gap_ms):
        reply = self.ser.command("benchtx %d %d %d" % (freq_hz, n, gap_ms))
        if not reply or not reply.startswith("benchtx"):
            raise SerialError("benchtx failed: %r" % (reply,))
        # burst duration + margin: n packets, each ~1 s of airtime at SF8/BW62.5
        time.sleep(n * (gap_ms / 1000.0) + 5.0)

    def calshow(self):
        reply = self.ser.command("calshow")
        if not reply:
            raise SerialError("no reply to calshow on reference board")
        return calib.parse_calshow(reply)


# ---------------------------------------------------------------------------
# simulation (also used by the self-tests)
# ---------------------------------------------------------------------------

class FakeDut:
    """Synthetic module: drift = -k_true*(T-T0_true)^2, compensation = the blob's
    +k*(T-T0)^2, and packets are decoded while |drift - compensation| is inside
    the capture half-window (ppm). Used by the self-tests and by --simulate."""

    def __init__(self, k_true=0.04, t0_true=22.0, temp_c=25.0,
                 half_window_ppm=BW62_5_PPM, ref_offset_ppm=0.0):
        self.k_true = k_true
        self.t0_true = t0_true
        self.temp_c = temp_c
        self.half_window_ppm = half_window_ppm
        self.ref_offset_ppm = ref_offset_ppm
        self.k = 0.0
        self.t0 = 25.0
        self.logged = 0

    def drift_ppm(self, temp_c=None):
        t = self.temp_c if temp_c is None else temp_c
        return -self.k_true * (t - self.t0_true) ** 2

    def applied_ppm(self):
        return self.k * (self.temp_c - self.t0) ** 2

    def capture_ratio(self, ref_offset_ppm=0.0):
        """Fraction of packets decoded for a reference this far off the DUT's
        nominal frequency. 50% at the +/-BW/2 capture edge.

        The DUT's real LO error is (crystal drift + applied compensation) in ppm;
        a reference sitting ref_offset_ppm above nominal leaves a residual of
        ref_offset - LO error.
        """
        lo_err = self.drift_ppm() + self.applied_ppm()
        err = abs(ref_offset_ppm + self.ref_offset_ppm - lo_err)
        return max(0.0, min(1.0, 1.0 - err / (2.0 * self.half_window_ppm)))

    def set_cal(self, k, t0):
        self.k, self.t0 = k, t0
        return "cal k=%.6g T0=%.2fC -> persisted (valid=yes)" % (k, t0)

    def window_count(self, capture_s=None, telemetry_period_s=60.0):
        ratio = self.capture_ratio()
        self.logged = int(round(ratio * self.pkts_per_window))
        return self.logged

    pkts_per_window = 20

    def calshow(self):
        return {
            "valid": self.k > 0.0, "k": self.k, "t0": self.t0, "range_c": 90.0,
            "die_temp_c": self.temp_c, "off_hz": self.applied_ppm() * DEFAULT_NOMINAL_HZ / 1e6,
        }

    def status(self):
        return {"mode": "MAP", "distinct": 1, "logged": self.logged, "dropped": 0, "buf": 0,
                "bw_khz": 62.5 if self.k > 0 else 125.0, "fallback": self.k == 0.0,
                "die_temp_c": self.temp_c, "off_hz": 0.0, "cal_valid": self.k > 0.0}

    def reset_counter(self):
        self.logged = 0


# ---------------------------------------------------------------------------
# measurement algorithms
# ---------------------------------------------------------------------------

def scan_edges(dut, temp_c, t0_offset_c=15.0, nominal_per_window=20, capture_s=60.0,
               k_min=0.002, k_max=2.0, grid=40, rel_tol=0.01, log=print):
    """Find the injected-offset band in which the DUT decodes the reference.

    The DUT's own `cal <k> <T0>` sets a known, positive offset
    O(k) = k*(T-T0_prog)^2. A cold crystal is slow, so reception needs
    O = required = k_true*(T-T0_true)^2 and holds while |required - O| stays
    inside the capture half-window. That gives a band [k_lo, k_hi] whose midpoint
    is the required compensation:

        required_ppm(T) = 0.5*(O(k_lo) + O(k_hi))

    No decodable baseline is assumed: at any interesting temperature the drift
    already exceeds the window, so k=0 decodes nothing and the band has to be
    *searched for*. A coarse log grid locates it, then each 50% crossing is
    bisected.

    T0_prog is deliberately placed `t0_offset_c` away from the die temperature:
    the parabola is FLAT at its own turnover, so programming T0_prog == T would
    inject nothing at all (dO/dk = (T-T0_prog)^2 = 0). At 15 C offset the
    sensitivity is 225 ppm per unit k, so k_max=2 reaches ~450 ppm of injection;
    the firmware clamps the applied offset at MAX_PPM (300), which this function
    refuses to cross.

    Band open at k=0 (drift smaller than the half window, i.e. warm points): only
    the upper edge is reachable and the width is taken from the BW
    (half_window_ppm).
    """

    t0_prog = temp_c + t0_offset_c
    sens = (temp_c - t0_prog) ** 2

    def ratio_for(k):
        dut.set_cal(k, t0_prog)
        return dut.window_count(capture_s) / float(nominal_per_window)

    def offset_of(k):
        return k * sens

    log("  grid scan: T0_prog=%.1f C, sensitivity %.0f ppm/k, k in [%g, %g]"
        % (t0_prog, sens, k_min, k_max))
    ks = [k_min * (k_max / k_min) ** (i / float(grid - 1)) for i in range(grid)]
    ratios = []
    for k in ks:
        if offset_of(k) > MAX_PPM:
            ratios.append(0.0)
            continue
        ratios.append(ratio_for(k))
    best = max(range(len(ks)), key=lambda i: ratios[i])
    if ratios[best] < 0.5:
        raise RuntimeError(
            "no injected offset in [%g, %g] (up to %.0f ppm) restores reception "
            "at %.1f C (best ratio %.2f): either the module drifted beyond that "
            "range, or the reference is not being decoded at all (wrong SF/BW, "
            "reference silent, or the reference itself is drifting)."
            % (k_min, k_max, offset_of(k_max), temp_c, ratios[best]))
    log("  best grid k=%.4f (O=%+.1f ppm) ratio=%.2f" % (ks[best], offset_of(ks[best]), ratios[best]))

    # walk out from the best grid point while the 50% condition holds
    a = best
    while a > 0 and ratios[a - 1] >= 0.5:
        a -= 1
    b = best
    while b + 1 < len(ks) and ratios[b + 1] >= 0.5:
        b += 1

    def bisect(lo_k, hi_k):
        """Return the k where ratio crosses 0.5, given ratio(lo_k)>=.5>ratio(hi_k)."""
        while (hi_k - lo_k) / hi_k > rel_tol:
            mid = 0.5 * (lo_k + hi_k)
            if ratio_for(mid) < 0.5:
                hi_k = mid
            else:
                lo_k = mid
        return lo_k

    if b + 1 < len(ks):
        k_hi = bisect(ks[b], ks[b + 1])
    else:
        raise RuntimeError("the band is still open at k_max=%g (%.0f ppm): widen "
                           "k_max or check MAX_PPM" % (k_max, offset_of(k_max)))
    if a > 0:
        k_lo = bisect(ks[a], ks[a - 1]) if ratios[a - 1] < 0.5 else None
        if ratios[a - 1] >= 0.5:
            k_lo = None
    else:
        k_lo = None     # band already open at the bottom of the grid

    if k_lo is not None:
        required = 0.5 * (offset_of(k_lo) + offset_of(k_hi))
        width = offset_of(k_hi) - offset_of(k_lo)
        method = "midpoint of both edges"
    else:
        required = offset_of(k_hi) - half_window_ppm
        width = None
        method = "upper edge minus half window (BW-derived width)"
    return {
        "temp_c": temp_c, "t0_programmed": t0_prog, "k_lo": k_lo, "k_hi": k_hi,
        "required_offset_ppm": required, "measured_width_ppm": width,
        "method": method, "sensitivity_ppm_per_k": sens,
        "best_ratio": ratios[best],
    }


MAX_PPM = 300.0            # SelfCal::MAX_PPM
HALF_WINDOW_PPM = BW62_5_PPM
half_window_ppm = HALF_WINDOW_PPM  # module-level default for scan_edges


def reduce_refsweep(steps, nominal_hz, nominal_width_hz=None):
    win = calib.find_passband_window(steps, nominal_hz, nominal_width_hz)
    if win is None:
        return None
    # The accepted band is centred on the DUT's real LO, so the band centre is
    # the DUT's drift; compensation is its negation.
    win["required_offset_ppm"] = -win["offset_ppm"]
    return win


# ---------------------------------------------------------------------------
# commands
# ---------------------------------------------------------------------------

def _open_dut(args):
    if args.simulate:
        return FakeDut(k_true=args.sim_k, t0_true=args.sim_t0, temp_c=args.sim_temp,
                       ref_offset_ppm=args.sim_ref_ppm)
    return Dut(args.dut_port, dry=False)


def cmd_soak(args):
    dut = _open_dut(args)
    rows = []
    for sp in [float(x) for x in args.setpoints.split(",")]:
        print("hold the module at %+.1f C and wait for soak ..." % sp)
        hist = []
        while True:
            cs = dut.calshow()
            hist.append(cs["die_temp_c"])
            if len(hist) > args.window:
                hist.pop(0)
            span = max(hist) - min(hist) if len(hist) == args.window else 1e9
            print("  die_temp=%.2f C  drift_window=%.2f C  off_hz=%.0f" %
                  (cs["die_temp_c"], span, cs["off_hz"]))
            if span < args.stable_c:
                if args.stable_secs and not args.simulate:
                    time.sleep(args.stable_secs)   # confirm the soak really holds
                break
            if not args.simulate:
                time.sleep(args.interval)           # a simulated soak takes no time
        rows.append({"point_label": "%+gC" % sp, "setpoint_c": sp,
                     "ts": time.strftime("%Y-%m-%dT%H:%M:%S"),
                     "die_temp_c": "%.2f" % cs["die_temp_c"],
                     "applied_off_hz": "%.0f" % cs["off_hz"],
                     "cal_valid": int(cs["valid"])})
    _write_csv(args.out, rows)
    print("wrote %d soak points to %s" % (len(rows), args.out))
    if args.simulate:
        return 0
    print("NOTE: %s" % BEACON_TELEMETRY_NOTE)
    return 0


def cmd_edgescan(args):
    dut = _open_dut(args)
    out_rows = []
    for sp in [x for x in args.points.split(",") if x.strip()]:
        target = float(sp)
        if args.simulate:
            dut.temp_c = target
            tp = target
        else:
            tp = dut.calshow()["die_temp_c"]
        print("point %+g C (die_temp=%.2f C): scanning injected offset ..." % (target, tp))
        res = scan_edges(dut, tp, t0_offset_c=args.t0_offset,
                         nominal_per_window=args.pkts, capture_s=args.capture_s,
                         k_max=args.k_max)
        print("  -> required compensation %+.1f ppm (%s)" %
              (res["required_offset_ppm"], res["method"]))
        out_rows.append({
            "point_label": "%+gC" % target,
            "die_temp_c": "%.2f" % res["temp_c"],
            "required_offset_ppm": "%.2f" % res["required_offset_ppm"],
            "drift_ppm": "%.2f" % -res["required_offset_ppm"],
            "k_lo": "" if res["k_lo"] is None else "%.6g" % res["k_lo"],
            "k_hi": "%.6g" % res["k_hi"],
            "measured_width_ppm": "" if res["measured_width_ppm"] is None
                                  else "%.1f" % res["measured_width_ppm"],
            "method": res["method"],
        })
    _write_csv(args.out, out_rows)
    print("wrote %d points to %s" % (len(out_rows), args.out))
    return 0


def cmd_refsweep(args):
    nominal = args.nominal_hz
    dut = _open_dut(args)
    ref = None if args.simulate else RefTx(args.ref_port)
    out_rows = []
    lo = nominal + args.start_hz
    hi = nominal + args.stop_hz
    f = lo
    while f <= hi + 0.5 * args.step_hz:
        dut.reset_counter()
        if args.simulate:
            ratio = dut.capture_ratio(ref_offset_ppm=(f - nominal) / nominal * 1e6)
            logged = int(round(ratio * args.pkts))
        else:
            ref.burst(int(round(f)), args.pkts, args.gap_ms)
            logged = dut.status()["logged"]
        row = {"point_label": args.point, "ref_freq_hz": "%.0f" % f,
               "ref_offset_ppm": "%.2f" % ((f - nominal) / nominal * 1e6),
               "pkts_sent": args.pkts, "pkts_recv": logged,
               "capture_ratio": "%.3f" % (logged / float(args.pkts))}
        out_rows.append(row)
        print("  %+.1f ppm: %d/%d" % (float(row["ref_offset_ppm"]), logged, args.pkts))
        f += args.step_hz
    _write_csv(args.out, out_rows)
    steps = [(float(r["ref_freq_hz"]), float(r["capture_ratio"])) for r in out_rows]
    win = reduce_refsweep(steps, nominal, nominal_width_hz=round(BW62_5_PPM * 2 * nominal / 1e6))
    if win is None:
        print("no passband window found in this sweep - widen --start-hz/--stop-hz")
        return 2
    print("passband centre %+.0f Hz (%+.1f ppm) width %.0f Hz" %
          (win["offset_hz"], win["offset_ppm"], win["width_hz"]))
    print("required compensation %.1f ppm" % win["required_offset_ppm"])
    if ref:
        ref.close()
    return 0


def cmd_fit(args):
    pts = _read_points(args.input)
    res = calib.fit_curve(pts, t0_fixed=args.t0_fixed)
    print("fit: k=%.5f ppm/C^2  T0=%.2f C   (residual %.2f ppm rms, %d points, "
          "span %.1f C)" % (res["k"], res["t0"], res["rms_ppm"], res["n_points"],
                            res["t_span_c"]))
    if res["t0_fixed"] is None:
        print("     bias term: %.2f ppm (unmodelled reference/initial-tolerance)"
              % res["bias_ppm"])
    else:
        print("     bias term: %.2f ppm (T0 pinned at %.2f C)"
              % (res["bias_ppm"], res["t0_fixed"]))
    for w in res["warnings"]:
        print("WARNING: %s" % w)
    blob = calib.pack_blob(res["k"], res["t0"], version=1)
    with open(args.out, "wb") as fh:
        fh.write(blob)
    print("wrote %d-byte blob to %s" % (len(blob), args.out))
    print("blob hex: %s" % blob.hex())
    print("persist on the module with:  %s" % calib.cal_command(res["k"], res["t0"]))
    print("expected applied offset: %+.0f Hz at T0, %+.0f Hz at %.1f C" % (
        0.0, calib.required_offset_ppm(res["t_min_c"], res["k"], res["t0"]) *
        args.nominal_hz / 1e6, res["t_min_c"]))
    return 0 if not res["warnings"] else 1


def cmd_lag(args):
    rows = _read_csv(args.input)
    t = [float(r["t_s"]) for r in rows]
    temp = [float(r["die_temp_c"]) for r in rows]
    off = [float(r[args.column]) for r in rows]
    res = calib.fit_lag(t, temp, off, args.k, args.t0, max_lag_s=args.max_lag_s)
    print(json.dumps(res, indent=2))
    if res.get("ok"):
        print("crystal thermal lag tau ~ %.0f s (model residual %.1f ppm vs %.1f ppm "
              "with no lag; excitation span %.1f C)"
              % (res["tau_s"], res["rms_ppm"], res["rms_no_lag_ppm"],
                 res["excitation_span_c"]))
        if res["lag_identifiable"]:
            print("measured die-vs-crystal lag = %.0f s" % res["lag_s"])
        else:
            print("lag NOT identifiable from this log - no lag number reported")
        print("SelfCal TEMP_TC_SECS is 10 s: %s" %
              ("consistent with the measurement" if res["tau_s"] < 30 else
               "TOO SHORT - raise TEMP_TC_SECS to ~%.0f s (see bench/README.md)"
               % res["tau_s"]))
    for note in res.get("notes", []):
        print("NOTE: %s" % note)
    for warning in res.get("warnings", []):
        print("WARNING: %s" % warning)
    return 0 if res.get("ok") else 1


# ---------------------------------------------------------------------------
# ramp logging + hysteresis (the bench-measurable lag)
# ---------------------------------------------------------------------------

# Default injected compensation for the simulated ramp: the requirement at -10 C
# with k=0.04, T0=25, so the reception band in crystal-temperature space sits
# inside the swept span (-40..+25 C) and both ramps cross an edge.
SIM_INJ_PPM = 49.0
SIM_EXPECTED_PKTS = 20


def _sim_ramp_rows(args, direction):
    """Synthetic ramp log with the same shape the real logger emits."""
    dt = float(args.interval)
    n = max(8, int(round(float(args.duration) / dt)))
    lo, hi = (-40.0, 25.0) if direction == "up" else (25.0, -40.0)
    temp = [lo + (hi - lo) * i / (n - 1) for i in range(n)]
    crystal = [temp[0]]
    a = 1.0 - math.exp(-dt / args.sim_tau)
    for i in range(1, n):
        crystal.append(crystal[-1] + (temp[i] - crystal[-1]) * a)
    rows = []
    for i in range(n):
        req = calib.required_offset_ppm(crystal[i], args.sim_k, args.sim_t0)
        inside = abs(req - args.sim_inj_ppm) < BW62_5_PPM
        rows.append({"t_s": "%.2f" % (i * dt),
                     "die_temp_c": "%.2f" % temp[i],
                     "pkts": args.sim_expected_pkts if inside else 0})
    return rows


def cmd_ramp(args):
    """Log die temperature + packets received per interval while the module is
    swept through temperature. Run it twice, once per direction."""
    if args.simulate:
        rows = _sim_ramp_rows(args, args.direction)
    else:
        dut = _open_dut(args)
        rows = []
        t0 = time.monotonic()
        print("logging every %.1f s for %.0f s; drive the %s sweep now"
              % (args.interval, args.duration, args.direction))
        while time.monotonic() - t0 < args.duration:
            tel = dut.calshow()
            dut.reset_counter()
            time.sleep(args.interval)
            logged = dut.status()["logged"]
            # one periodic telemetry record per MAP_TELEMETRY_SECS inflates it
            inflight = int(round(args.interval / 60.0))
            rows.append({"t_s": "%.2f" % (time.monotonic() - t0),
                         "die_temp_c": "%.2f" % tel["die_temp_c"],
                         "pkts": max(0, logged - inflight)})
        dut.close()
    peak = max([int(r["pkts"]) for r in rows] or [1]) or 1
    for r in rows:
        r["ratio"] = "%.3f" % (int(r["pkts"]) / float(peak))
    _write_csv(args.out, rows)
    print("wrote %d samples to %s (%d peak packets)" % (len(rows), args.out, peak))
    return 0


def _ramp_triples(path):
    rows = _read_csv(path)
    t = [float(r["t_s"]) for r in rows]
    temp = [float(r["die_temp_c"]) for r in rows]
    ratio = [float(r["ratio"]) for r in rows]
    return t, temp, ratio


def cmd_hyst(args):
    """Time constant from an up/down ramp pair - the number TEMP_TC_SECS must match."""
    up = _ramp_triples(args.up)
    down = _ramp_triples(args.down)
    res = calib.fit_edge_hysteresis(up, down, threshold=args.threshold)
    print(json.dumps(res, indent=2))
    if res.get("ok"):
        tau = res["tau_s"]
        print("crystal thermal lag tau ~ %.0f s  (edge shift %.2f C over rates "
              "%.3f + %.3f K/s)" % (tau, res["delta_t_edge_c"],
                                    res["rate_up_k_per_s"], res["rate_down_k_per_s"]))
        print("SelfCal TEMP_TC_SECS is 10 s: %s" %
              ("consistent with the measurement" if tau < 30 else
               "TOO SHORT - raise TEMP_TC_SECS to ~%.0f s (see bench/README.md)" % tau))
    for note in res.get("notes", []):
        print("NOTE: %s" % note)
    return 0 if res.get("ok") else 1


def _write_csv(path, rows):
    if not rows:
        return
    with open(path, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    print("wrote %s" % path)


def _read_csv(path):
    with open(path, newline="") as fh:
        return list(csv.DictReader(fh))


def _read_points(path):
    rows = _read_csv(path)
    pts = []
    for r in rows:
        temp = float(r.get("die_temp_c") or r["temp_c"])
        if "required_offset_ppm" in r and r["required_offset_ppm"] not in ("", None):
            y = float(r["required_offset_ppm"])
        else:
            y = -float(r["drift_ppm"])          # compensation = -drift
        pts.append((temp, y))
    return pts


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__,
                               formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)

    def add_sim(sp):
        sp.add_argument("--simulate", action="store_true",
                        help="use a synthetic module (no hardware)")
        sp.add_argument("--sim-k", type=float, default=0.04)
        sp.add_argument("--sim-t0", type=float, default=22.0)
        sp.add_argument("--sim-temp", type=float, default=25.0)
        sp.add_argument("--sim-ref-ppm", type=float, default=0.0)

    sp = sub.add_parser("soak", help="record soaked die-temperature points")
    sp.add_argument("--dut-port", default="/dev/ttyACM0")
    sp.add_argument("--setpoints", default="+25,+10,0,-20,-40,-45")
    sp.add_argument("--window", type=int, default=10)
    sp.add_argument("--interval", type=float, default=10.0)
    sp.add_argument("--stable-c", type=float, default=0.2)
    sp.add_argument("--stable-secs", type=float, default=120.0)
    sp.add_argument("--out", default="soak.csv")
    add_sim(sp)
    sp.set_defaults(func=cmd_soak)

    sp = sub.add_parser("edgescan", help="injected-offset band per soak point")
    sp.add_argument("--dut-port", default="/dev/ttyACM0")
    sp.add_argument("--points", default="+40,+25,+10,0,-20,-40,-45",
                    help="die temperatures to visit (must straddle the turnover)")
    sp.add_argument("--t0-offset", type=float, default=15.0,
                    help="place programmed T0 this far from the die temp so the "
                         "injected offset is not zero")
    sp.add_argument("--pkts", type=int, default=20,
                    help="reference packets per capture window")
    sp.add_argument("--capture-s", type=float, default=60.0)
    sp.add_argument("--k-max", type=float, default=2.0)
    sp.add_argument("--out", default="measured.csv")
    add_sim(sp)
    sp.set_defaults(func=cmd_edgescan)

    sp = sub.add_parser("refsweep", help="swept reference transmitter (benchtx)")
    sp.add_argument("--dut-port", default="/dev/ttyACM0")
    sp.add_argument("--ref-port", default="/dev/ttyUSB0")
    sp.add_argument("--point", default="+25C")
    sp.add_argument("--nominal-hz", type=float, default=DEFAULT_NOMINAL_HZ)
    sp.add_argument("--start-hz", type=float, default=-40_000.0)
    sp.add_argument("--stop-hz", type=float, default=40_000.0)
    sp.add_argument("--step-hz", type=float, default=4_000.0)
    sp.add_argument("--pkts", type=int, default=20)
    sp.add_argument("--gap-ms", type=int, default=250)
    sp.add_argument("--out", default="refsweep.csv")
    add_sim(sp)
    sp.set_defaults(func=cmd_refsweep)

    sp = sub.add_parser("fit", help="fit k/T0 and emit the blob")
    sp.add_argument("--input", default="measured.csv")
    sp.add_argument("--t0-fixed", type=float, default=None)
    sp.add_argument("--out", default="selfcal.dat")
    sp.add_argument("--nominal-hz", type=float, default=DEFAULT_NOMINAL_HZ)
    sp.set_defaults(func=cmd_fit)

    sp = sub.add_parser("lag", help="die-vs-crystal lag from a ramp log")
    sp.add_argument("--input", default="ramp.csv")
    sp.add_argument("--column", default="required_offset_ppm")
    sp.add_argument("--k", type=float, default=0.04)
    sp.add_argument("--t0", type=float, default=25.0)
    sp.add_argument("--max-lag-s", type=float, default=300.0)
    sp.set_defaults(func=cmd_lag)

    sp = sub.add_parser("ramp", help="log die temp + reception ratio during a sweep")
    sp.add_argument("--dut-port", default="/dev/ttyACM0")
    sp.add_argument("--direction", choices=("up", "down"), default="up")
    sp.add_argument("--interval", type=float, default=5.0,
                    help="sample period (default 5 s; must be well under the lag)")
    sp.add_argument("--duration", type=float, default=600.0)
    sp.add_argument("--out", default="ramp-up.csv")
    add_sim(sp)
    sp.add_argument("--sim-tau", type=float, default=45.0)
    sp.add_argument("--sim-inj-ppm", type=float, default=SIM_INJ_PPM)
    sp.add_argument("--sim-expected-pkts", type=int, default=SIM_EXPECTED_PKTS)
    sp.set_defaults(func=cmd_ramp)

    sp = sub.add_parser("hyst", help="time constant from an up/down ramp pair")
    sp.add_argument("--up", default="ramp-up.csv")
    sp.add_argument("--down", default="ramp-down.csv")
    sp.add_argument("--threshold", type=float, default=0.5)
    sp.set_defaults(func=cmd_hyst)

    args = p.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
