#!/usr/bin/env bash
# Deploy scubaaaa-api to the NanoPi R5C via scp + SSH.
# Usage: ./deploy.sh [--restart]
set -euo pipefail

# Load credentials from nano.env
if [[ -f nano.env ]]; then
  source nano.env
fi

HOST="${HOST:-192.168.2.1}"
USER="${USER:-root}"
PASS="${PASS:-password}"
REMOTE_DIR="/opt/scubaaaa-api"
RESTART=${1:-""}

SCP="sshpass -p $PASS scp -r -o StrictHostKeyChecking=no"
SSH="sshpass -p $PASS ssh -o StrictHostKeyChecking=no $USER@$HOST"

echo "==> Syncing code to $USER@$HOST:$REMOTE_DIR ..."
$SSH "mkdir -p $REMOTE_DIR"

# Copy project files (exclude git, cache, venv, secrets)
for item in app requirements.txt; do
  sshpass -p "$PASS" scp -r -o StrictHostKeyChecking=no \
    "$item" "$USER@$HOST:$REMOTE_DIR/"
done

echo "==> Installing dependencies on NanoPi ..."
$SSH bash <<ENDSSH
  cd $REMOTE_DIR
  pip3 install -q --break-system-packages --upgrade pip
  pip3 install -q --break-system-packages -r requirements.txt
ENDSSH

echo "==> Installing procd init.d service ..."
sshpass -p "$PASS" scp -o StrictHostKeyChecking=no \
  init.d/scubaaaa-api "$USER@$HOST:/etc/init.d/scubaaaa-api"
$SSH chmod +x /etc/init.d/scubaaaa-api
$SSH /etc/init.d/scubaaaa-api enable

if [[ "$RESTART" == "--restart" ]]; then
  echo "==> Restarting service on NanoPi ..."
  $SSH /etc/init.d/scubaaaa-api restart
  echo "==> API running on http://$HOST:8000"
  echo "    Logs: $SSH logread -e uvicorn"
else
  echo "==> Sync done. Run with --restart to also start/restart the service."
fi
