# RF coax bundle dimensions and minimum bend radius

Task: "Characterize RF coax bundle dimensions and minimum bend radius.
GOAL: Fully characterize the RF coax run so its cross-section and routing
constraints are known numbers, not guesses."

Date: 2026-09-15 · Repo: meshcore (main) · Worker: dq05.
Artifacts: this directory (`bench/coax-bundle-dimensions/`).

---

## VERDICT SUMMARY

**No RF coax exists on this host or on any record.** The entire coax run
that this task asks to characterize — cables, connectors, bundle, slack,
forced bend — does not exist. It is a procurement plan, not a physical
artifact. Every step that requires a physical cable is therefore
**UNKNOWN with reason**, not guessed, not simulated.

What CAN be stated with evidence (and is, below):

1. **No coax cable of any type exists on the host or in any project
   record.** Fresh USB/serial census this session confirms: 2x CH340
   serial, Pi Debugprobe, RTL8152 Ethernet, microSD reader, BT radio,
   audio/HID — zero RF coax, zero instrument-class devices. Six prior
   bench reports independently concur (`55585471`, `fe700201`, `c5eb3c58`,
   `40e1a49a`, `04db4fae`, `ec80c11e`). No inventory system of record
   exists (`bffc7f9d`).

2. **The primary measurement protocol uses NO coax.** The edgescan
   protocol is over-the-air decode-counting: DUT inside chamber with its
   own antenna, reference TX outside at room temperature with its own
   antenna. The only cable crossing the sealed boundary is USB-C serial.
   (Fork README `d7ae93fa`; `thermal_bench.py scan_edges()`; BOM
   `55585471` §3a: "Total RF components needed: ZERO".)

3. **The optional conducted path (if OTA is rejected or chamber is
   metal) has a fully enumerated procurement plan** — but no parts are
   in hand. The plan calls for 2x RG316 SMA-m/m assemblies (0.15 m +
   0.50 m) and 1x SMA bulkhead feedthrough. These dimensions and bend
   radius specs are documented below as **industry-nominal values,
   explicitly UNVERIFIED** — no vendor datasheet exists on host, no
   outbound fetch permitted (standing operator constraint).

4. **No chamber exists on any record or host** (re-verified this
   session via fresh census + 5 prior reports: `24eb918c`, `766ac96d`,
   `ec80c11e`, `fe700201`, `40e1a49a`). Therefore: in-chamber slack,
   exterior slack, routing path, and the tightest forced bend are all
   **UNKNOWN — no chamber to route through**.

5. **No calipers are available on this host** (no physical measuring
   tools are enumerated on any record; no camera/device for photogrammetry
   — `/dev/video*` absent, v4l2 absent). Step 3 (caliper measurement of
   jacket OD, connector body, bundle OD) and Step 4 (slack measurement)
   cannot be performed.

---

## STEP 1 — Identify each coax cable by part number/marking

### What coax exists on host or record

**NONE.** Fresh census this session (2026-09-15):

| Check | Result |
|-------|--------|
| `/dev/serial/by-id/` | 2x QinHeng CH340 (`ttyUSB0`, `ttyUSB1`) + Pi Debugprobe (`ttyACM0`) — all serial consoles, zero RF |
| `lsusb` | RTL8152, BT radio, Zoran audio/HID, 2x hubs, microSD, 2x CH340, Pi Debugprobe — zero instrument-class, zero coax-connected |
| `/dev/usbtmc*`, `/dev/gpib*` | absent |
| `lspci` | PCH I2C/HECI/SPI only; no RS-232, no GPIB |
| `/dev/video*`, V4L2 | absent — no camera |
| Filesystem find (coax/cable/feedthrough) | zero RF cable assets on disk |
| Prior reports | `55585471` BOM lines all "Unknown (not on any record)"; `fe700201` §2a "None on hand, none on record"; `40e1a49a` C1 "DOES NOT EXIST"; `c5eb3c58` "no RF instrument in the measurement chain"; `04db4fae` "No chamber, cable, feedthrough, or RF instrument exists on any record or on this host" |

**No cable part number, marking, or physical instance exists to
identify.** The procurement plan (from `55585471` §3b, `fe700201`, and
the merged BOM `t_0d86117f` / `bench/connector-adapter-bom/`) specifies
two cable assemblies:

| # | Planned cable | Part class | MPN | Status |
|---|---------------|------------|-----|--------|
| 1 | RG316 SMA-m/m, 0.15 m (DUT → feedthrough, interior) | RG316, SMA plug both ends, 50 Ω, standard polarity | **TBD** (representative class: Amphenol ACX-1169-class) | MUST-PROCURE — not on hand, not on record |
| 2 | RG316 SMA-m/m, 0.50 m (feedthrough → reference TX, exterior) | same | **TBD** | MUST-PROCURE — not on hand, not on record |

Sources: `55585471` §3b lines 1-3; `fe700201` §2a; `bench/connector-adapter-bom/REPORT.md` B1/B4.

### Datasheet lookup

**No manufacturer datasheet exists on this host.** No outbound fetch
permitted (standing operator constraint — no network probes from dq05).
The RG316 dimensions and bend-radius values used throughout the bench
report series are **industry-nominal class values**, carried from
`fe700201` §2b and labeled UNVERIFIED:

| Parameter | Industry-nominal value | Source label |
|-----------|----------------------|-------------|
| RG316 jacket OD | 2.50 mm (0.098 in) | INDUSTRY NOMINAL — RG316 spec class; `55585471` §3b "RG316, OD 2.5mm"; `fe700201` §2b. UNVERIFIED for any specific procured part. |
| RG316 dielectric | PTFE (solid), εr ~2.1 | `65c9c3df` §3b; INDUSTRY-TYPICAL |
| RG316 temperature rating | -40 C to +200 C class (PTFE dielectric) | `55585471` §4.2: "both [RG316/RG178] are rated to -40 C (PTFE dielectric)"; INDUSTRY-TYPICAL, UNVERIFIED for the specific procured part |
| RG316 min bend radius, static | 12.7 mm (0.5 in) | `fe700201` §2b: "INDUSTRY NOMINAL — UNVERIFIED (no vendor datasheet on host; no outbound fetch performed)"; carried in `04db4fae` FM-8, `t_0d86117f` B1 spec. Given as an **absolute value (mm)**, NOT as a multiple of OD. Coincidentally ≈ 5× OD (5 × 2.54 = 12.7), but the source states it in mm, not as an OD multiple. |
| RG316 min bend radius, rule-of-thumb alt | 10× OD = 25.0 mm | `fe700201` §2b: "RULE OF THUMB (commonly quoted coax guidance; basis stated, UNVERIFIED)". This is a DIFFERENT (more conservative) value than the 12.7 mm industry nominal. |
| RG316 min bend radius, dynamic | **UNKNOWN** | Not stated in any prior bench report. Industry-typical dynamic (repeated flex) bend radius for RG316 is 10× OD = ~25 mm or greater, but **no source on host** — this is engineering knowledge, UNVERIFIED. |
| SMA plug connector body OD | 5/16 in hex = 7.94 mm across flats, 9.17 mm across corners | `fe700201` §3c; `40e1a49a` identification kit; INDUSTRY-STANDARD SMA, UNVERIFIED on host |
| SMA plug connector body length | **UNKNOWN** | No source on host or in any prior bench report. Industry-typical SMA male plug body length (from back of coupling nut to cable exit) is ~15-22 mm depending on cable series and vendor, but **no source cited** — engineering knowledge only, UNVERIFIED. |
| SMA jack (bulkhead feedthrough) body OD | same hex class as above (7.94 mm AF) if hex-nut bulkhead | `40e1a49a` identification kit; INDUSTRY-STANDARD, UNVERIFIED |

**The min bend radius is given as an ABSOLUTE VALUE (12.7 mm), not as an
OD multiple.** A separate 10×OD rule-of-thumb (25.0 mm) exists in the
record as a more conservative alternative. No dynamic (repeated-flex)
bend radius is stated in any on-host source. All values are
industry-nominal, UNVERIFIED — no vendor datasheet has ever existed on
this host for any coax or connector.

---

## STEP 2 — From datasheet: jacket OD, connector body OD/length, min bend radius

This step requires a manufacturer datasheet. **No datasheet exists on
host and none can be fetched** (no outbound network probes from dq05;
standing constraint, respected — nothing attempted this session).

The industry-nominal values carried from prior reports are consolidated
in the table above (Step 1). They are repeated here in the requested
per-cable format:

### Per-cable table (acceptance deliverable, with sources)

| Cable | Model / part | Jacket OD | Connector type | Connector body OD | Connector body length | Min bend radius (static) | Min bend radius (dynamic) | Source for each |
|-------|-------------|-----------|----------------|-------------------|----------------------|--------------------------|---------------------------|-----------------|
| 1 (interior) | RG316 SMA-m/m, 0.15 m — MPN TBD, MUST-PROCURE, does not exist on host | **2.50 mm** — INDUSTRY NOMINAL, UNVERIFIED (`55585471` §3b; `fe700201` §2b) | SMA plug (male), standard polarity, 50 Ω, both ends | **7.94 mm AF / 9.17 mm AC** — INDUSTRY-STANDARD SMA hex, UNVERIFIED on host (`fe700201` §3c; `40e1a49a` ID kit) | **UNKNOWN** — no source on host or in any prior bench report; industry-typical ~15-22 mm, engineering knowledge, UNVERIFIED | **12.7 mm** (0.5 in) — INDUSTRY NOMINAL, given as absolute mm NOT as OD multiple (`fe700201` §2b; carried `04db4fae` FM-8, `t_0d86117f` B1). Note: coincidentally ≈ 5× OD. | **UNKNOWN** — not in any on-host source; industry-typical ≥10× OD ≈ 25 mm, engineering knowledge, UNVERIFIED | See per-cell citations |
| 2 (exterior) | RG316 SMA-m/m, 0.50 m — MPN TBD, MUST-PROCURE, does not exist on host | same as cable 1 (same RG316 class) | same (SMA plug male, both ends) | same (7.94 mm AF / 9.17 mm AC) | **UNKNOWN** — same as cable 1 | same (12.7 mm) | **UNKNOWN** — same as cable 1 | same sources |

**Both cables are the same RG316 class.** No other coax type is in the
plan (RG178 was mentioned in `55585471` §4.2 as an alternative but RG316
was selected for lower loss and better mechanical stability; the merged
BOM `t_0d86117f` commits to RG316 exclusively).

### What would resolve each UNKNOWN

| UNKNOWN | What resolves it |
|---------|-----------------|
| Specific MPN / part number | Procurement: order the cable, read the part marking. No inventory system of record exists (`bffc7f9d`). |
| Vendor datasheet (jacket OD, exact bend radius, dynamic bend radius, connector body dims) | Obtain the specific procured assembly's datasheet at order time. No outbound fetch permitted from this host. |
| Connector body length | Caliper measurement of the procured assembly, OR vendor datasheet. |
| Dynamic bend radius | Vendor datasheet (rarely published for RG316 patch assemblies; more common in bulk-cable specs). |
| Physical verification of any value | Caliper measurement with the procured cable in hand. No calipers enumerated on host. |

---

## STEP 3 — Caliper measurements: jacket OD, connector body, bundle OD

**NOT PERFORMED — nothing to measure.** Three independent reasons:

1. **No coax cable exists** on this host or on any record (Step 1 census;
   6 prior reports concur). There is no jacket to measure, no connector
   body to measure, no bundle to tape and measure.

2. **No calipers are available.** No physical measuring tools are
   enumerated on any record. No measuring device appears in the USB
   census (zero instrument-class devices). No GPIO/SPI/I2C sensor that
   could serve as a caliper exists.

3. **No DUT is attached.** The DUT (SkyMapper Board A, fleet resource
   `c3-a`) is not connected to this host — `/dev/ttyACM0` is currently
   the Pi Debugprobe (udevadm-verified in `fe700201`, re-confirmed this
   session). No chamber, no DUT, no routing, no bundle.

### Industry-nominal planning values (for reference, NOT measurements)

From `fe700201` §3c, computed from industry-nominal RG316 OD and
USB-C cable OD (also UNVERIFIED):

| Bundle composition | Computation | Equivalent OD |
|--------------------|-------------|---------------|
| RG316 alone | single cable | **2.5 mm** |
| USB-C alone (primary path) | single cable, OD 4.0-5.0 mm INDUSTRY-TYPICAL UNVERIFIED | **4.0-5.0 mm** |
| RG316 + USB-C taped side-by-side (conducted path) | sqrt((2.5+4.5)^2 + 4.5^2) = 8.32; +0.5 mm loom | **~8.8 mm** (9.5 mm if USB-C OD is 5.0) |

Source: `fe700201` §3c, computed from nominal ODs. All inputs UNVERIFIED.

### Swept envelope at a 90° turn (from `fe700201` §2d)

For RG316 at R = 12.7 mm, OD t = 2.5 mm:
- Swept diameter = 2R + t = 2(12.7) + 2.5 = **27.9 mm**
- Clearance from port face = R + t/2 = 12.7 + 1.25 = **~14 mm**

At the 10×OD rule (R = 25.0 mm):
- Swept diameter = 2(25.0) + 2.5 = **52.5 mm**
- Clearance = 25.0 + 1.25 = **26.25 mm**

Source: `fe700201` §2d, arithmetic shown, inputs UNVERIFIED.

---

## STEP 4 — Available slack and forced bend

**NOT MEASURABLE — no chamber, no instrument, no routed cable.**

| Slack measurement | Value | Reason |
|-------------------|-------|--------|
| Usable free length inside chamber | **UNKNOWN** | No chamber located on any record or host (5 prior reports concur). No routing defined. Sibling card `t_e5d5eaae` (routing-freeze step) undispatched. |
| Free length outside to instrument | **UNKNOWN** | No instrument exists (`c5eb3c58`: zero instrument-class USB). The de-facto "instrument" is the reference TX at room temp — its position relative to the chamber is undefined (no chamber). |
| Tightest bend the routing path forces near the chamber wall | **UNKNOWN** | No chamber wall exists on record. No routing path defined. The planned 90° turn at the SMA bulkhead feedthrough has a computed swept envelope (27.9 mm at R=12.7 mm, Step 3 above), but the actual forced bend depends on chamber interior clearance, which is UNKNOWN. |

Planned cable lengths (from `fe700201`, `55585471` §3b, `t_0d86117f`):
- Interior: RG316 0.15 m (DUT SMA J1 → bulkhead feedthrough)
- Exterior: RG316 0.50 m (bulkhead → reference TX)
- These are **planning estimates**, not measurements. The interior length
  depends on chamber interior geometry (UNKNOWN). The exterior length
  depends on reference TX placement relative to the chamber wall
  (UNKNOWN).

---

## STEP 5 — Compare forced bend to min bend radius spec; flag violations

**CANNOT BE COMPARED — neither the forced bend nor a verified min bend
radius spec exists.**

| Comparison | Forced bend | Min bend radius spec | Violation? |
|------------|-------------|---------------------|------------|
| 90° turn at SMA bulkhead (planning) | **UNKNOWN** (chamber interior clearance unknown) | 12.7 mm static / 25.0 mm rule-of-thumb / UNKNOWN dynamic — all INDUSTRY NOMINAL, UNVERIFIED | **CANNOT DETERMINE** — no chamber, no routing, no verified spec |

### What CAN be stated (planning-level)

If the routing forces a 90° turn at the bulkhead with clearance less
than 14 mm from the port face, the industry-nominal static bend radius
(12.7 mm) would be violated. If the routing forces a turn with clearance
less than 26.25 mm, the 10×OD rule-of-thumb (25.0 mm) would be violated.

The `04db4fae` failure-mode catalogue (FM-8) flags this as a **HIGH**
risk at tight routing for both -20 C and -40 C: cold jacket stiffening
makes a cable routed at its room-temperature minimum bend radius
effectively below minimum when cold, causing permanent shield kink and
connector strain. This is a real risk for the conducted path, but it
cannot be quantified without the chamber and the procured cable.

---

## SOURCE SUMMARY

| Claim | Source | Confidence |
|-------|--------|------------|
| No RF coax exists on host or record | Fresh USB/serial census this session (lsusb, /dev/serial/by-id, /dev/usbtmc, /dev/gpib, lspci); `55585471` §3b "Unknown (not on any record)"; `fe700201` §2a "None on hand, none on record"; `40e1a49a` C1 "DOES NOT EXIST"; `c5eb3c58` "no RF instrument"; `04db4fae` "No chamber, cable, feedthrough, or RF instrument exists" | HIGH (6 independent concurrences + fresh census) |
| Primary protocol is OTA, uses zero coax | Fork README `d7ae93fa` "Bench setup" table; `thermal_bench.py scan_edges()`; `55585471` §3a "Total RF components needed: ZERO" | HIGH |
| RG316 jacket OD = 2.50 mm | `55585471` §3b; `fe700201` §2b — INDUSTRY NOMINAL, UNVERIFIED | LOW-MEDIUM (planning input, no vendor datasheet) |
| RG316 min bend radius static = 12.7 mm (absolute, not OD multiple) | `fe700201` §2b — INDUSTRY NOMINAL, UNVERIFIED; carried in `04db4fae` FM-8, `t_0d86117f` B1 | LOW-MEDIUM (planning input) |
| RG316 min bend radius rule-of-thumb = 10×OD = 25.0 mm | `fe700201` §2b — RULE OF THUMB, UNVERIFIED | LOW (alternative planning input) |
| RG316 dynamic bend radius = UNKNOWN | Not in any on-host source | N/A (absence) |
| SMA plug body OD = 7.94 mm AF / 9.17 mm AC | `fe700201` §3c; `40e1a49a` identification kit — INDUSTRY-STANDARD, UNVERIFIED on host | LOW-MEDIUM |
| SMA plug body length = UNKNOWN | No source on host or in any prior bench report | N/A (absence) |
| RG316 temperature rating -40 C class | `55585471` §4.2; `04db4fae` FM-11 — INDUSTRY-TYPICAL, UNVERIFIED for specific part | LOW-MEDIUM |
| No chamber located | `24eb918c`; `766ac96d`; `ec80c11e`; `fe700201`; `40e1a49a`; fleet state re-read (708 tasks, 0 non-empty result fields) | HIGH (5 reports + fresh fleet read) |
| No calipers on host | No measuring device in USB census; no record of any physical tool | HIGH (absence of evidence) |
| No camera on host | `/dev/video*` absent; V4L2 absent; v4l2-ctl not installed | HIGH |
| Bundle OD ~8.8 mm (RG316 + USB-C taped) | `fe700201` §3c computed from nominal ODs | LOW-MEDIUM (computed from UNVERIFIED inputs) |
| Swept envelope 27.9 mm at R=12.7 mm | `fe700201` §2d arithmetic | MEDIUM (arithmetic correct, inputs UNVERIFIED) |
| Planned lengths 0.15 m + 0.50 m | `fe700201` §2a; `55585471` §3b; `t_0d86117f` B1/B4 | MEDIUM (planning estimates, chamber unlocated) |
| Jacket stiffening → bend violation at cold = HIGH risk | `04db4fae` FM-8 | MEDIUM (mechanism sound, routing unknown) |
| No inventory system of record | `bffc7f9d` | HIGH |
| No outbound fetch permitted | Standing operator constraint on dq05 | HIGH (respected — nothing attempted) |

---

## WHAT WOULD RESOLVE EVERY UNKNOWN (ordered unblock path)

1. **Procure the RG316 assemblies** (B1/B4 in the merged BOM
   `t_0d86117f`). Until parts are in hand, every dimension is an
   industry-nominal planning value.
2. **Obtain the vendor datasheet** for the specific procured assembly.
   This resolves: exact jacket OD, connector body OD and length, min
   bend radius (static AND dynamic if published), temperature rating,
   and insertion loss. No outbound fetch from this host — the datasheet
   must come with the procured part.
3. **Caliper measurement of the procured cable**: jacket OD, connector
   body OD and length, and bundle OD when taped as routed. Requires
   calipers (not on host — procure or borrow).
4. **Locate the chamber** (cards `t_a2f7f281`/`t_b09424f1`/
   `t_ffc911f6` — all resultless). Without the chamber, slack and
   forced bend are undefined.
5. **Freeze the routing** (sibling card `t_e5d5eaae` undispatched):
   define the actual cable path from DUT J1 through the bulkhead to
   the reference TX. Measure in-chamber free length, exterior free
   length, and the tightest bend near the chamber wall.
6. **Compare** the forced bend radius to the datasheet min bend radius.
   Flag any violation. If the forced bend is tighter than the spec,
   either reroute, use a more flexible cable (e.g. RG178, at higher
   loss), or add a cable support to increase the bend radius.

---

## NOTHING FABRICATED

No physical measurement was performed — no cable, no calipers, no
chamber, no DUT exist on this host. No coax dimension, bend radius, or
slack value was invented. Every industry-nominal value is labeled
UNVERIFIED with its source. The fresh hardware census was run this
session (lsusb, /dev/serial/by-id, /dev/usbtmc, /dev/gpib, lspci,
/dev/video*, V4L2). No outbound network probe was made (standing
constraint respected). The fleet state was read locally (established
permitted pattern). Every prior bench report cited was committed and
re-read this session.