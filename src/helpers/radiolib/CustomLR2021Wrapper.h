#pragma once

#include "CustomLR2021.h"
#include "RadioLibWrappers.h"

#ifndef USE_LR2021
#define USE_LR2021
#endif

#ifndef LR2021_RX_BOOST_LEVEL
#define LR2021_RX_BOOST_LEVEL 7
#endif

class CustomLR2021Wrapper : public RadioLibWrapper {
public:
  CustomLR2021Wrapper(CustomLR2021& radio, mesh::MainBoard& board) : RadioLibWrapper(radio, board) { }

  void setParams(float freq, float bw, uint8_t sf, uint8_t cr) override {
    _base_freq_mhz = freq;                       // nominal center before any offset
    _params_bw_khz = bw;                         // remembered for runtime BW switches
    _params_sf = sf;
    _params_cr = cr;
    if (_center_offset_hz != 0.0f) freq += _center_offset_hz / 1e6f;
    ((CustomLR2021 *)_radio)->setFrequency(freq);
    ((CustomLR2021 *)_radio)->setSpreadingFactor(sf);
    ((CustomLR2021 *)_radio)->setBandwidth(bw);
    ((CustomLR2021 *)_radio)->setCodingRate(cr);
    updatePreamble(sf);
    applySideDetectorConfig();
    PacketMillis pm = calcMaxPacketMillis(sf, bw, cr, preambleLengthForSF(sf));
    ((CustomLR2021 *)_radio)->setPreambleMillis(pm.preambleMillis);
    ((CustomLR2021 *)_radio)->setMaxPayloadMillis(pm.payloadMillis);

  }

  float getRadioTemperatureC() override {
    // XOSC (crystal) sensor is the relevant one for crystal-frequency drift.
    // 13-bit resolution degrees Celsius. 0.0 if the read fails.
    return ((CustomLR2021 *)_radio)->getTemperature(RADIOLIB_LR2021_TEMP_SOURCE_XOSC);
  }

  // Runtime LoRa-bandwidth switch. Used by passive_mapper to fall back to a wide
  // (+/-72 ppm) capture window when no trustworthy thermal offset is available.
  // The LR2021 accepts the bandwidth write in standby with no image calibration
  // re-run (same free-retune class as setFrequency).
  bool setRxBandwidthKhz(float bw_khz) override {
    if (bw_khz <= 0.0f) return false;
    if (_params_bw_khz > 0.0f && bw_khz == _params_bw_khz) return true;   // already there

    CustomLR2021* r = (CustomLR2021 *)_radio;
    r->standby();
    int16_t status = r->setBandwidth(bw_khz);
    if (status != RADIOLIB_ERR_NONE) {
      MESH_DEBUG_PRINTLN("CustomLR2021Wrapper: setBandwidth(%.1f) returned %d", bw_khz, status);
      RadioLibWrapper::idle();     // leave the radio usable in its previous profile
      return false;
    }
    _params_bw_khz = bw_khz;
    // Preamble/payload airtime budgets are bandwidth-dependent.
    uint8_t sf = (_params_sf > 0) ? _params_sf : getSpreadingFactor();
    uint8_t cr = (_params_cr > 0) ? _params_cr : 5;
    PacketMillis pm = calcMaxPacketMillis(sf, bw_khz, cr, preambleLengthForSF(sf));
    r->setPreambleMillis(pm.preambleMillis);
    r->setMaxPayloadMillis(pm.payloadMillis);
    RadioLibWrapper::idle();       // re-arm RX with the new bandwidth
    MESH_DEBUG_PRINTLN("CustomLR2021Wrapper: RX bandwidth -> %.1f kHz", bw_khz);
    return true;
  }

  float getRxBandwidthKhz() const override { return _params_bw_khz; }

  void applyCenterFreqOffset() override {
    if (_base_freq_mhz > 0.0f && _center_offset_hz != 0.0f) {
      // offset is small (< ~300 ppm << 20 MHz image-cal trigger) so this is a
      // FREE retune - no front-end image calibration is re-run.
      ((CustomLR2021 *)_radio)->setFrequency(_base_freq_mhz + _center_offset_hz / 1e6f);
    }
  }

  bool configSideDetectors(const uint8_t* sideDetSFs, uint8_t num, float bw) override {
    LR2021LoRaSideDetector_t tmp[3];
    uint8_t sf = getSpreadingFactor();

    if (sf >= 10 && num > 1) { return false; }  // only 1 side detector allowed when primary SF >= 10
    for (int i = 0; i < num; i++) {
      if (sideDetSFs[i] > 12 || sideDetSFs[i] < 5) { return false; }  // must be valid SF
      if (sideDetSFs[i] <= sf) { return false; }  // must be < primary SF
      if (sideDetSFs[i] > sf + 4) { return false; }  // span must not be > 4

      tmp[i].sf = sideDetSFs[i];
      float tSym = calcTsym(tmp[i].sf, bw);
      if (tSym >= 16.0f) {
        tmp[i].ldro = true;
      } else {
        tmp[i].ldro = false; 
      }
      tmp[i].invertIQ = false;
      tmp[i].syncWord = 0x12;
    }
    int16_t status = ((CustomLR2021 *)_radio)->setSideDetector(tmp, num);
    RadioLibWrapper::idle(); // trigger startReceive()
    MESH_DEBUG_PRINTLN("setSideDetector() returned %d", status);

    if (status == RADIOLIB_ERR_NONE) {
      for (int i = 0; i < num; i++) { _sideDet[i] = tmp[i]; }
      _numSideDet = num;
    } else {
      return false;
    }
    
    return true;
  }

  int16_t applySideDetectorConfig() {
    int16_t status = ((CustomLR2021 *)_radio)->setSideDetector(_sideDet, _numSideDet);
    RadioLibWrapper::idle(); // trigger startReceive()
    return status;
  }

  float calcTsym(uint8_t sf, float bw) {
    float tSym = (float)(uint32_t(1) << sf) / (float)bw;
    return tSym;
  }

  bool isReceivingPacket() override {
    return ((CustomLR2021 *)_radio)->isReceiving();
  }

  float getCurrentRSSI() override {
    float rssi = -110;
    ((CustomLR2021 *)_radio)->getRssiInst(&rssi);
    return rssi;
  }

  void onSendFinished() override {
    RadioLibWrapper::onSendFinished();
    _radio->setPreambleLength(preambleLengthForSF(getSpreadingFactor())); // overcomes weird issues with small and big pkts
  }

  float getLastRSSI() const override { return ((CustomLR2021 *)_radio)->getRSSI(); }
  float getLastSNR() const override { return ((CustomLR2021 *)_radio)->getSNR(); }

  uint8_t getSpreadingFactor() const override { return ((CustomLR2021 *)_radio)->getSpreadingFactor(); }
  
  bool setRxBoostedGainMode(bool en) override {
    ((CustomLR2021 *)_radio)->standby(); // LR2021 must be in standby to accept setRxBoostedGainMode
    int16_t status = ((CustomLR2021 *)_radio)->setRxBoostedGainMode(en ? LR2021_RX_BOOST_LEVEL: 0);
    RadioLibWrapper::idle(); // trigger startReceive()
    return status == RADIOLIB_ERR_NONE;
  }

  bool getRxBoostedGainMode() const override {
    return ((CustomLR2021 *)_radio)->getRxBoostedGainMode();
  }

  protected:
    LR2021LoRaSideDetector_t _sideDet[3];
    size_t _numSideDet = 0;
    float _base_freq_mhz = 0.0f;
    // Current LoRa bandwidth (kHz). Seeded from the build profile because the
    // NiceRF/accompanying variants bring the radio up through
    // CustomLR2021::std_init() -> LR2021::begin(LORA_BW, ...) and never call
    // setParams(), so the wrapper would otherwise not know its own nominal BW
    // (status would report 0 and the "already there" fast path below would never
    // match). setParams() overrides this for the prefs-driven examples.
#if defined(LORA_BW)
    float _params_bw_khz = (float)LORA_BW;
#else
    float _params_bw_khz = 0.0f;
#endif
    uint8_t _params_sf = 0;        // params remembered for runtime BW switches
    uint8_t _params_cr = 0;
};
