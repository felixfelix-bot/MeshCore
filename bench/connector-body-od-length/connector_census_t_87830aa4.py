#!/usr/bin/env python3
"""Connector-body measurement readiness census + connector-run arithmetic.

Card: meshcore t_87830aa4 -- "Measure connector body OD and length, matched to
cable ID".

Stdlib only. No network, no clock, no randomness -> reruns are byte-identical.
It does NOT measure anything (no connector, no cable and no caliper exists on
this host); it (a) re-runs the physical census that makes measurement
impossible here, and (b) audits the connector census arithmetic for the frozen
variant-B coax run so the "every connector appears exactly once" acceptance
item is checkable, not asserted.
"""
import os
import subprocess
import sys

HOME = os.path.expanduser("~")
REPO = os.path.join(HOME, "repos", "meshcore")

FAIL = []


def check(label, ok, detail):
    FAIL.append(label) if not ok else None
    print(f"[{'PASS' if ok else 'FAIL'}] {label}: {detail}")


def sh(cmd):
    try:
        p = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=60)
        return (p.stdout or "").strip()
    except Exception as e:  # timeout / missing binary
        return f"<error: {e}>"


print("=" * 78)
print("SECTION 1 -- FRESH PHYSICAL CENSUS (run this session)")
print("=" * 78)

print("\n-- lsusb --")
print(sh("lsusb") or "<empty>")

print("\n-- serial / instrument buses --")
for pat in ("/dev/serial/by-id", "/dev/usbtmc*", "/dev/gpib*", "/dev/ttyACM*", "/dev/ttyUSB*"):
    out = sh(f"ls -d {pat} 2>&1")
    print(f"  {pat:22s} -> {out}")

print("\n-- camera --")
for pat in ("/dev/video*", "/dev/media*", "/sys/class/video4linux"):
    out = sh(f"ls -d {pat} 2>&1")
    print(f"  {pat:22s} -> {out}")

print("\n-- measuring-tool assets on disk (bounded, name match) --")
names = ("*caliper*", "*micrometer*", "*vernier*", "*tape-measure*", "*tapescan*")
hits = []
# pruned, shallow walk: a real instrument asset would sit in a project/report dir,
# not buried in a build cache; pruning keeps the census fast and deterministic.
prune = ("-not -path '*/.git/*' -not -path '*/.cache/*' -not -path '*/.local/*' "
         "-not -path '*/node_modules/*' -not -path '*/.venv/*' -not -path '*/venv/*' "
         "-not -path '*/__pycache__/*' -not -path '*/.mozilla/*' -not -path '*/.config/*'")
# Targeted roots only: a walk of all of $HOME is dominated by ~/worktrees
# (~470 repo checkouts) and would take minutes for no added coverage -- a real
# instrument asset would live in a report, repo, or kanban attachment dir.
roots = (f"{HOME} -maxdepth 1", f"{HOME}/reports -maxdepth 4",
         f"{HOME}/repos -maxdepth 4", f"{HOME}/.hermes -maxdepth 4",
         f"{HOME}/Documents -maxdepth 3", f"{HOME}/Downloads -maxdepth 3")
or_expr = " -o ".join(f"-iname '{n}'" for n in names)
for root in roots:
    out = sh(
        f"timeout 20 find {root} -type f \\( {or_expr} \\) {prune} 2>/dev/null | head -20"
    )
    if out:
        hits.append(out)
print("  caliper/micrometer/vernier/tape assets: " + ("\n".join(hits) if hits else "ZERO HITS"))
check("no measuring instrument asset on host", not hits, f"{len(hits)} hit groups")

print("\n-- physical RF coax / connector assets in the project repo (bounded) --")
# files only: bench/ directories are NAMED for the subject (e.g.
# bench/sma-ice-bridging-failure-modes/) -- a directory name is not an asset.
out = sh(
    f"timeout 20 find {REPO} -maxdepth 5 -type f \\( -iname '*rg316*' -o -iname '*rg-316*' "
    f"-o -iname '*sma*' -o -iname '*.s2p' \\) -not -path '*/.git/*' 2>/dev/null | head -20"
)
print("  " + (out if out else "ZERO HITS"))
check("no physical RF coax/connector asset in repo tree", not out, out or "zero")

print("\n-- connector / cable photographs anywhere in reports or kanban home --")
out = sh(
    f"timeout 25 find {HOME}/reports {HOME}/.hermes/kanban -maxdepth 5 "
    f"\\( -iname '*connector*.jpg' -o -iname '*connector*.png' -o -iname '*_close.jpg' "
    f"-o -iname '*_wide.jpg' \\) 2>/dev/null | head -10"
)
print("  " + (out if out else "ZERO HITS"))
check("no connector photograph exists", not out, out or "zero")

print("\n-- procurement records (a part on order would carry a P/N) --")
out = sh(
    f"timeout 25 grep -rl --include='*.csv' --include='*.json' --include='*.txt' "
    f"-e 'ACX-1169' -e '132134' {REPO}/bench 2>/dev/null | head -10"
)
print("  files naming a representative SMA MPN: " + (out.replace(chr(10), ", ") if out else "none (MPN TBD)"))
print("  (a hit means the class is CITED in a report, not that a part exists)")

print()
print("=" * 78)
print("SECTION 2 -- CONNECTOR CENSUS ARITHMETIC (frozen variant-B coax run)")
print("=" * 78)

# Frozen chain, bench/connector-adapter-bom/REPORT.md STEP 3 (committed):
#   DUT J1 [SMA-F jack edge-launch] -> C-RF-INT-1 [SMA-M plug === SMA-M plug]
#     -> SMA bulkhead feedthrough [SMA-F jack | wall | SMA-F jack]
#     -> C-RF-EXT-1 [SMA-M plug === SMA-M plug] -> REF-TX J1 [SMA-F jack]
#
# (connector_id, cable_id_terminated, kind, coaxial_interfaces)
RUN = [
    ("CN-1  DUT carrier J1 (\"SMA-868\") edge-launch jack", "C-RF-INT-1", "board jack", 1),
    ("CN-2  C-RF-INT-1 plug, DUT end", "C-RF-INT-1", "cable plug", 1),
    ("CN-3  C-RF-INT-1 plug, bulkhead end", "C-RF-INT-1", "cable plug", 1),
    ("CN-4  SMA bulkhead feedthrough, jack-jack panel mount",
     "C-RF-INT-1 (interior interface) + C-RF-EXT-1 (exterior interface)",
     "bulkhead, ONE body / TWO interfaces", 2),
    ("CN-5  C-RF-EXT-1 plug, bulkhead end", "C-RF-EXT-1", "cable plug", 1),
    ("CN-6  C-RF-EXT-1 plug, ref-TX end", "C-RF-EXT-1", "cable plug", 1),
    ("CN-7  REF-TX J1 edge-launch jack", "C-RF-EXT-1", "board jack", 1),
]
CONDITIONAL = [
    ("CN-8  connector saver (BOM B6), SMA M-F bullet adapter at DUT J1",
     "C-RF-INT-1", "adapter, CONDITIONAL on B6 decision", 2),
]
OUT_OF_RUN = [
    ("B7  SMA 50-ohm termination load, DUT J2 (2.4 GHz port)", "not on the coax run: J2 is not part of the conducted path"),
    ("B8  SMA dust caps x4", "protective caps, not connectors; they cover interfaces when UNMATED"),
    ("C-SER-1 / C-SER-2 USB-C plugs", "USB-C serial cable ends -- not coax connectors, not on the coax run"),
    ("U.FL (I-PEX) receptacle, ESP32-C3 SuperMini", "WiFi/BLE radio, not on the LR2021 868 MHz measurement path"),
    ("FT-1 .. FT-5 chamber bulkhead feedthroughs", "all five states are NON-EXISTENT -- no chamber, no bulkhead"),
]

print("\nBodies in the coax run (each listed exactly once):")
for cid, cable, kind, ifs in RUN:
    print(f"  {cid:60s} | {cable:56s} | {kind} | if={ifs}")
n_bodies = len(RUN)
n_halves = sum(r[3] for r in RUN)
print(f"\n  bodies = {n_bodies}; interface-halves = {n_halves}; joints = {n_halves // 2}")

print("\nConditional body (in the run ONLY if BOM B6 is used):")
for cid, cable, kind, ifs in CONDITIONAL:
    print(f"  {cid:60s} | {cable:56s} | {kind} | if={ifs}")
print(f"  bodies_if_B6_used = {n_bodies + len(CONDITIONAL)}")

print("\nExplicitly OUT of the run (so no connector is silently missing or doubled):")
for item, why in OUT_OF_RUN:
    print(f"  {item:60s} | {why}")

print("\n-- identity checks --")
bulk_rows = [r for r in RUN if "bulkhead" in r[2]]
check("bulkhead counted once, not twice",
      len(bulk_rows) == 1 and bulk_rows[0][3] == 2,
      "CN-4 carries 2 coaxial interfaces in 1 body row")
check("interface arithmetic closes", n_halves == 8 and n_halves // 2 == 4,
      f"{n_bodies} bodies -> {n_halves} halves -> {n_halves // 2} mating joints (J1|plug, plug|bulkhead, bulkhead|plug, plug|J1)")
check("every run body is tied to a cable ID", all(r[1] for r in RUN), "no orphan connector")
check("each of the 2 RF cables terminates exactly 2 cable-end plugs",
      sum(1 for r in RUN if r[1] == "C-RF-INT-1" and r[2] == "cable plug") == 2
      and sum(1 for r in RUN if r[1] == "C-RF-EXT-1" and r[2] == "cable plug") == 2,
      "C-RF-INT-1: CN-2,CN-3 ; C-RF-EXT-1: CN-5,CN-6")
cable_ids = set()
for r in RUN:
    for tok in r[1].replace("(", " ").replace(")", " ").split():
        if tok.startswith("C-RF-"):
            cable_ids.add(tok.rstrip(",;"))
check("cable-ID coverage complete", sorted(cable_ids) == ["C-RF-EXT-1", "C-RF-INT-1"],
      f"frozen coax IDs present: {sorted(cable_ids)}")
check("measured numbers available for any body", False,
      "0 of 7 bodies have a measured OD or length -- no part exists (UNKNOWN, see report)")

print("\n" + "=" * 78)
print("RESULT: census rerun complete; connector-run census closes arithmetically.")
print(f"        checks failed: {len(FAIL)}" + (f" -> {FAIL}" if FAIL else ""))
print("        NOTE: the one expected FAIL is the honest measurement gap:")
print("        no connector body OD / length is measurable on this host.")
print("=" * 78)
sys.exit(0)
