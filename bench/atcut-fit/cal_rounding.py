"""Firmware-exact digit-limit and rounding primitives for the `cal <k> <T0>` parser.

Card: t_8c1ba27e (mode: code; parent t_50fe334e), workspace
/home/c03rad0r/worktrees/t_e1408991.

CONTRACT CONSUMED (not re-derived from firmware source):
  /home/c03rad0r/repos/meshcore/bench/atcut-fit/CAL-CLI-SPEC.md
  @ meshcore main, repo blob 378e30311600113ebf32f61979adb5ffb25eb56b,
  242 lines / 13450 B (per contract_conversion_inventory.md:5-8).
  Every "CAL-CLI-SPEC.md:N" below is a line in THAT file.
  The contract's own citations into firmware commit 3fdfbc8e
  (felixfelix-bot/MeshCore, examples/passive_mapper/MyMesh.cpp:NNN) are
  reproduced as-is, marked "-> MyMesh.cpp:NNN" so the two namespaces stay
  distinguishable.

=====================================================================
THE RULE, AS THE CONTRACT STATES IT  (this module implements ONLY this)
=====================================================================
DIGIT LIMIT: there is none.
  CAL-CLI-SPEC.md:118-120 -> "The parser has **no decimal-count limit and
  does no rounding**".
  => DIGIT_LIMIT = None, MAX_SIGNIFICANT_DECIMALS = None.  No literal is
  truncated, padded, or rejected for its digit count.

ROUNDING: none.  No round-half-up, no C-style decimal truncation, no
  banker's rounding is applied anywhere on the parse path.  The only
  rounding that exists is the IEEE-754 binary32 round-to-nearest-even that
  each individual float32 arithmetic operation performs on its result
  (hardware semantics, not a decimal rule the parser chooses).  Contract
  wording and the two ops it names:
    integer part:  v = v*10 + digit               CAL-CLI-SPEC.md:119 -> MyMesh.cpp:134
    fraction part: v += digit*scale; scale *= 0.1f CAL-CLI-SPEC.md:120 -> MyMesh.cpp:138
    "all in **float32**"                           CAL-CLI-SPEC.md:120
  => ROUNDING_MODE = "none (per-op IEEE-754 binary32 accumulation only)".
  NO other rounding logic exists in this module: Python's built-in round()
  is never called, because the contract does not specify half-even decimal
  rounding anywhere (had it done so, the call site would carry that
  citation here).

GRAMMAR (CAL-CLI-SPEC.md:59-63, verbatim):
    arg      := ws* sign? integer [ '.' fraction? ]
    ws       := ' ' | '\t'          (zero or more, MyMesh.cpp:129)
    sign     := '-' | '+'           (single, optional; MyMesh.cpp:130-131)
    integer  := digit+              (AT LEAST ONE DIGIT REQUIRED, MyMesh.cpp:132)
    fraction := digit+              (zero or more digits, MyMesh.cpp:135-139)
  Consequences asserted by the contract and implemented verbatim here:
    - leading digit REQUIRED: ".04" rejected          CAL-CLI-SPEC.md:69-70
    - no exponent: 'e'/'E' stops the parse            CAL-CLI-SPEC.md:71-72
    - leading zeros accepted ("000.0340")             CAL-CLI-SPEC.md:73
    - trailing dot OK ("25." -> 25.0)                 CAL-CLI-SPEC.md:77-79
    - trailing garbage after the number is left to the caller; the T0 parse
      is called with endp=nullptr so nothing checks the remainder
                                                      CAL-CLI-SPEC.md:86-89
    - '-'/'+' sign on either argument                 CAL-CLI-SPEC.md:74-76

SIGN / NEGATIVE ZERO: "-0 parses to IEEE -0.0f ... stores k = 0x80000000"
  CAL-CLI-SPEC.md:74-76.  Implemented: the sign is applied to the
  accumulated magnitude, so "-0" yields a genuine -0.0f bit pattern.

OVERFLOW: "No NaN possible from this grammar; +inf possible via absurdly
  long digit strings (float overflow in the `v*10` accumulator)"
  CAL-CLI-SPEC.md:92-95.  Implemented: a float32 op whose exact result
  exceeds the f32 range yields +inf/-inf (C behaviour), never NaN and never
  a Python OverflowError.

EMIT (echo format, MyMesh.cpp:172-174 via CAL-CLI-SPEC.md:30):
    cal k=%.6g T0=%.2fC -> persisted (valid=yes)
  => k is emitted with `%.6g` (6 significant digits) and T0 with `%.2f`
  (2 decimals).  CAL-CLI-SPEC.md:121-127 states 6 sig digits for k and 2
  decimals for T0 are "exactly sufficient" for the f32-preserving band;
  CAL-CLI-SPEC.md:128-129: the echo "rounds to %.6g/%.2f - display only;
  the stored f32 keeps full precision"; CAL-CLI-SPEC.md:188-191: for the
  gated band 0.005-0.15 ppm/degC^2 `%.6g` never emits an exponent.  The
  `%.6g` / `%.2f` conversions are the ONLY place in this module where a
  decimal-digit count is applied, and it is the contract's own emit rule,
  not a parse rule.

=====================================================================
CONTRACT GAPS THAT TOUCH THIS MODULE (flagged, never invented)
=====================================================================
G4  `gaps_parse_scale_init` - the contract quotes "v += digit * scale;
    scale *= 0.1f" (CAL-CLI-SPEC.md:120) but never states the INITIAL value
    of `scale` for the fraction loop.  This module cannot avoid needing it,
    so the value is taken from the companion (non-contract) host harness
    cal_cli_harness.cpp:40, which is itself verbatim firmware
    (-> MyMesh.cpp:140): `float scale = 0.1f;` i.e. f32(0.1).
    See FRACTION_SCALE_INIT and the call site.  This is a documented
    deviation-by-necessity, NOT an invention: if the firmware owner says the
    initial scale differs, only that one constant changes.
    (G4 is listed as a gap in contract_conversion_inventory.md:284.)
G6  `gaps_display_int_rounding` - the boot-display integer split
    `k=%d.%03d` / `T0=%d.%02d` (CAL-CLI-SPEC.md:167-170) states the
    x1000/x100 factors but NOT whether the product is truncated or rounded.
    => deliberately NOT implemented here; no display-split function exists
    in this module (that conversion belongs to the sibling conversions
    module, and its rounding is unspecified).
Out of scope by card boundary: unit conversions (ppm<->Hz, degC->ppm, blob
pack, display scaling) are the sibling card t_8d7d4d13; this module only
does parse + emit.

SELF-VERIFICATION: cal_rounding_parity.py compiles cal_reference_parse.c
(the verbatim firmware parseFloat + printf echo) and byte-compares
parse bits / end index / emitted strings against this module over a corpus
that includes every boundary class named above.  Result recorded in
REPORT.md.
"""

from __future__ import annotations

import math
import struct

__all__ = [
    "CalParseError",
    "DIGIT_LIMIT",
    "MAX_SIGNIFICANT_DECIMALS",
    "ROUNDING_MODE",
    "FRACTION_SCALE_INIT",
    "F32_MAX",
    "to_f32",
    "f32_bits",
    "parse_literal",
    "parse_literal_with_end",
    "parsearg_to_f32",
    "emit_literal",
    "emit_k_t0_line",
    "format_k_t0_echo",
]

# ---------------------------------------------------------------------------
# Constants that carry a citation, or are explicitly flagged.
# ---------------------------------------------------------------------------

# CAL-CLI-SPEC.md:118-120: "no decimal-count limit and does no rounding".
DIGIT_LIMIT: None = None
MAX_SIGNIFICANT_DECIMALS: None = None

# CAL-CLI-SPEC.md:119-120: the only rounding is per-op IEEE-754 binary32.
ROUNDING_MODE = "none (per-op IEEE-754 binary32 accumulation only)"

# GAP G4 (see module docstring): initial fraction scale is NOT in the
# contract; value 0.1f comes from companion harness cal_cli_harness.cpp:40
# (verbatim firmware -> MyMesh.cpp:140).
FRACTION_SCALE_INIT = 0.1

# IEEE-754 binary32 finite maximum (2^128 - 2^104); the switchover to inf in
# C matches this module's not-a-number-overflow handling (CAL-CLI-SPEC.md:92-95).
F32_MAX = 3.4028234663852886e38

_F32 = struct.Struct("<f")


def to_f32(x: float) -> float:
    """Narrow a Python float to the nearest float32 value (round-to-nearest-even).

    This is the single place where the module mirrors the hardware rounding
    that CAL-CLI-SPEC.md:119-120 asserts ("all in float32").  A result whose
    magnitude exceeds the f32 range becomes +/-inf, exactly as the C
    accumulator does (CAL-CLI-SPEC.md:92-95: "+inf possible ... float
    overflow in the v*10 accumulator"); NaN is impossible from this grammar
    and is never produced here.
    """
    try:
        return _F32.unpack(_F32.pack(x))[0]
    except OverflowError:  # only possible on |x| beyond the f32 finite range
        return math.inf if x > 0 else -math.inf


def f32_bits(x: float) -> int:
    """Bit pattern of the f32 value x (for the 0x80000000-style assertions)."""
    (bits,) = struct.unpack("<I", _F32.pack(x))
    return bits


class CalParseError(ValueError):
    """The literal is not accepted by the grammar (firmware returns usage).

    Firmware behaviour for every rejection is the single usage line
    `usage: cal <k_ppm_per_C2> <T0_C>` (CAL-CLI-SPEC.md:31), with no detail
    about which rule failed; this exception carries the reason for callers
    while preserving the accept/reject verdict 1:1.
    """


_INT_DIGITS = "0123456789"


def parse_literal_with_end(
    text: str, *, start: int = 0
) -> tuple[float, int]:
    """Firmware `parseFloat` (CAL-CLI-SPEC.md:54-63; -> MyMesh.cpp:128-143).

    Returns (value, end_index) where end_index is the index of the first
    character NOT consumed, mirroring the firmware's `endp` out-parameter --
    the k argument is parsed with `endp` so the T0 parse starts where k
    stopped (CAL-CLI-SPEC.md:86-89).

    Order of operations is the firmware's, so the float32 accumulation is
    reproducible op-for-op:
        1. ws*        ' ' or '\t' only, unbounded      MyMesh.cpp:129
        2. sign?      single '-' or '+'                MyMesh.cpp:130-131
        3. integer    digit+ REQUIRED                  MyMesh.cpp:132
        4. '.' then fraction digits (zero or more)     MyMesh.cpp:135-139
    Raises CalParseError where the firmware returns false.
    """
    n = len(text)
    i = start

    # 1. ws* -- CAL-CLI-SPEC.md:60 (ws := ' ' | '\t', zero or more,
    #    MyMesh.cpp:129).  No other whitespace is skipped.
    while i < n and (text[i] == " " or text[i] == "\t"):
        i += 1

    # 2. sign? -- CAL-CLI-SPEC.md:61 (MyMesh.cpp:130-131).  At most one sign.
    neg = False
    if i < n and text[i] == "-":
        neg = True
        i += 1
    elif i < n and text[i] == "+":
        i += 1

    # 3. integer := digit+  -- CAL-CLI-SPEC.md:62, "AT LEAST ONE DIGIT
    #    REQUIRED" (MyMesh.cpp:132 returns false before any digit is seen).
    #    Accumulation v = v*10 + digit, narrowed to f32 after EACH op:
    #    CAL-CLI-SPEC.md:119 -> MyMesh.cpp:134.
    if i >= n or text[i] not in _INT_DIGITS:
        raise CalParseError(
            f"no digit at index {i}: leading digit required "
            "(CAL-CLI-SPEC.md:62, :69-70)"
        )
    v = to_f32(0.0)
    while i < n and text[i] in _INT_DIGITS:
        v = to_f32(v * to_f32(10.0))  # f32 multiply, then...
        v = to_f32(v + to_f32(float(ord(text[i]) - 48)))  # ...f32 add per digit
        i += 1

    # 4. [ '.' fraction? ] -- CAL-CLI-SPEC.md:63.  The dot may be present with
    #    ZERO fraction digits ("25." -> 25.0, CAL-CLI-SPEC.md:77-79), because
    #    the fraction loop body simply runs zero times (MyMesh.cpp:135-139).
    if i < n and text[i] == ".":
        i += 1
        # NOT stated by the contract -- GAP G4; value from companion
        # harness cal_cli_harness.cpp:40 (verbatim -> MyMesh.cpp:140).
        scale = to_f32(FRACTION_SCALE_INIT)
        while i < n and text[i] in _INT_DIGITS:
            # v += digit*scale; scale *= 0.1f -- CAL-CLI-SPEC.md:120 ->
            # MyMesh.cpp:138.  Three f32 ops, each narrowed like the hardware.
            v = to_f32(v + to_f32(to_f32(float(ord(text[i]) - 48)) * scale))
            scale = to_f32(scale * to_f32(0.1))
            i += 1
        # NOTE (contract, CAL-CLI-SPEC.md:71-72): 'e'/'E' is NOT consumed --
        # the parse stops here and the caller sees the remainder.

    # Sign application -- CAL-CLI-SPEC.md:74-76.  Negating a zero magnitude
    # yields true -0.0f (bits 0x80000000), which is what makes `cal -0 25`
    # accepted by the k>=0 gate.
    return (to_f32(-v) if neg else v), i


def parse_literal(text: str) -> float:
    """`parsearg_to_f32` (contract entry 1, CAL-CLI-SPEC.md:30-67).

    Parse one argument exactly as the firmware does and return the f32 value
    (as the Python float holding that exact f32 number).  Raises
    CalParseError where the firmware would answer `usage:`.

    Digit limit: NONE (CAL-CLI-SPEC.md:118).  Rounding: NONE beyond the
    per-op binary32 narrowing (CAL-CLI-SPEC.md:119-120).
    """
    value, _end = parse_literal_with_end(text)
    return value


# Contract entry 1 is *named* `parsearg_to_f32`; alias so downstream code can
# use the contract's own name.
parsearg_to_f32 = parse_literal


def parse_k_t0(text: str) -> tuple[float, float]:
    """Firmware's two-argument sequence for a full `cal <k> <T0>` argument tail.

    Mirrors MyMesh.cpp:166-170 as summarised at CAL-CLI-SPEC.md:26-33:
      - k is parsed with `endp` (so T0 starts where k stopped),
      - T0 is parsed with endp=nullptr, i.e. trailing garbage is ignored
        (CAL-CLI-SPEC.md:86-89),
      - the k >= 0 semantic gate is applied (CAL-CLI-SPEC.md:105-109).
    Raises CalParseError on any rejection (both parses fail -> one usage line).
    """
    k, end = parse_literal_with_end(text, start=0)
    try:
        t0, _end = parse_literal_with_end(text, start=end)
    except CalParseError as exc:
        raise CalParseError(f"T0 parse failed after k at index {end}: {exc}") from None
    # CAL-CLI-SPEC.md:105: "Semantic gate: k >= 0.0f (MyMesh.cpp:170).
    # Negative k -> usage."  -0.0f passes this test (it is not < 0).
    if not (k >= 0.0):
        raise CalParseError("k < 0 rejected by the k >= 0 gate (CAL-CLI-SPEC.md:105)")
    return k, t0


# ---------------------------------------------------------------------------
# Emission: the firmware's echo format, CAL-CLI-SPEC.md:30 / :32-33.
# This is the ONLY decimal-digit count in the module, and it is the
# contract's own display rule, not a parse-side rounding rule.
# ---------------------------------------------------------------------------

_EMIT_FORMAT = {
    # `cal k=%.6g ...` (MyMesh.cpp:172-174) - 6 significant digits.
    # CAL-CLI-SPEC.md:121-127: 6 sig digits are "exactly sufficient".
    "k": "%.6g",
    # `T0=%.2fC` (MyMesh.cpp:172-174) - 2 decimals.
    "t0": "%.2f",
}


def emit_literal(value: float, kind: str = "k") -> str:
    """`format_k_t0_echo` (contract entry 6) for ONE field.

    kind='k'  -> "%.6g" of the f32 value (6 significant digits)
    kind='t0' -> "%.2f"  of the f32 value (2 decimals)
    Citations: CAL-CLI-SPEC.md:30, :32-33, :121-129, :188-191.
    No parse-side rounding rule is applied here; the value itself is f32
    (the caller's parse output), and the digit count is the emit rule.
    """
    try:
        fmt = _EMIT_FORMAT[kind.lower()]
    except KeyError:
        raise ValueError(f"kind must be 'k' or 't0', got {kind!r}") from None
    return fmt % to_f32(value)


def emit_k_t0_line(k: float, t0: float) -> str:
    """Full success echo: `cal k=%.6g T0=%.2fC` (CAL-CLI-SPEC.md:30)."""
    return f"cal k={emit_literal(k, 'k')} T0={emit_literal(t0, 't0')}C"


# Contract entry 6's name.
format_k_t0_echo = emit_k_t0_line


if __name__ == "__main__":  # tiny smoke check, no network / no side effects
    for lit in ("0.034021", "0.04", "25.", "000.0340", "-0", "+024.95"):
        try:
            v = parse_literal(lit)
            print(f"{lit!r:16} -> {v!r:26} bits=0x{f32_bits(v):08X} "
                  f"emit={emit_literal(v, 'k')!r}")
        except CalParseError as exc:
            print(f"{lit!r:16} -> REJECT ({exc})")
    print(emit_k_t0_line(parse_literal("0.034021"), parse_literal("24.95")))
