# Linux VPS deployment guide for the MT5 Gold Scalper

## 1. Choose a VPS

Use a Linux VPS with:

- Ubuntu 22.04 or Debian 12
- 2 GB RAM minimum
- stable internet access
- public IP address

## 2. Connect to the VPS

```bash
ssh root@YOUR_VPS_IP
```

## 3. Install basic packages

```bash
apt update && apt upgrade -y
apt install -y python3 python3-pip python3-venv git curl unzip
```

## 4. Clone or upload the project

```bash
mkdir -p /opt
cd /opt
git clone https://github.com/your-user/your-repo.git gold_mt5_scalper
```

If the project is already on the server, just copy it into `/opt/gold_mt5_scalper`.

## 5. Install Python dependencies

```bash
cd /opt/gold_mt5_scalper
python3 -m venv .venv
. .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

## 6. Configure the environment

Edit the `.env` file:

```bash
nano /opt/gold_mt5_scalper/.env
```

Set your correct MT5 account, server, path, and Telegram values.

Example:

```env
MT5_LOGIN=123456
MT5_PASSWORD=your_password
MT5_SERVER=Broker-Demo
MT5_PATH=/opt/mt5/terminal64.exe
ACCOUNT_BALANCE=1000.0
RISK_PERCENT=1.0
SYMBOL=XAUUSD
STOP_AT_ENTRY=true
FAST_EMA=8
MID_EMA=21
SLOW_EMA=50
RSI_PERIOD=14
ATR_PERIOD=14
TARGET_POINTS=20
MAX_HOLD_SECONDS=45
TELEGRAM_ENABLED=true
TELEGRAM_BOT_TOKEN=your_token
TELEGRAM_CHAT_ID=your_chat_id
```

## 7. Start the bot manually

```bash
cd /opt/gold_mt5_scalper
. .venv/bin/activate
python src/bot.py
```

## 8. Run as a service with systemd

Copy the provided service file or use the script:

```bash
cp deploy/gold_mt5_scalper.service /etc/systemd/system/
```

Then:

```bash
systemctl daemon-reload
systemctl enable gold_mt5_scalper.service
systemctl start gold_mt5_scalper.service
systemctl status gold_mt5_scalper.service
```

## 9. Check logs

```bash
journalctl -u gold_mt5_scalper.service -f
```

## 10. Security recommendations

- keep the VPS in a separate environment
- use a demo account first
- avoid exposing confidential login info in shared files
- use firewall rules if needed

## 11. Mobile access

From your Android phone on the same network or via public IP:

```text
http://YOUR_VPS_IP:5000/mobile
```

## 12. Telegram alerts

Make a Telegram bot with BotFather and get the chat ID. Then place both values in `.env`.

## 13. Production checklist

- test with demo MT5 account
- validate VPS connectivity
- verify Telegram alerts work
- confirm MT5 terminal path is correct
- confirm symbol XAUUSD is available

## 14. Important warning

This is a developer project for education and testing. Gold is very volatile and the stop-at-entry rule is aggressive. Always test realistically before trading live capital.
