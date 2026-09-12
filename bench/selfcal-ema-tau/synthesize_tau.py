#!/usr/bin/env python3
"""Synthesize the two parent thermal analyses (cross-correlation lag + hysteresis)
into one firmware-actionable recommendation for SelfCal's EMA time constant
TEMP_TC_SECS, plus an honest statement of open-loop transient limits.

Parents (this repo, committed):
  bench/thermal-lag/analyze_thermal_lag.py   -> per-ramp xcorr lag, loop-area
     delay fit (primary), EMA rec hooks      (REPORT.md: NO-DATA verdict)
  bench/thermal-hysteresis/hysteresis_fit.py -> dT at matched ppm levels,
     tau_hyst = dT/(r_warm+r_cool)           (REPORT.md: NO-DATA verdict)

Inputs (--lag-json / --hyst-json): the `--json` outputs of the two parents.
Missing files or missing fields are NOT errors: they produce a definitive
"not applicable because <reason>" field (fleet integrity rule: no TBDs, no
fabrication). Exit 0 for every definitive verdict; exit 2 only for malformed
JSON (structurally unreadable input).

CROSS-CHECK CONVENTION (important, corrects a parent-prose erratum):
  Both estimators measure the SAME quantity: the single die-sensor -> crystal
  effective-temperature lag tau.  For a first-order crystal lag tau and
  constant ramp slews r_w / r_c, matched-ppm (matched T_xtal) crossings obey
      T_die,w(L) - tau*r_w = T_die,c(L) + tau*r_c
  =>  dT(L) = tau*(r_w + r_c)   =>   tau_hyst = dT/(r_w+r_col) recovers tau.
  The hysteresis tool implements exactly this and its self-test recovers the
  planted single-ramp lag directly (planted 25 s -> tau_hyst 24.4 s).
  The note "tau_hyst ~ 2x the sibling's single-ramp xcorr lag" printed in the
  hysteresis REPORT.md / JSON is therefore an ERRATUM (the 2x lives in
  dT = 2*tau*r for equal slews; dividing by r_w+r_c removes it).  The two
  methods are compared 1:1 here.  (The lag tool's own
  hysteresis_time_equivalent = dT/median-single-rate IS ~2*tau and is halved
  before comparison if it is ever used as the hysteresis input.)

DISAGREEMENT FLAG: methods disagree when |lag_x - tau_hyst| exceeds the
1-sigma combined uncertainty sqrt(unc_x^2 + unc_h^2) (also reported at 2-sigma).

KEEP-OR-CHANGE RULE (mirrors analyze_thermal_lag.ema_recommendation exactly):
  tau_ema should approximate the measured die->crystal lag so the FILTERED
  die temperature tracks the crystal's effective temperature.
  rec = max(lag, ci_lo); if rec <= 2*tau_now: rec = max(rec, tau_now);
  round to 5 s.  KEEP when rec == tau_now; CHANGE otherwise.
  transient_limited = (ci_lo > 2*tau_now)  -> the unconditional limitation
  note must be quoted wherever the recommendation is cited.

Usage:
  python3 synthesize_tau.py [--lag-json bench/thermal-lag/lag.json]
                            [--hyst-json bench/thermal-hysteresis/hyst.json]
                            [--tau-now 10] [--json out.json]
  python3 synthesize_tau.py --self-test
"""

import argparse
import json
import math
import sys
import tempfile
import os

DEFAULT_LAG_JSON = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "thermal-lag", "lag.json")
DEFAULT_HYST_JSON = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                 "..", "thermal-hysteresis", "hyst.json")

FIRMWARE = {
    "constant": "TEMP_TC_SECS",
    "file": "examples/passive_mapper/host/SelfCal.h:47 (felixfelix-bot/MeshCore "
            "feat/passive-mapper @ d7ae93fa, verified by fresh ls-remote+fetch "
            "this session)",
    "value_now_s": 10.0,
    "update": "first-order EMA, alpha = 1 - exp(-dt/TEMP_TC_SECS) (SelfCal.h:118); "
              "compensation computed from the FILTERED temp: "
              "offset = +k*(T_ema - T0)^2 (SelfCal.h:133); output clamps: "
              "SLEW_PPM 25 / DEADBAND_PPM 1 / MAX_PPM 300 (SelfCal.h:48-50)",
    "closed_loop": "FEI residual path (SelfCal.feedMeasured) is inert on LR2021 "
                   "(never called; on-chip frequency-error estimate is a "
                   "verified dead end there) - open-loop has no backstop",
}


# ------------------------------------------------------------------ inputs

def load_json(path, label):
    """Return (dict|None, reason|None). Missing file -> (None, reason)."""
    if not os.path.isfile(path):
        return None, f"{label}: file not found: {path}"
    try:
        with open(path) as fh:
            return json.load(fh), None
    except (json.JSONDecodeError, OSError) as exc:
        raise SystemExit(f"MALFORMED {label} input ({path}): {exc}") from exc


def extract_lag(lag):
    """Per-ramp lags, primary (loop-area) and combined xcorr estimates."""
    if lag is None:
        return {"available": False, "reason": "lag JSON absent (see above)"}
    segs = lag.get("segments") or []
    per_ramp = [{"ramp": s.get("segment"),
                 "lead_s": s.get("lead_s"),
                 "unc_s": s.get("uncertainty_s"),
                 "unc_a_halfwidth_s": s.get("unc_a_peak_halfwidth_s"),
                 "unc_b_bootstrap_s": s.get("unc_b_bootstrap_halfwidth_s"),
                 "ci_s": s.get("bootstrap_ci_s")}
                for s in segs if s.get("lead_s") is not None]
    prim = lag.get("lag_primary") or {}
    comb = lag.get("combined") or {}
    out = {"available": bool(per_ramp or prim or comb), "per_ramp": per_ramp}
    if prim.get("lead_s") is not None:
        out["primary"] = {"lead_s": prim["lead_s"],
                          "unc_s": prim.get("uncertainty_s"),
                          "method": prim.get("method")}
    elif comb.get("lead_s") is not None:
        out["primary"] = {"lead_s": comb["lead_s"],
                          "unc_s": comb.get("uncertainty_s"),
                          "method": "combined xcorr (loop-area absent)"}
    else:
        out["reason"] = ("lag JSON present but contains no lead estimate "
                         "(analyzer emitted no lag)")
    return out


def extract_hyst(hyst):
    """tau_hyst = dT/(r_w+r_c) with CI; recovers the SINGLE die->crystal lag
    (see module docstring) -> compared 1:1 against the lag estimates."""
    if hyst is None:
        return {"available": False, "reason": "hysteresis JSON absent (see above)"}
    te = hyst.get("time_equivalent") or {}
    h = hyst.get("hysteresis") or {}
    ci = (hyst.get("bootstrap_ci") or {}).get("median_tau_hyst_s_p16_p84")
    tau = te.get("median_tau_hyst_s")
    out = {
        "available": tau is not None,
        "median_dT_C": h.get("median_dT_C"),
        "iqr_dT_C": h.get("iqr_dT_C"),
        "median_tau_hyst_s": tau,
        "iqr_tau_hyst_s": te.get("iqr_tau_hyst_s"),
        "median_dt_warming_s": te.get("median_dt_warming_s"),
        "median_dt_cooling_s": te.get("median_dt_cooling_s"),
        "slews_C_per_s": hyst.get("slew_rates_C_per_s"),
        "ci_s": ci,
    }
    if tau is not None and ci:
        out["unc_s"] = float(max(abs(tau - ci[0]), abs(ci[1] - tau)))
    if tau is None:
        out["reason"] = ("hysteresis JSON present but median_tau_hyst_s "
                         "absent (no matched-level crossing on both directions)")
    return out


# ------------------------------------------------------------- synthesis

def cross_check(lag_est, hyst_est):
    """1:1 comparison of the two methods (see docstring for the erratum)."""
    lx = lag_est.get("primary", {}).get("lead_s") if lag_est.get("available") else None
    lu = lag_est.get("primary", {}).get("unc_s") if lx is not None else None
    hx = hyst_est.get("median_tau_hyst_s") if hyst_est.get("available") else None
    hu = hyst_est.get("unc_s") if hx is not None else None
    if lx is None or hx is None:
        return {
            "flag": None,
            "status": "NOT APPLICABLE because at least one parent estimate is "
                      "absent (no two numbers exist to compare)",
            "lag_used_s": lx, "hyst_used_s": hx,
        }
    diff = lx - hx
    sig = math.sqrt((lu or 0.0) ** 2 + (hu or 0.0) ** 2)
    flag_1s = abs(diff) > sig
    flag_2s = abs(diff) > 2.0 * sig
    return {
        "flag": flag_1s,
        "status": ("DISAGREE beyond combined 1-sigma" if flag_1s else
                   "agree within combined 1-sigma"),
        "at_2sigma": ("also beyond 2-sigma" if flag_2s else
                      "within 2-sigma" if flag_1s else "within 1-sigma"),
        "lag_used_s": lx, "hyst_used_s": hx,
        "difference_s": diff,
        "combined_sigma_s": sig,
        "convention": "1:1 (tau_hyst recovers the single die->crystal lag; the "
                      "'~2x' note in hysteresis_fit.py output is an erratum - "
                      "its own self-test recovers the planted 25 s directly)",
    }


def keep_or_change(point, unc, tau_now, flagged):
    """Parent rule: rec = max(point, ci_lo); lifted to tau_now when within
    2x; rounded to 5 s.  A disagreement flag widens the CI to the union and
    marks the recommendation provisional."""
    if point is None:
        return {"action": "KEEP", "tau_s": tau_now,
                "change_from_current_s": None,
                "transient_limited": None,
                "provisional": False,
                "rule": "no measured lag exists -> keep current constant; "
                        "changing it on synthetic/self-test numbers would be "
                        "fabrication"}
    lo, hi = point - (unc or 0.0), point + (unc or 0.0)
    if flagged:
        lo = min(lo, point - 2.0 * (unc or 0.0))
        hi = max(hi, point + 2.0 * (unc or 0.0))
    rec = max(point, lo)
    if rec <= 2.0 * tau_now:
        rec = max(rec, tau_now)
    rec = float(5.0 * round(rec / 5.0))
    return {
        "action": "KEEP" if abs(rec - tau_now) < 1e-9 else "CHANGE",
        "tau_s": rec,
        "change_from_current_s": None if abs(rec - tau_now) < 1e-9 else tau_now,
        "ci_used_s": [lo, hi],
        "transient_limited": bool(lo > 2.0 * tau_now),
        "provisional": bool(flagged),
        "rule": "rec = max(lag, ci_lo), floored at tau_now when within 2x, "
                "rounded to 5 s" + ("; CI widened 2x (cross-method "
                                    "disagreement -> provisional)" if flagged else ""),
    }


def illustrative_transient_table():
    """Open-loop transient mis-compensation arithmetic, using the firmware's
    OWN sizing constants.  ILLUSTRATIVE ONLY - k is unmeasured (atcut-fit
    NO-FIT); these rows are formula evaluations, never measurements."""
    rows = []
    # Fork's own sizing case: k = 0.04 ppm/C^2 (SelfCal.h MAX_PPM comment:
    # "0.04*(25-(-56.5))^2 = 266 ppm"), |T - T0| = 40 C (ascent mid-band)
    for k, dT0, k_label in ((0.04, 40.0, "k=0.04 (fork sizing constant, NOT measured)"),
                            (0.034, 40.0, "k=0.034 (AT-cut family default, NOT measured)")):
        sens = 2.0 * k * dT0  # ppm per C
        for rate, r_label in ((0.0167, "0.017 C/s = 1 C/min (bench-style ramp)"),
                              (0.03, "0.03 C/s ~ 1.8 C/min (ISA-ascent order)")):
            for dtau in (10.0, 25.0):
                rows.append({
                    "k_label": k_label, "rate_label": r_label,
                    "mismatch_s": dtau,
                    "sensitivity_ppm_per_C": round(sens, 3),
                    "error_ppm": round(sens * rate * dtau, 2),
                })
    return rows


def synthesize(lag_path, hyst_path, tau_now):
    lag_raw, lag_reason = load_json(lag_path, "lag")
    hyst_raw, hyst_reason = load_json(hyst_path, "hyst")
    lag_est = extract_lag(lag_raw)
    if not lag_est.get("available") and lag_reason:
        lag_est["reason"] = f"NOT APPLICABLE because {lag_reason} - parent " \
                            f"bench ramp CSV never existed (committed NO-DATA verdict)"
    hyst_est = extract_hyst(hyst_raw)
    if not hyst_est.get("available") and hyst_reason:
        hyst_est["reason"] = f"NOT APPLICABLE because {hyst_reason} - parent " \
                             f"bench ramp CSV never existed (committed NO-DATA verdict)"
    cc = cross_check(lag_est, hyst_est)
    point = lag_est.get("primary", {}).get("lead_s") if lag_est.get("available") else None
    unc = lag_est.get("primary", {}).get("unc_s") if point is not None else None
    # with no lag estimate at all, fall back to tau_hyst as the point estimate
    if point is None and hyst_est.get("available"):
        point, unc = hyst_est["median_tau_hyst_s"], hyst_est.get("unc_s")
    rec = keep_or_change(point, unc, tau_now, cc["flag"] is True)
    return {
        "verdict": "MEASURED" if point is not None else "NO-DATA",
        "firmware": FIRMWARE,
        "tau_now_s": tau_now,
        "lag": lag_est,
        "hysteresis": hyst_est,
        "cross_check": cc,
        "recommendation": rec,
        "limitation_note": (
            "During fast temperature transients the open-loop compensation "
            "will lead or trail the crystal by the (un)matched portion of the "
            "die-vs-crystal lag: open-loop error ~ 2k|T-T0| * dT/dt * |lag - "
            "TEMP_TC_SECS|. The closed-loop CFO path cannot backstop this on "
            "LR2021 - the FEI residual path is inert there (verified dead "
            "end) - so the open-loop model's accuracy is transient-limited. "
            "With no measured lag, the current 10 s EMA's transient tracking "
            "error is UNQUANTIFIED; the illustrative rows bound the scale."),
        "illustrative_transient_rows_NOT_measurements": illustrative_transient_table(),
        "rerun_when_data_lands": (
            "python3 bench/thermal-lag/analyze_thermal_lag.py --csv <ramp.csv> "
            "--json bench/thermal-lag/lag.json && "
            "python3 bench/thermal-hysteresis/hysteresis_fit.py --csv <ramp.csv> "
            "--json bench/thermal-hysteresis/hyst.json && "
            "python3 bench/selfcal-ema-tau/synthesize_tau.py"),
    }


# ---------------------------------------------------------------- report

def _fmt(v, spec="+.1f"):
    return ("--" if v is None else format(v, spec))


def render_report(res):
    L = []
    w = L.append
    fw = res["firmware"]
    w("SELFCAL EMA TIME-CONSTANT RECOMMENDATION - synthesis of thermal-lag + hysteresis parents")
    w("=" * 88)
    w(f"VERDICT: {res['verdict']}   |   firmware constant: {fw['constant']} = "
      f"{fw['value_now_s']:.1f} s (now)")
    w(f"firmware: {fw['file']}")
    w("")
    w("INPUTS (parent deliverables)")
    w(f"  (a) per-ramp cross-correlation lag, seconds +/- uncertainty:")
    if res["lag"].get("available"):
        for r in res["lag"]["per_ramp"]:
            w(f"      {r['ramp']:<8} lag {_fmt(r['lead_s'])} s  unc {_fmt(r['unc_s'])} s")
        if "primary" in res["lag"]:
            p = res["lag"]["primary"]
            w(f"      primary ({p.get('method') or 'loop-area delay fit'}): "
              f"{_fmt(p['lead_s'])} +/- {_fmt(p['unc_s'])} s")
    else:
        w(f"      {res['lag'].get('reason')}")
    w(f"  (b) hysteresis magnitude, C and equivalent seconds:")
    if res["hysteresis"].get("available"):
        hh = res["hysteresis"]
        w(f"      median dT = {_fmt(hh['median_dT_C'], '+.2f')} C (IQR {_fmt(hh['iqr_dT_C'], '.2f')})"
          f"  ->  tau_hyst = {_fmt(hh['median_tau_hyst_s'])} s"
          + (f"  CI [{hh['ci_s'][0]:+.1f}, {hh['ci_s'][1]:+.1f}]" if hh.get("ci_s") else ""))
    else:
        w(f"      {res['hysteresis'].get('reason')}")
    w("")
    w("CROSS-METHOD CHECK (lag vs hysteresis-in-seconds)")
    cc = res["cross_check"]
    if cc["flag"] is None:
        w(f"  {cc['status']}")
    else:
        w(f"  lag {_fmt(cc['lag_used_s'])} s vs tau_hyst {_fmt(cc['hyst_used_s'])} s: "
          f"{cc['status']} (diff {_fmt(cc['difference_s'])} s vs combined sigma "
          f"{_fmt(cc['combined_sigma_s'])} s; {cc['at_2sigma']})")
        w(f"  convention: {cc['convention']}")
    w("")
    w("RECOMMENDATION (directly translatable: SelfCal.h TEMP_TC_SECS)")
    rec = res["recommendation"]
    w(f"  {rec['action']} TEMP_TC_SECS = {rec['tau_s']:.1f} s"
      + (f"  (change from {rec['change_from_current_s']:.1f} s)" if rec["change_from_current_s"] else ""))
    w(f"  rule: {rec['rule']}")
    if rec.get("transient_limited"):
        w("  TRANSIENT-LIMITED: measured-lag CI lower bound exceeds 2x the current constant.")
    if rec.get("provisional"):
        w("  PROVISIONAL: cross-method disagreement - resolve before adopting.")
    w("  rationale: the EMA tau should make the FILTERED die temperature track")
    w("  the crystal's effective temperature through transients, i.e. tau_ema ~")
    w("  measured die->crystal lag; compensation is computed from T_ema")
    w("  (SelfCal.h:133), so a mismatched tau biases every transient ppm directly.")
    w("")
    w("LIMITATION NOTE (open-loop, unconditional)")
    for line in res["limitation_note"].split(". "):
        w(f"  {line.rstrip('.')}.")
    w("  update path: " + fw["update"])
    w("  closed loop: " + fw["closed_loop"])
    w("")
    w("ILLUSTRATIVE transient mis-compensation scale (formula rows from the")
    w("firmware's own sizing constants; k is UNMEASURED - atcut-fit NO-FIT;)")
    w("error_ppm = 2k|T-T0| * ramp_rate * mismatch_s:")
    w(f"  {'k (ppm/C^2)':<47}{'ramp rate':<38}{'mismatch':>9}{'-> ppm':>8}")
    for r in res["illustrative_transient_rows_NOT_measurements"]:
        w(f"  {r['k_label']:<47}{r['rate_label']:<38}{r['mismatch_s']:>7.0f}s"
          f"{r['error_ppm']:>8.2f}")
    w("")
    w("RE-RUN WHEN PARENT CSV LANDS:")
    w("  " + res["rerun_when_data_lands"])
    return "\n".join(L)


# -------------------------------------------------------------- self-test

def _self_test():
    ok = [0, 0, 0]

    def check(name, cond):
        print(f"  [{'PASS' if cond else 'FAIL'}] {name}")
        ok[0 if cond else 1] += 1

    with tempfile.TemporaryDirectory() as td:
        # Scenario A: consistent synthetic parents (planted tau = 25 s)
        lag_a = os.path.join(td, "lag.json")
        hyst_a = os.path.join(td, "hyst.json")
        with open(lag_a, "w") as fh:
            json.dump({"lag_primary": {"lead_s": 24.5, "uncertainty_s": 2.0},
                       "combined": {"lead_s": 23.9, "uncertainty_s": 3.0},
                       "segments": [{"segment": "cooling", "lead_s": 24.9,
                                     "uncertainty_s": 2.5},
                                    {"segment": "warming", "lead_s": 24.1,
                                     "uncertainty_s": 2.8}]}, fh)
        with open(hyst_a, "w") as fh:
            json.dump({"hysteresis": {"median_dT_C": 1.34, "iqr_dT_C": 0.21},
                       "time_equivalent": {"median_tau_hyst_s": 24.4,
                                           "iqr_tau_hyst_s": 1.3},
                       "bootstrap_ci": {"median_tau_hyst_s_p16_p84": [23.6, 25.9]}}, fh)
        res = synthesize(lag_a, hyst_a, 10.0)
        print("Scenario A - consistent synthetic parents (planted tau 25 s):")
        check("verdict MEASURED", res["verdict"] == "MEASURED")
        check("cross-check agrees (1:1, not 1:2)",
              res["cross_check"]["flag"] is False
              and abs(res["cross_check"]["difference_s"]) < 0.5)
        check("CHANGE to 25 s (ci_lo 22.5 > 2*10 -> transient-limited)",
              res["recommendation"]["action"] == "CHANGE"
              and res["recommendation"]["tau_s"] == 25.0
              and res["recommendation"]["transient_limited"] is True)
        check("per-ramp rows surfaced (2)", len(res["lag"]["per_ramp"]) == 2)

        # Scenario B: disagreeing parents -> flag + provisional
        hyst_b = os.path.join(td, "hyst_b.json")
        with open(hyst_b, "w") as fh:
            json.dump({"hysteresis": {"median_dT_C": 2.9},
                       "time_equivalent": {"median_tau_hyst_s": 55.0},
                       "bootstrap_ci": {"median_tau_hyst_s_p16_p84": [53.0, 57.0]}}, fh)
        resb = synthesize(lag_a, hyst_b, 10.0)
        print("Scenario B - disagreeing synthetic parents:")
        check("flag DISAGREE beyond 1-sigma",
              resb["cross_check"]["flag"] is True
              and resb["cross_check"]["status"].startswith("DISAGREE"))
        check("recommendation PROVISIONAL",
              resb["recommendation"]["provisional"] is True)

        # Scenario C: the real case today - both parents NO-DATA
        missing = os.path.join(td, "does_not_exist.json")
        resc = synthesize(missing, missing, 10.0)
        print("Scenario C - NO-DATA (real case: parent CSV never existed):")
        check("verdict NO-DATA", resc["verdict"] == "NO-DATA")
        check("recommendation KEEP 10 s",
              resc["recommendation"]["action"] == "KEEP"
              and resc["recommendation"]["tau_s"] == 10.0
              and resc["recommendation"]["change_from_current_s"] is None)
        check("every input field carries NA-because",
              "NOT APPLICABLE because" in resc["lag"]["reason"]
              and "NOT APPLICABLE because" in resc["hysteresis"]["reason"])
        check("cross-check field definitive NA",
              resc["cross_check"]["flag"] is None
              and "NOT APPLICABLE" in resc["cross_check"]["status"])
        check("limitation note present (unconditional)",
              "transient-limited" in resc["limitation_note"]
              and "LR2021" in resc["limitation_note"])
        check("illustrative rows carry NOT-measured labels",
              all("NOT measured" in r["k_label"]
                  for r in resc["illustrative_transient_rows_NOT_measurements"]))

        # malformed JSON -> exit-2 path
        bad = os.path.join(td, "bad.json")
        with open(bad, "w") as fh:
            fh.write("{not json")
        try:
            load_json(bad, "lag")
            check("malformed JSON raises SystemExit", False)
        except SystemExit:
            check("malformed JSON raises SystemExit", True)

    print(f"\nSELF-TEST: {ok[0]} passed, {ok[1]} failed "
          "(synthetic only - never a hardware measurement)")
    return 0 if ok[1] == 0 else 1


# ------------------------------------------------------------------ main

def main():
    ap = argparse.ArgumentParser(
        description=(__doc__ or "SelfCal EMA time-constant synthesis").splitlines()[0])
    ap.add_argument("--lag-json", default=DEFAULT_LAG_JSON,
                    help="thermal-lag analyzer --json output")
    ap.add_argument("--hyst-json", default=DEFAULT_HYST_JSON,
                    help="hysteresis_fit --json output")
    ap.add_argument("--tau-now", type=float, default=FIRMWARE["value_now_s"],
                    help="current firmware EMA time constant (default 10 s)")
    ap.add_argument("--json", help="write machine-readable result here")
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        sys.exit(_self_test())
    res = synthesize(args.lag_json, args.hyst_json, args.tau_now)
    print(render_report(res))
    if args.json:
        with open(args.json, "w") as fh:
            json.dump(res, fh, indent=1)
        print(f"\n[json written: {args.json}]")


if __name__ == "__main__":
    main()
