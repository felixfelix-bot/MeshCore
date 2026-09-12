#!/usr/bin/env python3
"""Thermal hysteresis analysis: cooling-vs-warming die-temp gap at matched
frequency-error levels — independent cross-check on die-vs-crystal lag.

Fleet task (sibling of bench/thermal-lag): quantify the die-temperature
difference between cooling and warming ramps at matched ppm-error levels.
If the die-temp sensor (XOSC source) leads the crystal by a lag tau, then at
matched ppm (matched crystal temperature) the die reads HIGH on warming and
LOW on cooling:

    T_die_warming(L) - T_die_cooling(L) = tau * (r_warm + r_cool)

where r_* are the ramp die-temp slew rates.  Hence

    tau_hyst(L) = dT(L) / (r_warm + r_cool)

is a direct, time-domain-free estimate of the die-vs-crystal lag, comparable
to the sibling's cross-correlation / loop-area delay fit.

Input CSV columns (header required; same aliases as analyze_thermal_lag.py):
    timestamp_s   relative or absolute seconds (monotonic)
    phase         optional: 'dwell', 'cooling', 'warming'; auto-detected
                  from die-temp slope if absent
    die_temp_c    LR2021 die temperature, getRadioTemperatureC (XOSC source)
    ppm_err       externally measured carrier frequency error vs reference, ppm
    fallback      optional, ignored (recorded as-is)

Method (mirrors the sibling task's conventions so results compare cleanly):
 1. Ramps split by phase labels (or auto-detected monotonic die-temp runs,
    >=120 s span, >=3 C range, >=20 rows).
 2. Resampled onto a common uniform time base: linear interpolation at
    dt = median sample interval of the whole series (the interval and method
    are stated in the output).
 3. Parametric curve freq_error_ppm vs die_temp per direction (time is the
    parameter); ppm levels (default 7, task allows 5-10) placed on the
    interior 80% of the two directions' ppm-range overlap (sibling margin).
 4. Per level: die temp at the level crossing on each direction's pooled
    curve, found by TIME-ORDERED bracketing + linear interpolation, taking
    the median crossing (robust to noise-triggered multiple crossings).
    Hysteresis dT = T_warm - T_cool.  Every level is reported; a level with
    no bracketed crossing on a direction is printed UNCOVERED, never dropped.
 5. Equivalent seconds via each ramp's average die-temp slew rate (|OLS
    slope| of die temp vs time over the ramp, per sibling convention):
    dt_warm = dT / r_warm, dt_cool = dT / r_cool, and the branch-agnostic
    lag tau_hyst = dT / (r_warm + r_cool)  (~2x the single-ramp xcorr lag
    when the slews are equal — see module docstring above).
 6. Optional --k/--t0 (sibling atcut-fit deliverable): each ppm level is
    also expressed as an effective crystal temperature via
    offset_ppm = -k*(T - T0)^2, sweep branch below T0:
    T_xtal = T0 - sqrt((ppm - offset)/k), static offset from dwell rows.
    The method stands without them.

SELF-TEST output is synthetic pipeline validation only and is never a
measurement of any hardware.

Usage:
    python3 hysteresis_fit.py --csv ramp_session.csv [--json out.json]
        [--k 0.034] [--t0 25.0] [--n-levels 7]
    python3 hysteresis_fit.py --self-test
"""

import argparse
import csv
import json
import math
import sys

import numpy as np

# ---------------------------------------------------------------- loading
# identical column contract/aliases as the sibling analyze_thermal_lag.py

DEFAULT_COLS = {
    "timestamp_s": ("timestamp_s", "timestamp", "time_s", "t_s", "time"),
    "phase": ("phase", "segment", "stage", "state"),
    "die_temp_c": ("die_temp_c", "die_temp", "die_c", "temp_c"),
    "ppm_err": ("ppm_err", "ppm", "freq_err_ppm", "cfo_ppm"),
    "fallback": ("fallback",),
}


def load_csv(path, overrides=None):
    overrides = overrides or {}
    with open(path, newline="") as fh:
        rdr = csv.reader(fh)
        header = [h.strip() for h in next(rdr)]
        colmap = {}
        for key, aliases in DEFAULT_COLS.items():
            names = [overrides[key]] if key in overrides else list(aliases)
            for n in names:
                if n in header:
                    colmap[key] = header.index(n)
                    break
        for req in ("timestamp_s", "die_temp_c", "ppm_err"):
            if req not in colmap:
                raise SystemExit(f"CSV error: required column '{req}' not found "
                                 f"(header: {header}; use --col-{req} to override)")
        rows = []
        for raw in rdr:
            if not raw:
                continue
            try:
                t = float(raw[colmap["timestamp_s"]])
                tdie = float(raw[colmap["die_temp_c"]])
                ppm = float(raw[colmap["ppm_err"]])
            except (ValueError, IndexError):
                continue  # skip malformed/annotation rows
            ph = raw[colmap["phase"]].strip().lower() if "phase" in colmap else ""
            fb = raw[colmap["fallback"]].strip() if "fallback" in colmap else ""
            rows.append((t, tdie, ppm, ph, fb))
    if len(rows) < 20:
        raise SystemExit(f"CSV error: only {len(rows)} usable rows — not enough for "
                         "hysteresis analysis")
    rows.sort(key=lambda r: r[0])
    return rows


def contiguous_runs(rows):
    """Split rows into runs at phase-class changes or time gaps > max(10*dt, 30 s)."""
    def kind(ph):
        if "cool" in ph:
            return "cooling"
        if "warm" in ph:
            return "warming"
        return "dwell"

    dts = [rows[i + 1][0] - rows[i][0] for i in range(len(rows) - 1)]
    gap_thr = max(10.0 * float(np.median(dts)), 30.0)
    runs, cur = [], [rows[0]]
    cur_kind = kind(rows[0][3])
    for r in rows[1:]:
        k = kind(r[3])
        if k != cur_kind or r[0] - cur[-1][0] > gap_thr:
            runs.append((cur_kind, cur))
            cur, cur_kind = [r], k
        else:
            cur.append(r)
    runs.append((cur_kind, cur))
    return runs


def split_segments(rows, min_span_s=120.0, min_range_c=3.0):
    """Ramp segments. Trust explicit phase labels when present; otherwise
    detect monotonic runs of die temp via windowed-slope sign (sibling
    convention: ~30 s window, 0.002 C/s direction threshold)."""
    labeled = [r for r in rows if r[3] in ("cooling", "warming", "cool", "warm", "dwell")]
    segs = []
    if labeled:
        for kind, run in contiguous_runs(rows):
            if kind == "dwell" or len(run) < 20:
                continue
            segs.append((kind, run))
        return segs

    t = np.array([r[0] for r in rows])
    y = np.array([r[1] for r in rows])
    dt = float(np.median(np.diff(t)))
    win = max(3, int(round(30.0 / max(dt, 0.05))))
    slopes = []
    for i in range(len(y)):
        lo, hi = max(0, i - win), min(len(y), i + win + 1)
        slopes.append(np.polyfit(t[lo:hi], y[lo:hi], 1)[0])
    slopes = np.convolve(np.array(slopes), np.ones(win) / win, mode="same")
    direction, start = 0, 0
    for i, s in enumerate(slopes):
        d = -1 if s < -0.002 else (1 if s > 0.002 else direction)
        if d != direction and d != 0:
            segs_append(segs, rows[start:i], direction, min_span_s, min_range_c)
            direction, start = d, i
    segs_append(segs, rows[start:], direction, min_span_s, min_range_c)
    return segs


def segs_append(segs, block, direction, min_span_s, min_range_c):
    if not block or direction == 0:
        return
    span = block[-1][0] - block[0][0]
    rng = max(b[1] for b in block) - min(b[1] for b in block)
    if span >= min_span_s and rng >= min_range_c and len(block) >= 20:
        segs.append(("cooling" if direction < 0 else "warming", block))


# ------------------------------------------------------ resample / curves

def resample_uniform(rows, dt):
    """Linear interpolation of each ramp onto the COMMON uniform base dt."""
    t = np.array([r[0] for r in rows])
    tdie = np.array([r[1] for r in rows])
    ppm = np.array([r[2] for r in rows])
    grid = np.arange(t[0], t[-1] + dt / 2, dt)
    return grid, np.interp(grid, t, tdie), np.interp(grid, t, ppm)


def ramp_slew_rate(grid, tdie):
    """Average die-temp slew rate over the ramp: |OLS slope| of T vs t."""
    return abs(float(np.polyfit(grid, tdie, 1)[0]))


def crossings(grid, tdie, ppm, level):
    """All time-ordered crossings of `level` in the ppm series, interpolated
    onto die temp.  Returns arrays of T_die and t at each crossing."""
    Ts, ts_ = [], []
    for i in range(len(ppm) - 1):
        a, b = ppm[i], ppm[i + 1]
        if a == level:
            Ts.append(tdie[i])
            ts_.append(grid[i])
            continue
        if (a - level) * (b - level) < 0:
            f = (level - a) / (b - a)
            Ts.append(tdie[i] + f * (tdie[i + 1] - tdie[i]))
            ts_.append(grid[i] + f * (grid[i + 1] - grid[i]))
    return np.array(Ts), np.array(ts_)


# ------------------------------------------------------- hysteresis core

def analyze(rows, k=None, t0=None, n_levels=7, n_boot=200, seed=7):
    segs = split_segments(rows)
    n_cool = sum(1 for n, _ in segs if "cool" in n)
    n_warm = sum(1 for n, _ in segs if "warm" in n)
    if not segs or n_cool == 0 or n_warm == 0:
        counts = {"cooling_ramps": n_cool, "warming_ramps": n_warm,
                  "dwell_runs": sum(1 for n, r in contiguous_runs(rows) if n == "dwell"),
                  "usable_rows": len(rows)}
        raise NoRampsError(counts)

    dts_all = np.diff(np.array([r[0] for r in rows]))
    dt = max(float(np.median(dts_all)), 0.05)  # common uniform base

    # per-direction pooled resampled curves + per-ramp slew rates
    pooled = {"warming": [], "cooling": []}
    slews = {"warming": [], "cooling": []}
    ramp_info = []
    for name, run in segs:
        d = "warming" if "warm" in name else "cooling"
        grid, tdie, ppm = resample_uniform(run, dt)
        r = ramp_slew_rate(grid, tdie)
        pooled[d].append((grid, tdie, ppm))
        slews[d].append(r)
        ramp_info.append({
            "ramp": f"{d}#{len(slews[d])}", "n_samples": len(run),
            "span_s": float(run[-1][0] - run[0][0]),
            "die_temp_range_C": [float(min(x[1] for x in run)),
                                 float(max(x[1] for x in run))],
            "ppm_range": [float(min(x[2] for x in run)),
                          float(max(x[2] for x in run))],
            "avg_slew_C_per_s": r,
        })
    curves = {d: (np.concatenate([c[0] for c in v]),
                  np.concatenate([c[1] for c in v]),
                  np.concatenate([c[2] for c in v]))
              for d, v in pooled.items()}

    # ppm overlap of the two directions -> levels on the interior 80%
    lo = max(curves["warming"][2].min(), curves["cooling"][2].min())
    hi = min(curves["warming"][2].max(), curves["cooling"][2].max())
    if hi - lo < 1.0:
        raise NoRampsError({"reason": f"ppm overlap of ramps only {hi - lo:.3f} ppm "
                                       "(need >= 1.0)", "cooling_ramps": n_cool,
                            "warming_ramps": n_warm})
    levels = np.linspace(lo + 0.1 * (hi - lo), hi - 0.1 * (hi - lo), n_levels)

    r_warm = float(np.median(slews["warming"]))
    r_cool = float(np.median(slews["cooling"]))

    table = []
    for lv in levels:
        row = {"level_ppm": float(lv)}
        for d in ("warming", "cooling"):
            g, T, p = curves[d]
            Tc, tc = crossings(g, T, p, lv)
            if len(Tc) == 0:
                row[f"T_die_{d}_C"] = None
                row[f"n_cross_{d}"] = 0
            else:
                row[f"T_die_{d}_C"] = float(np.median(Tc))
                row[f"n_cross_{d}"] = int(len(Tc))
                row[f"cross_spread_{d}_C"] = float(Tc.max() - Tc.min())
        Tw, Tc_ = row.get("T_die_warming_C"), row.get("T_die_cooling_C")
        if Tw is None or Tc_ is None:
            row["dT_C"] = None
            row["status"] = "UNCOVERED"
        else:
            row["dT_C"] = Tw - Tc_
            spread = max(row.get("cross_spread_warming_C", 0.0),
                         row.get("cross_spread_cooling_C", 0.0))
            row["status"] = "AMBIGUOUS" if spread > 2.0 else "ok"
            row["dt_equiv_warming_s"] = row["dT_C"] / r_warm if r_warm > 1e-9 else None
            row["dt_equiv_cooling_s"] = row["dT_C"] / r_cool if r_cool > 1e-9 else None
            row["tau_hyst_s"] = row["dT_C"] / (r_warm + r_cool)
        table.append(row)

    ok = [r for r in table if r["dT_C"] is not None]
    if not ok:
        raise NoRampsError({"reason": "no ppm level bracketed on both directions",
                            "cooling_ramps": n_cool, "warming_ramps": n_warm})

    dTs = np.array([r["dT_C"] for r in ok])
    taus = np.array([r["tau_hyst_s"] for r in ok])

    # moving-block bootstrap CI on the medians (resample blocks of the pooled
    # curves, redo crossings at the same levels)
    ci = bootstrap_ci(curves, levels, r_warm, r_cool, n_boot, seed)

    res = {
        "resample": {"method": "linear interpolation onto uniform grid",
                     "interval_s": dt, "base": "median sample interval of whole series"},
        "ramps": ramp_info,
        "slew_rates_C_per_s": {"warming_median": r_warm, "cooling_median": r_cool,
                               "per_ramp": {d: [float(x) for x in v]
                                            for d, v in slews.items()}},
        "ppm_overlap": [float(lo), float(hi)],
        "n_levels": int(n_levels),
        "levels": table,
        "hysteresis": {
            "median_dT_C": float(np.median(dTs)),
            "iqr_dT_C": float(np.percentile(dTs, 75) - np.percentile(dTs, 25)),
            "min_dT_C": float(dTs.min()), "max_dT_C": float(dTs.max()),
            "levels_reported": len(table), "levels_covered": len(ok),
            "levels_uncovered": len(table) - len(ok),
        },
        "time_equivalent": {
            "median_dt_warming_s": float(np.median([r["dt_equiv_warming_s"] for r in ok])),
            "median_dt_cooling_s": float(np.median([r["dt_equiv_cooling_s"] for r in ok])),
            "median_tau_hyst_s": float(np.median(taus)),
            "iqr_tau_hyst_s": float(np.percentile(taus, 75) - np.percentile(taus, 25)),
            "note": "tau_hyst = dT/(r_warm+r_cool); equals ~2x the single-ramp "
                    "xcorr lag when slews are equal (both ramps each lag by tau)",
        },
        "bootstrap_ci": ci,
    }

    if k is not None and t0 is not None:
        ppm_off, n_dw = dwell_offset_estimate(rows, k, t0)
        if ppm_off is not None:
            res["ppm_to_xtal"] = {
                "k_ppm_per_K2": k, "t0_C": t0,
                "dwell_static_offset_ppm": ppm_off, "dwell_points": n_dw,
                "method": "T_xtal = T0 - sqrt((ppm - offset)/k) (below-T0 branch)",
                "T_xtal_per_level_C": {
                    f"{r['level_ppm']:.3f}":
                        float(t0 - math.sqrt(max((r["level_ppm"] - ppm_off) / k, 0.0)))
                    for r in table},
            }
    return res


class NoRampsError(Exception):
    pass


def bootstrap_ci(curves, levels, r_warm, r_cool, n_boot, seed, block_s=120.0):
    rng = np.random.default_rng(seed)
    med_dT, med_tau = [], []
    for _ in range(n_boot):
        dT_lv = []
        for lv in levels:
            Tcs = {}
            for d in ("warming", "cooling"):
                g, T, p = curves[d]
                n = len(g)
                bl = max(10, int(round(block_s / max(1e-3, g[1] - g[0]))))
                if n < 4 * bl:
                    Tcs[d] = np.array([])
                    continue
                starts = rng.integers(0, n - bl, size=max(2, n // bl))
                idx = np.unique(np.concatenate([np.arange(s, s + bl) for s in starts]))
                Tc, _ = crossings(g[idx], T[idx], p[idx], lv)
                Tcs[d] = Tc
            if len(Tcs["warming"]) and len(Tcs["cooling"]):
                dT_lv.append(np.median(Tcs["warming"]) - np.median(Tcs["cooling"]))
        if len(dT_lv) >= 3:
            dT_lv = np.array(dT_lv)
            med_dT.append(np.median(dT_lv))
            med_tau.append(np.median(dT_lv) / (r_warm + r_cool))
    if len(med_dT) < 50:
        return None
    return {
        "n_boot": len(med_dT),
        "median_dT_C_p16_p84": [float(np.percentile(med_dT, 16)),
                                 float(np.percentile(med_dT, 84))],
        "median_tau_hyst_s_p16_p84": [float(np.percentile(med_tau, 16)),
                                       float(np.percentile(med_tau, 84))],
    }


def dwell_offset_estimate(rows, k, t0):
    """Static ppm offset at the T0 end from dwell rows (sibling convention)."""
    dw = [r for r in rows if "dwell" in r[3]]
    if len(dw) < 3:
        return None, 0
    ppm = np.array([r[2] for r in dw])
    td = np.array([r[1] for r in dw])
    resid = ppm - k * (td - t0) ** 2
    return float(np.median(resid)), len(dw)


# ---------------------------------------------------------------- report

def print_report(res):
    rs = res["resample"]
    print("THERMAL HYSTERESIS — die temp (XOSC) at matched freq-error levels")
    print("=" * 72)
    print(f"resample: {rs['method']}, interval {rs['interval_s']:.2f} s ({rs['base']})")
    print("\nramps (avg slew = |OLS slope| of die temp vs time):")
    for r in res["ramps"]:
        print(f"  {r['ramp']:<10} n={r['n_samples']:>4}  span={r['span_s']:>6.0f}s  "
              f"dieT {r['die_temp_range_C'][0]:6.1f}..{r['die_temp_range_C'][1]:6.1f}C  "
              f"ppm {r['ppm_range'][0]:7.2f}..{r['ppm_range'][1]:7.2f}  "
              f"slew={r['avg_slew_C_per_s']:.4f} C/s")
    sr = res["slew_rates_C_per_s"]
    print(f"  slew used for conversion: warming median {sr['warming_median']:.4f} C/s, "
          f"cooling median {sr['cooling_median']:.4f} C/s")
    ov = res["ppm_overlap"]
    print(f"\nppm overlap [{ov[0]:.2f}, {ov[1]:.2f}] -> {res['n_levels']} levels "
          f"(interior 80%)")

    hdr = (f"{'level_ppm':>10} {'T_cool_C':>9} {'T_warm_C':>9} {'dT_C':>7} "
           f"{'dt@warm_s':>10} {'dt@cool_s':>10} {'tau_hyst_s':>11} {'status':>10}")
    print("\n" + hdr)
    print("-" * len(hdr))
    for r in res["levels"]:
        if r["dT_C"] is None:
            miss = "cool" if r.get("T_die_cooling_C") is None else "warm"
            print(f"{r['level_ppm']:>10.3f} {'--':>9} {'--':>9} {'--':>7} "
                  f"{'--':>10} {'--':>10} {'--':>11} "
                  f"{r['status'] + '(' + miss + ')':>10}")
            continue
        print(f"{r['level_ppm']:>10.3f} {r['T_die_cooling_C']:>9.2f} "
              f"{r['T_die_warming_C']:>9.2f} {r['dT_C']:>+7.2f} "
              f"{r['dt_equiv_warming_s']:>+10.1f} {r['dt_equiv_cooling_s']:>+10.1f} "
              f"{r['tau_hyst_s']:>+11.1f} {r['status']:>10}")

    h = res["hysteresis"]
    print(f"\nHYSTERESIS: median dT = {h['median_dT_C']:+.2f} C "
          f"(IQR {h['iqr_dT_C']:.2f}, range {h['min_dT_C']:+.2f}..{h['max_dT_C']:+.2f}; "
          f"{h['levels_covered']}/{h['levels_reported']} levels covered, "
          f"{h['levels_uncovered']} uncovered)")
    te = res["time_equivalent"]
    print(f"TIME EQUIVALENT: dT/r_warm = {te['median_dt_warming_s']:+.1f} s, "
          f"dT/r_cool = {te['median_dt_cooling_s']:+.1f} s")
    print(f"  die-vs-crystal lag from hysteresis: tau_hyst = dT/(r_warm+r_cool) = "
          f"{te['median_tau_hyst_s']:+.1f} s (IQR {te['iqr_tau_hyst_s']:.1f} s) — "
          f"{te['note']}")
    ci = res.get("bootstrap_ci")
    if ci:
        print(f"  bootstrap {ci['n_boot']} reps: median dT CI "
              f"[{ci['median_dT_C_p16_p84'][0]:+.2f}, {ci['median_dT_C_p16_p84'][1]:+.2f}] C, "
              f"tau_hyst CI [{ci['median_tau_hyst_s_p16_p84'][0]:+.1f}, "
              f"{ci['median_tau_hyst_s_p16_p84'][1]:+.1f}] s")
    if "ppm_to_xtal" in res:
        p = res["ppm_to_xtal"]
        print(f"\nK/T0 CONVERSION: k={p['k_ppm_per_K2']} ppm/K^2, T0={p['t0_C']} C, "
              f"static offset={p['dwell_static_offset_ppm']:+.2f} ppm "
              f"({p['dwell_points']} dwell pts)")
        for lv, tx in sorted(p["T_xtal_per_level_C"].items(), key=lambda kv: float(kv[0])):
            print(f"  ppm {float(lv):8.3f} -> effective crystal T {tx:6.2f} C")


# --------------------------------------------------------------- self-test

def _first_order(x, dt, tau):
    alpha = 1.0 - math.exp(-dt / tau)
    y = np.empty_like(x)
    y[0] = x[0]
    for i in range(1, len(x)):
        y[i] = y[i - 1] + alpha * (x[i] - y[i - 1])
    return y


def self_test():
    PLANTED_TAU = 25.0
    K, T0 = 0.034, 25.0
    dt = 2.0
    rng = np.random.default_rng(42)
    profiles = [("cooling", 25.0, -20.0, 0.025), ("warming", -20.0, 5.0, 0.030)]
    rows, t = [], 0.0
    tdie_series, t_series, seg_ids = [], [], []
    for name, tstart, tend, rate in profiles:
        dur = abs(tend - tstart) / rate
        n = int(dur / dt)
        for i in range(n):
            t_series.append(t)
            tdie_series.append(tstart + (tend - tstart) * (i / n))
            seg_ids.append(name)
            t += dt
        for _ in range(60):  # soak plateau between/after ramps
            t_series.append(t)
            tdie_series.append(tend)
            seg_ids.append("dwell")
            t += dt
    tdie = np.array(tdie_series)
    t_s = np.array(t_series)
    tdie_meas = tdie + rng.normal(0, 0.15, len(tdie))
    txtal = _first_order(tdie, dt, PLANTED_TAU)
    ppm = K * (txtal - T0) ** 2 + rng.normal(0, 0.05, len(tdie))
    rows = [(float(t_s[i]), float(tdie_meas[i]), float(ppm[i]), seg_ids[i], "")
            for i in range(len(tdie))]

    res = analyze(rows, k=K, t0=T0, n_levels=7)
    print("SELF-TEST (synthetic validation only — NOT a hardware measurement)")
    print_report(res)

    med = res["hysteresis"]["median_dT_C"]
    tau = res["time_equivalent"]["median_tau_hyst_s"]
    r_w = res["slew_rates_C_per_s"]["warming_median"]
    r_c = res["slew_rates_C_per_s"]["cooling_median"]
    expected_dT = PLANTED_TAU * (r_w + r_c)
    err_tau = abs(tau - PLANTED_TAU)
    ok_all = res["hysteresis"]["levels_uncovered"] == 0
    ok_dT = abs(med - expected_dT) <= 0.25 * expected_dT
    ok_tau = err_tau <= 4.0
    ok_sign = med > 0 and tau > 0
    print(f"\nplanted tau = {PLANTED_TAU:.1f} s; expected dT = tau*(r_w+r_c) = "
          f"{expected_dT:.2f} C (r_w={r_w:.4f}, r_c={r_c:.4f})")
    print(f"recovered: median dT = {med:+.2f} C, tau_hyst = {tau:+.1f} s "
          f"(|err| = {err_tau:.2f} s)")
    print(f"all levels covered: {'PASS' if ok_all else 'FAIL'}; "
          f"dT recovery: {'PASS' if ok_dT else 'FAIL'}; "
          f"tau recovery: {'PASS' if ok_tau else 'FAIL'}; "
          f"sign (die leads): {'PASS' if ok_sign else 'FAIL'}")
    status = "SELF-TEST PASS" if (ok_all and ok_dT and ok_tau and ok_sign) \
        else "SELF-TEST FAIL"
    print(status)
    return 0 if status.endswith("PASS") else 1


# -------------------------------------------------------------------- main

def main():
    ap = argparse.ArgumentParser(
        description=(__doc__ or __name__).splitlines()[0])
    ap.add_argument("--csv", help="ramp CSV (timestamp_s, die_temp_c, ppm_err, [phase])")
    ap.add_argument("--json", help="optional JSON output path")
    ap.add_argument("--k", type=float, help="fitted k in ppm/K^2 (sibling atcut-fit deliverable)")
    ap.add_argument("--t0", type=float, help="fitted T0 in C")
    ap.add_argument("--n-levels", type=int, default=7, help="ppm levels (5-10, default 7)")
    ap.add_argument("--col-timestamp_s", dest="c_ts")
    ap.add_argument("--col-phase", dest="c_ph")
    ap.add_argument("--col-die_temp_c", dest="c_td")
    ap.add_argument("--col-ppm_err", dest="c_ppm")
    ap.add_argument("--col-fallback", dest="c_fb")
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()

    if args.self_test:
        sys.exit(self_test())
    if not args.csv:
        ap.error("--csv required (or --self-test)")
    if not 5 <= args.n_levels <= 10:
        ap.error("--n-levels must be 5..10")

    overrides = {}
    for key, val in (("timestamp_s", args.c_ts), ("phase", args.c_ph),
                     ("die_temp_c", args.c_td), ("ppm_err", args.c_ppm),
                     ("fallback", args.c_fb)):
        if val:
            overrides[key] = val
    try:
        rows = load_csv(args.csv, overrides)
    except FileNotFoundError:
        raise SystemExit(f"CSV error: file not found: {args.csv}")
    try:
        res = analyze(rows, k=args.k, t0=args.t0, n_levels=args.n_levels)
    except NoRampsError as e:
        print("VERDICT: NO DATA — hysteresis not measurable from this CSV")
        print(f"quantitative gate: {dict(e.args[0])}")
        print("(need >=1 cooling AND >=1 warming ramp, each >=120 s span, >=3 C "
              "die-temp range, >=20 rows, >=1.0 ppm range overlap)")
        sys.exit(1)
    print_report(res)
    if args.json:
        with open(args.json, "w") as fh:
            json.dump(res, fh, indent=2)
        print(f"\nJSON written: {args.json}")


if __name__ == "__main__":
    main()
