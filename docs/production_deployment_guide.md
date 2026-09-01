# Production deployment guide for the MT5 gold scalper

## 1. Requirements

- Ubuntu 22.04 or Debian 12 VPS
- Python 3.11 or newer
- MT5 terminal installed on the server or a remote MT5 bridge
- broker account with XAUUSD or XAUUSDMICRO access
- Telegram bot token and chat ID

## 2. Install system packages

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3 python3-pip python3-venv git curl ufw
```

## 3. Create project directory

```bash
sudo mkdir -p /opt/gold_mt5_scalper
cd /opt/gold_mt5_scalper
```

Upload or clone the project into this folder.

## 4. Install dependencies

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

## 5. Configure the environment

Edit `.env`:

```bash
nano /opt/gold_mt5_scalper/.env
```

Example values:

```env
MT5_LOGIN=123456
MT5_PASSWORD=your_mt5_password
MT5_SERVER=Broker-Demo
MT5_PATH=/opt/mt5/terminal64.exe
ACCOUNT_BALANCE=1000.0
RISK_PERCENT=1.0
SYMBOL=XAUUSD
ALT_SYMBOL=XAUUSDMICRO
BROKER_MODE=mt5
STOP_AT_ENTRY=true
FAST_EMA=8
MID_EMA=21
SLOW_EMA=50
RSI_PERIOD=14
ATR_PERIOD=14
TARGET_POINTS=20
MAX_HOLD_SECONDS=45
TELEGRAM_ENABLED=true
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_CHAT_ID=your_chat_id_here
TELEGRAM_WEBHOOK_URL=https://your-vps-domain.com/telegram/webhook
DERIVE_BRIDGE=false
VPS_USER=root
VPS_HOST=your_server_ip
```

## 6. Start the bot manually

```bash
cd /opt/gold_mt5_scalper
. .venv/bin/activate
python src/bot.py
```

## 7. Start the dashboard

```bash
cd /opt/gold_mt5_scalper
. .venv/bin/activate
python src/mobile_dashboard.py
```

Open from browser:

```text
http://YOUR_VPS_IP:5000/mobile
```

## 8. Start the Telegram bot controller

```bash
cd /opt/gold_mt5_scalper
. .venv/bin/activate
python src/telegram_bot_controller.py
```

This exposes the webhook endpoint at:

```text
http://YOUR_VPS_IP:5001/telegram/webhook
```

Then register the webhook:

```text
http://YOUR_VPS_IP:5001/telegram/setWebhook
```

## 9. Create the systemd service

Create this file:

```bash
sudo nano /etc/systemd/system/gold_mt5_scalper.service
```

Contents:

```ini
[Unit]
Description=Gold MT5 Scalper Bot
After=network.target

[Service]
Type=simple
WorkingDirectory=/opt/gold_mt5_scalper
ExecStart=/opt/gold_mt5_scalper/.venv/bin/python /opt/gold_mt5_scalper/src/bot.py
Restart=always
RestartSec=5
User=root
Environment=PYTHONUNBUFFERED=1

[Install]
WantedBy=multi-user.target
```

Then:

```bash
sudo systemctl daemon-reload
sudo systemctl enable gold_mt5_scalper.service
sudo systemctl start gold_mt5_scalper.service
sudo systemctl status gold_mt5_scalper.service
```

## 10. View logs

```bash
journalctl -u gold_mt5_scalper.service -f
```

## 11. Firewall

```bash
sudo ufw allow 22/tcp
sudo ufw allow 5000/tcp
sudo ufw allow 5001/tcp
sudo ufw enable
```

## 12. Broker-specific notes for Derive / XAUUSDMICRO

- Use the broker symbol exactly as offered by MT5
- If your broker exposes XAUUSDMICRO, set:

```env
SYMBOL=XAUUSD
ALT_SYMBOL=XAUUSDMICRO
BROKER_MODE=mt5
DERIVE_BRIDGE=false
```

- If your broker uses a Derive bridge layer, keep the bridge flag enabled and feed the route through the broker’s custom MT5 gateway
- Always validate symbol names in the MT5 Market Watch before starting the bot

## 13. Safety warning

This setup is for learning and testing. Gold and micro-gold are volatile. Do not run live capital until you validate the configuration on demo accounts and confirm execution, stops, and alerts work correctly.
