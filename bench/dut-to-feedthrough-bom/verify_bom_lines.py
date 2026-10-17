#!/usr/bin/env python3
"""Verifier for t_fe6e9c1b deliverable (DUT -> chamber interior -> bulkhead feedthrough BOM lines).

Re-derives the card's acceptance conditions from the shipped markdown file itself.
Stdlib only. No network. Read-only.

Usage: python3 _verify_t_fe6e9c1b.py [path-to-deliverable]
"""
import re
import sys
import hashlib

PATH = sys.argv[1] if len(sys.argv) > 1 else \
    "/home/c03rad0r/worktrees/t_e1408991/dut-to-feedthrough-bom-t_fe6e9c1b-2026-10-17.md"

FAILS = []
CHECKS = 0


def chk(name, cond, detail=""):
    global CHECKS
    CHECKS += 1
    if cond:
        print("PASS  %s%s" % (name, ("  [" + detail + "]") if detail else ""))
    else:
        print("FAIL  %s%s" % (name, ("  [" + detail + "]") if detail else ""))
        FAILS.append(name)


def split_row(line):
    """Split a markdown table row on UNESCAPED pipes; unescape \\| afterwards."""
    s = line.strip()
    if s.startswith("|"):
        s = s[1:]
    if s.endswith("|"):
        s = s[:-1]
    cells, cur, i = [], "", 0
    while i < len(s):
        c = s[i]
        if c == "\\" and i + 1 < len(s) and s[i + 1] == "|":
            cur += "|"
            i += 2
            continue
        if c == "|":
            cells.append(cur.strip())
            cur = ""
            i += 1
            continue
        cur += c
        i += 1
    cells.append(cur.strip())
    return cells


text = open(PATH, encoding="utf-8").read()
lines = text.splitlines()
print("file: %s" % PATH)
print("sha256: %s" % hashlib.sha256(open(PATH, "rb").read()).hexdigest())
print("lines: %d  bytes: %d" % (len(lines), len(text.encode())))
print("-" * 78)

# ---- 1. the mandated 7-column header, in the card's order -------------------
MANDATED = [
    "item description",
    "qty",
    "part number",
    "disposition",
    "lead-time",
    "source/vendor",
    "cited source",
]
hdr_idx = None
for i, ln in enumerate(lines):
    if ln.strip().startswith("|") and "Item description" in ln and "QTY" in ln:
        hdr_idx = i
        break
chk("mandated header row exists", hdr_idx is not None)
hdr = split_row(lines[hdr_idx]) if hdr_idx is not None else []
chk("header has exactly 7 columns", len(hdr) == 7, "got %d" % len(hdr))
for k, want in enumerate(MANDATED):
    got = hdr[k].lower() if k < len(hdr) else ""
    chk("column %d contains %r" % (k + 1, want), want in got, got[:60])

# ---- 2. BOM body rows -------------------------------------------------------
# body = consecutive table rows after the separator line
body = []
j = (hdr_idx or 0) + 2
while j < len(lines) and lines[j].strip().startswith("|"):
    body.append(lines[j])
    j += 1
chk("BOM body has >= 3 data rows", len(body) >= 3, "got %d" % len(body))
rows = [split_row(r) for r in body]
chk("every BOM row has exactly 7 cells", all(len(r) == 7 for r in rows),
    "row lens: %s" % [len(r) for r in rows])
chk("no empty cell in any BOM row",
    all(all(c.strip() for c in r) for r in rows),
    str([[i for i, c in enumerate(r) if not c.strip()] for r in rows]))

ids = []
for r in rows:
    m = re.match(r"\*\*(RF-[0-9]+[ab]?)", r[0])
    ids.append(m.group(1) if m else None)
chk("every BOM row carries an RF-n id", all(ids), str(ids))
chk("no duplicate id in the table", len(set(ids)) == len(ids), str(ids))
chk("expected ids present", set(ids) >= {"RF-1a", "RF-1b", "RF-2", "RF-3", "RF-4"}, str(ids))

# ---- 3. per-row: QTY, one disposition token, series + gender + impedance ----
DISP = ("ON-HAND", "MUST-PROCURE", "MUST-FABRICATE")
for r, rid in zip(rows, ids):
    desc, qty, mpn, disp, lead, vendor, cite = r
    d = desc + " " + mpn
    chk("%s: QTY cell non-empty and numeric-ish" % rid, bool(re.match(r"^[0-9]", qty)),
        qty[:40])
    found = [tok for tok in DISP if tok in disp]
    chk("%s: exactly one disposition token" % rid, len(found) == 1, str(found))
    chk("%s: series SMA named" % rid, "SMA" in d)
    geo = ("SMA-F" in d) or ("SMA-M" in d)
    chk("%s: explicit gender token present (SMA-F / SMA-M)" % rid, geo)
    chk("%s: impedance stated" % rid, "50 \u03a9" in d or "50 ohm" in d or "50-ohm" in d)
    chk("%s: lead-time cell populated" % rid, bool(lead.strip()))
    chk("%s: source/vendor cell populated" % rid, len(vendor.strip()) > 3)
    chk("%s: cited-source cell populated" % rid, len(cite.strip()) > 20, str(len(cite)))
    chk("%s: cited source names a parent row IF-n" % rid, bool(re.search(r"\bIF-[0-9]\b", cite)),
        re.findall(r"IF-[0-9]+", cite)[:3].__str__())

# ---- 4. inherited UNVERIFIED / UNSPECIFIED annotation -----------------------
for r, rid in zip(rows, ids):
    blob = " ".join(r)
    chk("%s: carries UNVERIFIED or UNSPECIFIED annotation" % rid,
        ("UNVERIFIED" in blob) or ("UNSPECIFIED" in blob))
# every parent row consumed here is itself unflagged from conflict
for rid in ("RF-1a", "RF-1b", "RF-2", "RF-3", "RF-4"):
    blob = " ".join(rows[ids.index(rid)])
    chk("%s: conflict restated inline (see open risks / conflict wording)" % rid,
        ("see open risks" in blob) or ("conflict" in blob.lower()))

# ---- 5. no fabricated "VERIFIED" claim --------------------------------------
chk("no bare VERIFIED positive claim in the BOM table",
    not any(re.search(r"(?<!UN)VERIFIED(?!\s*[/-])", " ".join(r)) for r in rows),
    "rows must not assert VERIFIED")

# ---- 6. dispositions are honest (no ON-HAND for anything not owned) --------
onhand = [rid for r, rid in zip(rows, ids) if "ON-HAND" in r[3]]
chk("ON-HAND only on the DUT-integral part RF-1a", onhand in ([], ["RF-1a"]), str(onhand))

# ---- 7. structural sections present ----------------------------------------
for needle, label in [
    ("SEGMENT BOUNDARY", "segment boundary section"),
    ("DE-CONFLICTION", "de-confliction section"),
    ("ACCEPTANCE CROSS-CHECK", "acceptance cross-check section"),
    ("NOTHING FABRICATED", "honesty section"),
    ("UNVERIFIED / UNSPECIFIED REGISTER", "flags register"),
]:
    chk("%s present" % label, needle in text)
chk("out-of-scope sibling segment card t_a4844b93 named",
    "t_a4844b93" in text)
chk("parent card t_1bb81290 named as the input", "t_1bb81290" in text)
chk("frozen cable id C-RF-INT-1 named", "C-RF-INT-1" in text)
chk("no attenuator line invented (explicit non-line statement present)",
    "Inline pad / attenuator" in text or "attenuator — deliberately NOT a line" in text
    or "deliberately NOT a line" in text)

# ---- 8. scope leakage: exterior leg must be declared out, not listed -------
chk("exterior assembly C-RF-EXT-1 declared OUT of scope", "C-RF-EXT-1" in text)
chk("no C-RF-EXT-1 row in the BOM table",
    not any("C-RF-EXT-1" in r[0] for r in rows))

# ---- 9. feedthrough appears once, as one physical connector ----------------
# a row "is" the feedthrough when the item name in its first 80 chars names it;
# merely MENTIONING a feedthrough inside another row's rationale does not count.
ft_rows = [rid for r, rid in zip(rows, ids) if "feedthrough" in r[0][:80].lower()]
chk("bulkhead feedthrough is exactly ONE BOM line", len(ft_rows) == 1, str(ft_rows))
chk("that line is RF-3", ft_rows == ["RF-3"], str(ft_rows))
# and the RF-3 description must state both faces + the wall bore in one item
rf3 = rows[ids.index("RF-3")][0]
chk("RF-3 names all three interface points (IF-6 / IF-8 / IF-7) in one item",
    all(t in rf3 for t in ("IF-6", "IF-8", "IF-7")))
chk("RF-3 requires an unfiltered part", "UNFILTERED" in rf3.upper())
chk("RF-3 states F-F (jack-jack) explicitly",
    ("SMA-F to SMA-F" in rf3) or ("jack-jack" in rf3.lower()))

# ---- 10. mutually-exclusive candidates declared, not hidden ----------------
chk("RF-1a/RF-1b declared mutually exclusive",
    "mutually exclusive" in text.lower())

print("-" * 78)
print("%d checks, %d PASS, %d FAIL" % (CHECKS, CHECKS - len(FAILS), len(FAILS)))
if FAILS:
    for f in FAILS:
        print("  FAILED:", f)
    sys.exit(1)
sys.exit(0)
