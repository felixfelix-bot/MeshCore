// Host test for DensityWindow (pure C++, no Arduino deps).
// RED-GREEN: this test targets behavior that does not exist yet.
#include <stdio.h>
#include <string.h>
#include <assert.h>

#include "../DensityWindow.h"

static int failures = 0;
#define CHECK(cond) do { if (!(cond)) { \
  printf("FAIL %s:%d: %s\n", __FILE__, __LINE__, #cond); failures++; } } while (0)

static void fill_key(uint8_t* out, uint8_t seed) {
  for (int i = 0; i < 6; i++) out[i] = (uint8_t)(seed + i);
}

int main() {
  // --- count distinct: 3 senders observed at same time ----------------------
  {
    DensityWindow w;
    uint8_t a[6], b[6], c[6];
    fill_key(a, 1); fill_key(b, 2); fill_key(c, 3);
    uint32_t now = 1000000;
    w.observe(a, 6, now); w.observe(a, 6, now); // duplicate same key
    w.observe(b, 6, now); w.observe(c, 6, now);
    CHECK(w.distinctCount(now) == 3);
  }

  // --- count distinct: duplicates across time collapse ----------------------
  {
    DensityWindow w;
    uint8_t a[6]; fill_key(a, 9);
    uint32_t now = 1000000;
    w.observe(a, 6, now);
    w.observe(a, 6, now + 60);
    w.observe(a, 6, now + 120);
    CHECK(w.distinctCount(now + 120) == 1);
  }

  // --- window expiry: old entries drop out of the 10-min window -------------
  {
    DensityWindow w;
    uint8_t a[6], b[6];
    fill_key(a, 1); fill_key(b, 2);
    uint32_t now = 1000000;
    w.observe(a, 6, now);
    w.observe(b, 6, now + 30);
    // a was heard at 1000000; at 1000000+10*60+1 it expires
    uint32_t later = now + 10 * 60 + 1;
    CHECK(w.distinctCount(later) == 1); // only b remains (b heard at +30 < window)
    // b heard at now+30 expires at now+30+600
    uint32_t later2 = now + 700;
    CHECK(w.distinctCount(later2) == 0);
  }

  // --- fresh observation keeps a key alive (sliding window) -----------------
  {
    DensityWindow w;
    uint8_t a[6]; fill_key(a, 1);
    uint32_t now = 1000000;
    w.observe(a, 6, now);
    w.observe(a, 6, now + 590);       // refresh just inside window
    CHECK(w.distinctCount(now + 660) == 1); // still alive (refreshed at +590)
    CHECK(w.distinctCount(now + 590 + 600 + 1) == 0); // then expires
  }

  // --- hysteresis: 5-up threshold enters MAP mode ----------------------------
  {
    DensityWindow w;
    uint32_t now = 2000000;
    uint8_t keys[5][6];
    for (int i = 0; i < 5; i++) fill_key(keys[i], 10 + i);
    for (int i = 0; i < 5; i++) w.observe(keys[i], 6, now);
    // First update call at/above threshold starts the dwell candidate, stays NODE.
    CHECK(w.update(now + 10) == DensityWindow::MODE_NODE);
    // Just below dwell: still NODE.
    CHECK(w.update(now + 10 + 299) == DensityWindow::MODE_NODE);
    // After dwell (>=300s) at >=5 distinct it transitions to MAP.
    CHECK(w.update(now + 10 + 301) == DensityWindow::MODE_MAP);
  }

  // --- hysteresis: 2-down threshold returns to NODE mode --------------------
  {
    DensityWindow w;
    uint32_t now = 3000000;
    // Start in MAP mode by seeding 5 senders and dwelling.
    uint8_t keys[5][6];
    for (int i = 0; i < 5; i++) fill_key(keys[i], 20 + i);
    for (int i = 0; i < 5; i++) w.observe(keys[i], 6, now);
    CHECK(w.update(now) == DensityWindow::MODE_NODE);      // candidate starts
    CHECK(w.update(now + 301) == DensityWindow::MODE_MAP); // now in MAP
    // Now only 2 distinct remain -> need dwell before dropping to NODE.
    // Rely on expiry so that only 2 remain at now+601.
    uint32_t t = now + 601;
    // keys heard at `now` only, so they all expire at once. Re-seed 2 fresh.
    uint8_t x[6], y[6]; fill_key(x, 30); fill_key(y, 31);
    w.observe(x, 6, t); w.observe(y, 6, t);
    CHECK(w.distinctCount(t) == 2);
    // First update at <=2 starts NODE candidate but stays MAP (below dwell).
    CHECK(w.update(t) == DensityWindow::MODE_MAP);
    // Just below dwell: still MAP.
    CHECK(w.update(t + 299) == DensityWindow::MODE_MAP);
    // After dwell at <=2 it drops to NODE.
    CHECK(w.update(t + 301) == DensityWindow::MODE_NODE);
  }

  // --- no transition when count sits between thresholds ----------------------
  {
    DensityWindow w;
    uint32_t now = 4000000;
    uint8_t keys[3][6];
    for (int i = 0; i < 3; i++) fill_key(keys[i], 40 + i);
    for (int i = 0; i < 3; i++) w.observe(keys[i], 6, now);
    // count=3 is between down(2) and up(5): no transition even after dwell.
    CHECK(w.update(now) == DensityWindow::MODE_NODE);
    // And a later large dwell still does not flap.
    CHECK(w.update(now + 900) == DensityWindow::MODE_NODE);
  }

  // --- dwell is reset if count re-crosses before dwell completes ------------
  {
    DensityWindow w;
    uint32_t now = 5000000;
    // Force MAP mode first: 5 keys + dwell.
    uint8_t keys[5][6];
    for (int i = 0; i < 5; i++) fill_key(keys[i], 50 + i);
    for (int i = 0; i < 5; i++) w.observe(keys[i], 6, now);
    CHECK(w.update(now) == DensityWindow::MODE_NODE);        // candidate starts
    CHECK(w.update(now + 301) == DensityWindow::MODE_MAP);   // now in MAP

    // Now we are in MAP. Drop to <=2 then bounce back above 2 before dwell.
    // Start a fresh base epoch.
    uint32_t t2 = now + 2000;
    uint8_t a[6]; fill_key(a, 60);
    w.observe(a, 6, t2);
    CHECK(w.distinctCount(t2) == 1);           // now in "low" candidate
    // Before 300s dwell, a 3rd distinct arrives -> count back above 2, reset candidate.
    uint8_t b[6], c[6]; fill_key(b, 61); fill_key(c, 62);
    w.observe(b, 6, t2 + 50); w.observe(c, 6, t2 + 50);
    CHECK(w.distinctCount(t2 + 50) == 3);       // candidate invalidated (count>2 again)
    // Since count never stayed <=2 for full dwell, still MAP.
    CHECK(w.update(t2 + 400) == DensityWindow::MODE_MAP);
  }

  if (failures == 0) {
    printf("ALL DENSITY_WINDOW TESTS PASSED\n");
    return 0;
  }
  printf("%d DENSITY_WINDOW TEST(S) FAILED\n", failures);
  return 1;
}
