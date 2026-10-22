// SelfCal.h - pure host-compilable open-loop thermal frequency compensation.
// No Arduino dependencies.
//
// MODEL / SIGN CONVENTION
//   Crystal drift away from the turnover temperature (AT-cut, parabolic):
//     drift_ppm(T) = -k*(T-T0)^2      (k = 0.03..0.04 ppm/C^2, taken as a
//                                      MAGNITUDE here; the crystal is SLOW on
//                                      both sides of T0)
//   A slow crystal makes the synthesised LO land LOW, so a receiver programmed
//   to f0 actually centres its passband at f0*(1+drift). To put the passband
//   back on an on-frequency (warm, at-turnover) transmitter the RX must be
//   programmed HIGH by |drift|:
//     applied_offset_ppm(T) = +k*(T-T0)^2 = -drift_ppm(T)
//   i.e. the applied offset is the NEGATION of the drift. Applying the drift
//   itself (the pre-2026-09-11 sign) doubles the error instead of cancelling
//   it: at -40 C with k=0.04,T0=25 it applies -169 ppm where +169 is required,
//   leaving the passband 338 ppm off instead of on-frequency.
//   Direction cross-check in the tree: RadioLibWrapper::setCenterFreqOffset()
//   feeds applyCenterFreqOffset(), which does
//     ((CustomLR2021*)_radio)->setFrequency(_base_freq_mhz + hz/1e6f)
//   so a POSITIVE offset programs the RX center HIGH. A negative applied offset
//   is never correct in any configuration (both sides of the turnover are slow).
//   Applied with 1 Hz-granularity free retune at the radio layer.
//
// PRIMARY  : open-loop temp model driven by getTemperature() die temp, with a
//            thermal-lag EMA (~10s tc) and output slew/deadband/max clamps.
// SECONDARY: closed-loop residual estimate fed by a frequency-error source
//            (FEI measurement). INERT on LR2021/LR11x0 (no FEI field) - the
//            wrapper simply never calls feedMeasured() there. On FEI-capable
//            chips the residual is median-filtered, SNR-gated (>-10dB) and
//            EMA-smoothed, then added to the open-loop offset.
#pragma once

#include <stdint.h>
#include <string.h>
#include <math.h>

class SelfCal {
public:
  // Serialized cal blob: 2 floats (k, T0) + u16 magic + u8 version.
  static const uint8_t BLOB_SIZE = 3 * 4 + 2 + 1; // 15 bytes
  static const uint16_t CAL_MAGIC = 0x5343;       // 'SC'

  // In-class constexpr values (C++11-safe: used as prvalues only, so no
  // out-of-line definition is needed and no ODR multiple-definition occurs
  // when the header is included by several translation units).
  static constexpr float TEMP_TC_SECS = 10.0f;     // thermal-lag time constant
  static constexpr float SLEW_PPM     = 25.0f;     // max |delta| per update
  static constexpr float DEADBAND_PPM = 1.0f;      // ignore sub-deadband changes
  static constexpr float MAX_PPM      = 300.0f;    // absolute output clamp
                                                   // must cover the profile floor:
                                                   // 0.04*(25-(-56.5))^2 = 266 ppm
  static constexpr float SNR_GATE_DB  = -10.0f;    // FEI residual acceptance gate
  // Validity band of the open-loop model around the calibration point T0. Outside
  // |T - T0| <= CAL_RANGE_C the parabola is extrapolated and the residual error
  // can exceed the SF8/BW62.5 capture window, so callers should fall back to the
  // wide-bandwidth profile instead of trusting the model.
  //
  // Sized to the mission profile, not to a round number. ISA/standard-atmosphere
  // profile: the temperature floor is -56.5 C, held from 11 km to 20 km, rising
  // to about -46 C at 30 km. A module whose turnover T0 lands anywhere in a
  // realistic +25..+33 C therefore needs 82..90 C of modelled range to stay in
  // band for the whole profile; a 60 C band (the earlier value) disqualified the
  // calibration exactly where it is needed and silently degraded the mapper to
  // the BW125 fallback (2x noise bandwidth) for the whole flight. The fit's own
  // residual is the real validity gate - this constant is only the outer sanity
  // bound, sized to trip on a bogus sensor reading rather than on the profile.
  // Bench calibration must sweep at least as deep as the expected flight minimum
  // (a kitchen freezer only reaches ~-18 C; dry ice/IPA (-78 C) or a chamber is
  // required) and a fit extrapolated beyond the swept span is not flight-valid -
  // see bench/README.md.
  static constexpr float CAL_RANGE_C  = 90.0f;

  SelfCal()
    : _k(0.0f), _T0(0.0f), _ver(0), _cal_valid(false),
      _temp_ema(0.0f), _temp_init(false), _offset_ppm(0.0f), _muted(false),
      _residual_ema(0.0f), _median_n(0), _last_snr(-100.0f) { }

  // --- calibration ----------------------------------------------------------
  // k is the MAGNITUDE of the AT-cut quadratic coefficient (ppm/C^2, > 0);
  // T0 is the turnover temperature (C). The blob stores k with this sign, so
  // the serial CLI keeps rejecting negative k (a negative k would flip the
  // compensation direction again).
  void setCalibration(float k, float T0) {
    _k = k; _T0 = T0; _cal_valid = true;
  }

  bool loadCalibration(const uint8_t* blob, uint8_t len) {
    if (len != BLOB_SIZE) return false;
    float k, T0, spare; uint16_t magic; uint8_t ver;
    memcpy(&k, blob, 4);
    memcpy(&T0, blob + 4, 4);
    memcpy(&spare, blob + 8, 4);
    memcpy(&magic, blob + 12, 2);
    ver = blob[14];
    (void)spare;
    if (magic != CAL_MAGIC) return false;
    _k = k; _T0 = T0; _ver = ver; _cal_valid = true;
    // cold-start offset from the model (never blind-zero)
    _temp_ema = T0;   // assume ambient ~ T0 until first real reading
    _temp_init = true;
    return true;
  }

  void storeCalibration(uint8_t* blob) const {
    memcpy(blob, &_k, 4);
    memcpy(blob + 4, &_T0, 4);
    float spare = 0.0f;
    memcpy(blob + 8, &spare, 4);
    uint16_t magic = CAL_MAGIC;
    memcpy(blob + 12, &magic, 2);
    blob[14] = _ver;
  }

  // --- temperature input (with dt in seconds for EMA) ------------------------
  void setTemperatureC(float t, float dt) {
    if (!_temp_init) { _temp_ema = t; _temp_init = true; return; }
    float alpha = 1.0f - expf(-dt / TEMP_TC_SECS);
    if (alpha > 1.0f) alpha = 1.0f;
    if (alpha < 0.0f) alpha = 0.0f;
    _temp_ema += (t - _temp_ema) * alpha;
  }

  // --- core update: returns applied offset in ppm ----------------------------
  float update() {
    if (_muted) return _offset_ppm;
    if (!_cal_valid) { _offset_ppm = 0.0f; return _offset_ppm; }

    // Compensation, not drift: the crystal is slow away from T0, so the LO is
    // low and the RX must be programmed HIGH by |drift| = k*(T-T0)^2 (k>0).
    // Signing this -k*(T-T0)^2 (as it was) inverts the correction and doubles
    // the error - see the header note.
    float raw = _k * (_temp_ema - _T0) * (_temp_ema - _T0);
    // max clamp
    if (raw > MAX_PPM) raw = MAX_PPM;
    if (raw < -MAX_PPM) raw = -MAX_PPM;
    // slew clamp: limit movement vs previous output
    float target = raw;
    float delta = target - _offset_ppm;
    if (delta > SLEW_PPM) delta = SLEW_PPM;
    if (delta < -SLEW_PPM) delta = -SLEW_PPM;
    target = _offset_ppm + delta;
    // deadband: suppress output movement below threshold
    target += _residual_ema;   // add closed-loop residual (0 when inert)
    if (fabsf(target - _offset_ppm) < DEADBAND_PPM) {
      // leave _offset_ppm unchanged (deadband hold)
    } else {
      _offset_ppm = target;
    }
    // clamp again after residual/deadband joining
    if (_offset_ppm > MAX_PPM) _offset_ppm = MAX_PPM;
    if (_offset_ppm < -MAX_PPM) _offset_ppm = -MAX_PPM;
    return _offset_ppm;
  }

  // --- FEI secondary (inert on LR2021; never called there) -------------------
  // fed frequency-error residual (ppm) gated by SNR (dB).
  void feedMeasured(float freq_error_ppm, float snr) {
    _last_snr = snr;
    if (snr <= SNR_GATE_DB) return;              // SNR gate reject
    // median-of-5 filter
    _median_buf[_median_n] = freq_error_ppm;
    _median_n = (_median_n < 5) ? _median_n + 1 : 5;
    float sorted[5];
    memcpy(sorted, _median_buf, _median_n * sizeof(float));
    // insertion sort
    for (int i = 1; i < (int)_median_n; i++) {
      float v = sorted[i]; int j = i - 1;
      while (j >= 0 && sorted[j] > v) { sorted[j + 1] = sorted[j]; j--; }
      sorted[j + 1] = v;
    }
    float median = sorted[_median_n / 2];
    // scalar EMA on the temp-model residual
    _residual_ema += (median - _residual_ema) * 0.2f;  // ~5-sample smoothing
  }

  // --- calibration range -----------------------------------------------------
  // Is 't' inside the band where the calibrated parabola is trustworthy?
  // Requires a valid blob AND |t - T0| <= CAL_RANGE_C.
  bool inCalRange(float t) const {
    if (!_cal_valid) return false;
    float d = t - _T0;
    if (d < 0.0f) d = -d;
    return d <= CAL_RANGE_C;
  }

  // Can we produce a trustworthy offset for this die temperature? Callers use
  // this (together with a "no reading" sentinel check) to decide whether to
  // engage the degraded wide-bandwidth RX profile.
  bool canCompensate(float t) const { return inCalRange(t); }

  // --- accessors -------------------------------------------------------------
  float getOffsetPpm() const { return _offset_ppm; }
  float getTempC() const { return _temp_ema; }
  float getK() const { return _k; }
  float getT0() const { return _T0; }
  bool isCalValid() const { return _cal_valid; }
  uint8_t getVersion() const { return _ver; }
  bool isMuted() const { return _muted; }
  void setMuted(bool m) { _muted = m; }
  void setVersion(uint8_t v) { _ver = v; }

private:
  float _k, _T0;
  uint8_t _ver;
  bool _cal_valid;

  float _temp_ema;
  bool _temp_init;
  float _offset_ppm;
  bool _muted;

  // secondary (FEI) residual path
  float _residual_ema;
  float _median_buf[5];
  uint8_t _median_n;
  float _last_snr;
};
