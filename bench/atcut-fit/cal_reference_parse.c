/* cal_reference_parse.c - reference oracle for cal_rounding.py (card t_8c1ba27e).
 *
 * The parseFloat() below is VERBATIM firmware code, copied byte-for-byte from
 * the companion host harness bench/atcut-fit/cal_cli_harness.cpp:27-47, which
 * carries the provenance header:
 *   parseFloat : examples/passive_mapper/MyMesh.cpp:128-143
 *   (felixfelix-bot/MeshCore, branch feat/passive-mapper, commit 3fdfbc8e)
 * It is the exact function the contract cites at CAL-CLI-SPEC.md:54-63,
 * :118-120.  It is compiled here only as an ORACLE so the Python module's
 * float32 accumulation can be byte-compared against real C float arithmetic;
 * nothing in the Python module is derived from this file except the value
 * FRACTION_SCALE_INIT = 0.1f, which the contract leaves as GAP G4 and which
 * is marked as such at the call site in cal_rounding.py.
 *
 * Build (see cal_rounding_parity.py, which does this itself):
 *   gcc -std=c99 -O2 -ffp-contract=off -o _calref_parse cal_reference_parse.c
 *   (also verified with -O0 and -O2 -ffp-contract=fast)
 *
 * Protocol: one literal per stdin line (no embedded whitespace/newlines),
 * argv[1] selects the echo format ("k" = %.6g, "t0" = %.2f).
 * For each input line prints:
 *   <accept 0|1> TAB <bits 0xXXXXXXXX | -> TAB <end index> TAB <emit string>
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

/* ---- VERBATIM MyMesh.cpp:125-143 (via cal_cli_harness.cpp:27-47) -------- */
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
/* ---- end verbatim ------------------------------------------------------- */

int main(int argc, char** argv) {
  const char* mode = (argc > 1) ? argv[1] : "k";
  char line[4096];
  char buf[512];
  while (fgets(line, sizeof line, stdin)) {
    size_t n = strlen(line);
    while (n && (line[n-1] == '\n' || line[n-1] == '\r')) line[--n] = 0;
    const char* end = NULL;
    float v = 0.0f;
    bool ok = parseFloat(line, &end, &v);
    if (!ok) { printf("0\t-\t-\t-\n"); continue; }
    uint32_t bits; memcpy(&bits, &v, 4);
    ptrdiff_t consumed = end ? (end - line) : 0;
    if (strcmp(mode, "t0") == 0) snprintf(buf, sizeof buf, "%.2f", v);
    else                          snprintf(buf, sizeof buf, "%.6g", v);
    printf("1\t0x%08X\t%ld\t%s\n", bits, (long)consumed, buf);
  }
  return 0;
}
