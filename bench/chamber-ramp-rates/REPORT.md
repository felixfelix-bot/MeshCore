# Chamber max ramp rates + RF feedthrough thermal penalty (authoritative numbers)

Fleet card: `meshcore:t_67f3b03e` — "Establish chamber max ramp rates and RF
feedthrough thermal penalty. GOAL: Produce the authoritative ramp-rate numbers
this analysis must use."

Date: 2026-09-15 (session ~03:15-04:40+02:00) · Repo: meshcore (main) ·
Worker: dq05 (profile worker-heavy) · Host: `c03rad0r-DQ05proplus`.
Artifacts: this directory (`bench/chamber-ramp-rates/`).

Lifecycle: this is the **first worker output for this card**. Claim history
(fleet state): claimed by dq05 2026-09-14 (headroom 0.762) — resultless, no
artifact ever produced; re-claimed this session (`running[]` entry dq05,
ts 1789438521 = 2026-09-15 04:35:21+02:00). The only prior occurrences of
the card ID anywhere on record are two resultless listings: sibling
ramp-feasibility report `79ea692e` (its dead-card table) and the BOM report
`55585471` (its unresolved-dependency list). This report closes that gap.

---

## VERDICT SUMMARY — the authoritative numbers

**No chamber ramp rate is SPECIFIED anywhere and none is MEASURED anywhere:
the chamber has never been identified, so no manual/datasheet exists, and no
run has ever occurred, so no measured rate exists.** Both rate paths the card
contemplates (datasheet citation, or measurement with stated method) are dead
at the location gate. What this report produces instead — and what every
downstream analysis must use until a real unit is identified — is a set of
**labeled planning inputs** plus the only two on-record rate-adjacent
empirical anchors. These are the authoritative numbers *in the only sense
that currently exists*: they are the committed, cross-checked values the
fleet's feasibility chain already uses, with their provenance made explicit
and their uncertainty bounded.

### The deliverable, exactly as the card specifies

| # | Quantity | Value + unit | Load condition | Exact source | Provenance |
|---|---|---|---|---|---|
| 1 | **Nominal heating ramp rate (max)** | 3.0 C/min | small DUT load: one LR2021 module on a ~75x55 mm carrier PCB (~20-40 g) + one USB-C serial cable; assumed, not qualified by any datasheet (no datasheet exists) | Planning estimate for a compact environmental-chamber class, first issued in sibling report `bench/ramp-feasibility/REPORT.md` (commit `79ea692e`, Step 1 + source-summary table), grounded mid-range against the typical 2-5 C/min heating class for ESPEC/Thermotron/Binder-class compact chambers cited there | **PLANNING ESTIMATE — LOW confidence; NOT a datasheet spec, NOT measured.** No chamber manual exists (`t_a8b9d449` resultless; nameplate `24eb918c`, controller `766ac96d`, identify `t_a2f7f281` all dead: no make/model/serial on any record) |
| 2 | **Nominal cooling ramp rate (max)** | 1.5 C/min | same assumed small DUT load as row 1 | Same: `79ea692e` Step 1 — deliberately conservative mid-range pick from the 1-3 C/min unloaded cooling class it cites for compact chambers, chosen as the slow direction that dominates the descending setpoint sequence | **PLANNING ESTIMATE — LOW confidence; NOT a datasheet spec, NOT measured.** No measured cooling rate exists (chamber-holds `72f3aab9`: all four setpoints UNVERIFIED, "no chamber was commanded, no setpoint was reached or held, zero air-temp data exists"; soak-rollup `c4be4400`: zero calshow samples ever) |
| 3 | **Effective (de-rated) cooling ramp rate near the feedthrough** | **1.05 C/min** = 0.70 x 1.5 C/min | same as row 2, plus the cable cold-bridge across the boundary (below) | This report, Step 3 — derating factor **f = 0.70 (dimensionless multiplier; checkable formula: effective_rate = f x nominal_rate = 0.70 x 1.5 C/min = 1.05 C/min)**, continuing and formalizing the 70% assumption first stated in `79ea692e` Step 3 | **PLANNING ASSUMPTION — LOW confidence; NOT measured.** No feedthrough, gasket, or coax exists on any record to measure (`fe700201` fit survey, `40e1a49a` feedthrough survey, `621a2e57` penetration survey — all UNKNOWN at the location gate) |
| 4 | **Load condition assumed** | small module-class load, effectively unloaded | DUT = NiceRF LR2021 on SkyMapper Board A carrier (~20-40 g PCB, 2x soldered wire dipoles), one USB-C serial cable; chamber otherwise empty | Fork README `d7ae93fa:examples/passive_mapper/bench/README.md` "Bench setup" table (DUT row) read by SHA this session; DUT description per `0b7bfe92` (RF exits are soldered wire dipoles, no connectors on the measurement path) | **ASSUMED, stated explicitly.** No datasheet load-qualification exists to cite because no chamber datasheet exists; at this load mass, chamber-internal mass dominates, so de-rating with load is minimal (`79ea692e` Step 1) |
| 5 | **Only measured-adjacent empirical anchor** | 20-40 min per freezer setpoint (combined ramp + soak for a small module) | small module in freezer/chamber (operator context) | Fork README `d7ae93fa` verbatim: "Expect 20-40 min per freezer setpoint for a true soak on a small module." | **OPERATOR EMPIRICISM — MEDIUM confidence as a bound, NOT a rate.** It bounds the combined ramp+soak per transition; it is the only quantitative soak/ramp-time figure anywhere on record |

**The feedthrough derating, stated as a checkable number rather than prose
(card acceptance criterion):**

    f_derate = 0.70                     (dimensionless)
    effective_cooling_rate = f_derate x nominal_cooling_rate
                           = 0.70 x 1.5 C/min
                           = 1.05 C/min  (near the feedthrough)

**Cross-check against the on-record empirical bound (row 5):** the deepest
transition -20 -> -40 C at the derated 1.05 C/min takes 20/1.05 = 19.0 min of
ramp; with the 15 min settle+soak hold used by the feasibility chain, that is
34 min per transition — inside the 20-40 min/setpoint README band. At the
nominal (un-derated) 1.5 C/min the same transition is 13.3 + 15 = 28.3 min,
also inside. The derated number is therefore the conservative end of the
only empirical anchor on record, as it should be.

---

## STEP 1 — The specified maximum ramp rate: why neither rate path exists

### Path A (datasheet/manual rate): DEAD — no chamber has ever been identified

The chamber's make, model, serial, and controller have never been captured on
any record or host. Every card that would have produced a nameable unit — and
therefore a citable manual/datasheet — is dead, re-verified fresh this session:

| Card / report | What it would have given | Status |
|---|---|---|
| `t_a2f7f281` "Physically identify thermal chamber: make, model, serial, controller" | the unit identity that names its manual | decision `claim`, resultless |
| `t_ffc911f6` "Physically inspect thermal chamber and record verbatim nameplate data" | nameplate (would carry the model -> manual) | BLOCKED — "no chamber was located, zero data recorded" (`24eb918c`) |
| `t_a8b9d449` "Find chamber manual and cite setpoint range and ramp procedure by page" | the manual itself, ramp rate by page | skip->claim churn, resultless |
| `t_b09424f1` / `t_fbfead68` "Identify chamber (range/accuracy/ramp)" / "classify controller" | range/accuracy/ramp triple | resultless / UNKNOWN (`766ac96d`: "no chamber/controller exists on any record or host") |
| `t_deaaa866` "Establish chamber ramp rate (C/min) from datasheet or controller log" | this card's sibling | resultless |
| `t_c1c07af9` chamber-ownership (`4b3ec9b5`) | custodian who could name the unit | Felix MEDIUM (operator-scoping); no unit named |
| `t_f2b50f53` penetration/gasket survey (`621a2e57`) | the gasket the cables cross | BLOCKED at location gate, all dims UNKNOWN |

Host-side (all fresh checks by this session's siblings and by the
chamber-holds/preflight reports): no chamber controller process, no
SCPI/Modbus/LabVIEW software, no instrument-class USB (2x CH340 serial +
Pi Debugprobe + RTL8152 + microSD only), no chamber manual/datasheet file
anywhere on the filesystem. Fleet state re-read this session: **698 cards,
zero result-bearing keys in the schema** (programmatic key census: the schema
carries body/decision/claims metadata only — no result/output/artifact key
occurs even once). The fork README itself treats the cold source as
interchangeable — "freezer (-18..-20 C), dry-ice + IPA bath (~-78 C), or a
chamber" — i.e. the only chamber-consuming protocol on record does not even
assume a chamber exists.

**Therefore: no manual/datasheet ramp rate for heating or cooling exists to
cite, for any load condition.** Rows 1-2 of the deliverable table are the
standing planning estimates that fill this void, and they are labeled as
such.

### Path B (measured rate, with method): DEAD — no run has ever occurred

The card instructs: "If no datasheet rate exists, state the measurement
method used (e.g. two thermocouples, empty vs. loaded) and the measured
value." **No measurement exists to report, and no measurement method was
ever exercised.** The complete evidence:

- **No chamber commanded, ever:** chamber-holds `72f3aab9` — all four
  setpoints (+25/0/-20/-40 C) UNVERIFIED, "no chamber was commanded, no
  setpoint was reached or held, zero air-temp data exists"; the prior
  `done` ledger entry for that card produced no PASS and no log.
- **No soak ever run:** soak-rollup `c4be4400` — all four per-setpoint soak
  campaigns UNVERIFIED, zero calshow samples, zero measured die-temp bands.
- **No thermocouples or temperature-logging instruments exist on this host:**
  the only temperature sensor is the motherboard ACPI thermal zone
  (acpitz, 27.8 C — host-internal, explicitly NOT a chamber reading, per
  `72f3aab9`); USB census shows zero instrument-class devices; the
  chamber-preflight card `ec80c11e` is BLOCKED at its own attachment-proof
  gate ("worker NOT physically attached to any chamber").
- **The DUT itself is not attached** (ttyACM0 = Pi Debugprobe per `0b7bfe92`/
  `fe700201`), so even a DUT-side die-temperature ramp log is impossible
  today.

**Therefore: no measured ramp rate (heating or cooling, empty or loaded,
one- or two-thermocouple method) exists.** The only measurement-adjacent
figure on record is the operator-empirical 20-40 min/setpoint bound
(deliverable row 5), which is a combined ramp+soak time, not a rate.

### What the two planning rates are grounded in (and why these numbers)

From `79ea692e` Step 1, re-verified this session against every source it
cites: a standard compact environmental chamber (ESPEC/Thermotron/Binder
class) typically specifies 2-5 C/min heating and 1-3 C/min cooling unloaded,
de-rating with load. The 3.0 C/min heating pick is mid-range of that class;
the 1.5 C/min cooling pick is deliberately conservative (low-mid) because
(a) cooling is the slow direction and dominates the descending setpoint
sequence (+25 -> 0 -> -20 -> -40 C), and (b) if the "chamber" turns out to
be a kitchen freezer (the fork README's own fallback), natural compressor
cooling for a small load runs ~0.5-1.5 C/min — the 1.5 C/min estimate then
coincides with the *fast* end of the freezer range, i.e. it remains the
defensible middle of everything the unit could plausibly be. A dry-ice/IPA
bath (the README's other cold source) has no controlled ramp at all; the
ramp is the natural cooling transient.

**Bounding, from the record:** the condensation-risk report `65c9c3df`
(§4) already adopts 0.5 C/min as its slow-ramp mitigation figure and cites
`79ea692e`'s sensitivity table: 0.5 C/min (kitchen-freezer pace) -> ~3 h
total session; 1.0 -> ~1.8 h; 1.5 -> ~1.5 h; 3.0 -> ~1.1 h (3 ramps + 4
holds). **Even the slowest plausible rate (0.5 C/min) keeps the required
>= 2 ramps and 4 setpoints feasible in a single session**, so the
feasibility verdict is insensitive to which planning rate the chamber
finally proves out at — the rate uncertainty affects session length, not
feasibility.

---

## STEP 2 — Load-mass / chamber-fill dependence

**No datasheet qualification exists to record** (no datasheet exists), so
per the card's fallback the assumed load condition is stated explicitly:

**Assumed load condition (deliverable row 4):** one NiceRF LR2021 module on
a ~75x55 mm SkyMapper carrier PCB (module ~1-2 g, carrier PCB ~20-40 g
total), fitted with two soldered wire-dipole antennas (16.4 cm / 3.1 cm per
the wiring record cited in `0b7bfe92`) — i.e. a small module-class load,
effectively an empty chamber by the standards of test-chamber load ratings
(typically quoted per 25-50 kg of aluminum or steel product load).

Two load-related statements from the record:

1. **DUT mass is negligible; the cable load matters more.** The carrier
   PCB's thermal mass is orders of magnitude below the chamber-class load
   ratings the 2-5 / 1-3 C/min figures refer to, so the rates are not
   meaningfully de-rated by the DUT itself (`79ea692e` Step 1: "at this
   load mass, chamber ramp-rate de-rating is minimal (the chamber's
   internal mass dominates). The extra thermal load of the RF cabling is
   more significant than the DUT mass itself."). The one cable that
   crosses the boundary in the primary protocol is the USB-C serial
   cable (mass ~10-20 g class, industry-typical — no cable datasheet
   exists on host, UNVERIFIED); the optional conducted path adds two
   RG316 assemblies (0.15 m + 0.50 m, ~5-10 g each class-typical,
   UNVERIFIED).
2. **If the unit proves to be a kitchen freezer**, the README's empirical
   "20-40 min per freezer setpoint" was itself observed with exactly this
   load class (small module, sealed bag) — so the empirical anchor
   already embeds the assumed load condition.

**No rate-vs-load function can be given** — that would require the
chamber's datasheet. The load condition is frozen here as "small
module-class load, effectively unloaded" so any future datasheet can be
read against exactly this assumption.

---

## STEP 3 — RF cabling through the gasket: cold-bridge load and the de-rated effective rate

### What actually crosses the boundary (per the protocol of record)

- **Primary path (over-the-air edgescan):** the ONLY cable crossing the
  sealed boundary is the **USB-C serial cable** (DUT CLI at
  /dev/ttyACM0). The antenna lives inside the chamber, the reference TX
  lives outside at room temperature, and `scan_edges()` counts decoded
  packets — there is no RF cable on the RF path (fork README `d7ae93fa`
  "Bench setup" table; BOM `55585471` §3a "Total RF components needed:
  ZERO"; feedthrough survey `40e1a49a` concurs).
- **Optional conducted path** (only if OTA is rejected or the chamber
  proves to be a metal box): DUT SMA -> RG316 0.15 m (interior) -> SMA
  bulkhead feedthrough -> RG316 0.50 m (exterior) -> reference TX
  (`55585471` §3b; parts do not exist on any record — MUST-PROCURE).
- **Neither feedthrough nor gasket is known:** the fit survey (`fe700201`),
  feedthrough survey (`40e1a49a`), and penetration/gasket survey
  (`621a2e57`) are all UNKNOWN at the location gate — no gasket geometry,
  no feedthrough port, no coax exists on any record or host. The word
  "gasket" in this card refers to the door-seal class the cables would
  squeeze across; the 65c9c3df/fe700201 chain already establishes a
  gasket-crossing cable is a certain leak path (frost at the crossing),
  which matters for moisture, not for ramp rate.

### The two thermal penalties the crossing introduces

1. **Extra thermal load (mass term):** the crossing cable adds thermal
   mass the chamber must cool. For the primary path this is one USB-C
   serial cable (~10-20 g class); for the conducted path two RG316
   assemblies (~5-10 g each) plus a bulkhead connector body. All these
   masses are one-to-two orders of magnitude below any chamber-class load
   rating, so the *mass* penalty on the rate is negligible — consistent
   with Step 2's "effectively unloaded" load condition.
2. **Cold-bridge / heat-leak term (the one that matters):** the cable is a
   conductor from the warm room into the cold interior. With the
   exterior at ~+20-25 C and the chamber air at -40 C, a ~60-65 C
   gradient stands along the cable length. The copper conductors and
   shield braid carry heat inward continuously; the air volume near the
   crossing point is therefore held warmer than the chamber's bulk air,
   and the region near the feedthrough ramps slower. The DUT sits near
   the feedthrough (short interior cable: 0.15 m in the conducted
   variant; USB-C reach similarly short in the primary variant), so the
   DUT's local air is the de-rated region. This is the standard
   mechanism the failure-modes catalogue already carries
   (`04db4fae` FM-12: "cold metalwork extends below the lab dew point
   along any metal/heat-conductive path from the chamber"; `65c9c3df`
   §2b: exterior feedthrough face est. -15 to -30 C at the -40 C
   setpoint — the bridge works in BOTH directions; the inward leak is
   the ramp-rate term). No quantitative coax thermal-resistance model
   exists on record (no vendor datasheet on host, no outbound fetch
   permitted — standing dq05 constraint, respected this session).

### The de-rating, stated as the checkable number

**Assumption (explicit, per the card's own instruction):**

    cooling rate near the feedthrough assumed 70% of nominal
    f_derate = 0.70  (dimensionless multiplier)
    effective_cooling_rate = 0.70 x 1.5 C/min = 1.05 C/min

**Grounding for the 0.70 figure (all legs checkable):**

- **Not worse than 0.50:** the mass term is negligible (Step 2/3 above:
  grams vs. chamber-class ratings), so even a worst-case thin-gasket,
  thick-cable configuration cannot halve a rate whose load de-rating is
  already negligible; the 0.5 floor also corresponds to the
  kitchen-freezer *unloaded* natural pace already carried in the record's
  own sensitivity table (`79ea692e`, `65c9c3df` §4).
- **Not better than 0.90:** the bridge is certain to exist (60-65 C
  gradient over the crossing, copper-dominated), the crossing is certain
  to be imperfectly sealed (gasket-squeeze class per the leak-path
  chain), and the DUT is certain to sit within the affected air volume —
  so some derating is guaranteed; 0.90 is the thin-cable, good-port
  ceiling from `79ea692e` Step 3 caveat 2.
- **0.70 mid-range:** the same caveat bounds the plausible range as
  "50% (thick coax, poor seal) to 90% (thin coax, good port)"; 70% is
  its midpoint and is the value already committed in `79ea692e` Step 3,
  carried into the feasibility COMMENT (`bench/chamber-feasibility/
  COMMENT.md` lines 86-88: "feedthrough cold-bridge derating 70% of
  nominal -> 1.05 C/min effective"), and consumed downstream by the
  condensation-risk mitigation figures (`65c9c3df` §4 compares 0.5 vs
  1.5 C/min nominal). Keeping 0.70 maintains chain consistency; changing
  it now would silently invalidate two committed sibling analyses
  without new evidence.

**Effect of the derating on the worst-case transition (from `79ea692e`
Step 3, re-verified arithmetically this session):** -20 -> -40 C at
1.05 C/min = 19.0 min ramp vs. 13.3 min at nominal; full 4-setpoint
session at the derated rate = ~122 min (2.0 h) ramp+hold vs. ~103 min at
nominal. The >= 2-ramp feasibility verdict survives either way.

**What would replace 0.70 with a measured number (unblock path):** locate
and identify the chamber (cards `t_a2f7f281`/`t_b09424f1`/
`t_ffc911f6`/`t_a8b9d449`); obtain its manual's heating/cooling rate
spec and its load-qualification; then either read the gasket/feedthrough
geometry (`fe700201`/`40e1a49a`/`621a2e57` frozen conventions) into a
coax thermal-resistance model, or measure the rate near the feedthrough
directly with a second sensor during the first commanded run
(chamber-holds `72f3aab9` re-run with the DUT placed at the intended
position). Until then, 0.70 x nominal is the number this analysis uses.

---

## UNVERIFIED register (what a located chamber must resolve, nothing more)

| # | Unknown | Why it is unknown | What resolves it |
|---|---|---|---|
| 1 | Chamber identity (make/model/serial) | never captured; all identify cards resultless | `t_a2f7f281` family — one nameplate visit |
| 2 | Datasheet heating rate, load-qualified | no manual exists | `t_a8b9d449` — manual by page/section |
| 3 | Datasheet cooling rate, load-qualified | no manual exists | same |
| 4 | Measured empty-vs-loaded rates (any method) | no run ever occurred; no chamber, no thermocouples on host | chamber-holds re-run with two-sensor method (chamber air + near-feedthrough air), empty then loaded |
| 5 | Gasket/feedthrough geometry | all surveys UNKNOWN at location gate | `fe700201`/`40e1a49a`/`621a2e57` frozen caliper conventions |
| 6 | Coax/USB-C thermal data (conductivity, mass, length as routed) | no cable datasheet on host; no outbound fetch permitted | vendor datasheet at procurement (`55585471` BOM) |
| 7 | DUT-side measured ramp (die-temperature log) | DUT not attached (ttyACM0 = Pi Debugprobe) | attach DUT; `thermal_bench.py soak` produces the die-temp series |
| 8 | Actual derating factor f (vs. assumed 0.70) | product of unknowns 2/3/5/6 | measured rate near feedthrough vs. bulk air during first run (replaces 0.70) |

---

## Source summary

| Claim | Source | Confidence |
|---|---|---|
| No chamber identified: no make/model/serial/controller/manual/datasheet on any record or host | fleet state re-read this session (698 cards, zero result-bearing keys; programmatic key census); `t_a2f7f281`/`t_a8b9d449`/`t_b09424f1`/`t_ffc911f6`/`t_fbfead68`/`t_deaaa866` all resultless; nameplate `24eb918c` BLOCKED; controller `766ac96d` UNKNOWN; ownership `4b3ec9b5` (Felix MEDIUM, no unit named); preflight `ec80c11e` BLOCKED at attachment gate | HIGH (exhaustive; fresh re-verification) |
| No run ever occurred: no chamber commanded, no setpoint held, zero air-temp data | chamber-holds `72f3aab9` (all four setpoints UNVERIFIED, verbatim evidence section re-read this session); soak-rollup `c4be4400` (zero calshow samples); dryrun `ea8b9c8e` | HIGH |
| No thermocouple / temperature-logging instrument on host | `72f3aab9` §1 (USB census + SCPI/LXI port sweep); `40e1a49a` STEP 1 (zero instrument-class USB, no usbtmc/gpib); only sensor = motherboard acpitz | HIGH |
| Heating 3.0 C/min, cooling 1.5 C/min (planning inputs, small-load) | `79ea692e` Step 1 + source table; class grounding (2-5 / 1-3 C/min compact-chamber ranges) as cited there; NOT measured, NOT a datasheet value | LOW (labeled planning estimate — the only numbers that exist) |
| 0.70 feedthrough derating -> 1.05 C/min effective | this report Step 3 (formalization + bounds); original 70% assumption `79ea692e` Step 3 caveat 2 (range 50-90%); consumed by `bench/chamber-feasibility/COMMENT.md:86-88` and consistent with `65c9c3df` §4 sensitivity | LOW (planning assumption; bounds stated; checkable formula given) |
| 20-40 min per freezer setpoint (only empirical anchor) | fork README `d7ae93fa` verbatim (read by SHA this session) | MEDIUM (operator empiricism; bounds combined ramp+soak, not a rate) |
| Session-time sensitivity to rate: 0.5 C/min -> ~3 h; 3.0 -> ~1.1 h | `79ea692e` sensitivity table; `65c9c3df` §4 | MEDIUM (arithmetic on labeled inputs) |
| Load condition: small module (~20-40 g carrier), effectively unloaded; cable mass more significant than DUT mass | fork README `d7ae93fa` bench-setup table; `0b7bfe92` (DUT form: LR2021 + wire dipoles); `79ea692e` Step 1 | MEDIUM (assumed, stated; no datasheet qualification exists) |
| Primary path crosses ONLY a USB-C serial cable; zero RF feedthrough parts; conducted path = 2x RG316 + SMA bulkhead (MUST-PROCURE) | fork README `d7ae93fa`; `55585471` §3a/§3b; `40e1a49a` GAP section | HIGH (committed chain) |
| Gasket-crossing cable = certain leak path; feedthrough face -15..-30 C at -40 C setpoint | `65c9c3df` §2b/§4 (Magnus dew-point chain); `fe700201` §4; `04db4fae` FM-12 | HIGH (as committed; moisture chain, not rate) |
| No cable/vendor datasheet on host; no outbound fetch permitted (nothing attempted this session) | standing dq05 constraint; reaffirmed in `04db4fae` §6.5/`7` | HIGH |
| This is the first worker output for t_67f3b03e | grep of bench/ (only hits: `79ea692e` dead-card table, `55585471` unresolved-dependency list); fleet claims map (dq05 2026-09-14 resultless -> re-claimed this session) | HIGH |

---

## NOTHING FABRICATED

No chamber ramp rate was invented as a spec: the 3.0 / 1.5 C/min figures are
carried from the committed sibling analysis with their planning-estimate
label attached, not promoted to measurements. No chamber, thermocouple,
cable, gasket, or DUT was inspected (none exists on any record or host; the
DUT is not attached). No run was simulated. The derating 0.70 is presented
as an assumption with a checkable formula and explicit bounds, exactly as
the card's acceptance criterion demands. The only empirical figure quoted
(20-40 min/setpoint) is verbatim from the fork README. The fleet state was
read locally (established permitted pattern); no outbound probe was made.