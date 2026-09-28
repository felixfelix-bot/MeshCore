# Calibration-command emission sites — meshcore-fork-fix

Enumeration only (no fixes). Every `path:line` below is pinned to the committed
tree named in this header and is reproducible with the listed grep commands.

## Repository inspected

- Repo root: `/home/c03rad0r/repos/meshcore-fork-fix`
- Remote: origin = https://github.com/c03rad0r/MeshCore.git
- Primary branch inspected: `main`
- Commit SHA: `931ec31af7c331a5fc21df0c84ef4b51f58645c7` (`931ec31`, "analysis: tighten claim mappings and flag unverified figures in citation list")
- Linked branch (named by the task): `worker-base/dut-rf-port-evidence` @ `07a3ca9e05b0ab23b878200b2c44b04e08131972` (`07a3ca9`), checked out in worktree `/home/c03rad0r/worktrees/dut-rf-port-evidence/`

### Branches checked (scope clause)

1. `main` @ `931ec31` — all greps pinned to this tree (`git grep … HEAD`).
2. `worker-base/dut-rf-port-evidence` @ `07a3ca9` — greps re-run on this tree.
   - `git merge-base --is-ancestor 07a3ca9 931ec31` → YES: the linked branch is an ancestor of main.
   - `git diff --stat 07a3ca9 931ec31 -- src lib examples test arch` → **empty**: all code is byte-identical between the two branches (main adds only `analysis/failure-modes/sma-coax-interface-citations.md`).
   - `\bcal\b` on 07a3ca9: 0 hits (same as main). `calibrat` in src+examples: same sites as main.
3. Branches reachable from the linked branch = the linked branch's full history (since it is an ancestor of main, that history is also reachable from main). Verified additionally:
   - Remote tips present locally and **ancestors of the linked branch** (hence covered by its tree): `91f3fa0` (`default-scope`), `8fc2da5` (`flood.max.advert`).
   - Delta check 91f3fa0 → 07a3ca9: no calibration emission site was deleted on the way (calibrat hits 20 → 23, additions only).
   - History pickaxe over the reachable range: `git log --oneline 07a3ca9 -G'calibrat' -- src` → 8 commits (a2dc2eb, b2032e1, f54948e, 85f764a, 9bae9d0, 27f7326, c7be216, f86e6c0). No commit ever introduced a text `cal` command.
   - Remote tips NOT inspectable locally (missing git objects, fetch failed): `dev` @ `5f3b7f2`, `feature/nicerf-lr2021-variant` @ `1ed56aa`, `fix/2739-review-fixes` @ `05ad173`, `gh-pages` @ `efb883d`. See Caveats.

### Exclusions applied

- `vendor/`, `node_modules/`: 0 such paths in the tree.
- `.git/`: not grepped.
- Generated lockfiles: none in tree. (`src/helpers/config/generic_33v_3s_28d/bsec_iaq.txt` is a generated BSEC config blob, referenced at EnvironmentSensorManager.cpp:24 — recorded, not a code site.)
- Vendored third-party code kept in the fork's tree (`lib/nrf52` SoftDevice headers, `lib/ed25519`, `arch/stm32` LittleFS port): hits there are recorded as excluded — they contain no emission sites (SoftDevice RC-calibration API structs and comments only).

## Headline finding

**No text-based `cal` command emitter exists** in this repo, on either branch.
There is no code site that builds or sends a string command line starting with
`cal `, no `"cal"`/`'cal'` literal, and no `cal` CLI sub-command. Verified by
grep (all zero-hit, see Grep log) AND by exhaustive enumeration of every
command-dispatch table:

- `CommonCLI::handleCommand` @ src/helpers/CommonCLI.cpp:215 — full token list enumerated (poweroff, shutdown, reboot, clkreboot, advert.zerohop, advert, clock sync, start ota, clock, time, neighbors, neighbor.remove, tempradio, password, clear stats, get, set, erase, ver, board, sensor get/set/list, region*, gps*, powersaving*). No `cal`.
- `CommonCLI::handleSetCmd` @ :481 / `handleGetCmd` @ :768 — every config key enumerated. No cal key.
- Example command handlers (companion_radio `checkCLIRescueCmd` @ MyMesh.cpp:2009, simple_secure_chat main.cpp:425+, room server / repeater `get acl` handlers). No cal.
- `docs/cli_commands.md` — full `####` command index enumerated. No cal command documented.

What DOES exist is a full **radio/sensor calibration command infrastructure**
at the driver layer (SPI frames to the LoRa chip, I2C commands to the RAK12035
soil-moisture sensor, and periodic noise-floor/AGC calibration triggers).
Those emitters are enumerated below, ordered by emission relevance.

## Ordered emission-site list

### TIER 1 — Direct emitters (send a calibration command to hardware or into the radio pipeline)

All C++. Snippets are byte-exact from the tree at `931ec31`.

1. `src/helpers/radiolib/SX126xReset.h:13` — fn `sx126xResetAGC(SX126x* radio)` (inline, def :8)
   `radio->mod->SPIwriteStream(RADIOLIB_SX126X_CMD_CALIBRATE, &calData, 1, true, false);`
   Emits the SX126x `Calibrate` SPI command with `calData = RADIOLIB_SX126X_CALIBRATE_ALL` (0x7F, set at :12) — ADC/PLL/image calibration.

2. `src/helpers/radiolib/SX126xReset.h:23` — fn `sx126xResetAGC` (def :8)
   `radio->calibrateImage(radio->freqMHz);`
   Emits the image-rejection calibration command re-targeted to the actual operating frequency (the 0x7F default covers only 902–928 MHz, per comment :21).

3. `src/helpers/radiolib/LR11x0Reset.h:12` — fn `lr11x0ResetAGC(LR11x0* radio, float freqMHz)` (inline, def :8)
   `radio->calibrate(RADIOLIB_LR11X0_CALIBRATE_ALL);`
   Emits the LR11x0 calibrate-all command (0x3F).

4. `src/helpers/radiolib/LR11x0Reset.h:16` — fn `lr11x0ResetAGC` (def :8)
   `radio->calibrateImageRejection(freqMHz - 4.0f, freqMHz + 4.0f);`
   Emits the LR11x0 image-rejection calibration for a 4 MHz band around the operating frequency.

5. `src/helpers/sensors/RAK12035_SoilMoisture.cpp:259` — fn `RAK12035_SoilMoisture::set_humidity_full(uint16_t full)` (def :253, "Command 07")
   `if (!write_rak12035(SOILMOISTURESENSOR_SET_WET_CAL, buf, 2)) {`
   Emits I2C calibration-write command 0x07 (WET calibration) with a 2-byte payload.

6. `src/helpers/sensors/RAK12035_SoilMoisture.cpp:275` — fn `RAK12035_SoilMoisture::set_humidity_zero(uint16_t zero)` (def :269, "Command 08")
   `if (!write_rak12035(SOILMOISTURESENSOR_SET_DRY_CAL, buf, 2)) {`
   Emits I2C calibration-write command 0x08 (DRY calibration) with a 2-byte payload.

7. `src/helpers/sensors/RAK12035_SoilMoisture.cpp:347` — fn `RAK12035_SoilMoisture::get_humidity_full()` (def :343, "Command 0A")
   `if (!read_rak12035(SOILMOISTURESENSOR_GET_WET_CAL, buf, 2)) {`
   Emits I2C calibration-read command 0x0A (WET calibration value).

8. `src/helpers/sensors/RAK12035_SoilMoisture.cpp:363` — fn `RAK12035_SoilMoisture::get_humidity_zero()` (def :359, "Command 0B")
   `if (!read_rak12035(SOILMOISTURESENSOR_GET_DRY_CAL, buf, 2)) {`
   Emits I2C calibration-read command 0x0B (DRY calibration value).

9. `src/Dispatcher.cpp:68` — fn `Dispatcher::loop()` (def :66)
   `_radio->triggerNoiseFloorCalibrate(getInterferenceThreshold());`
   Emits the periodic noise-floor calibration trigger to the radio driver (cadence `NOISE_FLOOR_CALIB_INTERVAL`, 2000 ms, set at :15-16), parameterized by the interference threshold (CLI `int.thresh`).

10. `examples/kiss_modem/main.cpp:147` — fn `loop()` (def :126)
    `radio_driver.triggerNoiseFloorCalibrate(0);`
    Example-side periodic noise-floor calibration trigger (cadence `NOISE_FLOOR_CALIB_INTERVAL_MS` 2000, :21).

11. `src/Dispatcher.cpp:133` — fn `Dispatcher::loop()` (def :66)
    `_radio->resetAGC();`
    Emits the AGC-reset chain, which cascades to the SPI Calibrate emitters (#1–4) via the chip-specific `doResetAGC()` overrides (#13–14). Guarded by :132 `if (getAGCResetInterval() > 0 && millisHasNowPassed(next_agc_reset_time))`.

12. `examples/kiss_modem/main.cpp:132` — fn `loop()` (def :126)
    `radio_driver.resetAGC();`
    Example-side AGC-reset → calibration chain trigger (cadence `AGC_RESET_INTERVAL_MS` 30000, :22).

13. `src/helpers/radiolib/CustomSX1262Wrapper.h:41` — fn `CustomSX1262Wrapper::doResetAGC()` (override)
    `void doResetAGC() override { sx126xResetAGC((SX126x *)_radio); }`
    Routes the AGC reset to the SX126x Calibrate SPI emitters (#1–2). Identical sibling sites:
    - `src/helpers/radiolib/CustomSX1268Wrapper.h:38` — `void doResetAGC() override { sx126xResetAGC((SX126x *)_radio); }`
    - `src/helpers/radiolib/CustomLLCC68Wrapper.h:34` — same
    - `src/helpers/radiolib/CustomSTM32WLxWrapper.h:35` — same

14. `src/helpers/radiolib/CustomLR1110Wrapper.h:19` — fn `CustomLR1110Wrapper::doResetAGC()` (override)
    `void doResetAGC() override { lr11x0ResetAGC((LR11x0 *)_radio, ((CustomLR1110 *)_radio)->getFreqMHz()); }`
    Routes the AGC reset to the LR11x0 calibrate emitters (#3–4).

15. `src/helpers/sensors/RAK12035_SoilMoisture.cpp:139` and `:142` — fn `RAK12035_SoilMoisture::begin(uint8_t addr)` (def :86)
    `     set_humidity_full(_wet);` (:139, `_wet = 2000` at :138)
    `   set_humidity_zero(_dry);` (:142, `_dry = 50` at :141)
    Build-flag-gated (`#if ENABLE_RAK12035_CALIBRATION` at :137) direct emission of both sensor calibration commands at init. NOTE: in the default build this block is compiled out — see #22 for the typo'd guard macro.

16. `src/helpers/radiolib/RadioLibWrappers.cpp:58` — fn `RadioLibWrapper::triggerNoiseFloorCalibrate(int threshold)` (def :58)
    `_threshold = threshold;` … `if (_num_floor_samples >= NUM_NOISE_FLOOR_SAMPLES) {  // ignore trigger if currently sampling`
    The radio-driver sink for the trigger (#9, #10): puts noise-floor calibration sampling into (re)converge mode.

17. `src/helpers/radiolib/RadioLibWrappers.cpp:74` — fn `RadioLibWrapper::resetAGC()` (def :70)
    `doResetAGC();`
    Generic front door that dispatches to the chip-specific calibration-reset emitters (#13–14); also resets the noise-floor calibration state at :81–83.

### TIER 2 — Builders (assemble the payloads/state the emitters use)

18. `src/helpers/sensors/RAK12035_SoilMoisture.cpp:255-257` — fn `set_humidity_full` (def :253)
    `uint8_t buf[2]; buf[0] = (full >> 8) & 0xFF;   // High byte` / `buf[1] = full & 0xFF;`
    Builds the 2-byte payload for the WET calibration command written at :259.

19. `src/helpers/sensors/RAK12035_SoilMoisture.cpp:271-273` — fn `set_humidity_zero` (def :269)
    `uint8_t buf[2]; buf[0] = (zero >> 8) & 0xFF;   // High byte` / `buf[1] = zero & 0xFF;`
    Builds the 2-byte payload for the DRY calibration command written at :275.

20. `src/helpers/sensors/RAK12035_SoilMoisture.cpp:287-288` — fn `RAK12035_SoilMoisture::get_sensor_moisture()` (def :284)
    `_wet_cal = get_humidity_full();` / `_dry_cal = get_humidity_zero();`
    Loads the calibration values into members `_wet_cal`/`_dry_cal` (declared :96-97) by emitting the read commands (#7, #8); the moisture output is then clamped between the calibration points (comment at :307).

21. `src/helpers/sensors/RAK12035_SoilMoisture.cpp:522` and `:541` — fns `read_rak12035(uint8_t cmd, uint8_t *data, uint8_t length)` (def :522) and `write_rak12035(uint8_t cmd, uint8_t *data, uint8_t length)` (def :541)
    `_i2c->beginTransmission(_addr);`
    The shared low-level I2C transport every RAK12035 calibration command passes through.

22. `src/helpers/sensors/RAK12035_SoilMoisture.h:37-41` — file scope
    `#define SOILMOISTURESENSOR_SET_WET_CAL       0x07   // (w)   2 bytes`
    `#define SOILMOISTURESENSOR_SET_DRY_CAL       0x08   // (w)   2 bytes`
    `#define SOILMOISTURESENSOR_GET_WET_CAL       0x0A   // (r)   2 bytes`
    `#define SOILMOISTURESENSOR_GET_DRY_CAL       0x0B   // (r)   2 bytes`
    The calibration command opcodes used by #5–8.

23. `src/helpers/sensors/RAK12035_SoilMoisture.h:19-20` — file scope
    `#ifndef ENABLE_RAK12025_CALIBRATION`
    `#define ENABLE_RAK12025_CALIBRATION = 0  // Used to generate Calibration Version of Firmware`
    ENUMERATION NOTE (observed, not fixed): the header guard spells the macro `ENABLE_RAK12025_CALIBRATION` ("12025"), while every consumer (`RAK12035_SoilMoisture.cpp:137`, `EnvironmentSensorManager.cpp:453,464`) tests `ENABLE_RAK12035_CALIBRATION` ("12035"). The macro the .cpp tests is therefore never defined by the header, so `#if ENABLE_RAK12035_CALIBRATION` evaluates 0 in the default build and the begin() calibration emission (#15) and the calibration telemetry channel are compiled out unless the user passes `-D ENABLE_RAK12035_CALIBRATION=1` (the broken `= 0` define form would also not survive `-D` style usage cleanly).

24. `src/Dispatcher.cpp:15-16` — file scope
    `#ifndef NOISE_FLOOR_CALIB_INTERVAL` / `  #define NOISE_FLOOR_CALIB_INTERVAL   2000     // 2 seconds`
    Sets the emission cadence of #9.

25. `examples/kiss_modem/main.cpp:21,27,28` — file scope
    `#define NOISE_FLOOR_CALIB_INTERVAL_MS 2000` … `static uint32_t next_noise_floor_calib_ms = 0;` … `static uint32_t next_agc_reset_ms = 0;`
    Cadence constants + scheduler state for #10 and #12.

26. `src/Dispatcher.h:66-68` — class `Dispatcher` (interface)
    `virtual void triggerNoiseFloorCalibrate(int threshold) { }` / `virtual void resetAGC() { }`
    The virtual emission interface #9/#11 call through.

27. `src/Dispatcher.h:122` — class `Dispatcher` (state)
    `unsigned long next_floor_calib_time, next_agc_reset_time;`
    Scheduler state for the two calibration cadences (guarded at Dispatcher.cpp:67 and :132).

28. `src/helpers/radiolib/RadioLibWrappers.h:20,51,52` — class declarations
    `virtual void doResetAGC();` / `void triggerNoiseFloorCalibrate(int threshold) override;` / `void resetAGC() override;`
    Declarations of the radio-driver emission surface.

29. `src/helpers/radiolib/RadioLibWrappers.cpp:81-83` — fn `RadioLibWrapper::resetAGC()` (def :70)
    `_noise_floor = 0;` / `_num_floor_samples = 0;` / `_floor_sample_sum = 0;`
    Resets the noise-floor calibration sampling state after an AGC reset so it reconverges from scratch.

30. `src/helpers/sensors/EnvironmentSensorManager.cpp:466-467` — fn `query_rak12035(uint8_t ch, uint8_t sub_ch, CayenneLPP& lpp)` (static, def :459)
    `float wet = RAK12035.get_humidity_full();` / `float dry = RAK12035.get_humidity_zero();`
    Emits the calibration-read commands (#7, #8) to publish wet/dry calibration values as telemetry (guarded `#ifdef ENABLE_RAK12035_CALIBRATION` at :464).

31. `src/helpers/sensors/EnvironmentSensorManager.cpp:453-454` — fn `init_rak12035(TwoWire* wire, uint8_t addr)` (static, def :453)
    `#ifdef ENABLE_RAK12035_CALIBRATION` / `  return 2;  // moisture channel + calibration channel`
    Build-flag plumbing that reserves the calibration telemetry channel.

### TIER 3 — Format helpers / calibration-adjacent CLI surface (no `cal` command exists)

32. `src/helpers/CommonCLI.cpp:749-756` — fn `CommonCLI::handleSetCmd(...)` (def :481)
    `} else if (memcmp(config, "adc.multiplier ", 15) == 0) {` … `sprintf(reply, "OK - multiplier set to %.3f", _prefs->adc_multiplier);`
    `set adc.multiplier` — the battery-reading fine-tune (documented "Fine-tune the battery reading", docs/cli_commands.md:375). The closest thing to a calibration command in the CLI.

33. `src/helpers/CommonCLI.cpp:895-900` — fn `CommonCLI::handleGetCmd(...)` (def :768)
    `} else if (memcmp(config, "adc.multiplier", 14) == 0) {` … `sprintf(reply, "> %.3f", adc_mult);`
    Get side of #32.

34. `src/helpers/CommonCLI.cpp:503-506` — fn `handleSetCmd` (def :481)
    `} else if (memcmp(config, "agc.reset.interval ", 19) == 0) {` … `sprintf(reply, "OK - interval rounded to %d", ((uint32_t) _prefs->agc_reset_interval) * 4);`
    Sets the cadence of the AGC-reset/calibration chain (#11).

35. `src/helpers/CommonCLI.cpp:499-502` — fn `handleSetCmd` (def :481)
    `} else if (memcmp(config, "int.thresh ", 11) == 0) {` … `_prefs->interference_threshold = atoi(&config[11]);`
    Sets the threshold parameter that `Dispatcher::loop()` passes into `triggerNoiseFloorCalibrate()` (#9) — directly parameterizes the calibration emission.

36. `src/helpers/CommonCLI.cpp:565-569` — fn `handleSetCmd` (def :481)
    `} else if (memcmp(config, "radio.rxgain ", 13) == 0) {` … `_callbacks->setRxBoostedGain(_prefs->rx_boosted_gain);`
    `set radio.rxgain` — RX boosted-gain (gain-calibration-adjacent) setting.

37. `src/helpers/CommonCLI.cpp:805-806` — fn `handleGetCmd` (def :768)
    `} else if (memcmp(config, "radio.rxgain", 12) == 0) {` / `sprintf(reply, "> %s", _prefs->rx_boosted_gain ? "on" : "off");`
    Get side of #36.

38. `src/helpers/CommonCLI.cpp:338` and `:342` — fn `handleCommand` (def :215), `sensor list` branch (dispatch at :328)
    `sprintf(dp, "%d vars\n", end);` … `sprintf(dp, "%s=%s\n", _sensors->getSettingName(i), _sensors->getSettingValue(i));`
    The ONLY sites in src/ that sprintf a multi-line reply with trailing `\n`. Recorded because the task's builder grep covers sprintf-with-`\n`; contains no cal content.

39. `src/helpers/sensors/EnvironmentSensorManager.cpp:903,905,911,913` — fn `EnvironmentSensorManager::loop()` (def :889)
    `MESH_DEBUG_PRINTLN("lat %f lon %f", node_lat, node_lon);`
    The only `%f` sites in src/ (GPS debug logging). Recorded for the format-verb grep; no calibration content.

40. `src/helpers/esp32/TBeamBoard.cpp:115-117` — fn `TBeamBoard::printPMU()` (def :106)
    `// learn the battery curve and will automatically calibrate the battery percentage`
    Comment documenting automatic PMU battery calibration; no command emission.

41. `src/helpers/sensors/EnvironmentSensorManager.cpp:24` — file scope
    `#include "config/generic_33v_3s_28d/bsec_iaq.txt" // 3.3v, LP, 28 day background calibration window`
    Generated BSEC calibration-window config include; no command emission.

42. `src/helpers/sensors/EnvironmentSensorManager.cpp:234` — comment (`// hardware channel; MLX90614 and RAK12035+calibration`); no emission.

43. Interference-threshold parameter sources feeding #9 (example overrides of `getInterferenceThreshold()`):
    - `examples/companion_radio/MyMesh.cpp:261` — fn `MyMesh::getInterferenceThreshold() const`
    - `examples/simple_repeater/MyMesh.h:150-151` — fn `MyMesh::getInterferenceThreshold() const`
    - `examples/simple_room_server/MyMesh.h:144-145` — fn `MyMesh::getInterferenceThreshold() const`
    - `examples/simple_sensor/SensorMesh.cpp:323-324` — fn `SensorMesh::getInterferenceThreshold() const`

44. Vendored/excluded hits recorded for completeness (no emission sites):
    - `lib/nrf52/include/ble.h:125,294-310,328` and `lib/nrf52/s140_nrf52_7.3.0_API/include/ble.h:126,288-312` + `nrf_sdm.h:241-262` — Nordic SoftDevice RC-oscillator calibration API structs (`ble_common_opt_extended_rc_cal_t`, `rc_ctiv`, `rc_temp_ctiv`). Third-party vendor API surface, not the application's emission path.
    - `docs/cli_commands.md` — command index enumerated; calibration-adjacent commands only (`adc.multiplier` :375, `agc.reset.interval` :567, `int.thresh` :555, `radio.rxgain` :252). No `cal`.

## Grep log (exact commands and results)

All greps were run from the repo root `/home/c03rad0r/repos/meshcore-fork-fix`.
`git grep <pattern> HEAD` pins hits to commit `931ec31` — this is deliberate: the
shared working tree had 90 files deleted from disk by a sibling session, so
filesystem rg would produce false negatives (see Caveats).

Literal tokens:
- `git grep -n 'cal ' HEAD` — many raw hits, ALL false positives from English prose ("local advert", "physical", "Electrical", "Critical", "Typical values", "cycles") in README/docs/analysis and lib/nrf52 comments. 0 calibration-command hits.
- `git grep -n 'cal %' HEAD` — rc=1, 0 hits.
- `git grep -n '"cal"' HEAD` — rc=1, 0 hits.
- `git grep -nF "'cal'" HEAD` — rc=1, 0 hits.
- `git grep -nE '\bcal\b' HEAD` — rc=1, 0 hits.
- `git grep -niE '\bcal\b' HEAD` (case-insensitive, full tree) — rc=1, 0 hits.
- `git grep -nE '\bcal\b' 07a3ca9` (linked branch) — rc=1, 0 hits.
- `git grep -n 'cal %' 07a3ca9` — rc=1, 0 hits.

Format verbs:
- `git grep -nF '%g' HEAD -- src examples test` — rc=1, 0 hits. Full tree: rc=1, 0.
- `git grep -nF '%e' HEAD -- src examples test` — rc=1, 0 hits. Full tree: rc=1, 0.
- `git grep -nF '%f' HEAD -- src examples test` — 4 hits (EnvironmentSensorManager.cpp:903,905,911,913 — GPS debug).
- `git grep -nF '%d' HEAD -- src examples test` — 189 hits (generic integer formatting; none cal).
- `git grep -nF '%v' HEAD -- src examples test` — rc=1, 0 hits. Full tree: rc=1, 0.
- `git grep -nF '%s' HEAD -- src examples test` — 156 hits (generic string formatting; none cal).

Identifiers / field names:
- `git grep -n 'gain' HEAD -- src lib examples arch` — `rx_boosted_gain` sites (companion_radio MyMesh.cpp:884-886,966; simple_repeater MyMesh.cpp:915-917,965; NodePrefs.h:31; CommonCLI radio.rxgain) + "again" false positives in lib/nrf52 doc comments.
- `git grep -nw 'k' HEAD -- src` — 11 hits, loop indices only (Mesh.cpp:156-163,325-326; OLEDDisplay.cpp:1125,1141,1145).
- `git grep -nw 'K' HEAD -- src examples` — rc=1, 0 hits.
- `git grep -n 'temp_offset' HEAD` — rc=1, 0 hits.
- `git grep -n 'temperatureOffset' HEAD` — rc=1, 0 hits.
- `git grep -nw 'T0' HEAD -- src lib examples arch` — 0 code hits.
- `git grep -nw 't0' HEAD -- src lib examples arch` — only `lib/ed25519/fe.c` field-element temporaries (365-447, 882-934); no cal relevance.
- `git grep -n 'offset' HEAD -- src examples` — packet/path offsets (Mesh.cpp:54-58; simple_repeater MyMesh.cpp:288-289), display defines (ST7789Display.cpp:6,10), RTC digital-offset comment (RTC_RX8130CE.cpp:21-23); no cal-command builders.
- `git grep -niE 'calibration' HEAD` — 56 hits: lib/nrf52 SoftDevice headers (see #44), radio ResetAGC comments (SX126xReset.h:6-7,21; LR11x0Reset.h:6-7,14-15), RAK12035 code+comments, EnvironmentSensorManager (24,234,453-454,464), analysis/ physics docs.
- `git grep -niE 'calibrat' HEAD -- src examples` — 40 hits, every one classified above.
- `git grep -nE '\bCAL[A-Z_]|_CAL\b' HEAD -- src examples` — RAK12035 opcodes + call sites (#5-8, #22).
- `git grep -niE 'calib' HEAD -- variants platformio.ini` — rc=1, 0 hits (no build-flag enables in any variant).
- Untracked-file check (on disk): `grep -nE '\bcal\b|"cal"|\x27cal\x27|cal %' analysis/failure-modes/ice_bridge_s11_calc.py` — 0 hits; `grep -cE 'calibrat'` → 0. (Only untracked source file in the repo.)
- Linked-worktree untracked reports: `grep -rniE '\bcal\b|calibrat' /home/c03rad0r/worktrees/dut-rf-port-evidence/reports/` — 1 hit, the English word "calibrated" in FIELD-DATA.md:49; no code.

String builders writing a command line with trailing newline:
- `git grep -nE '\b(sprintf|snprintf|printf|vsnprintf)\s*\(' HEAD -- src examples test` — census of all formatting sites (CommonCLI replies, companion_radio Serial.printf, UITask display strings, DataStore path building). None build a cal command.
- `git grep -nE '(sprintf|snprintf)\([^)]*\\n' HEAD -- src examples test` — exactly 2 hits: CommonCLI.cpp:338 and :342 (see #38).
- `git grep -nE '\+\s*"\\n"' HEAD -- src examples test` — rc=1, 0 hits.
- `git grep -nE '"\\n"\s*\+' HEAD -- src examples test` — rc=1, 0 hits.
- `git grep -nE 'printf\([^)]*\\n"' HEAD -- src examples` — 42 hits, Serial debug prints; none cal.
- `git grep -nE 'StringBuilder|fmt\.Sprintf|System\.out' HEAD` — rc=1, 0 hits (no Go/Java in tree).

History / reachability:
- `git log --oneline 07a3ca9 -G'calibrat' -- src` — 8 commits: f86e6c0 (BSEC window), c7be216 (sensor init fix), 27f7326 (RAK12035 addition #2223), 9bae9d0 (LR11x0 comment fix), 85f764a (Calibrate configured frequency for AGC reset), f54948e (LR11x10 AGC reset), b2032e1 (dry), a2dc2eb (when doing AGC reset, call Calibrate(0x7F)).
- `git log --all --oneline -G'\bcal\b' -- src examples` — FAILED: "error: Could not read ecd30f4d364d190beac467224063d56ed681c5f2 / fatal: cannot simplify commit d9ff3a4…" — the local object store has holes. The reachable-from-linked pickaxe above succeeded and covers all commits reachable from the linked branch.
- `git merge-base --is-ancestor 07a3ca9 931ec31` → 0 (linked is ancestor of main).
- `git diff --stat 07a3ca9 931ec31 -- src lib examples test arch` → empty.
- `git merge-base --is-ancestor 91f3fa0 07a3ca9` → 0; `git merge-base --is-ancestor 8fc2da5 07a3ca9` → 0.
- `git ls-remote origin` → main@07a3ca9 (= linked branch tip); local main is 3 analysis-doc commits ahead.

## Caveats

1. Shared-tree state: the working tree has 90 unstaged deletions (boards/, docs/, 11 src files, etc.) from a sibling session — disk ≠ HEAD. All greps were pinned to the commit trees (`git grep … HEAD` / `… 07a3ca9`) so every recorded `path:line` is reproducible against the SHA. I did not restore, stage, or commit any of those deletions.
2. Missing git objects: object store has holes (e.g. ecd30f4 unreadable). `git log --all -G` pickaxes fail; the reachable-from-linked range pickaxe succeeded. `git fetch origin dev …` also fails on the same missing objects, so remote tips dev @ 5f3b7f2, feature/nicerf-lr2021-variant @ 1ed56aa, fix/2739-review-fixes @ 05ad173, gh-pages @ efb883d could NOT be inspected locally — a follow-up enumeration should repair the object store (full refetch/re-clone) and re-grep those four tips before declaring them cal-free. Note these are NOT reachable from the linked branch (they are ahead of / parallel to it), so they are outside the task's "branches reachable from it" scope, but are disclosed for completeness.
3. `git grep` pinned to the commit was used instead of on-disk rg for reason (1); this means untracked files were checked separately (done: the one untracked source file and the linked worktree's reports — both clean).

## Conclusion

- **Text `cal` command emitter: none found.** Explicit statement backed by the zero-hit greps above and by exhaustive enumeration of every CLI dispatch table (CommonCLI handleCommand/handleSetCmd/handleGetCmd, example handlers, docs index).
- **Calibration command emitters that DO exist: 17 direct sites** (SPI Calibrate frames for SX126x/LR11x0, RAK12035 I2C calibration read/write commands, periodic noise-floor + AGC calibration triggers), **14 builder sites** (payload construction, opcodes, cadence constants, virtual emission interfaces, build-flag plumbing), **13 format-helper / CLI-adjacent sites** (`adc.multiplier`, `agc.reset.interval`, `int.thresh`, `radio.rxgain` — the natural hooks a future `cal` command would build on), enumerated above with byte-exact snippets.
- Enumeration-only finding worth flagging to the maintainer (not fixed here): the `ENABLE_RAK12025_CALIBRATION` / `ENABLE_RAK12035_CALIBRATION` macro-name mismatch (#23) means the RAK12035 calibration emission path is dead code in the default build.