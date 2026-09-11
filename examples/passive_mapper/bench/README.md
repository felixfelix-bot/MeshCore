# passive_mapper thermal calibration bench kit

The mapper's open-loop thermal model (`host/SelfCal.h`) is **inert until a
per-module calibration blob exists**: with no blob `k = 0`, the applied offset is
0 Hz, nothing compensates at altitude, and the radio silently degrades to the
BW125 fallback (2x noise bandwidth) whenever the die drops out of the ±90 C band
around `T0`. This directory is the measurement kit that produces that blob.

## The model and its sign convention (read this before trusting a number)

AT-cut crystal drift away from turnover is parabolic:

    drift_ppm(T)     = -k*(T - T0)^2      k = 0.02..0.06 ppm/C^2 (magnitude)

A slow crystal makes the synthesised LO land LOW, so a receiver *programmed* to
f0 actually centres its passband at `f0*(1+drift)`. To put the passband back on an
on-frequency (warm) transmitter the RX must be programmed HIGH by the magnitude
of the drift:

    applied_offset_ppm(T) = +k*(T - T0)^2 = -drift_ppm(T)

`k` is stored as a **magnitude and must be positive**; `cal` rejects negative k.
Everything in this kit reports *required compensation* (positive = program the RX
center high). `calshow`'s `off_hz` is the same quantity in Hz. The crystal drift
is `-off_hz`; do not confuse the two - the pre-2026-09-11 firmware applied the
drift itself and doubled the error instead of cancelling it.

Direction cross-check in the tree:
`RadioLibWrapper::setCenterFreqOffset()` -> `applyCenterFreqOffset()` ->
`((CustomLR2021*)_radio)->setFrequency(_base_freq_mhz + hz/1e6f)`, i.e. a
positive offset tunes the RX center **up**.

## What has to be measured, and by whom

This is **bench work for the operator** (Felix), not for an agent: it needs a
NiceRF LR2021 module, a way to hold it at temperature for hours, and a second
MeshCore node as a reference transmitter. No agent host in this fleet has the
module attached and none can put a board in a freezer. The scriptable parts
(parsers, fit, blob, estimators) are tested in software - see *Dry run*.

Deliverable per module: a `k`/`T0` pair, the fit residual, the measured
die-vs-crystal time constant `tau`, and the resulting `/selfcal.dat` blob.
The blob is **per module** - never copy one between modules.

## Bench setup

| Role | Item | Notes |
|---|---|---|
| DUT | NiceRF LR2021 board (SkyMapper Board A or a spare) running `pio run -e LR2021_passive_mapper -t upload` | serial CLI at 115200 8N1, `/dev/ttyACM0` unless a UART bridge moves it |
| Reference TX | any MeshCore node on the nominal frequency, SF8/BW62.5, transmitting continuously | **keep it at room temperature**: the model compensates for a *warm* transmitter seen by a *cold* RX. Freeze the reference too and the required compensation is ~0, because both ends drift together |
| Cold | freezer (-18..-20 C), dry-ice + IPA bath (~-78 C), or a chamber | must reach the expected flight minimum; a kitchen freezer alone is **not** enough for a stratospheric profile |
| Warm | hot plate / oven / warm room, +30..+40 C | at least one point **above** `T0`, or `T0` cannot be fitted (see below) |

Playback notes from the mule: a *sealed* bag around the module, because an
IPA/dry-ice bath plus a bare board equals condensation and ice on the RF path.
Expect 20-40 min per freezer setpoint for a true soak on a small module.

### Firmware CLI you will use

    status    # mode, bw (62.5 or 125 fallback), die_temp=, off_hz=, cal=yes/no
    calshow   # cal valid=.. k=.. T0=..C range=+/-90C die_temp=.. off_hz=..
    cal <k> <T0>   # persist the calibration (k > 0, ppm/C^2; T0 in C)
    reset     # zero the record counter (used for packet counting)

There is no dedicated offset-injection command: `edgescan` injects the offset
through `cal` itself, programming `T0_prog = die_temp + 15 C` so the parabola is
off its flat point (`dO/dk = (T-T0_prog)^2 = 225 ppm per unit k`).

## Protocol

### 1. Sweep points (`soak`)

    python3 examples/passive_mapper/bench/thermal_bench.py soak \
        --dut-port /dev/ttyACM0 \
        --setpoints "+25,+40,0,-20,-40,-55" \
        --stable-c 0.2 --window 10 --interval 10 --stable-secs 120 \
        --out soak.csv

Walks the setpoints, waits for the die temperature to hold inside 0.2 C across a
10-sample window, confirms for another 120 s, and records `die_temp_c` +
`off_hz` per point. Sweep as deep as the atmosphere will take it (-55 C covers
the ISA floor of -56.5 C with margin) and include at least one point above the
turnover.

### 2. Required compensation per point (`edgescan`)

    python3 examples/passive_mapper/bench/thermal_bench.py edgescan \
        --dut-port /dev/ttyACM0 --points "+40,+25,0,-20,-40,-55" \
        --t0-offset 15 --pkts 20 --capture-s 60 --out measured.csv

For each soaked point this searches the injected-offset band in which the DUT
still decodes the reference (coarse log grid, then a bisection of each 50 %
crossing), and reports the required compensation as the band midpoint. Run it
with the module **still at temperature** - do not let it warm up between steps.
Sanity check while it runs: at +40 C and at -55 C the printed compensation must
have opposite slope sign if the sweep brackets `T0`; if it is still rising at the
cold end, the sweep never crossed the turnover and `T0` is unidentifiable.

### 3. Fit and persist (`fit`)

    python3 examples/passive_mapper/bench/thermal_bench.py fit \
        --input measured.csv --out selfcal.dat
    # then, on the module:
    #   cal <k> <T0>          <- the exact line is printed by `fit`

`fit` solves `compensation_ppm = k*(T-T0)^2` (+ a bias term, which absorbs the
reference's own offset and the initial tolerance), prints the RMS residual and
warnings, writes the 15-byte blob, and prints the `cal` line. If the sweep only
covered one side of `T0`, re-run with `--t0-fixed <T0>` and treat `T0` as
assumed, not measured. Expect `k` in 0.02..0.06 ppm/C^2; a residual above
~5 ppm RMS inside the swept span means a bad point (usually a point that was not
soaked) - re-run that point rather than widening the tolerance.

Verify on the module:

    cal <k> <T0>      -> "persisted (valid=yes)"
    calshow           -> off_hz matches k*(die_temp-T0)^2, range=+/-90C
    status            -> bw=62.5  (no "(fallback)")

### 4. Die-vs-crystal lag (`ramp` + `hyst`)

The model drives its parabola from the LR2021 *die* sensor, but the crystal has
its own thermal mass, so the crystal temperature is `die_temp - tau*dT/dt`. A
sweep therefore shows hysteresis: one physical reception edge appears at a die
temperature `tau*rate` warmer on the heating sweep and `tau*rate` colder on the
cooling sweep, so

    tau = (edge_up - edge_down) / (rate_up + rate_down)

Log both directions with the reference transmitting and a **fixed** injected
offset (any `cal` whose requirement is within a half-window somewhere in the
swept span):

    python3 examples/passive_mapper/bench/thermal_bench.py ramp --direction up \
        --interval 5 --duration 600 --out ramp-up.csv
    python3 examples/passive_mapper/bench/thermal_bench.py ramp --direction down \
        --interval 5 --duration 600 --out ramp-down.csv
    python3 examples/passive_mapper/bench/thermal_bench.py hyst \
        --up ramp-up.csv --down ramp-down.csv

`hyst` prints `tau` and whether `SelfCal::TEMP_TC_SECS` (10 s) is consistent with
it. Both ramps must be the same span at comparable rates; if the printed
`tau` is negative the sweeps were swapped or a different band edge was picked up,
and no number is reported. A slow sweep is fine - the edge shift grows with the
rate - but a rate below ~0.002 K/s puts the shift under the sensor resolution.
If `tau` > 30 s, raise `TEMP_TC_SECS` to the measured value; if the lag is large
(at or above the ramp period) it is a real limit on the open-loop model: the EMA
cannot track a fast cool-down, and the BW125 fallback is what covers that window.

### 5. Record it (durable)

Add one row per module to `bench/RESULTS.md`, including the module ID
(EUI/serial + board label), the blob hex, `k`, `T0`, sweep span, residual, `tau`,
operator and date. The blob itself lives on the module's filesystem
(`/selfcal.dat` on the mapper) - the per-module record in the repo is what makes
it reproducible when a board is reflashed or swapped.

## Dry run (no hardware)

    python3 examples/passive_mapper/bench/test_calib.py        # 18 checks
    bash examples/passive_mapper/host/run_tests.sh             # host + bench kit
    # full simulated pipeline, known k=0.04/T0=22/tau=45:
    cd examples/passive_mapper/bench
    python3 thermal_bench.py soak     --simulate --out /tmp/soak.csv
    python3 thermal_bench.py edgescan --simulate --out /tmp/measured.csv
    python3 thermal_bench.py fit      --input /tmp/measured.csv --out /tmp/selfcal.dat
    python3 thermal_bench.py ramp --simulate --direction up   --out /tmp/up.csv
    python3 thermal_bench.py ramp --simulate --direction down --out /tmp/down.csv
    python3 thermal_bench.py hyst --up /tmp/up.csv --down /tmp/down.csv

Every device-touching subcommand accepts `--simulate`. The serial paths
themselves (`RawSerial`, termios) are not exercised by the tests and are only
proven by the first real bench run.

## Known limits

* The fit is only valid inside the swept span; the parabola is extrapolated
  beyond it, so a sweep that stops at -20 C is not a stratospheric calibration.
* `MAX_PPM` clamps the applied offset at 300 ppm; the ISA floor (`-56.5 C`) needs
  ~266 ppm from a +25 C turnover, so the clamp is not the binding constraint -
  the fit is.
* The die sensor sits next to the PA, so self-heating biases warm readings; the
  die-vs-crystal `tau` from step 4 is the honest measure of how much of the
  sensor's swing reaches the crystal.
* Cal is per module *and* per frequency plan: `k`/`T0` describe the crystal, not
  the firmware, so they survive a reflash but must be re-measured after a module
  swap or a board-level repair.
