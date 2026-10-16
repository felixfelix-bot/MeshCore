#!/usr/bin/env python3
"""
t_cdcc5b88 -- RF feedthrough cold-bridge derating of the cooling ramp.
BASIC MODEL: Q = k*A*dT/L ; derated rate = nominal - Q*60/Cch.
All inputs are stated numeric ASSUMPTIONS (no chamber exists on any record/host).
"""
import csv, json, os

HERE = os.path.dirname(os.path.abspath(__file__))

# ---- A: cross-sections from Belden 83284 (RG316) DCR, rho_cu(20C)=1.724e-8 ----
RHO = 1.724e-8
A_CNT = RHO / (82.5 / 1000 / 0.3048)     # centre conductor  -> 0.0637 mm^2
A_SHD = RHO / (8.5 / 1000 / 0.3048)      # lumped 95% braid   -> 0.6182 mm^2 (UB)
A_USB = 0.258e-6                          # 2x 20AWG VBUS+GND (ASSUMED 0.129 mm^2 each)
A_N_CNT = 0.406e-6                        # N-series/AWG16-equiv centre (ASSUMED)

# ---- chamber effective cooling capacitance (ASSUMED class) ----
CCH = 50000.0            # J/K  (20-40 kJ/K sensitivity)
NOM = 1.5                # C/min nominal cooling (planning estimate 79ea692e)
K_CU = 400.0             # W/m/K

def Q(k, A, dT, L):  return k * A * dT / L
def rate(Q_W, Cch=CCH, nom=NOM):  return nom - Q_W * 60.0 / Cch
def fac(r, nom=NOM):  return r / nom

L_BASIC = 0.050
dT20, dT40 = 45.0, 65.0

def blockA():
    c20 = Q(K_CU, A_CNT, dT20, L_BASIC)
    u20 = Q(K_CU, A_USB, dT20, L_BASIC)
    tot20, tot40 = c20 + u20, c20 * dT40 / dT20 + u20 * dT40 / dT20
    return dict(A_cnt=A_CNT, A_shd=A_SHD, A_usb=A_USB,
                Q_cnt_20=c20, Q_usb_20=u20, Q_tot_20=tot20, Q_tot_40=tot40,
                r20=rate(tot20), r40=rate(tot40), f20=fac(rate(tot20)), f40=fac(rate(tot40)))

def blockB():
    """sensitivity envelope: conjugation x L x dT x Cch"""
    conj = [("P-1 coax centre only", 1.0),
            ("P-1 + full braid", 1.0 + A_SHD / A_CNT),
            ("P-1 + braid + USB-C", 1.0 + A_SHD / A_CNT + A_USB / A_CNT)]
    rows = []
    for cn, m in conj:
        for Lt, L in (("10 mm", .010), ("25 mm", .025), ("50 mm", .050)):
            for dt, dT in (("45 K", dT20), ("65 K", dT40)):
                for cc in (20000.0, 40000.0, 50000.0):
                    q = K_CU * A_CNT * m * dT / L
                    r = rate(q, cc)
                    rows.append((cn, Lt, dt, cc, q, r, fac(r)))
    return rows

def blockC():
    """Tier B: conducted variant, 2x record-specified RG316 (0.15m+0.50m) AT the feedthrough"""
    out = []
    for Lt, L in (("10 mm", .010), ("25 mm", .025), ("50 mm", .050)):
        q = K_CU * 2 * A_CNT * dT40 / L
        out.append((Lt, q, rate(q), fac(rate(q))))
    return out

def blockD():
    """wall series continuity + blower-test ceiling"""
    A_wall, t_pu, k_pu, t_st, k_st = 0.60 * 0.80, 0.05, 0.025, 0.001, 50.0
    qw = A_wall * dT40 / (t_pu / k_pu + t_st / k_st)          # 15.6 W
    cfm = rate(qw) - NOM                                       # added by wall continuity
    R_b = 2 * A_CNT
    qb = K_CU * R_b * dT40 / L_BASIC                           # blower ceiling (100% of rate as heat)
    return dict(Q_wall=qw, cfm_delta=cfm, Q_blower=qb,
                r_blower=rate(qb), f_blower=fac(rate(qb)))

def blockE():
    """checkable threshold: A_met needed for f <= 0.90"""
    f = 0.90
    q_allow = (1 - f) * NOM * CCH / 60.0
    L_lo = 0.010
    a_need = q_allow * L_lo / (K_CU * dT20)                    # L=10 mm, dT=45 K
    return dict(q_allow_W=q_allow, A_thresh_L50=a_need * 0.050 / L_lo * 1e0, A_thresh_mm2=a_need * 1e6)

if __name__ == "__main__":
    a, b, c, d, e = blockA(), blockB(), blockC(), blockD(), blockE()
    out = []
    out.append("========== t_cdcc5b88 RF feedthrough cold-bridge derating (BASIC) ==========")
    out.append("")
    out.append("§A assumed geometry, from RG316 DCR (Belden 83284):")
    out.append(f"   A centre  = {a['A_cnt']*1e6:.4f} mm^2   (26AWG 7x34 SCCS)")
    out.append(f"   A braid   = {a['A_shd']*1e6:.4f} mm^2   (lumped 95% shield, UPPER BOUND)")
    out.append(f"   A usb     = {a['A_usb']*1e6:.4f} mm^2   (2x20AWG VBUS+GND, ASSUMED)")
    out.append("")
    out.append("§B BASIC derating (L=50 mm across wall, Cch=50 kJ/K, nominal 1.5 C/min):")
    out.append(f"   Q coax centre        = {a['Q_cnt_20']*1000:8.4f} mW   (dT=45 K)")
    out.append(f"   Q USB-C 2x20AWG      = {a['Q_usb_20']*1000:8.4f} mW   (dT=45 K)")
    out.append(f"   Q total (-20 C)      = {a['Q_tot_20']*1000:8.4f} mW   -> rate {a['r20']:.4f} C/min = {a['f20']*100:.2f}% of nominal")
    out.append(f"   Q total (-40 C)      = {a['Q_tot_40']*1000:8.4f} mW   -> rate {a['r40']:.4f} C/min = {a['f40']*100:.2f}% of nominal")
    out.append("")
    fmin, fmax = min(b, key=lambda r: r[6]), max(b, key=lambda r: r[6])
    out.append(f"§C sensitivity envelope ({len(b)} cases): f = {fmin[6]:.4f} ({fmin[6]*100:.2f}%) .. {fmax[6]:.4f} ({fmax[6]*100:.2f}%)")
    out.append(f"   worst case: {fmin[0]} / L={fmin[1]} / dT={fmin[2]} / Cch={fmin[3]/1000:.0f} kJ/K"
               f" -> Q={fmin[4]*1000:.1f} mW rate={fmin[5]:.4f} C/min")
    out.append(f"   best  case: {fmax[0]} / L={fmax[1]} / dT={fmax[2]} / Cch={fmax[3]/1000:.0f} kJ/K"
               f" -> Q={fmax[4]*1000:.1f} mW rate={fmax[5]:.4f} C/min")
    out.append("")
    out.append("§D Tier B (conducted variant, 2x record RG316), dT=65 K, Cch=50 kJ/K:")
    for Lt, q, r, f in c:
        out.append(f"   L={Lt:>6}  Q={q:7.3f} W  rate={r:.4f} C/min = {f*100:.2f}% of nominal")
    out.append("")
    out.append("§E wall/ceiling cross-checks:")
    out.append(f"   Q floor+walls = {d['Q_wall']:.1f} W -> rate pull {d['cfm_delta']:+.4f} C/min (wall continuity)")
    out.append(f"   blower-test ceilin: Q={d['Q_blower']:.0f} W at 1.5 C/min -> {d['r_blower']:.4f} C/min = {d['f_blower']*100:.1f}%")
    out.append("")
    out.append("§F checkable threshold (f<=0.90):")
    out.append(f"   Q_allow = {e['q_allow_W']:.1f} W ; L=10 mm,dT=45 K -> A_met = {e['A_thresh_mm2']:.2f} mm^2")
    out.append("")
    out.append("§G SELF-TEST of the assumption chain:")
    for r_ in (0.5, 1.5, 3.0):
        out.append(f"   Cch x R_nom = 50 kJ/K x {r_} C/min = {50000*r_/60:.1f} W net cooling")
    out.append(f"   back-solve for f=0.90 at L=50mm,dT=45K (A_met=10 vs 50 mm^2 scaled):")
    out.append(f"      A_met={e['A_thresh_L50']*1e6:.2f} mm^2 required (linear in 1/L*L -> ~9.4 mm^2)")
    txt = "\n".join(out)
    print(txt)
    with open(os.path.join(HERE, "derate.out"), "w") as fh:
        fh.write(txt + "\n")
    with open(os.path.join(HERE, "derate.csv"), "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["case", "L", "dT_K", "Cch_J_per_K", "Q_W", "rate_C_per_min", "f_of_nominal"])
        for row in b:
            w.writerow([row[0], row[1], row[2], row[3], f"{row[4]:.6g}", f"{row[5]:.6f}", f"{row[6]:.6f}"])
    with open(os.path.join(HERE, "derate.json"), "w") as fh:
        json.dump({"A_cnt_mm2": a['A_cnt']*1e6, "A_shd_mm2": a['A_shd']*1e6,
                   "Q_tot_20_W": a['Q_tot_20'], "Q_tot_40_W": a['Q_tot_40'],
                   "f_20": a['f20'], "f_40": a['f40'],
                   "envelope_f_min": fmin[6], "envelope_f_max": fmax[6]}, fh, indent=2)
    print("\nwrote: derate.out derate.csv derate.json")
