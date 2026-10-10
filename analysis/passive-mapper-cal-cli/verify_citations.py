#!/usr/bin/env python3
"""Byte-exact citation verifier for the pinned `cal <k> <T0>` report.

Every (path, line, expected-substring) below is re-extracted from
`git show <PIN>:<path>` — never from memory and never from the working tree.
Exit 0 only if every citation matches.
"""
import subprocess
import sys

PIN = "3fdfbc8e120e13d7543fe224c380e27533e720aa"
REPO = "/home/c03rad0r/worktrees/cal-serial-pin"

CITATIONS = [
    # ---- main.cpp : serial reader / terminator / dispatch ----
    ("examples/passive_mapper/main.cpp", 15, "static char command[160];"),
    ("examples/passive_mapper/main.cpp", 18, "Serial.begin(115200);"),
    ("examples/passive_mapper/main.cpp", 30, "FILESYSTEM* fs;"),
    ("examples/passive_mapper/main.cpp", 70, "while (Serial.available() && len < (int)sizeof(command)-1) {"),
    ("examples/passive_mapper/main.cpp", 72, "if (c != '\\n') {"),
    ("examples/passive_mapper/main.cpp", 77, "if (c == '\\r') break;"),
    ("examples/passive_mapper/main.cpp", 79, "if (len == (int)sizeof(command)-1) {  // command buffer full"),
    ("examples/passive_mapper/main.cpp", 80, "command[sizeof(command)-1] = '\\r';"),
    ("examples/passive_mapper/main.cpp", 83, "if (len > 0 && command[len - 1] == '\\r') {  // received complete line"),
    ("examples/passive_mapper/main.cpp", 88, "the_mesh.handleCommand(command, reply);"),
    # ---- MyMesh.cpp : dispatch, parser, handler, blob writer ----
    ("examples/passive_mapper/MyMesh.cpp", 15, "// model offset_ppm = -k*(T-T0)^2 from the LR2021 die temperature, applied as"),
    ("examples/passive_mapper/MyMesh.cpp", 125, '// Minimal decimal float parser for the CLI. Deliberately avoids sscanf("%f")/'),
    ("examples/passive_mapper/MyMesh.cpp", 127, "// is not worth it for two calibration numbers. Accepts [-+]?digits[.digits]."),
    ("examples/passive_mapper/MyMesh.cpp", 128, "static bool parseFloat(const char* s, const char** endp, float* out) {"),
    ("examples/passive_mapper/MyMesh.cpp", 129, "while (*s == ' ' || *s == '\\t') s++;"),
    ("examples/passive_mapper/MyMesh.cpp", 131, "if (*s == '-') { neg = true; s++; } else if (*s == '+') { s++; }"),
    ("examples/passive_mapper/MyMesh.cpp", 132, "if (*s < '0' || *s > '9') return false;"),
    ("examples/passive_mapper/MyMesh.cpp", 134, "while (*s >= '0' && *s <= '9') { v = v * 10.0f + (float)(*s - '0'); s++; }"),
    ("examples/passive_mapper/MyMesh.cpp", 135, "if (*s == '.') {"),
    ("examples/passive_mapper/MyMesh.cpp", 138, "while (*s >= '0' && *s <= '9') { v += (float)(*s - '0') * scale; scale *= 0.1f; s++; }"),
    ("examples/passive_mapper/MyMesh.cpp", 145, "void MyMesh::handleCommand(char* cmd, char* reply) {"),
    ("examples/passive_mapper/MyMesh.cpp", 166, '} else if (strncmp(cmd, "cal ", 4) == 0) {'),
    ("examples/passive_mapper/MyMesh.cpp", 167, "// Persist a bench-derived calibration: cal <k> <T0>   (k in ppm/C^2, T0 in C)"),
    ("examples/passive_mapper/MyMesh.cpp", 169, "const char* p = cmd + 4;"),
    ("examples/passive_mapper/MyMesh.cpp", 170, "if (parseFloat(p, &p, &k) && parseFloat(p, nullptr, &t0) && k >= 0.0f) {"),
    ("examples/passive_mapper/MyMesh.cpp", 171, "bool ok = writeCalBlob(k, t0);"),
    ("examples/passive_mapper/MyMesh.cpp", 172, 'snprintf(reply, 160, "cal k=%.6g T0=%.2fC -> %s (valid=%s)",'),
    ("examples/passive_mapper/MyMesh.cpp", 173, 'k, t0, ok ? "persisted" : "RAM only, file write failed",'),
    ("examples/passive_mapper/MyMesh.cpp", 176, 'snprintf(reply, 160, "usage: cal <k_ppm_per_C2> <T0_C>");'),
    ("examples/passive_mapper/MyMesh.cpp", 179, 'snprintf(reply, 160, "cal valid=%s k=%.6g T0=%.2fC range=+/-%.0fC die_temp=%.1f off_hz=%.0f",'),
    ("examples/passive_mapper/MyMesh.cpp", 183, 'snprintf(reply, 160, "commands: status, mode, flush, reset, erase, cal <k> <T0>, calshow");'),
    ("examples/passive_mapper/MyMesh.cpp", 60, 'File f = _fs->open(MAP_CAL_FILE, "r");'),
    ("examples/passive_mapper/MyMesh.cpp", 66, "if (_selfcal.loadCalibration(blob, SelfCal::BLOB_SIZE)) {"),
    ("examples/passive_mapper/MyMesh.cpp", 270, "bool MyMesh::writeCalBlob(float k, float t0) {"),
    ("examples/passive_mapper/MyMesh.cpp", 271, "_selfcal.setCalibration(k, t0);"),
    ("examples/passive_mapper/MyMesh.cpp", 273, "_fs->remove(MAP_CAL_FILE);                 // avoid appending to an old blob"),
    ("examples/passive_mapper/MyMesh.cpp", 274, 'File f = _fs->open(MAP_CAL_FILE, "w", true);'),
    ("examples/passive_mapper/MyMesh.cpp", 277, "_selfcal.storeCalibration(blob);"),
    ("examples/passive_mapper/MyMesh.cpp", 278, "size_t n = f.write(blob, SelfCal::BLOB_SIZE);"),
    ("examples/passive_mapper/MyMesh.cpp", 279, "f.close();"),
    ("examples/passive_mapper/MyMesh.cpp", 280, "return n == SelfCal::BLOB_SIZE;"),
    ("examples/passive_mapper/MyMesh.cpp", 356, "bool usable = (t != 0.0f) && _selfcal.canCompensate(t);"),
    ("examples/passive_mapper/MyMesh.cpp", 386, "float offset_hz = ppm * (_nominal_freq_mhz * 1.0f); // ppm * MHz = Hz"),
    # ---- MyMesh.h ----
    ("examples/passive_mapper/MyMesh.h", 17, "using File = fs::File;"),
    ("examples/passive_mapper/MyMesh.h", 48, '#define MAP_CAL_FILE        "/selfcal.dat"'),
    ("examples/passive_mapper/MyMesh.h", 166, "bool writeCalBlob(float k, float t0);"),
    # ---- host/SelfCal.h ----
    ("examples/passive_mapper/host/SelfCal.h", 2, "// No Arduino dependencies. Model: offset_ppm = -k*(T-T0)^2 (parabolic AT-cut"),
    ("examples/passive_mapper/host/SelfCal.h", 21, "static const uint8_t BLOB_SIZE = 3 * 4 + 2 + 1; // 15 bytes"),
    ("examples/passive_mapper/host/SelfCal.h", 22, "static const uint16_t CAL_MAGIC = 0x5343;       // 'SC'"),
    ("examples/passive_mapper/host/SelfCal.h", 28, "static constexpr float SLEW_PPM     = 25.0f;     // max |delta| per update"),
    ("examples/passive_mapper/host/SelfCal.h", 29, "static constexpr float DEADBAND_PPM = 1.0f;      // ignore sub-deadband changes"),
    ("examples/passive_mapper/host/SelfCal.h", 30, "static constexpr float MAX_PPM      = 300.0f;    // absolute output clamp"),
    ("examples/passive_mapper/host/SelfCal.h", 36, "static constexpr float CAL_RANGE_C  = 60.0f;"),
    ("examples/passive_mapper/host/SelfCal.h", 39, ": _k(0.0f), _T0(0.0f), _ver(0), _cal_valid(false),"),
    ("examples/passive_mapper/host/SelfCal.h", 44, "void setCalibration(float k, float T0) {"),
    ("examples/passive_mapper/host/SelfCal.h", 45, "_k = k; _T0 = T0; _cal_valid = true;"),
    ("examples/passive_mapper/host/SelfCal.h", 66, "memcpy(blob, &_k, 4);"),
    ("examples/passive_mapper/host/SelfCal.h", 67, "memcpy(blob + 4, &_T0, 4);"),
    ("examples/passive_mapper/host/SelfCal.h", 68, "float spare = 0.0f;"),
    ("examples/passive_mapper/host/SelfCal.h", 70, "uint16_t magic = CAL_MAGIC;"),
    ("examples/passive_mapper/host/SelfCal.h", 72, "blob[14] = _ver;"),
    ("examples/passive_mapper/host/SelfCal.h", 89, "float raw = -_k * (_temp_ema - _T0) * (_temp_ema - _T0);"),
    ("examples/passive_mapper/host/SelfCal.h", 91, "if (raw > MAX_PPM) raw = MAX_PPM;"),
    ("examples/passive_mapper/host/SelfCal.h", 96, "if (delta > SLEW_PPM) delta = SLEW_PPM;"),
    ("examples/passive_mapper/host/SelfCal.h", 101, "if (fabsf(target - _offset_ppm) < DEADBAND_PPM) {"),
    ("examples/passive_mapper/host/SelfCal.h", 107, "if (_offset_ppm > MAX_PPM) _offset_ppm = MAX_PPM;"),
    ("examples/passive_mapper/host/SelfCal.h", 136, "bool inCalRange(float t) const {"),
    ("examples/passive_mapper/host/SelfCal.h", 137, "if (!_cal_valid) return false;"),
    ("examples/passive_mapper/host/SelfCal.h", 140, "return d <= CAL_RANGE_C;"),
    ("examples/passive_mapper/host/SelfCal.h", 157, "void setVersion(uint8_t v) { _ver = v; }"),
    # ---- FS mapping + tree-wide corroboration ----
    ("src/helpers/IdentityStore.h", 3, "#if defined(ESP32) || defined(RP2040_PLATFORM)"),
    ("src/helpers/IdentityStore.h", 5, "#define FILESYSTEM  fs::FS"),
    ("src/helpers/CommonCLI.cpp", 150, 'File file = fs->open("/prefs.json", "w", true);'),
    ("examples/companion_radio/DataStore.cpp", 41, 'return fs->open(filename, "w", true);'),
    ("examples/passive_mapper/host/tests/test_self_cal.cpp", 152, "cal.setCalibration(0.037f, -12.5f);"),
]


def main() -> int:
    cache: dict[str, list[str]] = {}
    fails = 0
    for path, lineno, expected in CITATIONS:
        if path not in cache:
            out = subprocess.run(
                ["git", "show", f"{PIN}:{path}"],
                cwd=REPO, capture_output=True, text=True, check=True,
            )
            cache[path] = out.stdout.splitlines()
        lines = cache[path]
        if lineno < 1 or lineno > len(lines):
            print(f"FAIL {path}:{lineno} -> file has only {len(lines)} lines")
            fails += 1
            continue
        actual = lines[lineno - 1]
        if expected in actual:
            print(f"PASS {path}:{lineno}")
        else:
            print(f"FAIL {path}:{lineno}\n  expected: {expected!r}\n  actual  : {actual!r}")
            fails += 1
    print(f"\nPIN={PIN}")
    print(f"citations checked: {len(CITATIONS)}  failures: {fails}")
    if fails == 0:
        print("ALL CITATIONS VERIFIED AT PIN")
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())
