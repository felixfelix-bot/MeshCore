#pragma once

#include <Arduino.h>
#include <Mesh.h>
#include <target.h>
#include <helpers/StaticPoolPacketManager.h>
#include <helpers/SimpleMeshTables.h>
#include <helpers/ArduinoHelpers.h>
#include <helpers/IdentityStore.h>

#if defined(NRF52_PLATFORM) || defined(STM32_PLATFORM)
  #include <InternalFileSystem.h>
#elif defined(RP2040_PLATFORM)
  #include <LittleFS.h>
#elif defined(ESP32)
  #include <SPIFFS.h>
  using File = fs::File;
#endif

#include "host/DensityWindow.h"
#include "host/SelfCal.h"
#include "RateLimiter.h"

// passive_mapper: a passive RX mapper + density-adaptive node (SkyMapper Board A).
//
//  - Logs a fixed 16-byte binary record per received packet to a RAM ring that
//    is block-appended to LittleFS every 4 KB or 10 s (never per-packet I/O).
//  - Counts DISTINCT sender pubkeys in a sliding 10-min window and switches
//    between MAP mode (>=5 nodes: silent, repeat off, advert off) and NODE mode
//    (<=2 nodes: behaves like a normal relay node) with asymmetric hysteresis
//    and a 5-min dwell.
//  - Applies open-loop thermal frequency compensation (SelfCal) to keep the
//    LX2021 crystal on-frequency at altitude.

#define MAP_DEFAULT_FREQ   869.618f   // MHz nominal (LR2021 868-band)

// LittleFS log of the fixed 16-byte mapper records.
#define MAP_LOG_FILE        "/map.dat"

// 4 KB RAM ring -> block-append flush thresholds
#define MAP_RING_CAPACITY   4096
#define MAP_FLUSH_SECS      10

#ifndef MAP_ADVERT_SECS
  #define MAP_ADVERT_SECS   30          // self-advert period in NODE mode (0 = off)
#endif

#ifndef MAP_ADVERT_PAYLOAD
  #define MAP_ADVERT_PAYLOAD "SkyMapper-A"   // app_data in self advert (optional)
#endif

class MyMesh : public mesh::Mesh {
public:
  MyMesh(mesh::MainBoard& board, mesh::Radio& radio, mesh::MillisecondClock& ms,
         mesh::RNG& rng, mesh::RTCClock& rtc, mesh::MeshTables& tables);

  void begin(FILESYSTEM* fs);
  void loop();

  // minimal CLI: "status", "mode", "flush", "reset", "erase".
  void handleCommand(char* cmd, char* reply);

  mesh::DispatcherAction onRecvPacket(mesh::Packet* pkt) override;

  mesh::LocalIdentity& getSelfId() { return self_id; }
  void saveIdentity(const mesh::LocalIdentity&) { /* identity persisted in main */ }

  // stats accessors for the CLI / status line
  uint32_t getPacketsLogged() const { return _records_logged; }
  uint32_t getDistinctNodes() { return _density.distinctCount(_last_now); }
  const char* getModeName() const { return _density.getMode() == DensityWindow::MODE_MAP ? "MAP" : "NODE"; }

protected:
  void logRxRaw(float snr, float rssi, const uint8_t raw[], int len) override;
  void logRx(mesh::Packet* pkt, int len, float score) override;
  void logTx(mesh::Packet* pkt, int len) override { (void)pkt; (void)len; }
  void logTxFail(mesh::Packet* pkt, int len) override { (void)pkt; (void)len; }

  bool allowPacketForward(const mesh::Packet* packet) override;
  uint32_t getRetransmitDelay(const mesh::Packet* packet) override;
  float getAirtimeBudgetFactor() const override;
  uint8_t getExtraAckTransmitCount() const override { return 0; }

private:
  // ---- mapper record (fixed 16 bytes) --------------------------------------
  struct MapRecord {
    uint32_t epoch;      // 4  : UNIX epoch (rtc_clock, GPS-disciplined)
    uint8_t  pub_prefix[6]; // 6 : sender pubkey prefix (0 for non-ADVERT)
    int8_t   rssi;       // 1  : dBm
    int8_t   snr_x4;     // 1  : snr*4
    uint8_t  flags;      // 1  : (payload_type<<4)|route
    uint8_t  payload_len;// 1
    uint8_t  path_hash[2]; // 2 : last-two path hashes (topology)
    // total = 16 bytes
  };
  static_assert(sizeof(MapRecord) == 16, "MapRecord must be exactly 16 bytes");

  // ---- LittleFS ring
  FILESYSTEM* _fs;
  uint8_t  _ring[MAP_RING_CAPACITY];   // RAM ring buffer
  uint16_t _ring_len;                  // bytes currently buffered
  uint32_t _last_flush_ms;             // millis() of last flush
  uint32_t _records_logged;            // lifetime records written (incl. mode events)

  // ---- density-adaptive node
  DensityWindow _density;
  uint32_t _last_now;                  // last rtc epoch sampled
  DensityWindow::Mode _last_mode;
  uint32_t _mode_entered_epoch;        // epoch of last mode transition
  RateLimiter _fwd_limiter;            // NODE-mode forward guard (2 / 60s)
  uint32_t _next_advert_epoch;         // when to next self-advert (NODE mode)

  // ---- thermal self-calbration
  SelfCal _selfcal;
  float   _nominal_freq_mhz;
  float   _applied_offset_hz;
  float   _applied_die_temp_c;
  uint32_t _last_selfcal_ms;
  bool    _bw_fallback;                // BW125 fallback (temp unavailable/out-of-range)

  // ---- rx capture state
  float _last_snr_raw;                 // set by logRxRaw
  float _last_rssi;                    // set by logRxRaw

  // helpers
  void feedMapRecord(const mesh::Packet* pkt);
  void queueModeTransitionRecord(DensityWindow::Mode new_mode, uint8_t count);
  void flushRing();
  void updateSelfCal();
  void applyMode();
  void sendSelfAdvert();
};

inline
mesh::DispatcherAction MyMesh::onRecvPacket(mesh::Packet* pkt) {
  return mesh::Mesh::onRecvPacket(pkt);   // default route/advert handling
}

inline
float MyMesh::getAirtimeBudgetFactor() const {
  // EU 10% duty in NODE mode: airtime_factor >= 9 (default token bucket of 50%
  // would be illegal). MAP mode does not transmit so the factor is irrelevant.
  return _density.getMode() == DensityWindow::MODE_MAP ? 1.0f : 9.0f;
}
