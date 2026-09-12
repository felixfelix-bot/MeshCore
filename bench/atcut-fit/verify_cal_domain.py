#!/usr/bin/env python3
"""Domain-wide proof: every `cal` command the fitter can emit is parser-legal.

The fitter (fit_atcut.py) only emits commands once ALL sanity gates pass, so
the emittable domain is bounded: k in K_PLAUSIBLE (0.005..0.150 ppm/C^2,
gate-enforced) and T0 in any plausible sweep bracket. This script sweeps that
whole domain densely, renders `cal %.6g %.2f` for every (k, T0), and round-
trips each line through the verbatim Python port of the firmware's parseFloat
(MyMesh.cpp:128-143 @ felixfelix-bot/MeshCore feat/passive-mapper 3fdfbc8e),
plus the k >= 0 CLI gate (MyMesh.cpp:170).

It also quantifies the worst-case compensation error introduced by the
%.6g / %.2f rounding (task caveat: "rounding effect on compensation accuracy
in ppm over the swept range") and by float32 storage.

Synthetic format analysis only — no hardware data touched, exit 0 on PASS.
"""

import math
import re
import struct
import sys

sys.path.insert(0, __file__.rsplit("/", 1)[0])
from fit_atcut import K_PLAUSIBLE, cal_command, verify_command  # noqa: E402

# Swept die-temp distance from the vertex for the parent task's sweep
# (+25 -> -40 C with T0 near room temp): |T - T0| <= 65 C.
MAX_DT_C = 65.0

K_TOKEN = re.compile(r"^[0-9]+\.[0-9]+$")   # leading digit, no sign/exp
T0_TOKEN = re.compile(r"^-?[0-9]+\.[0-9][0-9]$")  # %.2f: always d.dd


def ulp_f32(x):
    """Unit in the last place of x as float32 (bit-increment method —
    math.ulp() would give the DOUBLE ulp, ~2^29x too small here)."""
    b = struct.pack("<f", x)
    i = struct.unpack("<I", b)[0]
    sign = i & 0x80000000
    mag = i & 0x7FFFFFFF
    nxt = (mag + 1) | sign          # next f32 away from zero
    f2 = struct.unpack("<f", struct.pack("<I", nxt))[0]
    f1 = struct.unpack("<f", b)[0]
    return abs(f2 - f1)


PHI = 0.6180339887498949  # golden-ratio stride: adversarial, never "nice"


def main():
    fails = []
    n = 0
    # golden-ratio jittered (k, T0): values with full 7+ decimal digits so the
    # %.6g / %.2f rounding is genuinely exercised, plus the exact band edges.
    lo, hi = K_PLAUSIBLE
    ks = [lo, hi] + [lo + (hi - lo) * ((i * PHI) % 1.0) for i in range(1199)]
    t0s = [-40.0, 45.0] + [-40.0 + 85.0 * ((i * PHI) % 1.0)
                           for i in range(399)]
    for k in ks:
        for t0 in t0s:
            cmd = cal_command(k, t0)
            ok, detail = verify_command(cmd, k, t0)
            n += 1
            if not ok:
                fails.append((k, t0, cmd, detail))
                continue
            body = cmd[4:]
            k_tok, _, t0_tok = body.partition(" ")
            if not K_TOKEN.match(k_tok):
                fails.append((k, t0, cmd, "k token %r not plain decimal" % k_tok))
            if not T0_TOKEN.match(t0_tok):
                fails.append((k, t0, cmd, "T0 token %r not d.dd" % t0_tok))
    print("domain sweep: %d jittered (k,T0) combinations, k in [%.3f, %.3f], "
          "T0 in [-40, +45] C" % (n, min(ks), max(ks)))
    print("  every rendered `cal %.6g %.2f` line round-trips through the "
          "firmware parseFloat port + k>=0 gate:")
    print("  %s (%d failures)" % ("PASS" if not fails else "FAIL", len(fails)))
    for f in fails[:5]:
        print("   FAIL:", f)

    # ---- rounding / storage error budget (worst case over the domain) ----
    worst_k_round_ppm = 0.0
    worst_t0_round_ppm = 0.0
    for k in ks:
        k_r = float("%.6g" % k)          # what the command encodes
        dk = abs(k_r - k)
        worst_k_round_ppm = max(worst_k_round_ppm, dk * MAX_DT_C ** 2)
        for t0 in t0s:
            t0_r = float("%.2f" % t0)
            dt = abs(t0_r - t0)
            if dt == 0.0:
                continue
            # applied offset difference at the worst point of the sweep
            d_ppm = abs(k * ((MAX_DT_C + dt) ** 2 - MAX_DT_C ** 2))
            worst_t0_round_ppm = max(worst_t0_round_ppm, d_ppm)

    k_typ = 0.034  # LR2021-class AT-cut typical
    t0_typ = 25.0
    store_k_ppm = ulp_f32(k_typ) * MAX_DT_C ** 2
    store_t0_ppm = k_typ * ((MAX_DT_C + ulp_f32(t0_typ)) ** 2 - MAX_DT_C ** 2)

    print("error budget over |T-T0| <= %.0f C:" % MAX_DT_C)
    print("  %%.6g rounding of k : worst %.2e ppm across the k gate band"
          % worst_k_round_ppm)
    print("  %%.2f rounding of T0: worst %.3f ppm (at k=0.15; %.3f ppm at "
          "LR2021-typical k=0.034)"
          % (worst_t0_round_ppm,
             k_typ * ((MAX_DT_C + 0.005) ** 2 - MAX_DT_C ** 2)))
    print("  f32 storage ulp    : k %.1e ppm, T0 %.1e ppm (at k=0.034 T0=25)"
          % (store_k_ppm, store_t0_ppm))

    ok = not fails
    print("DOMAIN PROOF " + ("PASS" if ok else "FAIL"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
