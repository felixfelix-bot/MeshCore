#!/usr/bin/env python3
"""passive_mapper bench-calibration library (stdlib only).

Everything here is host-side and hardware-free: blob (de)serialisation that must
byte-match `SelfCal` in examples/passive_mapper/host/SelfCal.h, serial-CLI line
parsers, the k/T0 curve fit, the passband-window reduction and the die-vs-crystal
lag estimator. thermal_bench.py is the CLI on top; test_calib.py exercises all of
it against synthetic data with known ground truth.

SIGN CONVENTION (load-bearing, see SelfCal.h):
    drift_ppm(T)          = -k*(T-T0)^2      # crystal is SLOW away from turnover
    required_offset_ppm(T) = +k*(T-T0)^2      # RX must be programmed HIGH
    k >= 0 is the MAGNITUDE of the quadratic coefficient, T0 is the turnover in C.
The fit below works on *required compensation*, i.e. the negation of a measured
crystal drift.
"""

import math
import struct

BLOB_SIZE = 15
CAL_MAGIC = 0x5343  # 'SC'
BLOB_STRUCT = "<fffHB"  # k, T0, spare, magic, version

# ---------------------------------------------------------------------------
# calibration blob (must match SelfCal::storeCalibration/loadCalibration)
# ---------------------------------------------------------------------------


def pack_blob(k, t0, version=0):
    """Serialise {k,T0} into the 15-byte /selfcal.dat layout."""
    if k < 0.0:
        raise ValueError("k must be >= 0 (magnitude): got %r" % (k,))
    if not (0.0 <= version <= 255):
        raise ValueError("version out of range: %r" % (version,))
    return struct.pack(BLOB_STRUCT, float(k), float(t0), 0.0, CAL_MAGIC, int(version))


def unpack_blob(blob):
    if len(blob) != BLOB_SIZE:
        raise ValueError("blob must be %d bytes, got %d" % (BLOB_SIZE, len(blob)))
    k, t0, _spare, magic, version = struct.unpack(BLOB_STRUCT, blob)
    if magic != CAL_MAGIC:
        raise ValueError("bad magic 0x%04X (expected 0x%04X)" % (magic, CAL_MAGIC))
    return {"k": k, "t0": t0, "version": version}


def cal_command(k, t0):
    """The exact serial-CLI line that persists this calibration on the module."""
    return "cal %.6g %.2f" % (float(k), float(t0))


def required_offset_ppm(t_c, k, t0):
    return k * (t_c - t0) * (t_c - t0)


def drift_ppm(t_c, k, t0):
    return -required_offset_ppm(t_c, k, t0)


# ---------------------------------------------------------------------------
# serial CLI line parsers (MyMesh::handleCommand reply formats)
# ---------------------------------------------------------------------------

def _parse_kv(line):
    out = {}
    for tok in line.strip().split():
        if "=" in tok:
            key, val = tok.split("=", 1)
            out[key] = val
    return out


def parse_calshow(line):
    """`cal valid=yes k=0.04 T0=25.00C range=+/-80C die_temp=-40.0 off_hz=146982`"""
    kv = _parse_kv(line)
    if "valid" not in kv or "die_temp" not in kv:
        raise ValueError("not a calshow reply: %r" % (line,))
    return {
        "valid": kv.get("valid") == "yes",
        "k": float(kv["k"]),
        "t0": float(kv["T0"].rstrip("C")),
        "range_c": float(kv["range"].split("/-")[-1].rstrip("C")),
        "die_temp_c": float(kv["die_temp"]),
        "off_hz": float(kv["off_hz"]),
    }


def parse_status(line):
    """`mode=MAP distinct=3 logged=120 dropped=0 buf=0 bw=62.5 die_temp=-40.1 off_hz=... cal=yes`"""
    kv = _parse_kv(line)
    if "logged" not in kv:
        raise ValueError("not a status reply: %r" % (line,))
    bw_raw = kv.get("bw", "0")
    return {
        "mode": kv.get("mode", "?"),
        "distinct": int(kv.get("distinct", 0)),
        "logged": int(kv["logged"]),
        "dropped": int(kv.get("dropped", 0)),
        "buf": int(kv.get("buf", 0)),
        "bw_khz": float(bw_raw.split("(")[0]),
        "fallback": "(fallback)" in bw_raw,
        "die_temp_c": float(kv.get("die_temp", 0.0)),
        "off_hz": float(kv.get("off_hz", 0.0)),
        "cal_valid": kv.get("cal") == "yes",
    }


# ---------------------------------------------------------------------------
# k/T0 fit:  required_offset_ppm(T) = k*(T-T0)^2   (k >= 0, T0 free)
#            required_offset_ppm(T) = k*(T-T0)^2 + b   (T0 fixed)
# ---------------------------------------------------------------------------

MIN_POINTS = 3
MIN_SPAN_C = 25.0


def fit_curve(points, t0_fixed=None, t0_min=-60.0, t0_max=120.0):
    """Fit the AT-cut parabola to [(temp_C, required_offset_ppm), ...].

    t0_fixed=None  -> 2-parameter fit (k, T0) by grid search over T0 with an
                      exact 1-parameter least squares inside (k >= 0).
    t0_fixed=x     -> linear 2-parameter fit (k, bias) with T0 pinned.

    Returns a dict with k, t0, bias_ppm, rms_ppm, warnings and
    brackets_turnover (False means T0 is not identifiable from this data - the
    crystal drift is monotonic on one side of the turnover, so any single-sided
    sweep can be explained by many (k, T0) pairs).
    """
    pts = [(float(t), float(y)) for t, y in points]
    if len(pts) < MIN_POINTS:
        raise ValueError("need >= %d points, got %d" % (MIN_POINTS, len(pts)))
    temps = [t for t, _ in pts]
    span = max(temps) - min(temps)
    warnings = []
    if span < MIN_SPAN_C:
        warnings.append(
            "temperature span is only %.1f C (<%.0f C): k and T0 are poorly "
            "conditioned; sweep further apart" % (span, MIN_SPAN_C))

    if t0_fixed is None:
        best = None
        for coarse in _frange(t0_min, t0_max, 0.5):
            cand = _fit_k_only(pts, coarse)
            if best is None or cand["rms_ppm"] < best["rms_ppm"]:
                best = cand
        centre = best["t0"]
        for fine in _frange(centre - 0.6, centre + 0.6, 0.01):
            cand = _fit_k_only(pts, fine)
            if cand["rms_ppm"] < best["rms_ppm"]:
                best = cand
        bias = 0.0
    else:
        best = _fit_k_and_bias(pts, float(t0_fixed))
        bias = best["bias_ppm"]

    k, t0, rms = best["k"], best["t0"], best["rms_ppm"]
    brackets = min(temps) < t0 < max(temps)
    if not brackets:
        warnings.append(
            "fit temperature range [%.1f, %.1f] does not straddle the fitted "
            "turnover T0=%.1f C: T0 is unidentifiable, treat k/T0 as a "
            "one-sided approximation only" % (min(temps), max(temps), t0))
    if rms > 10.0:
        warnings.append(
            "residual %.1f ppm exceeds the 10 ppm accuracy budget - the "
            "parabola does not describe this module (measurement error, or the "
            "sensor is tracking the die and not the crystal)" % rms)
    return {
        "k": k,
        "t0": t0,
        "bias_ppm": bias,
        "rms_ppm": rms,
        "n_points": len(pts),
        "t_span_c": span,
        "t_min_c": min(temps),
        "t_max_c": max(temps),
        "t0_fixed": t0_fixed,
        "brackets_turnover": brackets,
        "warnings": warnings,
    }


def _fit_k_only(pts, t0):
    """Least-squares k for fixed T0, no bias term."""
    sxy = sxx = 0.0
    for t, y in pts:
        x = (t - t0) * (t - t0)
        sxy += x * y
        sxx += x * x
    k = sxy / sxx if sxx > 0.0 else 0.0
    if k < 0.0:
        k = 0.0
    rms = _rms(pts, lambda t: k * (t - t0) * (t - t0))
    return {"k": k, "t0": t0, "rms_ppm": rms, "bias_ppm": 0.0}


def _fit_k_and_bias(pts, t0):
    """Exact 2x2 normal equations for y = k*x + b with x = (t-T0)^2."""
    n = float(len(pts))
    sx = sy = sxx = sxy = 0.0
    for t, y in pts:
        x = (t - t0) * (t - t0)
        sx += x
        sy += y
        sxx += x * x
        sxy += x * y
    det = sxx * n - sx * sx
    if abs(det) < 1e-12:
        return {"k": 0.0, "t0": t0, "bias_ppm": 0.0, "rms_ppm": float("inf")}
    k = (sxy * n - sx * sy) / det
    b = (sxx * sy - sx * sxy) / det
    if k < 0.0:  # magnitude convention: clamp, keep the bias as fitted
        k = 0.0
        b = sy / n
    rms = _rms(pts, lambda t: k * (t - t0) * (t - t0) + b)
    return {"k": k, "t0": t0, "bias_ppm": b, "rms_ppm": rms}


def _rms(pts, model):
    s = 0.0
    for t, y in pts:
        d = model(t) - y
        s += d * d
    return math.sqrt(s / len(pts))


def _frange(lo, hi, step):
    n = int(round((hi - lo) / step))
    return [lo + i * step for i in range(n + 1)]


# ---------------------------------------------------------------------------
# passband window reduction (reference-TX frequency sweep vs DUT packet count)
# ---------------------------------------------------------------------------

def find_passband_window(steps, nominal_hz, nominal_width_hz=None, threshold=0.5):
    """Reduce [(ref_freq_hz, capture_ratio), ...] to the DUT's passband window.

    The DUT decodes the reference while |f_ref - f_DUT_LO| < BW/2, so the
    accepted band in *reference* frequency is centred on the DUT's real LO:

        center_hz = f_DUT_LO ;  drift_ppm = (center_hz - nominal_hz)/nominal_hz*1e6

    Returns None when the sweep shows no window (wrong SF/BW, no packets, PA
    saturated, ...). One-sided windows (the sweep started inside the window) are
    closed using nominal_width_hz when supplied.
    """
    rows = sorted(((float(f), float(r)) for f, r in steps), key=lambda r: r[0])
    if not rows:
        return None
    peak = max(r for _, r in rows)
    if peak <= 0.0:
        return None
    level = peak * threshold
    freqs = [f for f, _ in rows]
    ratios = [r for _, r in rows]

    edges = []
    for i in range(1, len(rows)):
        r0, r1 = ratios[i - 1], ratios[i]
        if (r0 - level) * (r1 - level) < 0.0:
            f0, f1 = freqs[i - 1], freqs[i]
            frac = (level - r0) / (r1 - r0)
            edges.append(f0 + frac * (f1 - f0))

    step_hz = (freqs[-1] - freqs[0]) / max(1, len(freqs) - 1)
    if len(edges) >= 2:
        low, high = edges[0], edges[-1]
    elif len(edges) == 1 and nominal_width_hz:
        # only one crossing seen: assume the nominal capture width
        if ratios[0] > level:          # started inside -> missing low edge
            high, low = edges[0], edges[0] - nominal_width_hz
        else:                          # ended inside -> missing high edge
            low, high = edges[0], edges[0] + nominal_width_hz
    else:
        return None
    return {
        "center_hz": 0.5 * (low + high),
        "edge_low_hz": low,
        "edge_high_hz": high,
        "width_hz": high - low,
        "offset_hz": 0.5 * (low + high) - nominal_hz,
        "offset_ppm": (0.5 * (low + high) - nominal_hz) / nominal_hz * 1e6,
        "peak_ratio": peak,
        "step_hz": step_hz,
        "resolution_ppm": abs(step_hz) / nominal_hz * 1e6,
        "n_steps": len(rows),
    }


def match_reference(fitted_ppm, reference_ppm):
    """DUT-vs-reference offset: the reference is only a reference to the extent
    its own crystal is at turnover (see bench/README.md)."""
    return fitted_ppm - reference_ppm


# ---------------------------------------------------------------------------
# die-vs-crystal lag (ramp/step response)
# ---------------------------------------------------------------------------

MIN_EXCITATION_C = 8.0     # die-temp span below which tau is not resolvable
MIN_IMPROVEMENT = 0.2      # the lagged model must cut this fraction of the residual
NOISE_FLOOR_PPM = 0.05     # residual below this is "model fits exactly", not signal


def fit_lag(times_s, temp_c, offset_ppm, k, t0, max_lag_s=300.0):
    """Estimate the crystal's thermal time constant from a ramp/step log.

    temp_c    : raw die temperature series (C), uniform sampling
    offset_ppm: measured required compensation at the same instants (ppm)
    k, t0     : the fitted model parameters; used to build the temperature-only
                prediction whose lag is being measured

    Method: the crystal's frequency response is a first-order lag of the die
    sensor, so simulate a 1-pole filter on the die temperature and pick the tau
    whose prediction of the measured compensation has the lowest RMS residual.
    That tau IS the number SelfCal's TEMP_TC_SECS (10 s) must match.

    A derivative cross-correlation delay estimator was tried first and dropped on
    the evidence: on synthetic data with a KNOWN 45 s lag it reported |r| = 0.05
    for an ideal step (no peak at all), and for a slow ambient ramp it peaked at
    r = -0.68 on the EDGE of the search window and was still -0.90 one sample
    beyond it - i.e. it reported the window boundary, not a lag. Both stimuli
    give broad derivative pulses, so the correlation peak carries no information;
    the residual fit recovers the same tau exactly on both. `lag_s` is therefore
    the fitted 1-pole constant, and identifiability is gated on excitation size
    and model improvement, not on a correlation peak.
    """
    n = len(times_s)
    if n < 8 or len(temp_c) != n or len(offset_ppm) != n:
        return {"ok": False, "reason": "need >=8 samples of (time, temp, offset)"}
    order = sorted(range(n), key=lambda i: times_s[i])
    t = [times_s[i] for i in order]
    T = [temp_c[i] for i in order]
    Y = [offset_ppm[i] for i in order]
    dt = (t[-1] - t[0]) / (n - 1)
    if dt <= 0:
        return {"ok": False, "reason": "non-increasing timestamps"}

    span_c = max(T) - min(T)
    rms_no_lag = _rms_pts([(Y[i], required_offset_ppm(T[i], k, t0)) for i in range(n)])

    best = None
    for tau in _frange(1.0, max_lag_s, 1.0):
        filt = _one_pole(T, dt, tau)
        rms = _rms_pts([(Y[i], required_offset_ppm(filt[i], k, t0)) for i in range(n)])
        if best is None or rms < best[1]:
            best = (tau, rms)
    tau_s, rms = best
    tau_at_edge = tau_s >= max_lag_s - 1.0

    if rms_no_lag > NOISE_FLOOR_PPM:
        improvement_frac = 1.0 - rms / rms_no_lag
    else:
        improvement_frac = 0.0
    improved = rms_no_lag > NOISE_FLOOR_PPM and improvement_frac >= MIN_IMPROVEMENT
    identifiable = span_c >= MIN_EXCITATION_C and improved and not tau_at_edge
    lag_s = round(tau_s, 1) if identifiable else None

    notes = []
    if span_c < MIN_EXCITATION_C:
        notes.append(
            "not enough thermal excitation (die span %.1f C < %.1f C): tau is not "
            "resolvable from this log - ramp the module over a wider excursion "
            "(freezer sweep) or step it (TX power / hot-air step) and log again"
            % (span_c, MIN_EXCITATION_C))
    if rms_no_lag <= NOISE_FLOOR_PPM:
        notes.append(
            "the measured compensation matches the no-lag model to %.3f ppm: "
            "either the sample rate is far slower than the lag, or the logged "
            "column is the model output rather than a measurement"
            % rms_no_lag)
    elif not improved:
        notes.append(
            "the lagged model does not improve on the plain model (%.2f ppm vs "
            "%.2f ppm rms): the die sensor and the crystal are thermally coupled "
            "well enough that no separate lag is resolvable at this "
            "stimulus/sample rate" % (rms, rms_no_lag))
    if tau_at_edge:
        notes.append(
            "tau is pinned at the edge of the search window (%.0f s): re-run "
            "with a larger --max-lag-s" % max_lag_s)

    return {
        "ok": rms <= rms_no_lag and not tau_at_edge,
        "tau_s": tau_s,
        "rms_ppm": rms,
        "rms_no_lag_ppm": rms_no_lag,
        "improvement_frac": improvement_frac,
        "lag_s": lag_s,
        "lag_identifiable": identifiable,
        "excitation_span_c": span_c,
        "tau_at_search_edge": tau_at_edge,
        "dt_s": dt,
        "n": n,
        "warnings": (
            ["lag estimate is quantised by the sample interval (%.1f s)" % dt]
            if dt > 10 else []
        ),
        "notes": notes,
    }


def _one_pole(x, dt, tau):
    alpha = 1.0 - math.exp(-dt / tau)
    out = [x[0]]
    for i in range(1, len(x)):
        out.append(out[-1] + (x[i] - out[-1]) * alpha)
    return out


def _rms_pts(pairs):
    s = 0.0
    for a, b in pairs:
        s += (a - b) * (a - b)
    return math.sqrt(s / len(pairs))


# ---------------------------------------------------------------------------
# ramp hysteresis: the lag that IS measurable on a bench
# ---------------------------------------------------------------------------

def crossing_temp(times, temp, ratio, threshold=0.5, rising=True, last=False):
    """Die temperature at which the reception ratio crosses `threshold`.

    rising=True  -> the entry edge (reception starts as the crystal crosses into
                    the capture window, the up-sweep case)
    rising=False -> the exit edge (reception stops again, the down-sweep case)
    Returns None when the series never crosses, i.e. the injected offset was never
    inside the capture window during this ramp - that ramp carries no information
    and must not be silently treated as "no lag".

    last=True takes the LAST crossing instead of the first (a full sweep through
    the band crosses twice; without this the caller can compare the wrong edge).
    """
    idx = range(len(times) - 1, 0, -1) if last else range(1, len(times))
    for i in idx:
        a, b = ratio[i - 1], ratio[i]
        hit = (a < threshold <= b) if rising else (a >= threshold > b)
        if not hit:
            continue
        span = b - a
        f = 0.0 if span == 0.0 else (threshold - a) / span
        return temp[i - 1] + (temp[i] - temp[i - 1]) * f
    return None


def ramp_rate_k_per_s(times, temp):
    """Median |dT/dt| of a logged ramp (K/s). Median, not mean: the soak at each
    end of the sweep is ~0 K/s and would drag a mean rate toward zero."""
    rates = []
    for i in range(len(times) - 1):
        dt = times[i + 1] - times[i]
        if dt > 0:
            rates.append(abs((temp[i + 1] - temp[i]) / dt))
    if not rates:
        return 0.0
    rates.sort()
    return rates[len(rates) // 2]


def fit_edge_hysteresis(up, down, threshold=0.5, min_rate_k_per_s=0.002):
    """tau from the up/down shift of one reception edge (thermal hysteresis).

    up / down : (times_s, die_temp_c, ratio) triples for a heating and a cooling
                sweep of the SAME injected offset over the same temperature span.

    The crystal temperature is die_temp - tau*dT/dt, so one physical band edge
    appears at a die temperature tau*rate HIGHER on the up-sweep (crystal colder
    than the sensor) and tau*rate LOWER on the down-sweep (crystal warmer). The
    die-temperature gap between the two crossings is therefore

        dT_edge = tau * (rate_up + rate_down)   ->   tau = dT_edge/(rate_up+rate_down)

    This needs only a reception flag vs die temperature, so it works with a plain
    reference transmitter and needs no per-point soak: the two ramps ARE the
    experiment. Slow ramps (few K/min) are fine as long as the clock is stable;
    it is the *sensor-to-crystal* lag that is being measured, and a slow ramp
    makes it small but still resolvable, whereas the residual fit needs the ramp.
    """
    notes = []
    if len(up[0]) < 8 or len(down[0]) < 8:
        return {"ok": False, "reason": "need >=8 samples in each ramp"}
    rate_up = ramp_rate_k_per_s(up[0], up[1])
    rate_dn = ramp_rate_k_per_s(down[0], down[1])
    if rate_up < min_rate_k_per_s or rate_dn < min_rate_k_per_s:
        return {"ok": False,
                "reason": "ramp rate too low (%.4f / %.4f K/s): move the module "
                          "faster than %.3f K/s, or the hysteresis is below the "
                          "sensor resolution" % (rate_up, rate_dn, min_rate_k_per_s)}
    # Heating sweeps INTO the band from the cold side (first rising crossing);
    # cooling from the hot side exits it at the SAME cold band edge (last falling
    # crossing). Comparing anything else compares two different band edges.
    t_edge_up = crossing_temp(up[0], up[1], up[2], threshold, rising=True, last=False)
    t_edge_dn = crossing_temp(down[0], down[1], down[2], threshold, rising=False,
                              last=True)
    if t_edge_up is None or t_edge_dn is None:
        notes.append("no reception edge in the %s sweep: the injected offset never "
                     "entered the capture window during that ramp, so it carries no "
                     "lag information - check the reference is transmitting and the "
                     "injected offset is within a half-window of the requirement"
                     % ("up" if t_edge_up is None else "down"))
        return {"ok": False, "reason": notes[-1], "notes": notes,
                "rate_up_k_per_s": rate_up, "rate_down_k_per_s": rate_dn}
    dT = t_edge_up - t_edge_dn
    tau = dT / (rate_up + rate_dn)
    if tau < 0:
        notes.append("the edges are INVERTED (up-sweep edge %.1f C is colder than "
                     "the down-sweep edge %.1f C): the ramps were swapped, or the "
                     "die sensor leads the crystal in the wrong direction for this "
                     "setup" % (t_edge_up, t_edge_dn))
    if abs(rate_up - rate_dn) > 0.3 * max(rate_up, rate_dn):
        notes.append("ramp rates differ by %.0f%% (%.3f vs %.3f K/s): the tau above "
                     "assumes a constant rate over the edge, so re-run with a "
                     "matched pair before trusting it to better than ~30%%"
                     % (100.0 * abs(rate_up - rate_dn) / max(rate_up, rate_dn),
                        rate_up, rate_dn))
    return {
        "ok": tau > 0.0,
        "tau_s": tau,
        "lag_s": tau if tau > 0.0 else None,
        "lag_identifiable": tau > 0.0,
        "edge_up_c": t_edge_up,
        "edge_down_c": t_edge_dn,
        "delta_t_edge_c": dT,
        "rate_up_k_per_s": rate_up,
        "rate_down_k_per_s": rate_dn,
        "notes": notes,
    }
