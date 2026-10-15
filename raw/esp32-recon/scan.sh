#!/usr/bin/env bash
# READ-ONLY recon scanner + mechanical triage for the esp32-* repo family.
# Only reads git objects / files. Writes TSV into the recon worktree.
# usage: bash scan.sh <outdir>
set -u
OUTDIR="${1:?outdir}"
mkdir -p "$OUTDIR"
RAW="$OUTDIR/raw-hits.tsv"
CAN="$OUTDIR/candidates.tsv"
NAMEKEEP="$OUTDIR/filename-keeps.tsv"
: > "$RAW"; : > "$CAN"; : > "$NAMEKEEP"

emit () { # repo rev path line text
  printf '%s\t%s\t%s:%s\t%s\n' "$1" "$2" "$3" "$4" "$5" >> "$RAW"
}

scan_git () { # label dir rev...
  local label="$1" dir="$2"; shift 2
  local rev
  for rev in "$@"; do
    git -C "$dir" grep -niE 'shadow.?card|human.?gate|board|gate' "$rev" -- '*.md' '*.txt' '*.rst' 2>/dev/null \
    | while IFS= read -r ln; do
        # git grep output: <rev>:<path>:<lineno>:<text>
        local rest="${ln#*:}"           # <path>:<lineno>:<text>
        local p="${rest%%:*}"
        local rest2="${rest#*:}"
        local n="${rest2%%:*}"
        local t="${rest2#*:}"
        emit "$label" "$rev" "$p" "$n" "$t"
      done
  done
}

# ---- git roots ----
scan_git esp32-mesh /home/c03rad0r/esp32-mesh \
  feature/redeem-ecash master \
  feature/ecash-redemption feature/ecash-redemption-backup feature/ecash-redemption-before-merge \
  feature/introduce-captive-portal pretty-captive-portal individual-authentication \
  internet-passthrough-works mutex-worked with-delay captive-portal-opens-in-browser \
  config-json-refactor v0.1.0

scan_git esp32-tollgate /home/c03rad0r/repos/tollgate-esp32 \
  master remotes/origin/master remotes/upstream/master \
  remotes/origin/balloon-pow-e-hash remotes/origin/balloon-pow-extraction \
  remotes/origin/balloon-tollgate-c3-port v1.4.0 v-balloon-pre-strip \
  archive/cvm-integration archive/display-fix archive/local-relay \
  archive/miner-integration archive/mining-payment \
  archive/multi-mint-support-pre-rebase archive/tollgate-core-component \
  archive/tollgate-core-v2

scan_git wisp-esp32 /home/c03rad0r/wisp-esp32 \
  main fork/balloon-nostr-extraction remotes/origin/main remotes/origin/feature/subscription-manager

# ---- non-git plain-grep roots ----
scan_plain () { # label path
  local label="$1" path="$2"
  [ -d "$path" ] || { printf 'MISSING\t%s\t%s\n' "$label" "$path" >> "$RAW"; return; }
  grep -rniE 'shadow.?card|human.?gate|board|gate' "$path" \
    --include='*.md' --include='*.txt' --include='*.rst' 2>/dev/null \
  | while IFS= read -r ln; do
      local p="${ln%%:*}"
      local rest="${ln#*:}"
      local n="${rest%%:*}"
      local t="${rest#*:}"
      emit "$label" "WORKTREE-ASIS" "$p" "$n" "$t"
    done
}
scan_plain esp32-tollgate-relay            /home/c03rad0r/esp32-tollgate-relay
scan_plain esp32-repeater-captive-portal   /home/c03rad0r/esp32-mesh/esp32-repeater-captive-portal
scan_plain esp32-balloon-integration-meshcore-pr /home/c03rad0r/esp32-balloon-integration-meshcore-pr
scan_plain ailaptop-migration-esp32-tollgate /home/c03rad0r/repos/ailaptop-migration/esp32-tollgate
scan_plain ailaptop-migration-esp32-mesh     /home/c03rad0r/repos/ailaptop-migration/esp32-mesh
scan_plain ailaptop-migration-esp32_balloon   /home/c03rad0r/repos/ailaptop-migration/esp32_balloon_integration

# ---- step 4: filename-based keeps (regardless of regex) ----
for spec in "esp32-mesh|/home/c03rad0r/esp32-mesh" \
            "esp32-tollgate|/home/c03rad0r/repos/tollgate-esp32" \
            "wisp-esp32|/home/c03rad0r/wisp-esp32"; do
  label="${spec%%|*}"; dir="${spec#*|}"
  if [ -e "$dir/.git" ]; then
    for rev in $(git -C "$dir" for-each-ref --format='%(refname:short)' refs/heads refs/tags refs/remotes 2>/dev/null); do
      git -C "$dir" ls-tree -r --name-only "$rev" 2>/dev/null \
      | grep -iE 'design-review-notes|(^|/)ADR[-_/]|decision|rfc' \
      | sed "s|^|$label\t$rev\t|" >> "$NAMEKEEP"
    done
  fi
done
for spec in "esp32-tollgate-relay|/home/c03rad0r/esp32-tollgate-relay" \
            "esp32-repeater-captive-portal|/home/c03rad0r/esp32-mesh/esp32-repeater-captive-portal" \
            "esp32-balloon-integration-meshcore-pr|/home/c03rad0r/esp32-balloon-integration-meshcore-pr" \
            "ailaptop-migration-esp32-tollgate|/home/c03rad0r/repos/ailaptop-migration/esp32-tollgate" \
            "ailaptop-migration-esp32-mesh|/home/c03rad0r/repos/ailaptop-migration/esp32-mesh" \
            "ailaptop-migration-esp32_balloon|/home/c03rad0r/repos/ailaptop-migration/esp32_balloon_integration"; do
  label="${spec%%|*}"; dir="${spec#*|}"
  find "$dir" -type f \( -name '*.md' -o -name '*.txt' -o -name '*.rst' \) 2>/dev/null \
  | grep -iE 'design-review-notes|(^|/)ADR[-_/]|decision|rfc' \
  | sed "s|^|$label\tWORKTREE-ASIS\t|" >> "$NAMEKEEP"
done

echo "RAW=$(wc -l < "$RAW")"
echo "NAMEKEEP=$(sort -u "$NAMEKEEP" | wc -l)"
echo "RAWBYREPO:"
awk -F'\t' '{print $1"\t"$2}' "$RAW" | sort | uniq -c | sort -k2
