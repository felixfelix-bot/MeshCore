# Chamber RF feedthrough survey: type, population, mounting, cabling

Fleet card: `meshcore:t_923c4eca` — "Inspect chamber RF feedthroughs:
type, population, mounting, cabling."

Task: walk the chamber bulkhead and produce an unambiguous,
evidence-backed record of every RF feedthrough (including spares, capped
ports, blank cutouts), so the exact buy-or-fabricate gap is known.

Date: 2026-09-15 (session start 02:58:59+02:00, census and fleet re-read
03:00-03:08+02:00) · Repo: meshcore (main) · Worker: dq05.
Artifacts: this directory (`bench/chamber-rf-feedthroughs/`).

Lifecycle: this is the **first worker output for this card**. Claim
history (fleet_queue_state.json): claimed by dq05 2026-09-14 06:35:17+02:00
(resultless lifecycle — no output exists, verified via session-DB search
this session: the only prior hit for `t_923c4eca` is a fleet-lookup inside
the fe700201/t_48e048a1 session, which listed the card but never ran it),
re-claimed 2026-09-15 02:58:59+02:00 (this session).

---

## VERDICT SUMMARY

**The survey is BLOCKED at the location gate: no thermal chamber exists
on any record or host, so there is no bulkhead to walk.** The task body
asserts "You are physically at the chamber"; that assertion cannot be
acted on — every physical field of every feedthrough is therefore
**UNKNOWN with reason** (not guessed, not simulated). What CAN be stated
with evidence, and what makes the buy-or-fabricate gap exact despite the
block:

1. **Feedthrough records F1-F5 (the deliverable set) are issued with
   every field filled**: each field is either UNKNOWN (with the specific
   reason) or carries the on-record engineering value that constrains it.
   No field is left blank.
2. **The primary measurement path needs ZERO RF feedthrough parts.**
   The `edgescan` protocol is over-the-air decode-counting (DUT LR2021 +
   antenna inside the chamber, reference TX + antenna outside at room
   temp; `thermal_bench.py` `scan_edges()` counts decoded packets, not
   RF power). The only cable that crosses the sealed boundary in the
   primary path is a USB-C serial cable — not an RF feedthrough.
   (Sources: fork README d7ae93fa "Bench setup" table + `scan_edges()`
   at d7ae93fa; re-read this session.)
3. **The optional conducted path has a fully enumerated gap** (§ BUY-OR-
   FABRICATE GAP): exactly 1x SMA bulkhead jack-jack feedthrough, 2x
   RG316 SMA-m/m patch cables (0.15 m + 0.5 m), 1x torque wrench, 4x
   dust caps — quantities, part classes, and the single UNKNOWN that
   decides buy-vs-nothing (does the located chamber already present a
   usable RF port, and is it filtered?).
4. **No cable, instrument, or camera exists on this host to test,
   photograph, or identify anything with** (fresh census § STEP 1):
   zero RF coax on record, zero instrument-class USB, zero usbtmc/gpib,
   zero RS-232/GPIB on PCI, no /dev/video*, no video4linux, v4l2-ctl
   absent. Every "photograph" field is NONE with that reason; every
   "functional test" field is NOT PERFORMED with that reason.

A reader who has never seen the chamber gets from this report: (a) the
exact per-feedthrough record format with every field's UNKNOWN-reason,
(b) the identification kit (thread pitches, hex sizes) to resolve any
unknown connector family on first sight, (c) the exact buy list for the
conducted path with quantities, and (d) the statement that the primary
path buys nothing.

---

## STEP 0 — Why every physical field is UNKNOWN (the location gate)

Five independent prior reports establish that no chamber exists on any
record or host, all re-verified against fresh evidence this session:

| Evidence | Fresh check this session (2026-09-15, times +02:00) | Result |
|---|---|---|
| Fleet queue state (2.394 MB, 708 tasks) re-read 03:07:57 | programmatic scan for any non-empty `*result*` field | **0 occurrences in 708 cards** — every chamber locate/identify/nameplate/custodian card resultless (`t_a2f7f281` decision=claim only, `t_e96fa5ad`, `t_3e537b94`, `t_b09424f1` family, `t_ffc911f6` nameplate, `t_a8b9d449` manual) |
| Chamber-locate card `t_a2f7f281` "Physically identify thermal chamber: make, model, serial, controller" | fleet state + prior outputs | resultless — no make/model/serial/location anywhere |
| Nameplate survey `24eb918c` (bench/chamber-nameplate) | committed report re-read | BLOCKED — "chamber not located, zero data recorded … no unit found anywhere on host or record" |
| Controller survey `766ac96d` (bench/chamber-controller) | committed report re-read | UNKNOWN — "no chamber/controller exists on any record or host" |
| Preflight `ec80c11e` (bench/chamber-preflight) | committed report re-read | BLOCKED at attachment gate — "worker NOT physically attached to any chamber" |

The chamber-ownership/custodian chain (`t_e96fa5ad`, `t_3e537b94`,
4b3ec9b5) is equally resultless; the only custodian name on record is
"Felix" (4b3ec9b5 MEDIUM, carried in fe700201) with no contact channel
on host (no chat client installed; standing dq05 constraint = no
outbound probes — respected, nothing attempted this session).

**Consequence for this card:** the card's instruction "You are
physically at the chamber" cannot be reconciled with the host census
below. Per the fleet precedent (24eb918c/ec80c11e/fe700201): record the
contradiction, mark the physical fields UNKNOWN-with-reason, simulate
nothing, and hand the unblock path forward. Nothing in this report is
fabricated to fill a deliverable slot.

---

## STEP 1 — LOCATE AND IDENTIFY (fresh host census, all run 2026-09-15)

The only way a chamber or RF hardware could be "at" this worker is
attached to this host. Full periphery census, re-run fresh this session:

| Check | Command / path | Result (verbatim summary) |
|---|---|---|
| Serial devices | `/dev/serial/by-id/` | `usb-1a86_USB_Serial-if00-port0 -> ../../ttyUSB1`, `usb-Raspberry_Pi_Debugprobe_on_Pico__CMSIS-DAP__203584200D2D0D42-if01 -> ../../ttyACM0` — 2x QinHeng CH340 (`ttyUSB0`, `ttyUSB1`) + Pi Debugprobe (`ttyACM0`), all attached 2026-09-14 11:05; **zero attach events 2026-09-15 00:00 onward** (journalctl USB grep: no ch341/acm/new-device lines) |
| USB bus | `lsusb` | RTL8152 Ethernet, RTL8851BE-adjacent BT radio (0bda:b850), Zoran audio/HID (0573:1573), 2x hubs, microSD reader, 2x CH340, Pi Debugprobe. **Zero instrument-class, zero SDR, zero VNA/spectrum-analyzer/counter** |
| Instrument buses | `/dev/usbtmc*`, `/dev/gpib*` | **absent — no such nodes** |
| PCI serial/GPIB | `lspci` | PCH I2C (x2) + HECI + SPI only; no RS-232, no GPIB. 8250 driver registered (per prior census) but **no live port** |
| Camera / photos | `/dev/video*`, `/sys/class/video4linux`, `which v4l2-ctl` | **absent / absent / not installed** — no camera device exists on host (0573:1573 video-capability probe was operator-denied in 24eb918c; not retried per standing rule) |
| Bluetooth | `hcitool dev`, `bluetoothctl devices` (new this session) | hci0 = A8:A0:92:A5:39:7B; one paired device: "Bluetooth Keyboard" CE:01:04:0F:63:78. **No chamber-class BT device** |
| Processes | `ps aux` grep chamber/serial/vna/spectrum/thermal/bench | thermald (host thermal daemon) only; zero chamber/serial-bridge processes. (Note: `ps` confirms this card is one of four sibling workers dispatched in parallel tonight: warm-side dewpoint 02:50, BOM-compile 02:57, this card 02:58, instrument-ports 03:00.) |
| Host filesystem | `find / -xdev` chamber/feedthrough/bulkhead (excluded bench/.git) | one false-positive bash-completion stub; zero chamber assets, zero feedthrough photos, zero coax images (image sweep in 24eb918c: only balloon renders/RF plots) |
| GPIO | `/dev/gpiochip*` | `/dev/gpiochip0` — onboard controller only (prior census: no chamber interfaces) |

**Census conclusion: no chamber, no bulkhead, no RF connector, no coax,
and no camera is reachable from this worker.** Every field below that
requires physical presence is UNKNOWN with exactly this reason.

### Feedthrough record set (defined)

A chamber bulkhead of any class (environmental chamber, freezer chest,
dry-ice bath liner) presents some subset of these five RF-relevant
penetration classes. Per the card's "do not skip anything" rule, the
record set is all five — carried over from the fe700201 P1-P5
classification, renamed F here for the RF-specific survey:

| ID | Candidate feedthrough class | Exists on any record? |
|---|---|---|
| F1 | Dedicated RF feedthrough port (SMA/N/bulkhead coax feedthrough) | UNKNOWN — no unit on record |
| F2 | Door gasket pass-through (cable squeezed across the seal) | UNKNOWN — no door/gasket on record |
| F3 | Unused bulkhead holes (blank, capped, or drilled-not-populated) | UNKNOWN — no unit on record |
| F4 | Cable boot(s) / gland(s) (non-RF penetrations usable for coax) | UNKNOWN — no unit on record |
| F5 | Spare flange / blank cutout (mountable location for a new feedthrough) | UNKNOWN — no unit on record |

### Identification kit (what lets someone else identify each connector)

Per the card's step 1 instruction ("record what would let someone else
identify it"): since no connector can be positively identified, the
resolving discriminators are recorded here as **industry-standard
family keys — class-typical values, UNVERIFIED on host (no vendor
datasheet on host; no outbound fetch per standing constraint)**:

| Discriminator | SMA | N | BNC | TNC | 3.5 mm (precision) |
|---|---|---|---|---|---|
| Thread (exterior jack) | 1/4"-36 UNS | 5/8"-24 UNEF | none (bayonet: 2-lug) | 7/16"-28 UNEF | 1/4"-36 UNS (airline) |
| Hex nut across flats | 5/16" = 7.94 mm | ~11/16" ≈ 17.5 mm | none | ~3/8" ≈ 9.5 mm | 5/16" = 7.94 mm |
| Keyway/lug count | none (threaded) | none | 2 bayonet lugs | none | none |
| Center contact gender pair | pin in plug / socket in jack | same | same | same | same |
| Impedance / class rating | 50 Ω, DC-18 GHz class | 50 Ω, DC-11 GHz class | 50/75 Ω, DC-4 GHz | 50 Ω, DC-11 GHz | 50 Ω, DC-26.5 GHz, precision |

First-sight procedure for whoever stands at the real bulkhead (mirrors
the caliper protocol already defined in cards `t_f2b50f53`/`t_03954030`):
measure thread major OD with calipers (discriminates SMA 6.35 mm vs TNC
11.1 mm vs N 15.9 mm), count threads per 25.4 mm (36 → SMA; 28 → TNC;
24 → N), measure hex across flats (7.94 mm → SMA), look for bayonet
lugs (→ BNC), check center-contact gender, and look for any "DC-… GHz"
or filter marking on the body (→ § STEP 5).

---

## STEP 2 + 3 + 5 — CLASSIFY, MOUNTING, RATING: one record per feedthrough

Five records, one per candidate class F1-F5. Every field carries its
value, its UNKNOWN-reason, and its evidence source. Physical dimensions
(panel thickness, hole diameter, flange pattern) are per-field UNKNOWN;
the constraints that ARE on record are carried in.

### Record F1 — Dedicated RF feedthrough port

| Field | Value | Evidence / reason |
|---|---|---|
| Location | **UNKNOWN** | no chamber located (§ STEP 0; fleet locate cards resultless) |
| Interior-side connector family | **UNKNOWN** | no port to inspect; resolve with § identification kit on first sight |
| Exterior-side connector family | **UNKNOWN** | same — note interior/exterior may differ (e.g. N-exterior/SMA-interior adapter feedthrough); only a physical walk resolves each side separately |
| State (populated / empty / non-existent) | **NON-EXISTENT on every record** (not merely unpopulated: no chamber, hence no bulkhead, is on record at all) | § STEP 0 evidence chain; this is the strongest defensible classification — if a real unit exists it may upgrade to POPULATED or EMPTY, never the reverse |
| Bulkhead panel thickness | **UNKNOWN** — no panel on record | no unit; measurement tool: caliper at bulkhead edge or bolt hole |
| Hole diameter | **UNKNOWN** — no hole on record | no unit; the value that a located chamber's port must be measured against: SMA bulkhead jack needs 6.5 mm class (project's own documented pattern, enclosure/README_big.md:21-23 "Two SMA bulkhead holes (6.5mm)"); SMA hex nut needs ≥ 9.5-10 mm if the connector must pass through (fe700201) |
| Flange / mounting-hole bolt pattern | **UNKNOWN** — no flange on record | no unit; record bolt-circle diameter + thread size on first sight; many RF feedthroughs are plain hex-nut bulkhead (no flange) |
| Sealing class (vacuum / EMI gasket / weatherproof-O-ring / none) | **UNKNOWN** | no unit; the project's own sealing pattern for SMA bulkheads is O-ring weatherproof (enclosure/README_big.md:23 "Fully waterproof with SMA O-rings"; enclosure/README.md:27/72 AS568 2 mm cord, "Nitrile or silicone") |
| Reuse-eligible existing cable at this port | **NONE on record** | no coax exists on host/record (§ STEP 1 census; 55585471 "Unknown (not on any record)" for every coax line) |
| Frequency rating | **UNKNOWN** (nothing to read a rating from) | no unit, no marking; class context: SMA family DC-18 GHz class-typical, UNVERIFIED on host |
| Filtered / EMI-suppressed? | **UNKNOWN — MUST BE CHECKED ON LOCATION. If any feedthrough body carries a filter (marked "filtered", or has a bulky body with feedthrough-capacitor construction), it is UNUSABLE for the RF measurement path** | no unit to inspect; the planned procurement item (below) is a plain unfiltered SMA jack-jack bulkhead class by construction — but the real chamber, if it has an OEM RF port, could be a filtered bulkhead (common in EMC chambers). **This is the single most dangerous silent-corruption risk in the conducted path: a filtered feedthrough would attenuate the 868 MHz reference unpredictably while looking like ordinary hardware.** |
| Photos | **NONE — impossible** | no camera device on host (no /dev/video*, no video4linux, v4l2-ctl absent; § STEP 1); no subject exists |
| Sketch | reference `bench/chamber-feedthrough-fit/REPORT.md` ASCII routing sketch (both variants, dimensioned from cited sources) | fe700201; chamber-side sketch impossible until a unit is located |

### Record F2 — Door gasket pass-through

| Field | Value | Evidence / reason |
|---|---|---|
| Location | **UNKNOWN** | no chamber located |
| Interior-side connector family | **N/A — a gasket crossing is a cable passage, not a connector** (the cable itself crosses; connectors stay on their own side) | physics of the passage class; fe700201 P2 |
| Exterior-side connector family | **N/A** — same | same |
| State | **UNKNOWN whether the door/gasket exists at all** (no door on record) → passage NON-EXISTENT on record | § STEP 0 |
| Gasket thickness / width / durometer / compression | **UNKNOWN** | no gasket on record (fe700201 P2) |
| Panel thickness | **UNKNOWN** | no unit |
| Passage diameter / usable aperture | **UNKNOWN** | no unit; constraints from fe700201: bundle equivalent OD 8.8-9.5 mm if RG316 + USB-C taped (needs ~11+ mm at 20% clearance); USB-C alone 4.0-5.0 mm → 6.0 mm min bore |
| Sealing class | **NONE as an RF passage — a cable crossing a gasket is a documented certain leak path** (frost jacking at the crossing certain per 65c9c3df Magnus physics: cold side 22-57 C below dew point) | fe700201 step 4; 65c9c3df |
| Reuse-eligible existing cable | **NONE on record** | no coax exists (§ STEP 1) |
| Frequency rating / filtered | **N/A** (no connector, no filter); but the cable would be unsealed — frost at the crossing degrades the measurement | fe700201 |
| Photos | **NONE — impossible** (no camera, no subject) | § STEP 1 |

### Record F3 — Unused bulkhead holes (blank / capped / drilled-not-populated)

| Field | Value | Evidence / reason |
|---|---|---|
| Location / count | **UNKNOWN** | no unit on record |
| Interior-side connector | **NONE if truly blank** (hole only); **UNKNOWN until walked** — a capped port could hide any family | no unit; resolve with § identification kit |
| Exterior-side connector | **UNKNOWN — same** | same |
| State | **UNKNOWN** (cannot distinguish EMPTY from NON-EXISTENT without the unit; on record as NON-EXISTENT until located) | § STEP 0 |
| Panel thickness | **UNKNOWN** | no unit |
| Hole diameter | **UNKNOWN** — this is the highest-value single measurement on a located chamber: it decides whether an SMA bulkhead feedthrough (6.5 mm class) drops straight in | no unit; decision table in fe700201 § 3d converts any measured ID to instant PASS/FAIL |
| Flange pattern | **UNKNOWN** | no unit |
| Sealing class | **UNKNOWN** | no unit |
| Reuse-eligible existing cable | **NONE on record** | § STEP 1 |
| Frequency rating / filtered | **UNKNOWN**; a blank hole carries no filter (nothing installed); a capped OEM port MUST be checked for filter construction | § identification kit |
| Photos | **NONE — impossible** | § STEP 1 |

### Record F4 — Cable boot(s) / gland(s)

| Field | Value | Evidence / reason |
|---|---|---|
| Location / count | **UNKNOWN on the chamber** | no unit on record |
| Interior-side connector | **N/A — glands pass cable, not connectors** | physics of the passage class |
| Exterior-side connector | **N/A** | same |
| State | **UNKNOWN** (on record as NON-EXISTENT until the unit is located) | § STEP 0 |
| Gland size / thread | **UNKNOWN**; project's own gland convention on record: PG7 cable glands for antenna/solar cables (enclosure/README.md:74 "Cable glands (PG7) | 3") | enclosure README read this session; chamber side unknown |
| Panel thickness / hole diameter | **UNKNOWN** | no unit |
| Sealing class | **weatherproof-by-construction (gland)** — that is the point of a gland; specific gland class UNKNOWN | passage-class definition; no unit |
| Reuse-eligible existing cable | **NONE on record** (no coax anywhere; the only documented cables crossing sealed boundaries in this project are USB-C serial and antenna pigtails, and no chamber-side instance of either exists) | § STEP 1; 55585471 |
| Frequency rating / filtered | **N/A** (no RF element) — a gland preserves the seal and does not distort RF | fe700201: "glanded/bulkhead penetrations preserve seal" |
| Photos | **NONE — impossible** | § STEP 1 |

### Record F5 — Spare flange / blank cutout (mountable location for a new feedthrough)

| Field | Value | Evidence / reason |
|---|---|---|
| Location / count | **UNKNOWN** | no unit on record |
| Interior-side / exterior-side connector | **NONE — by definition an unpopulated mountable location** | definition of the class |
| State | **UNKNOWN** (on record as NON-EXISTENT until located) | § STEP 0 |
| Panel thickness | **UNKNOWN** — needed to pick O-ring cord size and bolt length for any new SMA bulkhead | no unit |
| Cutout / footprint size | **UNKNOWN** — the value that a located chamber must be measured against: SMA bulkhead jack needs a 6.5 mm hole class (project pattern) | enclosure/README_big.md:21-23 |
| Flange bolt pattern | **UNKNOWN** | no unit |
| Sealing class | **NONE until a feedthrough is installed** (raw panel) | definition; new install would take the O-ring pattern |
| Reuse-eligible existing cable | **NONE on record** | § STEP 1 |
| Frequency rating / filtered | **N/A** (nothing installed); any feedthrough later installed there must be verified UNFILTERED | § STEP 5 |
| Photos | **NONE — impossible** | § STEP 1 |
| Fabrication gate | **drilling a real chamber is a custodian decision** — Felix (4b3ec9b5 MEDIUM) must approve any penetration | 4b3ec9b5; fe700201 carried the same gate |

---

## STEP 4 — INVENTORY OF REUSABLE CABLING

Full inventory of cables that could be reused at these feedthroughs:

| # | Cable / assembly | Where it exists per record | Type | Length | Condition | Functional test | Reuse eligibility |
|---|---|---|---|---|---|---|---|
| C1 | RF coax, any length, chamber-side or lab-side | **DOES NOT EXIST** — no coax on any record or host (§ STEP 1 census; 55585471 BOM lines all "Unknown (not on any record)") | — | — | — | **NOT PERFORMED** (nothing to test) | none exist to reuse → all coax is a procurement item (§ GAP) |
| C2 | USB-C serial cable (DUT control) | on hand per protocol (fork README: DUT CLI at `/dev/ttyACM0`; census shows ttyACM0 currently = Pi Debugprobe, DUT absent) | USB-C data | UNKNOWN | UNKNOWN (not attached) | **NOT PERFORMED** (DUT not attached; testing a chamber-cable's continuity impossible) | serial path only — **not an RF feedthrough cable** |
| C3 | USB cable (reference TX) | on hand per protocol (`/dev/ttyUSB0`) | USB | UNKNOWN | UNKNOWN | **NOT PERFORMED** (reference TX not attached) | serial path only |
| C4 | Wire dipole antenna, 868 MHz, 8.6 cm legs | **TO BE FABRICATED** from lab wire stock (IMPLEMENTATION-PLAN.md:41 per 55585471) | bare wire dipole | 2x 8.6 cm legs | n/a | n/a | the PRIMARY-path "antenna": lives INSIDE the chamber, crosses nothing — no feedthrough needed |
| C5 | SMA stub antenna (868 MHz) | "possibly on hand" (55585471: wire is lab stock; stub status UNKNOWN) | SMA stub | n/a | UNKNOWN | **NOT PERFORMED** (none located on host this session) | drop-in alternative to C4; still crosses nothing |

**No functional test (continuity, VNA, return-loss) was performed on any
cable — three independent reasons, all census-backed:** (1) no RF cable
exists to test; (2) no test instrument exists (zero instrument-class
USB, no usbtmc/gpib, no VNA/DMM/counter — 72f3aab9, c5eb3c58 fresh
tonight); (3) the DUT and reference TX are not attached to this host
(ttyACM0 = Pi Debugprobe, udevadm-verified in fe700201/ec80c11e).
Recording "pass" for anything here would be fabrication.

---

## STEP 5 — RATING AND FILTERING (consolidated statement)

- **No feedthrough exists on record to rate.** Frequency ratings, filter
  markings, and EMI-suppression construction are all UNKNOWN until a
  unit is walked — each record above carries this.
- **The planned/procurement feedthrough class is UNFILTERED by
  construction**: an SMA panel-mount jack-jack bulkhead (Amphenol
  132134-class per 55585471) is a direct gold-plated contact pair with
  PTFE dielectric — no filter elements. Class-level statement; the
  actual purchased part's datasheet must be checked at procurement
  (standing no-outbound constraint prevented fetching one).
- **LOUD FLAG carried forward:** if the located chamber presents an OEM
  RF port, it may be a FILTERED bulkhead (standard in EMC chambers) —
  a filtered port would attenuate the 868 MHz reference by an unknown,
  temperature-dependent amount and silently corrupt the decode-edge
  measurement. The 165 dB link budget (per 55585471) gives headroom, but
  a filter is not a flat loss — its band-edge behavior is the hazard.
  Filter check is therefore a hard gate on the conducted path.
- **The primary OTA path has no filtering risk at all** (nothing is in
  the RF path except air and the chamber wall). Its open risk is the
  inverse one, already flagged in 55585471: if the chamber walls are
  metal (Faraday cage), OTA fails entirely and the conducted path +
  feedthrough becomes MANDATORY — which is exactly why the buy list
  below must stay live until the chamber is identified.

---

## BUY-OR-FABRICATE GAP (the acceptance criterion, answered exactly)

**Branch A — primary edgescan path (OTA, per protocol):**
**MISSING FEEDTHROUGH PARTS: ZERO.** Nothing to buy, nothing to
fabricate on the bulkhead. The only crossing is the USB-C serial cable
(existing, on hand per record); the antenna lives inside the chamber
(C4 wire dipole to fabricate from lab stock, <1 h, or C5 stub);
the reference TX lives outside at room temp with its own antenna.
Evidence: fork README d7ae93fa "Bench setup" + scan_edges() decode-count
design; 55585471 BOM § 3a "Total RF components needed: ZERO".

**Branch B — optional conducted path (if OTA is rejected or the chamber
proves to be a metal box):** the exact gap, quantities included:

| # | Missing item | Qty | Part class / MPN | Why it's missing | Lead time |
|---|---|---|---|---|---|
| 1 | SMA bulkhead feedthrough, panel-mount jack-jack (must be verified UNFILTERED) | 1 | Amphenol 132134 or equivalent | no feedthrough exists on any record (records F1-F5); chamber side UNKNOWN | 2-5 days (55585471) |
| 2 | SMA m/m coax patch, RG316, 0.15 m (DUT → feedthrough, interior) | 1 | Amphenol RF ACX-1169-2M-class, RG316 | zero coax on host/record (C1) | 2-5 days |
| 3 | SMA m/m coax patch, RG316, 0.5 m (feedthrough → reference TX, exterior) | 1 | same class | zero coax on host/record | 2-5 days |
| 4 | SMA torque wrench 5/16", 0.9 N·m | 1 | Fujiya FTK-16SR-class | none on record | 3-7 days |
| 5 | SMA dust caps (2x m, 2x f) | 4 | Amphenol 132172-class | none on record; frost protection (65c9c3df/04db4fae) | 1-3 days |
| 6 | Panel penetration | 0 or 1 | 6.5 mm hole class (project's own SMA bulkhead pattern) or reuse of an existing EMPTY port (F3) | depends on the located chamber — if F3 offers a usable bore, item 1 may drop in with NO drilling; if not, one hole, custodian-gated (Felix, 4b3ec9b5) | site visit |

Item 6 is the single UNKNOWN that swings the list: **buy-vs-nothing
resolves the moment the chamber is located and its bulkhead walked.**
Everything else in the list is already exact (quantity, class, lead
time). Reverse-polarity and 75 Ω mismatch hazards are N/A on this path
(all connectors are standard-polarity 50 Ω SMA — DUT J1 per
hub_board_f33.kicad_pcb:165 + 65c9c3df:305; reference TX same family;
c5eb3c58 table tonight).

---

## UNBLOCK PATH (unchanged in kind, now with this survey's kit)

1. **A human names the unit and its location** (or connects it to a
   fleet host): cards `t_a2f7f281` (identify), `t_b09424f1` family,
   `t_ffc911f6` (nameplate) are the standing resultless blockers.
2. **One caliper site visit** (protocol per `t_f2b50f53`/`t_03954030`):
   walk the bulkhead with this report's record set F1-F5, measure each
   port's thread OD / thread pitch / hex AF / hole ID / panel thickness,
   apply the § identification kit and fe700201's fit-decision table.
3. **Check every located port for filter construction** (§ STEP 5 loud
   flag) before allowing it into the RF path.
4. **Custodian gate**: any drilling goes through Felix (4b3ec9b5).
5. Replace every UNVERIFIED planning input (USB-C overmold width,
   coax bend radius R=12.7 mm nominal, SMA dims) with measured values;
   re-dispatch this card.

Parallel-sibling status, not awaited (per fleet precedent): the
warm-side dewpoint worker (02:50) and BOM-compile worker (02:57) were
still running at 03:08; the instrument-ports worker (03:00) committed
`c5eb3c58` at 03:03:02+02:00 (no RF instrument exists — consistent with
every census claim here). The BOM-compile sibling consumes this output;
the GAP table above is structured for direct merge.

---

## SOURCE SUMMARY

| Claim | Source | Confidence |
|---|---|---|
| No chamber located on any record/host; all locate/identify cards resultless | fleet_queue_state.json re-read 03:07:57+02:00 (708 tasks, 0 non-empty result fields); 24eb918c; ec80c11e; 766ac96d; fe700201 | HIGH (fresh programmatic re-read + 4 committed reports) |
| This is first worker output for t_923c4eca | claims map (06:35:17 Sep 14 resultless, 02:58:59 Sep 15); session-DB search: only prior hit is a card-ID lookup in the fe700201 session | HIGH |
| No camera device on host | `/dev/video*` absent, `/sys/class/video4linux` absent, v4l2-ctl not installed (fresh); 24eb918c | HIGH |
| Zero instrument-class devices / no usbtmc / no gpib / no RF coax on host | fresh lsusb, /dev nodes, lspci (§ STEP 1); c5eb3c58 tonight; 72f3aab9; c4be4400 | HIGH |
| DUT ttyACM0 currently = Pi Debugprobe (DUT absent) | /dev/serial/by-id fresh + fe700201 udevadm verification | HIGH |
| Primary path is OTA decode-count; zero RF feedthrough parts needed | fork README d7ae93fa "Bench setup" table; `scan_edges()` at d7ae93fa ("counts decoded packets"); 55585471 § 3a | HIGH |
| Conducted-path buy list with quantities and lead times | 55585471 § 3b/4 (re-read this session, hash verified) | HIGH (as the standing BOM of record; MPNs are representative classes, labeled so at source) |
| SMA bulkhead pattern: 6.5 mm panel hole, O-ring sealing, "fully waterproof" | enclosure/README_big.md:20-23 verbatim (read this session) | HIGH (project's own documented pattern) |
| PG7 gland convention, AS568 2 mm O-ring cord "Nitrile or silicone" | enclosure/README.md:27/29/72/74 verbatim | HIGH |
| Thread/hex identification kit values (SMA 1/4"-36 UNS, 7.94 mm AF; N 5/8"-24; TNC 7/16"-28; BNC 2-lug) | industry-standard connector families — **class-typical, UNVERIFIED on host** (no vendor datasheet on host; no outbound fetch per standing constraint) | MEDIUM (used only as an identification aid, not as procurement spec) |
| SMA hex nut needs ≥9.5-10 mm bore if connector passes; RG316 min bore 3.0 mm; USB-C min bore 6.0 mm | fe700201 § 3c/3d computed tables | HIGH (computed, cited) |
| Gasket-crossing cable = certain leak path; frost jacking certain | fe700201 § 4; 65c9c3df Magnus physics | HIGH |
| Filtered OEM feedthroughs exist and are the top conducted-path corruption risk | engineering knowledge of EMC-chamber hardware; **no instance on record** — flagged as a check, not a claim about this chamber | MEDIUM (flag, not finding) |
| Chamber custodian: Felix, MEDIUM, gates drilling | 4b3ec9b5 (carried in fe700201) | MEDIUM |
| Parallel siblings' status (dewpoint/BOM running; instrument-ports committed c5eb3c58) | `ps aux` fresh; `git log --since 02:45` fresh | HIGH |

## NOTHING FABRICATED

No physical measurement, photograph, or connector identification was
invented. No feedthrough was simulated. Every physical field is
UNKNOWN with its reason; every on-record value carries its citation.
No functional test is reported as performed. The fleet state was read
locally (established permitted pattern); no outbound probe was made.