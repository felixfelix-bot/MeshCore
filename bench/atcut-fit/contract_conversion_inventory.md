# Contract conversion inventory - `cal <k> <T0>` parser contract

- Card: **t_bb4bbf91** 'Extract full conversion inventory from parser contract' (meshcore board, run 1041, 2026-10-01).
- Contract artifact inventoried (read top to bottom, 242 lines):
  `/home/c03rad0r/repos/meshcore/bench/atcut-fit/CAL-CLI-SPEC.md`
  @ repo `main` commit `bb8cdc9dae469cf0b8261579ee580655c3ec5650`,
  git blob `378e30311600113ebf32f61979adb5ffb25eb56b` (working tree == HEAD,
  242 lines, 13450 B). Created by commit `2075f921` (family card
  n4s-t_d6484f25 'Document serial cal <k> <T0> parser contract with file:line
  citations'); confirmed the only `*spec*` file tracked in the repo by
  bench/cal-emission-provenance/SPEC-SECTIONS.md:64-65. The contract pins
  firmware felixfelix-bot/MeshCore feat/passive-mapper @ `3fdfbc8e`; all
  MyMesh.cpp / SelfCal.h / main.cpp references below are the CONTRACT's own
  citations into that pin, reproduced as-is.
- Format: **Markdown** (repo convention: prose bench docs). Exactly two content sections follow: the conversion entries and the gaps.
- Scope: THIS ONE FILE only. Companion docs (REPORT.md, CAL-COMMAND.md,
  cal_cli_harness.cpp, verify_cal_domain.py, SPEC-SECTIONS.md, PROVENANCE-MAP.md)
  are NOT part of the contract and are NOT inventoried; they are named only where
  they affect interpretation. The %.6g/%.2f rounding-penalty budget in
  CAL-COMMAND.md is quantification in a companion doc, not a contract conversion.
- Verbatim guarantee: every quoted citation block below is spliced programmatically from
  the contract file bytes at the cited line numbers (never retyped); a
  post-write checker re-extracts and byte-compares every block (see
  completion report).

## Conversions

9 conversion entries, ordered by first contract appearance.

### 1. `parsearg_to_f32`

- **Direction(s) covered:** decimal ASCII text -> IEEE-754 binary32 (float32). One direction only; the reverse (float32 -> decimal text) is documented only as the printf formats of entry 6.
- **Input -> output units:** in: unitless decimal token (`k` semantically ppm/degC^2, `T0` semantically degC) -> out: float32
- **Exact factor / offset (as documented):** integer part: `v = v*10 + digit`; fraction: `v += digit * scale; scale *= 0.1f` (exact operators as quoted; the initial value of `scale` is NOT stated in the contract - see Gaps G4)
- **Integer-vs-float semantics (as stated):** float32, "atof-style, not atoi"; integers are just the integer-only case. Documented edge semantics: `-0` parses to IEEE -0.0f and stores bit pattern 0x80000000; no NaN possible; +inf possible via float overflow in the `v*10` accumulator.
- **Contract citations (verbatim):**

> **bench/atcut-fit/CAL-CLI-SPEC.md:59-63**
>
>     arg      := ws* sign? integer [ '.' fraction? ]
>     ws       := ' ' | '\t'          (zero or more, MyMesh.cpp:129)
>     sign     := '-' | '+'           (single, optional; MyMesh.cpp:130-131)
>     integer  := digit+              (AT LEAST ONE DIGIT REQUIRED, MyMesh.cpp:132)
>     fraction := digit+              (zero or more digits, MyMesh.cpp:135-139)

> **bench/atcut-fit/CAL-CLI-SPEC.md:67-68**
>
> - **Integer-vs-float**: both arguments are parsed as decimal floats —
>   `atof`-style, not `atoi`. Integers are just the `integer`-only case.

> **bench/atcut-fit/CAL-CLI-SPEC.md:118-120**
>
> - The parser has **no decimal-count limit and does no rounding**: integer
>   part accumulates `v = v*10 + digit` (MyMesh.cpp:134), fraction accumulates
>   `v += digit * scale; scale *= 0.1f` (MyMesh.cpp:138), all in **float32**.

> **bench/atcut-fit/CAL-CLI-SPEC.md:74-76**
>
> - **Sign**: `+`/`-` allowed on both args (MyMesh.cpp:130-131). `-0` parses to
>   IEEE −0.0f, and `k >= 0.0f` is TRUE for −0.0, so `cal -0 25` is ACCEPTED
>   and stores k = 0x80000000 [H].

> **bench/atcut-fit/CAL-CLI-SPEC.md:92-93**
>
> - **No NaN possible** from this grammar; **+inf possible** via absurdly long
>   digit strings (float overflow in the `v*10` accumulator, MyMesh.cpp:134) —

### 2. `parsed_f32_pass_through`

- **Direction(s) covered:** float32 -> float32 (verbatim identity, no numeric change). Documented NON-conversion: the parsed bit patterns flow unchanged from parse to model to blob.
- **Input -> output units:** in: parsed float32 k, T0 -> out: identical float32 values in the calibration model and /selfcal.dat
- **Exact factor / offset (as documented):** none - 'NO scaling, multiplier, or fixed-point is applied anywhere'
- **Integer-vs-float semantics (as stated):** float32 bit patterns passed verbatim; integer form never materializes on this path.
- **Contract citations (verbatim):**

> **bench/atcut-fit/CAL-CLI-SPEC.md:110-114**
>
> - **NO scaling, multiplier, or fixed-point is applied anywhere**: the parsed
>   float32 bit patterns are passed verbatim `handleCommand → writeCalBlob →
>   setCalibration → storeCalibration → memcpy into the blob`
>   (MyMesh.cpp:171, MyMesh.cpp:271, SelfCal.h:65-73). What you type is what
>   the model uses and what lands in `/selfcal.dat`.

### 3. `temp_to_offset_ppm`

- **Direction(s) covered:** degC -> ppm (one direction; inverse not documented - see Gaps G3)
- **Input -> output units:** in: T (die temp, degC), T0 (vertex temp, degC), k (ppm/degC^2) -> out: offset_ppm (ppm)
- **Exact factor / offset (as documented):** `offset_ppm = -k*(T-T0)^2` - explicit negation: applied compensation offset is NEGATED relative to measured drift
- **Integer-vs-float semantics (as stated):** float32 model (fed by the verbatim parsed f32 of entry 2); no integer semantics documented for the model.
- **Contract citations (verbatim):**

> **bench/atcut-fit/CAL-CLI-SPEC.md:99-101**
>
> - **k: ppm/°C²** — the parabola magnitude in
>   `offset_ppm = -k*(T-T0)^2` (model at SelfCal.h:89). Positive magnitude:
>   the applied compensation offset is NEGATED relative to measured drift

> **bench/atcut-fit/CAL-CLI-SPEC.md:104**
>
> - **T0: degrees C** — the vertex temperature of the parabola.

### 4. `ppm_to_hz`

- **Direction(s) covered:** ppm -> Hz (one direction; Hz -> ppm not documented - see Gaps G2)
- **Input -> output units:** in: offset in ppm, frequency in MHz -> out: offset in Hz
- **Exact factor / offset (as documented):** `offset_hz = ppm * freq_MHz`, i.e. ppm x MHz = Hz. The value of freq_MHz itself is NOT stated in the contract - see Gaps G5.
- **Integer-vs-float semantics (as stated):** float (f32 path); no integer semantics documented.
- **Contract citations (verbatim):**

> **bench/atcut-fit/CAL-CLI-SPEC.md:102-103**
>
>   (offset applied at MyMesh.cpp:386-389 as `offset_hz = ppm * freq_MHz`,
>   i.e. ppm × MHz = Hz).

### 5. `clamp_offset_ppm_300`

- **Direction(s) covered:** ppm -> ppm (range clamp on the model output)
- **Input -> output units:** in: model output offset_ppm -> out: clamped offset_ppm, bounds +/- 300 ppm
- **Exact factor / offset (as documented):** clamp to +/- 300 ppm (SelfCal.h:30, SelfCal.h:91-92 per the contract). Clamp ordering relative to the ppm->Hz conversion of entry 4 is NOT stated - see Gaps G7.
- **Integer-vs-float semantics (as stated):** float; bounds are decimal +/-300.
- **Contract citations (verbatim):**

> **bench/atcut-fit/CAL-CLI-SPEC.md:92-95**
>
> - **No NaN possible** from this grammar; **+inf possible** via absurdly long
>   digit strings (float overflow in the `v*10` accumulator, MyMesh.cpp:134) —
>   pathological, accepted by the k≥0 gate; the model output is then clamped
>   to ±300 ppm anyway (SelfCal.h:30, SelfCal.h:91-92).

### 6. `format_k_t0_echo`

- **Direction(s) covered:** float32 -> decimal display/emission string. Same direction documented at four sites: success echo, calshow, display rounding rule, and fitter emission format.
- **Input -> output units:** in: k (float32, ppm/degC^2), T0 (float32, degC) -> out: decimal strings
- **Exact factor / offset (as documented):** k rendered `%.6g` (6 significant digits), T0 rendered `%.2f` (2 decimals); for the gated k band 0.005-0.15 ppm/degC^2 `%.6g` never emits an exponent
- **Integer-vs-float semantics (as stated):** float32 -> string; 'display only; the stored f32 keeps full precision'; 'More digits are accepted but cannot be stored' (float32 bounds preservation to ~7.2 significant decimal digits).
- **Contract citations (verbatim):**

> **bench/atcut-fit/CAL-CLI-SPEC.md:30**
>
>   `cal k=%.6g T0=%.2fC -> persisted (valid=yes)` (MyMesh.cpp:172-174);

> **bench/atcut-fit/CAL-CLI-SPEC.md:32-33**
>
> - Read-back command: `calshow` → `cal valid=%s k=%.6g T0=%.2fC range=+/-60C
>   die_temp=... off_hz=...` (MyMesh.cpp:178-181, CAL_RANGE_C at SelfCal.h:36).

> **bench/atcut-fit/CAL-CLI-SPEC.md:121-127**
>
> - Preservation is therefore bounded by float32 (~7.2 significant decimal
>   digits). [H] ulp comparison against correctly-rounded `strtof` for
>   cal-shaped values: `0.034021` exact match, `0.04` +1 ulp, `24.95` −1 ulp,
>   `0.04123456789012` exact (everything past ~7 digits is already below f32
>   resolution). ⇒ **6 significant digits for k and 2 decimals for T0 are
>   exactly sufficient** and match the firmware's own echo format `%.6g` /
>   `%.2f` (MyMesh.cpp:172). More digits are accepted but cannot be stored.

> **bench/atcut-fit/CAL-CLI-SPEC.md:128-129**
>
> - The echo/`calshow` display rounds to `%.6g`/`%.2f` — display only; the
>   stored f32 keeps full precision.

> **bench/atcut-fit/CAL-CLI-SPEC.md:188-191**
>
> Conforms to the fitter's emission format `cal %.6g %.2f` (fit_atcut.py /
> the fork's own bench kit): for the gated k band 0.005–0.15 ppm/°C² and any
> plausible T0, `%.6g` never emits an exponent and always keeps the leading
> digit, so the printed line is always parser-legal.

### 7. `pack_cal_blob`

- **Direction(s) covered:** float32 pair -> 15-byte little-endian blob (store direction), and bytes -> float32 pair (load direction, documented as a bit-identical round-trip)
- **Input -> output units:** in: k, T0 (float32), spare 0.0f, magic u16 0x5343, version byte -> out: 15-byte /selfcal.dat blob
- **Exact factor / offset (as documented):** memcpy, native (little-endian on all supported targets) - no numeric scaling; layout: k f32 LE @0, T0 f32 LE @4, spare 0.0f @8, magic 0x5343 LE -> bytes `43 53` @12, version byte 0 @14
- **Integer-vs-float semantics (as stated):** float32 -> 4 LE bytes each (k, T0); spare stored as f32 0.0f; magic u16 -> 2 LE bytes; version stored as integer byte, always 0. Load path checks length + magic only and round-trips both floats bit-identically.
- **Contract citations (verbatim):**

> **bench/atcut-fit/CAL-CLI-SPEC.md:133-137**
>
> `writeCalBlob(k, t0)` (MyMesh.cpp:270-281): `setCalibration(k, t0)` (:271,
> RAM-first — a later FS failure still leaves the new cal active, reply says
> "RAM only, file write failed"), then remove+rewrite `/selfcal.dat`
> (MAP_CAL_FILE, MyMesh.h:48; remove :273, open "w" :274, write :278, success
> = wrote exactly BLOB_SIZE :280).

> **bench/atcut-fit/CAL-CLI-SPEC.md:139-149**
>
> Blob = **15 bytes** (`SelfCal::BLOB_SIZE`, SelfCal.h:21), written by
> `storeCalibration` (SelfCal.h:65-73) via `memcpy` (native endianness — all
> supported targets nRF52/STM32/ESP32/RP2040 are little-endian):
> 
> | offset | size | field        | source                      |
> |--------|------|--------------|-----------------------------|
> | 0      | 4    | k, f32 LE    | SelfCal.h:66                |
> | 4      | 4    | T0, f32 LE   | SelfCal.h:67                |
> | 8      | 4    | spare = 0.0f | SelfCal.h:68-69             |
> | 12     | 2    | magic 0x5343 ('SC'), LE → bytes `43 53` | SelfCal.h:22, :70-71 |
> | 14     | 1    | version = `_ver` | SelfCal.h:72            |

> **bench/atcut-fit/CAL-CLI-SPEC.md:151-157**
>
> Version byte is always **0**: `_ver` starts 0 (SelfCal.h:39), `setVersion`
> exists (SelfCal.h:157) but is **never called anywhere in the example**
> (grep over examples/passive_mapper @ 3fdfbc8e: zero call sites), and
> `loadCalibration` (SelfCal.h:48-63) only propagates a ver that was itself 0.
> Load path checks length + magic only (SelfCal.h:49, :57), then seeds the
> thermal EMA with T0 (`_temp_ema = T0`, SelfCal.h:60) — another confirmation
> T0 is plain °C.

> **bench/atcut-fit/CAL-CLI-SPEC.md:164-165**
>
>     reload: loadCalibration() round-trips both floats bit-identically,
>             cold-start EMA = T0 = 24.95 C

### 8. `k_to_milliunits_display`

- **Direction(s) covered:** float32 k -> boot-debug display integers (display-only direction)
- **Input -> output units:** in: k (ppm/degC^2, float32) -> out: milli-units, printed as `%d.%03d`
- **Exact factor / offset (as documented):** x1000 (milli-units)
- **Integer-vs-float semantics (as stated):** float32 x 1000 rendered via integer printf fields `k=%d.%03d`; 'display scaling only, not storage'. The rounding rule for the integer split is NOT stated - see Gaps G6.
- **Contract citations (verbatim):**

> **bench/atcut-fit/CAL-CLI-SPEC.md:167-170**
>
> Boot-time cross-check: `begin()` loads the blob and debug-prints
> `selfcal: loaded cal blob (k=%d.%03d T0=%d.%02d)` — k printed in
> milli-units (×1000), T0 in centi-degrees (×100) — display scaling only,
> not storage (MyMesh.cpp:60-69).

### 9. `t0_to_centidegrees_display`

- **Direction(s) covered:** float32 T0 -> boot-debug display integers (display-only direction)
- **Input -> output units:** in: T0 (degC, float32) -> out: centi-degrees, printed as `%d.%02d`
- **Exact factor / offset (as documented):** x100 (centi-degrees)
- **Integer-vs-float semantics (as stated):** float32 x 100 rendered via integer printf fields `T0=%d.%02d`; 'display scaling only, not storage'. The rounding rule for the integer split is NOT stated - see Gaps G6.
- **Contract citations (verbatim):**

> **bench/atcut-fit/CAL-CLI-SPEC.md:167-170**
>
> Boot-time cross-check: `begin()` loads the blob and debug-prints
> `selfcal: loaded cal blob (k=%d.%03d T0=%d.%02d)` — k printed in
> milli-units (×1000), T0 in centi-degrees (×100) — display scaling only,
> not storage (MyMesh.cpp:60-69).

#### Documented items deliberately NOT counted as conversions

Considered and excluded - documented in the contract, but they transform no units:

- **Semantic gate `k >= 0.0f` (validation, not a conversion; no upper bound on k, no constraint at all on T0)**

> **bench/atcut-fit/CAL-CLI-SPEC.md:105-109**
>
> - **Semantic gate**: `k >= 0.0f` (MyMesh.cpp:170). Negative k → usage [H].
>   No upper bound on k, **no constraint at all on T0** (any sign/magnitude
>   accepted; also accepted after a prior blob load — `setCalibration` never
>   validates, SelfCal.h:44-46, it just sets `_cal_valid = true`). Even
>   `cal 0 25` marks the cal "valid" with zero compensation [H: -0 case].

- **Validity band |T_die - T0| <= 60 degC with BW125 fallback outside it (a range predicate, not a conversion; CAL-COMMAND.md notes the band widens to 90 degC in post-pin commit d83b3660 - outside this contract)**

> **bench/atcut-fit/CAL-CLI-SPEC.md:199-203**
>
> range=+/-60C die_temp=... off_hz=...` (MyMesh.cpp:178-181). Note the
> calibrated band is |T_die − T0| ≤ 60 °C (SelfCal.h:36, :136-141) — outside
> it the firmware falls back to BW125 and holds the last offset
> (MyMesh.cpp:356-371), which is why T0 should be the fitted vertex, not an
> arbitrary midpoint.

- **Thermal EMA seeded with T0 (`_temp_ema = T0`, plain assignment of same-unit value; the EMA recurrence itself is NOT in the contract - see Gaps G9)**

> **bench/atcut-fit/CAL-CLI-SPEC.md:155-157**
>
> Load path checks length + magic only (SelfCal.h:49, :57), then seeds the
> thermal EMA with T0 (`_temp_ema = T0`, SelfCal.h:60) — another confirmation
> T0 is plain °C.

## Gaps

Conversions a reasonable engineer would expect that the contract does NOT
state. Gaps are NEVER to be implemented; they are recorded for review only.

- **G1 `gaps_raw_counts_to_ppm`** - raw counts <-> ppm: no counts-domain conversion is documented anywhere in the contract (verified: 'raw' has zero occurrences; the only 'count' hit is 'decimal-count limit' at CAL-CLI-SPEC.md:118, about digit counts; 'ADC' occurs only as a substring of 'loadCalibration' at :154/:164), while the parent work item explicitly names the raw-counts domain (t_3bd737f9 body: 'Hz <-> ppm <-> raw counts').
- **G2 `gaps_hz_to_ppm`** - Hz -> ppm: only ppm -> Hz (`offset_hz = ppm * freq_MHz`) is documented (CAL-CLI-SPEC.md:102-103); the inverse direction is never stated.
- **G3 `gaps_offset_ppm_to_temp`** - offset_ppm -> temperature (solving T from a measured offset): only degC -> ppm (`offset_ppm = -k*(T-T0)^2`, CAL-CLI-SPEC.md:99-101) is documented; the inverse is never stated.
- **G4 `gaps_parse_scale_init`** - Initial fraction-scale constant for `v += digit * scale; scale *= 0.1f` (CAL-CLI-SPEC.md:120): the contract quotes the accumulation but never states the initial value of `scale` at the start of the fraction loop.
- **G5 `gaps_freq_mhz_value`** - Value/source of `freq_MHz` in `offset_hz = ppm * freq_MHz` (CAL-CLI-SPEC.md:102-103): the conversion is documented but the carrier-frequency constant and where it comes from are not stated.
- **G6 `gaps_display_int_rounding`** - Rounding rule for the boot-display integer split `k=%d.%03d` / `T0=%d.%02d` (CAL-CLI-SPEC.md:167-170): factors x1000/x100 are stated but how the product becomes the printed integers (truncate vs round) is not.
- **G7 `gaps_clamp_ordering`** - Ordering of the +/-300 ppm clamp (CAL-CLI-SPEC.md:94-95) relative to the ppm->Hz conversion (CAL-CLI-SPEC.md:102-103): the contract does not state whether the clamp applies to offset_ppm only, or also to offset_hz.
- **G8 `gaps_display_scale_inverse`** - Inverse of the boot-display scalings (milli-units -> k, centi-degrees -> T0): not documented; only the display direction exists (CAL-CLI-SPEC.md:167-170).
- **G9 `gaps_temp_ema_recurrence`** - die-temp EMA update (recurrence/time-constant converting successive die-temp samples into `_temp_ema`): the contract only documents the seed `_temp_ema = T0` (CAL-CLI-SPEC.md:155-157); the EMA conversion itself is absent.

---

End of inventory: 9 conversions, 3 documented non-conversions, 9 gaps.
