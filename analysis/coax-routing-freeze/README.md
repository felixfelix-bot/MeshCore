# coax-routing-freeze

**Freeze the coax routing and the measurement setup — then every later reading
means something.**

This directory answers card `t_e5d5eaae`: route the coax bundle exactly as it
will be installed, *then* record the tool resolutions, bench conditions and cable
IDs that turn a raw reading into a value with an uncertainty. It exists because
bundle OD, tape pitch and forced-bend radius are properties of the **installed
routing** — measure them before the routing is final and they describe nothing.

## Current state: **BLOCKED — awaiting physical observation**

```
$ python3 validate_setup_record.py
VERDICT: BLOCKED (2)
  R2 $: 33 field(s) still unset -> setup is NOT frozen
```

**Every physical value in this package reads `<<UNSET>>`. None of them was
measured, and none may be inferred, estimated or taken from a datasheet.**
`evidence/HOST_CAPABILITY.txt` records why: no instrument is attached, the one
camera node returns a scene-less frame (YAVG 0.21/255, 4 grey levels), and a scan
of 182 boards × 8 862 task records found no measured value for this run.

## Files

| File | Role |
|---|---|
| `SETUP_FREEZE_RECORD.md` | **the deliverable** — the frozen-setup record: routing (§a), caliper resolution (§b), tape resolution (§c), bench conditions (§d), cable IDs (§e), change-flag rule (§6) |
| `setup_state.json` | the machine-readable half — edit this, then update the `.md` |
| `validate_setup_record.py` | the acceptance gate: exit `0` COMPLETE / `1` INVALID / `2` BLOCKED |
| `test_validate_setup_record.py` | 40 tests, one mutant per acceptance criterion |
| `scripts/probe_host_capability.sh` | re-runnable, read-only host-capability probe |
| `scripts/frame_luma.py` | frame-brightness statistics (why the camera cannot serve as an instrument) |
| `evidence/HOST_CAPABILITY.txt` | the probe's real output |

## How to use it (at the bench)

```sh
cd analysis/coax-routing-freeze
# 1. route + tie + loom the bundle exactly as installed  (SETUP_FREEZE_RECORD.md §2)
# 2. fill every <<UNSET>> in setup_state.json and in the .md
python3 validate_setup_record.py            # names every field still missing
python3 validate_setup_record.py --emit frozen_constants.json
python3 test_validate_setup_record.py       # 40 tests
```

The gate refuses to say COMPLETE while anything is unset, refuses a value that is
not a **number with units**, and **recomputes** tape pitch (`span / wraps`) and
bend radius (`chord²/(8·sagitta) + sagitta/2`) so an estimated value cannot pass
as a measured one.

## The one thing left

A person at the bench with the caliper and tape named in §3–§4 of the record.
See `../../REPORT.md` for the hand-off.
