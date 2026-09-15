# RF feedthrough list — chamber bulkhead survey

Fleet card: `meshcore:t_764d141d` — "Survey and identify all RF feedthroughs
on chamber bulkhead. Walk the entire chamber bulkhead and locate every RF
feedthrough, including spares, capped ports, and blank cutouts. For each,
identify the connector family on the chamber-interior side and chamber-exterior
side separately. If a connector cannot be positively identified, record what
would allow identification (thread pitch, pin diameter, keyway count). Assign
exactly one state per feedthrough: POPULATED, EMPTY, or NON-EXISTENT. Produce a
list of all feedthroughs with their location, interior/exterior connector types,
and state. This list is the input for subsequent measurement and cabling tasks."

Date: 2026-09-15 (fresh census 18:14:16+02:00) · Repo: meshcore (main) ·
Worker: dq05 · Host: `c03rad0r-DQ05proplus`.
Artifacts: this directory (`bench/chamber-rf-feedthrough-list/`) —
`FEEDTHROUGH-LIST.md` (this file) + `feedthrough_list.csv` (machine-readable
copy of the list, same rows).

Lifecycle: **first worker output for `t_764d141d`**. Claim history
(`fleet_queue_state.json`, read this session): claimed by dq05 ts
1789473878 (headroom 0.25), re-claimed ts 1789488776, running ts
1789489098 (this session). No prior output or result exists for this card.

Related committed outputs this list builds on (not duplicated here):
- `bench/chamber-rf-feedthroughs/REPORT.md` (`40e1a49a`, card `t_923c4eca`) —
  full evidence-backed F1-F5 record set, buy-or-fabricate gap, cabling inventory.
- `bench/connector-family-reference/REFERENCE.md` (`7b67b378`, card for the
  connector-family reference sheet) — 15-family master table with thread, hex,
  pin Ø, polarity; the source for the identification kit below.
- `bench/feedthrough-survey-protocol/PROTOCOL.md` (`abe0d36f`, card `t_03954030`)
  — normative ID scheme (FT-DOOR-n / FT-WALL-<SIDE>-n), measurement + photo rules.

---

## VERDICT

**SURVEY BLOCKED AT THE LOCATION GATE: no thermal chamber exists on any record
or host, so there is no bulkhead to walk.** The card's instruction to "walk the
entire chamber bulkhead" cannot be acted on — the premise that a chamber is
present is contradicted by every census and every prior report. Per the fleet
precedent (`24eb918c`/`ec80c11e`/`40e1a49a`/`fe700201`): record the
contradiction, do not simulate, and issue the deliverable with every field
filled — each field either UNKNOWN-with-reason or the on-record value that
constrains it.

**Result: 0 feedthroughs enumerated.** No bulkhead exists, so no penetration
of any kind exists. The 5 candidate classes any chamber of this measurement
class would present are carried below as **survey targets**, each assigned
state **NON-EXISTENT** (no penetration at all — there is no bulkhead). When a
human names the chamber, this list executes verbatim on one site visit: each
target upgrades to POPULATED or EMPTY with measured connector families — never
the reverse.

Fresh re-verification this session (2026-09-15T18:14:16+02:00):

| Check | Result |
|---|---|
| Serial `/dev/serial/by-id/` | 2x QinHeng CH340 (`ttyUSB0`/`ttyUSB1`) + Pi Debugprobe (`ttyACM0`), all attached 2026-09-14 11:05; zero instrument-class |
| `/dev/usbtmc*` `/dev/gpib*` | absent — no VNA / spectrum-analyzer / counter |
| `/dev/video*` `/sys/class/video4linux` | absent — no camera device on host |
| Filesystem `*chamber*` (excl bench/.git) | one false-positive bash-completion stub only (same as `40e1a49a`/`24eb918c`) |
| 9 prior bench reports | all concur no chamber: `40e1a49a`/`fe700201`/`24eb918c`/`766ac96d`/`ec80c11e`/`c5eb3c58`/`66573e52`/`55585471`/`f14f6a92` |

---

## THE LIST (deliverable)

One row per candidate feedthrough class. State vocabulary is exactly the three
values the card defines — **POPULATED** (usable connector/cable installed),
**EMPTY** (hole/cutout exists, no connector), **NON-EXISTENT** (no penetration
at all) — exactly one per feedthrough, no hybrid states.

| ID | Candidate class | Location | Interior-side connector | Exterior-side connector | State | What settles an UNKNOWN connector |
|---|---|---|---|---|---|---|
| FT-1 | Dedicated RF feedthrough port (SMA / N / bulkhead coax feedthrough) | UNKNOWN — no chamber located (`40e1a49a` STEP 0; fleet locate cards `t_a2f7f281`/`t_b09424f1` resultless) | UNKNOWN — no port to inspect; interior and exterior may differ (e.g. N-exterior / SMA-interior adapter feedthrough) — only a physical walk resolves each side separately | UNKNOWN — same; resolve with the identification kit below on first sight | **NON-EXISTENT** | thread major Ø + pitch, center-pin Ø, keyway/lug count (kit below) |
| FT-2 | Door-gasket pass-through (cable squeezed across the seal) | UNKNOWN — no door/gasket on record | N/A — a gasket crossing is a cable passage, not a connector; the cable itself crosses, connectors stay on their own side | N/A — same | **NON-EXISTENT** | N/A — no connector to identify; the cable family (not connector) is what matters here |
| FT-3 | Unused / capped / blank bulkhead holes | UNKNOWN — no unit on record | UNKNOWN until walked — a capped port could hide any family; a truly blank hole has no connector | UNKNOWN — same | **NON-EXISTENT** | thread major Ø + pitch, center-pin Ø, keyway/lug count; a blank hole: bore ID only (caliper) |
| FT-4 | Cable boot(s) / gland(s) (non-RF penetrations usable for coax) | UNKNOWN on the chamber | N/A — glands pass cable, not connectors | N/A — same | **NON-EXISTENT** | N/A — no RF connector; gland thread/size if assessing coax pass-through clearance |
| FT-5 | Spare flange / blank cutout (mountable location for a new feedthrough) | UNKNOWN — no unit on record | NONE — by definition an unpopulated mountable location | NONE — by definition | **NON-EXISTENT** | N/A — nothing installed to identify; panel thickness + cutout footprint decide what feedthrough can drop in |

**State assignment rationale:** NON-EXISTENT is the strongest defensible
classification when no chamber exists on any record — there is no bulkhead, hence
no penetration of any kind. A located chamber may upgrade any row to POPULATED or
EMPTY after a physical walk; the classification can only relax, never tighten.
No row is left without a state; no row carries a hybrid or "UNKNOWN" state —
UNKNOWN appears only in the connector and location fields, where it is a
field-level status with its reason, not a feedthrough-level state.

**On-record constraints that bound the connector fields when the chamber is
located** (carried from `40e1a49a`, not claims about any real part):

- The project's own SMA bulkhead pattern: 6.5 mm panel hole, O-ring weatherproof
  seal ("Two SMA bulkhead holes (6.5mm)", "Fully waterproof with SMA O-rings" —
  `enclosure/README_big.md:21-23`, read in `40e1a49a`).
- The planned procurement feedthrough class is an unfiltered SMA panel-mount
  jack-jack bulkhead (Amphenol 132134-class, `55585471` B2) — direct gold-plated
  contact pair, PTFE dielectric, no filter elements.
- **LOUD FLAG** (`40e1a49a` STEP 5): if the located chamber presents an OEM RF
  port, it may be a FILTERED bulkhead (standard in EMC chambers) — a filter would
  attenuate the 868 MHz reference unpredictably and silently corrupt the
  decode-edge measurement. Filter check (bulky body / feedthrough-capacitor
  construction / "filtered" marking) is a hard gate on the conducted path.
- The primary edgescan measurement path is OTA (over-the-air decode-counting)
  and needs ZERO RF feedthrough parts (`55585471` §3a, fork README `d7ae93fa`).
  The conducted path + feedthrough is optional, triggered only if the chamber
  walls are metal (Faraday cage) and OTA fails.

---

## IDENTIFICATION KIT — what resolves an UNKNOWN connector on first sight

The card requires: "If a connector cannot be positively identified, record what
would allow identification (thread pitch, pin diameter, keyway count)." Since no
connector can be positively identified (no chamber, no port), the resolving
discriminators are recorded here. All values are from the committed
connector-family reference (`7b67b378`); provenance per column.

| Family | Thread (exterior jack) | Pitch | Center pin Ø | Keyway / lugs | Impedance / class | Provenance |
|---|---|---|---|---|---|---|
| SMA | 1/4"-36 UNS, major 6.35 mm | 0.7056 mm/thread (36 TPI) | ~1.2-1.3 mm | none (threaded) | 50 Ω, DC-18 GHz | thread/hex COMMITTED `7b67b378` row 1; pin Ø CLASS-TYPICAL |
| RP-SMA | identical to SMA | identical | swapped: jack = pin ~1.2 mm | none | 50 Ω | COMMITTED `7b67b378` row 2 (hazard H2: will not mate with SMA) |
| 3.5 mm (precision) | 1/4"-36 UNS, 6.35 mm | 0.7056 mm | 1.52 mm (COMPUTED, 50 Ω air line) | none | 50 Ω, DC-26.5 GHz | COMMITTED + COMPUTED `7b67b378` row 3 |
| 2.92 mm (K) | 1/4"-36 UNS, 6.35 mm | 0.7056 mm | 1.27 mm (COMPUTED) | none | 50 Ω, DC-40 GHz | CLASS-TYPICAL + COMPUTED `7b67b378` row 4 |
| N | 5/8"-24 UNEF, major 15.875 mm | 1.0583 mm/thread (24 TPI) | ~1.6 mm | none (threaded) | 50 Ω, DC-11 GHz | thread COMMITTED `7b67b378` row 5; pin Ø CLASS-TYPICAL |
| RP-N | identical to N | identical | swapped: jack = pin | none | 50 Ω | CLASS-TYPICAL `7b67b378` row 6 |
| TNC | 7/16"-28 UNEF, major 11.1125 mm | 0.9071 mm/thread (28 TPI) | ~1.0-1.1 mm | none (threaded) | 50 Ω, DC-11 GHz | thread COMMITTED `7b67b378` row 7; hex CORRECTED to 12.7 mm there |
| RP-TNC | identical to TNC | identical | swapped: jack = pin | none | 50 Ω | CLASS-TYPICAL `7b67b378` row 8 |
| BNC | none (bayonet) | n/a | ~1.0-1.1 mm | **2 bayonet lugs** | 50/75 Ω, DC-4 GHz | bayonet/lugs COMMITTED `7b67b378` row 9; pin Ø CLASS-TYPICAL |
| RP-BNC | none (bayonet) | n/a | swapped: jack = pin | 2 lugs | 50 Ω | CLASS-TYPICAL `7b67b378` row 10 |
| SMB | none (snap-on) | n/a | ~0.5 mm | none (snap) | 50 Ω, DC-4 GHz | CLASS-TYPICAL `7b67b378` row 11 |
| MCX | none (snap-on) | n/a | ~0.4-0.5 mm | none (snap) | 50 Ω, DC-6 GHz | CLASS-TYPICAL `7b67b378` row 12 |
| MMCX | none (snap-on) | n/a | ~0.3 mm | none (snap) | 50 Ω, DC-6 GHz | CLASS-TYPICAL `7b67b378` row 13 |
| SMP | none (push-on) | n/a | ~0.5 mm (jack = pin, inverted) | none (push) | 50 Ω, DC-40 GHz | CLASS-TYPICAL `7b67b378` row 14 |
| U.FL / I-PEX MHF1 | none (snap/push) | n/a | ~0.3-0.4 mm (receptacle = pin, inverted) | none (snap) | 50 Ω, DC-6 GHz | COMMITTED anchor `7b67b378` row 15; pin Ø CLASS-TYPICAL |

**First-sight procedure** (mirrors `40e1a49a:148-154` and the caliper protocol
`t_03954030`): for each located port, measure thread major OD with calipers
(discriminates SMA/3.5 mm/2.92 mm 6.35 mm vs TNC 11.1 mm vs N 15.9 mm), count
threads per 25.4 mm (36 -> SMA group; 28 -> TNC; 24 -> N), measure hex across
flats (7.94 mm -> SMA group; 12.7 mm -> TNC; 17.46 mm -> N), look for bayonet
lugs (2 lugs -> BNC family), check center-contact gender (pin-in-plug vs
pin-in-jack resolves standard vs RP), and look for any "DC-… GHz" or filter
marking on the body. Measure each bore twice 90° apart (protocol §3); mark
ELLIPTICAL if readings differ > 0.2 mm.

**Four pairs are UNSEPARABLE without a center-contact (pin-location) photo**
(`7b67b378` confusion notes): SMA/RP-SMA, N/RP-N, TNC/RP-TNC, BNC/RP-BNC —
identical thread + hex, only the center-contact location differs. Two more
need a marking/photo: SMA-vs-3.5 mm/2.92 mm (same thread, air vs PTFE
dielectric), BNC 50-vs-75 Ω (same body, different impedance).

---

## UNBLOCK PATH (unchanged in kind, now with this list)

1. **A human names the unit and its location** (or connects it to a fleet host):
   cards `t_a2f7f281` (identify), `t_b09424f1` family, `t_ffc911f6` (nameplate)
   are the standing resultless blockers.
2. **One caliper site visit**: walk the bulkhead with this list (FT-1…FT-5),
   measure each port's thread OD / pitch / hex AF / pin Ø / hole ID / panel
   thickness, apply the identification kit, and assign the real state
   (POPULATED / EMPTY / NON-EXISTENT) per port. Use the ID scheme from
   `bench/feedthrough-survey-protocol/PROTOCOL.md` (FT-DOOR-n / FT-WALL-<SIDE>-n)
   for the actual enumerated ports.
3. **Check every located port for filter construction** (LOUD FLAG above) before
   allowing it into the RF path.
4. **Custodian gate**: any drilling goes through Felix (`4b3ec9b5` MEDIUM).
5. Re-dispatch this card with the measured list; downstream measurement and
   cabling tasks consume the populated rows.

---

## NOTHING FABRICATED

No physical measurement, photograph, or connector identification was invented.
No feedthrough was simulated. The list reports 0 enumerated feedthroughs because
no chamber/bulkhead exists on any record or host (re-verified fresh this
session). Every candidate-class row carries state NON-EXISTENT with its reason.
Every connector field is UNKNOWN with its reason, or carries the on-record
constraint that bounds it (cited). The identification kit values are labeled
COMMITTED / COMPUTED / CLASS-TYPICAL per the connector-family reference; no
outbound fetch was attempted (standing dq05 constraint respected). The fleet
state was read locally (established permitted pattern).
