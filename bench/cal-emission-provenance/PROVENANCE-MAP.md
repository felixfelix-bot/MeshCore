# Cal-emission provenance map — conversion work item + every `cal <k> <T0>` builder

Task card: **n4s-t_b23c606a** "Locate conversion work item and all cal-emission
sites (provenance map)" (backlog). Board: **Meshcore Board**
(`meshcore-board`, creator `npub1ux9p69c6t8v8fmwnxerj4l4n5c2d8hyr897ap9lfy25emnhqyyes7wxnqk`,
500 cards). Board data read via `kanbanstr-cli board show` / `card list` this
session 2026-09-15. Repo: `/home/c03rad0r/repos/meshcore`, branch `main`
@ `abe0d36f` + dangling fork commit `d7ae93fa` (and pinned ancestor
`3fdfbc8e`) present in the same object store.

This map is a SOURCE INVENTORY (hunting, not validating). Every claim below
has a location. Later tasks cite these IDs.

---

## (a) Board work-item references

`kanbanstr-cli card list --board-pubkey npub1ux9p… --board-id meshcore-board`
exposes only Title / ID / Status / Rank — no card body, no link fields. No
card on this board carries a linked PR/branch/commit sha via the CLI; the
emitter work landed as direct commits to `main` (listed per card below).
Searches run: `board list | grep -iE 'meshcore|atcut|fit|cal|freq|clock|tcxo'`
(1119 boards → only `meshcore-board` matches), then `card list` piped through
`grep -iE 'cal|atcut|T0|fit|emit|provenance'`, `grep -iE 'convert'`, and
`grep -iE 'parabola|fitted'` over all 500 cards.

### The conversion work items (emit `cal <k> <T0>` literals)

| ID | Title | Status |
|---|---|---|
| n4s-t_91f4019e | Convert fitted k/T0 into parser literal strings | backlog |
| n4s-t_2656f57c | Convert fitted k/T0 into parser representation | backlog |
| n4s-t_0017d836 | Inventory all candidate `cal <k> <T0>` literals from the conversion task and plan | backlog |
| n4s-t_291d4094 | Assemble final cal <k> <T0> deliverable with caveats | backlog |
| n4s-t_2e041ab8 | Verify literal cal string character-by-character against parser | backlog |

### Upstream cards the conversion consumes (their outputs ARE the emitters)

| ID | Title | Status | Committed output (this repo, `main`) |
|---|---|---|---|
| n4s-t_3f930320 | Fit AT-cut parabola constants (k, T0) from freezer-sweep CSV | done | ab17ec5b, a8017b27, 2075f921, c7cdf306, a9d72654 — bench/atcut-fit/ (fit_atcut.py emitter, REPORT.md, CAL-CLI-SPEC.md, CAL-COMMAND.md, cal_cli_harness.cpp, verify_cal_domain.py) |
| n4s-t_d6484f25 | Document serial `cal <k> <T0>` parser contract with file:line citations | done | 2075f921 (CAL-CLI-SPEC.md) |
| n4s-t_c11f2cbe | Pin exact `cal <k> <T0>` serial CLI syntax in MeshCore passive_mapper | done | cited pin: felixfelix-bot/MeshCore feat/passive-mapper @ 3fdfbc8e |
| n4s-t_8f776e31 | Re-derive `cal <k> <T0>` parser contract from firmware source, cited | backlog | none yet (re-derivation pending) |

### Sibling cards in this provenance cluster

| ID | Title | Status |
|---|---|---|
| n4s-t_f11477d5 | Assemble flat candidate cal-literal list with bytes, provenance, intent | backlog |
| n4s-t_c260596e | Extract plan intent and no-fit branch behavior for cal emission | backlog |
| n4s-t_c45f7bc1 | Enumerate code-level cal literal variants (>=8 byte forms) | backlog |

### Dispatch state of the conversion cards (checked, not assumed)

- t_2656f57c WAS dispatched once: session `20260914_194259_6b43c6`
  (2026-09-14, this profile's session DB). Its card body was recovered
  verbatim (quoted in §(c)-5). That run was interrupted BEFORE building any
  artifact; `git log --all --oneline | grep -iE 'convert|literal|representation|rounding'`
  → zero conversion commits. No deliverable exists yet.
- t_91f4019e: no dispatch session found
  (`session_search "parser literal strings" cal emit` → 0 hits), no commit.
  Status on board still `backlog` for both.

---

## (b) Emission sites, ordered

Scope swept: every ref reachable from `main` (local + all `origin/*`:
dev, default-scope, feature/nicerf-lr2021-variant, fix/2739-review-fixes,
flood.max.advert, gh-pages, t-impulse-ui) via
`git grep -nE '"cal %|cal_command|%.6g' $(rev-list --all --max-count=400)` —
matches in exactly 7 files, all listed below; plus dangling fork commit
`d7ae93fa` (git fsck: the ONLY dangling commit) and its pinned ancestor
`3fdfbc8e`. Greps run (verbatim): `grep -rn 'cal %' .`,
`grep -rn '%\.6g' .`,
`grep -rn 'cal_command\|verify_command\|pack_blob\|emit' --include='*.py' bench/`,
`grep -rn 'cal ' bench/ --include='*.py' --include='*.cpp'`,
`git grep -nE '"cal %|cal_command|%.6g' d7ae93fa -- examples/passive_mapper/`,
`git grep -nE '"cal %|"cal |cal_command' HEAD -- src examples test`.

Language legend: PY = Python 3, C++ = firmware/harness C++.

### A. In this repo (reachable from main)

1. **bench/atcut-fit/fit_atcut.py:154-157** — PY, `cal_command(k, t0)`.
   THE canonical repo emitter; this is where the conversion
   (fitted float k/T0 → literal wire string) happens.
   ```python
   def cal_command(k, t0):
       """Exact format: firmware reply echoes k=%.6g T0=%.2f; the fork's own bench
       kit (bench/calib.py::cal_command) emits `cal %.6g %.2f`."""
       return "cal %.6g %.2f" % (k, t0)
   ```

2. **bench/atcut-fit/fit_atcut.py:389-393** — PY, `report()` — the dispatch:
   emits the line after all fit gates pass; prints it verbatim
   (no trailing `\r` is appended here; the CR is a wire-framing detail).
   ```python
   cmd = cal_command(res["k"], res["t0"])
   ...
   print("    " + cmd)
   ```

3. **bench/atcut-fit/fit_atcut.py:400-402** — PY, no-fit branch (the
   anti-emitter the conversion card t_c260596e targets):
   `"VERDICT: DO NOT ISSUE cal — data does not support a clean parabola
   (see FAIL checks above). No command emitted."`

4. **bench/atcut-fit/fit_atcut.py:396** — PY, expected-firmware-reply render
   (echo side, not a wire emitter):
   `"cal k=%.6g T0=%.2fC -> persisted (valid=yes)" % (res["k"], res["t0"])`.

5. **bench/atcut-fit/fit_atcut.py:430** — PY, self-test call:
   `verify_command(cal_command(res["k"], res["t0"]), res["k"], res["t0"])`.

6. **bench/atcut-fit/verify_cal_domain.py:25,62-63** — PY, domain proof:
   renders 481,601 candidate lines via the same builder
   (`from fit_atcut import K_PLAUSIBLE, cal_command, verify_command`;
   `cmd = cal_command(k, t0)` / `ok, detail = verify_command(cmd, k, t0)`).
   Renders only — never issues.

7. **bench/atcut-fit/verify_cal_domain.py:86,90** — PY, token round-trip
   value renders (`float("%.6g" % k)`, `float("%.2f" % t0)`) feeding the
   grammar regex checks; also :32 the K_TOKEN/T0_TOKEN `%.6g`/`%.2f` shape
   regexes.

8. **bench/atcut-fit/cal_cli_harness.cpp:64-79** — C++,
   `handleCommandMock()` — VERBATIM copy of the firmware cal branch
   (`strncmp(cmd, "cal ", 4) == 0`), the reply/usage/help snprintf's
   (`"cal k=%.6g T0=%.2fC -> %s (valid=%s)"`, `"usage: cal <k_ppm_per_C2>
   <T0_C>"`, `"commands: ... cal <k> <T0>, calshow"`). CONSUMER replica
   (parser side), documents the format every emitter must satisfy.

9. **bench/atcut-fit/cal_cli_harness.cpp:120-146** — C++ test vectors:
   literal `cal` line strings exercising the parser
   (`run("cal 0.034021 24.95", true)`, `run("cal .04 25", false)`, …).

10. **bench/atcut-fit/cal_cli_harness.cpp:200-205** — C++ wire-framing
    vectors (`"cal 0.04 25\r"` executes; `"cal 0.04 25\n"` never executes).

11. **bench/dryrun-ambient/sample_calshow.py:190,193** — PY parser FIXTURES
    (not emitters): help line
    `"  -> commands: status, mode, flush, reset, erase, cal <k> <T0>, calshow"`
    and `"  -> usage: cal <k_ppm_per_C2> <T0_C>"` cases for the die-temp
    parser. No command is built here.

12. Doc sites quoting the emission format (context, path:line):
    bench/atcut-fit/REPORT.md:67-68, :96, :256;
    bench/atcut-fit/CAL-CLI-SPEC.md:188-191 and §7 (see (c));
    bench/atcut-fit/CAL-COMMAND.md:63, :71, :76, :147;
    bench/atcut-fit/fit_atcut.py:35-39 (docstring, see (c)).

### B. Fork bench kit — felixfelix-bot/MeshCore feat/passive-mapper

Reachable ONLY as dangling commit `d7ae93fa` in this repo's object store
(verified `git cat-file -t d7ae93fa` = commit; `git fsck --dangling` lists it
alone; the branch itself is NOT fetched). Spec pin `3fdfbc8e` is its
ancestor, also present. The repo's fit_atcut.py:156 cites this kit as the
format source.

13. **d7ae93fa:examples/passive_mapper/bench/calib.py:48-50** — PY,
    the fork's canonical builder (origin of the `cal %.6g %.2f` format):
    ```python
    def cal_command(k, t0):
        """The exact serial-CLI line that persists this calibration on the module."""
        return "cal %.6g %.2f" % (float(k), float(t0))
    ```

14. **d7ae93fa:examples/passive_mapper/bench/thermal_bench.py:141-143** — PY,
    `Bench.set_cal()` — the ONLY site that actually writes the line to a
    serial wire: `reply = self.ser.command(calib.cal_command(k, t0))`
    (+ gate `reply.startswith("cal ")`).

15. **d7ae93fa:examples/passive_mapper/bench/thermal_bench.py:236** — PY,
    dry-run mock reply builder:
    `return "cal k=%.6g T0=%.2fC -> persisted (valid=yes)" % (k, t0)`.

16. **d7ae93fa:examples/passive_mapper/bench/thermal_bench.py:515** — PY,
    CLI emission hint:
    `print("persist on the module with:  %s" % calib.cal_command(res["k"], res["t0"]))`.

17. **d7ae93fa:examples/passive_mapper/bench/test_calib.py:67** — PY,
    format regression test:
    `check(calib.cal_command(0.04, 25.0) == "cal 0.04 25.00", "cal command format")`.

18. **d7ae93fa:examples/passive_mapper/MyMesh.cpp:170-188** — C++ firmware
    CONSUMER (defines the contract; at spec pin 3fdfbc8e the same lines sit
    at :166-183): `strncmp(cmd, "cal ", 4)`, parseFloat calls, echo
    `cal k=%.6g T0=%.2fC`, `calshow` `cal valid=%s k=%.6g T0=%.2fC`.
    Companion declarations: d7ae93fa:examples/passive_mapper/MyMesh.h:79
    (help list naming `cal <k> <T0>`), 3fdfbc8e MyMesh.h:48 (`MAP_CAL_FILE`
    = `/selfcal.dat`), 3fdfbc8e host/SelfCal.h:21,36,65-73 (15-byte blob,
    ±60 C band, memcpy storage — the persistence end of the pipe).

### Emitter classification (for the sibling literal/variant cards)

- Can ISSUE to hardware: #14 (fork thermal_bench.py:141) only.
- Build a `cal` literal string: #1 (repo fit_atcut.py:157), #13 (fork
  calib.py:50). Byte-identical formats.
- Render candidate lines without issuing: #2, #5, #6, #15, #16.
- Consumer/contract side (parse, echo, store): #7-#10, #18.
- Fixtures quoting the literal only: #11.
- No emitter exists in `src/`, `examples/` of THIS repo's reachable tree
  (upstream MeshCore has no passive_mapper): verified
  `git grep -nE '"cal %|"cal |cal_command' HEAD -- src examples test` →
  zero hits; `ls examples/` shows companion_radio, kiss_modem,
  simple_repeater, simple_room_server, simple_secure_chat, simple_sensor.

---

## (c) Plan / spec references (what the conversion SHOULD emit)

1. **bench/atcut-fit/CAL-CLI-SPEC.md §7 "Verbatim command template"
   (lines 172-203)** — the normative emission template:
   > `cal <k> <T0>\r`
   > "`<k>` — ppm/°C², parabola magnitude, ≥ 0, plain decimal only:
   > `[0-9]+(.[0-9]+)?`, leading digit before any `.`, no exponent, no sign
   > (a `+` is legal but pointless; `-` is rejected). Emit ≤ 6 significant
   > digits, e.g. `0.034021`."
   > "`<T0>` — °C, any sign, plain decimal, e.g. `24.95` / `-10.5` / `25`.
   > 2 decimals are fully preserved by the f32 blob."
   > "terminator: **CR (0x0D)**, optionally followed by LF. LF-only will NOT
   > execute."
   §7 tail (lines 188-191): "Conforms to the fitter's emission format
   `cal %.6g %.2f` (fit_atcut.py / the fork's own bench kit): for the gated k
   band 0.005–0.15 ppm/°C² and any plausible T0, `%.6g` never emits an
   exponent … so the printed line is always parser-legal."
   §1 (lines 22-31) pins the dispatch + reply + usage strings; §2 (lines
   35-52) the CR framing.

2. **bench/atcut-fit/REPORT.md §1 "Firmware-verified `cal` CLI contract
   (read at the pinned commit)" (lines 35-68)**:
   > "Emission format (what the fitter prints): **`cal %.6g %.2f`** —
   > identical to the fork's own bench kit (`bench/calib.py::cal_command` at
   > branch head)."

3. **bench/atcut-fit/CAL-COMMAND.md, section "What a filled command WILL
   look like (format contract, parser-walked)" (lines 69-103)**:
   > "The fitter's emission format is `cal %.6g %.2f` + CR."
   > worked example: `cal 0.0340211 24.95\r` (synthetic SYNTH-1 stand-in).
   And its VERDICT block (lines 12-18), the no-fit branch behavior:
   > "NO `cal` COMMAND TO ISSUE — the fit child task returned NO-FIT …
   > `cal <k> <T0>\r        <- NOT FILLED. Do not issue a cal command yet.`"

4. **bench/atcut-fit/fit_atcut.py docstring, "Method (per task)" step 3
   (lines 35-39)** — the plan text embedded in the emitter tool itself:
   > "3. Emit the verbatim command `cal %.6g %.2f` — format verified against
   > a Python port of the firmware's own parseFloat()
   > (examples/passive_mapper/MyMesh.cpp, felixfelix-bot/MeshCore
   > feat/passive-mapper @ 3fdfbc8e), which accepts only
   > [-+]?digits[.digits] (leading digit REQUIRED, no exponent) and enforces
   > k >= 0. The firmware echoes `cal k=%.6g T0=%.2fC -> persisted`."

5. **Conversion card t_2656f57c body** (recovered from dispatch session
   `20260914_194259_6b43c6`, message id 7951, this profile's session DB —
   the only card body recoverable; the CLI exposes no bodies):
   > "METHOD:
   >   1. Apply any unit conversion the parser expects (e.g. Hz <-> ppm <->
   >   raw counts, degC offsets) using only the conversions documented by the
   >   contract task.
   >   2. Round each constant to the accepted number of decimals / digit
   >   limit using the parser's own rounding rule (round half up vs C
   >   truncation must match the firmware's parse).
   >   3. Emit the candidate literal strings for each acceptable
   >   representation (e.g. minimal form, fixed-decimal form, integer form if
   >   applicable)."
   > "DELIVERABLE: a table of k and T0 (fitted, converted, rounded,
   >   sent-literal), the candidate literal strings, and the
   >   ppm-vs-temperature error summary; plus an explicit NO-COMMAND branch
   >   when the fit failed."
   Note the parser contract's answer to METHOD 1-2 (already derivable from
   CAL-CLI-SPEC.md §4 lines 110-114: "NO scaling, multiplier, or fixed-point
   is applied anywhere" and §5: "The parser has no decimal-count limit and
   does no rounding") — the conversion tasks will restate this; the
   no-COMMAND branch is live because the fit verdict is NO-FIT
   (CAL-COMMAND.md:12-16).

---

## (d) Repo root and refs inspected

- Root: `/home/c03rad0r/repos/meshcore`
- Reachable refs swept: `main` @ `abe0d36f` (= HEAD, matches origin/main
  history; local ahead 48), and every ref under `refs/remotes/origin/`
  (main, dev, default-scope, feature/nicerf-lr2021-variant,
  fix/2739-review-fixes, flood.max.advert, gh-pages, t-impulse-ui) plus
  `rev-list --all --max-count=400` history sweep.
- Same object store, outside ref reach: dangling fork commit `d7ae93fa`
  (felixfelix-bot/MeshCore feat/passive-mapper head, "docs(passive_mapper):
  refsweep contract no longer cites a nonexistent benchtx card") and pinned
  ancestor `3fdfbc8e` ("feat(passive_mapper): BW125 runtime fallback,
  cal-range predicate, cal-blob writer", 2026-09-11).
- Working-tree status at sweep time: 3 pre-existing untracked bench dirs
  (`bench/atcut-fit/__pycache__/`, `bench/sma-ice-bridging-failure-modes/`,
  `bench/thermal-lag/__pycache__/`) — not touched by this task.
- Board: meshcore-board via kanbanstr-cli (NIP-100); card list pulled
  2026-09-15 this session (500 cards).

Nothing was measured, no command was issued to hardware, no firmware was
flashed; this map inventories sources only.