#!/bin/bash
# kill-switch.sh — stop all local agent/MCP processes immediately. Read-only
# except process termination. Use when an agent misbehaves, a credential
# leaks mid-run, or red-team finds a live breach.
#
# What it does NOT do: revoke tokens, close tunnels, notify anyone.
# Those are manual follow-ups listed at the end.
set -u

echo "=== killing local MCP/agent processes ==="
for pat in "powops.mcp" "legislation.mcp_server" "powstock.mcp" "mcp_server.py" "agents/sessions"; do
  pids=$(pgrep -f "$pat" 2>/dev/null || true)
  if [ -n "$pids" ]; then
    echo "killing [$pat]: $pids"
    # shellcheck disable=SC2086
    kill $pids 2>/dev/null || true
  fi
done

sleep 2
echo "=== survivors ==="
remaining=$(pgrep -af "mcp_server\.py|powops\.mcp|powstock\.mcp|legislation\.mcp" 2>/dev/null || true)
if [ -n "$remaining" ]; then
  echo "$remaining"
  echo "STILL RUNNING — escalate (kill -9 PIDs above)"
else
  echo "none. all MCP processes stopped."
fi

echo
echo "=== manual follow-ups (not automated) ==="
echo "1. Revoke any exposed tokens (dashboard, OAuth, API keys)."
echo "2. systemctl --user stop powops-dashboard (if dashboard involved)."
echo "3. Cloudflare: pause tunnel if external exposure suspected."
echo "4. Write findings/YYYY-MM-DD-killswitch.md with cause + output above."
