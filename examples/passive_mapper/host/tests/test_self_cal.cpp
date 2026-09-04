// Host test for SelfCal (pure C++, no Arduino deps).
// RED-GREEN: targets the open-loop thermal compensation state machine.
#include <stdio.h>
#include <string.h>
#include <math.h>
#include <assert.h>

#include "../SelfCal.h"

static int failures = 0;
#define CHECK(cond) do { if (!(cond)) { \
  printf("FAIL %s:%d: %s\n", __FILE__, __LINE__, #cond); failures++; } } while (0)

static float close(float a, float b, float eps) { return fabsf(a - b) <= eps; }

int main() {
  // --- cold start from cal table is never zero -------------------------------
  {
    SelfCal cal;
    cal.setCalibration(0.04f, 25.0f);   // k=0.04 ppm/C^2, T0=25C
    cal.setTemperatureC(-40.0f, 1.0f);  // cold-start die temp
    // offset_ppm = -k*(T-T0)^2 = -0.04*65^2 = -169 ppm.
    // Slew clamp limits the first step; verify it is NONZERO (never blind 0)
    // and converges to ~-169 once it settles.
    float o0 = cal.update();
    CHECK(fabsf(o0) > 0.0f);
    // converge: hold temp, repeatedly update (each step slews <=25ppm)
    for (int i = 0; i < 20; i++) { cal.update(); }
    CHECK(fabsf(cal.getOffsetPpm() + 169.0f) < 2.0f);
    CHECK(cal.isCalValid());
  }

  // --- open-loop model at T0 is ~0 (deadband zeros it) ------------------------
  {
    SelfCal cal;
    cal.setCalibration(0.04f, 25.0f);
    cal.setTemperatureC(25.0f, 1.0f);
    // model = -0.04*0 = 0; within deadband -> exactly 0
    CHECK(cal.update() == 0.0f);
  }

  // --- asymmetric temp: +50C and -50C give same magnitude (parabolic model) ---
  {
    SelfCal cal1, cal2;
    cal1.setCalibration(0.04f, 25.0f); cal2.setCalibration(0.04f, 25.0f);
    cal1.setTemperatureC(75.0f, 10.0f);
    cal2.setTemperatureC(-25.0f, 10.0f);
    CHECK(fabsf(cal1.update()) - fabsf(cal2.update()) < 1.0f);
  }

  // --- EMA smooths temperature: step in T does not jump fully immediately -----
  {
    SelfCal cal;
    cal.setCalibration(0.05f, 25.0f);
    // settle at 25C
    cal.setTemperatureC(25.0f, 30.0f); cal.update();
    // now step to -20; after 1s EMA only moves a fraction of the 45C step
    cal.setTemperatureC(-20.0f, 1.0f);
    float mid = cal.getTempC();
    CHECK(mid > -20.0f && mid < 24.0f);       // between, converging toward -20
    // after a long settle it reaches ~-20
    cal.setTemperatureC(-20.0f, 200.0f);
    CHECK(close(cal.getTempC(), -20.0f, 1.0f));
  }

  // --- max clamp: extreme temp does not exceed +-300 ppm ---------------------
  {
    SelfCal cal;
    cal.setCalibration(0.04f, 25.0f);
    cal.setTemperatureC(-300.0f, 30.0f);  // absurd temp -> huge raw model
    CHECK(fabsf(cal.update()) <= 300.0f);
  }

  // --- slew clamp: a large instantaneous residual change is limited to ~25ppm --
  {
    SelfCal cal;
    cal.setCalibration(0.04f, 25.0f);
    cal.setTemperatureC(25.0f, 30.0f); cal.update();   // ~0 ppm
    // Big step: model at -40C is -169ppm; from ~0 the slew clamp caps movement.
    cal.setTemperatureC(-40.0f, 1.0f);
    float o1 = cal.update();
    float o2 = cal.update();   // second update same temp, still converging
    CHECK(fabsf(o1) <= 25.0f + 1.0f);   // first update moved at most ~25ppm
    CHECK(fabsf(o2) <= fabsf(o1) + 25.0f + 1.0f);
  }

  // --- deadband: tiny changes near steady state produce no output change -----
  {
    SelfCal cal;
    cal.setCalibration(0.04f, 25.0f);
    cal.setTemperatureC(25.9f, 30.0f);   // just below 1ppm-equivalent
    float v1 = cal.update();
    cal.setTemperatureC(26.1f, 30.0f);   // tiny temp change
    float v2 = cal.update();
    CHECK(fabsf(v2 - v1) < 1.0f);        // deadband suppresses microchanges
  }

  // --- mute holds output ------------------------------------------------------
  {
    SelfCal cal;
    cal.setCalibration(0.04f, 25.0f);
    cal.setTemperatureC(-40.0f, 10.0f);
    cal.update();
    float held = cal.getOffsetPpm();
    cal.setMuted(true);
    cal.setTemperatureC(25.0f, 10.0f);   // big change, but muted
    cal.update();
    CHECK(fabsf(cal.getOffsetPpm() - held) < 0.5f);  // held
    cal.setMuted(false);
    cal.update();
    CHECK(fabsf(cal.getOffsetPpm() - held) > 0.5f);  // released, moves
    CHECK(cal.isMuted() == false);
  }

  // --- FEI secondary: SNR gate rejects feed below -10dB ----------------------
  {
    SelfCal cal;
    cal.setCalibration(0.04f, 25.0f);
    cal.setTemperatureC(25.0f, 10.0f); cal.update();
    cal.feedMeasured(200.0f, -20.0f);   // bad SNR -> rejected (inert on LR2021)
    cal.update();
    CHECK(cal.getOffsetPpm() == 0.0f);  // no change (model at 25C is 0)
    // now a good-SNR residual drives the offset positive
    for (int i = 0; i < 5; i++) {
      cal.feedMeasured(200.0f, -5.0f);  // good SNR -> accepted
      cal.update();
    }
    CHECK(cal.getOffsetPpm() > 0.0f);
  }

  // --- serialization roundtrip preserves cal params --------------------------
  {
    SelfCal cal;
    cal.setCalibration(0.037f, -12.5f);
    uint8_t blob[SelfCal::BLOB_SIZE];
    cal.storeCalibration(blob);
    SelfCal cal2;
    bool ok = cal2.loadCalibration(blob, SelfCal::BLOB_SIZE);
    CHECK(ok);
    CHECK(close(cal2.getK(), 0.037f, 1e-4f));
    CHECK(close(cal2.getT0(), -12.5f, 1e-3f));
    CHECK(cal2.isCalValid());
    // tamper with magic (bytes 12..13) -> invalid
    SelfCal cal3;
    uint8_t bad[SelfCal::BLOB_SIZE];
    memcpy(bad, blob, SelfCal::BLOB_SIZE);
    bad[12] ^= 0xFF;
    CHECK(cal3.loadCalibration(bad, SelfCal::BLOB_SIZE) == false);
  }

  if (failures == 0) {
    printf("ALL SELF_CAL TESTS PASSED\n");
    return 0;
  }
  printf("%d SELF_CAL TEST(S) FAILED\n", failures);
  return 1;
}
