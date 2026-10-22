#!/bin/bash
# Fast bounded PDF sweep: first page only, 5s timeout, parallelised.
# Proves whether ANY pdf under ~ or /mnt contains a chamber/commissioning/ramp-rate term.
find /home/c03rad0r /mnt -xdev -type f -iname '*.pdf' 2>/dev/null \
  | grep -viE 'node_modules|/\.git/|site-packages|dist-packages|/snap/|\.gomod' > /tmp/pdflist.txt
echo "PDF count: $(wc -l < /tmp/pdflist.txt)"
scan() {
  f="$1"
  n=$(timeout 5 pdftotext -f 1 -l 1 "$f" - 2>/dev/null | grep -ciE 'commissioning|ramp rate|heating rate|cooling rate|thermal chamber|degC/min|°C/min')
  if [ -n "$n" ] && [ "$n" != "0" ]; then echo "HIT($n): $f"; fi
}
export -f scan
# -P 8 parallel; xargs feeds filenames
xargs -a /tmp/pdflist.txt -d '\n' -P 8 -I{} bash -c 'scan "$@"' _ {}
echo "PDF SWEEP DONE"
