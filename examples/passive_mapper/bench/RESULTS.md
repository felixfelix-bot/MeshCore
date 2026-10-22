# passive_mapper calibration records (per module)

One row per calibrated module. `k`/`T0` describe **that module's crystal** - do
not copy a row to another board. `blob_hex` is the 15-byte `/selfcal.dat`
content; the authoritative copy is the file on the module itself, this table is
how you rebuild it after a reflash or a board swap.

Protocol: see `README.md`. Blob layout: `2x f32 (k, T0)` + `u16 magic 0x5343` +
`u8 version`, little-endian.

| module id (EUI/serial) | board label | date | k (ppm/C^2) | T0 (C) | sweep span (C) | residual (ppm rms) | tau (s) | TEMP_TC_SECS | blob_hex | operator | notes |
|---|---|---|---|---|---|---|---|---|---|---|---|
| _not yet measured_ | SkyMapper Board A (LR2021) | | | | | | | 10 | | | pending: needs the freezer/dry-ice sweep, see the card |

## How to fill a row

```bash
cd examples/passive_mapper/bench
python3 thermal_bench.py fit --input measured.csv --out selfcal.dat   # prints k, T0, residual, blob hex, cal line
python3 thermal_bench.py hyst --up ramp-up.csv --down ramp-down.csv   # prints tau
python3 -c "import calib; print(calib.pack_blob(K, T0, version=1).hex())"
```

Then persist on the module: `cal <k> <T0>`, and confirm `calshow` shows
`valid=yes` with the expected `off_hz`.

## Assumptions recorded with every run

* Reference transmitter held at room temperature (the model compensates a warm
  TX seen by a cold RX).
* Sweep reached at least the expected flight minimum; the fit is not valid
  outside the swept span.
* `T0` was bracketed by the sweep (points on both sides of turnover); a
  single-sided sweep must be recorded as `--t0-fixed` with the assumed value.
