# Plan/spec sections defining the `cal <k> <T0>` emission contract

Task card: **t_e30a2e15** — "Extract plan/spec sections defining the cal emission
contract" (worker-base, 2026-10-01). Parent: `t_b23c606a` (provenance map).
Sibling lanes: `t_fc07ecf0` (emission-site grep), `t_f688bbf0` (board hunt),
`t_dc868c3b` (assembler).

**Repo root inspected:** `/home/c03rad0r/repos/meshcore` (git repo, remote
`https://github.com/c03rad0r/MeshCore.git`).
**Branch / commit:** `main` @ `32dd320419f90c6b5c9d11e191c540d3ede8b594`
(working tree; status showed only untracked `bench/atcut-fit/__pycache__/`,
`bench/chamber-ramp-rates/COMMENT.md`, `bench/sma-ice-bridging-failure-modes/`,
`bench/thermal-lag/__pycache__/`).
**Also inspected, same object store, outside branch reach:** pinned fork ancestor
`3fdfbc8e120e13d7543fe224c380e27533e720aa` ("feat(passive_mapper): BW125 runtime
fallback, cal-range predicate, cal-blob writer") and dangling fork head
`d7ae93fa1d0f71fa704d59c801351c28c3d9020a` ("docs(passive_mapper): refsweep
contract no longer cites a nonexistent benchtx card") — both verified present via
`git cat-file -t` this session.

Nothing was measured, nothing issued to hardware, nothing fabricated. Every claim
below carries a `path#heading` (or card id) + a verbatim quote. No document was
found that carries an HTML anchor; heading text is given verbatim instead.

---

## 0. Search surfaces swept (and the negatives)

Terms requested by the card: `cal`, `calibration`, `cal <k>`, `T0`,
`temp_offset`, `gain`, `conversion`, `emit`, `command line`.

Surfaces checked: repo design docs (`docs/`), READMEs, CONTRIBUTING, ADRs
(none exist), `*.md` under `bench/`, repo-root `*.md`, in-code block
comments/docstrings, and kanban card bodies/comments on the `meshcore` board
(`~/.hermes/kanban/boards/meshcore/kanban.db`, 689 tasks + `task_comments`).

Exact commands run (all read-only):

    search_files pattern 'cal\s*<k>'  path /home/c03rad0r/repos/meshcore
    git grep -nE 'cal %|cal <k>|%.6g|cal_command|cal %\.' -- '*.md' '*.py' '*.cpp' '*.h'
    grep -rn -iE 'cal\s*<|cal %|"cal |`cal |calibration|temp_offset|T0' docs README.md CONTRIBUTING.md RELEASE.md
    grep -niE 'calibrat|\bcal\b|selfcal|tempco|T0' README.md CONTRIBUTING.md RELEASE.md
    grep -rnE 'range=\+/-|CAL_RANGE_C|\+/-60|\+/-90|\+/-80' bench/ docs/
    grep -rnE 'three arg|3 arg|third argument|third arg|argc' --include='*.md' bench/
    git ls-files | grep -iE 'plan|adr|design|spec'
    ls -d .hermes/plans ./.hermes            (absent)
    python3 sqlite3 (read-only URI) over boards/meshcore/kanban.db:
        SELECT * FROM tasks            -- 689 rows, regex over title+body
        SELECT * FROM task_comments    -- regex over body
    git show d7ae93fa:examples/passive_mapper/bench/README.md  (+ calib.py,
        RESULTS.md, thermal_bench.py, MyMesh.cpp, test_calib.py)
    git show d7ae93fa:examples/passive_mapper/MyMesh.cpp | sed -n '160,200p'

Verified negatives:

- **`gain`, `temp_offset`, `temperatureOffset`: ZERO hits** anywhere in the
  repo docs, the fork bench kit, or the board card bodies/comments. The contract
  has no "gain" or "temperature-offset" field; the temperature field is `T0`.
- **No `docs/`-, README-, CONTRIBUTING- or RELEASE-level design doc** mentions
  `cal`/calibration at all (`grep -niE 'calibrat|\bcal\b|selfcal|tempco|T0'
  README.md CONTRIBUTING.md RELEASE.md` → 0 hits; `docs/` tree is upstream
  MeshCore protocol docs only: companion_protocol, kiss_modem_protocol,
  packet_format, cli_commands, …).
- **No `plans/`, `adr/`, `design/`, `specs/` directory in the repo**; the only
  `*spec*` tracked file is `bench/atcut-fit/CAL-CLI-SPEC.md` itself.
- **No "three-argument" / "third argument" / `argc` spec text** in any `bench/`
  markdown (`grep -rnE 'three arg|3 arg|third argument|third arg|argc'` → 0).
- The `tollgate` term from the sibling card's search list is not present in the
  cal-emission doc space.

The plan/spec surface for this contract is therefore exactly three kinds of
document: (A) the `bench/atcut-fit/` report suite in this repo, (B) the fork's
own bench kit reachable only as object `d7ae93fa`, and (C) kanban card bodies.

---

## 1. GROUP A — this repo, `bench/atcut-fit/` (+ the provenance map)

### A1. `bench/atcut-fit/CAL-CLI-SPEC.md#7. Verbatim command template`
Path: `/home/c03rad0r/repos/meshcore/bench/atcut-fit/CAL-CLI-SPEC.md:172-191`

>     cal <k> <T0>\r
>
> with:
>
> - `<k>`  — ppm/°C², parabola magnitude, ≥ 0, plain decimal only:
>   `[0-9]+(.[0-9]+)?`, leading digit before any `.`, no exponent, no sign
>   (a `+` is legal but pointless; `-` is rejected). Emit ≤ 6 significant
>   digits, e.g. `0.034021`.
> - `<T0>` — °C, any sign, plain decimal, e.g. `24.95` / `-10.5` / `25`.
>   2 decimals are fully preserved by the f32 blob.
> - separator: single space (multiple spaces/tabs also legal; comma is not).
> - terminator: **CR (0x0D)**, optionally followed by LF. LF-only will NOT
>   execute.
>
> Conforms to the fitter's emission format `cal %.6g %.2f` (fit_atcut.py /
> the fork's own bench kit): for the gated k band 0.005–0.15 ppm/°C² and any
> plausible T0, `%.6g` never emits an exponent and always keeps the leading
> digit, so the printed line is always parser-legal.

Also the fill-in example immediately below (lines 193-196):

>     cal 0.034021 24.95\r
>       -> cal k=0.034021 T0=24.95C -> persisted (valid=yes)

### A2. `bench/atcut-fit/CAL-CLI-SPEC.md#1. Command surface and dispatch`
Path: `.../bench/atcut-fit/CAL-CLI-SPEC.md:17-33`

> - The `cal` command is selected by `strncmp(cmd, "cal ", 4) == 0`
>   (MyMesh.cpp:166). The 4th byte must be a **space (0x20)** …
> - Exactly **2 arguments, order `cal <k> <T0>`**: `k` first, `T0` second
>   (MyMesh.cpp:168-170). Units stated in the handler's own comment at
>   MyMesh.cpp:167: *"cal <k> <T0>   (k in ppm/C^2, T0 in C)"*.
> - On success the firmware replies
>   `cal k=%.6g T0=%.2fC -> persisted (valid=yes)` (MyMesh.cpp:172-174);
>   on any parse failure `usage: cal <k_ppm_per_C2> <T0_C>` (MyMesh.cpp:176).
> - Read-back command: `calshow` → `cal valid=%s k=%.6g T0=%.2fC range=+/-60C
>   die_temp=... off_hz=...` (MyMesh.cpp:178-181, CAL_RANGE_C at SelfCal.h:36).

§2 of the same file (`#2. Serial line framing`, lines 35-52) is the normative
statement of the CR framing, and §5 (`#5. Precision / decimal places`,
lines 116-129) the normative statement on digits:

> ⇒ **6 significant digits for k and 2 decimals for T0 are
> exactly sufficient** and match the firmware's own echo format `%.6g` /
> `%.2f` (MyMesh.cpp:172).

### A3. `bench/atcut-fit/REPORT.md#What WAS delivered / 1. Firmware-verified cal CLI contract`
Path: `.../bench/atcut-fit/REPORT.md:67-68`

> Emission format (what the fitter prints): **`cal %.6g %.2f`** — identical to
> the fork's own bench kit (`bench/calib.py::cal_command` at branch head).

And `bench/atcut-fit/REPORT.md#Ready-to-issue command (TEMPLATE ONLY — cannot be filled without data)`, lines 110-118:

>     cal <k_ppm_per_C2> <T0_C>        e.g. format: cal 0.034021 24.95
>
> Rules: k ≥ 0, leading digit before any decimal point, no exponent, 6
> significant digits for k and 2 decimals for T0 are plenty for the f32 blob.

### A4. `bench/atcut-fit/CAL-COMMAND.md#What a filled command WILL look like (format contract, parser-walked)`
Path: `.../bench/atcut-fit/CAL-COMMAND.md:69-103`

> The fitter's emission format is `cal %.6g %.2f` + CR. Walked manually through
> the parser path (MyMesh.cpp @ 3fdfbc8e; every step harness-verified), using
> the SELF-TEST's synthetic SYNTH-1 values as stand-in — **these are synthetic
> and must never be issued to real hardware**:
>
>     cal 0.0340211 24.95\r

and the same file's `#VERDICT` block, lines 12-18 (the no-fit branch):

> ## VERDICT: NO `cal` COMMAND TO ISSUE — the fit child task returned NO-FIT
>
>    cal <k> <T0>\r        <- NOT FILLED. Do not issue a cal command yet.

### A5. `bench/atcut-fit/fit_atcut.py` — module docstring, `Method (per task)` step 3
Path: `.../bench/atcut-fit/fit_atcut.py:35-39`

>  3. Emit the verbatim command `cal %.6g %.2f` — format verified against a
>     Python port of the firmware's own parseFloat() (examples/passive_mapper/
>     MyMesh.cpp, felixfelix-bot/MeshCore feat/passive-mapper @ 3fdfbc8e), which
>     accepts only [-+]?digits[.digits] (leading digit REQUIRED, no exponent) and
>     enforces k >= 0. The firmware echoes `cal k=%.6g T0=%.2fC -> persisted`.

### A6. `bench/atcut-fit/cal_cli_harness.cpp` — in-code block comment + snprintf (consumer contract)
Path: `.../bench/atcut-fit/cal_cli_harness.cpp:65-79`

>     // Persist a bench-derived calibration: cal <k> <T0>   (k in ppm/C^2, T0 in C)
>       snprintf(reply, 160, "cal k=%.6g T0=%.2fC -> %s (valid=%s)", …
>       snprintf(reply, 160, "commands: status, mode, flush, reset, erase, cal <k> <T0>, calshow");

### A7. `bench/dryrun-ambient/REPORT.md` — echo-side contract (secondary)
Path: `.../bench/dryrun-ambient/REPORT.md:76-83`

> the `calshow` reply contract
> `cal valid=%s k=%.6g T0=%.2fC range=+/-%.0fC die_temp=%.1f
> off_hz=%.0f` was read directly from the fork source
> (MyMesh.cpp:178-181 @ 3fdfbc8e)

### A8. `bench/cal-emission-provenance/PROVENANCE-MAP.md` — meta-spec (secondary; cites A1-A7, §(c) lines 212-277)
Path: `.../bench/cal-emission-provenance/PROVENANCE-MAP.md:214-228`. This is a
*spec-by-reference* document (it quotes the others); use A1-A5 as primary and
cite this one as the existing map. Its §(c)-1 quotes A1 §7; §(c)-2 quotes A3;
§(c)-3 quotes A4; §(c)-4 quotes A5; §(c)-5 recovers the `t_2656f57c` card body
(see C2 below). NOTE: the map's own header (line 7-9) states it was written
against `main @ abe0d36f`, which is **not** the current HEAD (`32dd3204`).

---

## 2. GROUP B — fork bench kit `felixfelix-bot/MeshCore feat/passive-mapper`

Reachable in this object store only as dangling commit `d7ae93fa` (branch itself
not fetched). Spec pin `3fdfbc8e` is its ancestor. This kit is the **origin of
the `cal %.6g %.2f` format** and the fork's own plan prose.

### B1. `README.md#Firmware CLI you will use`  (d7ae93fa)
Path: `d7ae93fa:examples/passive_mapper/bench/README.md#Firmware CLI you will use` (lines 58-67)

>     status    # mode, bw (62.5 or 125 fallback), die_temp=, off_hz=, cal=yes/no
>     calshow   # cal valid=.. k=.. T0=..C range=+/-90C die_temp=.. off_hz=..
>     cal <k> <T0>   # persist the calibration (k > 0, ppm/C^2; T0 in C)
>     reset     # zero the record counter (used for packet counting)

### B2. `README.md#3. Fit and persist (fit)`  (d7ae93fa)
Path: `d7ae93fa:.../bench/README.md#3. Fit and persist (`fit`)` (lines 99-118)

>     # then, on the module:
>     #   cal <k> <T0>          <- the exact line is printed by `fit`
>
> `fit` solves `compensation_ppm = k*(T-T0)^2` (+ a bias term, …), prints the RMS
> residual and warnings, writes the 15-byte blob, and prints the `cal` line.
> …
> Verify on the module:
>
>     cal <k> <T0>      -> "persisted (valid=yes)"
>     calshow           -> off_hz matches k*(die_temp-T0)^2, range=+/-90C
>     status            -> bw=62.5  (no "(fallback)")

### B3. `README.md#What has to be measured, and by whom`  (d7ae93fa)
Path: `d7ae93fa:.../bench/README.md#What has to be measured, and by whom` (lines 33-44)

> Deliverable per module: a `k`/`T0` pair, the fit residual, the measured
> die-vs-crystal time constant `tau`, and the resulting `/selfcal.dat` blob.
> The blob is **per module** - never copy one between modules.

### B4. `README.md#5. Record it (durable)`  (d7ae93fa)
Path: `d7ae93fa:.../bench/README.md#5. Record it (durable)` (lines 150-157)

> Add one row per module to `bench/RESULTS.md`, including the module ID
> (EUI/serial + board label), the blob hex, `k`, `T0`, sweep span, residual, `tau`,
> operator and date.

### B5. `calib.py` — the canonical builder + sign convention
Path: `d7ae93fa:examples/passive_mapper/bench/calib.py#cal_command` (lines 48-50)

> def cal_command(k, t0):
>     """The exact serial-CLI line that persists this calibration on the module."""
>     return "cal %.6g %.2f" % (float(k), float(t0))

module docstring, lines 11-18 (sign convention, load-bearing):

> SIGN CONVENTION (load-bearing, see SelfCal.h):
>     drift_ppm(T)          = -k*(T-T0)^2      # crystal is SLOW away from turnover
>     required_offset_ppm(T) = +k*(T-T0)^2      # RX must be programmed HIGH
>     k >= 0 is the MAGNITUDE of the quadratic coefficient, T0 is the turnover in C.

### B6. `RESULTS.md#How to fill a row`  (d7ae93fa)
Path: `d7ae93fa:.../bench/RESULTS.md#How to fill a row`

> Then persist on the module: `cal <k> <T0>`, and confirm `calshow` shows
> `valid=yes` with the expected `off_hz`.

### B7. `MyMesh.cpp:166-183` — the firmware handler's own in-code comment (GROUND spec)
Path: `d7ae93fa:examples/passive_mapper/MyMesh.cpp#L166-183` (at pin 3fdfbc8e the
same lines sit at `:166-183` per CAL-CLI-SPEC; the comment text itself is the
authoritative field spec).

>   } else if (strncmp(cmd, "cal ", 4) == 0) {
>     // Persist a bench-derived calibration: cal <k> <T0>
>     //   k  = |quadratic tempco| in ppm/C^2 (>0, magnitude - model applies
>     //        +k*(T-T0)^2 because a slow crystal needs the LO programmed high)
>     //   T0 = turnover temperature in C
>     float k = 0.0f, t0 = 0.0f;
>     const char* p = cmd + 4;
>     if (parseFloat(p, &p, &k) && parseFloat(p, nullptr, &t0) && k >= 0.0f) {
>       bool ok = writeCalBlob(k, t0);
>       snprintf(reply, 160, "cal k=%.6g T0=%.2fC -> %s (valid=%s)", …);
>     } else {
>       snprintf(reply, 160, "usage: cal <k_ppm_per_C2> <T0_C>  (k>0 = magnitude)");

### B8. `test_calib.py#L67` — format regression assertion (the pinned byte shape)
Path: `d7ae93fa:.../bench/test_calib.py:67`

>     check(calib.cal_command(0.04, 25.0) == "cal 0.04 25.00", "cal command format")

---

## 3. GROUP C — kanban card bodies (board `meshcore`, `~/.hermes/kanban/boards/meshcore/kanban.db`)

These are part of the "plan" surface per the parent card (STEP 3 names "kanban
card body"). Cards were read read-only this session; the board list CLI exposes
no bodies, so the DB was queried directly.

### C1. `t_2e041ab8` — "Verify literal cal string character-by-character against parser"
> GOAL: Independently prove that the exact literal `cal <k> <T0>` string survives
> the firmware's parse path with no character-level surprise.
>
>  3. Probe the boundaries the contract lists: values needing one more digit than
>    allowed, negative T0, values that would be clamped, an empty or
>    single-argument line, and trailing CR/LF.
>  4. Explicitly check the no-fit branch: confirm the plan issues no command at
>    all rather than a placeholder.

### C2. `t_2656f57c` — "Convert fitted k/T0 into parser representation; quantify rounding ppm"
> METHOD:
>   1. Apply any unit conversion the parser expects (e.g. Hz <-> ppm <-> raw
>   counts, degC offsets) using only the conversions documented by the contract task.
>   2. Round each constant to the accepted number of decimals / digit limit using
>   the parser's own rounding rule (round half up vs C truncation must match the
>   firmware's parse).
>   3. Emit the candidate literal strings for each acceptable representation (e.g.
>   minimal form, fixed-decimal form, integer form if applicable).
>   …
>   5. If the fit task returned a no-fit verdict, DO NOT fabricate a command: report
>   the failed-fit numbers, why the fit failed, and state explicitly that no cal
>   command should be issued yet.
>
> DELIVERABLE: a table of k and T0 (fitted, converted, rounded, sent-literal), the
> candidate literal strings, and the ppm-vs-temperature error summary; plus an
> explicit NO-COMMAND branch when the fit failed.

Note: at the time of writing the body's step 1 ("using only the conversions
documented by the contract task") has **no documented conversions to consume** —
see the conflict list §4-6.

### C3. `t_91f4019e` — "Convert fitted k/T0 into parser literal strings" (archived)
>   4. NO-FIT BRANCH: if the fit task returned a no-fit verdict, DO NOT fabricate a
>   command. Report the failed-fit numbers, why the fit failed … and explicitly state
>   that no cal command should be issued yet. This branch takes precedence over steps 1-3.
>
> DELIVERABLE: the k/T0 conversion table, the enumerated candidate literal strings,
> and the no-fit report when applicable.

### C4. `t_0017d836` — "Inventory all candidate `cal <k> <T0>` literals from the conversion task and plan"
>  - Record exact file:line locations for every emission site, plus the plan
>    section(s) that describe what should be emitted.
>  STEP 2 — ENUMERATE every distinct literal form the code or plan could produce.
>  Cover at minimum (>=8 total): happy path (`cal 1000 25`); … negative T0
>  (`cal 1000 -5`); zero T0 (`cal 1000 0`); comma decimal separator … scientific
>  notation …; missing/empty second argument (`cal 1000 ` / `cal 1000`); trailing
>  whitespace / CRLF …; the NO-FIT branch — explicitly state whether the plan emits
>  nothing, an empty string, a placeholder, or no command at all.

### C5. `t_c260596e` — "Extract plan intent and no-fit branch behavior for cal emission" (archived)
> GOAL: Determine, from the plan/spec (and the code path that implements it), what
> the conversion task INTENDS to emit for each case — especially the NO-FIT branch.
>   3. Resolve the NO-FIT case PLAINLY, one of: 'emits nothing', 'emits empty
>   string', 'emits placeholder <exact bytes>', 'emits no command at all'. If plan
>   and code disagree, report both and label the disagreement — do not silently pick one.

### C6. `t_291d4094` — "Assemble final cal <k> <T0> deliverable with caveats" (archived)
>   1. Select the passing literal; if several pass, choose the one with the smallest
>   rounding penalty in ppm.
>   2. Write out the verbatim command line exactly as it must be typed (no
>   placeholders, no angle brackets at the end).
>   …
>   4. List caveats: rounding effect … validity range of the fit, per-module
>   persistence note …, and the explicit statement that NO command is issued if the
>   fit verdict was no-fit.

### C7. `t_3f930320` — "Fit AT-cut parabola constants (k, T0) from freezer-sweep CSV" (status done)
> (2) Convert: k = -a, T0 = -b/(2a). (3) Sanity checks: parabola must open downward
> in offset (a < 0, i.e. k > 0); T0 must land in a plausible room-temperature region
> and inside or near the swept range … FAILURE PATH: if residuals are large … do NOT
> force a fit … DELIVERABLE: table of (T, offset_ppm, residual), fitted k and T0 with
> units, R^2, and caveats.

### C8. `t_d6484f25` — "Document serial `cal <k> <T0>` parser contract with file:line citations"
> ACCEPTANCE CRITERIA … A fresh worker who never opens the firmware can take any
> literal line — `cal 3.2 -12`, `cal 0x10 25`, `cal 3.2` (missing arg2), `cal abc 1`,
> `cal 1e9 25` — and state from your table alone whether it parses and exactly what
> stored values it produces.

### C9. `t_c11f2cbe` — "Pin exact `cal <k> <T0>` serial CLI syntax in MeshCore passive_mapper"
>   - required decimal places / precision, truncation vs rounding, and any tolerance
>   or range check that can reject the value.
>   - line terminator expectations (\n vs \r\n), max argument count, and whether
>   trailing whitespace or extra tokens are tolerated.
> …
> (c) a verbatim command template showing where k and T0 are substituted and at
> what precision, e.g. `cal 12.345 21.5\r\n` with the real numbers, precision and
> terminator justified by the quoted parser line

### C10. `t_8f776e31` — "Re-derive `cal <k> <T0>` parser contract from firmware source, cited"
> - exponent notation (e/E) and whether it is silently truncated by atoi/strtol
> - trailing garbage after the last digit (ignored endptr?)
> - integer overflow / clamping (saturate, wrap, reject-to-0?)
> - truncation at fixed-width buffers
> - missing second argument
> - empty line
> - trailing '\r', '\n', '\r\n', and whether the newline is stripped before tokenizing

### C11. `t_fc07ecf0` — "Grep repo for every cal-command emission site (path:line)" (sibling of this cluster)
No emission-format statement; scoping card only. Listed here because it is the
companion lane to this task and its greps are recorded in §0.

### C12. `t_bb4bbf91` / `t_3bd737f9` / `t_85fffb5a` — the conversions-module cards
These are the only cards that describe what the *conversion* layer should
produce. `t_bb4bbf91` (ready) — "Extract full conversion inventory from parser
contract":

> 2. For each conversion, record: a suggested snake_case function name, the
> conversion direction(s) covered (e.g. hz_to_ppm and ppm_to_hz are two entries if
> the contract documents both directions), input/output units, the exact numeric
> offset or scaling factor, and the integer-vs-float type semantics stated.
> 3. Cite each entry VERBATIM with file:line (e.g. `contracts/parser.md:142`).
> …
> 5. Emit the inventory as a single artifact file `contract_conversion_inventory.md`
> … with two sections: `## Conversions` and `## Gaps`.

`t_85fffb5a` (todo) — "Implement conversions.py strictly from the contract
inventory":

> 1. Walk the inventory top to bottom and create one function per documented
> conversion entry, including both directions where the contract documents both.
> …
> 3. Add a module-level constant `gaps: list[str]` … Nothing else from gaps may be
> implemented.
> 4. Preserve integer-vs-float semantics exactly as documented.

---

## 4. Conflicts / ambiguities found (both sides quoted; NOT resolved)

**(1) "two args" vs "three args" — tolerated third token.**
The template is consistently two-argument: A1 `cal <k> <T0>\r`; A2 "Exactly **2
arguments**"; B1 `cal <k> <T0>`; B7 handler comment `cal <k> <T0>`. But the
parser **silently accepts a third**: A1's own §3 (CAL-CLI-SPEC.md:86-89) and §8
edge-case matrix (line 212) both record the opposite:

> - **Trailing garbage after T0 is silently ignored**: the T0 parse is called
>   with `endp = nullptr` and nothing checks the remainder
>   (MyMesh.cpp:170) — `cal 0.034 24.95xyz` and `cal 0.04 25 99` both succeed [H].

> | `cal 0.04 25 99`            | ACCEPT (3rd arg ignored)                         |

So the *emission* contract is exactly two tokens, but the *parse* contract is
"first two tokens only, rest discarded". A doc that says "exactly 2" and a doc
that says "a 3rd arg is accepted" are both correct and describe different sides
of the same line.

**(2) T0 decimal count: `%.2f` emission vs integer T0 accepted.**
Emission format is `%.2f` (A3, A4, A5, B2, B5). But the parser accepts any
decimal count, and the canonical example is integer: A1 §8 (line 210)
`| cal 0.04 25 | ACCEPT, canonical |`, and B8's regression pins `cal 0.04 25.00`
(two decimals). Both are quoted; the *format* is 2 decimals, the *grammar*
allows 0..N.

**(3) Validity band: ±60 °C at the pin vs ±90 °C at branch head.**
A2 (CAL-CLI-SPEC.md:32-33) reads `range=+/-60C` and cites `CAL_RANGE_C at
SelfCal.h:36` at pin `3fdfbc8e`. A3 (REPORT.md:70-75) records the drift:

> - `d83b3660`: the APPLIED compensation sign was corrected … and `CAL_RANGE_C`
>   widened 60 → 90 C.

and B1/B2 (fork branch head) read `range=+/-90C`; A4 (CAL-COMMAND.md:118-120)
notes "(CAL_RANGE_C, SelfCal.h:36; widened to 90 C in post-pin commit
`d83b3660` — check the deployed firmware's pin)". Both numbers are on record;
the correct one depends on the deployed pin. Not resolved here.

**(4) Blob `version` default: 0 vs 1 — direct doc-vs-doc contradiction.**
A4 (CAL-COMMAND.md:132-136):

> - **Blob rebuild note**: `pack_blob` now defaults `version=0`, matching the
>   firmware byte-for-byte … A previous default of 1 produced blobs that still
>   loaded (length+magic check only) but did not match what the firmware itself
>   writes.

vs B6 (fork RESULTS.md, "How to fill a row"):

> python3 -c "import calib; print(calib.pack_blob(K, T0, version=1).hex())"

The repo doc says 0; the fork's own results doc says 1. Quoted both; not
resolved. (Fork `calib.py` defines `pack_blob(k, t0, version=0)` — default 0 —
per B5's file header, which agrees with A4.)

**(5) k upper bound: firmware unbounded vs fitter-gated vs bench-expected.**
A2 (CAL-CLI-SPEC.md:105-109): "Semantic gate: `k >= 0.0f` … **No upper bound on
k**". A5/A1 gate the fitter to `0.005–0.15 ppm/°C²`. B2 (fork README) says
"Expect `k` in 0.02..0.06 ppm/C^2". Three different numbers, three different
roles (parse gate vs fit gate vs typical value); none quoted as the "contract".
Not resolved.

**(6) NO-FIT branch: card asks for a plain verdict, no document gives one.**
`t_c260596e` (C5) demands a resolution into one of 'emits nothing' / 'emits
empty string' / 'emits placeholder <exact bytes>' / 'emits no command at all'.
The only located statements are: A4's `cal <k> <T0>\r  <- NOT FILLED. Do not
issue a cal command yet.`, and the code (`fit_atcut.py:400-402`) which prints a
prose verdict and emits nothing:

> `"VERDICT: DO NOT ISSUE cal — data does not support a clean parabola (see FAIL checks above). No command emitted."`

The cards (C2, C3) mandate "DO NOT fabricate a command". **No document found
uses any of C5's four phrases verbatim**, so C5's acceptance remains unmet by
the current doc set. Reported, not resolved.

**(7) `conversions` contract artifact referenced but absent.**
C2 step 1, C12 and `t_40a13e6c`/`t_50fe334e`/`t_3bd737f9`/`t_85fffb5a` all
consume "the parser contract artifact" / `contract_conversion_inventory.md` /
`conversions.py`. **No such artifact exists** in the repo (`docs/` has none;
no `contracts/` dir; `git ls-files | grep -iE 'plan|adr|design|spec'` returns
only `CAL-CLI-SPEC.md`). The nearest actual contract artifact is
`bench/atcut-fit/CAL-CLI-SPEC.md` (A1/A2). Flagged as a gap, not resolved.

---

## 5. Ordered citation list (short form)

Grouped by document; `path#heading` + the line range quoted above. Use §A1 as the
primary normative emission template; §B7 as the ground firmware comment; §C2/C3
as the plan intent; §A4 as the no-fit verdict.

    ROOT /home/c03rad0r/repos/meshcore @ main 32dd3204
    A1 bench/atcut-fit/CAL-CLI-SPEC.md#7. Verbatim command template        :172-191
    A2 bench/atcut-fit/CAL-CLI-SPEC.md#1. Command surface and dispatch     :17-33
       bench/atcut-fit/CAL-CLI-SPEC.md#2. Serial line framing               :35-52
       bench/atcut-fit/CAL-CLI-SPEC.md#5. Precision / decimal places        :116-129
    A3 bench/atcut-fit/REPORT.md#What WAS delivered (1. Firmware-verified
       cal CLI contract)                                                    :35-68
       bench/atcut-fit/REPORT.md#Ready-to-issue command (TEMPLATE ONLY)     :110-123
    A4 bench/atcut-fit/CAL-COMMAND.md#What a filled command WILL look like  :69-103
       bench/atcut-fit/CAL-COMMAND.md#VERDICT                              :12-18
    A5 bench/atcut-fit/fit_atcut.py  (docstring Method step 3)             :35-39
    A6 bench/atcut-fit/cal_cli_harness.cpp                                 :65-79
    A7 bench/dryrun-ambient/REPORT.md (calshow reply contract)             :76-83
    A8 bench/cal-emission-provenance/PROVENANCE-MAP.md#(c)                 :212-277
       (meta; cites A1-A5; written at main @ abe0d36f, not current HEAD)
    B1 d7ae93fa:examples/passive_mapper/bench/README.md#Firmware CLI you
       will use                                                            :58-67
    B2 d7ae93fa:.../bench/README.md#3. Fit and persist (fit)               :99-118
    B3 d7ae93fa:.../bench/README.md#What has to be measured, and by whom   :33-44
    B4 d7ae93fa:.../bench/README.md#5. Record it (durable)                 :150-157
    B5 d7ae93fa:.../bench/calib.py#cal_command                             :48-50
    B6 d7ae93fa:.../bench/RESULTS.md#How to fill a row
    B7 d7ae93fa:examples/passive_mapper/MyMesh.cpp (handler comment)       :166-183
    B8 d7ae93fa:.../bench/test_calib.py                                    :67
    C1 kanban t_2e041ab8 (verify literal char-by-char)
    C2 kanban t_2656f57c (conversion + rounding ppm)   [METHOD steps 1-5]
    C3 kanban t_91f4019e (parser literal strings)      [NO-FIT BRANCH]
    C4 kanban t_0017d836 (literal inventory)           [STEP 2/3]
    C5 kanban t_c260596e (plan intent + no-fit resolution)
    C6 kanban t_291d4094 (final deliverable + caveats)
    C7 kanban t_3f930320 (fit AT-cut, done)
    C8 kanban t_d6484f25 (document parser contract)
    C9 kanban t_c11f2cbe (pin exact syntax)
    C10 kanban t_8f776e31 (re-derive parser contract)
    C11 kanban t_fc07ecf0 (emission-site grep; sibling lane)
    C12 kanban t_bb4bbf91 / t_3bd737f9 / t_85fffb5a (conversions module)

---

## 6. Acceptance check for this card

- At least one plan/spec reference with heading text and a verbatim quote:
  **YES** — §A1 (`CAL-CLI-SPEC.md#7. Verbatim command template`, quoted
  verbatim), plus §A2-A5, §B1-B8.
- Grouped by document with the repo root/branch inspected: **YES** — §1-A repo
  docs (`/home/c03rad0r/repos/meshcore` @ `main 32dd3204`), §2-B fork kit
  (`d7ae93fa`, pin `3fdfbc8e`), §3-C kanban card bodies (`meshcore` board).
- Conflicts quoted on both sides, not resolved: **YES** — §4 (1)-(7).
- No speculation: every claim carries a `path#heading`, `path:line`, commit sha,
  or card id.
- Searches run recorded, including the verified negatives (`gain`,
  `temp_offset`, `temperatureOffset` = 0 hits; no `docs/`-level design doc; no
  plans/ADR dir): **YES** — §0.
