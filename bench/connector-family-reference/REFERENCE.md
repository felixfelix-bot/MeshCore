# RF connector-family reference sheet — diameter, thread, polarity

Task (fleet offload, meshcore): "Build connector-family reference sheet
(diameter, thread, polarity). GOAL: A reference sheet of candidate RF
connector families, so the classification step matches measurements
against sourced numbers instead of guessing. This task needs NO access
to the DUT and can run in parallel with the physical inspection."

Date: 2026-09-15 · Repo: meshcore (main) · Worker: dq05 (profile
worker-heavy) · Host: `c03rad0r-DQ05proplus`. Artifacts: this directory
(`bench/connector-family-reference/`): `REFERENCE.md` (this file),
`connector_family_calc.py`, `output.txt`.

---

## STATUS BANNER — READ FIRST

**Every number in this file is REFERENCE data. Nothing here is a
measurement of any physical part.** No DUT access occurred (the task
requires none); no connector, cable, or instrument exists on this host
(seven prior bench reports + census, see Provenance). Every value is
labeled with its provenance class:

| Label | Meaning |
|---|---|
| **COMMITTED** | verbatim value already committed in a bench report of this repo (exact path:line cited) |
| **COMPUTED** | pure arithmetic on a COMMITTED value or a definition (unit conversion, hex AC, 50-ohm air-line ratio) — reproduced in `connector_family_calc.py`, cross-checked, all 4 checks PASS, rerun byte-identical |
| **CLASS-TYPICAL, UNVERIFIED** | industry-standard family value from engineering knowledge; **approximate**; no vendor datasheet or standard text exists on this host and no outbound fetch is permitted (standing constraint, respected — nothing attempted) |

Standing constraints honored: no outbound fetch from this host (8 prior
bench reports concur, e.g. `rf-connector-geometry` STEP 3); no camera on
host; no DUT attached. This sheet therefore cites, per row: the committed
bench anchor where one exists (COMMITTED), the governing
standard/manufacturer-spec **class** (named, but its text is not on host —
CLASS-TYPICAL), and computed derivations (COMPUTED). No value is
presented as sourced from a document not on this host.

Consumers: the physical first-sight identification procedure
(`bench/chamber-rf-feedthroughs/REPORT.md:148-154`), the feedthrough
survey protocol (`bench/feedthrough-survey-protocol/PROTOCOL.md`), and
procurement receiving checks (`bench/connector-adapter-bom/REPORT.md`
hazard H2).

---

## MASTER TABLE — candidate RF connector families

Thread sizes are the **external coupling thread of the jack** (the
parent connector class; see the convention note under the table). OD =
body hex across-flats (AF) / across-corners (AC) where the family uses a
hex; body OD otherwise. All diameters mm (in where applicable); all
pitches TPI (mm/thread).

| # | Family | Body OD / hex | Thread major Ø | Pitch | Mating style | Standard polarity: who carries the pin | RP flip: what changes | Center contact Ø (pin / socket) | Dielectric, typical | Board-mount / bulkhead variants | Source (per row) | Provenance |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | **SMA** (SubMiniature version A) | hex AF 7.94 mm (5/16 in), AC 9.17 mm | 1/4"-36 UNS = 6.35 mm (0.250 in) | 36 TPI = 0.7056 mm/thread | threaded | **plug (pin); jack = socket** | see row 2 | pin ~1.2-1.3 mm (0.050 in class); socket ID ~1.3-1.4 mm class | PTFE, natural white/off-white | edge-launch PCB jack (committed: `hub_board_f33.kicad_pcb` J1/J2 `custom:SMA_Edge_Mount`); panel/bulkhead jack-jack jam-nut (committed BOM B2, Amphenol 132134-class); cable plug (committed BOM B1/B4); right-angle PCB jacks exist | thread/hex/AC COMMITTED `bench/chamber-rf-feedthroughs/REPORT.md:142-143` + `bench/rf-connector-geometry/REPORT.md:239-240`; 0.7056 mm COMMITTED `rf-connector-geometry:240`; PTFE COMMITTED as BOM required spec (`connector-adapter-bom` B2); pin Ø CLASS-TYPICAL; interface standard class: MIL-STD-348 / MIL-C-39012 (text not on host) | COMMITTED + CLASS-TYPICAL |
| 2 | **RP-SMA** (reverse-polarity SMA) | **identical** to SMA: AF 7.94 mm, AC 9.17 mm | **identical** 1/4"-36 UNS = 6.35 mm | **identical** 36 TPI = 0.7056 mm | threaded | n/a (this IS the flip) | **plug = socket; jack = pin.** Only the center contacts swap; outer thread/hex unchanged | plug: socket ID ~1.3 mm class; jack: pin ~1.2 mm class — same contact sizes as SMA | PTFE, natural white | bulkhead jack on WiFi routers (pin visible in threaded boss); cable plug (antenna side, socket recessed in nut) | committed hazard H2 verbatim: "RP-SMA plugs look nearly identical to standard SMA but have NO center pin (pin/socket swapped) — they will not mate" `bench/connector-adapter-bom/REPORT.md:130`; thread = row 1 COMMITTED | COMMITTED (thread) + COMMITTED (H2 behavior) |
| 3 | **3.5 mm** (precision) | hex AF 7.94 mm (5/16 in), AC 9.17 mm | 1/4"-36 UNS = 6.35 mm (same group as SMA) | 36 TPI = 0.7056 mm | threaded | plug = pin; jack = socket | no commercial RP variant | center Ø **1.52 mm** = COMPUTED from the 50-ohm air line: b/2 / (2.301) with b = 3.5 mm outer ID (60·ln(b/a) = 50 ohm in air) | **air** dielectric (small PTFE support beads) — the family key | instrument-panel jack; precision cable plug; PCB end-launch; bulkhead uncommon | thread "1/4-36 UNS (airline)" COMMITTED `chamber-rf-feedthroughs:142`; hex COMMITTED `:143`; "DC-26.5 GHz, precision" COMMITTED `:146`; center COMPUTED (`connector_family_calc.py`); standard class IEEE Std 287 (text not on host) | COMMITTED + COMPUTED |
| 4 | **2.92 mm (K)** (precision) | hex AF 7.94 mm (5/16 in), AC 9.17 mm | 1/4"-36 UNS = 6.35 mm (same group as SMA) | 36 TPI = 0.7056 mm | threaded | plug = pin; jack = socket | none | center Ø **1.27 mm** COMPUTED same 50-ohm air-line method, b = 2.92 mm | air dielectric (PTFE beads) | instrument-panel jack; precision cable plug; PCB end-launch | thread group = SMA group (KNOWLEDGE; mates with SMA); hex/hex from row 3 anchors; DC-40 GHz class; standard class IEEE Std 287 (text not on host) | CLASS-TYPICAL + COMPUTED |
| 5 | **N** (Neill) | hex AF 17.46 mm (11/16 in; committed "~17.5 mm"), AC 20.16 mm COMPUTED | 5/8"-24 UNEF = 15.875 mm (0.625 in; committed "~15.9 mm") | 24 TPI = 1.0583 mm/thread | threaded | plug = pin; jack = socket | see row 6 | pin ~1.6 mm class; socket ID ~1.7 mm class | PTFE white | panel/bulkhead jack (very common); cable plug; PCB edge-launch exists | thread "5/8-24 UNEF" COMMITTED `chamber-rf-feedthroughs:142`; major 15.9 mm COMMITTED `:150-151`; hex ~17.5 mm COMMITTED `:143`; "DC-11 GHz class" COMMITTED `:146`; pin Ø CLASS-TYPICAL; standard class MIL-STD-348 / MIL-C-39012 (text not on host) | COMMITTED + CLASS-TYPICAL |
| 6 | **RP-N** | identical to N | identical 5/8"-24 UNEF = 15.875 mm | identical 24 TPI = 1.0583 mm | threaded | n/a | plug = socket; jack = pin (same flip as RP-SMA) | same contact sizes as N | PTFE white | rare; bulkhead jack + cable plug (some WLAN/broadcast gear) | flip definition = row 2 pattern (KNOWLEDGE); thread = row 5 COMMITTED | CLASS-TYPICAL |
| 7 | **TNC** (Threaded Neill-Concelman) | hex AF **12.7 mm (1/2 in)** AC 14.66 mm COMPUTED — **CORRECTED**: the committed kit value "~3/8 in ~9.5 mm" `chamber-rf-feedthroughs:143` is geometrically IMPOSSIBLE (9.5 < 11.11 thread major; a hex's AF must exceed the thread it encloses). Quantified correction from the kit's own SMA and N wall consistency: (7.94-6.35)/2 = 0.80 mm and (17.46-15.875)/2 = 0.79 mm wall per side → 11.11 + 2x0.79 = **12.70 mm = 1/2 in** exactly. See `connector_family_calc.py` audit B2 | 7/16"-28 UNEF = 11.1125 mm (0.4375 in; committed "~11.1 mm") | 28 TPI = 0.9071 mm/thread | threaded | plug = pin; jack = socket | see row 8 | pin ~1.0-1.1 mm class (shares contact geometry with BNC); socket ~1.2 mm class | PTFE white | panel/bulkhead jack; cable plug; PCB jack | thread "7/16-28 UNEF" COMMITTED `chamber-rf-feedthroughs:142`; major 11.1 mm COMMITTED `:150-151`; "DC-11 GHz class" COMMITTED `:146`; **hex value FLAGGED as erroneous at `:143`** and corrected here (COMPUTED + CLASS-TYPICAL); pin Ø CLASS-TYPICAL | COMMITTED + COMPUTED-CORRECTED |
| 8 | **RP-TNC** | identical to TNC (AF 12.7 mm corrected) | identical 7/16"-28 UNEF = 11.1125 mm | identical 28 TPI = 0.9071 mm | threaded | n/a | plug = socket; jack = pin | same contact sizes as TNC | PTFE white | common on older enterprise WiFi antennas (Cisco/Ubiquiti class); bulkhead jack on APs; cable plug on antennas | flip pattern = row 2 (KNOWLEDGE); thread = row 7 COMMITTED | CLASS-TYPICAL |
| 9 | **BNC** (Bayonet Neill-Concelman) | no hex — knurled bayonet ring, body OD ~14-15 mm class | **none** (2-lug bayonet) | n/a | **bayonet** (2 lugs, quarter-turn) | plug = pin; jack = socket | see row 10 | pin ~1.0-1.1 mm class (shared with TNC); socket ~1.2 mm class | PTFE on quality 50-ohm parts; cheaper parts nylon/Delrin; 75-ohm video variants exist | panel/bulkhead jack (ubiquitous); cable plug; PCB through-hole jack | "none (bayonet: 2-lug)" COMMITTED `chamber-rf-feedthroughs:142`; "2 bayonet lugs" COMMITTED `:144`; "50/75 ohm, DC-4 GHz" COMMITTED `:146`; body OD/pin Ø/dielectric CLASS-TYPICAL; standard class MIL-STD-348 (text not on host) | COMMITTED + CLASS-TYPICAL |
| 10 | **RP-BNC** | identical to BNC | none (2-lug bayonet) | n/a | bayonet | n/a | plug = socket; jack = pin | same sizes as BNC | PTFE/nylon | rare; specialty radio equipment only | flip pattern = row 2 (KNOWLEDGE); bayonet = row 9 COMMITTED | CLASS-TYPICAL |
| 11 | **SMB** (SubMiniature version B) | no hex/thread — snap sleeve; jack shroud OD ~4.5 mm class, plug sleeve ~3.6 mm class | **none** (snap-on) | n/a | **snap-on** | plug = pin; jack = socket | RP variants exist (automotive/telecom) but uncommon | pin ~0.5 mm class; socket ~0.6 mm class | PTFE white | PCB receptacle (jack) + cable plug; panel jack less common | dimensions CLASS-TYPICAL; DC-4 GHz class (up to 10 GHz extended); standard class MIL-STD-348 / CECC (text not on host) | CLASS-TYPICAL |
| 12 | **MCX** (MicroCoaX) | snap sleeve; plug OD ~3.0 mm class (~30 % smaller than SMB) | **none** (snap-on) | n/a | snap-on | plug = pin; jack = socket | RP variants uncommon | pin ~0.4-0.5 mm class | PTFE white | PCB jack + cable plug; bulkhead uncommon | dimensions CLASS-TYPICAL; DC-6 GHz class; standard class CECC 22220 / IEC (text not on host) | CLASS-TYPICAL |
| 13 | **MMCX** (micro-mate micro-CoaX) | snap sleeve; plug OD ~2.2-2.4 mm class (~45 % smaller than MCX) | **none** (snap-on) | n/a | snap-on | plug = pin; jack = socket | RP variants uncommon | pin ~0.3 mm class | PTFE white | PCB jack + cable plug; SMD dominant | dimensions CLASS-TYPICAL; DC-6 GHz class; standard class IEC 61169 (text not on host) | CLASS-TYPICAL |
| 14 | **SMP** (SubMiniature Push-on) | push-on outer sleeve ~2.6-3.0 mm class | **none** (push-on; detent or smooth bore) | n/a | **push-on** | **INVERTED vs SMA: female jack carries the pin; male plug carries a slotted socket** and slides over the jack's outer | no commercial RP (gender is already outer-based) | jack pin ~0.5 mm class; plug socket ~0.6 mm class | mostly air (small PTFE bead) | PCB jack + cable plug + male-male "bullet" adapter + female-female bulkhead; blind-mate board-to-board | dimensions CLASS-TYPICAL; DC-40 GHz class; male-female engagement direction is the family key (KNOWLEDGE); standard class: manufacturer interface spec (Corning Gilbert / radial class; text not on host) | CLASS-TYPICAL |
| 15 | **U.FL / I-PEX MHF1** (Hirose U.FL; I-PEX MHF is cross-licensed equivalent; clones ubiquitous) | **no hex/thread — snap-on; receptacle (board, "female") body OD ~3 mm class** ("tiny 3 mm press-fit" COMMITTED `connector-adapter-bom` H4 `:132`) | **none** (snap/push) | n/a | **board-mount push/snap** | **INVERTED vs SMA: the RECEPTACLE (board, female) carries the center pin; the PLUG (cable, male) carries a spring socket** and its shell snaps over the receptacle's ring | no commercial RP variant (convention already inverted) | receptacle pin ~0.3-0.4 mm class; plug socket ~0.4 mm class | receptacle insulator resin (white or black); plug insert typically white | PCB receptacle + cable plug ONLY (no bulkhead variant; bulkheads require a U.FL-to-SMA pigtail — the project's own documented accessory: "U.FL-to-SMA pigtail + 3dBi SMA antenna included" COMMITTED `esp32c3-mini-v1.json:30`) | "U.FL (I-PEX) for external antenna" COMMITTED `esp32c3-mini-v1.json:29` (project anchor: this carrier's U.FL is MHF1-CLASS); "tiny 3 mm press-fit" COMMITTED `connector-adapter-bom:132`; pin Ø/contact convention CLASS-TYPICAL; DC-6 GHz class; interface spec = Hirose U.FL datasheet class (text not on host) | COMMITTED (anchor + OD class) + CLASS-TYPICAL |

**Convention note (gender, threaded families):** in SMA/N/TNC/BNC the
"plug" is the cable-side part whose coupling nut carries the INTERNAL
thread; the "jack" carries the EXTERNAL coupling thread — so the threaded
part of a jack looks like a "male" bolt while the electrical gender
follows the CENTER contact (plug = pin in all four families). The
committed kit states the thread on the "exterior jack" for exactly this
reason (`chamber-rf-feedthroughs:142`). In the committed procurement
chain this means: "SMA plug, male pin" (BOM B1/B4) = pin inside a
nut-threaded plug; "SMA female jack" (PCB edge-launch, bulkhead) =
socket inside the externally-threaded boss.

**RP definition, once:** reverse polarity swaps ONLY the center contacts
(plug: pin→socket, jack: socket→pin). Outer thread, hex, and body
geometry are UNCHANGED — that is the whole point of RP (FCC Part 15
consumer-antenna deterrence, KNOWLEDGE). Consequence for this campaign:
**no caliper or thread-pitch measurement can ever separate a standard
family from its RP twin.** See the ambiguity list.

---

## U.FL / MHF genuine-diameter variation (task-required note)

"U.FL" and "I-PEX MHF1" are cross-licensed equivalents and mate with each
other. But the MHF GENERATIONS are different interfaces with genuinely
different diameters — they do NOT cross-mate:

| Generation | Receptacle body OD class | Mating height class | Mates with MHF1/U.FL? | Provenance |
|---|---|---|---|---|
| MHF1 (= U.FL class; the project's carrier part, `esp32c3-mini-v1.json:29`) | ~2.6-2.8 mm (overall footprint ~3 mm class — "tiny 3 mm press-fit" COMMITTED) | ~1.2-1.4 mm | (this IS the U.FL class) | COMMITTED anchor + CLASS-TYPICAL dims |
| MHF2 | ~1.6-2.0 mm | ~1.0 mm | NO | CLASS-TYPICAL |
| MHF3 | ~1.6 mm | ~0.9 mm | NO (smallest) | CLASS-TYPICAL |
| MHF4 | ~1.6-2.5 mm | ~1.0 mm class | NO | CLASS-TYPICAL |

All MHF1/2/3/4 dimensions CLASS-TYPICAL, UNVERIFIED — no Hirose or I-PEX
datasheet on host, none fetched (standing constraint). The variation is
recorded because the task asks for it and because it is a real FPV/laptop
procurement trap: an MHF4 pigtail will not mate a U.FL receptacle even
though listing photos look identical. Related lookalikes: **W.FL**
(Hirose, ~2.0 mm class, 4 GHz-class, does NOT mate U.FL) and **H.FL**
(Hirose, SMA-threaded miniature — has a thread, so not confused with
U.FL on inspection). The project's own part is MHF1-class: any pigtail
bought for the SuperMini's U.FL must be U.FL/MHF1 ("U.FL-to-SMA pigtail
... included" `esp32c3-mini-v1.json:30`).

---

## Commonly-confused-with / distinguishing-feature notes

1. **SMA vs RP-SMA — THE explicit callout.** They share the SAME
   1/4"-36 UNS thread (6.35 mm major, 36 TPI, 0.7056 mm pitch) and the
   SAME 7.94 mm AF hex. They differ ONLY in center-pin location:
   standard = pin in the plug; RP = socket in the plug, pin in the jack.
   A photo of the pin location (or looking into the open interface) is
   the ONLY field discriminator. A threaded-almost-home cross-mating
   damages the jack (COMMITTED hazard H2, `connector-adapter-bom:130`);
   this is the campaign's single most likely wrong-part event.
2. **SMA vs 3.5 mm vs 2.92 mm (K)** — same thread group, same hex, and
   they intentionally mate. Distinguish by markings ("3.5mm"/"K"),
   price/provenance, and the dielectric look (air-line with tiny beads
   vs full PTFE), not by caliper. At 868 MHz they are interchangeable
   electrically (COMMITTED `connector-adapter-bom` H3: precision adds
   nothing below 18 GHz).
3. **SMA vs TNC vs N** — unambiguous by thread major OD: 6.35 vs 11.11
   vs 15.88 mm (gaps 4.76 / 4.76 / 9.53 mm — far above caliper error);
   corroborated by TPI 36/28/24 and hex 7.94/12.7/17.46 mm (COMMITTED
   first-sight procedure `chamber-rf-feedthroughs:150-152`).
4. **RP-SMA vs RP-TNC** — WiFi antennas come in both; distinguish by
   thread OD exactly as in note 3, then by pin location as in note 1.
5. **TNC vs BNC** — identical contact size (same 1.0 mm-class pin,
   KNOWLEDGE-class); thread vs 2-lug bayonet is the discriminator
   (`chamber-rf-feedthroughs:144`).
6. **BNC 50 ohm vs 75 ohm** — same shell, same bayonet; they MATE
   mechanically. 75-ohm video BNCs (and 75-ohm N variants) are common lab
   stock; distinguishing requires markings/dielectric inspection, and
   for the campaign a 75-ohm substitution is a hazard (COMMITTED H1
   75-vs-50-ohm hazard class, `connector-adapter-bom:129`).
7. **BNC vs MHV** — MHV (high-voltage) looks like BNC with an extended
   dielectric; do NOT mate (KNOWLEDGE).
8. **N vs 7-16 DIN** — broadcast sites use 7-16 DIN (16 mm-class thread,
   much larger); larger than N in every dimension, so no caliper
   ambiguity (KNOWLEDGE, out of the candidate list — no such part on any
   record).
9. **SMB vs MCX vs MMCX** — all snap-on, no thread; sorted by size:
   SMB jack shroud ~4.5 mm > MCX ~3.0 mm > MMCX ~2.2-2.4 mm class. They
   do not cross-mate. FAKRA (automotive) is an SMB interface inside a
   keyed plastic housing — snap one on and it IS SMB-class (KNOWLEDGE).
10. **SMP vs everything** — push-on with detent; the only family in this
    list where the JACK presents the pin and the plug slides OVER it
    (inverted convention, blind-mate heritage). Not confusable with SMA
    (no thread) but confusable with nothing else here except MMCX at a
    glance — detent click and the pin-in-jack are the tells.
11. **U.FL vs clones/generations** — see the MHF table above; all
    MHF1-class clones (U.FL, MHF, various no-names) mate each other;
    MHF2/3/4 and W.FL do not. No pin-location ambiguity within U.FL
    (the convention is fixed), but plug-vs-receptacle engagement is
    counterintuitive: the plug (cable side) contains the SOCKET contact.

---

## First-sight decision tree (caliper → family → pin photo → polarity)

Step 1: bayonet lugs visible? → BNC-family (row 9/10). No hex, no thread,
quarter-turn ring.
Step 2: snap-on, no thread at all? → size sort: ~4.5 mm shroud = SMB;
~3.0 mm = MCX; ~2.2-2.4 mm = MMCX; ~3 mm board receptacle with raised
ring (plug snaps over) = U.FL/MHF1; detent push-on with pin in jack =
SMP. (All CLASS-TYPICAL sizes; bring the pin-photo habit anyway.)
Step 3: threaded? measure thread major OD: 6.35 mm (36 TPI) → SMA group;
11.11 mm (28 TPI) → TNC group; 15.88 mm (24 TPI) → N group.
Step 4: hex AF as corroborator: 7.94 mm → SMA group; 12.7 mm → TNC
(corrected value — see row 7); 17.46 mm → N.
Step 5 (the ONLY way to split standard from RP): photograph or
inspection of the OPEN interface center — pin or socket on which side.
This is the ambiguity list, below.

---

## PAIRS THAT CANNOT BE DISTINGUISHED WITHOUT A PHOTO OF PIN LOCATION

The required list. These pairs are dimensionally IDENTICAL in every
externally measurable respect (thread, pitch, hex/OD, bayonet pattern) —
a caliper, thread gauge, or eye cannot separate them; only direct
inspection of the center-contact location (a pin-location photo) can:

1. **SMA vs RP-SMA** — same 1/4"-36 UNS thread, same 7.94 mm AF hex.
   Standard: plug carries the pin. RP: plug carries the socket, jack
   carries the pin. (The campaign's #1 wrong-part hazard, COMMITTED H2.)
2. **N vs RP-N** — same 5/8"-24 UNEF thread, same hex.
3. **TNC vs RP-TNC** — same 7/16"-28 UNEF thread, same hex (older WiFi
   gear is frequently RP-TNC; assume nothing without the pin photo).
4. **BNC vs RP-BNC** — same 2-lug bayonet shell.

Related-but-different photo requirements (NOT pin-location pairs, listed
to prevent over-claiming what a caliper can do): **SMA vs 3.5 mm vs
2.92 mm** (same thread + hex; need a photo of markings/dielectric, not
pin location) and **BNC 50 vs 75 ohm** (need a marking photo). By
contrast, MHF1 vs MHF2/3/4 IS caliper-separable (different diameters),
and SMA vs TNC vs N is trivially caliper-separable.

---

## Committed-value correction (flagged, with arithmetic)

`bench/chamber-rf-feedthroughs/REPORT.md:143` lists the TNC hex nut as
"~3/8 in ≈ 9.5 mm" AF. **This is geometrically impossible**: a hex nut's
across-flats must EXCEED the major diameter of the thread it encloses
(11.11 mm for 7/16"-28); 9.5 mm AF would place the nut's flats INSIDE
the thread's major circle. The kit's own SMA and N rows imply a
consistent wall of 0.79-0.80 mm per side; applying that wall to TNC
gives 11.1125 + 2 x 0.79 = 12.70 mm = exactly 1/2 in — the class-typical
TNC coupling/jam-nut hex. This sheet carries 12.7 mm AF (1/2 in), AC
14.66 mm COMPUTED, labeled CLASS-TYPICAL like the rest of the kit, and
flags the source line rather than silently repeating it. Full audit in
`connector_family_calc.py` section B2; the same script reproduces every
COMMITTED anchor it touches (4/4 cross-checks PASS: SMA major 6.35,
SMA pitch 0.7056, TNC major 11.1125, SMA hex AC 9.17).

---

## NOTHING FABRICATED

This sheet contains zero measurements: no physical connector, cable,
chamber, DUT, caliper, or camera exists on this host (seven prior bench
reports and fresh censuses concur — `rf-connector-geometry` STEP 0,
`instrument-rf-connectors`, `coax-bundle-dimensions`, `chamber-rf-
feedthroughs`, `connector-adapter-bom`, `dut-rf-ports`, `dut-board-
identity`). The DUT was not accessed (task requires none). No vendor
datasheet or standard text exists on this host and no outbound fetch was
attempted (standing constraint). Every CLASS-TYPICAL value is marked
approximate/UNVERIFIED with its carrier; every COMMITTED value is cited
to path:line in this repo; every COMPUTED value shows its arithmetic in
`connector_family_calc.py` (stdlib only, byte-identical rerun, output
captured verbatim in `output.txt`). One committed value (TNC hex 9.5 mm)
is flagged as impossible rather than repeated. Every number carries a
unit. Every family in the task's minimum list has a full row (15 rows:
SMA, RP-SMA, 3.5 mm, 2.92 mm K, N, RP-N, TNC, RP-TNC, BNC, RP-BNC, SMB,
MCX, MMCX, SMP, U.FL/MHF1), the MHF1/2/3/4 variation note is present,
and the pin-location ambiguity list is present.