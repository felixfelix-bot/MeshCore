// MyMesh.cpp - passive_mapper implementation (SkyMapper Board A).
//
// 16-byte fixed binary record per RX packet buffered in a 4 KB RAM ring and
// block-appended to the on-device filesystem every 4 KB or 10 s (never per-packet
// open/close — the flash-wear trap in simple_repeater's logRx).
//
// Density-adaptive: counts DISTINCT sender pubkeys in a sliding 10-min window
// (DensityWindow, pure host class) and switches between:
//   MAP  mode (>=5 nodes): repeat OFF, advert OFF (advert_interval=0), pure RX.
//   NODE mode (<=2 nodes): normal relay — advert on, forwarding allowed but
//         rate-limited to (2 / 60 s) and EU 10% duty (airtime factor >= 9).
// Asymmetric hysteresis 5-up / 2-down + 5-min dwell (in DensityWindow).
//
// Thermal self-calibration (SelfCal, pure host class): open-loop AT-cut drift
// model offset_ppm = -k*(T-T0)^2 from the LR2021 die temperature, applied as
// setCenterFreqOffset() (free retune, <20 MHz trigger), re-applied before every
// RX re-arm by RadioLibWrapper::startRecv(). When the die temperature is
// unavailable (radio returns the 0.0f sentinel) or outside the calibrated band
// (SelfCal::inCalRange), the mapper switches the radio to BW125 (a +/-72 ppm
// capture window) and keeps the last offset, instead of trusting a model that is
// extrapolating outside its calibration. The mode is restored on recovery.
//
// The calibration blob (/selfcal.dat) is loaded at boot; `cal <k> <T0>` on the
// serial CLI writes it from bench/freezer measurements so compensation is not
// inert in the field.

#include "MyMesh.h"

// ---- constructor -----------------------------------------------------------

MyMesh::MyMesh(mesh::MainBoard& board, mesh::Radio& radio, mesh::MillisecondClock& ms,
               mesh::RNG& rng, mesh::RTCClock& rtc, mesh::MeshTables& tables)
    : mesh::Mesh(radio, ms, rng, rtc, *new StaticPoolPacketManager(32), tables),
      _fs(nullptr),
      _ring_len(0), _last_flush_ms(0), _records_logged(0),
      _density(), _last_now(0), _last_mode(DensityWindow::MODE_NODE), _mode_entered_epoch(0),
      _fwd_limiter(2, 60),            // NODE-mode forward guard: max 2 forwards / 60 s
      _next_advert_epoch(0),
      _nominal_freq_mhz(MAP_DEFAULT_FREQ), _applied_offset_hz(0.0f), _applied_die_temp_c(0.0f),
      _raw_die_temp_c(0.0f),
      _last_selfcal_ms(0), _bw_fallback(false), _last_telem_epoch(0), _fw_records(0),
      _last_snr_raw(0.0f), _last_rssi(0.0f)
{
  (void)board;
  _last_now = rtc_clock.getCurrentTime();
  _mode_entered_epoch = _last_now;
}

// ---- begin -----------------------------------------------------------------

void MyMesh::begin(FILESYSTEM* fs) {
  mesh::Mesh::begin();
  _fs = fs;

  // Attempt to load persisted calibration blob (3 floats + u16 magic + u8 ver).
  // Mismatch/missing -> keep the in-RAM default (k=0 -> offset 0) until a
  // bench calibration fills it in. Cold-start via loadCalibration() never 0 if
  // a valid blob exists.
  if (_fs) {
    File f = _fs->open(MAP_CAL_FILE, "r");
    if (f) {
      uint8_t blob[SelfCal::BLOB_SIZE];
      int n = f.read(blob, SelfCal::BLOB_SIZE);
      f.close();
      if (n == SelfCal::BLOB_SIZE) {
        if (_selfcal.loadCalibration(blob, SelfCal::BLOB_SIZE)) {
          MESH_DEBUG_PRINTLN("selfcal: loaded cal blob (k=%d.%03d T0=%d.%02d)",
                             (int)_selfcal.getK(), (int)(_selfcal.getK()*1000)%1000,
                             (int)_selfcal.getT0(), (int)(_selfcal.getT0()*100)%100);
        }
      }
    }
  }

  _last_selfcal_ms = millis();
  applyMode();
}

// ---- loop ------------------------------------------------------------------

void MyMesh::loop() {
  mesh::Mesh::loop();

  uint32_t now = rtc_clock.getCurrentTime();          // epoch seconds (GPS-disciplined)
  _last_now = now;

  // Thermal self-cal: read die temp, run estimator, apply offset. Re-armed on
  // every startRecv() by the wrapper, so applying here is idempotent + cheap.
  updateSelfCal();

  // Periodic telemetry: die temperature + applied offset (the 16-byte RX record
  // has no room for them; see the synthetic-record note in MyMesh.h). Fires once
  // as soon as the RTC has a real epoch, then every MAP_TELEMETRY_SECS.
  if (now != 0 && (_last_telem_epoch == 0 ||
                   (int32_t)(now - _last_telem_epoch) >= (int32_t)MAP_TELEMETRY_SECS)) {
    queueTelemetryRecord();
  }

  // Flush the ring on size or age threshold.
  if (_ring_len >= MAP_RING_CAPACITY ||
      (_ring_len > 0 && (millis() - _last_flush_ms) >= MAP_FLUSH_SECS * 1000UL)) {
    flushRing();
  }

  // Density update + dwell/hysteresis transition handling.
  DensityWindow::Mode prev = _density.getMode();
  DensityWindow::Mode m = _density.update(now);
  if (m != prev) {
    applyMode();
    uint8_t cnt = _density.distinctCount(now);
    queueModeTransitionRecord(m, cnt);
    _mode_entered_epoch = now;
  }

  // NODE mode: periodic self-advert (off in MAP mode).
  if (_density.getMode() == DensityWindow::MODE_NODE && _next_advert_epoch &&
      (int32_t)(now - _next_advert_epoch) >= 0) {
    sendSelfAdvert();
    _next_advert_epoch = now + (MAP_ADVERT_SECS > 0 ? MAP_ADVERT_SECS : 0);
  }
}

// ---- handleCommand (minimal CLI) -------------------------------------------

// Minimal decimal float parser for the CLI. Deliberately avoids sscanf("%f")/
// strtof: the scanf float machinery costs ~16 KB of flash in this image, which
// is not worth it for two calibration numbers. Accepts [-+]?digits[.digits].
static bool parseFloat(const char* s, const char** endp, float* out) {
  while (*s == ' ' || *s == '\t') s++;
  bool neg = false;
  if (*s == '-') { neg = true; s++; } else if (*s == '+') { s++; }
  if (*s < '0' || *s > '9') return false;
  float v = 0.0f;
  while (*s >= '0' && *s <= '9') { v = v * 10.0f + (float)(*s - '0'); s++; }
  if (*s == '.') {
    s++;
    float scale = 0.1f;
    while (*s >= '0' && *s <= '9') { v += (float)(*s - '0') * scale; scale *= 0.1f; s++; }
  }
  *out = neg ? -v : v;
  if (endp) *endp = s;
  return true;
}

void MyMesh::handleCommand(char* cmd, char* reply) {
  reply[0] = 0;
  if (strcmp(cmd, "status") == 0) {
    snprintf(reply, 160, "mode=%s distinct=%u logged=%u dropped=%u buf=%u bw=%.1f%s die_temp=%.1f off_hz=%.0f cal=%s",
             _density.getMode() == DensityWindow::MODE_MAP ? "MAP" : "NODE",
             (unsigned)_density.distinctCount(_last_now),
             (unsigned)_records_logged, (unsigned)_fw_records, (unsigned)_ring_len,
             _radio->getRxBandwidthKhz(), _bw_fallback ? "(fallback)" : "",
             _raw_die_temp_c, _applied_offset_hz,
             _selfcal.isCalValid() ? "yes" : "no");
  } else if (strcmp(cmd, "mode") == 0) {
    snprintf(reply, 160, "%s", _density.getMode() == DensityWindow::MODE_MAP ? "MAP" : "NODE");
  } else if (strcmp(cmd, "flush") == 0) {
    flushRing();
    snprintf(reply, 160, "flushed %u records to %s", (unsigned)_records_logged, MAP_LOG_FILE);
  } else if (strcmp(cmd, "reset") == 0) {
    _records_logged = 0;
    snprintf(reply, 160, "record counter reset to 0");
  } else if (strcmp(cmd, "erase") == 0) {
    if (_fs) { _fs->remove(MAP_LOG_FILE); }
    snprintf(reply, 160, "erased %s", MAP_LOG_FILE);
  } else if (strncmp(cmd, "cal ", 4) == 0) {
    // Persist a bench-derived calibration: cal <k> <T0>   (k in ppm/C^2, T0 in C)
    float k = 0.0f, t0 = 0.0f;
    const char* p = cmd + 4;
    if (parseFloat(p, &p, &k) && parseFloat(p, nullptr, &t0) && k >= 0.0f) {
      bool ok = writeCalBlob(k, t0);
      snprintf(reply, 160, "cal k=%.6g T0=%.2fC -> %s (valid=%s)",
               k, t0, ok ? "persisted" : "RAM only, file write failed",
               _selfcal.isCalValid() ? "yes" : "no");
    } else {
      snprintf(reply, 160, "usage: cal <k_ppm_per_C2> <T0_C>");
    }
  } else if (strcmp(cmd, "calshow") == 0) {
    snprintf(reply, 160, "cal valid=%s k=%.6g T0=%.2fC range=+/-%.0fC die_temp=%.1f off_hz=%.0f",
             _selfcal.isCalValid() ? "yes" : "no", _selfcal.getK(), _selfcal.getT0(),
             SelfCal::CAL_RANGE_C, _raw_die_temp_c, _applied_offset_hz);
  } else {
    snprintf(reply, 160, "commands: status, mode, flush, reset, erase, cal <k> <T0>, calshow");
  }
}

// ---- RX logging hooks ------------------------------------------------------

void MyMesh::logRxRaw(float snr, float rssi, const uint8_t raw[], int len) {
  // snr/rssi captured before packet parse; used by logRx() for the record.
  _last_snr_raw = snr;
  _last_rssi = rssi;
  (void)raw; (void)len;
}

void MyMesh::logRx(mesh::Packet* pkt, int len, float score) {
  (void)len; (void)score;
  feedMapRecord(pkt);
}

// ---- forwarding / duty -----------------------------------------------------

bool MyMesh::allowPacketForward(const mesh::Packet* packet) {
  // MAP mode: never forward (silent). NODE mode: forward but rate-limited to
  // (2 / 60 s) and hard-capped at NODE-level duty.
  //
  // Forwarding scheme (design decision, spec asked for it explicitly): we use the
  // stock Mesh forward path, i.e. strict seen-hash once-only dedup + base
  // retransmit (which appends this node's hash to the path), and we did NOT
  // implement the "never-append-hash" variant. Rationale: forwarding only ever
  // happens in NODE mode, which by definition means <=2 distinct senders in a
  // 10-minute window - a sparse mesh where path pollution from one extra hop is
  // negligible, while skipping the hash append would break the loop
  // suppression that the seen-hash table alone cannot guarantee across
  // multi-hop floods. Cost/benefit does not favour the exotic path here.
  if (_density.getMode() != DensityWindow::MODE_NODE) return false;
  return _fwd_limiter.allow(_last_now);
}

uint32_t MyMesh::getRetransmitDelay(const mesh::Packet* packet) {
  // Keep retransmits sparse to respect EU 10% duty in NODE mode.
  (void)packet;
  return 2000 + (uint32_t)getRNG()->nextInt(0, 8) * 500;
}

// ---- 16-byte record production ---------------------------------------------

void MyMesh::feedMapRecord(const mesh::Packet* pkt) {
  MapRecord rec;
  memset(&rec, 0, sizeof(rec));

  rec.epoch = _last_now;                     // u32 epoch seconds
  rec.rssi  = (int8_t)_last_rssi;            // i8 dBm
  rec.snr_x4 = (int8_t)(pkt->getSNR() * 4);  // i8 snr*4
  rec.flags = (uint8_t)((pkt->getPayloadType() << 4) | (pkt->isRouteDirect() ? 1 : 0));
  rec.payload_len = (uint8_t)(pkt->payload_len > 255 ? 255 : pkt->payload_len);

  // Last-two path hashes (topology inference): trailing hash bytes of any path.
  if (pkt->getPathHashCount() > 0 && pkt->payload_len >= 0) {
    uint8_t hsz = pkt->getPathHashSize();
    const uint8_t* path = pkt->path;
    uint8_t count = pkt->getPathHashCount();
    if (count >= 2) {
      rec.path_hash[0] = path[(count - 2) * hsz];
      rec.path_hash[1] = path[(count - 1) * hsz];
    } else if (count == 1) {
      rec.path_hash[0] = path[0];
    }
  }

  // Advert payload layout: 32B pubkey + 4B timestamp + 64B sig + app_data.
  if (pkt->getPayloadType() == PAYLOAD_TYPE_ADVERT && pkt->payload_len >= PUB_KEY_SIZE) {
    memcpy(rec.pub_prefix, &pkt->payload[0], 6);   // u8[6] sender pubkey prefix
    // Feed distinct-sender density counter.
    _density.observe(rec.pub_prefix, 6, _last_now);
  }

  // Append to ring.
  if (_ring_len + sizeof(MapRecord) <= MAP_RING_CAPACITY) {
    memcpy(&_ring[_ring_len], &rec, sizeof(MapRecord));
    _ring_len += sizeof(MapRecord);
    _records_logged++;
  } else {
    // ring full — flush is handled in loop(); count the drop instead of
    // overwriting (the ring is flushed before it can wrap).
    _fw_records++;
  }
}

bool MyMesh::writeCalBlob(float k, float t0) {
  _selfcal.setCalibration(k, t0);
  if (!_fs) return false;
  _fs->remove(MAP_CAL_FILE);                 // avoid appending to an old blob
  File f = _fs->open(MAP_CAL_FILE, "w", true);
  if (!f) return false;
  uint8_t blob[SelfCal::BLOB_SIZE];
  _selfcal.storeCalibration(blob);
  size_t n = f.write(blob, SelfCal::BLOB_SIZE);
  f.close();
  return n == SelfCal::BLOB_SIZE;
}

void MyMesh::queueModeTransitionRecord(DensityWindow::Mode new_mode, uint8_t count) {
  // Log a mode transition as a 16-byte record so the topology log records
  // density-mode changes. Uses a synthetic record (epoch, flags field encodes
  // 0xF0 | new_mode, count in payload_len).
  MapRecord rec;
  memset(&rec, 0, sizeof(rec));
  rec.epoch = _last_now;
  rec.rssi = 0;
  rec.snr_x4 = 0;
  rec.flags = (uint8_t)(0xF0 | (new_mode == DensityWindow::MODE_MAP ? 1 : 0));
  rec.payload_len = count;
  if (_ring_len + sizeof(MapRecord) <= MAP_RING_CAPACITY) {
    memcpy(&_ring[_ring_len], &rec, sizeof(MapRecord));
    _ring_len += sizeof(MapRecord);
    _records_logged++;
  } else {
    _fw_records++;
  }
  MESH_DEBUG_PRINTLN("passive_mapper: mode -> %s (distinct=%u)",
                     new_mode == DensityWindow::MODE_MAP ? "MAP" : "NODE", (unsigned)count);
}

void MyMesh::queueTelemetryRecord() {
  // Synthetic 16-byte record: epoch + die temp (rssi) + applied offset/100 Hz
  // (path_hash, i16 LE) + flags 0xF2 (telemetry, bit 0x04 = BW125 fallback).
  // This is how "die_temp_C + applied_offset_hz" reaches the log: the normal RX
  // record layout is fixed at 16 bytes with no spare field.
  MapRecord rec;
  memset(&rec, 0, sizeof(rec));
  rec.epoch = _last_now;
  rec.rssi = (int8_t)_raw_die_temp_c;                    // whole degrees C (raw reading)
  int32_t off100 = (int32_t)(_applied_offset_hz / 100.0f); // 100 Hz units, +/-3.27 MHz
  if (off100 > 32767) off100 = 32767;
  if (off100 < -32768) off100 = -32768;
  rec.path_hash[0] = (uint8_t)(off100 & 0xFF);
  rec.path_hash[1] = (uint8_t)((off100 >> 8) & 0xFF);
  rec.flags = (uint8_t)(0xF0 | 0x2 | (_bw_fallback ? 0x04 : 0x00));
  rec.payload_len = (uint8_t)(_selfcal.isCalValid() ? 1 : 0);  // 1 = cal blob present
  if (_ring_len + sizeof(MapRecord) <= MAP_RING_CAPACITY) {
    memcpy(&_ring[_ring_len], &rec, sizeof(MapRecord));
    _ring_len += sizeof(MapRecord);
    _records_logged++;
  } else {
    _fw_records++;   // ring full; loop() flushes on the next pass
  }
  _last_telem_epoch = _last_now;
}

// ---- ring flush (block append) ----------------------------------------------

void MyMesh::flushRing() {
  if (!_fs || _ring_len == 0) { _ring_len = 0; return; }
  File f = _fs->open(MAP_LOG_FILE, "a", true);
  if (f) {
    f.write(_ring, _ring_len);
    f.close();
  }
  _ring_len = 0;
  _last_flush_ms = millis();
}

// ---- thermal self-calibration ----------------------------------------------

void MyMesh::updateSelfCal() {
  uint32_t now_ms = millis();
  float dt = (now_ms - _last_selfcal_ms) / 1000.0f;
  if (dt < 0.0f) dt = 0.0f;
  _last_selfcal_ms = now_ms;

  float t = _radio->getRadioTemperatureC();      // LR2021 die temp (XOSC sensor)
  _raw_die_temp_c = t;                           // raw reading, incl. 0.0 sentinel
  // 0.0f is the radio's "no reading" sentinel; a valid but uncalibrated/
  // out-of-band temperature is just as uncompensatable.
  bool usable = (t != 0.0f) && _selfcal.canCompensate(t);

  if (!usable) {
    if (!_bw_fallback) {
      _bw_fallback = true;
      // Fall back to a WIDE RX profile (+/-72 ppm capture window). Keep the last
      // offset applied (hold) - never blind-zero it. If the radio has no runtime
      // bandwidth hook we say so rather than silently pretending.
      bool ok = _radio->setRxBandwidthKhz(MAP_FALLBACK_BW_KHZ);
      MESH_DEBUG_PRINTLN("passive_mapper: temp unusable (t=%.1f, cal_ok=%d) -> BW%.0f fallback %s",
                         t, (int)_selfcal.isCalValid(), MAP_FALLBACK_BW_KHZ,
                         ok ? "engaged" : "UNSUPPORTED on this radio");
      queueTelemetryRecord();     // record the transition state immediately
    }
    return;
  }

  if (_bw_fallback) {
    // Temperature is back inside the calibrated band: restore the nominal profile.
    _bw_fallback = false;
    _radio->setRxBandwidthKhz(MAP_NOMINAL_BW_KHZ);
    MESH_DEBUG_PRINTLN("passive_mapper: temp usable again (t=%.1f) -> BW%.1f restored",
                       t, MAP_NOMINAL_BW_KHZ);
    queueTelemetryRecord();
  }

  _applied_die_temp_c = t;

  _selfcal.setTemperatureC(t, dt);
  float ppm = _selfcal.update();
  float offset_hz = ppm * (_nominal_freq_mhz * 1.0f); // ppm * MHz = Hz
  if (offset_hz != _applied_offset_hz) {
    _applied_offset_hz = offset_hz;
    _radio->setCenterFreqOffset(offset_hz);
  }
}

// ---- mode application -------------------------------------------------------

void MyMesh::applyMode() {
  if (_density.getMode() == DensityWindow::MODE_MAP) {
    // MAP: silent. No repeats, no adverts.
    _next_advert_epoch = 0;
  } else {
    // NODE: behave like a regular node — advert on, repeats allowed (rate-limited).
    if (MAP_ADVERT_SECS > 0) {
      _next_advert_epoch = _last_now + MAP_ADVERT_SECS;
    } else {
      _next_advert_epoch = 0;
    }
  }
  // airtime budget factor is mode-derived in getAirtimeBudgetFactor().
}

void MyMesh::sendSelfAdvert() {
  mesh::Packet* pkt = createAdvert(self_id, (const uint8_t*)MAP_ADVERT_PAYLOAD,
                                   strlen(MAP_ADVERT_PAYLOAD));
  if (pkt) {
    sendZeroHop(pkt);
  }
}
