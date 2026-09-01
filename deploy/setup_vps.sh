#!/usr/bin/env bash
set -e

PROJECT_DIR="/opt/gold_mt5_scalper"
REPO_DIR="${PROJECT_DIR}"
USER="root"

mkdir -p "$PROJECT_DIR"
cd "$PROJECT_DIR"

python3 -m venv .venv
. .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

cat > /etc/systemd/system/gold_mt5_scalper.service <<EOF
[Unit]
Description=Gold MT5 Scalper Bot
After=network.target

[Service]
Type=simple
WorkingDirectory=${REPO_DIR}
ExecStart=${REPO_DIR}/.venv/bin/python ${REPO_DIR}/src/bot.py
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

printf "\nVPS setup complete. Check status with: systemctl status gold_mt5_scalper.service\n"
