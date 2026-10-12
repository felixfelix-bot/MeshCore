# Bench Frequency-Instrument Inventory — BLOCKED (no physical access)

**Task:** On-bench inventory of every instrument on the bench that can READ, MEASURE,
GENERATE, or REFERENCE a frequency, plus one line per pure reference source encountered.

**Worker:** `worker-base` (fleet offload worker, repository `meshcore-fork-fix`)
**Branch:** `worker-base/bench-freq-instrument-inventory`
**Date:** 2026-10-12

**Status: BLOCKED — capability, not budget.** The instrument rows below are **PLACEHOLDERS**,
present only to satisfy the required schema. They contain **no invented serials, models, tags,
or ports**. Read this warning before consuming the table.

---

## 0. Why this report is blocked (read first)

The task is explicitly a **PHYSICAL task**: *"you must be physically standing at the bench with a
notepad or phone... read every value off the physical label."* This worker is a **software agent
running in a shell on a headless Linux host**. It has:

- **no camera** it can point at a bench (no `~/bench-images` capture pipeline — that directory is a
  misnomer holding only OpenWrt `.bin`/`.apk` firmware artifacts; verified below);
- **no operator** relaying labels (a delegate/subprocess has no user to ask);
- **no instrument connectivity** — the decisive check (see §3): no USBTMC (`/dev/usbtmc*`),
  no GPIB (`/dev/gpib*`), no VISA/pyvisa, no identifiable test-equipment on the USB bus. The only
  serial devices attached are the laptop's **own** Sierra Wireless EM7455 LTE modem.

Therefore the agent **cannot read a single physical label**. Per the honesty contract, the agent
**must not** fabricate tag numbers, make/models, serial numbers, locations, or reference-port
capability. Guessing serials would be the exact failure the task forbids
(*"never invented"*). So the correct deliverable is this blocked-work report plus a
**fill-in worksheet** the human at the bench can complete in one pass.

**What WOULD unblock this** (any one of):
1. A human at the bench fills the worksheet in §5 (or pastes/attaches the raw label text).
2. Camera photos of each instrument (front + rear labels) are dropped in a directory the worker can
   read, and the worker OCRs them. *(Note: OCR of a photo is second-hand vs. reading the label; the
   task explicitly requires physical reading, so this is a fallback, not a substitute.)*
3. The instruments are cabled for remote control (USBTMC/GPIB/LAN-VISA); then `*IDN?` over SCPI
   returns real make/model/serial and the worker can enumerate them directly.

---

## 1. Inventory table

Schema is as required: `tag | make/model | serial | location | function | freq-ref-capable (Y/N/maybe) | notes`.
**`TBD` = to be determined at the bench by the human. No value here was invented.**

| tag | make/model | serial | location | function | freq-ref-capable (Y/N/maybe) | notes |
|-----|-----------|--------|----------|----------|------------------------------|-------|
| TBD | TBD | UNREADABLE - no physical access (shell agent, no camera/operator) | TBD - bench not observable | TBD | maybe - cannot be determined without reading the rear ref-in/out ports | PLACEHOLDER ROW. Not a real instrument. Replace at the bench. |
| TBD | TBD | UNREADABLE - no physical access (shell agent, no camera/operator) | TBD - bench not observable | TBD | maybe - cannot be determined without reading the rear ref-in/out ports | PLACEHOLDER ROW. Not a real instrument. Replace at the bench. |

> **The `<N>` placeholder rows above are NOT items.** They exist solely so the required six-column
> schema is present. **True in-scope item count from this run = 0.** Do not report a count of 2.

---

## 2. UNIDENTIFIED subsection

**none identified** — no device was observed, because the bench is not observable from this shell.
(If, during the human pass, any device's identity cannot be established, record here:
approximate size H×W×D in cm; connector types + counts; all visible silkscreen/lettering/logos/model
fragments; front-panel control layout; exact location; photograph if possible.)

---

## 3. On-box evidence of the capability gap (reproducible)

```
$ ls -la /dev/usbtmc* /dev/gpib* /dev/video*            # instrument I/O + cameras
ls: cannot access '/dev/usbtmc*': No such file or directory
ls: cannot access '/dev/gpib*':   No such file or directory
crw-rw---- 1 root video 81, 0 /dev/video0              # laptop webcam only, not a bench rig
crw-rw---- 1 root video 81, 1 /dev/video1

$ lsusb                                                  # no test equipment vendor present
... Sierra Wireless EM7455 (laptop WWAN), Intel BT, Bison Integrated Camera,
    Realtek card reader, ASIX/RTL USB-Ethernet dongles, Genesys hubs ...

$ readlink /dev/serial/by-id/*                           # only the laptop's own LTE modem
usb-Sierra_Wireless_EM7455_..._LF84167162011024-if00-port0 -> ../../ttyUSB0

$ ls ~/bench-images/                                     # NOT bench photos
openwrt-25.12.5-mediatek-filogic-glinet_gl-mt3000-*.bin ... tollgate-wrt_*.apk
```

Conclusion: **0 frequency instruments are observable or addressable from this host.**

---

## 4. Reference-source gear (separate-parallel)

**none encountered** — the bench was not observable, so no rubidium / GPSDO / OCXO could be seen.
(If found at the bench, log a single line only: `tag | make/model | location`. Do not expand to the
six-column table — that gear is owned by another worker.)

---

## 5. Human fill-in worksheet (one pass, bench side)

Walk the bench rack by rack, shelf by shelf, left→right. One block per instrument. Cover the REAR
panels on the second pass (ref in/out ports decide the last column). Add rows as needed.

```
ITEM n
tag .................. : (label text, or the literal string: none)
make/model ........... : 
serial ............... : (character-for-character; if unreadable -> UNREADABLE - <reason>)
location ............. : rack id + RU   OR   shelf id + left/right position
function ............. : (one line: what it does on THIS bench)
freq-ref-capable ..... : Y / N / maybe  +  one-clause reason
      e.g. N - counter only, needs external ref in
      e.g. Y - internal OCXO plus ref in/out on rear
      e.g. maybe - rear 10 MHz port unlabeled, could not verify without powering
connectors seen ...... : (BNC / N / SMA / SO-239 / TNC ... + counts)
```

Also capture, in the same pass:
```
[ ] Any device with an RF port whose identity is unsure -> fill the UNIDENTIFIED block in §2.
[ ] Any pure reference source (rubidium/GPSDO/OCXO)  -> one line only: tag | make/model | location.
[ ] Areas you could NOT access (locked cabinet, rear of rack, under bench) -> note for §6.
```

---

## 6. Closing count and access statement

**Total in-scope instruments recorded in this run: 0** (table rows that are real items = 0;
UNIDENTIFIED entries = 0; the §1 placeholder rows are not items and must not be counted).
Separate-parallel pure reference sources recorded: **0**.

**Bench areas that could not be accessed: the entire bench.** This worker had **no physical or
remote access** to the bench, so 0 of an unknown total number of instruments were inventoried.
When the human pass in §5 is completed, the true total = number of real table rows + UNIDENTIFIED
entries, and its closing sentence must list any areas still inaccessible (locked cabinet, rack
rear, etc.).
