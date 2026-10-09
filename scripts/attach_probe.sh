#!/usr/bin/env bash
# attach_probe.sh — chamber attachment proof (task t_0e98e408 / meshcore board)
# Reproducible negative-evidence capture: is a thermal-chamber controller
# physically attached to THIS host, or reachable on the local network?
# Writes raw evidence to raw/. Read-only. No chamber is commanded.
set -u
OUT="$(cd "$(dirname "$0")/.." && pwd)/raw"
mkdir -p "$OUT"
say() { echo "===== $* =====" ; }
run() { # run <outfile> <cmd...>
  local f="$OUT/$1"; shift
  { echo "\$ $*"; "$@" 2>&1; echo "[exit=$?]"; } > "$f"
  echo "wrote $(wc -l < "$f") lines -> $f"
}

say "environment"
{ date -u '+%Y-%m-%dT%H:%M:%SZ'; hostname; uname -a; echo "user=$(id -un)"; } > "$OUT/00-environment.txt"
cat "$OUT/00-environment.txt"

say "A. serial-device enumeration (ls -l /dev/serial/by-id/*, ttyUSB/ttyACM)"
{
  echo '$ ls -l /dev/serial/by-id/*'
  ls -l /dev/serial/by-id/* 2>&1
  echo
  echo '$ ls -l /dev/ttyUSB* /dev/ttyACM*'
  ls -l /dev/ttyUSB* /dev/ttyACM* 2>&1
} > "$OUT/10-serial-devices.txt"
cat "$OUT/10-serial-devices.txt"

say "B. USB device tree (is any USB-serial bridge present?)"
{
  echo '$ lsusb'
  lsusb 2>&1
  echo
  echo '$ lsusb | grep -iE "ftdi|prolific|cp210|ch34|serial|rs232|rs485|usb-serial"'
  lsusb 2>&1 | grep -iE 'ftdi|prolific|cp210|ch34|serial|rs232|rs485' || echo '(no match — no USB-serial bridge chip present)'
} > "$OUT/11-usb-devices.txt"
cat "$OUT/11-usb-devices.txt"

say "C. dmesg evidence (may be restricted)"
{
  echo '$ dmesg | grep -iE "usb|serial|tty|ftdi|prolific|cp210|ch34" | tail -40'
  (dmesg 2>&1 | grep -iE 'usb|serial|tty|ftdi|prolific|cp210|ch34' | tail -40) || echo '(dmesg unavailable / kernel.dmesg_restrict)'
  echo
  echo '$ cat /proc/version'
  cat /proc/version 2>&1
} > "$OUT/12-dmesg.txt"
cat "$OUT/12-dmesg.txt"

say "D. identity query on each enumerated ttyUSB (serial probe, *IDN?/ATI)"
python3 - "$OUT/20-serial-identity.txt" <<'PY' 2>&1 | tee -a "$OUT/20-serial-identity.txt"
import serial, time, sys, glob
paths = sorted(glob.glob('/dev/ttyUSB*')) + sorted(glob.glob('/dev/ttyACM*'))
print("# serial identity probe; query bytes written verbatim, reply captured byte-for-byte")
if not paths:
    print("# NO ttyUSB*/ttyACM* paths exist")
for p in paths:
    for label, payload, baud in (("*IDN? (SCPI)", b"*IDN?\r\n", 9600),
                                 ("ATI (modem AT)",  b"ATI\r\n",  115200)):
        try:
            s = serial.Serial(p, baud, timeout=2)
            s.reset_input_buffer()
            s.write(payload)
            time.sleep(1.2)
            resp = s.read(600)
            s.close()
            print(f"{p} @ {baud}  sent={payload!r}  recv={resp!r}")
        except Exception as e:
            print(f"{p} @ {baud}  sent={payload!r}  ERROR={e!r}")
PY

say "E. localhost listeners (any controller GUI/daemon?)"
{
  echo '$ ss -tlnp'
  ss -tlnp 2>&1
} > "$OUT/30-localhost-listeners.txt"
cat "$OUT/30-localhost-listeners.txt"

say "F. chamber-control software present on host?"
{
  echo '# filesystem names matching *chamber*/*thermotron*/*espec*/*watlow*/*environmental-chamber*'
  find / -xdev \( -iname '*chamber*' -o -iname '*thermotron*' -o -iname '*espec*' -o -iname '*watlow*' \) 2>/dev/null | grep -vE '/proc/|/sys/' | head -40
  echo "[none above => no chamber-control software/data found]"
  echo
  echo '# python modules that would drive a controller'
  python3 - <<'PY'
import importlib.util as u
for m in ('pymodbus','minimalmodbus','pyvisa','gpib','labjack','nidaqmx','smbus','labx'):
    print(f"{m}: {'present' if u.find_spec(m) else 'ABSENT'}")
PY
} > "$OUT/50-chamber-software.txt"
cat "$OUT/50-chamber-software.txt"

say "G. bounded LAN probe for typical controller ports (502=Modbus,111/102=SCPI/VXI,S7)"
if command -v nmap >/dev/null; then
  timeout 200 nmap -n -Pn -p 502,111,102,5000 -T4 --max-retries 1 --host-timeout 6s \
    192.168.2.0/24 10.177.21.0/24 > "$OUT/40-nmap-lan.txt" 2>&1
  grep -E 'Nmap scan report|/tcp|open' "$OUT/40-nmap-lan.txt" | head -40
  echo "[full -> $OUT/40-nmap-lan.txt]"
else
  echo "nmap unavailable" | tee "$OUT/40-nmap-lan.txt"
fi

say "done"
ls -la "$OUT"
