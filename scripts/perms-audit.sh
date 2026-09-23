#!/bin/bash
set -u
# perms-audit.sh — check secret file permissions. Read-only.
check() { # path maxperm
  if [ -e "$1" ]; then
    perm=$(stat -c %a "$1")
    if [ "$perm" -le "$2" ]; then echo "OK   $1 ($perm)"; else echo "FAIL $1 ($perm, want <=$2)"; fi
  else echo "SKIP $1 (absent)"; fi
}
check ~/.powops/dashboard_token 600
for f in /home/ubuntu/powuk/.env /home/ubuntu/powstock/.env /home/ubuntu/repair/.env; do check "$f" 600; done
echo "--- git remotes with embedded credentials ---"
found=0
for d in /home/ubuntu/*/; do
  [ -d "$d/.git" ] || continue
  if git -C "$d" remote -v 2>/dev/null | grep -qE "://[^/]*:[^/]*@"; then echo "FAIL $(basename $d): credentials in remote"; found=1; fi
done
[ $found -eq 0 ] && echo "OK   no embedded credentials in remotes"
echo "--- systemd units with embedded secrets ---"
units_hit=0
for u in ~/.config/systemd/user/*.service; do
  [ -e "$u" ] || continue
  if grep -Eq "^(Environment|ExecStart)=.*(TOKEN|KEY|SECRET|PASSWORD)=" "$u" 2>/dev/null; then
    echo "FAIL $(basename $u): secret in unit file (move to 600 EnvironmentFile)"
    units_hit=1
  fi
done
[ $units_hit -eq 0 ] && echo "OK   no secrets in systemd units"
[ $units_hit -ne 0 ] && exit 1
exit 0
echo "--- ssh keys ---"
ls -la ~/.ssh/authorized_keys 2>/dev/null || echo "SKIP no authorized_keys"
