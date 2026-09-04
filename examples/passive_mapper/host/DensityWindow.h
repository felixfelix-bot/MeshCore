// DensityWindow.h - pure host-compilable density-adaptive window classifier.
// No Arduino dependencies. Tracked distinct sender pubkeys in a sliding window,
// with asymmetric hysteresis thresholds (up=5, down=2) and a dwell time before
// each mode transition.
#pragma once

#include <stdint.h>
#include <string.h>

class DensityWindow {
public:
  enum Mode : uint8_t { MODE_NODE = 0, MODE_MAP = 1 };

  // up to this many tracked pubkey entries in the sliding window
  static const uint8_t MAX_ENTRIES = 64;
  static const uint8_t KEY_LEN = 6;

  DensityWindow(uint32_t window_secs = 600,
                uint8_t map_up_threshold = 5,
                uint8_t node_down_threshold = 2,
                uint32_t dwell_secs = 300)
    : _window_secs(window_secs), _up_th(map_up_threshold),
      _down_th(node_down_threshold), _dwell_secs(dwell_secs),
      _n(0), _mode(MODE_NODE), _candidate_valid(false), _candidate_at(0),
      _candidate_mode(MODE_NODE), _transition_at(0) { }

  // Record a distinct sender pubkey prefix heard at 'now' (epoch secs).
  void observe(const uint8_t* pubkey_prefix, uint8_t len, uint32_t now) {
    if (len > KEY_LEN) len = KEY_LEN;
    // refresh if present
    for (uint8_t i = 0; i < _n; i++) {
      if (memcmp(_entries[i].key, pubkey_prefix, KEY_LEN) == 0) {
        _entries[i].last_seen = now;
        return;
      }
    }
    if (_n < MAX_ENTRIES) {
      memcpy(_entries[_n].key, pubkey_prefix, KEY_LEN);
      _entries[_n].last_seen = now;
      _n++;
    } else {
      // table full: overwrite the oldest entry
      uint32_t oldest = now;
      uint8_t idx = 0;
      for (uint8_t i = 0; i < _n; i++) {
        if (_entries[i].last_seen < oldest) { oldest = _entries[i].last_seen; idx = i; }
      }
      memcpy(_entries[idx].key, pubkey_prefix, KEY_LEN);
      _entries[idx].last_seen = now;
    }
  }

  // Distinct senders with last-heard within the window at 'now'.
  uint8_t distinctCount(uint32_t now) {
    prune(now);
    return _n;
  }

  // Update mode with hysteresis + dwell. Call periodically with 'now'.
  Mode update(uint32_t now) {
    prune(now);
    if (_mode == MODE_NODE) {
      // Looking to go up to MAP when count >= up threshold for dwell.
      if (_n >= _up_th) {
        if (!_candidate_valid || _candidate_mode != MODE_MAP) {
          _candidate_valid = true; _candidate_mode = MODE_MAP; _candidate_at = now;
        }
        if (now - _candidate_at >= _dwell_secs) {
          _mode = MODE_MAP; _candidate_valid = false; _transition_at = now;
        }
      } else {
        _candidate_valid = false;   // count fell back below threshold, reset dwell
      }
    } else { // MODE_MAP
      // Looking to go down to NODE when count <= down threshold for dwell.
      if (_n <= _down_th) {
        if (!_candidate_valid || _candidate_mode != MODE_NODE) {
          _candidate_valid = true; _candidate_mode = MODE_NODE; _candidate_at = now;
        }
        if (now - _candidate_at >= _dwell_secs) {
          _mode = MODE_NODE; _candidate_valid = false; _transition_at = now;
        }
      } else {
        _candidate_valid = false;
      }
    }
    return _mode;
  }

  Mode getMode() const { return _mode; }
  uint32_t lastTransitionAt() const { return _transition_at; }

private:
  struct Entry {
    uint8_t key[KEY_LEN];
    uint32_t last_seen;
  };

  void prune(uint32_t now) {
    uint8_t w = 0;
    for (uint8_t i = 0; i < _n; i++) {
      if (now - _entries[i].last_seen < _window_secs) {
        if (w != i) _entries[w] = _entries[i];
        w++;
      }
    }
    _n = w;
  }

  uint32_t _window_secs;
  uint8_t _up_th, _down_th;
  uint32_t _dwell_secs;
  uint8_t _n;
  Mode _mode;
  bool _candidate_valid;
  uint32_t _candidate_at;
  Mode _candidate_mode;
  uint32_t _transition_at;
  Entry _entries[MAX_ENTRIES];
};
