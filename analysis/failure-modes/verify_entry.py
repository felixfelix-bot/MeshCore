#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Acceptance gate for FM-FT-MOUNT-01.

Checks, mechanically and against the frozen calculator transcript:
  1. the four labelled attributes (a)-(d) are present;
  2. the template fields are present;
  3. >= 2 sources are cited and each carries a number;
  4. every key number quoted in the entry appears in the calculator output;
  5. NO mitigation / corrective-action vocabulary anywhere in the entry.

Run: python3 analysis/failure-modes/verify_entry.py
"""

import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ENTRY = os.path.join(HERE, "feedthrough-mount-cold-loosening.md")
CALC_OUT = os.path.join(HERE, "feedthrough_mount_thermal_calc.out")

FAILS = []


def check(name, ok, detail=""):
    print("%-4s %s%s" % ("PASS" if ok else "FAIL", name, ("  <- " + detail) if detail and not ok else ""))
    if not ok:
        FAILS.append(name + (" : " + detail if detail else ""))


def main():
    entry = open(ENTRY, encoding="utf-8").read()
    calc = open(CALC_OUT, encoding="utf-8").read()
    low = entry.lower()

    # 1 -- the four labelled attributes ------------------------------------
    print("== 1. four labelled attributes ==")
    for tag, needle in (
        ("(a) MECHANISM", "## (a) mechanism"),
        ("(b) LIKELIHOOD", "## (b) likelihood"),
        ("(c) REVERSIBILITY", "## (c) reversibility"),
        ("(d) CONSEQUENCE CLASS", "## (d) consequence class"),
    ):
        check("attribute %s" % tag, needle in low)

    # 2 -- template fields -------------------------------------------------
    print("\n== 2. template fields ==")
    for field in ("**ID**", "**Title**", "**(a) Mechanism**", "**(b) Likelihood −20 °C**",
                  "**(b) Likelihood −40 °C**", "**(c) Reversibility**",
                  "**(d) Consequence class**", "**References**"):
        check("field %s" % field, field in entry)

    # 3 -- cited sources, each with a number -------------------------------
    print("\n== 3. cited sources with numbers ==")
    refs = re.findall(r"\*\*\[(S[^\]]+)\]", entry)
    check(">= 2 distinct sources", len(refs) >= 2, "found %d" % len(refs))
    for tag in ("S1", "S2", "S3", "S4", "S5", "S6", "S7"):
        body = re.search(r"\*\*\[%s\][^\n]*\n(.*?)(?=\n\*\*\[|\n\*\*Companion|\Z)" % tag, entry, re.S)
        if not body:
            check("source %s present" % tag, False)
            continue
        has_num = bool(re.search(r"\d", body.group(1)))
        check("source %s carries a number" % tag, has_num)
    tags = sorted(set(re.findall(r"\[(S_?[^\]]+)\]", entry)))
    print("   distinct tags cited inline: %s" % tags)
    check(">= 2 distinct tags cited inline", len(tags) >= 2, str(tags))

    # 4 -- quoted numbers: entry form <-> calculator transcript form -------
    print("\n== 4. quoted numbers reproduce in the calculator output ==")
    pairs = [("17.3", "17.3"), ("16.0", "16.0"), ("14.4", "14.4"), ("9.9", "9.9"),
             ("18 - 19", "18 - 19"), ("23", "23.0"), ("21 - 24", "21 - 24"),
             ("24", "24.0"), ("112 - 135", "112 - 135"), ("8.1", "8.1"),
             ("1068", "1068"), ("1334", "1334"), ("712", "712"), ("890", "890"),
             ("392", "392"), ("589", "589"), ("461", "461"), ("692", "692"),
             ("255", "255"), ("382", "382"), ("195", "195"), ("292", "292"),
             ("0.30", "0.30"), ("0.46", "0.456"), ("0.68", "0.684"),
             ("49", "49.0"), ("546", "545.9"), ("764", "764.2"), ("2.7", "2.7"),
             ("0.15", "0.152"), ("0.23", "0.228"), ("1.09", "1.086"),
             ("228", "228"), ("342", "342"), ("117.7", "117.7")]
    for entry_form, calc_form in pairs:
        check("number %s in entry" % entry_form, entry_form in entry)
        check("number %s in transcript" % calc_form, calc_form in calc)

    # 5 -- zero mitigation content ----------------------------------------
    # Scanned strictly over the entry body, i.e. everything BEFORE the reference
    # list, plus one documented exemption: the scope-discipline sentence, which
    # *negates* the forbidden categories. The reference list is excluded because
    # source titles/URLs are citations by definition (the source S2 is literally
    # titled "Bulkhead Jamb Nut Torque Recommendations"); §R is still scanned for
    # the presence of a number per source in check 3 above.
    print("\n== 5. mitigation / corrective-action lexicon (must be empty) ==")
    lex = ["mitigat", "corrective", "recommend", "remediat", "should be", "must be",
           "shall be", "redesign", "design change", "lock washer", "threadlock",
           "loctite", "action item", "best practice", "to prevent", "in order to avoid",
           "add a ", "increase the torque", "specify a", "improve", "solution", "fix "]
    exempt_marker = "no mitigation, no design change, no corrective action"
    ref_start = low.find("## §r references")
    hits = []
    skipped = 0
    for lineno, line in enumerate(entry.splitlines(), 1):
        l = line.lower()
        if ref_start >= 0 and sum(len(x) + 1 for x in entry.splitlines()[:lineno - 1]) > ref_start:
            continue  # inside the reference list
        if exempt_marker in l:
            skipped += 1
            continue
        for tok in lex:
            if tok in l:
                hits.append((tok, lineno, line.strip()[:110]))
    for tok, line, ctx in hits:
        print("   HIT  '%s'  L%d  %s" % (tok, line, ctx))
    print("   exempt lines skipped: %d (negated scope sentence); reference list excluded" % skipped)
    check("zero mitigation vocabulary in entry body", not hits, "%d hits" % len(hits))

    print("\n== verdict ==")
    if FAILS:
        print("FAILED %d check(s):" % len(FAILS))
        for f in FAILS:
            print("  - " + f)
        return 1
    print("ALL CHECKS PASS — one structured entry, attributes (a)-(d) present,")
    print(">= 2 numbered sources, zero mitigation content.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
