#!/usr/bin/env python3
"""Re-extract every citation block from contract_conversion_inventory.md and
byte-compare each against the contract source. Exit 0 only if ALL blocks
match. Also re-hash the contract copy and compare with the pinned blob."""
import hashlib
import re
import sys
from pathlib import Path

SRC = Path("/home/c03rad0r/worktrees/t_bb4bbf91/bench/atcut-fit/CAL-CLI-SPEC.md")
INV = Path("/home/c03rad0r/worktrees/t_bb4bbf91/contract_conversion_inventory.md")
PINNED_BLOB = "378e30311600113ebf32f61979adb5ffb25eb56b"

src_lines = SRC.read_text().splitlines()
raw = SRC.read_bytes()
blob = hashlib.sha1(("blob %d\0" % len(raw)).encode() + raw).hexdigest()
blob_ok = blob == PINNED_BLOB

inv = INV.read_text()

# match blocks like:  > **bench/atcut-fit/CAL-CLI-SPEC.md:59-63**  /  :118
pat = re.compile(
    r"> \*\*bench/atcut-fit/CAL-CLI-SPEC\.md:(\d+)(?:-(\d+))?\*\*\n((?:>.*\n?)+?)(?=\n\n|\n[^>]|\Z)"
)
n_ok = n_fail = 0
fails = []
for m in pat.finditer(inv):
    a = int(m.group(1))
    b = int(m.group(2) or m.group(1))
    body = m.group(3)
    # drop the leading bare ">" continuation line that follows the header,
    # then strip the "> " prefixes (and bare ">" continuation lines)
    qlines = body.splitlines()[1:]
    spliced = "\n".join(
        (ln[2:] if ln.startswith("> ") else "") for ln in qlines
    )
    expected = "\n".join(src_lines[a - 1 : b])
    if spliced.rstrip("\n") == expected.rstrip("\n"):
        n_ok += 1
    else:
        n_fail += 1
        fails.append((a, b, spliced[:80], expected[:80]))

print(f"contract sha1 blob: {blob}  pinned-match={blob_ok}")
print(f"citation blocks byte-verified OK: {n_ok}   FAILED: {n_fail}")
for f in fails:
    print("FAIL", f)
# sanity: no invented function names outside the 9 entries
names = re.findall(r"^### `?([a-z0-9_]+)`?$", inv, re.M)
print("entry headings:", names)
gaps = re.findall(r"\*\*G(\d) `([a-z0-9_]+)`\*\*", inv)
print("gaps:", [g[1] for g in gaps], f"({len(gaps)} total)")
sys.exit(0 if (n_fail == 0 and blob_ok) else 1)