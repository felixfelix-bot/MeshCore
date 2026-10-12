# PINNED REPORT — `cal <k> <T0>` serial CLI syntax in MeshCore `passive_mapper`

## 0. Revision pin (do not drift)

| item | value |
|---|---|
| repo | `felixfelix-bot/MeshCore` (the code repo behind the requested `meshcore-fork-fix` workspace) |
| branch | `feat/passive-mapper` |
| commit | `3fdfbc8e120e13d7543fe224c380e27533e720aa` |
| subject | `feat(passive_mapper): BW125 runtime fallback, cal-range predicate, cal-blob writer` |
| `git rev-parse HEAD` | `3fdfbc8e120e13d7543fe224c380e27533e720aa` (detached checkout) |
| working dir of interest | `examples/passive_mapper` |
| clone used | `/home/c03rad0r/worktrees/cal-serial-pin` |

Every citation below is valid **at 3fdfbc8e and only at 3fdfbc8e**. The remote
branch tip has since moved (`git ls-remote … refs/heads/feat/passive-mapper` =
`d7ae93fa1d0f71fa704d59c801351c28c3d9020a`), so this pin must be used explicitly.

**Workspace caveat (honest):** the requested workspace
`/home/c03rad0r/repos/meshcore-fork-fix` is **unusable at this revision**: its object
store is damaged (`git fetch` → `fatal: pack has 50 unresolved deltas`,
`error: Could not read ecd30f4d…`), 90 tracked files are deleted from its working
tree, and `git rev-parse 3fdfbc8e` there fails with `malformed object name`.
Work was therefore done in a fresh clone (`/home/c03rad0r/worktrees/cal-serial-pin`)
checked out at the same SHA. A copy of this report is also left at the requested
workspace path.

---

## 1. Full dispatch + persistence chain (file:line @ 3fdfbc8e)

There is **no command table** for this CLI. Dispatch is an `if/else` `strcmp`
chain in `MyMesh::handleCommand`; `cal` is one branch of it.

| # | what | location | verbatim source line |
|---|---|---|---|
| a | serial line reader → dispatch | `examples/passive_mapper/main.cpp:88` | `    the_mesh.handleCommand(command, reply);` |
| a | dispatch entry (no table; if/else chain) | `examples/passive_mapper/MyMesh.cpp:145` | `void MyMesh::handleCommand(char* cmd, char* reply) {` |
| a | **`cal` command-table-equivalent entry** | `examples/passive_mapper/MyMesh.cpp:166` | `  } else if (strncmp(cmd, "cal ", 4) == 0) {` |
| b | argument parser (custom primitive) | `examples/passive_mapper/MyMesh.cpp:128-143` | `static bool parseFloat(const char* s, const char** endp, float* out) {` |
| b | parser invocation for `k` and `T0` | `examples/passive_mapper/MyMesh.cpp:170` | `    if (parseFloat(p, &p, &k) && parseFloat(p, nullptr, &t0) && k >= 0.0f) {` |
| b | token pointer setup | `examples/passive_mapper/MyMesh.cpp:169` | `    const char* p = cmd + 4;` |
| c | call into the blob writer | `examples/passive_mapper/MyMesh.cpp:171` | `      bool ok = writeCalBlob(k, t0);` |
| c | blob writer definition | `examples/passive_mapper/MyMesh.cpp:270` | `bool MyMesh::writeCalBlob(float k, float t0) {` |
| c | blob writer declaration | `examples/passive_mapper/MyMesh.h:166` | `  bool writeCalBlob(float k, float t0);` |
| d | blob field assignments | `examples/passive_mapper/host/SelfCal.h:65-73` | `  void storeCalibration(uint8_t* blob) const {` |
| d | blob assignment call site | `examples/passive_mapper/MyMesh.cpp:277` | `  _selfcal.storeCalibration(blob);` |
| e | final flash/FS write | `examples/passive_mapper/MyMesh.cpp:273-280` | `  _fs->remove(MAP_CAL_FILE);                 // avoid appending to an old blob` … `  return n == SelfCal::BLOB_SIZE;` |
| e | storage path (a plain file, **not** NVS) | `examples/passive_mapper/MyMesh.h:48` | `#define MAP_CAL_FILE        "/selfcal.dat"` |
| — | load-at-boot of the same file | `examples/passive_mapper/MyMesh.cpp:59-73` | `    File f = _fs->open(MAP_CAL_FILE, "r");` |
| — | FS type mapping | `src/helpers/IdentityStore.h:5` | `  #define FILESYSTEM  fs::FS` (ESP32/RP2040, `FS.h`) |

Verbatim handler body (`examples/passive_mapper/MyMesh.cpp:166-177`):

```cpp
  } else if (strncmp(cmd, "cal ", 4) == 0) {
    // Persist a bench-derived calibration: cal <k> <T0>   (k in ppm/C^2, T0 in C)
    float k = 0.0f, t0 = 0.0f;
    const char* p = cmd + 4;
    if (parseFloat(p, &p, &k) && parseFloat(p, nullptr, &t0) && k >= 0.0f) {
      bool ok = writeCalBlob(k, t0);
      snprintf(reply, 160, "cal k=%.6g T0=%.2fC -> %s (valid=%s)",
               k, t0, ok ? "persisted" : "RAM only, file write failed",
               _selfcal.isCalValid() ? "yes" : "no");
    } else {
      snprintf(reply, 160, "usage: cal <k_ppm_per_C2> <T0_C>");
    }
```

Verbatim blob writer (`examples/passive_mapper/MyMesh.cpp:270-281`):

```cpp
bool MyMesh::writeCalBlob(float k, float t0) {
  _selfcal.setCalibration(k, t0);
  if (!_fs) return false;
  _fs->remove(MAP_CAL_FILE);                 // avoid appending to an old blob
  File f = _fs->open(MAP_CAL_FILE, "w", true);
  if (!f) return false;
  uint8_t blob[SelfCal::BLOB_SIZE];
  _selfcal.storeCalibration(blob);
  size_t n = f.write(blob, SelfCal::BLOB_SIZE);
  f.close();
  return n == SelfCal::BLOB_SIZE;
}
```

---

## 2. Pinned grammar

### 2.1 Token order — `cal <k> <T0>` (k FIRST)

Justified by `MyMesh.cpp:169-170`: the pointer after the literal `"cal "` is fed
to the **first** `parseFloat`, which writes `k`; the **second** `parseFloat`
writes `t0`. The usage string says the same thing
(`MyMesh.cpp:176`, verbatim):
`      snprintf(reply, 160, "usage: cal <k_ppm_per_C2> <T0_C>");`

No named/keyed form exists: the parser is purely positional. `cal 21.5 12.345`
would silently calibrate with k=21.5, T0=12.345 — it is *not* rejected.

### 2.2 Separators and the literal prefix

* The command must begin with the exact 4 bytes `c`,`a`,`l`,`0x20` — `strncmp(cmd, "cal ", 4)`
  (`MyMesh.cpp:166`). `cal` alone, `cal\t…`, or `cal:…` does **not** match this
  branch; they fall through to the generic listing at `MyMesh.cpp:183`
  (`"commands: status, mode, flush, reset, erase, cal <k> <T0>, calshow"`).
* Between `cal` and the first number, and between the two numbers, **one or more
  spaces or tabs** are accepted — `parseFloat` skips them itself
  (`MyMesh.cpp:129`, verbatim): `  while (*s == ' ' || *s == '\t') s++;`
  So `cal   12   21` is valid; but the space after `cal` is mandatory because of
  the literal prefix (a tab there fails).

### 2.3 Parsing primitive / format specifier

**Custom hand-rolled parser, not `sscanf`, `strtod`, `strtof` or `atoi`.** The
source states the reason verbatim (`MyMesh.cpp:125-127`):

```cpp
// Minimal decimal float parser for the CLI. Deliberately avoids sscanf("%f")/
// strtof: the scanf float machinery costs ~16 KB of flash in this image, which
// is not worth it for two calibration numbers. Accepts [-+]?digits[.digits].
```

Full primitive (`examples/passive_mapper/MyMesh.cpp:128-143`, verbatim):

```cpp
static bool parseFloat(const char* s, const char** endp, float* out) {
  while (*s == ' ' || *s == '\t') s++;
  bool neg = false;
  if (*s == '-') { neg = true; s++; } else if (*s == '+') { s++; }
  if (*s < '0' || *s > '9') return false;
  float v = 0.0f;
  while (*s >= '0' && *s <= '9') { v = v * 10.0f + (float)(*s - '0'); s++; }
  if (*s == '.') {
    s++;
    float scale = 0.1f;
    while (*s >= '0' && *s <= '9') { v += (float)(*s - '0') * scale; scale *= 0.1f; s++; }
  }
  *out = neg ? -v : v;
  if (endp) *endp = s;
  return true;
}
```

Consequences (all derivable from the lines above):

* accepted lexical form: `[-+]?[0-9]+(.[0-9]+)?` — optional sign, **at least one
  digit before** any `.` (`:132` rejects a string starting with `.`), optional
  single fraction part.
* numeric type: **`float`** (32-bit) accumulation; the value is stored as
  `float` (`MyMesh.cpp:170`, `SelfCal.h:66-67`). Not fixed-point, not integer.
* **no hex**: `0x10` parses as `0` (the `x` stops the digit loop); there is no
  `0x` handling anywhere in the primitive.
* **no exponent**: `1e3` parses as `1` (the `e` stops the loop); for the real
  command this is harmless for `k` but fatal for the pair — e.g. `cal 1.2e-3 21`
  leaves `e-3 21` for the `T0` parse, which finds no digit and fails
  (`MyMesh.cpp:132`) → usage error.
* a trailing `.` (`12.`) is accepted (the `.` is consumed, zero fraction digits).
* `parseFloat` returns a bool; a `false` result is the only "not a number"
  signal (it never reports overflow/NaN; there is no range check inside it).

### 2.4 Units and scaling

* **`k` is in ppm/°C² and `T0` is in °C — engineering units, no internal
  conversion on parse or on store.** The heap of evidence:
  * the handler comment (`MyMesh.cpp:167`):
    `    // Persist a bench-derived calibration: cal <k> <T0>   (k in ppm/C^2, T0 in C)`
  * the usage string (`MyMesh.cpp:176`): `usage: cal <k_ppm_per_C2> <T0_C>`
  * the blob is a raw `memcpy` of the two floats — **no multiplier is applied**
    (`SelfCal.h:66-67`).

    ```cpp
      memcpy(blob, &_k, 4);
      memcpy(blob + 4, &_T0, 4);
    ```
  * the only arithmetic involving `k` is the model itself
    (`SelfCal.h:89`): `float raw = -_k * (_temp_ema - _T0) * (_temp_ema - _T0);`
  * the ppm→Hz conversion happens **downstream of the model**, on the model's
    output, not on the parsed `k` (`MyMesh.cpp:386`):
    `  float offset_hz = ppm * (_nominal_freq_mhz * 1.0f); // ppm * MHz = Hz`

  There is **no `1e3`/`1e6` scaling** applied to `k` or `T0` at parse, at store,
  or at write. Byte-identical float32 values are what land on flash.

### 2.5 Precision, rounding, truncation

* The parser **does not truncate the user's decimal digits** — it consumes all
  of them (`:137-138`) and round-accumulates into a `float`; the effective
  precision is that of IEEE-754 binary32 (≈7 significant decimal digits;
  e.g. `cal 12.345 …` yields k ≈ 12.3450002669…).
* No explicit rounding step, no `floor`/`round`, and no deadband at parse time.
* The reply echoes `k` as `%.6g` and `T0` as `%.2f`
  (`MyMesh.cpp:172-173`), and `calshow` echoes `k=%.6g T0=%.2fC`
  (`MyMesh.cpp:179`). **Use ≤6 significant digits for `k` and ≤2 decimals for
  `T0`** so the echoed values round-trip visibly. Anything finer is representable
  but not displayed.

### 2.6 Range / tolerance checks that can reject the value

Exactly **one** acceptance predicate on the numbers
(`MyMesh.cpp:170`): `… && k >= 0.0f`.

* Rejection happens when: (i) no numeric `k` token (incl. `k` starting `.`);
  (ii) no numeric `T0` token; (iii) `k < 0.0f`. All three produce the single
  reply `usage: cal <k_ppm_per_C2> <T0_C>` (`MyMesh.cpp:176`).
* **No upper bound on `k`**, no bound at all on `T0` (negative `T0` is accepted —
  mirrored by the unit test `host/tests/test_self_cal.cpp:152`,
  `cal.setCalibration(0.037f, -12.5f);`). Over-large `k` is not rejected; it
  simply saturates at runtime under the model clamp `MAX_PPM = 300.0f`
  (`SelfCal.h:30`, applied at `SelfCal.h:91-92` and `:107-108`).
* A *runtime* validity band exists but does **not** affect acceptance:
  `|T - T0| <= CAL_RANGE_C` with `CAL_RANGE_C = 60.0f`
  (`SelfCal.h:36`, predicate `SelfCal.h:136-141`). Outside it the firmware keeps
  the last offset and drops to BW125 instead of trusting the parabola
  (`MyMesh.cpp:356-371`). It is a compensation-trust limit, not a CLI check.

### 2.7 Line terminator, max argument count, trailing bytes

Terminator — **CR (`0x0D`) is required**; LF-only **never dispatches**.
Verbatim reader (`examples/passive_mapper/main.cpp:70-83`):

```cpp
  while (Serial.available() && len < (int)sizeof(command)-1) {
    char c = Serial.read();
    if (c != '\n') {
      command[len++] = c;
      command[len] = 0;
      Serial.print(c);
    }
    if (c == '\r') break;
  }
  if (len == (int)sizeof(command)-1) {  // command buffer full
    command[sizeof(command)-1] = '\r';
  }

  if (len > 0 && command[len - 1] == '\r') {  // received complete line
```

* `\r\n` works: `\r` appends + breaks (`:72-77`), the later `\n` is swallowed by
  `:72` and never starts a command.
* bare `\r` works.
* bare `\n` does nothing but sit in the buffer — the dispatch test at `:83`
  requires `'\r'`, so an LF-terminated line is only ever executed if it grows to
  fill the 160-byte buffer (see below). **Do not use LF-only.**

Argument count / buffer bounds:

* no argument-count limit is enforced; **extra tokens after `T0` are silently
  ignored** — the second `parseFloat` is called with `endp == nullptr`
  (`MyMesh.cpp:170`) and stops at the first non-digit, and its result is not
  checked against end-of-string.
* the line buffer is `static char command[160];` (`main.cpp:15`) → max 159
  payload bytes plus terminator. If it fills, `command[159]` is force-set to
  `'\r'` (`main.cpp:79-81`) and the **truncated** line is executed anyway.
* trailing whitespace after `T0` is tolerated (ignored, same reason as extra
  tokens); trailing whitespace before numbers is skipped (`MyMesh.cpp:129`).

---

## 3. Sign convention and internal scaling of the blob

* **The caller supplies a POSITIVE magnitude `k`; the firmware negates it in the
  model.** The handler enforces the sign (`MyMesh.cpp:170`): `… && k >= 0.0f`;
  the model applies the minus (`SelfCal.h:89`):
  `    float raw = -_k * (_temp_ema - _T0) * (_temp_ema - _T0);`
  i.e. `offset_ppm = -k * (T - T0)^2` (also stated at `MyMesh.cpp:15` and
  `SelfCal.h:2`). Passing a negative `k` is rejected with the usage reply —
  so a signed coefficient cannot be expressed through this CLI.
* **No negation, scaling or clamping of `k`/`T0` occurs before the write.**
  `SelfCal::setCalibration` stores them verbatim (`SelfCal.h:44-46`):
  `  void setCalibration(float k, float T0) {\n    _k = k; _T0 = T0; _cal_valid = true;\n  }`
  and `storeCalibration` (`SelfCal.h:65-73`) `memcpy`s them as raw float32:
  `k` at bytes 0-3, `T0` at bytes 4-7, a spare float `0.0f` at bytes 8-11,
  `uint16_t magic = CAL_MAGIC` (`0x5343`, `'SC'`) at bytes 12-13, version byte
  `_ver` at byte 14.
* `BLOB_SIZE = 3 * 4 + 2 + 1; // 15 bytes` (`SelfCal.h:21`). Note the version
  byte is `0` unless `setVersion()` was called (`SelfCal.h:39` ctor default,
  `:157` setter) — `cal` never calls it, so it writes `0`.
* Clamping happens **downstream, in the model, on the computed offset only**:
  `MAX_PPM = 300.0f` (`SelfCal.h:30`, applied `:91-92`, `:107-108`),
  `SLEW_PPM = 25.0f` per update (`:28`, applied `:96-97`),
  `DEADBAND_PPM = 1.0f` (`:29`, `:101-102`). None of these reject or alter the
  value at CLI/store time.

---

## 4. Persistence — **YES, immediate; no follow-up command is needed**

* The `cal` handler itself performs the write synchronously: `writeCalBlob(k, t0)`
  (`MyMesh.cpp:171`) → `_fs->remove(MAP_CAL_FILE)` (`:273`) →
  `_fs->open(MAP_CAL_FILE, "w", true)` (`:274`) → `f.write(blob, 15)` (`:278`) →
  `f.close()` (`:279`) → success only if `n == SelfCal::BLOB_SIZE` (`:280`).
* The handler reports it to the operator and is the firmware's own contract for
  "committed": `snprintf(reply, 160, "cal k=%.6g T0=%.2fC -> %s (valid=%s)", k, t0,
  ok ? "persisted" : "RAM only, file write failed", …)` (`MyMesh.cpp:172-174`).
* The file loaded at boot is the same one it wrote — durable-store proof
  (`MyMesh.cpp:59-73`, verbatim):
  `    File f = _fs->open(MAP_CAL_FILE, "r");`
  and `MyMesh.h:48`: `#define MAP_CAL_FILE        "/selfcal.dat"`.
* There is **no** `save`, `commit`, `write` or `nvs commit` command in this CLI.
  The complete command list is `MyMesh.cpp:183`:
  `  snprintf(reply, 160, "commands: status, mode, flush, reset, erase, cal <k> <T0>, calshow");`
* There is **no NVS / Preferences / prefs usage anywhere in
  `examples/passive_mapper`** (`git grep -ni 'nvs\|preferences\|prefs' 3fdfbc8e -- examples/passive_mapper` → 0 hits). The
  store is a flat file on the platform filesystem (`FILESYSTEM* _fs`, wired in
  `main.cpp:30-46`: SPIFFS on ESP32, LittleFS on RP2040, InternalFS on
  NRF52/STM32; `FILESYSTEM` = `fs::FS` per `src/helpers/IdentityStore.h:5`).

### Caveats that are genuinely not determinable from source

* `writeCalBlob` calls `f.close()` but **no `flush()`/`sync()`**; whether
  `File::close()` itself commits the data to flash is **not determinable from
  source** at 3fdfbc8e — `File` is the platform SDK type (`using File = fs::File;`
  on ESP32, `MyMesh.h:17`), not in-tree. The same write-then-close pattern is
  used for every other persistent artifact in this repo (e.g.
  `src/helpers/CommonCLI.cpp:150`, `src/helpers/IdentityStore.cpp:55`).
* The semantics of the third argument `true` in `_fs->open(MAP_CAL_FILE, "w", true)`
  are likewise **not determinable from source** (platform SDK). The same 3-arg
  form is used tree-wide, e.g. `examples/companion_radio/DataStore.cpp:41`:
  `  return fs->open(filename, "w", true);`.
* Failure window visible in source: `:273` removes the existing blob *before*
  `:274` opens the new one, so a failing write leaves **no** blob on flash; the
  in-RAM calibration stays valid until reset, and the reply says
  `RAM only, file write failed` (`:173`). Therefore: **require the reply to
  contain `persisted` (and `valid=yes`) as the success criterion.**

---

## 5. Byte-exact command template

Grammar, quoted from the parser:

```
cal␠<k: [-+]?[0-9]+([.][0-9]+)?>␠<T0: [-+]?[0-9]+([.][0-9]+)?>\r
```

* `cal␠` — literal 4 bytes incl. `0x20` (`MyMesh.cpp:166`).
* `k` — first number, **ppm/°C²**, must satisfy `k >= 0.0f` (`:170`); ≤6
  significant digits so the `%.6g` echo round-trips (`:172`).
* separator — one or more spaces or tabs (`:129`).
* `T0` — second number, **°C**, sign allowed (`:131`), may be negative.
* terminator — **CR `0x0D`** (`main.cpp:77`, `:83`); `\r\n` also works (the `\n`
  is swallowed at `main.cpp:72`); LF-only does **not** dispatch.

Concrete, quotable instances (identical numbers to the repo's own unit test
`host/tests/test_self_cal.cpp:152`, `cal.setCalibration(0.037f, -12.5f);`):

```
cal 0.037 -12.5\r\n
cal 0.037 -12.5\r
```

Generic instance with a mid-range bench value:

```
cal 12.345 21.5\r\n
```

Echoed reply on success (`MyMesh.cpp:172-173` format string, with `%.6g`/`%.2f`):

```
cal k=0.037 T0=-12.50C -> persisted (valid=yes)
```

---

## 6. Items marked `not determinable from source`

1. Whether `File::close()` (platform SDK, `MyMesh.h:17` / `IdentityStore.h:5`)
   issues the flash commit / fsync — `not determinable from source` at 3fdfbc8e.
2. The exact semantics of the third `open()` argument `true` (create-if-missing?)
   — `not determinable from source` at 3fdfbc8e; only its call-site usage is
   observable (tree-wide pattern).
3. Byte order of the stored floats is the host's native endianness (`memcpy` of a
   `float`, `SelfCal.h:66-67`); the endianness of the MCU is not asserted in-tree
   for every target — `not determinable from source` for non-little-endian targets.
4. The physical serial transport framing (baud 115200 set at `main.cpp:18`) and
   any USB-CDC echo translation — the firmware-level expectation is exactly the
   `\r`-terminated byte sequence above; anything the transport adds or strips is
   `not determinable from source`.

---

## 7. Method / verification

* Clone: `git clone https://github.com/felixfelix-bot/MeshCore.git` →
  `/home/c03rad0r/worktrees/cal-serial-pin`, then `git checkout 3fdfbc8e`
  (`git rev-parse HEAD` = `3fdfbc8e120e13d7543fe224c380e27533e720aa`).
* Greps run against the pinned tree with `git grep … 3fdfbc8e -- <path>` for:
  `"cal `, `calshow`, `selfcal.dat`, `writeCalBlob`, `CalBlob`, `parseFloat`,
  `tempCal`, `nvs|preferences|prefs`, `FILESYSTEM`, `flush()`, `"w", true`.
* Every line quoted above is re-extracted from `git show 3fdfbc8e:<path>` by
  `analysis/passive-mapper-cal-cli/verify_citations.py`; see
  `verify_citations.out` in the same directory for the PASS/FAIL transcript.
