#!/usr/bin/env python3
"""Self-tests for the passive_mapper bench kit (stdlib, no hardware).

Run:  python3 examples/passive_mapper/bench/test_calib.py

Covers:
  * blob byte layout byte-for-byte against SelfCal (magic/version/size, LE floats)
  * serial-CLI reply parsers against the exact MyMesh formats
  * lossless recovery of a KNOWN (k, T0) from synthetic sweep data, including the
    single-sided (unidentifiable T0) case that produces a warning
  * the injected-offset edge scan (thermal_bench.scan_edges) end-to-end against a
    synthetic module with a known drift curve - the same code path the bench run
    uses, minus the serial port
  * passband-window reduction of a swept reference
  * lag estimator on synthetic first-order-lag step/ramp logs, incl.
    the no-excitation case that must refuse to report a number
"""

import csv
import math
import os
import random
import struct
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import calib                      # noqa: E402
import thermal_bench as tb        # noqa: E402

FAILS = []


def check(cond, label):
    if not cond:
        FAILS.append(label)
        print("FAIL: %s" % label)


def approx(a, b, tol, label):
    check(abs(a - b) <= tol, "%s (got %.4f, want %.4f +/- %.4f)" % (label, a, b, tol))


# --- blob layout ------------------------------------------------------------
def test_blob():
    blob = calib.pack_blob(0.0375, -12.5, version=1)
    check(len(blob) == 15, "blob is 15 bytes")
    check(len(blob) == calib.BLOB_SIZE, "blob size matches SelfCal::BLOB_SIZE")
    k, t0, spare, magic, ver = struct.unpack("<fffHB", blob)
    approx(k, 0.0375, 1e-7, "blob k round-trip")
    approx(t0, -12.5, 1e-6, "blob T0 round-trip")
    check(spare == 0.0, "blob spare is zero")
    check(magic == 0x5343, "blob magic is 'SC' 0x5343")
    check(ver == 1, "blob version byte honoured")
    back = calib.unpack_blob(blob)
    approx(back["k"], 0.0375, 1e-7, "unpack k")
    approx(back["t0"], -12.5, 1e-6, "unpack T0")
    bad = bytearray(blob)
    bad[12] ^= 0xFF
    try:
        calib.unpack_blob(bytes(bad))
        check(False, "bad magic must raise")
    except ValueError:
        pass
    check(calib.cal_command(0.04, 25.0) == "cal 0.04 25.00", "cal command format")


# --- CLI parsers ------------------------------------------------------------
def test_parsers():
    cs = calib.parse_calshow(
        "cal valid=yes k=0.04 T0=25.00C range=+/-80C die_temp=-40.0 off_hz=146982")
    check(cs["valid"] is True, "calshow valid")
    approx(cs["k"], 0.04, 1e-9, "calshow k")
    approx(cs["t0"], 25.0, 1e-9, "calshow T0")
    approx(cs["range_c"], 80.0, 1e-9, "calshow range")
    approx(cs["die_temp_c"], -40.0, 1e-9, "calshow die temp")
    approx(cs["off_hz"], 146982.0, 1e-9, "calshow applied offset")

    st = calib.parse_status(
        "mode=MAP distinct=3 logged=120 dropped=0 buf=0 bw=125.0(fallback) "
        "die_temp=0.0 off_hz=0 cal=no")
    check(st["fallback"] is True, "status fallback flag")
    approx(st["bw_khz"], 125.0, 1e-9, "status bw parse")
    check(st["logged"] == 120, "status logged")
    check(st["cal_valid"] is False, "status cal flag")


# --- model / sign convention ------------------------------------------------
def test_model_sign():
    # cold crystal -> LO low -> RX programmed HIGH (positive offset)
    for t in (-45.0, -20.0, 0.0, 60.0):
        check(calib.required_offset_ppm(t, 0.04, 25.0) > 0.0,
              "required compensation positive at %.0f C" % t)
        check(calib.drift_ppm(t, 0.04, 25.0) < 0.0,
              "crystal drift negative at %.0f C" % t)
    approx(calib.required_offset_ppm(-40.0, 0.04, 25.0), 169.0, 1e-6,
           "required compensation at -40 C is +169 ppm (LO high)")


# --- fit recovery -----------------------------------------------------------
def test_fit_recovers_known_k_t0():
    rng = random.Random(7)
    k_true, t0_true = 0.0385, 21.5
    temps = [-45.0, -40.0, -20.0, -5.0, 10.0, 25.0, 40.0]
    pts = [(t, calib.required_offset_ppm(t, k_true, t0_true) + rng.uniform(-0.5, 0.5))
           for t in temps]
    res = calib.fit_curve(pts)
    approx(res["k"], k_true, 0.0015, "fit recovers k from bracketed span")
    approx(res["t0"], t0_true, 1.5, "fit recovers T0 from bracketed span")
    check(res["brackets_turnover"], "bracketed span flagged identifiable")
    check(res["rms_ppm"] < 1.0, "fit residual below 1 ppm on clean data")
    check(not res["warnings"], "clean bracketed fit has no warnings: %s" % res["warnings"])


def test_fit_single_sided_warns():
    k_true, t0_true = 0.04, 22.0
    pts = [(t, calib.required_offset_ppm(t, k_true, t0_true))
           for t in (-45.0, -40.0, -30.0, -20.0)]
    res = calib.fit_curve(pts)
    check(not res["brackets_turnover"], "single-sided span not identifiable")
    check(any("unidentifiable" in w for w in res["warnings"]),
          "single-sided span warns about T0: %s" % res["warnings"])


def test_fit_t0_fixed():
    k_true = 0.04
    pts = [(t, calib.required_offset_ppm(t, k_true, 25.0) + 2.0)
           for t in (-45.0, -20.0, 0.0, 40.0)]
    res = calib.fit_curve(pts, t0_fixed=25.0)
    approx(res["k"], k_true, 0.002, "fixed-T0 fit k")
    approx(res["bias_ppm"], 2.0, 0.3, "fixed-T0 fit recovers the bias term")
    check(res["rms_ppm"] < 0.5, "fixed-T0 fit residual")


def test_fit_rejects_bad_input():
    try:
        calib.fit_curve([(0.0, 0.0), (10.0, 1.0)])
        check(False, "fit must reject < 3 points")
    except ValueError:
        pass
    res = calib.fit_curve([(0.0, 10.0), (5.0, 10.5), (10.0, 11.0)])
    check(any("span" in w for w in res["warnings"]), "narrow span warns")


# --- edge scan against a synthetic module -----------------------------------
def test_scan_edges_recovers_required():
    k_true, t0_true = 0.04, 22.0
    for temp in (-45.0, -40.0, -20.0, 0.0, 25.0, 40.0):
        dut = tb.FakeDut(k_true=k_true, t0_true=t0_true, temp_c=temp,
                         half_window_ppm=tb.HALF_WINDOW_PPM)
        res = tb.scan_edges(dut, temp, t0_offset_c=15.0, nominal_per_window=20,
                            capture_s=0.0, k_max=2.0, log=lambda *a: None)
        want = calib.required_offset_ppm(temp, k_true, t0_true)
        # 20 packets/window quantises the 50% crossing to ~1/(2*half_window/20)
        tol = max(6.0, 0.12 * want)
        approx(res["required_offset_ppm"], want, tol,
               "edge scan at %.0f C" % temp)


def test_scan_edges_needs_a_receivable_baseline():
    # a module whose drift at -45 C needs ~900 ppm of injection: unreachable
    # inside MAX_PPM, so the scan must fail loudly instead of inventing a value
    dut = tb.FakeDut(k_true=0.2, t0_true=22.0, temp_c=-45.0)
    try:
        tb.scan_edges(dut, -45.0, capture_s=0.0, log=lambda *a: None)
        check(False, "scan must fail when no reachable offset restores reception")
    except RuntimeError:
        pass


# --- reference sweep reduction ---------------------------------------------
def test_passband_reduction():
    nominal = 869_618_000.0
    drift_ppm = -81.0                      # DUT LO 81 ppm low
    half = tb.HALF_WINDOW_PPM
    steps = []
    for i in range(-60, 61):
        off_ppm = i * 2.0
        r = 1.0 if abs(off_ppm - drift_ppm) < half else 0.0
        steps.append((nominal * (1 + off_ppm / 1e6), r))
    win = tb.reduce_refsweep(steps, nominal)
    approx(win["offset_ppm"], drift_ppm, 2.5, "passband centre vs true drift")
    approx(win["required_offset_ppm"], -drift_ppm, 2.5,
           "required compensation = -drift")
    return win


def test_passband_one_sided():
    nominal = 869_618_000.0
    half = tb.HALF_WINDOW_PPM
    steps = []
    for i in range(-40, 41):                 # window opened mid-sweep
        off_ppm = i * 2.0
        steps.append((nominal * (1 + off_ppm / 1e6), 1.0 if off_ppm < 20.0 else 0.0))
    width_hz = 2 * half * nominal / 1e6
    win = tb.reduce_refsweep(steps, nominal, nominal_width_hz=width_hz)
    approx(win["offset_ppm"], 20.0 - half, 3.0, "one-sided window uses BW width")
    check(win["width_hz"] > 0, "one-sided window reports a width")


# --- lag estimator ----------------------------------------------------------
def test_lag_estimator():
    """Step stimulus: the crystal response is a 1-pole lag of the die sensor."""
    dt = 5.0
    n = 240
    tau_true = 45.0
    temp = [-30.0 if i * dt < 400.0 else 25.0 for i in range(n)]
    filt = [temp[0]]
    for i in range(1, n):
        a = 1.0 - math.exp(-dt / tau_true)
        filt.append(filt[-1] + (temp[i] - filt[-1]) * a)
    off = [calib.required_offset_ppm(f, 0.04, 25.0) for f in filt]
    res = calib.fit_lag([i * dt for i in range(n)], temp, off, 0.04, 25.0,
                        max_lag_s=120.0)
    check(res["ok"], "lag fit ran: %s" % res.get("notes"))
    approx(res["tau_s"], tau_true, 12.0, "lag fit recovers the crystal tau")
    check(res["rms_ppm"] < res["rms_no_lag_ppm"],
          "lag model beats the no-lag model (%.2f < %.2f)"
          % (res["rms_ppm"], res["rms_no_lag_ppm"]))
    check(res["lag_identifiable"] is True, "step stimulus is identifiable")
    approx(res["lag_s"], tau_true, 12.0, "step stimulus reports the lag")


def _band_ramp(dt, t_lo, t_hi, tau, inj_ppm, k=0.04, t0=25.0, half=35.9):
    """Crystal-lagged sweep + a reception flag. The flag is a BAND in crystal
    temperature space, the die temp is what the sensor reports, so the band edge
    lands at a different die temperature on the heating and the cooling sweep."""
    n = max(8, int(round(abs(t_hi - t_lo) / max(1e-9, abs(t_hi - t_lo)) * (600.0 / dt))))
    temp = [t_lo + (t_hi - t_lo) * i / (n - 1) for i in range(n)]
    crystal = [temp[0]]
    a = 1.0 - math.exp(-dt / tau)
    for i in range(1, n):
        crystal.append(crystal[-1] + (temp[i] - crystal[-1]) * a)
    ratio = [1.0 if abs(calib.required_offset_ppm(c, k, t0) - inj_ppm) < half else 0.0
             for c in crystal]
    return [i * dt for i in range(n)], temp, ratio


def _ramp(dt, n, tau, t_lo, t_hi, ramp_s):
    """Synthetic die temp ramp + the crystal response (1-pole lag of the die)."""
    temp = [t_lo + (t_hi - t_lo) * min(1.0, i * dt / ramp_s) for i in range(n)]
    filt = [temp[0]]
    for i in range(1, n):
        a = 1.0 - math.exp(-dt / tau)
        filt.append(filt[-1] + (temp[i] - filt[-1]) * a)
    off = [calib.required_offset_ppm(f, 0.04, 25.0) for f in filt]
    return temp, off


def test_lag_slow_ramp_resolves_tau():
    """A full freezer/chamber ramp (55 K over 10 min) is a valid stimulus: the
    residual fit resolves the time constant even though the derivative
    cross-correlation that was tried first degenerates on it (it reported the
    edge of its own search window). Documented so nobody re-adds the
    correlation gate."""
    dt = 5.0
    n = 240
    tau_true = 45.0
    temp, off = _ramp(dt, n, tau_true, -30.0, 25.0, 600.0)
    res = calib.fit_lag([i * dt for i in range(n)], temp, off, 0.04, 25.0,
                        max_lag_s=120.0)
    check(res["ok"], "slow ramp fit ran: %s" % res.get("notes"))
    approx(res["tau_s"], tau_true, 12.0, "slow ramp recovers the crystal tau")
    check(res["lag_identifiable"] is True,
          "slow ramp over 55 K is an identifiable stimulus")
    approx(res["lag_s"], tau_true, 12.0, "slow ramp reports the lag")


def test_lag_requires_excitation():
    """Too little thermal excitation -> NO lag number, and the operator is told
    what to do about it. A lag cannot be measured from a flat log or from a few
    kelvin of drift, and reporting one would be a fabricated number."""
    dt = 5.0
    n = 240
    temp, off = _ramp(dt, n, 45.0, 20.0, 23.0, 600.0)     # 3 K span
    res = calib.fit_lag([i * dt for i in range(n)], temp, off, 0.04, 25.0,
                        max_lag_s=120.0)
    check(res["lag_identifiable"] is False,
          "3 K span reports no identifiable lag (span %.1f C)" % res["excitation_span_c"])
    check(res["lag_s"] is None, "small span does not emit a spurious lag number")
    check(any("excitation" in x for x in res["notes"]),
          "small span tells the operator to excite the board: %s" % res["notes"])

    flat = [22.0] * n
    off_flat = [calib.required_offset_ppm(22.0, 0.04, 25.0)] * n
    res = calib.fit_lag([i * dt for i in range(n)], flat, off_flat, 0.04, 25.0,
                        max_lag_s=120.0)
    check(res["lag_identifiable"] is False, "flat log reports no lag")
    check(res["lag_s"] is None, "flat log does not invent a lag")
    check(any("excitation" in x for x in res["notes"]),
          "flat log tells the operator to excite the board")


def test_lag_rejects_short_input():
    res = calib.fit_lag([0.0, 1.0], [1.0, 2.0], [0.0, 1.0], 0.04, 25.0)
    check(res["ok"] is False, "lag fit rejects short input")


def test_edge_hysteresis_recovers_tau():
    """The bench lag method: sweep the module up and down through the reception
    edge of a FIXED injected offset. The die-temperature gap between the two
    crossings is tau*(rate_up+rate_down), so the time constant falls out with no
    soak, no k/T0 fit and no model of the drift - only a reception flag."""
    dt = 5.0
    inj = calib.required_offset_ppm(-10.0, 0.04, 25.0)
    up = _band_ramp(dt, -40.0, 25.0, 45.0, inj)
    down = _band_ramp(dt, 25.0, -40.0, 45.0, inj)
    res = calib.fit_edge_hysteresis(up, down)
    check(res["ok"], "hysteresis fit ran: %s" % res.get("notes"))
    approx(res["tau_s"], 45.0, 10.0, "hysteresis recovers the crystal tau")
    check(res["lag_identifiable"] is True, "hysteresis lag is identifiable")
    check(res["edge_up_c"] > res["edge_down_c"],
          "the heating edge sits at a WARMER die temp than the cooling edge")
    # A slow sweep is still measurable: the method scales with the ramp rate.
    slow_up = _band_ramp(dt, -40.0, 25.0, 45.0, inj)
    res_slow = calib.fit_edge_hysteresis(slow_up, down)
    check(res_slow["ok"], "hysteresis fit runs on a slow sweep")


def test_edge_hysteresis_refuses_bad_input():
    """No reception edge, identical sweeps, or a standstill must NOT produce a
    tau: this is the number that gets written into SelfCal, so a wrong one is
    worse than none."""
    inj = calib.required_offset_ppm(-10.0, 0.04, 25.0)
    up = _band_ramp(5.0, -40.0, 25.0, 45.0, inj)
    down = _band_ramp(5.0, 25.0, -40.0, 45.0, inj)

    # injected offset far outside the capture window at every temperature: no edge
    blind = _band_ramp(5.0, -40.0, 25.0, 45.0, 290.0)
    res = calib.fit_edge_hysteresis(blind, down)
    check(res["ok"] is False, "no reception edge in one ramp -> no tau")
    check(any("edge" in n for n in res.get("notes", [])),
          "the refusal names the missing edge: %s" % res.get("notes"))

    # the same ramp handed in twice: the "down" pass then picks up the WARM edge
    # of the band, i.e. a different physical edge, and tau comes out negative
    res = calib.fit_edge_hysteresis(up, up)
    check(res["ok"] is False, "identical sweeps -> no usable lag")
    check(res["lag_s"] is None, "identical sweeps report no lag number")
    check(any("INVERTED" in n for n in res.get("notes", [])),
          "the inverted-edge case is named: %s" % res.get("notes"))

    # too few samples
    res = calib.fit_edge_hysteresis(([0.0, 1.0], [1.0, 2.0], [0.0, 1.0]),
                                    (down[0][:4], down[1][:4], down[2][:4]))
    check(res["ok"] is False, "short ramp pair rejected")


def test_ramp_hyst_cli_sim_roundtrip():
    """End-to-end software run of the bench lag protocol: the same subprocess
    commands the operator will run, on synthetic data with a known tau."""
    import contextlib
    import io
    d = tempfile.mkdtemp(prefix="pm_bench_")
    up_csv = os.path.join(d, "up.csv")
    dn_csv = os.path.join(d, "down.csv")
    for direction, out in (("up", up_csv), ("down", dn_csv)):
        with contextlib.redirect_stdout(io.StringIO()):
            rc = tb.main(["ramp", "--simulate", "--direction", direction,
                          "--duration", "600", "--interval", "5", "--sim-tau", "45",
                          "--out", out])
        check(rc == 0, "ramp --simulate %s generated a log" % direction)
    rows = list(csv.DictReader(open(up_csv)))
    check(len(rows) > 100, "ramp log has samples (%d)" % len(rows))
    check("ratio" in rows[0] and "die_temp_c" in rows[0],
          "ramp log columns: %s" % sorted(rows[0].keys()))
    with contextlib.redirect_stdout(io.StringIO()):
        rc = tb.main(["hyst", "--up", up_csv, "--down", dn_csv])
    check(rc == 0, "hyst accepted the simulated ramp pair")


def main():
    for fn in (test_blob, test_parsers, test_model_sign,
               test_fit_recovers_known_k_t0, test_fit_single_sided_warns,
               test_fit_t0_fixed, test_fit_rejects_bad_input,
               test_scan_edges_recovers_required,
               test_scan_edges_needs_a_receivable_baseline,
               test_passband_reduction, test_passband_one_sided,
               test_lag_estimator, test_lag_slow_ramp_resolves_tau,
               test_lag_requires_excitation, test_lag_rejects_short_input,
               test_edge_hysteresis_recovers_tau,
               test_edge_hysteresis_refuses_bad_input,
               test_ramp_hyst_cli_sim_roundtrip):
        before = len(FAILS)
        try:
            fn()
        except Exception as exc:                     # noqa: BLE001
            FAILS.append("%s raised %r" % (fn.__name__, exc))
            print("FAIL: %s raised %r" % (fn.__name__, exc))
        status = "ok" if len(FAILS) == before else "FAILED"
        print("%-45s %s" % (fn.__name__, status))
    if FAILS:
        print("\n%d BENCH-KIT TEST(S) FAILED" % len(FAILS))
        return 1
    print("\nALL BENCH-KIT TESTS PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
