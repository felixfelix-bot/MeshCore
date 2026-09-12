#!/usr/bin/env python3
"""Thermal lag analysis: XOSC die temp vs external carrier frequency error (ppm).

Fleet task: characterize die-vs-crystal thermal lag from LR2021 ramp logs and
recommend a SelfCal EMA time constant.

Input CSV columns (header required; names configurable via --col-*):
    timestamp_s   relative or absolute seconds (monotonic)
    phase         optional: 'dwell', 'cooling', 'warming' (or setpoint labels);
                  auto-detected from die-temp slope if absent
    die_temp_c    LR2021 die temperature, getRadioTemperatureC (XOSC source)
    ppm_err       externally measured carrier frequency error vs reference, ppm
    fallback      optional, ignored (recorded as-is)

Methods:
 1. Per-ramp cross-correlation lag between the die-temp and ppm-error
    trajectories (both linearly detrended, uniformly resampled onto a stated
    common time base by linear interpolation; the ORIGINAL raw sample rate is
    recorded per ramp). The ppm trace is sign-flipped per ramp so die temp and
    frequency error move together (equivalent to taking the |r| peak; the
    applied flip is reported). Lag offsets span min(max_lag, lag_frac * ramp
    span). Parabolic sub-sample peak.
    Uncertainty, both reported: (a) half-width of the xcorr peak at
    r_peak/sqrt(2) (floored at half the resample interval); (b) moving-block
    bootstrap over sliding sub-windows of the ramp. If |lag| < one resample
    interval the lag is reported explicitly as "< 1 sample = X s".
    Convention: lag > 0 means die temp LEADS the crystal (crystal trails the
    die sensor) — the ppm trajectory is delayed by that many seconds.
 2. Cross-check, loop-area delay fit: the delay tau that minimizes the
    ppm-vs-(delayed die temp) hysteresis loop area (monotonic ppm(T) branch,
    no k/T0 needed), with T-bin jackknife uncertainty.
 3. Hysteresis: die temp at matched ppm crossing levels, warming vs cooling.
 4. Optional ppm -> effective crystal temp via fitted k/T0
    (offset_ppm = -k*(T - T0)^2, sweep branch below T0).
 5. SelfCal EMA time-constant recommendation + open-loop transient-error bound.

Self-test (--self-test): plants a known first-order crystal lag in synthetic
ramps and asserts recovery. SELF-TEST output is synthetic pipeline validation
only and is never a measurement of any hardware.

Usage:
    python3 analyze_thermal_lag.py --csv bench_session.csv [--json out.json]
        [--k 0.034] [--t0 25.0] [--tau-now 10] [--max-lag 600]
    python3 analyze_thermal_lag.py --self-test
"""

import argparse
import csv
import json
import math
import sys

import numpy as np

# ---------------------------------------------------------------- loading

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
            if not raw or not raw[colmap["timestamp_s"]].strip():
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
        raise SystemExit(f"CSV error: only {len(rows)} usable rows — not enough for lag analysis")
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
    """Split into labeled ramp segments. Trust explicit phase labels when present;
    otherwise detect monotonic runs of die temp (median-filtered slope).
    Each ramp keeps its adjacent dwell plateaus (flat shoulders) so the
    detrended trajectories carry step-edge structure for the cross-correlation."""
    labeled = [r for r in rows if r[3] in ("cooling", "warming", "cool", "warm", "dwell")]
    segs = []
    if labeled:
        runs = contiguous_runs(rows)
        for j, (kind, run) in enumerate(runs):
            if kind == "dwell" or len(run) < 20:
                continue
            block = []
            if j > 0 and runs[j - 1][0] == "dwell":
                block += runs[j - 1][1]
            block += run
            if j + 1 < len(runs) and runs[j + 1][0] == "dwell":
                block += runs[j + 1][1]
            segs.append((kind, block))
        return segs

    # auto-detect: median-filter then sign of local slope over a window
    t = np.array([r[0] for r in rows])
    y = np.array([r[1] for r in rows])
    dt = float(np.median(np.diff(t)))
    win = max(3, int(round(30.0 / dt)))  # ~30 s slope window
    slopes = []
    for i in range(len(y)):
        lo, hi = max(0, i - win), min(len(y), i + win + 1)
        slopes.append(np.polyfit(t[lo:hi], y[lo:hi], 1)[0])
    slopes = np.array(slopes_smooth(slopes, win))
    direction = 0
    start = 0
    for i, s in enumerate(slopes):
        d = -1 if s < -0.002 else (1 if s > 0.002 else direction)
        if d != direction and d != 0:
            block = rows[start:i]
            segs_append(segs, block, direction, t, min_span_s, min_range_c)
            direction, start = d, i
    segs_append(segs, rows[start:], direction, t, min_span_s, min_range_c)
    return segs


def slopes_smooth(x, win):
    k = np.ones(win) / win
    return np.convolve(x, k, mode="same")


def segs_append(segs, block, direction, t, min_span_s, min_range_c):
    if not block or direction == 0:
        return
    span = block[-1][0] - block[0][0]
    rng = max(b[1] for b in block) - min(b[1] for b in block)
    if span >= min_span_s and rng >= min_range_c and len(block) >= 20:
        segs.append(("cooling" if direction < 0 else "warming", block))


# ------------------------------------------------------- resample / xcorr

def resample_uniform(rows, dt=None):
    t = np.array([r[0] for r in rows])
    tdie = np.array([r[1] for r in rows])
    ppm = np.array([r[2] for r in rows])
    if dt is None:
        dt = float(np.median(np.diff(t)))
    dt = max(dt, 0.05)
    grid = np.arange(t[0], t[-1] + dt / 2, dt)
    return grid, np.interp(grid, t, tdie), np.interp(grid, t, ppm), dt


def detrend(x, y):
    p = np.polyfit(x, y, 1)
    return y - np.polyval(p, x)


def xcorr_curve(grid, a, b, max_lag, dt):
    """r(tau) = corr(a delayed by tau, b now). Peak tau>0 => a leads b."""
    a0, b0 = detrend(grid, a), detrend(grid, b)
    a0 = (a0 - a0.mean()) / (a0.std() or 1.0)
    b0 = (b0 - b0.mean()) / (b0.std() or 1.0)
    taus = np.arange(-max_lag, max_lag + dt / 2, dt)
    rs = np.empty(len(taus))
    n = len(b0)
    for i, tau in enumerate(taus):
        k = int(round(tau / dt))
        if k >= 0:
            ai, bi = a0[:n - k] if k else a0, b0[k:]
        else:
            ai, bi = a0[-k:], b0[:n + k]
        if len(ai) < 20:
            rs[i] = np.nan
            continue
        ai = (ai - ai.mean()) / (ai.std() or 1.0)
        bi = (bi - bi.mean()) / (bi.std() or 1.0)
        rs[i] = float(np.dot(ai, bi) / len(ai))
    return taus, rs


def parabolic_peak(taus, rs):
    idx = int(np.nanargmax(np.abs(rs)))
    if 0 < idx < len(rs) - 1:
        y0, y1, y2 = rs[idx - 1], rs[idx], rs[idx + 1]
        denom = (y0 - 2 * y1 + y2)
        shift = 0.5 * (y0 - y2) / denom if abs(denom) > 1e-12 else 0.0
        shift = max(-1.0, min(1.0, shift))
        step = taus[1] - taus[0]
        return float(taus[idx] + shift * step), float(rs[idx]), idx
    return float(taus[idx]), float(rs[idx]), idx


def plateau_width(taus, rs, idx, frac=0.99):
    """Width of the |r| >= frac*max region — systematic uncertainty floor."""
    thr = frac * abs(rs[idx])
    ok = np.abs(rs) >= thr
    lo = idx
    while lo > 0 and ok[lo - 1]:
        lo -= 1
    hi = idx
    while hi < len(ok) - 1 and ok[hi + 1]:
        hi += 1
    return float(taus[hi] - taus[lo])


def bootstrap_lag(grid, a, b, max_lag, dt, n_boot=200, block_s=120.0, seed=7):
    """Moving-block bootstrap over the ramp; returns (p16, p84) of the lag."""
    rng = np.random.default_rng(seed)
    a0, b0 = detrend(grid, a), detrend(grid, b)
    n = len(a0)
    bl = max(10, int(round(block_s / dt)))
    lags = []
    for _ in range(n_boot):
        starts = rng.integers(0, n - bl, size=max(2, n // bl))
        idx = np.concatenate([np.arange(s, s + bl) for s in starts])
        idx = np.unique(idx)
        if len(idx) < 40 or grid[idx][-1] - grid[idx][0] < 3 * max_lag:
            continue
        g2 = grid[idx]
        taus, rs = xcorr_curve(g2, a0[idx], b0[idx], max_lag, dt)
        if np.all(np.isnan(rs)):
            continue
        lag, _, _ = parabolic_peak(taus, rs)
        lags.append(lag)
    if len(lags) < 50:
        return None
    return float(np.percentile(lags, 16)), float(np.percentile(lags, 84)), len(lags)


def raw_sample_stats(block):
    """Original (pre-resample) sampling statistics of a ramp block."""
    d = np.diff(np.array([r[0] for r in block], dtype=float))
    return {"n_raw": len(block),
            "median_dt_s": float(np.median(d)),
            "min_dt_s": float(d.min()), "max_dt_s": float(d.max())}


def peak_halfwidth(taus, rs, idx):
    """(a) Uncertainty: half-width of the xcorr peak at |r| = r_peak/sqrt(2)
    (the 1-sigma correlation point), measured over the contiguous region
    around the peak."""
    thr = abs(rs[idx]) / math.sqrt(2.0)
    ok = np.abs(rs) >= thr
    lo = idx
    while lo > 0 and ok[lo - 1]:
        lo -= 1
    hi = idx
    while hi < len(ok) - 1 and ok[hi + 1]:
        hi += 1
    return 0.5 * float(taus[hi] - taus[lo])


# ------------------------------------------------- loop-area delay fitting
# Primary lag estimator: the delay tau that minimizes the area of the
# ppm-vs-(delayed die temp) hysteresis loop. Needs no k/T0 (only requires
# ppm(T_xtal) monotonic over the sweep, true for the AT-cut parabola below T0).

def branch_masks(t, T, thr_c_s=0.002):
    """Warming/cooling row masks from windowed die-temp slope."""
    dt = float(np.median(np.diff(t)))
    win = max(3, int(round(30.0 / max(dt, 0.05))))
    warm = np.zeros(len(t), bool)
    cool = np.zeros(len(t), bool)
    for i in range(len(t)):
        lo, hi = max(0, i - win), min(len(t), i + win + 1)
        s = np.polyfit(t[lo:hi], T[lo:hi], 1)[0]
        if s > thr_c_s:
            warm[i] = True
        elif s < -thr_c_s:
            cool[i] = True
    return warm, cool


def _bin_means(Tb, pb, edges):
    idx = np.digitize(Tb, edges) - 1
    ok = (idx >= 0) & (idx < len(edges) - 1)
    cnts = np.bincount(idx[ok], minlength=len(edges) - 1)
    sums = np.bincount(idx[ok], weights=pb[ok], minlength=len(edges) - 1)
    means = np.where(cnts >= 2, sums / np.maximum(cnts, 1), np.nan)
    return means, cnts


def loop_area(T_shift, ppm, warm, cool, n_bins=40):
    """Mean |ppm_warm - ppm_cool| over shared T bins (ppm units). NaN if too
    little shared coverage."""
    Tw, Tc = T_shift[warm], T_shift[cool]
    lo = max(Tw.min() if len(Tw) else np.nan, Tc.min() if len(Tc) else np.nan)
    hi = min(Tw.max() if len(Tw) else np.nan, Tc.max() if len(Tc) else np.nan)
    if not np.isfinite(lo + hi) or hi - lo < 2.0:
        return np.nan
    edges = np.linspace(lo + 0.05 * (hi - lo), hi - 0.05 * (hi - lo), n_bins + 1)
    mw, cw = _bin_means(Tw, ppm[warm], edges), _bin_means(Tc, ppm[cool], edges)
    diff = np.abs(mw[0] - cw[0])
    valid = np.isfinite(diff) & (mw[1] >= 2) & (cw[1] >= 2)
    if valid.sum() < 5:
        return np.nan
    return float(np.mean(diff[valid]))


def delay_fit_lag(t, T, ppm, warm, cool, max_lag, dt, n_bins=40):
    """Scan delays tau (positive = die delayed = die LEADS crystal) and return
    the tau minimizing the loop area, with parabolic sub-sample refinement."""
    step = max(dt, 1.0)
    taus = np.arange(-max_lag, max_lag + step / 2, step)
    areas = np.array([loop_area(np.interp(t - tau, t, T), ppm, warm, cool, n_bins)
                      for tau in taus])
    if np.all(np.isnan(areas)):
        return None
    idx = int(np.nanargmin(areas))
    amin = areas[idx]
    # parabolic refinement around the minimum
    lag = taus[idx]
    if 0 < idx < len(taus) - 1 and np.isfinite(areas[idx - 1]) and np.isfinite(areas[idx + 1]):
        y0, y1, y2 = areas[idx - 1], amin, areas[idx + 1]
        denom = (y0 - 2 * y1 + y2)
        if abs(denom) > 1e-12:
            shift = max(-1.0, min(1.0, 0.5 * (y0 - y2) / denom))
            lag = float(taus[idx] + shift * step)
    # plateau: tau range within 5% of the minimum area (systematic floor)
    ok = areas <= amin * 1.05
    lo_i, hi_i = np.where(ok)[0][[0, -1]]
    plat = float(taus[hi_i] - taus[lo_i])
    return {"lead_s": float(lag), "min_loop_ppm": float(amin),
            "plateau_width_s": plat, "taus": taus, "areas": areas,
            "systematic_floor_s": 0.5 * step + 0.5 * plat}


def delay_fit_jackknife(t, T, ppm, warm, cool, max_lag, dt, n_bins=40):
    """Jackknife over T-bins: re-optimize tau leaving each bin out; std of the
    jackknife estimates -> statistical uncertainty."""
    base = delay_fit_lag(t, T, ppm, warm, cool, max_lag, dt, n_bins)
    if base is None:
        return None, None
    # precompute bin membership of the base fit to leave bins out
    T_shift = np.interp(t - base["lead_s"], t, T)
    Tw, Tc = T_shift[warm], T_shift[cool]
    lo, hi = max(Tw.min(), Tc.min()), min(Tw.max(), Tc.max())
    if hi - lo < 2.0:
        return base, None
    edges = np.linspace(lo, hi, n_bins + 1)
    labels_w = np.digitize(Tw, edges) - 1
    labels_c = np.digitize(Tc, edges) - 1
    ests = []
    for b in range(n_bins):
        w2 = warm.copy()
        c2 = cool.copy()
        wi = np.where(warm)[0][np.isin(labels_w, b)]
        ci = np.where(cool)[0][np.isin(labels_c, b)]
        w2[wi] = False
        c2[ci] = False
        r = delay_fit_lag(t, T, ppm, w2, c2, max_lag, dt, n_bins)
        if r is not None and abs(r["lead_s"] - base["lead_s"]) < 0.75 * max_lag:
            ests.append(r["lead_s"])
    if len(ests) < 10:
        return base, None
    return base, float(np.std(ests, ddof=1))


# ------------------------------------------------------------ hysteresis

def hysteresis(segs, n_levels=9):
    """Die temp at matched ppm crossing levels, warming minus cooling."""
    by_dir = {}
    for name, rows in segs:
        key = "warming" if "warm" in name else "cooling"
        by_dir.setdefault(key, []).append(rows)
    if not by_dir.get("warming") or not by_dir.get("cooling"):
        return None
    warm = [r for rows in by_dir["warming"] for r in rows]
    cool = [r for rows in by_dir["cooling"] for r in rows]
    out = {}
    for label, rows in (("warming", warm), ("cooling", cool)):
        t = np.array([r[0] for r in rows])
        y = np.array([r[2] for r in rows])  # ppm
        td = np.array([r[1] for r in rows])  # die temp
        order = np.argsort(y)
        out[label] = (y[order], td[order], t[order])
    yw, tw, _ = out["warming"]
    yc, tc, _ = out["cooling"]
    lo = max(yw.min(), yc.min())
    hi = min(yw.max(), yc.max())
    if hi - lo < 1.0:
        return None
    levels = np.linspace(lo + 0.1 * (hi - lo), hi - 0.1 * (hi - lo), n_levels)
    dts, dppm = [], []
    for lv in levels:
        Tw = float(np.interp(lv, yw, tw))
        Tc = float(np.interp(lv, yc, tc))
        dts.append(Tw - Tc)
        dppm.append(lv)
    dts = np.array(dts)
    return {
        "levels_ppm": [float(x) for x in dppm],
        "delta_T_per_level": [float(x) for x in dts],
        "median_dT_C": float(np.median(dts)),
        "iq_dT_C": float(np.percentile(dts, 75) - np.percentile(dts, 25)),
        "max_abs_dT_C": float(np.max(np.abs(dts))),
    }


def hysteresis_time_equivalent(segs, hyst):
    """Convert the die-temp hysteresis to seconds via the median ramp rate."""
    if hyst is None:
        return None
    rates = []
    for name, rows in segs:
        t = np.array([r[0] for r in rows])
        y = np.array([r[1] for r in rows])
        rates.append(abs(np.polyfit(t, y, 1)[0]))
    rate = float(np.median(rates))
    if rate < 1e-6:
        return None
    return hyst["median_dT_C"] / rate, rate


# ---------------------------------------------- ppm -> effective crystal T

def ppm_to_xtal_temp(ppm, k, t0, ppm_offset):
    """Sweep branch below T0: ppm ~ k*(T-T0)^2 + ppm_offset  =>  T = t0 - sqrt(...)."""
    arg = (ppm - ppm_offset) / k
    arg = np.clip(arg, 0.0, None)
    return t0 - np.sqrt(arg)


def dwell_offset_estimate(rows, k, t0):
    """Static ppm offset at the T0 end from dwell rows (phase contains 'dwell')."""
    dw = [r for r in rows if "dwell" in r[3]]
    if len(dw) < 3:
        return None, 0
    ppm = np.array([r[2] for r in dw])
    td = np.array([r[1] for r in dw])
    resid = ppm - k * (td - t0) ** 2
    return float(np.median(resid)), len(dw)


# ---------------------------------------------------- EMA recommendation

def ema_recommendation(lag_s, ci_lo, ci_hi, tau_now=10.0):
    if lag_s is None:
        return {
            "recommended_tau_s": tau_now,
            "action": "INSUFFICIENT DATA — keep current tau; rerun when ramp CSV exists",
        }
    rec = max(lag_s, ci_lo)  # round up conservatively within noise
    rec = max(rec, tau_now) if rec <= 2.0 * tau_now else rec
    # practical granularity: round to 5 s
    rec = float(5.0 * round(rec / 5.0))
    return {
        "measured_lead_s": lag_s,
        "ci_s": [ci_lo, ci_hi],
        "recommended_tau_s": rec,
        "change_from_current": None if abs(rec - tau_now) < 1e-9 else tau_now,
        "transient_limited": bool(ci_lo > 2.0 * tau_now),
        "note": ("die sensor leads crystal by more than ~2x the current EMA; "
                 "fast temperature transients are a limit on the open-loop model "
                 "(compensation will lead the crystal); closed-loop CFO cannot "
                 "backstop this on LR2021 (FEI path is a verified dead end)")
        if ci_lo > 2.0 * tau_now else
        "lag is compatible with the current EMA constant within uncertainty",
    }


def transient_error_bound(segs, lag_s, k=None, t0=None):
    """Worst-case open-loop mis-compensation during the fastest observed ramp:
    bound_ppm ~ d(offset)/dT * |dT/dt| * lead.  d(offset)/dT = 2*k*|T - T0|.
    Without k/T0, return the bound per unit k (ppm per (ppm/K^2))."""
    if lag_s is None:
        return None
    worst_rate, worst_T = 0.0, None
    for name, rows in segs:
        t = np.array([r[0] for r in rows])
        y = np.array([r[1] for r in rows])
        win = max(3, int(round(30.0 / max(0.05, np.median(np.diff(t))))))
        for i in range(0, len(y) - win, win):
            rate = abs(np.polyfit(t[i:i + win], y[i:i + win], 1)[0])
            if rate > worst_rate:
                worst_rate = rate
                worst_T = float(np.mean(y[i:i + win]))
    out = {"worst_ramp_rate_C_per_s": worst_rate, "at_die_temp_C": worst_T,
           "lead_s": lag_s}
    if k is not None and t0 is not None and worst_T is not None:
        sens = 2.0 * k * abs(worst_T - t0)  # ppm/K
        out["sensitivity_ppm_per_K"] = sens
        out["bound_ppm"] = sens * worst_rate * abs(lag_s)
    else:
        out["bound_ppm_per_k"] = (2.0 * abs(worst_T - t0) * worst_rate * abs(lag_s)
                                  if (worst_T is not None and t0 is not None)
                                  else None)
    return out


# ---------------------------------------------------------------- pipeline

def analyze(rows, k=None, t0=None, tau_now=10.0, max_lag=600.0,
            resample_dt=None, lag_frac=0.5, block_s=120.0):
    segs = split_segments(rows)
    if not segs:
        raise SystemExit("No usable ramp segments found (need >=1 cooling and >=1 warming "
                         "with >=120 s span and >=3 C die-temp range)")
    result = {
        "segments": [], "have_cooling": False, "have_warming": False,
        "parameters": {
            "resample": "linear interpolation onto uniform grid; interval = "
                        "--resample-dt if given, else max(0.5 s, raw median dt)",
            "resample_interval_s": resample_dt,
            "lag_search": "lags span -min(max_lag, lag_frac*ramp_span) .. +same",
            "lag_frac": lag_frac,
            "max_lag_s": max_lag,
            "bootstrap": "moving-block resampling over sliding sub-windows "
                         f"(block {block_s:.0f} s, 200 draws, seed 7)",
            "sign_convention": "lag > 0 = die temp LEADS crystal "
                               "(crystal trails die sensor)",
            "ppm_sign": "ppm trace sign-flipped per ramp so die_temp and ppm "
                        "trajectories move together (equivalent to |r| peak)",
        },
    }
    lag_estimates = []
    for name, block in segs:
        raw = raw_sample_stats(block)
        dt_rs = resample_dt if resample_dt is not None else max(0.5, raw["median_dt_s"])
        grid, tdie, ppm, dt = resample_uniform(block, dt_rs)
        span = float(grid[-1] - grid[0])
        eff_max_lag = min(max_lag, lag_frac * span)
        taus, rs = xcorr_curve(grid, tdie, ppm, eff_max_lag, dt)
        lag, rpeak, idx = parabolic_peak(taus, rs)
        flip = -1 if rpeak < 0 else 1        # per-ramp ppm sign flip (see parameters)
        hw = peak_halfwidth(taus, rs, idx)   # uncertainty (a)
        boot = bootstrap_lag(grid, tdie, ppm, eff_max_lag, dt, block_s=block_s)
        unc_a = float(max(hw, 0.5 * dt))     # peak half-width, sub-sample floor
        unc_b = (float(max(abs(lag - boot[0]), abs(boot[1] - lag)))
                 if boot else None)
        unc = max(unc_a, unc_b) if unc_b is not None else unc_a
        seg_res = {
            "segment": name,
            "n_samples_raw": raw["n_raw"],
            "raw_median_sample_interval_s": raw["median_dt_s"],
            "raw_sample_interval_range_s": [raw["min_dt_s"], raw["max_dt_s"]],
            "raw_sample_rate_hz": (1.0 / raw["median_dt_s"]
                                   if raw["median_dt_s"] > 0 else None),
            "resample_interval_s": dt,
            "span_s": float(block[-1][0] - block[0][0]),
            "die_temp_range_C": [float(min(r[1] for r in block)),
                                 float(max(r[1] for r in block))],
            "lag_search_window_s": float(eff_max_lag),
            "lead_s": float(lag),
            "peak_r_after_flip": float(rpeak * flip),
            "ppm_sign_flip": flip,
            "unc_a_peak_halfwidth_s": unc_a,
            "bootstrap_ci_s": [boot[0], boot[1]] if boot else None,
            "unc_b_bootstrap_halfwidth_s": unc_b,
            "uncertainty_s": float(unc),
            "lag_below_one_sample": bool(abs(lag) < dt),
            "one_sample_s": float(dt),
        }
        result["segments"].append(seg_res)
        result["have_cooling"] |= "cool" in name
        result["have_warming"] |= "warm" in name
        lag_estimates.append((lag, unc))

    # combined lag estimate (inverse-variance weight)
    comb, comb_sig = None, 0.0
    if lag_estimates:
        lags = np.array([l for l, _ in lag_estimates])
        sig = np.array([max(u, 0.5) for _, u in lag_estimates])
        w = 1.0 / sig ** 2
        comb = float(np.sum(w * lags) / np.sum(w))
        comb_sig = float(max(np.sqrt(1.0 / np.sum(w)), np.max(sig) * 0.5))
        result["combined"] = {"lead_s": comb, "uncertainty_s": comb_sig}

    hyst = hysteresis(segs)
    result["hysteresis"] = hyst
    if hyst:
        heq = hysteresis_time_equivalent(segs, hyst)
        result["hysteresis_time_equivalent_s"] = heq[0] if heq else None
        result["median_ramp_rate_C_per_s"] = heq[1] if heq else None

    if k is not None and t0 is not None:
        ppm_off, n_dw = dwell_offset_estimate(rows, k, t0)
        if ppm_off is not None:
            result["ppm_to_xtal"] = {
                "k_ppm_per_K2": k, "t0_C": t0,
                "dwell_static_offset_ppm": ppm_off, "dwell_points": n_dw,
                "method": "T_xtal = T0 - sqrt((ppm - offset)/k) (below-T0 branch)",
            }

    # ---- primary estimator: loop-area delay fit over the full series ----
    t_all = np.array([r[0] for r in rows])
    T_all = np.array([r[1] for r in rows])
    ppm_all = np.array([r[2] for r in rows])
    warm, cool = branch_masks(t_all, T_all)
    dt_all = float(np.median(np.diff(t_all)))
    df_max = min(max_lag, 0.25 * float(t_all[-1] - t_all[0]))
    if warm.any() and cool.any():
        df, df_jk = delay_fit_jackknife(t_all, T_all, ppm_all, warm, cool, df_max, dt_all)
        if df is not None:
            unc = float(max(df_jk or 0.0, df["systematic_floor_s"]))
            result["lag_primary"] = {
                "method": "loop-area delay fit (monotonic ppm(T), no k/T0 needed)",
                "lead_s": df["lead_s"],
                "jackknife_sigma_s": df_jk,
                "systematic_floor_s": df["systematic_floor_s"],
                "uncertainty_s": unc,
                "residual_loop_ppm_at_best_delay": df["min_loop_ppm"],
            }
    result["lag_xcorr_combined"] = result.get("combined")

    lead = result.get("lag_primary", {}).get("lead_s")
    lead_unc = result.get("lag_primary", {}).get("uncertainty_s")
    if lead is not None:
        result["ema"] = ema_recommendation(lead, lead - lead_unc, lead + lead_unc, tau_now)
        result["open_loop_transient_bound"] = transient_error_bound(segs, lead, k, t0)
    else:
        result["ema"] = ema_recommendation(None, None, None, tau_now)
        result["open_loop_transient_bound"] = None
    return result


def print_report(res):
    print("THERMAL LAG ANALYSIS — die temp (XOSC) vs external ppm error")
    print("=" * 68)
    for s in res["segments"]:
        print(f"\n[{s['segment']}]  n_raw={s['n_samples_raw']}  "
              f"raw dt median {s['raw_median_sample_interval_s']:.2f}s "
              f"({s['raw_sample_rate_hz']:.3f} Hz, range "
              f"{s['raw_sample_interval_range_s'][0]:.2f}..{s['raw_sample_interval_range_s'][1]:.2f}s)  "
              f"span={s['span_s']:.0f}s  dieT={s['die_temp_range_C'][0]:.1f}..{s['die_temp_range_C'][1]:.1f}C")
        print(f"  resample dt={s['resample_interval_s']:.2f}s (linear interp)  "
              f"lag window ±{s['lag_search_window_s']:.0f}s  "
              f"ppm sign flip={s['ppm_sign_flip']:+d}")
        print(f"  XCORR lag: die LEADS crystal by {s['lead_s']:+.2f} s "
              f"(peak r after flip={s['peak_r_after_flip']:+.2f})")
        print(f"  uncertainty (a) peak half-width: ±{s['unc_a_peak_halfwidth_s']:.2f} s")
        ci = s['bootstrap_ci_s']
        if ci:
            print(f"  uncertainty (b) sliding-block bootstrap: CI {ci[0]:+.1f}..{ci[1]:+.1f} s "
                  f"(half-width ±{s['unc_b_bootstrap_halfwidth_s']:.2f} s)")
        else:
            print("  uncertainty (b) sliding-block bootstrap: n/a (insufficient windows)")
        print(f"  total uncertainty ±{s['uncertainty_s']:.2f} s")
        if s["lag_below_one_sample"]:
            print(f"  NOTE: |lag| < 1 sample -> report as '< 1 sample = "
                  f"{s['one_sample_s']:.2f} s'")
    if "combined" in res and res["combined"]:
        c = res["combined"]
        print(f"\nXCORR CROSS-CHECK (per-ramp, detrended trajectories): combined "
              f"{c['lead_s']:+.1f} ± {c['uncertainty_s']:.1f} s")
    if res.get("lag_primary"):
        p = res["lag_primary"]
        jk = f"± {p['jackknife_sigma_s']:.1f}" if p.get("jackknife_sigma_s") is not None else "n/a"
        print(f"PRIMARY LAG (loop-area delay fit): die leads crystal by {p['lead_s']:+.1f} s "
              f"(jackknife {jk} s, systematic floor ±{p['systematic_floor_s']:.1f} s, "
              f"total ±{p['uncertainty_s']:.1f} s; residual loop "
              f"{p['residual_loop_ppm_at_best_delay']:.3f} ppm)")
        if res.get("lag_xcorr_combined"):
            xc = res["lag_xcorr_combined"]
            d = abs(p["lead_s"] - xc["lead_s"])
            print(f"  method agreement: |delay-fit - xcorr| = {d:.1f} s "
                  f"({'consistent' if d <= max(p['uncertainty_s'], xc['uncertainty_s']) else 'INCONSISTENT — investigate'})")
    if res.get("hysteresis"):
        h = res["hysteresis"]
        print(f"HYSTERESIS: median ΔT_die at matched ppm = {h['median_dT_C']:+.2f} C "
              f"(IQR {h['iq_dT_C']:.2f} C, max |ΔT| {h['max_abs_dT_C']:.2f} C over "
              f"{len(h['levels_ppm'])} ppm levels)")
        if res.get("hysteresis_time_equivalent_s") is not None:
            print(f"  time equivalent ≈ {res['hysteresis_time_equivalent_s']:+.1f} s "
                  f"at median ramp rate {res['median_ramp_rate_C_per_s']:.3f} C/s")
    if "ppm_to_xtal" in res:
        p = res["ppm_to_xtal"]
        print(f"K/T0 CONVERSION: k={p['k_ppm_per_K2']} ppm/K^2, T0={p['t0_C']} C, "
              f"static offset={p['dwell_static_offset_ppm']:+.2f} ppm from {p['dwell_points']} dwell pts")
    e = res["ema"]
    print(f"\nEMA RECOMMENDATION: tau = {e['recommended_tau_s']} s "
          f"(current {tau_now_txt(e)} s) — {e['note']}")
    b = res.get("open_loop_transient_bound")
    if b:
        if "bound_ppm" in b and b.get("bound_ppm") is not None:
            print(f"OPEN-LOOP TRANSIENT BOUND: {b['bound_ppm']:.2f} ppm during worst ramp "
                  f"({b['worst_ramp_rate_C_per_s']:.3f} C/s at {b['at_die_temp_C']:.1f} C, "
                  f"sens {b.get('sensitivity_ppm_per_K', float('nan')):.2f} ppm/K, lead {b['lead_s']:.1f} s)")
        elif b.get("bound_ppm_per_k") is not None:
            print(f"OPEN-LOOP TRANSIENT BOUND: {b['bound_ppm_per_k']:.1f} ppm per unit k "
                  f"during worst ramp ({b['worst_ramp_rate_C_per_s']:.3f} C/s, lead {b['lead_s']:.1f} s) "
                  f"— supply --k/--t0 for an absolute bound")


def tau_now_txt(e):
    cur = e.get("change_from_current")
    return str(cur) if cur is not None else str(e["recommended_tau_s"])


# ---------------------------------------------------------------- self-test

def _first_order(x, dt, tau):
    alpha = 1.0 - math.exp(-dt / tau)
    y = np.empty_like(x)
    y[0] = x[0]
    for i in range(1, len(x)):
        y[i] = y[i - 1] + alpha * (x[i] - y[i - 1])
    return y


def _make_synthetic(planted_tau, dt=2.0, seed=42):
    """Synthetic ramp session (SELF-TEST ONLY — never a hardware measurement):
    three ramps with dwell plateaus; crystal temp = first-order lag of die temp;
    ppm follows the AT-cut parabola of the (lagged) crystal temp."""
    K, T0 = 0.034, 25.0
    rng = np.random.default_rng(seed)
    profiles = [("cooling", 25.0, -20.0, 0.025), ("warming", -20.0, 5.0, 0.030),
                ("cooling", 5.0, -20.0, 0.022)]
    t, t_series, tdie_series, seg_ids = 0.0, [], [], []
    for name, tstart, tend, rate in profiles:
        n = int(abs(tend - tstart) / rate / dt)
        for i in range(n):
            t_series.append(t)
            tdie_series.append(tstart + (tend - tstart) * (i / n))
            t += dt
        for _ in range(60):
            t_series.append(t)
            tdie_series.append(tend)
            t += dt
        seg_ids += [name] * n + ["dwell"] * 60
    tdie = np.array(tdie_series)
    t_s = np.array(t_series)
    tdie_meas = tdie + rng.normal(0, 0.15, len(tdie))   # die-sensor noise
    txtal = _first_order(tdie, dt, planted_tau)          # crystal lags the die
    ppm = K * (txtal - T0) ** 2 + rng.normal(0, 0.05, len(tdie))
    seg_ids = (seg_ids + ["dwell"] * (len(tdie) - len(seg_ids)))[:len(tdie)]
    return K, T0, [(float(t_s[i]), float(tdie_meas[i]), float(ppm[i]),
                    seg_ids[i], "") for i in range(len(tdie))]


def self_test():
    all_ok = True

    # ---------------- scenario A: planted 25 s crystal lag (dt = 2 s) --------
    PLANTED = 25.0
    K, T0, rows = _make_synthetic(PLANTED)
    res = analyze(rows, k=K, t0=T0, tau_now=10.0, max_lag=300.0)
    print("SELF-TEST scenario A (synthetic only — NOT a hardware measurement): "
          f"planted die lead = {PLANTED:.1f} s")
    print_report(res)
    comb = res["combined"]
    err = abs(comb["lead_s"] - PLANTED)
    ok_a = comb["lead_s"] > 0 and err <= 12.0
    covered = (comb["lead_s"] - comb["uncertainty_s"] <= PLANTED
               <= comb["lead_s"] + comb["uncertainty_s"])
    prim = res.get("lag_primary")
    ok_prim = prim is not None and abs(prim["lead_s"] - PLANTED) <= 3.0
    ok_hyst = (res["hysteresis"] is not None
               and res["hysteresis"]["median_dT_C"] > 0.05)
    fields_ok = all(
        set(s) >= {"n_samples_raw", "raw_median_sample_interval_s",
                   "raw_sample_rate_hz", "resample_interval_s",
                   "lag_search_window_s", "ppm_sign_flip",
                   "unc_a_peak_halfwidth_s", "unc_b_bootstrap_halfwidth_s",
                   "lag_below_one_sample", "one_sample_s"}
        for s in res["segments"])
    prim_str = (f"loop-area cross-check {prim['lead_s']:+.1f} s"
                if prim else "loop-area cross-check n/a")
    print(f"\nscenario A: xcorr combined {comb['lead_s']:+.1f} ± "
          f"{comb['uncertainty_s']:.1f} s vs planted {PLANTED:.0f} s "
          f"(|err| {err:.2f} s, CI covers planted: {covered}); {prim_str}")
    print(f"  checks: xcorr ok={ok_a} fields ok={fields_ok} "
          f"loop-area(±3s) ok={ok_prim} hysteresis ok={ok_hyst}")
    all_ok &= ok_a and fields_ok and ok_prim and ok_hyst

    # -------- scenario B: planted 0.5 s lag, below one sample (dt = 2 s) -----
    # At sub-sample planted lag the detrended-shape xcorr is noise-dominated:
    # the honest assertions are (i) the loop-area cross-check recovers ~0,
    # (ii) the xcorr CI covers the planted value, (iii) the '< 1 sample' flag
    # logic is self-consistent with whatever point estimates occur.
    PLANTED_B = 0.5
    _, _, rows_b = _make_synthetic(PLANTED_B, seed=43)
    res_b = analyze(rows_b, max_lag=300.0)
    comb_b = res_b["combined"]
    flags = [s["lag_below_one_sample"] for s in res_b["segments"]]
    ok_flag = all(f == (abs(s["lead_s"]) < s["resample_interval_s"])
                  for f, s in zip(flags, res_b["segments"]))
    prim_b = res_b.get("lag_primary")
    ok_prim_b = prim_b is not None and abs(prim_b["lead_s"]) <= 3.0
    ok_cover_b = (comb_b is not None
                  and comb_b["lead_s"] - comb_b["uncertainty_s"] <= PLANTED_B
                  <= comb_b["lead_s"] + comb_b["uncertainty_s"])
    ok_b = ok_flag and ok_prim_b and ok_cover_b
    comb_b_str = (f"{comb_b['lead_s']:+.2f} ± {comb_b['uncertainty_s']:.1f} s"
                  if comb_b is not None else "n/a (no segments)")
    prim_b_str = (f"{prim_b['lead_s']:+.2f} s" if prim_b else "n/a")
    print(f"\nscenario B (synthetic only): planted {PLANTED_B:.1f} s < 1 sample "
          f"(dt=2.00 s) -> xcorr combined {comb_b_str} (CI covers planted: "
          f"{ok_cover_b}); loop-area cross-check {prim_b_str}; "
          f"'< 1 sample' flagged on {sum(flags)}/{len(flags)} ramps "
          f"(flag fires on point estimates; here uncertainty subsumes zero); "
          f"flag logic ok={ok_flag}")
    print(f"  checks: sub-sample recovery ok={ok_b}")
    all_ok &= ok_b

    status = "SELF-TEST PASS" if all_ok else "SELF-TEST FAIL"
    print(status)
    return 0 if all_ok else 1


# -------------------------------------------------------------------- main

def main():
    ap = argparse.ArgumentParser(description=(__doc__ or "").splitlines()[0])
    ap.add_argument("--csv", help="ramp CSV (timestamp_s, die_temp_c, ppm_err, [phase], [fallback])")
    ap.add_argument("--json", help="optional JSON output path")
    ap.add_argument("--k", type=float, help="fitted k in ppm/K^2 (sibling task deliverable)")
    ap.add_argument("--t0", type=float, help="fitted T0 in C")
    ap.add_argument("--tau-now", type=float, default=10.0, help="current SelfCal EMA tau (default 10 s)")
    ap.add_argument("--max-lag", type=float, default=600.0, help="max lag searched, s (default 600)")
    ap.add_argument("--resample-dt", type=float, default=None,
                    help="uniform resample interval in s (default: max(0.5, raw median dt)); "
                         "task suggestion 0.5-1.0 s")
    ap.add_argument("--lag-frac", type=float, default=0.5,
                    help="lag search window = lag_frac * ramp span (default 0.5)")
    ap.add_argument("--block-s", type=float, default=120.0,
                    help="bootstrap sub-window block length in s (default 120)")
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

    overrides = {}
    for key, val in (("timestamp_s", args.c_ts), ("phase", args.c_ph),
                     ("die_temp_c", args.c_td), ("ppm_err", args.c_ppm),
                     ("fallback", args.c_fb)):
        if val:
            overrides[key] = val
    rows = load_csv(args.csv, overrides)
    res = analyze(rows, k=args.k, t0=args.t0, tau_now=args.tau_now,
                  max_lag=args.max_lag, resample_dt=args.resample_dt,
                  lag_frac=args.lag_frac, block_s=args.block_s)
    print_report(res)
    if args.json:
        with open(args.json, "w") as fh:
            json.dump(res, fh, indent=2)
        print(f"\nJSON written: {args.json}")


if __name__ == "__main__":
    main()
