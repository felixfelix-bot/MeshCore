# `cal` serial-CLI argument spec — passive_mapper @ 3fdfbc8e

Firmware: felixfelix-bot/MeshCore, branch `feat/passive-mapper`,
commit `3fdfbc8e120e13d7543fe224c380e27533e720aa`
("feat(passive_mapper): BW125 runtime fallback, cal-range predicate, cal-blob
writer", 2026-09-11). All `file:line` citations below refer to that commit.
Every behavioral claim marked [H] is machine-verified by
`bench/atcut-fit/cal_cli_harness.cpp` (this directory), which compiles the
firmware's own `SelfCal.h` from the clone plus verbatim copies of
`parseFloat` (MyMesh.cpp:128-143) and the `cal` dispatch (MyMesh.cpp:166-177),
and a faithful port of the serial reader (main.cpp:67-93). Build/run
instructions at the bottom; expected output is embedded below per claim.

Companion doc: `REPORT.md` §1 (summary contract, post-pin drift). This file
is the full end-to-end extraction.

## 1. Command surface and dispatch

- The serial CLI reads one line into a 160-byte buffer and dispatches it via
  `MyMesh::handleCommand(command, reply)` — main.cpp:15, main.cpp:67-93,
  main.cpp:88; declaration MyMesh.h:82.
- The `cal` command is selected by `strncmp(cmd, "cal ", 4) == 0`
  (MyMesh.cpp:166). The 4th byte must be a **space (0x20)** — a tab after
  `cal` is NOT the cal command [H: `cal\t0.04 25` → help line]. Leading
  whitespace before `cal` also fails the prefix (no trimming).
- Exactly **2 arguments, order `cal <k> <T0>`**: `k` first, `T0` second
  (MyMesh.cpp:168-170). Units stated in the handler's own comment at
  MyMesh.cpp:167: *"cal <k> <T0>   (k in ppm/C^2, T0 in C)"*.
- On success the firmware replies
  `cal k=%.6g T0=%.2fC -> persisted (valid=yes)` (MyMesh.cpp:172-174);
  on any parse failure `usage: cal <k_ppm_per_C2> <T0_C>` (MyMesh.cpp:176).
- Read-back command: `calshow` → `cal valid=%s k=%.6g T0=%.2fC range=+/-60C
  die_temp=... off_hz=...` (MyMesh.cpp:178-181, CAL_RANGE_C at SelfCal.h:36).

## 2. Serial line framing (needed to build the literal string)

- **The line terminator is CR (`\r`, 0x0D).** Completion is detected by
  `command[len-1] == '\r'` (main.cpp:83), which then strips it (main.cpp:85).
- `\n` is **skipped, never appended** (main.cpp:72-76) — a LF-only-terminated
  line NEVER executes; the bytes just sit buffered until a `\r` arrives
  [H: `cal 0.04 25\n` → 0 commands executed; `cal 0.04 25\r` → 1].
- CRLF works (the trailing LF is drained silently on the next loop pass)
  [H: `\r\n` → exactly 1 command].
- Max command length 159 bytes; a full buffer force-terminates with `\r`
  (main.cpp:79-81), i.e. an over-long line executes TRUNCATED — keep the
  line ≤ 159 chars.
- Every received byte except `\n` is echoed; the reply is printed as
  `  -> <reply>` (main.cpp:75, main.cpp:89-91).

**Wire template (verbatim):**

    cal <k> <T0>\r

## 3. Number grammar — `parseFloat` (MyMesh.cpp:128-143)

Custom parser, deliberately not `sscanf("%f")`/`strtof` (flash cost, comment
at MyMesh.cpp:125-127). Grammar accepted for EACH argument:

    arg      := ws* sign? integer [ '.' fraction? ]
    ws       := ' ' | '\t'          (zero or more, MyMesh.cpp:129)
    sign     := '-' | '+'           (single, optional; MyMesh.cpp:130-131)
    integer  := digit+              (AT LEAST ONE DIGIT REQUIRED, MyMesh.cpp:132)
    fraction := digit+              (zero or more digits, MyMesh.cpp:135-139)

Hard properties (all [H]-verified):

- **Integer-vs-float**: both arguments are parsed as decimal floats —
  `atof`-style, not `atoi`. Integers are just the `integer`-only case.
- **Leading digit REQUIRED**: `.04` is REJECTED (MyMesh.cpp:132 returns false
  before any digit is seen). Write `0.04` [H].
- **No exponent**: `e`/`E` stops the parse. `4e-2` parses k as `4`, then the
  T0 parse chokes on `e` → usage error [H]. Never use scientific notation.
- **Leading zeros accepted**: `000.0340` → 0.0340, `+024.95` → 24.95 [H].
- **Sign**: `+`/`-` allowed on both args (MyMesh.cpp:130-131). `-0` parses to
  IEEE −0.0f, and `k >= 0.0f` is TRUE for −0.0, so `cal -0 25` is ACCEPTED
  and stores k = 0x80000000 [H].
- **Trailing dot OK**: `25.` → 25.0 (the fraction loop body just runs zero
  times, MyMesh.cpp:135-139) [H]. A second dot (`0..04`) stops the first
  parse at `0`, and the second parse fails at `.` → usage [H].
- **Separator between k and T0**: one or more spaces and/or tabs
  (the second `parseFloat` skips its own leading whitespace, MyMesh.cpp:129)
  [H: `cal 0.04  25`, `cal 0.04\t25` both accepted]. A **comma is NOT a
  separator** — `cal 0.04,25` → usage [H].
- **Missing separator TRAP**: `cal 0.04-25` is ACCEPTED with T0 = **−25** —
  the `-` is consumed as T0's sign [H]. A lost space silently negates T0.
- **Trailing garbage after T0 is silently ignored**: the T0 parse is called
  with `endp = nullptr` and nothing checks the remainder
  (MyMesh.cpp:170) — `cal 0.034 24.95xyz` and `cal 0.04 25 99` both succeed
  [H]. Only k's parse consumes via `endp` (to chain into T0).
- **Missing T0 → usage**: `cal 0.04` and `cal 0.04 ` both fail (the T0 parse
  hits end-of-string, no digit) [H].
- **No NaN possible** from this grammar; **+inf possible** via absurdly long
  digit strings (float overflow in the `v*10` accumulator, MyMesh.cpp:134) —
  pathological, accepted by the k≥0 gate; the model output is then clamped
  to ±300 ppm anyway (SelfCal.h:30, SelfCal.h:91-92).

## 4. Units, scaling, semantic gate

- **k: ppm/°C²** — the parabola magnitude in
  `offset_ppm = -k*(T-T0)^2` (model at SelfCal.h:89). Positive magnitude:
  the applied compensation offset is NEGATED relative to measured drift
  (offset applied at MyMesh.cpp:386-389 as `offset_hz = ppm * freq_MHz`,
  i.e. ppm × MHz = Hz).
- **T0: degrees C** — the vertex temperature of the parabola.
- **Semantic gate**: `k >= 0.0f` (MyMesh.cpp:170). Negative k → usage [H].
  No upper bound on k, **no constraint at all on T0** (any sign/magnitude
  accepted; also accepted after a prior blob load — `setCalibration` never
  validates, SelfCal.h:44-46, it just sets `_cal_valid = true`). Even
  `cal 0 25` marks the cal "valid" with zero compensation [H: -0 case].
- **NO scaling, multiplier, or fixed-point is applied anywhere**: the parsed
  float32 bit patterns are passed verbatim `handleCommand → writeCalBlob →
  setCalibration → storeCalibration → memcpy into the blob`
  (MyMesh.cpp:171, MyMesh.cpp:271, SelfCal.h:65-73). What you type is what
  the model uses and what lands in `/selfcal.dat`.

## 5. Precision / decimal places

- The parser has **no decimal-count limit and does no rounding**: integer
  part accumulates `v = v*10 + digit` (MyMesh.cpp:134), fraction accumulates
  `v += digit * scale; scale *= 0.1f` (MyMesh.cpp:138), all in **float32**.
- Preservation is therefore bounded by float32 (~7.2 significant decimal
  digits). [H] ulp comparison against correctly-rounded `strtof` for
  cal-shaped values: `0.034021` exact match, `0.04` +1 ulp, `24.95` −1 ulp,
  `0.04123456789012` exact (everything past ~7 digits is already below f32
  resolution). ⇒ **6 significant digits for k and 2 decimals for T0 are
  exactly sufficient** and match the firmware's own echo format `%.6g` /
  `%.2f` (MyMesh.cpp:172). More digits are accepted but cannot be stored.
- The echo/`calshow` display rounds to `%.6g`/`%.2f` — display only; the
  stored f32 keeps full precision.

## 6. Blob layout cross-check (what the firmware does with the values)

`writeCalBlob(k, t0)` (MyMesh.cpp:270-281): `setCalibration(k, t0)` (:271,
RAM-first — a later FS failure still leaves the new cal active, reply says
"RAM only, file write failed"), then remove+rewrite `/selfcal.dat`
(MAP_CAL_FILE, MyMesh.h:48; remove :273, open "w" :274, write :278, success
= wrote exactly BLOB_SIZE :280).

Blob = **15 bytes** (`SelfCal::BLOB_SIZE`, SelfCal.h:21), written by
`storeCalibration` (SelfCal.h:65-73) via `memcpy` (native endianness — all
supported targets nRF52/STM32/ESP32/RP2040 are little-endian):

| offset | size | field        | source                      |
|--------|------|--------------|-----------------------------|
| 0      | 4    | k, f32 LE    | SelfCal.h:66                |
| 4      | 4    | T0, f32 LE   | SelfCal.h:67                |
| 8      | 4    | spare = 0.0f | SelfCal.h:68-69             |
| 12     | 2    | magic 0x5343 ('SC'), LE → bytes `43 53` | SelfCal.h:22, :70-71 |
| 14     | 1    | version = `_ver` | SelfCal.h:72            |

Version byte is always **0**: `_ver` starts 0 (SelfCal.h:39), `setVersion`
exists (SelfCal.h:157) but is **never called anywhere in the example**
(grep over examples/passive_mapper @ 3fdfbc8e: zero call sites), and
`loadCalibration` (SelfCal.h:48-63) only propagates a ver that was itself 0.
Load path checks length + magic only (SelfCal.h:49, :57), then seeds the
thermal EMA with T0 (`_temp_ema = T0`, SelfCal.h:60) — another confirmation
T0 is plain °C.

[H] worked example, `cal 0.034021 24.95\r`:

    reply : cal k=0.034021 T0=24.95C -> persisted (valid=yes)
    k     : 0x3D0B599B   T0 : 0x41C79999
    blob  : 9B 59 0B 3D 99 99 C7 41 00 00 00 00 43 53 00
    reload: loadCalibration() round-trips both floats bit-identically,
            cold-start EMA = T0 = 24.95 C

Boot-time cross-check: `begin()` loads the blob and debug-prints
`selfcal: loaded cal blob (k=%d.%03d T0=%d.%02d)` — k printed in
milli-units (×1000), T0 in centi-degrees (×100) — display scaling only,
not storage (MyMesh.cpp:60-69).

## 7. Verbatim command template

    cal <k> <T0>\r

with:

- `<k>`  — ppm/°C², parabola magnitude, ≥ 0, plain decimal only:
  `[0-9]+(.[0-9]+)?`, leading digit before any `.`, no exponent, no sign
  (a `+` is legal but pointless; `-` is rejected). Emit ≤ 6 significant
  digits, e.g. `0.034021`.
- `<T0>` — °C, any sign, plain decimal, e.g. `24.95` / `-10.5` / `25`.
  2 decimals are fully preserved by the f32 blob.
- separator: single space (multiple spaces/tabs also legal; comma is not).
- terminator: **CR (0x0D)**, optionally followed by LF. LF-only will NOT
  execute.

Conforms to the fitter's emission format `cal %.6g %.2f` (fit_atcut.py /
the fork's own bench kit): for the gated k band 0.005–0.15 ppm/°C² and any
plausible T0, `%.6g` never emits an exponent and always keeps the leading
digit, so the printed line is always parser-legal.

Fill-in example (SYNTHETIC self-test numbers, not a measurement):

    cal 0.034021 24.95\r
      -> cal k=0.034021 T0=24.95C -> persisted (valid=yes)

Verify after issuing: `calshow\r` → `cal valid=yes k=0.034021 T0=24.95C
range=+/-60C die_temp=... off_hz=...` (MyMesh.cpp:178-181). Note the
calibrated band is |T_die − T0| ≤ 60 °C (SelfCal.h:36, :136-141) — outside
it the firmware falls back to BW125 and holds the last offset
(MyMesh.cpp:356-371), which is why T0 should be the fitted vertex, not an
arbitrary midpoint.

## 8. Edge-case matrix (harness-verified [H])

| input (line, pre-CR)        | outcome                                          |
|-----------------------------|--------------------------------------------------|
| `cal 0.034021 24.95`        | ACCEPT, k=0x3D0B599B T0=0x41C79999               |
| `cal 0.04 25`               | ACCEPT, canonical                               |
| `cal 0.034 24.95xyz`        | ACCEPT (trailing garbage ignored)                |
| `cal 0.04 25 99`            | ACCEPT (3rd arg ignored)                         |
| `cal 000.0340 +024.95`      | ACCEPT (leading zeros, + sign)                   |
| `cal 0.04  25` / `0.04<TAB>25` | ACCEPT (ws run between args)                  |
| `cal 25. 30`                | ACCEPT (trailing dot)                            |
| `cal 0.04 -40.0` / `0.04 1000` | ACCEPT (T0 unconstrained)                     |
| `cal +0.04 25`              | ACCEPT                                           |
| `cal -0 25`                 | ACCEPT (−0.0f ≥ 0.0f; stores 0x80000000)         |
| `cal 0.04-25`               | ACCEPT — **TRAP**: T0 silently = −25             |
| `cal .04 25`                | usage (leading digit required)                   |
| `cal 4e-2 25`               | usage (no exponent)                              |
| `cal 0.04` / `cal 0.04 `    | usage (T0 missing)                               |
| `cal 0..04 25`              | usage                                            |
| `cal -0.04 25`              | usage (k < 0)                                    |
| `cal 0.04,25`               | usage (comma not a separator)                    |
| `cal 0.04- 25`              | usage (sign with no digits after it)             |
| `cal<TAB>0.04 25` / `cal`   | not a cal command (help line)                    |
| wire `cal 0.04 25\n` (LF only) | NEVER EXECUTES                                |
| wire `cal 0.04 25\r` / `\r\n` | executes once                                 |

## 9. Reproducing the verification

    git clone --filter=blob:none https://github.com/felixfelix-bot/MeshCore
    git -C MeshCore checkout 3fdfbc8e
    g++ -O2 -Wall -Wextra -I MeshCore/examples/passive_mapper/host \
        -o cal_harness bench/atcut-fit/cal_cli_harness.cpp
    ./cal_harness        # 30/30 checks print [OK ], exit 0

Provenance note: the clone used this session lives at /tmp/mc-passive
(HEAD verified 3fdfbc8e). The harness embeds verbatim firmware code with
source line citations in comments; the only deviation is the mocked
filesystem layer in `writeCalBlobMock`, marked MOCK.
