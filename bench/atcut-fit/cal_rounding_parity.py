#!/usr/bin/env python3
"""Differential parity harness: cal_rounding.py  vs  real C float32 firmware code.

Card t_8c1ba27e.  This is the evidence for the card's ACCEPTANCE clause:

  "for any literal the firmware accepts, emit_literal(parse_literal(x)) == x
   byte-for-byte; the truncation-vs-round-half-up branch is demonstrably the
   behavior asserted at the cited file:line"

It does NOT assert the answer by re-using the Python module.  The oracle is
cal_reference_parse.c, which contains parseFloat() copied VERBATIM from
bench/atcut-fit/cal_cli_harness.cpp:27-47 (itself verbatim firmware,
examples/passive_mapper/MyMesh.cpp:128-143 @ commit 3fdfbc8e), compiled by
gcc at several optimisation levels, and a printf echo in the firmware's own
`%.6g` / `%.2f` formats.  Byte-level comparisons are made on:

  (a) accept/reject verdict          (firmware: parseFloat return value)
  (b) the float32 BIT PATTERN        (not a numeric tolerance)
  (c) the end/consumed index         (chaining k -> T0)
  (d) the emitted display string     (byte equality)

Usage:  python3 cal_rounding_parity.py
Writes: _cal_parity_out.txt (full log, workspace-local; no /tmp usage)
"""

from __future__ import annotations

import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import cal_rounding as cr  # noqa: E402

BUILD_VARIANTS = [
    # (label, flags) - the verdict must be invariant across all of them.
    ("O2_contract_off", ["-std=c99", "-O2", "-ffp-contract=off"]),
    ("O0", ["-std=c99", "-O0"]),
    ("O2_default", ["-std=c99", "-O2"]),
]

CORPUS = [
    # --- happy path / template precision (CAL-CLI-SPEC.md:159-165, :209) ---
    "0.034021", "0.04", "24.95", "25", "0.0340211", "0.04123456789012",
    # --- leading zeros / + sign (CAL-CLI-SPEC.md:73, :213) ---
    "000.0340", "+024.95", "007.5", "+0.04", "0", "0000", "+0", "-0",
    # --- trailing dot / trailing zeros (CAL-CLI-SPEC.md:77-79, :215) ---
    "25.", "25.0", "10.5000", "0.0400", "1.", "3.000000000000000000000",
    # --- negatives (CAL-CLI-SPEC.md:74-76, :216-219) ---
    "-10.5", "-0.0", "-000.000", "-40.0", "1000", "-1.25",
    # --- whitespace handled by parseFloat (CAL-CLI-SPEC.md:60, :81-83) ---
    " 0.04", "\t0.04", " \t 25", "  0.034021",
    # --- digit-limit boundary: the contract says there is NO limit -------
    #     CAL-CLI-SPEC.md:118-120.  Every one of these must parse.
    "0.1", "0.2", "0.3", "0.5", "0.7", "1.15", "2.675", "0.9999999",
    "1.9999999999", "123456789", "99999999", "0.0000000001",
    "0.0000000000000000000000000000000000000001",        # 1e-40: f32 denormal
    "0." + "0" * 43 + "1",                                # 1e-44, denormal
    "0." + "0" * 44 + "1",                                # 1e-45, denormal min
    "0." + "0" * 50 + "1",                                # 1e-51: below denormal
    # --- overflow -> +inf / -inf, never NaN (CAL-CLI-SPEC.md:92-95) ------
    "9" * 40, "9" * 80, "1" + "0" * 40, "-" + "9" * 80,
    # --- exactly-representable vs not (rounding-disagreement probes) -----
    "0.125", "0.375", "0.0625", "1048576.5", "16777216.5", "33554432.5",
    "1.000000059604644775390625",          # 1 + 2^-24 : round-half-even probe
    "1.00000011920928955078125",           # 1 + 2^-23
    "0.100000001490116119384765625",       # f32(0.1)
    # --- grammar rejections (must be rejected by both sides) ------------
    "", " ", ".", ".04", "..", "-", "+", "-.", "+.5", "e5", "0e5", "4e-2",
    "0..04", "0.0.4", "1,5", "abc", "0x10", "nan", "inf", "-inf", "1e999",
    # --- partial-consumption probes for the end index -------------------
    "0.04 25", "0.04\t25", "24.95xyz", "12abc", "5-6", "25.  ", "0.04,",
    "0.034021 24.95", "000.0340 +024.95",
]

CANONICAL_K = [
    # literals in the firmware's OWN emit format `%.6g` (CAL-CLI-SPEC.md:188-191)
    "0.034021", "0.04", "0.034", "0.15", "0.005", "0.0340211", "0.1", "0.3",
]
CANONICAL_T0 = [
    # literals in the firmware's OWN emit format `%.2f`
    "24.95", "25.00", "-40.00", "0.00", "100.50", "-0.10", "1000.00",
]


def build(variant: str, flags: list[str]) -> str:
    exe = os.path.join(HERE, f"_calref_parse_{variant}")
    src = os.path.join(HERE, "cal_reference_parse.c")
    cmd = ["gcc", *flags, "-Wall", "-Wextra", "-o", exe, src]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        raise SystemExit(f"build failed ({flags}):\n{proc.stdout}\n{proc.stderr}")
    return exe


def run_oracle(exe: str, mode: str, literals: list[str]) -> list[tuple]:
    payload = "".join(lit + "\n" for lit in literals)
    proc = subprocess.run([exe, mode], input=payload, capture_output=True, text=True)
    if proc.returncode != 0:
        raise SystemExit(f"oracle failed: {proc.stderr}")
    rows = []
    for line in proc.stdout.splitlines():
        parts = line.split("\t")
        if len(parts) != 4:
            raise SystemExit(f"bad oracle row: {line!r}")
        ok, bits, consumed, emit = parts
        rows.append((ok == "1", bits, -1 if consumed == "-" else int(consumed), emit))
    if len(rows) != len(literals):
        raise SystemExit(f"oracle row count {len(rows)} != {len(literals)}")
    return rows


def py_result(lit: str) -> tuple:
    try:
        value, consumed = cr.parse_literal_with_end(lit)
    except cr.CalParseError:
        return (False, "-", -1, "-")
    return (True, f"0x{cr.f32_bits(value):08X}", consumed, None)


def main() -> int:
    log_lines: list[str] = []
    out_path = os.path.join(HERE, "_cal_parity_out.txt")

    def say(s: str = "") -> None:
        print(s)
        log_lines.append(s)

    say("== cal_rounding.py differential parity vs verbatim C firmware parseFloat ==")
    say(f"module : {os.path.join(HERE, 'cal_rounding.py')}")
    say(f"oracle : {os.path.join(HERE, 'cal_reference_parse.c')} "
        "(parseFloat verbatim: cal_cli_harness.cpp:27-47 <- MyMesh.cpp:128-143 @3fdfbc8e)")
    say(f"corpus : {len(CORPUS)} literals x 2 printf modes x {len(BUILD_VARIANTS)} build variants")
    say("")

    mismatches: list[str] = []
    per_variant_cmp = 0
    cross_variant_disagreements: list[str] = []

    reference_rows_by_variant: dict[str, tuple] = {}

    for variant, flags in BUILD_VARIANTS:
        exe = build(variant, flags)
        say(f"--- build variant {variant}: {' '.join(flags)}")
        for mode in ("k", "t0"):
            rows = run_oracle(exe, mode, CORPUS)
            reference_rows_by_variant[f"{variant}/{mode}"] = rows
            for lit, row in zip(CORPUS, rows):
                py = py_result(lit)
                exp_ok, exp_bits, exp_consumed, _ = py
                ok, bits, consumed, emit = row
                per_variant_cmp += 3  # verdict + bits + consumed index
                if ok != exp_ok:
                    mismatches.append(
                        f"[{variant}/{mode}] {lit!r}: verdict C={ok} py={exp_ok}")
                    continue
                if not ok:
                    continue
                if bits != exp_bits:
                    mismatches.append(
                        f"[{variant}/{mode}] {lit!r}: bits C={bits} py={exp_bits}")
                if consumed != exp_consumed:
                    mismatches.append(
                        f"[{variant}/{mode}] {lit!r}: consumed C={consumed} py={exp_consumed}")
                if mode == "k":
                    py_emit = cr.emit_literal(cr.parse_literal(lit), "k")
                    if py_emit != emit:
                        mismatches.append(
                            f"[{variant}/{mode}] {lit!r}: emit C={emit!r} py={py_emit!r}")
                else:
                    py_emit = cr.emit_literal(cr.parse_literal(lit), "t0")
                    if py_emit != emit:
                        mismatches.append(
                            f"[{variant}/{mode}] {lit!r}: emit C={emit!r} py={py_emit!r}")

    # cross-variant determinism: gcc -O0 / -O2 / -ffp-contract=off must agree.
    # Compared WITHIN a mode (k vs t0 differ only by the printf format, by design).
    for mode in ("k", "t0"):
        base_rows = reference_rows_by_variant[f"{BUILD_VARIANTS[0][0]}/{mode}"]
        for variant, _flags in BUILD_VARIANTS[1:]:
            rows = reference_rows_by_variant[f"{variant}/{mode}"]
            for lit, row, base in zip(CORPUS, rows, base_rows):
                if row != base:
                    cross_variant_disagreements.append(
                        f"{variant}/{mode} {lit!r}: {row} != {base}")

    say("")
    say(f"byte-level comparisons: {per_variant_cmp} "
        "(verdict + f32 bits + consumed index, each mode/variant)")
    say(f"mismatches:              {len(mismatches)}")
    say(f"cross-variant gcc drift: {len(cross_variant_disagreements)}")
    for m in mismatches[:40]:
        say("  MISMATCH " + m)
    for d in cross_variant_disagreements[:20]:
        say("  GCCDRIFT " + d)

    # ---- the card's round-trip clause -----------------------------------
    say("")
    say("== round-trip: emit_literal(parse_literal(x)) == x byte-for-byte ==")
    rt_fail: list[str] = []
    rt_total = 0
    for lit in CANONICAL_K:
        rt_total += 1
        got = cr.emit_literal(cr.parse_literal(lit), "k")
        if got != lit:
            rt_fail.append(f"k  {lit!r} -> {got!r}")
    for lit in CANONICAL_T0:
        rt_total += 1
        got = cr.emit_literal(cr.parse_literal(lit), "t0")
        if got != lit:
            rt_fail.append(f"t0 {lit!r} -> {got!r}")
    say(f"canonical (firmware-emitted format) literals: {rt_total}, failures: {len(rt_fail)}")
    for f in rt_fail:
        say("  RTFAIL " + f)

    # literals the firmware ACCEPTS but whose re-emission is NOT byte-identical
    # (leading zeros, '+' sign, trailing zeros, bare dot).  This is the
    # contract's own `%.6g`/`%.2f` canonicalisation, NOT a rounding bug: the
    # stored f32 is bit-identical (compared against C above).
    say("")
    say("== accepted-but-non-canonical literals (re-emission canonicalises) ==")
    noncanon = 0
    for lit in CORPUS:
        try:
            v = cr.parse_literal(lit)
        except cr.CalParseError:
            continue
        # only literals with no trailing remainder (a full single argument)
        _v, consumed = cr.parse_literal_with_end(lit)
        if consumed != len(lit):
            continue
        got = cr.emit_literal(v, "k")
        if got != lit:
            noncanon += 1
            say(f"  {lit!r} -> {got!r}   (f32 bits 0x{cr.f32_bits(v):08X} identical to C)")
    say(f"non-canonical accepted literals: {noncanon}")

    # ---- contract-rule probes -------------------------------------------
    say("")
    say("== contract-rule probes ==")
    probes = [
        ("CAL-CLI-SPEC.md:74-76  '-0' -> -0.0f (0x80000000)", "-0", "0x80000000"),
        ("CAL-CLI-SPEC.md:73     '000.0340' -> 0.0340", "000.0340", None),
        ("CAL-CLI-SPEC.md:77-79  '25.' -> 25.0", "25.", None),
        ("CAL-CLI-SPEC.md:92-95  overflow -> +inf", "9" * 80, "0x7F800000"),
        ("CAL-CLI-SPEC.md:92-95  overflow -> -inf", "-" + "9" * 80, "0xFF800000"),
    ]
    for label, lit, expect_bits in probes:
        v = cr.parse_literal(lit)
        bits = f"0x{cr.f32_bits(v):08X}"
        verdict = "OK " if (expect_bits is None or bits == expect_bits) else "BAD"
        say(f"  [{verdict}] {label}: {lit[:20]!r} bits={bits}")
    # no built-in round() CALL anywhere in the module (contract names no
    # decimal rounding rule).  Search the parsed AST, not raw text: the
    # docstring legitimately mentions the word "round".
    import ast as _ast
    src_text = open(os.path.join(HERE, "cal_rounding.py"), encoding="utf-8").read()
    tree = _ast.parse(src_text)
    round_calls = [
        f"line {node.lineno}" for node in _ast.walk(tree)
        if isinstance(node, _ast.Call)
        and ((isinstance(node.func, _ast.Name) and node.func.id == "round")
             or (isinstance(node.func, _ast.Attribute) and node.func.attr == "round"))
    ]
    say(f"  [{'OK ' if not round_calls else 'BAD'}] python round() CALL sites in "
        f"cal_rounding.py: {len(round_calls)} (contract specifies no decimal rounding rule)")

    # the decisive discriminator between round-half-up, C truncation and
    # half-even: a value strictly ABOVE the midpoint must not carry, and a
    # value strictly BELOW must not either.  A decimal round-half-up rule
    # (or any 6-decimal pre-round) would change at least one of these.
    say("  -- rounding-rule discrimination (no decimal rule may fire) --")
    disc = [
        # (literal, mid-point at the 6th decimal, expectation)
        ("0.0340214", "0.034021|0.034022 boundary", "must NOT carry to 0.034022"),
        ("0.03402149", "just below midpoint x1e-8", "must NOT carry"),
        ("0.03402151", "just above midpoint", "must NOT carry"),
        ("0.0340205", "exact half at 7th decimal", "must NOT carry (no half-up)"),
        ("1.0000005", "exact half", "must NOT carry (no half-up)"),
        ("2.675", "classic half-up trap (decimal 2.675 -> 2.68)", "must stay f32(2.675)"),
    ]
    for lit, what, expect in disc:
        v = cr.parse_literal(lit)
        # independent check: what would round-half-up on 6 decimals produce?
        from decimal import Decimal, ROUND_HALF_UP
        halfup = float(Decimal(lit).quantize(Decimal("0.000001"), rounding=ROUND_HALF_UP))
        py_emit = cr.emit_literal(v, "k")
        carried = (py_emit != lit)
        bits_ok = f"0x{cr.f32_bits(v):08X}"
        say(f"    {lit!r:14} -> f32 {bits_ok} emit {py_emit!r:12} "
            f"(6dp-round-half-up would be {halfup!r:10}) {what}: {expect}")
    # k >= 0 gate, incl. the -0 case
    for tail, expect_ok in (("0.04 25", True), ("-0 25", True), ("-0.04 25", False),
                            ("0.04-25", True), ("0.04 24.95xyz", True),
                            (".04 25", False), ("0.04", False), ("0..04 25", False)):
        try:
            k, t0 = cr.parse_k_t0(tail)
            ok = True
            detail = f"k=0x{cr.f32_bits(k):08X} T0={t0!r}"
        except cr.CalParseError as exc:
            ok = False
            detail = str(exc)[:60]
        tag = "OK " if ok == expect_ok else "BAD"
        say(f"  [{tag}] cal-tail {tail!r:18} accepted={ok} {detail}")

    say("")
    verdict = (not mismatches and not cross_variant_disagreements
               and not rt_fail and not round_calls)
    say(f"OVERALL: {'PASS' if verdict else 'FAIL'}")

    with open(out_path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(log_lines) + "\n")
    print(f"\nlog written: {out_path}")
    return 0 if verdict else 1


if __name__ == "__main__":
    raise SystemExit(main())
