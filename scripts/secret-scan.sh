#!/bin/bash
# secret-scan.sh — grep all POW repos for leaked credential patterns. Read-only.
set -u
REPOS="powops powpowpow powuk powstock repair powrobots powproducts powphysical powk aionboard aocsec"
PATTERNS="ghp_[A-Za-z0-9]{20,}|github_pat_|sk-live-[A-Za-z0-9]|sk_test|AKIA[A-Z0-9]{16}|xox[bap]-|AIza[A-Za-z0-9_-]{30,}"
# Files that legitimately contain pattern strings (scanners, docs about formats)
ALLOWLIST="secret-scan.sh"
FAIL=0
for r in $REPOS; do
  d="/home/ubuntu/$r"
  [ -d "$d/.git" ] || continue
  revs=$(git -C "$d" rev-list --max-count=50 HEAD 2>/dev/null) || continue
  [ -n "$revs" ] || continue
  allow=$(grep -v "^#" "$(dirname "$0")/allowlist.txt" 2>/dev/null | awk -F'[#:]' -v repo="$r" '$1==repo {gsub(/ /, "", $2); print $2}')
  # shellcheck disable=SC2086
  hits=$(git -C "$d" grep -E -c "$PATTERNS" $revs -- 2>/dev/null | grep -v ":0$" | grep -v "$ALLOWLIST" | head -20)
  if [ -n "$allow" ]; then
    while IFS= read -r af; do
      [ -n "$af" ] || continue
      hits=$(printf "%s\n" "$hits" | grep -v ":$af:" || true)
    done <<< "$allow"
    hits=$(printf "%s\n" "$hits" | head -5)
  fi
  if [ -n "$hits" ]; then echo "[$r] HISTORY HITS:"; echo "$hits"; FAIL=1; fi
  envtracked=$(git -C "$d" ls-files 2>/dev/null | grep -E "(^|/)\.env$" | head -5)
  if [ -n "$envtracked" ]; then echo "[$r] TRACKED ENV:"; echo "$envtracked"; FAIL=1; fi
done
[ $FAIL -eq 0 ] && echo "secret-scan: clean"
exit $FAIL
