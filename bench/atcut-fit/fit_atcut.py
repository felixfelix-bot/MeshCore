#!/usr/bin/env python3
"""AT-cut thermal model fit: k, T0 from freezer-sweep soak dwell points.

Fleet task: fit offset_ppm = -k*(T - T0)^2 per LR2021 module and emit the exact
serial-CLI line the passive_mapper firmware accepts.

STATUS (2026-09-12): the parent bench task guard-tripped twice (no external
frequency reference, no chamber) and produced NO CSV. This tool is a turnkey
harness: the moment a real soak CSV exists, run it and the numbers + `cal`
command come out with zero re-derivation. It will REFUSE to emit a command from
data that does not support a clean parabola. Nothing here fabricates
measurements; --self-test uses synthetic data only and says so.

Input CSV (soak/dwell points only — one row per soaked setpoint, or the dwell
rows of a full session CSV; a `phase`/`kind` column, when present, is filtered
to dwell/soak rows):
    die_temp_c   LR2021 die temp at soak, C (getRadioTemperatureC, XOSC source)
    offset_ppm   externally measured carrier frequency error vs reference, ppm
                 (negative = carrier low; this is the crystal DRIFT, the same
                 sign convention as the model, not the applied compensation)
    [setpoint_c] optional chamber setpoint, recorded as-is
    [phase]      optional; rows not containing dwell/soak are skipped
    [...]        any other columns ignored

Method (per task):
 1. OLS quadratic offset_ppm = a*T^2 + b*T + c  ->  k = -a, T0 = -b/(2a).
 2. Sanity gates, each reported pass/warn/fail:
      n >= 4 points; T span >= 20 C; parabola opens downward (a < 0, k > 0);
      k in plausible AT-cut band (0.005..0.15 ppm/C^2, LR2021 class ~0.03..0.04);
      T0 in a plausible room-temperature region (warn outside 15..40 C);
      T0 identifiability: swept range must bracket T0 (single-sided sweep =>
      many (k, T0) fit equally well -> REFUSE);
      c consistent with -k*T0^2 (report the bias delta vs residual scatter);
      R^2, per-point residuals, leave-one-out stability of (k, T0).
 3. Emit the verbatim command `cal %.6g %.2f` — format verified against a
    Python port of the firmware's own parseFloat() (examples/passive_mapper/
    MyMesh.cpp, felixfelix-bot/MeshCore feat/passive-mapper @ 3fdfbc8e), which
    accepts only [-+]?digits[.digits] (leading digit REQUIRED, no exponent) and
    enforces k >= 0. The firmware echoes `cal k=%.6g T0=%.2fC -> persisted`.

Usage:
    python3 fit_atcut.py --csv soak.csv [--json out.json] [--module ID]
    python3 fit_atcut.py --self-test
"""

import argparse
import csv
import json
import sys

try:
    import numpy as np
except ImportError:  # pragma: no cover
    np = None

# ---------------------------------------------------------------- constants

MIN_POINTS = 4          # parent-task acceptance: >= 4 soaked setpoints
MIN_SPAN_C = 20.0       # below this, (k, T0) are poorly conditioned
K_PLAUSIBLE = (0.005, 0.15)   # ppm/C^2; LR2021-class AT-cut ~0.03..0.04
T0_ROOM_BAND_C = (15.0, 40.0)  # plausible turnover region (warn outside)
T0_MAX_EXTRAPOLATION_C = 15.0  # vertex far outside sweep => refuse
R2_MIN = 0.95
LOO_K_TOL = 0.010       # ppm/C^2 max LOO swing to call k stable
LOO_T0_TOL = 5.0        # C max LOO swing to call T0 stable

TEMP_ALIASES = ("die_temp_c", "die_temp", "die_c", "temp_c", "T", "t_die")
PPM_ALIASES = ("offset_ppm", "freq_err_ppm", "ppm_err", "drift_ppm", "ppm",
               "cfo_ppm")
PHASE_ALIASES = ("phase", "kind", "segment", "stage")
SETPOINT_ALIASES = ("setpoint_c", "setpoint", "target_c")


def load_csv(path):
    """Return [(setpoint_or_None, T_c, offset_ppm, phase), ...] for soak rows."""
    with open(path, newline="") as fh:
        rdr = csv.DictReader(fh)
        header = [h.strip() for h in (rdr.fieldnames or [])]

        def find(aliases):
            for a in aliases:
                if a in header:
                    return a
                # case-insensitive fallback
                for h in header:
                    if h.lower() == a.lower():
                        return h
            return None

        t_col = find(TEMP_ALIASES)
        p_col = find(PPM_ALIASES)
        ph_col = find(PHASE_ALIASES)
        sp_col = find(SETPOINT_ALIASES)
        if not t_col or not p_col:
            raise SystemExit(
                f"CSV error: need a die-temp column (one of {TEMP_ALIASES}) and "
                f"a ppm column (one of {PPM_ALIASES}); header was {header}")

        pts = []
        for row in rdr:
            if row.get(t_col) is None or row.get(p_col) is None:
                continue
            try:
                t = float(str(row[t_col]).strip())
                ppm = float(str(row[p_col]).strip())
            except ValueError:
                continue  # annotation / malformed row
            ph = str(row.get(ph_col, "") or "").strip().lower()
            if ph and not any(k in ph for k in ("dwell", "soak")):
                continue  # full-session CSV: keep only soak rows
            sp = None
            if sp_col:
                try:
                    sp = float(str(row[sp_col]).strip())
                except (ValueError, TypeError):
                    sp = None
            pts.append((sp, t, ppm, ph))
    if not pts:
        raise SystemExit("CSV error: no usable soak rows found")
    return pts


# ------------------------------------------------- firmware parseFloat port
# Verbatim port of the parser in MyMesh::handleCommand (feat/passive-mapper @
# 3fdfbc8e): optional spaces/tabs, optional sign, REQUIRED leading digits,
# optional fractional part. No exponent, no bare ".5". Returns (value, rest)
# or None. The emitted cal line is round-tripped through this before we print
# it — "verifiably consistent with the firmware's CLI parser".

def fw_parse_float(s):
    i = 0
    while i < len(s) and s[i] in " \t":
        i += 1
    neg = False
    if i < len(s) and s[i] in "-+":
        neg = s[i] == "-"
        i += 1
    if i >= len(s) or not s[i].isdigit():
        return None
    v = 0.0
    while i < len(s) and s[i].isdigit():
        v = v * 10.0 + float(s[i])
        i += 1
    if i < len(s) and s[i] == ".":
        i += 1
        scale = 0.1
        while i < len(s) and s[i].isdigit():
            v += float(s[i]) * scale
            scale *= 0.1
            i += 1
    return (-v if neg else v), s[i:]


def cal_command(k, t0):
    """Exact format: firmware reply echoes k=%.6g T0=%.2f; the fork's own bench
    kit (bench/calib.py::cal_command) emits `cal %.6g %.2f`."""
    return "cal %.6g %.2f" % (k, t0)


def verify_command(cmd, k, t0):
    """Round-trip the command through the firmware parser; also enforce the
    CLI's k >= 0 gate. Tolerances are the half-ULP of the rendered formats
    (%.6g for k, %.2f for T0): the firmware stores exactly the rounded values
    this command encodes. Returns (ok, detail)."""
    import math
    if not cmd.startswith("cal "):
        return False, "not a cal command"
    r1 = fw_parse_float(cmd[4:])
    if r1 is None:
        return False, "k token rejected by firmware parseFloat grammar"
    k2, rest = r1
    r2 = fw_parse_float(rest)
    if r2 is None:
        return False, "T0 token rejected by firmware parseFloat grammar"
    t2, tail = r2
    if tail.strip():
        return False, "trailing garbage after T0: %r" % tail
    if k2 < 0.0:
        return False, "firmware CLI rejects k < 0"
    # %.6g rounding: half-ULP at the 6th significant digit
    k_tol = 0.6 * 10.0 ** (math.floor(math.log10(abs(k))) - 5) if k else 1e-12
    if abs(k2 - k) > k_tol:
        return False, "k round-trip mismatch: %r -> %r" % (k, k2)
    if abs(t2 - t0) > 0.0051:  # %.2f rounding: half-ULP of 0.01
        return False, "T0 round-trip mismatch: %r -> %r" % (t0, t2)
    return True, (f"parses to k={k2!r} T0={t2!r}; "
                  "format matches the firmware's %.6g/%.2f echo")


def pack_blob(k, t0, version=0):
    """15-byte /selfcal.dat blob: 2x f32 LE (k, T0) + spare f32 + u16 0x5343 +
    u8 version (SelfCal.h @ 3fdfbc8e). For rebuild-after-reflash only; the cal
    command itself is authoritative. Version defaults to 0 because the
    firmware's _ver starts at 0 and setVersion() is never called anywhere in
    examples/passive_mapper @ 3fdfbc8e (CAL-CLI-SPEC.md §6; harness-verified
    firmware-written blob ends ... 43 53 00)."""
    import struct
    return struct.pack("<fffHB", k, t0, 0.0, 0x5343, version)


# -------------------------------------------------------------------- fit

def fit_quadratic(ts, ys):
    """OLS y = a*t^2 + b*t + c. Returns (a, b, c) and per-point residuals."""
    if np is not None:
        a, b, c = np.polyfit(np.array(ts), np.array(ys), 2)
        resid = [y - (a * t * t + b * t + c) for t, y in zip(ts, ys)]
        return float(a), float(b), float(c), resid
    # pure-python normal equations (3x3 solve)
    n = float(len(ts))
    s = [0.0] * 6  # sums of t^0..t^4
    sy = [0.0] * 3  # sums of y*t^0..t^2
    for t, y in zip(ts, ys):
        p = 1.0
        for i in range(5):
            s[i] += p
            p *= t
        s[5] += p
        p = 1.0
        for i in range(3):
            sy[i] += y * p
            p *= t

    def det3(m):
        return (m[0][0] * (m[1][1] * m[2][2] - m[1][2] * m[2][1])
                - m[0][1] * (m[1][0] * m[2][2] - m[1][2] * m[2][0])
                + m[0][2] * (m[1][0] * m[2][1] - m[1][1] * m[2][0]))

    m = [[s[4], s[3], s[2]], [s[3], s[2], s[1]], [s[2], s[1], n]]
    rhs = [sy[2], sy[1], sy[0]]
    d = det3(m)
    if abs(d) < 1e-30:
        raise SystemExit("fit error: singular normal equations (duplicate T?)")
    a = b = c = 0.0
    for j in range(3):
        mj = [row[:] for row in m]
        for i in range(3):
            mj[i][j] = rhs[i]
        val = det3(mj) / d
        if j == 0:
            a = val
        elif j == 1:
            b = val
        else:
            c = val
    resid = [y - (a * t * t + b * t + c) for t, y in zip(ts, ys)]
    return a, b, c, resid


def fit_and_check(pts):
    ts = [p[1] for p in pts]
    ys = [p[2] for p in pts]
    n = len(pts)
    span = max(ts) - min(ts)
    a, b, c, resid = fit_quadratic(ts, ys)
    ss_res = sum(r * r for r in resid)
    ybar = sum(ys) / n
    ss_tot = sum((y - ybar) ** 2 for y in ys)
    r2 = 1.0 - ss_res / ss_tot if ss_tot > 0 else float("nan")
    rms = (ss_res / n) ** 0.5 if n else float("nan")

    if abs(a) < 1e-12:
        k = float("nan")
        t0 = float("nan")
    else:
        k = -a
        t0 = -b / (2.0 * a)
    bias_delta = (c - (-k * t0 * t0)) if abs(a) > 1e-12 else float("nan")

    # leave-one-out stability
    loo_k, loo_t0 = [], []
    if n >= 5:
        for i in range(n):
            ts2 = [t for j, t in enumerate(ts) if j != i]
            ys2 = [y for j, y in enumerate(ys) if j != i]
            try:
                a2, b2, _, _ = fit_quadratic(ts2, ys2)
                if abs(a2) > 1e-12 and a2 < 0:
                    loo_k.append(-a2)
                    loo_t0.append(-b2 / (2.0 * a2))
            except SystemExit:
                pass

    checks = []

    def chk(name, ok, warn_msg=None, fail_msg=None):
        if ok:
            checks.append((name, "PASS", ""))
        elif fail_msg is not None:
            checks.append((name, "FAIL", fail_msg))
        else:
            checks.append((name, "WARN", warn_msg or ""))

    chk("n_points >= %d" % MIN_POINTS, n >= MIN_POINTS,
        None, "only %d soak points" % n)
    chk("T span >= %.0f C" % MIN_SPAN_C, span >= MIN_SPAN_C,
        "span %.1f C: (k,T0) poorly conditioned" % span,
        "span %.1f C is too narrow to identify (k,T0)" % span)
    down = abs(a) > 1e-12 and a < 0
    chk("parabola opens downward (a<0 => k>0)", down,
        None, "a=%.6g: curvature is UP in offset; AT-cut model does not hold "
              "(k=%.6g <= 0); refusing to force a fit" % (a, k))
    chk("k in %.3f..%.3f ppm/C^2" % K_PLAUSIBLE,
        abs(a) > 1e-12 and K_PLAUSIBLE[0] <= k <= K_PLAUSIBLE[1],
        "k=%.6g ppm/C^2 is outside the typical AT-cut band" % k, None)
    if abs(a) > 1e-12:
        chk("T0 in plausible room band %s C" % (T0_ROOM_BAND_C,),
            T0_ROOM_BAND_C[0] <= t0 <= T0_ROOM_BAND_C[1],
            "T0=%.2f C is outside %s; AT-cut turnovers are usually 20-30 C"
            % (t0, (T0_ROOM_BAND_C,)), None)
        outside = max(min(ts) - t0, t0 - max(ts), 0.0)
        if outside <= 2.0:
            # vertex essentially at the sweep edge: curvature still identified
            chk("T0 bracketed by sweep / not extrapolated", True)
        else:
            warn_brk = ("T0=%.2f C is %.1f C outside the swept range [%g..%g] C "
                        "— single-sided sweep: many (k,T0) pairs fit equally "
                        "well" % (t0, outside, min(ts), max(ts)))
            fail_brk = (warn_brk + " — vertex is pure extrapolation, (k,T0) "
                        "not identifiable; refusing")
            chk("T0 bracketed by sweep / not extrapolated", False,
                warn_brk if outside <= T0_MAX_EXTRAPOLATION_C else None,
                fail_brk if outside > T0_MAX_EXTRAPOLATION_C else None)
        chk("c consistent with -k*T0^2",
            abs(bias_delta) <= 5.0,
            "bias delta %+.2f ppm (unmodelled reference/initial crystal "
            "tolerance; the cal cannot correct a static offset — record it, "
            "consider cap trim if > ~10 ppm)" % bias_delta,
            None)
        chk("R^2 >= %.2f" % R2_MIN, r2 >= R2_MIN, None,
            "R^2=%.4f: residuals dominate — data does not support a clean "
            "parabola; refusing to force a fit" % r2)
    if loo_k:
        k_swing = max(loo_k) - min(loo_k)
        t0_swing = max(loo_t0) - min(loo_t0)
        chk("leave-one-out k stable < %.3f" % LOO_K_TOL, k_swing < LOO_K_TOL,
            None, "LOO k swings %.4f ppm/C^2 (an outlier owns the curvature)"
            % k_swing)
        chk("leave-one-out T0 stable < %.0f C" % LOO_T0_TOL, t0_swing < LOO_T0_TOL,
            None, "LOO T0 swings %.1f C (an outlier owns the vertex)" % t0_swing)

    ok = all(s != "FAIL" for _, s, _ in checks)
    warns = [m for _, s, m in checks if s == "WARN" and m]

    return {
        "n_points": n, "t_min_c": min(ts), "t_max_c": max(ts), "span_c": span,
        "a": a, "b": b, "c": c, "k": k, "t0": t0, "bias_delta_ppm": bias_delta,
        "rms_ppm": rms, "r2": r2, "residuals_ppm": resid,
        "loo_k_swing": (max(loo_k) - min(loo_k)) if loo_k else None,
        "loo_t0_swing": (max(loo_t0) - min(loo_t0)) if loo_t0 else None,
        "checks": checks, "ok": ok, "warnings": warns,
        "points": pts,
    }


# ------------------------------------------------------------------ report

def print_report(res, module_id=None):
    pts = res["points"]
    print("AT-CUT FIT — soak dwell points (T = LR2021 die temp, XOSC source)")
    print("=" * 66)
    for sp, t, ppm, _ in pts:
        sp_s = "%+g" % sp if sp is not None else "  -"
        print("  setpoint %-5s  T=%7.2f C  offset=%+8.3f ppm" % (sp_s, t, ppm))
    print("-" * 66)
    print("quadratic OLS: offset = a*T^2 + b*T + c")
    print("  a = %+.8g ppm/C^2   (k = -a = %.6g ppm/C^2)" % (res["a"], res["k"]))
    print("  b = %+.8g ppm/C" % res["b"])
    print("  c = %+.8g ppm       (ideal -k*T0^2 = %+.3f, delta %+.3f ppm)"
          % (res["c"], -res["k"] * res["t0"] ** 2, res["bias_delta_ppm"]))
    print("  T0 = -b/(2a) = %.2f C" % res["t0"])
    print("  R^2 = %.4f   rms residual = %.3f ppm   span = %.1f C"
          % (res["r2"], res["rms_ppm"], res["span_c"]))
    print("per-point residuals:")
    for (sp, t, ppm, _), r in zip(pts, res["residuals_ppm"]):
        print("  T=%7.2f C  meas=%+8.3f  fit=%+8.3f  resid=%+7.3f ppm"
              % (t, ppm, ppm - r, r))
    if res["loo_k_swing"] is not None:
        print("leave-one-out: k swing %.5f ppm/C^2, T0 swing %.2f C"
              % (res["loo_k_swing"], res["loo_t0_swing"]))
    print("-" * 66)
    for name, status, msg in res["checks"]:
        line = "  [%s] %s" % (status, name)
        if msg:
            line += " — " + msg
        print(line)
    print("-" * 66)
    if res["ok"]:
        cmd = cal_command(res["k"], res["t0"])
        vok, vdetail = verify_command(cmd, res["k"], res["t0"])
        print("CAL COMMAND (%s):" % (module_id or "module id REQUIRED — "
              "calibration is per-module, record board serial/markings"))
        print("    " + cmd)
        print("  firmware-parser verification: %s" % ("OK — " + vdetail if vok
                                                      else "FAILED — " + vdetail))
        print("  expected firmware reply: cal k=%.6g T0=%.2fC -> persisted (valid=yes)"
              % (res["k"], res["t0"]))
        print("  blob (rebuild /selfcal.dat after reflash): %s"
              % pack_blob(res["k"], res["t0"]).hex())
    else:
        print("VERDICT: DO NOT ISSUE cal — data does not support a clean "
              "parabola (see FAIL checks above). No command emitted.")
    for w in res["warnings"]:
        print("WARNING: %s" % w)


# ---------------------------------------------------------------- self-test

def _self_test():
    import random
    print("SELF-TEST — synthetic data only; NOT a measurement of any hardware")
    print("=" * 66)
    rng = random.Random(20260912)
    all_ok = True

    def synth(k, t0, bias, noise, setpoints):
        pts = []
        for sp in setpoints:
            t = sp + rng.uniform(-0.2, 0.2)   # die temp ~ setpoint at soak
            y = -k * (t - t0) ** 2 + bias + rng.gauss(0, noise)
            pts.append((sp, t, y, "dwell"))
        return pts

    # 1. clean bracketed sweep: must recover k/T0 and emit a verified command
    K, T0, BIAS = 0.034, 25.0, -0.8
    pts = synth(K, T0, BIAS, 0.10, [25, 5, 0, -20, -40])
    res = fit_and_check(pts)
    print_report(res, "SYNTH-1")
    ok1 = (res["ok"] and abs(res["k"] - K) < 0.004 and abs(res["t0"] - T0) < 1.5
           and verify_command(cal_command(res["k"], res["t0"]),
                              res["k"], res["t0"])[0])
    print("case1 clean bracketed sweep: %s (k_err=%.5f, T0_err=%.2f C)"
          % ("PASS" if ok1 else "FAIL", res["k"] - K, res["t0"] - T0))
    all_ok &= ok1

    # 2. wrong curvature (upward): must REFUSE, no command
    pts = [(25, 25.1, +2.0, "dwell"), (5, 5.0, +8.0, "dwell"),
           (-20, -20.2, +18.0, "dwell"), (-40, -40.1, +34.0, "dwell")]
    res = fit_and_check(pts)
    ok2 = not res["ok"] and res["k"] <= 0
    print("case2 upward curvature: %s (k=%.4g must be <=0; FAIL gates fired: %s)"
          % ("PASS" if ok2 else "FAIL", res["k"],
             [n for n, s, _ in res["checks"] if s == "FAIL"]))
    all_ok &= ok2

    # 3. single-sided sweep (all points below T0, vertex far outside): must refuse
    pts = synth(K, 25.0, 0.0, 0.05, [-5, -15, -25, -35])
    res = fit_and_check(pts)
    ok3 = not res["ok"]
    print("case3 single-sided sweep: %s (T0=%.2f C extrapolated; FAIL gates: %s)"
          % ("PASS" if ok3 else "FAIL", res["t0"],
             [n for n, s, _ in res["checks"] if s == "FAIL"]))
    all_ok &= ok3

    # 4. too few points: must refuse
    pts = synth(K, T0, 0.0, 0.05, [25, -20, -40])
    res = fit_and_check(pts)
    ok4 = not res["ok"]
    print("case4 n=3 points: %s (FAIL gates: %s)"
          % ("PASS" if ok4 else "FAIL",
             [n for n, s, _ in res["checks"] if s == "FAIL"]))
    all_ok &= ok4

    # 5. firmware parser round-trip grammar (port vs known quirks)
    r = fw_parse_float("0.034")
    r2 = fw_parse_float("  +25.13")
    r3 = fw_parse_float("25.")
    r4 = fw_parse_float("1e-2")

    def close(a, b, tol=1e-9):
        return a is not None and abs(a - b) <= tol

    quirk_ok = (fw_parse_float(".5") is None          # bare .5 REJECTED
                and r4 is not None and close(r4[0], 1.0) and r4[1] == "e-2"
                # ^ exponent NOT part of the grammar: parses as 1, leaves
                #   'e-2' as trailing garbage (the T0 parse would then fail)
                and close(r and r[0], 0.034)
                and close(r2 and r2[0], 25.13)
                and close(r3 and r3[0], 25.0))  # trailing dot ok
                # note: digit-accumulation float math (like the firmware's
                # parseFloat) differs from literals by ~1e-16, hence close()
    print("case5 firmware parseFloat quirks: %s" % ("PASS" if quirk_ok else "FAIL"))
    all_ok &= quirk_ok

    # 6. pure-Python normal-equations path must agree with numpy polyfit
    if np is not None:
        ts = [p[1] for p in pts]
        ys = [p[2] for p in pts]
        a_np, b_np, c_np, _ = fit_quadratic(ts, ys)
        global_np = globals()["np"]
        globals()["np"] = None          # force the fallback solver
        try:
            a_py, b_py, c_py, _ = fit_quadratic(ts, ys)
        finally:
            globals()["np"] = global_np
        ok6 = (abs(a_np - a_py) < 1e-9 and abs(b_np - b_py) < 1e-7
               and abs(c_np - c_py) < 1e-6)
        print("case6 pure-python fallback == numpy polyfit: %s "
              "(dPy a=%.2e b=%.2e c=%.2e)"
              % ("PASS" if ok6 else "FAIL", a_np - a_py, b_np - b_py, c_np - c_py))
        all_ok &= ok6

    print("SELF-TEST " + ("PASS" if all_ok else "FAIL"))
    return 0 if all_ok else 1


# -------------------------------------------------------------------- main

def main():
    ap = argparse.ArgumentParser(
        description=(__doc__ or "AT-cut k/T0 fit").splitlines()[0])
    ap.add_argument("--csv", help="soak CSV (die_temp_c, offset_ppm, ...)")
    ap.add_argument("--json", help="optional JSON output path")
    ap.add_argument("--module", help="module ID / board serial (per-module cal)")
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()

    if args.self_test:
        sys.exit(_self_test())
    if not args.csv:
        ap.error("--csv required (or --self-test)")

    pts = load_csv(args.csv)
    res = fit_and_check(pts)
    print_report(res, args.module)
    if args.json:
        slim = {k: v for k, v in res.items() if k not in ("points", "checks")}
        slim["points"] = [(sp, t, p) for sp, t, p, _ in res["points"]]
        slim["checks"] = res["checks"]
        with open(args.json, "w") as fh:
            json.dump(slim, fh, indent=2)
        print("\nJSON written: %s" % args.json)
    return 0 if res["ok"] else 1


if __name__ == "__main__":
    sys.exit(main() or 0)
