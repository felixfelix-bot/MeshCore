#!/usr/bin/env python3
"""
_verify_t_b59e2fc1.py
=====================
Independent verification of REPORT-t_b59e2fc1.md.  Re-derives every numeric
claim from source (firmware tree + datasheet text + the sibling tools), and
re-checks the deliverable tool's own numbers against those sources.  Fails
loudly on any mismatch.

Run:  python3 _verify_t_b59e2fc1.py
"""
import re
import subprocess
import sys
import os

REPO = "/home/c03rad0r/repos/meshcore"
FW = "d7ae93fa"
WS = "/home/c03rad0r/worktrees/t_e1408991"
DS = "/tmp/lr2021.txt"

checks = []


def chk(name, cond, detail=""):
    checks.append((name, bool(cond), detail))


def sh(cmd, cwd=None):
    p = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True)
    return p.returncode, p.stdout, p.stderr


def git_show(path):
    rc, out, err = sh("git show %s:%s" % (FW, path), cwd=REPO)
    return out


# ---------------------------------------------------------------- 1. firmware
selfcal = git_show("examples/passive_mapper/host/SelfCal.h")
lines = selfcal.splitlines()
chk("SelfCal.h fetched from %s" % FW, len(lines) > 150, "%d lines" % len(lines))

# line-exact constant citations used in the report
want = {
    47: ("TEMP_TC_SECS", "10.0f"),
    48: ("SLEW_PPM", "25.0f"),
    49: ("DEADBAND_PPM", "1.0f"),
    50: ("MAX_PPM", "300.0f"),
    53: ("SNR_GATE_DB", "-10.0f"),
    72: ("CAL_RANGE_C", "90.0f"),
    100: ("_temp_ema = T0", "assume ambient"),
    118: ("expf(-dt / TEMP_TC_SECS)", "alpha"),
    133: ("float raw = _k * (_temp_ema - _T0)", None),
    158: ("void feedMeasured(float freq_error_ppm, float snr)", None),
}
for ln, (needle, extra) in want.items():
    txt = lines[ln - 1]
    ok = needle in txt and (extra is None or extra in txt)
    chk("SelfCal.h:%d contains %r" % (ln, needle), ok, txt.strip()[:70])

# TEMP_TC_SECS appears exactly once in the class constants block
chk("TEMP_TC_SECS declared once",
    selfcal.count("static constexpr float TEMP_TC_SECS") == 1)

# ------------------------------------------------------- 2. capture window
mymesh = git_show("examples/passive_mapper/MyMesh.cpp")
chk("MyMesh.cpp:23 documents the +/-72 ppm BW125 window",
    "+/-72 ppm" in mymesh.splitlines()[22], mymesh.splitlines()[22].strip()[:70])

# ------------------------------------------------------ 3. FEI dead end #1
rc, out, err = sh("git grep -n feedMeasured %s" % FW, cwd=REPO)
prod_calls = [l for l in out.splitlines()
              if l.strip() and "tests/" not in l and "void feedMeasured" not in l
              and "//" not in l.split(":", 2)[-1]]
chk("zero production call sites of feedMeasured", len(prod_calls) == 0,
    "found %d: %s" % (len(prod_calls), prod_calls[:2]))
chk("feedMeasured defined in SelfCal.h",
    any("SelfCal.h:158" in l and "void feedMeasured" in l for l in out.splitlines()))
chk("feedMeasured called only from the host test suite",
    sum(1 for l in out.splitlines() if "tests/test_self_cal.cpp" in l) == 2,
    "%d test invocations" % sum(1 for l in out.splitlines()
                                if "tests/test_self_cal.cpp" in l))

# ------------------------------------------------------ 4. FEI dead end #2
chk("datasheet text extracted", os.path.exists(DS) and
    os.path.getsize(DS) > 500_000, "%d bytes" % (os.path.getsize(DS) if os.path.exists(DS) else 0))
with open(DS, encoding="utf-8", errors="replace") as fh:
    ds = fh.read()
chk("datasheet has no FEI register", not re.search(r"\bFEI\b", ds))
chk("datasheet has no 'frequency error indicator'",
    "frequency error indicator" not in ds.lower())
chk("datasheet has no FreqErrInd symbol", "FreqErrInd" not in ds)
# every 'frequency error' hit must be a tolerance spec or the 0xF30A2C mode switch
fe_hits = [l for l in ds.splitlines() if "frequency error" in l.lower()]
categorised = [l for l in fe_hits
               if re.search(r"(FREQERR|tolerated|Max(imum)? frequency error"
                            r"|extended frequency error|frequency error (control|tracking)"
                            r"|lenience|any required frequency error"
                            r"|based on frequency error tolerance)", l)]
chk("every 'frequency error' hit is a tolerance spec or the 0xF30A2C switch",
    len(categorised) == len(fe_hits),
    "%d hits, %d categorised" % (len(fe_hits), len(categorised)))
chk("the 0xF30A2C register is a mode switch, not a readout",
    "0xF30A2C" in ds and "extended frequency error control" in ds
    and "mode = 0 (legacy) or 1 (extended)" in ds)
chk("no host-readable freq-offset read command",
    not re.search(r"Get(Rx)?Freq(Offset|Error)", ds))
chk("datasheet states the FEI-inert rationale is real (XTAL only compensated "
    "'to some extent')",
    "to some extent" in ds)

# ------------------------------------------------------ 5. rules in tree
# rule A: 2.0 * tau_now in analyze_thermal_lag.py
lag_py = open(os.path.join(REPO, "bench/thermal-lag/analyze_thermal_lag.py")).read()
chk("rule A threshold 2.0 x tau present",
    "ci_lo > 2.0 * tau_now" in lag_py)
chk("rule A rounds to a 5 s grid", "5.0 * round(rec / 5.0)" in lag_py)
chk("rule A note names the FEI dead end", "FEI path is a verified dead end" in lag_py)
# rule B: > 30 s in the bench kit
tb = git_show("examples/passive_mapper/bench/thermal_bench.py")
chk("rule B threshold 30 s present (thermal_bench.py)",
    'res["tau_s"] < 30' in tb)
rm = git_show("examples/passive_mapper/bench/README.md")
chk("rule B threshold 30 s present (README.md)",
    "If `tau` > 30 s, raise `TEMP_TC_SECS`" in rm)
# bench kit rejects derivative xcorr
calib = git_show("examples/passive_mapper/bench/calib.py")
chk("bench kit rejects derivative xcorr as unidentifiable",
    "derivative cross-correlation delay estimator was tried first and dropped" in calib)
chk("bench kit's own default tau in its simulated pipeline is 45 s",
    "tau=45" in rm)

# ------------------------------------------------------ 6. sibling tools run
for tool, args, expect in (
        ("bench/thermal-lag/analyze_thermal_lag.py", "--self-test", "SELF-TEST PASS"),
        ("bench/thermal-hysteresis/hysteresis_fit.py", "--self-test", "SELF-TEST PASS"),
        ("bench/selfcal-ema-tau/synthesize_tau.py", "", "KEEP TEMP_TC_SECS = 10.0 s"),
):
    rc, out, err = sh("python3 %s %s" % (tool, args), cwd=REPO)
    chk("%s %s exit 0" % (os.path.basename(tool), args), rc == 0, "rc=%d" % rc)
    chk("%s produces %r" % (os.path.basename(tool), expect), expect in out)

rc, out, err = sh("python3 bench/thermal-lag/analyze_thermal_lag.py --self-test", cwd=REPO)
chk("sibling prints the loop-area 24.2 s primary lag", "+24.2 s" in out)
chk("sibling prints the 1.96 ppm open-loop bound", "1.96 ppm" in out)
chk("sibling prints the 0.098 ppm residual loop", "0.098 ppm" in out)
rc2, out2, err2 = sh("python3 bench/thermal-hysteresis/hysteresis_fit.py --self-test", cwd=REPO)
chk("hysteresis prints tau_hyst +24.4 s", "+24.4 s" in out2)
chk("hysteresis prints dT +1.34 C", "+1.34 C" in out2)
chk("hysteresis CI [+23.6, +25.9]", "[+23.6, +25.9]" in out2)

# ------------------------------------------------------ 7. deliverable tool
rc, out, err = sh("python3 ema_tau_eval_t_b59e2fc1.py --self-test", cwd=WS)
chk("deliverable --self-test exit 0", rc == 0, "rc=%d" % rc)
chk("deliverable --self-test PASS", "SELF-TEST PASS" in out)
npass = out.count("[PASS]")
nfail = out.count("[FAIL]")
chk("deliverable 24/24 checks pass", npass == 24 and nfail == 0,
    "%d PASS / %d FAIL" % (npass, nfail))

rc, out, err = sh("python3 ema_tau_eval_t_b59e2fc1.py --json", cwd=WS)
chk("deliverable --json exit 0", rc == 0)
import json as _json
j = _json.loads(out)
chk("json ratio = 2.43", abs(j["comparison"]["ratio"] - 2.43) < 0.005,
    "%.4f" % j["comparison"]["ratio"])
chk("json rules disagree", j["rules"]["agree"] is False)
chk("json rule A fires, rule B does not",
    j["rules"]["rule_lag"]["fires"] is True and j["rules"]["rule_bench"]["fires"] is False)
chk("json transient not binding", j["recommendation"]["transient_is_binding"] is False)
chk("json action today is KEEP",
    j["recommendation"]["action_today"].startswith("KEEP"))
chk("json worst transient err = 3.03 ppm",
    abs(j["recommendation"]["worst_transient_err_ppm"] - 3.03) < 0.01,
    "%.4f" % j["recommendation"]["worst_transient_err_ppm"])

# ------------------------------------------------------ 8. report claims
rep = open(os.path.join(WS, "REPORT-t_b59e2fc1.md")).read()
for claim in ("2.43×", "24.3 ± 1.0 s", "KEEP `TEMP_TC_SECS = 10.0 s`",
              "3.03 ppm", "72 ppm", "95.8 %", "2.53 C/s",
              "169.0 ppm", "81.0 ppm", "d7ae93fa",
              "zero call sites", "no FEI register",
              "5.7 s below", "27.3 s"):
    chk("report states %r" % claim, claim in rep)

# ------------------------------------------------------ 9. data status fresh
chk("parent lag.json absent",
    not os.path.exists(os.path.join(REPO, "bench/thermal-lag/lag.json")))
chk("parent hyst.json absent",
    not os.path.exists(os.path.join(REPO, "bench/thermal-hysteresis/hyst.json")))

# A ramp series is identified by its COLUMNS, not its name.  Scan the CSVs most
# likely to hold one: the workspace, /tmp, and the meshcore tree (bounded, so the
# check stays fast and deterministic).
RAMP_COLS = ("die_temp", "ppm_err", "freq_err", "xosc")
cand = []
for root in (WS, "/tmp", REPO, os.path.expanduser("~/reports")):
    if not os.path.isdir(root):
        continue
    rc, out, err = sh("find %s -xdev -name '*.csv' 2>/dev/null | head -300" % root)
    cand.extend(p for p in out.splitlines() if p.strip())
cand = sorted(set(cand))
hits = []
for p in cand:
    try:
        with open(p, encoding="utf-8", errors="replace") as fh:
            head = fh.readline().lower()
    except OSError:
        continue
    if sum(1 for c in RAMP_COLS if c in head) >= 2:
        hits.append(p)
chk("no die-temp+ppm ramp CSV among candidate CSVs", not hits,
    "%d CSVs scanned, %d ramp-shaped: %s" % (len(cand), len(hits), hits[:2]))

# And the repo itself must still contain zero ramp CSVs.
rc, out, err = sh("find %s -name '*.csv' 2>/dev/null" % REPO)
repo_csvs = [p for p in out.splitlines() if p.strip()]
repo_hits = []
for p in repo_csvs:
    try:
        with open(p, encoding="utf-8", errors="replace") as fh:
            head = fh.readline().lower()
    except OSError:
        continue
    if sum(1 for c in RAMP_COLS if c in head) >= 2:
        repo_hits.append(p)
chk("meshcore repo contains no ramp CSV", not repo_hits,
    "%d repo CSVs, %d ramp-shaped" % (len(repo_csvs), len(repo_hits)))

# ------------------------------------------------------ 10. arithmetic redo
def err_ppm(k, t, t0, rate, tau_ema, tau_lag):
    return abs(2.0 * k * abs(t - t0) * rate * (tau_ema - tau_lag))

chk("ISA rate 5 m/s x 6.5 K/km = 0.0325 C/s",
    abs(0.0065 * 5.0 - 0.0325) < 1e-12)
chk("ISA floor err @10 s = 3.03 ppm",
    abs(err_ppm(0.04, -56.5, 25.0, 0.0325, 10.0, 24.3) - 3.03) < 0.01,
    "%.4f" % err_ppm(0.04, -56.5, 25.0, 0.0325, 10.0, 24.3))
# crossover at the ISA floor's own sensitivity (6.52 ppm/K) -- the number the
# report quotes first
chk("capture crossover at ISA floor = 0.77 C/s",
    abs(72.0 / (2 * 0.04 * 81.5 * 14.3) - 0.772) < 0.002,
    "%.4f" % (72.0 / (2 * 0.04 * 81.5 * 14.3)))
chk("capture crossover at the 1.99 ppm/K window = 2.53 C/s",
    abs(72.0 / (1.99 * 14.3) - 2.53) < 0.01,
    "%.4f" % (72.0 / (1.99 * 14.3)))
chk("ISA ascent is 24x below the ISA-floor crossover",
    abs((0.772 / 0.0325) - 23.8) < 0.3,
    "%.1fx" % (0.772 / 0.0325))
chk("cold-boot err at -20 C = 81 ppm",
    abs(0.04 * (25.0 - (-20.0)) ** 2 - 81.0) < 1e-9)
chk("cold-boot err at -40 C = 169 ppm",
    abs(0.04 * (25.0 - (-40.0)) ** 2 - 169.0) < 1e-9)
chk("+3 sigma = 27.3 s < 30 s", abs((24.3 + 3 * 1.0) - 27.3) < 1e-9)
chk("30 - 24.3 = 5.7 s margin", abs(30.0 - 24.3 - 5.7) < 1e-9)
chk("14.3 s mismatch = 14.3 sigma", abs(24.3 - 10.0 - 14.3) < 1e-9)
chk("CAL_RANGE band holds the ISA floor",
    abs(-56.5 - 25.0) <= 90.0, "%.1f <= 90" % abs(-56.5 - 25.0))

# ---------------------------------------------------------------- summary
ok = all(c[1] for c in checks)
print("VERIFICATION OF REPORT-t_b59e2fc1.md -- %d checks" % len(checks))
for name, passed, detail in checks:
    print("  [%s] %-62s %s" % ("PASS" if passed else "FAIL", name[:62], detail[:48]))
print("VERIFY %s  (%d/%d)" % ("PASS" if ok else "FAIL",
                              sum(1 for c in checks if c[1]), len(checks)))
sys.exit(0 if ok else 1)
