# RF coax cable inventory — every distinct cable in the RF run

Card: `meshcore:t_9cfb7abd` — "Identify every distinct coax cable in the RF run"
Board: meshcore · Worker: worker-admin (run 2105) · Date: 2026-10-17
Host: `c03rad0r-DQ05proplus` · Workspace: `/home/c03rad0r/worktrees/t_e1408991` (scratch, not a git repo)

This is the DOWNSTREAM consumer of this card: cards `t_758163ec` ("for every part
number in the inventory") and `t_c17edc0d` ("for every connector style observed in
the cable inventory") are unbound until an inventory exists. This file is that
inventory.

---

## 0. VERDICT

**The RF run contains 2 distinct coax cables, and neither exists physically.**

| | |
|---|---|
| Distinct coax cables in the RF run | **2** — `C-RF-INT-1` (interior, 0.15 m) and `C-RF-EXT-1` (exterior, 0.50 m) |
| Cables with a **readable printed marking** to transcribe | **0** — no cable exists on this host or on any record, so no jacket print exists to read |
| Cables whose connector style was **observed** | **0** — no connector exists to observe |
| Full printed P/N strings of the form the card gives as examples (`Belden 9913F7`, `RG-214/U`, `LMR-400`) present anywhere in project records | **0** — searched by string, zero files |
| Count basis | the procurement plan / frozen routing spec, **not** an observation of a physical run |

The card's acceptance criterion — "every distinct cable appears exactly once; any
illegible or unreadable marking is listed as UNRESOLVED with a precise statement of
what is needed to resolve it" — is met by §2 (the inventory) plus §3 (the UNRESOLVED
register). No marking string was invented, normalized, or guessed; no appearance was
guessed; the one class string that does exist on record (`RG316`) is labelled as a
**planned cable class**, not as a transcribed jacket marking.

---

## 1. Step 1 — evidence attempt (fresh, this session)

The card's step 1 offers two routes: inspect the run directly, or obtain photos from
the operator. Both are closed, with fresh evidence recorded this session.

| Check (fresh, 2026-10-17) | Result | Consequence |
|---|---|---|
| `lsusb` | root hubs ×4, Realtek BT radio `0bda:b850`, Lexar ES4 `21c4:0004`, Zoran USB Audio/HID `0573:1573` | **zero instrument-class devices, zero coax-connected** |
| `/dev/serial/by-id/` | **absent** | the planned DUT console cable (`C-SER-1`) is not attached either; no console path to any RF instrument |
| `/dev/usbtmc*`, `/dev/gpib*` | absent | no instrument bus to terminate a coax into |
| `/dev/video*`, `/sys/class/video4linux`, `v4l2-ctl` | all absent / not installed | **no camera on this host — a photo of any jacket print cannot be taken here** |
| Fleet-wide result search — all **115** board DBs, every card `result` field | 3 result-bearing cards mention coax at all (`t_194fe19c`, `t_466fdfc5`, `t_68801742`) — all three are PTFE-coax *failure-mode research*, none an inventory | no sibling card anywhere on the fleet has produced a cable inventory or a marking transcription |
| meshcore attachment census (22 attachments) | content types: 15 markdown, 3 null, 2 csv, 1 plain, 1 python — **0 image types** | **no board anywhere holds a photo of a cable, connector, or jacket print** |
| Image sweep, home dirs (bounded depth, this session) | zero photographs of coax. The only large image corpus on the host is `scratch-av1a-s1/ocr/` — 730 frames extracted from a video, not cable photos | no photographic evidence exists on the host |
| String grep, meshcore tree, for the card's own example markings: `9913F7`, `LMR-400`, `RG-214` | **0 files each** | the card's example P/Ns are illustrative only; none is on record |
| String grep, same tree: `RG178`/`RG-178`, `LMR-100`, `RG316` | 8 files / 1 file / 27 files | the only coax classes that appear anywhere on record are RG316 (planned) and RG-178 / LMR-100 (considered-and-rejected alternatives) |
| Prior bench reports on this exact question | `bench/coax-cable-inventory/REPORT.md` (commit `31d3f26e`, 2026-09-15) and `bench/coax-bundle-dimensions/REPORT.md` — both return a **NO-COAX** verdict from fresh hardware censuses | the negative is independently corroborated, not a single-run artefact |
| Operator photos / labels | **not solicitable** — this is a headless dispatched worker with no live user, and the campaign's standing constraint forbids outbound contact | the photo route is closed by permission, not by choice |

**Three independent, individually sufficient reasons the physical path is closed:**
no cable exists to inspect; no camera exists to photograph one; the DUT is not
attached. Each was re-verified this session rather than inherited from the prior
report.

### 1.1 Why the run's composition is a PLAN, not an observation

The primary measurement protocol is over-the-air decode-counting — the DUT sits in
the chamber with its own soldered wire dipole and the reference TX outside has its
own antenna. The plan's own summary of RF parts required is **ZERO**
(`bench/rf-feedthrough-bom/REPORT.md` §3a; fork README `d7ae93fa`). Coax appears only
in the **optional conducted path** (variant B), which is a procurement plan: two
RG316 SMA-m/m assemblies plus one SMA bulkhead feedthrough, all MPN TBD, all
MUST-PROCURE. That plan is what fixes the count of 2.

---

## 2. DELIVERABLE — numbered inventory

Dedup key is the printed part number, per the card. **No printed part number was
readable on any cable, so dedup-by-marking is not exercisable.** The two items below
are therefore kept distinct by (a) their frozen cable ID (`bench/routing-freeze`
§5) and (b) their planned class + length, which differ (0.15 m vs 0.50 m) — they are
two distinct planned instances, not one item counted twice. If the procured
assemblies turn out to carry printed markings, re-dedup by marking string: both are
currently expected to be the same class, so a shared marking would **not** collapse
them into one item — they remain two separate physical cables in two separate run
segments.

### Item 1 — `C-RF-INT-1`

| Field | Value |
|---|---|
| **Full P/N or marking string** | **NO PRINTED MARKING EXISTS — cable does not exist.** Nothing was transcribed. Planned cable class as written on record: `RG316` (a class, not a jacket print). |
| **Marking status** | **UNRESOLVED** — see U1 in §3 |
| **Observed connector style(s)** | **NONE OBSERVED — no connector exists to observe.** Planned (not observed): SMA plug, male pin, **straight**, standard polarity, 50 Ω, both ends |
| **Location / length hint** | Run segment **interior** of chamber: DUT `J1` → 15 mm tie-off → tie `T1` → bend `B1` (R ≥ 25 mm) → 50 mm service loop → SMA bulkhead feedthrough. Planned length **0.15 m** |
| **Evidence reference** | `bench/coax-cable-inventory/REPORT.md` (commit `31d3f26e`, §2a/§3 "Cable 1"); `bench/routing-freeze/REPORT.md` §5 (frozen ID `C-RF-INT-1`); `bench/connector-adapter-bom/REPORT.md` line B1; `bench/rf-feedthrough-bom/REPORT.md` line 171 |

### Item 2 — `C-RF-EXT-1`

| Field | Value |
|---|---|
| **Full P/N or marking string** | **NO PRINTED MARKING EXISTS — cable does not exist.** Planned cable class as written on record: `RG316` |
| **Marking status** | **UNRESOLVED** — see U2 in §3 |
| **Observed connector style(s)** | **NONE OBSERVED.** Planned (not observed): SMA plug, male pin, **straight**, standard polarity, 50 Ω, both ends |
| **Location / length hint** | Run segment **exterior** of chamber: bulkhead feedthrough → 15 mm standoff → tie `T3` → drape → 100 mm exterior loop → reference-TX `J1`. Planned length **0.50 m** |
| **Evidence reference** | `bench/coax-cable-inventory/REPORT.md` (§2a/§3 "Cable 2"); `bench/routing-freeze/REPORT.md` §5 (frozen ID `C-RF-EXT-1`); `bench/connector-adapter-bom/REPORT.md` line B4; `bench/rf-feedthrough-bom/REPORT.md` line 169 |

### 2.1 Boundary — things that are NOT items in this inventory

Recorded so the run's inventory is not inflated by lookalikes, and so downstream
desks do not research the wrong part.

| Object | Why it is not an item here | Source |
|---|---|---|
| `C-SER-1` — USB-C serial, DUT console (variant A's primary chamber crossing) | **not coax** — USB-C serial cable | `bench/routing-freeze` §5 |
| `C-SER-2` — USB-C serial, reference-TX console | **not coax**, and never crosses the boundary | `bench/routing-freeze` §5 |
| SuperMini `U.FL`-to-SMA pigtail (+ 3 dBi SMA antenna) | **is a coax-class pigtail but is not in the RF run** — it is the ESP32-C3 SuperMini's WiFi/BLE accessory, outside the LoRa measurement path entirely. MPN not recorded; physical presence on the c3-a unit UNVERIFIED (clone batches vary). If it is ever brought into scope it becomes a **third distinct item** | `esp32c3-mini-v1.json` connectors block; `bench/dut-rf-ports/REPORT.md` §4/§5 |
| SMA edge-launch `J1`/`J2` on the `hub_board_f33` variant | **a board-mounted connector, not a cable.** Also a *different board* from the DUT | `hub_board_f33.kicad_pcb:165-179`; `bench/dut-rf-ports/REPORT.md` §5 |
| SMA bulkhead feedthrough | **a panel connector, not a cable** (it is the wall penetration the two cables mate to) | `bench/connector-adapter-bom` B2 |
| `RG-178`, `LMR-100` | **rejected alternatives, never on the run** — RG-178 rejected on record for higher loss; LMR-100 never on any record | `bench/rf-connector-geometry/REPORT.md` §(cable standard) |
| `RG-59` / `RG-6` (75 Ω video coax) | **not on the run**; flagged in the BOM only as a substitution hazard to reject at order time | `bench/connector-adapter-bom/REPORT.md` H1 |

---

## 3. UNRESOLVED register (what is needed, per cable, precisely)

Each entry states what a resolver must supply. These are the only outstanding
items; nothing else in this inventory is open.

| ID | Unresolved | Exactly what is needed to resolve it |
|---|---|---|
| **U1** | Full printed part number / marking string on **Item 1 (`C-RF-INT-1`)** | A close-up photo of the **jacket print on cable 1**, anywhere along its length with the print string in focus; a frame taken within **20 cm of either connector end** is acceptable. If the procured assembly arrives unmarked, photograph the **packaging label** (which carries the vendor P/N) instead and say so. |
| **U2** | Full printed part number / marking string on **Item 2 (`C-RF-EXT-1`)** | Same as U1, for **cable 2** — one focused frame of the jacket print, or the packaging label if the jacket is unmarked. |
| **U3** | **Observed** connector style at each end (both items) | Four photos — **each of the four connector ends** (cable 1 end A and B, cable 2 end A and B) — framed to show series (SMA vs 3.5 mm vs N vs TNC), gender (male pin vs female socket), and straight vs right-angle. The current table holds the *planned* spec only; observation is what the card asks for. |
| **U4** | The **count** of cables actually in the run | One photo of the **whole run/bundle as routed** (interior leg and exterior leg), so the count can be confirmed as 2 or corrected. Nothing on record states an observed cable count; 2 is the plan. |
| **U5** | Any **unmarked** cable's physical appearance | For any cable found unmarked: jacket **colour**, jacket **OD measured with calipers** (0.01 mm least count), and the **packaging part number** if available. Appearance values must be observed, not taken from the industry-typical reference values currently carried in `bench/coax-cable-inventory/REPORT.md`. |
| **U6** | Whether the SuperMini U.FL pigtail is present on the specific c3-a unit | If the run's scope is later widened to include it: a photo of the c3-a board's U.FL connector and its pigtail jacket print. Until then it stays out of scope per §2.1. |

**Note on the two downstream cards.** `t_758163ec` and `t_c17edc0d` both key their
work on "every P/N in the inventory" / "every connector style observed in the
inventory". As of this file there are **zero readable part numbers and zero observed
connector styles** — only a planned class (`RG316`) and a planned connector spec
(SMA plug, straight, standard polarity, 50 Ω). Those cards cannot produce a
marking-anchored table until U1–U4 are resolved. They can still proceed on the
*planned class* by researching `RG316` + `SMA` and labelling every number
PLANNED-CLASS rather than AS-BUILT; that substitution must be visible in their
output, not silent.

**Source conflict flagged (do not silently resolve).** `bench/instrument-rf-connectors`
§(table) states the reference TX's connector is "Female jack on the reference TX board
**(same as DUT)**", while `bench/dut-rf-ports` §VERDICT establishes the DUT has **no
RF connector at all** (soldered wire dipoles). The two committed reports disagree
about the DUT side. This inventory does not pick a winner: for the coax itself the
only thing that matters is that the cable is planned to present **male SMA plugs at
both ends**, which both reports agree on. Downstream connector work (`t_c17edc0d`)
should treat the reference-TX board's connector gender as UNVERIFIED-for-that-board
and note the conflict.

---

## 4. Sources

| # | Source | What it establishes |
|---|---|---|
| S1 | `bench/coax-cable-inventory/REPORT.md`, commit `31d3f26e` (2026-09-15) | prior cable-identification pass; NO-COAX verdict; per-cable UNMARKED flags |
| S2 | `bench/coax-bundle-dimensions/REPORT.md` | independent NO-COAX verdict on the same question |
| S3 | `bench/routing-freeze/REPORT.md` §5 | the **frozen cable ID list** — `C-RF-INT-1`, `C-RF-EXT-1`, `C-SER-1`, `C-SER-2` — with class, status, crossing, routing rule |
| S4 | `bench/connector-adapter-bom/REPORT.md` lines B1/B2/B4/B8, H1 | planned cable spec (RG316, SMA-m/m, 0.15 m / 0.50 m), feedthrough, and the 75 Ω substitution hazard |
| S5 | `bench/rf-feedthrough-bom/REPORT.md` lines 169–171 | procurement BOM: SMA m/m patch 0.15 m and 0.5 m, RG316 or RG178, representative Amphenol ACX-1169-class |
| S6 | `bench/rf-connector-geometry/REPORT.md` | RG-316 assumed standard; RG-178 and LMR-100 disposition |
| S7 | `bench/dut-rf-ports/REPORT.md` §4/§5 | DUT has no RF connector at all (soldered wire dipoles); U.FL pigtail is a WiFi/BLE accessory; the SMA edge-launch belongs to a different board |
| S8 | `bench/instrument-rf-connectors/REPORT.md` lines 87–98, 141 | reference-TX side: female jack; cable presents male SMA plugs both ends; SMA bulkhead jack-jack |
| S9 | fresh host census, this session (2026-10-17) | `lsusb`; `/dev/serial/by-id` absent; `/dev/usbtmc*`, `/dev/gpib*`, `/dev/video*`, `/sys/class/video4linux` absent; `v4l2-ctl` not installed |
| S10 | fleet-wide result sweep, this session — all 115 board DBs | only 3 result-bearing coax cards fleet-wide, all failure-mode research; no inventory anywhere |
| S11 | meshcore `task_attachments` census, this session | 22 attachments, **0 image types** — no cable photo on any board |

All `bench/**` sources above are committed files in `repos/meshcore` (branch `main`)
and were re-read this session.

---

## 5. Nothing fabricated

No cable was inspected, because none exists on this host or on any record. No
photograph was taken or claimed — no camera exists on the host. No part number was
invented: every P/N cell says the marking does not exist, and the one class string
present (`RG316`) is labelled a **planned class**, not a jacket print. No connector
style was recorded as *observed* — the SMA spec is labelled PLANNED throughout. No
colour, diameter, or length was guessed as an observation. No outbound contact or
network fetch was made. Every negative is backed by a command run or a committed
file read in this session, and the UNRESOLVED register states, per cable, the exact
photograph or measurement that would close it.
