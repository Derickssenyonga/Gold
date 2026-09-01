#!/usr/bin/env bash
set -e

PROJECT_DIR="/opt/gold_mt5_scalper"
USER="${USER:-root}"
PYTHON_BIN="${PYTHON_BIN:-python3}"

if [ "$EUID" -ne 0 ]; then
  echo "Please run as root or with sudo."
  exit 1
fi

apt-get update
apt-get install -y curl git python3 python3-venv python3-pip unzip

mkdir -p "$PROJECT_DIR"
cd "$PROJECT_DIR"

if [ -d "$PROJECT_DIR/.git" ]; then
  git pull
else
  echo "Please ensure the project files are already copied to $PROJECT_DIR"
  echo "This script expects the repository contents to be present before deployment."
  exit 1
fi

$PYTHON_BIN -m venv .venv
. .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

cat > /etc/systemd/system/gold_mt5_scalper.service <<EOF
[Unit]
Description=Gold MT5 Scalper Bot
After=network.target

[Service]
Type=simple
WorkingDirectory=${PROJECT_DIR}
ExecStart=${PROJECT_DIR}/.venv/bin/python ${PROJECT_DIR}/src/bot.py
Restart=always
RestartSec=5
User=${USER}
Environment=PYTHONUNBUFFERED=1

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable gold_mt5_scalper.service
systemctl start gold_mt5_scalper.service

cat > /etc/motd.d/gold_mt5_scalper <<EOF
Gold MT5 Scalper is running.
Check status with: systemctl status gold_mt5_scalper.service
Check logs with: journalctl -u gold_mt5_scalper.service -f
EOF

chmod 644 /etc/motd.d/gold_mt5_scalper

printf "\nUbuntu VPS deployment complete.\n"
printf "Status: systemctl status gold_mt5_scalper.service\n"
printf "Logs: journalctl -u gold_mt5_scalper.service -f\n"
