#!/bin/bash
set -u
# headers-check.sh — verify dashboard security headers. Read-only.
TOKEN=$(cat ~/.powops/dashboard_token)
echo "--- CSP ---"
curl -s -D - -o /dev/null "http://127.0.0.1:8796/style.css" | grep -i "^content-security-policy"
echo "--- auth ---"
echo -n "bad token: "; curl -s -o /dev/null -w "%{http_code}\n" "http://127.0.0.1:8796/api/status?token=wrong"
echo -n "no token: "; curl -s -o /dev/null -w "%{http_code}\n" "http://127.0.0.1:8796/api/status"
echo -n "bearer: "; curl -s -o /dev/null -w "%{http_code}\n" -H "Authorization: Bearer $TOKEN" "http://127.0.0.1:8796/api/health"
