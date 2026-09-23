#!/bin/bash
# token-rotate.sh — rotate powops dashboard token + restart dashboard. WRITES.
set -eu
python3 -c "import secrets; print(secrets.token_urlsafe(24))" > ~/.powops/dashboard_token
chmod 600 ~/.powops/dashboard_token
systemctl --user restart powops-dashboard.service
sleep 2
systemctl --user is-active powops-dashboard.service
echo "rotated. new prefix: $(head -c 6 ~/.powops/dashboard_token)..."
