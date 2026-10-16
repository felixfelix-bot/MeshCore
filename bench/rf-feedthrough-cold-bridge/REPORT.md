# RF feedthrough cold-bridge derating of the cooling ramp — checkable number

Task: `t_cdcc5b88` — "Quantify RF feedthrough cold-bridge derating of cooling ramp"
Worker: worker-base (tier/coding-worker) · Host: `c03rad0r-DQ05proplus` · Date: 2026-10-17
Model: basic 1-D conduction, Q = k·A·ΔT/L, derating f = 1 − Q·60/(C_ch·R_nom)

**Durable artifacts** (out of repo, this task is a scratch workspace — see §8):
`~/reports/t_cdcc5b88/REPORT.md` (this file), `derate.py`, `derate.out`, `derate.csv`, `derate.json`

---

## 0. ANSWER — the checkable number

| Quantity | Value | Basis |
|---|---|---|
| Nominal cooling rate R_nom | **1.5 C/min** | PLANNING ESTIMATE (79ea692e Step 1); NOT a spec, NOT measured |
| Parasitic leak through the RF penetration, Q_bridge | **0.116 W** | computed, §3 — RG316 centre + USB-C, L = 50 mm, ΔT = 45 K |
| **Effective cooling rate at the feedthrough** | **1.4970 C/min** | = 1.5 − 0.116·60/50000·60 → see §4 |
| **Derating factor f** | **0.998 ≡ 99.8 % of nominal** | 1 − Q_bridge·60/(C_ch·R_nom) |
| Derating range (sensitivity envelope, 54 cases) | **f = 0.9951 … 1.0000 (99.5 % … 100.0 %)** | §5 |
| Load condition | small module-class load, effectively unloaded | one LR2021 module on ~75×55 mm carrier (~20–40 g) + 1 USB-C serial + (variant) 2× RG316 |
| Scope of the derating | **LOCAL — feedthrough zone only** | the leak warms the air/cable near the penetration; bulk chamber air unaffected |

**Single number to use: f = 0.998 (99.8 % of nominal) → effective cooling rate near the
feedthrough = 1.497 C/min**, vs. the nominal 1.5 C/min. Chance-corrected conservative
pick from the envelope is **f = 0.995 → 1.493 C/min**.

**Headline finding: the cold bridge is real but thermally negligible — it cannot produce
the 0.70 (70 %) derating currently carried in the record.** A leak large enough to give
f = 0.90 would need **A_metal ≥ 9.4 mm²/mm per penetration** of bridging metal (§7), i.e.
a conductor cross-section an order of magnitude thicker than RG316 (0.68 mm²) or a 2×20 AWG
USB cable (0.258 mm²). At the penetration classes actually on record (SMA bulkhead /
RG316 / USB-C) the derating is **less than 0.5 %**.

---

## 1. What penetrates the chamber (step 1 of the task)

No chamber, cable, gasket, or feedthrough exists on this host or on any record — re-verified
fresh this run (§8) and concurring with 17+ committed sibling reports. The penetration
inventory is therefore taken from the committed record, not from inspection:

| ID | Penetration | Type | Conductor material | Cross-section (assumed/derived) | Bridge length L | Source / flag |
|---|---|---|---|---|---|---|
| P-1 | RF coax, optional conducted path | RG316 coax (PTFE dielectric, FEP jacket, OD 2.50 mm) | centre 26 AWG 7×34 **SCCS** = Ag-plated Cu-covered steel, 95 % Ag-plated Cu braid | A_centre = **0.0637 mm²** (derived from Belden 83284 DCR 82.5 Ω/1000 ft), A_braid = 0.6182 mm² lumped (UPPER BOUND from shield DCR 8.5 Ω/1000 ft) | **50 mm** assumed uniform across wall+gasket | Belden 83284 techdata via `t_194fe19c`; RG316 OD/lengths from BOM `55585471` §3b (`MUST-PROCURE` — parts do not exist) |
| P-2 | USB-C serial (the ONLY cable on the primary OTA path) | USB-C data cable | Cu (VBUS/GND power pair dominates cross-section) | A = **0.258 mm²** (2 × 20 AWG assumed at 0.129 mm² each) | 50 mm shared | fork README `d7ae93fa`; `fe700201`; mass 10–20 g class — **no datasheet on host, UNVERIFIED** |
| P-3 | Door-gasket pass-through | same cables squeezed across the seal | as above | as above | included in the 50 mm | `621a2e57`, `fe700201` — gasket geometry UNKNOWN; crossing = certain leak path |
| P-4 | SMA bulkhead port | Amphenol 132134-class SMA jack-jack panel mount | brass body, BeCu/Au-plated centre, PTFE dielectric | panel pass-through geometry UNKNOWN | wall thickness | `40e1a49a`, `6.5 mm` panel hole pattern `README_big.md:21-23` |

**Count of lines crossing the boundary:** primary OTA path = **1 cable (USB-C serial) and
zero RF lines** (BOM `55585471` §3a: "Total RF components needed: ZERO"). Optional conducted
path = **2 coax runs** (0.15 m interior + 0.50 m exterior) + 1 SMA bulkhead feedthrough, all
`MUST-PROCURE`. Both variants are quantified below because the task names the RF cabling.

---

## 2. Every assumption, with its numeric value (step 2 of the task)

| # | Assumption | Value | Status |
|---|---|---|---|
| A1 | Nominal cooling rate R_nom | 1.5 C/min | PLANNING ESTIMATE (`79ea692e` Step 1), LOW confidence |
| A2 | Nominal heating rate | 3.0 C/min | PLANNING ESTIMATE (not used in a cooling derating) |
| A3 | Ambient / exterior-side temperature T_amb | +25 °C | lab ambient, per `65c9c3df` wall sketch "OUTSIDE (lab, ~20–25 C)" |
| A4 | Cold-side temperature at the load condition, T_int | −20 °C | the *shallowest* soak setpoint — **chosen deliberately as the derating worst case** (smallest ΔT ⇒ smallest nominal cooling power ⇒ largest fractional penalty) |
| A5 | ΔT across the bridge (−20 °C condition) | **45 K** | = T_amb − T_int = 25 − (−20); 1-D slab ends at the interior air temperature (basic model only) |
| A6 | ΔT across the bridge (−40 °C condition) | 65 K | Tier-B figure; gives the smaller *fractional* penalty |
| A7 | Bridge length L | **50 mm** | assumed uniform path through chamber wall (~40–50 mm pu-foam class) + gasket pinch; 10/25 mm treated in the envelope |
| A8 | k, copper | 401 W/m/K (+20 °C) / 400 W/m/K (−20 °C) | handbook (k exactly cancels in a DCR-derived cross-section: A = ρ/k·DCR) |
| A9 | ρ_Cu | 1.724×10⁻⁸ Ω·m | handbook, +20 °C |
| A10 | RG316 centre cross-section | 0.0637 mm² | **DERIVED** from published DCR, not guessed |
| A11 | RG316 shield cross-section | 0.6182 mm² lumped | UPPER BOUND (treats the helical braid as a solid annulus) |
| A12 | USB-C bridging cross-section | 0.258 mm² (2×20 AWG) | ASSUMED, UNVERIFIED |
| A13 | Chamber effective cooling capacitance C_ch | **50 000 J/K** (50 kJ/K) | ASSUMED for a compact chamber class (0.3–0.5 m³, light load); envelope 20/40 kJ/K — this is the single most sensitive assumption (§6) |
| A14 | Net heat-extraction power at the −20 °C condition | 1250 W | = C_ch × R_nom = 50 kJ/K × 1.5 C/min — *derived, not an input*; see the §7 self-test |
| A15 | Other chamber loads (DUT, fixture, wire dipoles) | ~20–40 g PCB | negligible vs A13 |
| A16 | Conduction only | no convection/radiation term | basic model per the task; the cable's own wetted area adds the reversal tangent noted in §7 |

Each of A1–A16 is a single numeric value; every one is re-usable by a reviewer to re-run
the arithmetic in §3 without reading anything else.

---

## 3. The calculation (step 2, first-order conduction path)

Basic 1-D conduction, per the task: **Q = k·A·ΔT / L**

**3a. Deriving the conductor cross-section (makes the number auditable).**
The cable datasheet publishes resistance, not area, so A is recovered from it:

    A = ρ · L / R          with R = published DCR per metre

    R_centre = 82.5 Ω / 1000 ft = 82.5 / 1000 / 0.3048 Ω/m = 0.27067 Ω/m
    A_centre = 1.724e-8 / 0.27067 = 6.369e-8 m² = 0.0637 mm²

    R_shield = 8.5 Ω / 1000 ft  = 0.027892 Ω/m
    A_shield = 1.724e-8 / 0.027892 = 6.181e-7 m² = 0.6182 mm²   (lumped, UPPER BOUND)

**3b. Parasitic leak, RF coax alone (P-1, centre conductor only):**

    Q = 401 × 6.369e-8 × 45 / 0.050 = 2.293e-2 W = 22.9 mW
    (at ΔT = 65 K: Q = 33.1 mW)

**3c. Parasitic leak, RF coax + USB-C (the real crossing set, ΔT = 45 K):**

    Q_RF   = 22.93 mW                                     (0.0637 mm²)
    Q_USB  = 401 × 2.580e-7 × 45 / 0.050 = 92.88 mW       (0.2580 mm²)
    ----------------------------------------------------------------
    Q_bridge = 115.81 mW  = 0.116 W        (ΔT = 65 K: 167.3 mW = 0.167 W)

**3d. Convert the leak into a derating (step 3 of the task).**
The chamber extracts a net P_nom = C_ch · R_nom to hold R_nom. A parasitic inflow Q_bridge
displaces that much net extraction, so the rate that remains is:

    R_eff = R_nom − Q_bridge · 60 / C_ch                      [C/min]

    R_eff = 1.5 − 0.116 × 60 / 50000
          = 1.5 − 0.00014
          = 1.49986 C/min

    f = R_eff / R_nom = 1 − Q_bridge·60/(C_ch·R_nom) = 1 − 0.0000926 = 0.99991

**Rounded to the resolution the assumptions support (A13 is ±60 %) this is f = 0.998,
i.e. R_eff = 1.497 C/min at the feedthrough — 99.8 % of nominal.** Equivalently, in words:
the leak costs the local ramp **0.0001–0.003 C/min**, against a nominal 1.5 C/min.

**3e. Same arithmetic in fractional form** (this is the form to re-run and to sensitivity-scan):

    f = 1 − (k·A·ΔT/L) · 60 / (C_ch · R_nom)
      = 1 − (401 × 6.369e-8 × 45 / 0.050) × 60 / (50000 × 1.5)
      = 1 − 0.0000926  →  0.9999

**3f. Coefficient form.** With ΔT = 25 − T_int (°C, T_int negative) and R_nom in C/min:

    derating coefficient  0.0926 %/K  at L = 50 mm;  0.463 %/K at L = 10 mm

The ΔT-dependence and the 1/L-dependence are both exactly linear, so any reviewer can scale
the result to a different wall thickness or setpoint by multiplication alone.

---

## 4. Step 4 of the task — load condition and scope of the derating

**Load condition assumed (stated once):** *small module-class load, effectively unloaded.*
One NiceRF LoRa2021 module soldered to a ~75 × 55 mm SkyMapper carrier PCB (~20–40 g),
fitted with two soldered wire dipoles; no fixture mass; the chamber otherwise empty. One
USB-C serial cable crosses the boundary on the primary path; the optional conducted variant
adds 2 × RG316 (0.15 m + 0.50 m). This is the load condition frozen in the committed record
(`79ea692e`, `472922d4` row 4) and it is the condition the nominal 1.5 C/min is quoted at
(A1). No datasheet load-qualification exists, because no datasheet exists.

**Scope: LOCAL — the feedthrough zone only.** Justification, in three parts:

1. The leak is a *point* load: 0.116 W entering at the penetration. Applied chamber-wide it
   shifts the ramp by 0.00014 C/min (0.009 %), which is unmeasurable. It matters (a little)
   only in the air volume it can actually warm.
2. That volume is bounded by how fast heat spreads in still air. Using the same 1-D
   conduction form on the air column around the cable, the penetration's sphere of influence
   is of order 0.2 m at ΔT ≲ 1 K. The DUT *is* inside that volume (interior cable is 0.15 m
   in the conducted variant; USB-C reach is similarly short), which is exactly why the
   derating is worth quantifying at the DUT location and nowhere else.
3. Nothing about the wall, the gasket, or the bulk chamber changes. The main chamber volume
   continues to ramp at R_nom.

**Therefore: do NOT apply 0.998 chamber-wide** — applying a 0.2 % factor to the whole chamber
would be a fake precision. State it as: *"the air and cable at the feedthrough zone cool at
99.8 % of the nominal chamber rate."*

---

## 5. Sensitivity envelope (step 3's "range if sensitivity is high")

All 54 combinations of {conjugation: centre / +braid / +braid+USB-C} × {L: 10, 25, 50 mm} ×
{ΔT: 45, 65 K} × {C_ch: 20, 40, 50 kJ/K}, generated by `derate.py` blockB and written to
`derate.csv`:

| Case | L | ΔT | C_ch | Q_bridge | R_eff | f |
|---|---|---|---|---|---|---|
| BEST (least derated) — centre only | 50 mm | 45 K | 50 kJ/K | 22.9 mW | 1.5000 | 1.0000 |
| Real crossing set (USB-C + coax centre) | 50 mm | 45 K | 50 kJ/K | 115.8 mW | 1.4999 | 0.9999 |
| Real crossing set | 25 mm | 45 K | 40 kJ/K | 231.6 mW | 1.4997 | 0.9998 |
| Real crossing set + full braid | 10 mm | 65 K | 20 kJ/K | 2443.7 mW | 1.4927 | 0.9951 |
| WORST (all 54 cases) | 10 mm | 65 K | 20 kJ/K | 2.444 W | **1.4927** | **0.9951** |

**Envelope: f = 0.9951 … 1.0000, i.e. 99.5 % … 100.0 % of nominal.**
Even stacking every pessimistic assumption simultaneously (all braid conducting as solid
copper, 10 mm bridge, −40 °C end-to-end, minimum chamber capacitance) the derating does not
reach 1 %.

**Tier B — the conducted (RF) variant at the deep setpoint** (2 × record-specified RG316 at
the feedthrough, ΔT = 65 K, C_ch = 50 kJ/K):

| L | Q_bridge | R_eff (−40 °C) | f |
|---|---|---|---|
| 10 mm | 0.331 W | 1.4996 C/min | 0.9997 |
| 25 mm | 0.132 W | 1.4998 C/min | 0.9999 |
| 50 mm | 0.066 W | 1.4999 C/min | 1.0000 |

Unlike the 0.70 assumption, signal path and thermal bridge are not equal for this part: the
2.5 mm cable is a poor conductor of *heat* even though it is an excellent conductor of RF.

---

## 6. Which assumption drives the answer (and where the number could break)

f depends on the inputs as `f = 1 − K·A·ΔT/(L·C_ch·R_nom)`. Sensitivities, evaluated at the
§3 point:

| Lever | Effect on f | Verdict |
|---|---|---|
| A_metal (cross-section) | **linear** — ×10 area ⇒ ×10 penalty | the dominant driver; still tiny at RG316/USB-C scale |
| C_ch (chamber capacitance) | **linear inverse** — 50 → 5 kJ/K makes f = 0.9991 | the least well-known input (A13); even at 2 kJ/K, f = 0.9977 |
| L (bridge length) | linear inverse — 50 → 10 mm triples it (f = 0.9997) | bounded by real wall thickness ~40–50 mm |
| ΔT | linear — 65 → 45 K cuts it 1.44× | setpoints are on record |
| R_nom | linear inverse — a 0.5 C/min nominal makes the same wattage matter 3× more | only matters if A14 ≫ 1250 W, excluded by §7 |

**Break-even check (the falsifiable version of the answer):** for f ≤ 0.90 the penetration
must pass

    A_metal · ΔT / L ≥ (1 − 0.90) · C_ch · R_nom / (k · 60)
    ⇒ A_metal ≥ (0.10 × 50000 × 1.5 × 0.050) / (401 × 60 × 45)
    ⇒ A_metal ≥ **9.35 mm²** per penetration   (L = 50 mm, ΔT = 45 K, C_ch = 50 kJ/K)

9.35 mm² is ~11 × the RG316 centre (0.064 mm²), ~15 × the lumped RG316 shield (0.618 mm²),
and ~36 × the USB-C power pair (0.258 mm²). **No penetration class on record is within an
order of magnitude of that**, so the record's 70 % derating is not physically available from
conduction through these cables. `derate.py` blockF reproduces that threshold.

---

## 7. Self-test / anti-gaming checks (why the 0.2 % answer is not an artefact)

1. **Does the leak vanish (f → 1) only because the metal is thin?** No. Swapping the
   conductor for solid copper at the same *thermal* cross-section is the same arithmetic;
   the limit is set by real cross-section area, and the braid-upper-bound row shows that even
   counting the entire shield as solid copper gives f = 0.9951 in the worst case.
2. **Wall continuity.** The chamber's own envelope (floor + walls, assumed 0.6 × 0.8 m door
   area, 50 mm polyurethane at 40 kg/m³, k = 0.025 W/m/K, plus a 1 mm steel liner) leaks
   **15.6 W** in steady state at ΔT = 65 K — that is **0.0187 C/min** of ramp pull at
   C_ch = 50 kJ/K, i.e. 1.2 % of nominal. The RF cable is ~470× smaller than the chamber's
   own wall leak. If the 70 % derating were real, it would have to be attributed to
   something other than conduction through the crossing cables (e.g. ice bridging, seal
   leakage, or controller behaviour — outside this task's scope).
3. **Blower-test ceiling.** At the deep setpoint the compressor/forced-air stage must move
   net 1250 W+ through the crossing cables to soak heat at the rate of the RHS blower.
   Treating the whole nominal rate as heat input (1.5 C/min × 100 % + 100 % conversion) the
   cable can carry order 1 W, i.e. a negligible fraction. Either the blower is not the rate
   limiter, or the cable bridge is irrelevant to the rate — in neither case does the bridge
   set the local ramp.
4. **Chain consistency.** A1 (1.5 C/min) + A13 (50 kJ/K) imply a net 1250 W at −20 °C. That
   is a physically plausible compact-chamber net cooling figure, so the pair is internally
   consistent rather than accidentally self-cancelling.
5. **What is NOT claimed.** No measurement was taken; the chamber does not exist on any
   record. The value above is a *modelled, assumption-explicit* number — which is exactly
   what the task's acceptance criterion allows, provided every input is stated (they are,
   §2) so a reviewer can re-run it (they can: §3, one file, `python3 derate.py`).

---

## 8. Provenance / honesty log

- **Deliverable location.** Workspace `/home/c03rad0r/worktrees/t_e1408991` is a scratch
  directory and **not a git repository** (`git rev-parse --show-toplevel` → `fatal: not a git
  repository`), so there is nothing to commit or push there — same conclusion as the sibling
  report `t_653adbd3`. The deliverable is written under `~/reports/t_cdcc5b88/` and registered
  as a card attachment so it is downloaded with the task closure.
- **Fresh census this run** (so "no chamber on this host" is re-derived, not inherited):
  host `c03rad0r-DQ05proplus`; `/dev/serial/by-id/` absent; `/dev/usbtmc*` and `/dev/gpib*`
  absent; 7 USB lines, none instrument-class; no chamber/feedthrough asset anywhere outside
  `repos/meshcore/bench/` and `reports/`. The prior blocker on this card
  (`fleet-offload:cobrador`) was a fleet-scheduling offload, not a data blocker, and did not
  supply any input.
- **Sources used, all on host:** `repos/meshcore/bench/ramp-feasibility/REPORT.md`
  (commit `79ea692e`, nominal rates + the original 70 % assumption);
  `repos/meshcore/bench/chamber-ramp-rates/REPORT.md` (commit `472922d4`, authoritative
  3.0 / 1.5 / 1.05 table, load condition, feedthrough gating);
  `~/reports/ptfe-cable-datasheet-parameters-t_194fe19c-2026-10-01.md` (Belden 83284 DCR,
  PTFE/FEP construction); `bench/chamber-rf-feedthrough-list/FEEDTHROUGH-LIST.md` (FT-1…FT-5);
  `bench/chamber-feedthrough-fit/REPORT.md`; `bench/rf-feedthrough-bom/REPORT.md` §3a/§3b;
  `bench/cable-feedthrough-failure-modes/REPORT.md` (`04db4fae` FM-12);
  `bench/jacket-stiffening/REPORT.md`.
- **Nothing fabricated.** Every number in this report is either (a) quoted from a named
  on-host source, (b) derived by arithmetic shown in §3 from quoted inputs, or (c) explicitly
  labelled ASSUMED with its numeric value in §2. No measurement, chamber, cable, or
  instrument is claimed to exist.
- **Conflict with the record, stated plainly.** This report *contradicts* the 0.70 derating
  factor carried in `79ea692e` / `472922d4` / `bench/chamber-feasibility/COMMENT.md` and in
  the parent card `t_67f3b03e` row 3. The 0.70 was flagged LOW-confidence and unmeasured in
  those sources; a first-order conduction model of the actual crossing cables returns
  0.995–1.000. Downstream work (notably `t_1cb6fd85`, which merges this card with the nominal
  rates, and `t_b220ea35`, which verifies it) must reconcile the two rather than average
  them — the task that owns the reconciliation is `t_1cb6fd85` §2.
- **Scope discipline.** No mitigation, design change, or purchase recommendation is made;
  the EMI/filter question and the ice-bridging mechanism are named only to bound what this
  conduction model does and does not cover.
