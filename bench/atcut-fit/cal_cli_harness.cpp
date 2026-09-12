// cal_cli_harness.cpp — host-side verification of the passive_mapper `cal` CLI
// argument contract.
//
// Provenance (all code below is VERBATIM from felixfelix-bot/MeshCore,
// branch feat/passive-mapper, commit 3fdfbc8e, unless marked MOCK):
//   - parseFloat          : examples/passive_mapper/MyMesh.cpp:128-143
//   - cal command branch  : examples/passive_mapper/MyMesh.cpp:166-177
//   - writeCalBlob (FS-free part, marked MOCK where the filesystem calls were
//     dropped): examples/passive_mapper/MyMesh.cpp:270-281
//   - SelfCal blob code   : included UNMODIFIED from the clone via -I
//     (examples/passive_mapper/host/SelfCal.h)
//
// Build:
//   g++ -O2 -I<clone>/examples/passive_mapper/host -o cal_cli_harness cal_cli_harness.cpp
// The clone must be checked out at 3fdfbc8e.
//
// Each case prints ACCEPT/REJECT exactly as the firmware reply logic would,
// plus the parsed floats (hex bits) and the 15-byte blob the firmware would
// persist, so the output is directly checkable against the spec
// (CAL-CLI-SPEC.md in this directory).

#include <cstdio>
#include <cstring>
#include <cstdint>
#include "SelfCal.h"

// ---- VERBATIM MyMesh.cpp:125-143 --------------------------------------------
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
// ---- end verbatim -----------------------------------------------------------

static SelfCal _selfcal;   // same member as MyMesh.h:144

// MOCK of MyMesh::writeCalBlob (MyMesh.cpp:270-281): the real one also
// remove()/open()/write()s /selfcal.dat; here storeCalibration's output is
// captured in `blob_out` instead. Logic order and return-true path identical.
static bool writeCalBlobMock(float k, float t0, uint8_t* blob_out) {
  _selfcal.setCalibration(k, t0);                 // MyMesh.cpp:271
  if (!blob_out) return false;                    // (fs null check, :272)
  _selfcal.storeCalibration(blob_out);            // MyMesh.cpp:277
  return true;                                    // n == BLOB_SIZE, :280
}

// VERBATIM cal branch of MyMesh::handleCommand (MyMesh.cpp:166-177), with the
// reply buffer supplied by the caller exactly as main.cpp:86 does.
static bool calCommand(char* cmd, char* reply, uint8_t* blob) {
  if (strncmp(cmd, "cal ", 4) == 0) {
    // Persist a bench-derived calibration: cal <k> <T0>   (k in ppm/C^2, T0 in C)
    float k = 0.0f, t0 = 0.0f;
    const char* p = cmd + 4;
    if (parseFloat(p, &p, &k) && parseFloat(p, nullptr, &t0) && k >= 0.0f) {
      bool ok = writeCalBlobMock(k, t0, blob);
      snprintf(reply, 160, "cal k=%.6g T0=%.2fC -> %s (valid=%s)",
               k, t0, ok ? "persisted" : "RAM only, file write failed",
               _selfcal.isCalValid() ? "yes" : "no");
      return true;
    } else {
      snprintf(reply, 160, "usage: cal <k_ppm_per_C2> <T0_C>");
      return false;
    }
  }
  snprintf(reply, 160, "commands: status, mode, flush, reset, erase, cal <k> <T0>, calshow");
  return false;
}

static void hexfloat(const char* label, float f) {
  uint32_t bits; memcpy(&bits, &f, 4);
  printf("    %-4s = %.9g  (bits 0x%08X)\n", label, (double)f, bits);
}

static void run(const char* cmdline, bool expect_accept) {
  char cmd[160];
  snprintf(cmd, sizeof(cmd), "%s", cmdline);   // main.cpp delivers NUL-terminated, CR-stripped
  char reply[160]; reply[0] = 0;
  uint8_t blob[SelfCal::BLOB_SIZE]; memset(blob, 0, sizeof(blob));
  _selfcal = SelfCal();                        // fresh boot state
  bool accepted = calCommand(cmd, reply, blob);
  printf("[%s] %-28s -> %s\n", accepted == expect_accept ? "OK " : "MISMATCH",
         cmdline, reply);
  if (accepted) {
    hexfloat("k", _selfcal.getK());
    hexfloat("T0", _selfcal.getT0());
    printf("    blob : ");
    for (int i = 0; i < SelfCal::BLOB_SIZE; i++) printf("%02X ", blob[i]);
    printf("\n");
    // round-trip through the firmware loader (SelfCal.h:48-63)
    SelfCal reloaded;
    if (reloaded.loadCalibration(blob, SelfCal::BLOB_SIZE)) {
      uint32_t a, b; memcpy(&a, &blob[0], 4); memcpy(&b, &blob[4], 4);
      uint32_t c, d; float k2 = reloaded.getK(), t02 = reloaded.getT0();
      memcpy(&c, &k2, 4); memcpy(&d, &t02, 4);
      printf("    load : ok, bits %s / %s, cold-start EMA = T0 = %.2fC\n",
             a == c ? "identical" : "DIFFER", b == d ? "identical" : "DIFFER",
             (double)reloaded.getTempC());
    } else {
      printf("    load : FAILED (magic/version check)\n");
    }
  }
}

int main() {
  printf("== happy path & template precision ==\n");
  run("cal 0.034021 24.95", true);      // template precision (6 sig digits / 2 decimals)
  run("cal 0.04 25", true);             // canonical
  run("cal 0.034 24.95xyz", true);      // trailing garbage after T0: silently ignored
  run("cal 0.04 25 99", true);          // third argument ignored
  run("cal 000.0340 +024.95", true);    // leading zeros, + sign on T0
  run("cal +0.04 25", true);            // + sign on k

  printf("== separators ==\n");
  run("cal 0.04  25", true);            // multiple spaces between args
  run("cal 0.04\t25", true);            // tab between args
  run("cal 0.04,25", false);            // comma -> usage
  run("cal 0.04-25", true);             // TRAP: no separator -> T0 = -25
  run("cal 0.04- 25", false);           // '-' then space: t0 parse fails -> usage

  printf("== grammar rejections (usage:) ==\n");
  run("cal .04 25", false);             // leading digit required
  run("cal 4e-2 25", false);            // no exponent: k=4, t0 parse hits 'e' -> usage
  run("cal 0.04", false);               // T0 missing -> parse at end-of-string fails
  run("cal 0.04 ", false);              // trailing space, no T0 -> fails
  run("cal 0..04 25", false);           // k=0, then t0 parse at ".04" fails
  run("cal 25. 30", true);              // trailing dot with no fraction digits is fine

  printf("== sign/range gate (k >= 0, MyMesh.cpp:170) ==\n");
  run("cal -0.04 25", false);           // negative k rejected
  run("cal -0 25", true);               // -0.0f >= 0.0f is TRUE in IEEE -> accepted
  run("cal 0.04 -40.0", true);          // negative T0 is unrestricted
  run("cal 0.04 1000", true);           // any magnitude T0 accepted

  printf("== dispatch gate (strncmp \"cal \", MyMesh.cpp:166) ==\n");
  run("cal\t0.04 25", false);           // tab after 'cal' -> not the cal command at all
  run("cal", false);                    // no trailing space -> unknown command
  run("calshow", false);                // different command (parses nothing)

  printf("== float32 accumulation precision vs strtof ==\n");
  const char* vals[] = {"0.034021", "0.04", "24.95", "25", "0.0340211",
                        "0.04123456789012", "123456789", "0.1"};
  for (auto v : vals) {
    float fw; const char* p = v;
    parseFloat(p, nullptr, &fw);
    float ref = strtof(v, nullptr);
    uint32_t a, b; memcpy(&a, &fw, 4); memcpy(&b, &ref, 4);
    int32_t ulp = (int32_t)(a - b);
    printf("  %-16s firmware=0x%08X strtof=0x%08X %s (ulp diff %d)\n",
           v, a, b, a == b ? "==" : "!=", ulp);
  }

  printf("== serial line framing (port of main.cpp:67-93) ==\n");
  // Faithful port of the loop() reader in examples/passive_mapper/main.cpp.
  // Feeds bytes one at a time; counts how many commands complete and what
  // string each completed command carried.
  struct FramingSim {
    static int feed(const char* bytes, char cmds[][160], int max_cmds) {
      static char command[160];            // main.cpp:15
      command[0] = 0;
      int completed = 0;
      int len = strlen(command);
      for (const char* q = bytes; *q; q++) {
        char c = *q;                       // one Serial.read() per iteration
        if (len < (int)sizeof(command)-1) {  // main.cpp:70
          if (c != '\n') {                 // main.cpp:72-76
            command[len++] = c;
            command[len] = 0;
          }
          if (c == '\r') break;            // main.cpp:77
        }
      }
      if (len == (int)sizeof(command)-1) { // buffer full: main.cpp:79-81
        command[sizeof(command)-1] = '\r';
        len++;
      }
      if (len > 0 && command[len-1] == '\r') {  // main.cpp:83
        command[len-1] = 0;                // main.cpp:85
        if (completed < max_cmds) { snprintf(cmds[completed], 160, "%s", command); }
        completed++;
        command[0] = 0;                    // main.cpp:92
      }
      return completed;
    }
  };
  struct { const char* wire; int expect_n; const char* expect_cmd; } framing[] = {
    { "cal 0.04 25\r",            1, "cal 0.04 25"    },  // CR alone: executes
    { "cal 0.04 25\r\n",          1, "cal 0.04 25"    },  // CRLF: executes once, LF drained
    { "cal 0.04 25\n",            0, ""               },  // LF-only: NEVER executes
    { "cal 0.04 25",              0, ""               },  // no terminator: pending forever
    { "\r",                       1, ""               },  // bare CR: empty cmd -> help reply
    { "cal 0.04\t25\r",           1, "cal 0.04\t25"   },  // tab sep survives framing
  };
  for (auto& f : framing) {
    char cmds[1][160]; cmds[0][0] = 0;
    int n = FramingSim::feed(f.wire, cmds, 1);
    // NOTE: the loop() reader consumes one line per pass; the LF of CRLF is
    // drained on the NEXT pass, so a CRLF stream over a real serial link
    // completes exactly one command. Single-pass sim mirrors one loop pass.
    bool pass = (n == f.expect_n) &&
                (f.expect_n == 0 || strcmp(cmds[0], f.expect_cmd) == 0);
    printf("  [%s] wire=\"%s\" -> %d command(s)%s%s\n", pass ? "OK " : "MISMATCH",
           f.wire, n, n ? ", first=\"" : "", n ? cmds[0] : "");
  }
  return 0;
}
