#!/bin/bash
# secret-scan.sh — grep all POW repos for leaked credential patterns. Read-only.
REPOS="powops powpowpow powuk powstock repair powrobots powproducts powphysical powk aionboard aocsec"
PATTERNS="ghp_[A-Za-z0-9]{20,}|github_pat_|sk-live-[A-Za-z0-9]|sk_test|AKIA[A-Z0-9]{16}|xox[bap]-|AIza[A-Za-z0-9_-]{30,}"
FAIL=0
for r in $REPOS; do
  d="/home/ubuntu/$r"
  [ -d "$d/.git" ] || continue
  # committed history (last 50 commits) + tracked files
  hits=$(git -C "$d" grep -E -c "$PATTERNS" $(git -C "$d" rev-list --max-count=50 HEAD 2>/dev/null) -- 2>/dev/null | grep -v ":0$" | head -5)
  if [ -n "$hits" ]; then echo "[$r] HISTORY HITS:"; echo "$hits"; FAIL=1; fi
  # .env files accidentally tracked
  envtracked=$(git -C "$d" ls-files 2>/dev/null | grep -E "(^|/)\.env$" | head -5)
  if [ -n "$envtracked" ]; then echo "[$r] TRACKED ENV:"; echo "$envtracked"; FAIL=1; fi
done
[ $FAIL -eq 0 ] && echo "secret-scan: clean"
exit $FAIL
