#!/usr/bin/env python3
"""Generate contract_conversion_inventory.md for t_bb4bbf91.

Every citation block is spliced programmatically from the contract file
bytes at the cited line numbers (never retyped). After writing, the
checker re-extracts every block and byte-compares it against the source.
"""
import hashlib
import sys
from pathlib import Path

SRC = Path("/home/c03rad0r/worktrees/t_bb4bbf91/bench/atcut-fit/CAL-CLI-SPEC.md")
OUT = Path("/home/c03rad0r/worktrees/t_bb4bbf91/contract_conversion_inventory.md")

lines = SRC.read_text().splitlines()
blob = hashlib.sha1(("blob %d\0" % SRC.stat().st_size).encode() + SRC.read_bytes()).hexdigest()


def cite(a: int, b: int | None = None) -> str:
    """Verbatim splice of source lines [a..b] (1-based, inclusive)."""
    b = a if b is None else b
    return "\n".join(lines[a - 1 : b])


def block(a: int, b: int | None = None) -> str:
    """Markdown blockquote with the spliced text."""
    path = "bench/atcut-fit/CAL-CLI-SPEC.md"
    if a == b:
        head = f"> **{path}:{a}**\n>"
    else:
        head = f"> **{path}:{a}-{b}**\n>"
    body = "\n".join("> " + ln if ln else ">" for ln in cite(a, b).splitlines())
    return head + "\n" + body


E = []  # (name, subtitle, body) conversions
G = []  # gaps

# ---------------------------------------------------------------- doc header
hdr = f"""# Contract conversion inventory — `cal <k> <T0>` parser contract

- Card: **t_bb4bbf91** "Extract full conversion inventory from parser contract"
  (meshcore board, fleet offload run, 2026-10-12).
- Contract artifact inventoried, read top to bottom (242 lines):
  `bench/atcut-fit/CAL-CLI-SPEC.md`
  — a verbatim copy ships next to this inventory in THIS repo at the same
  relative path, git blob `378e30311600113ebf32f61979adb5ffb25eb56b`
  (13450 bytes, 242 lines; sha1 of working-tree copy verified by the checker
  in this run). Provenance: created by commit `2075f921` in the `meshcore`
  bench repo ("full cal CLI argument spec, machine-verified against firmware
  parser") and previously inventoried by fleet offload run 1041 on node dq05
  (commit `87658144`); that run's writeback never reached the board, so this
  run re-derives the inventory from the contract bytes independently and
  agrees with it. The contract pins firmware felixfelix-bot/MeshCore
  `feat/passive-mapper` @ `3fdfbc8e120e13d7543fe224c380e27533e720aa`; all
  MyMesh.cpp / SelfCal.h / main.cpp references inside the citations are the
  CONTRACT's own citations into that pin, reproduced as-is.
- Format: **Markdown** (repo convention: prose bench/analysis docs; the
  consumer card t_85fffb5a reads `## Conversions` and `## Gaps` sections).
  Exactly two content sections follow: the conversion entries and the gaps.
- Scope: THIS ONE FILE only. Companion docs named by the contract
  (`REPORT.md` §1, `CAL-COMMAND.md`, `cal_cli_harness.cpp`, `fit_atcut.py`,
  `verify_cal_domain.py`) are NOT part of the contract and are NOT
  inventoried; they are named only where they affect interpretation.
- Verbatim guarantee: every quoted citation block below was spliced
  programmatically from the contract file bytes at the cited line numbers
  (never retyped by hand); the checker re-extracts and byte-compares every
  block after writing (see completion report). Numeric factors and
  int-vs-float semantics are transcribed exactly as printed — no
  normalization, no rounding.

## Conversions

9 conversion entries, ordered by first contract appearance. Direction
semantics: where the contract documents both directions of a transform
(e.g. the blob pack/unpack round-trip) that is ONE entry covering both;
where it documents only one direction, the inverse lives in `## Gaps`.
"""

# ------------------------------------------------------------- entry builder
def entry(name, directions, units, factor, semantics, cites):
    s = f"### {name}\n\n"
    s += f"- **Direction(s) covered:** {directions}\n"
    s += f"- **Input -> output units:** {units}\n"
    s += f"- **Exact factor / offset (as documented):** {factor}\n"
    s += f"- **Integer-vs-float semantics (as stated):** {semantics}\n"
    s += "- **Contract citations (verbatim):**\n\n"
    s += "\n\n".join(cites)
    s += "\n"
    E.append((name, s))


entry(
    "parsearg_to_f32",
    "decimal ASCII text -> IEEE-754 binary32 (float32). One direction only; "
    "the reverse (float32 -> decimal text) is documented only as the printf "
    "formats of entry 6.",
    "in: unitless decimal token (`k` semantically ppm/degC^2, `T0` "
    "semantically degC) -> out: float32",
    "integer part: `v = v*10 + digit`; fraction: `v += digit * scale; "
    "scale *= 0.1f` (exact operators as quoted; the initial value of `scale` "
    "is NOT stated in the contract — see Gaps G4)",
    "float32, \"atof-style, not atoi\"; integers are just the integer-only "
    "case. Documented edge semantics: `-0` parses to IEEE −0.0f and stores "
    "bit pattern 0x80000000; no NaN possible; +inf possible via float "
    "overflow in the `v*10` accumulator.",
    [
        block(59, 63),
        block(67, 68),
        block(118, 120),
        block(74, 76),
        block(92, 93),
    ],
)

entry(
    "parsed_f32_pass_through",
    "float32 -> float32 (verbatim identity, no numeric change). Documented "
    "NON-conversion: the parsed bit patterns flow unchanged from parse to "
    "model to blob.",
    "in: parsed float32 k, T0 -> out: identical float32 values in the "
    "calibration model and /selfcal.dat",
    "none — \"NO scaling, multiplier, or fixed-point is applied anywhere\"",
    "float32 bit patterns passed verbatim; integer form never materializes "
    "on this path.",
    [
        block(110, 114),
    ],
)

entry(
    "temp_to_offset_ppm",
    "degC -> ppm (one direction; inverse not documented — see Gaps G3)",
    "in: T (die temp, degC), T0 (vertex temp, degC), k (ppm/degC^2) -> out: "
    "offset_ppm (ppm)",
    "`offset_ppm = -k*(T-T0)^2` — explicit negation: applied compensation "
    "offset is NEGATED relative to measured drift",
    "float32 model (fed by the verbatim parsed f32 of entry 2); no integer "
    "semantics documented for the model.",
    [
        block(99, 101),
        block(104, 104),
    ],
)

entry(
    "ppm_to_hz",
    "ppm -> Hz (one direction; Hz -> ppm not documented — see Gaps G2)",
    "in: offset in ppm, frequency in MHz -> out: offset in Hz",
    "`offset_hz = ppm * freq_MHz`, i.e. ppm × MHz = Hz. The value/source of "
    "freq_MHz itself is NOT stated in the contract — see Gaps G5.",
    "float (f32 path); no integer semantics documented.",
    [
        block(102, 103),
    ],
)

entry(
    "clamp_offset_ppm_300",
    "ppm -> ppm (range clamp on the model output)",
    "in: model output offset_ppm -> out: clamped offset_ppm, bounds ±300 ppm",
    "clamp to ±300 ppm (SelfCal.h:30, SelfCal.h:91-92 per the contract). "
    "Clamp ordering relative to the ppm->Hz conversion of entry 4 is NOT "
    "stated — see Gaps G7.",
    "float; bounds are decimal ±300.",
    [
        block(92, 95),
    ],
)

entry(
    "format_k_t0_echo",
    "float32 -> decimal display/emission string. Same direction documented "
    "at four sites: success echo, calshow, display rounding rule, and "
    "fitter emission format.",
    "in: k (float32, ppm/degC^2), T0 (float32, degC) -> out: decimal strings",
    "k rendered `%.6g` (6 significant digits), T0 rendered `%.2f` (2 "
    "decimals); for the gated k band 0.005–0.15 ppm/°C² `%.6g` never emits "
    "an exponent",
    "float32 -> string; \"display only; the stored f32 keeps full "
    "precision\"; \"More digits are accepted but cannot be stored\" "
    "(float32 bounds preservation to ~7.2 significant decimal digits).",
    [
        block(30, 30),
        block(32, 33),
        block(121, 127),
        block(128, 129),
        block(188, 191),
    ],
)

entry(
    "pack_cal_blob",
    "float32 pair -> 15-byte little-endian blob (store direction), and "
    "bytes -> float32 pair (load direction, documented as a bit-identical "
    "round-trip)",
    "in: k, T0 (float32), spare 0.0f, magic u16 0x5343, version byte -> out: "
    "15-byte /selfcal.dat blob",
    "memcpy, native (little-endian on all supported targets) — no numeric "
    "scaling; layout: k f32 LE @0, T0 f32 LE @4, spare 0.0f @8, magic 0x5343 "
    "LE -> bytes `43 53` @12, version byte 0 @14",
    "float32 -> 4 LE bytes each (k, T0); spare stored as f32 0.0f; magic u16 "
    "-> 2 LE bytes; version stored as integer byte, always 0. Load path "
    "checks length + magic only and round-trips both floats bit-identically.",
    [
        block(133, 137),
        block(139, 149),
        block(151, 157),
        block(159, 165),
    ],
)

entry(
    "k_to_milliunits_display",
    "float32 k -> boot-debug display integers (display-only direction)",
    "in: k (ppm/degC^2, float32) -> out: milli-units, printed as `%d.%03d`",
    "×1000 (milli-units)",
    "float32 × 1000 rendered via integer printf fields `k=%d.%03d`; "
    "\"display scaling only, not storage\". The rounding rule for the "
    "integer split is NOT stated — see Gaps G6.",
    [
        block(167, 170),
    ],
)

entry(
    "t0_to_centidegrees_display",
    "float32 T0 -> boot-debug display integers (display-only direction)",
    "in: T0 (degC, float32) -> out: centi-degrees, printed as `%d.%02d`",
    "×100 (centi-degrees)",
    "float32 × 100 rendered via integer printf fields `T0=%d.%02d`; "
    "\"display scaling only, not storage\". The rounding rule for the "
    "integer split is NOT stated — see Gaps G6.",
    [
        block(167, 170),
    ],
)

# ------------------------------------------- documented non-conversions part
nonconv = """#### Documented items deliberately NOT counted as conversions

Considered and excluded — documented in the contract, but they transform no
units:

- **Semantic gate `k >= 0.0f`** (validation, not a conversion; no upper
  bound on k, no constraint at all on T0)

""" + block(105, 109) + """

- **Validity band |T_die − T0| ≤ 60 °C with BW125 fallback outside it** (a
  range predicate, not a conversion)

""" + block(198, 203) + """

- **Thermal EMA seeded with T0** (`_temp_ema = T0`, plain assignment of a
  same-unit value; the EMA recurrence itself is NOT in the contract — see
  Gaps G9)

""" + block(155, 157) + "\n"

# ------------------------------------------------------------------- gaps part
gaps = """## Gaps

Conversions a reasonable engineer would expect that the contract does NOT
state. Gaps are NEVER to be implemented; they are recorded for review only.

- **G1 `gaps_raw_counts_to_ppm`** — raw counts <-> ppm: no counts-domain
  conversion is documented anywhere in the contract (verified by grep over
  the contract bytes: `raw` has zero occurrences; the only `count` hit is
  "decimal-count limit" at CAL-CLI-SPEC.md:118, about digit counts; `ADC`
  occurs only as a substring of `loadCalibration` at :154/:164), while the
  parent work family explicitly names the raw-counts domain (e.g.
  t_3bd737f9 body: "Hz <-> ppm <-> raw counts, degC offsets").

""" + block(118, 118) + """

- **G2 `gaps_hz_to_ppm`** — Hz -> ppm: only ppm -> Hz
  (`offset_hz = ppm * freq_MHz`) is documented (CAL-CLI-SPEC.md:102-103);
  the inverse direction is never stated.

- **G3 `gaps_offset_ppm_to_temp`** — offset_ppm -> temperature (solving T
  from a measured offset): only degC -> ppm
  (`offset_ppm = -k*(T-T0)^2`, CAL-CLI-SPEC.md:99-101) is documented; the
  inverse is never stated.

- **G4 `gaps_parse_scale_init`** — initial fraction-scale constant for
  `v += digit * scale; scale *= 0.1f` (CAL-CLI-SPEC.md:120): the contract
  quotes the accumulation but never states the initial value of `scale` at
  the start of the fraction loop.

- **G5 `gaps_freq_mhz_value`** — value/source of `freq_MHz` in
  `offset_hz = ppm * freq_MHz` (CAL-CLI-SPEC.md:102-103): the conversion is
  documented but the carrier-frequency constant and where it comes from are
  not stated.

- **G6 `gaps_display_int_rounding`** — rounding rule for the boot-display
  integer split `k=%d.%03d` / `T0=%d.%02d` (CAL-CLI-SPEC.md:167-170):
  factors ×1000/×100 are stated but how the product becomes the printed
  integers (truncate vs round) is not.

- **G7 `gaps_clamp_ordering`** — ordering of the ±300 ppm clamp
  (CAL-CLI-SPEC.md:94-95) relative to the ppm->Hz conversion
  (CAL-CLI-SPEC.md:102-103): the contract does not state whether the clamp
  applies to offset_ppm only, or also to offset_hz.

- **G8 `gaps_display_scale_inverse`** — inverse of the boot-display
  scalings (milli-units -> k, centi-degrees -> T0): not documented; only
  the display direction exists (CAL-CLI-SPEC.md:167-170).

- **G9 `gaps_temp_ema_recurrence`** — die-temp EMA update (recurrence /
  time-constant converting successive die-temp samples into `_temp_ema`):
  the contract only documents the seed `_temp_ema = T0`
  (CAL-CLI-SPEC.md:155-157); the EMA conversion itself is absent.

---

End of inventory: 9 conversions, 3 documented non-conversions, 9 gaps.
"""

OUT.write_text(hdr + "\n" + "\n".join(e[1] for e in E) + "\n" + nonconv + "\n" + gaps)
print("written", OUT, OUT.stat().st_size, "bytes; source blob", blob)