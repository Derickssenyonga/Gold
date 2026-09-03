# Gold Scalper Bot for MT5

This project is a production-style gold scalper framework for MetaTrader 5. It includes a realistic scalp strategy, full MT5 trade management, Telegram alerts, Android monitoring, and Ubuntu VPS deployment support.

## Included features

- Realistic gold scalp entries using EMA trend alignment, RSI, and ATR confirmation
- MT5 order management for opening, closing, and trailing positions
- Risk rule with stop placed at the entry price as requested
- Android-friendly live dashboard
- Telegram alerts and command support
- VPS deployment for Ubuntu servers and broker-based trading setups

## Strategy summary

- Symbol: XAUUSD or XAUUSDMICRO
- Timeframe: M1 or M5
- Logic: fast EMA > mid EMA > slow EMA, RSI momentum filter, ATR confirmation
- Risk rule: stop at the entry
- Take profit: small fast target in points
- Extra control: max positions cap and trailing stop logic

## Android note

Android cannot run MetaTrader 5 directly in the same way as a desktop PC. The practical setup is:

1. Run the Python bot on a Windows PC or Linux VPS.
2. Expose the dashboard over HTTP.
3. Use Android as a remote monitor or control screen.

Browser dashboard:

```text
http://<server-ip>:5000/mobile
```

APK-ready Kivy app:

```text
android_app/
```

## Building Android APK

Three methods to build the APK:

### Method 1: Cloud-based (Recommended for Windows)

**Using GitHub Actions** (automatic):
1. Push your code to GitHub
2. GitHub Actions automatically builds the APK
3. Download from Actions artifacts

**Using Buildozer Cloud**:
1. Visit https://buildozer.cloud/
2. Upload your project
3. Select "Android Debug"
4. Download the APK

### Method 2: WSL2 on Windows (Recommended)

**Quick build**:
```bash
build_apk_wsl.bat
```

**Manual setup**:
```bash
wsl --install
wsl --install -d Ubuntu-22.04
# Then in WSL:
cd android_app
buildozer android debug
```

### Method 3: Full Android Studio on Windows

See [docs/android_apk_build_guide.md](docs/android_apk_build_guide.md) for complete setup instructions.

## Installing on Android Device

Once you have the APK:

1. Transfer `goldscalper-1.0-debug.apk` to your Android device
2. Enable Settings → Security → "Unknown sources"
3. Open file manager and tap the APK
4. Select "Install"
5. Launch the app from your home screen

## Quick start

### Windows MT5 PC

Install the 64-bit MetaTrader 5 desktop terminal, copy `.env.example` to `.env`, and enter the account details supplied by your broker. Then double-click [start_mt5_pc.bat](start_mt5_pc.bat), or run:

```powershell
.\start_mt5_pc.bat
```

The bot requires MT5 to be installed and logged into the correct demo account. Confirm `MT5_PATH`, `MT5_SERVER`, and `SYMBOL` match the values shown by your broker. Test on demo before enabling live trading.


1. Install Python 3.11+
2. Create a virtual environment and install dependencies:

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

3. Fill in the required values in `.env`
4. Start the bot:

```bash
python src/bot.py
```

5. Start the dashboard:

```bash
python src/mobile_dashboard.py
```

6. Start the full stack in one command:

```bash
python run_full_stack.py
```

7. Open on Android or browser:

```text
http://<your-host>:5000/mobile
http://<your-host>:5050/
```

The admin panel at port 5050 gives you a quick status view, recent logs, and start/stop controls.

## Telegram setup

Set in `.env`:

```env
TELEGRAM_ENABLED=true
TELEGRAM_BOT_TOKEN=your_token_here
TELEGRAM_CHAT_ID=your_chat_id_here
TELEGRAM_WEBHOOK_URL=https://your-domain.com/telegram/webhook
```

Commands supported:

- /status
- /stats
- /start
- /stop
- /help

## Production deployment

Use the deployment guides:

- [docs/linux_vps_deployment_guide.md](docs/linux_vps_deployment_guide.md)
- [docs/production_deployment_guide.md](docs/production_deployment_guide.md)
- [deploy/ubuntu_vps_one_click.sh](deploy/ubuntu_vps_one_click.sh)

One-click Ubuntu deployment:

```bash
bash deploy/ubuntu_vps_one_click.sh
```

## File structure

- [src/bot.py](src/bot.py) — main trading loop
- [src/strategy.py](src/strategy.py) — gold scalp strategy
- [src/risk_manager.py](src/risk_manager.py) — risk and lot sizing
- [src/mt5_connector.py](src/mt5_connector.py) — MT5 order management
- [src/telegram_alerts.py](src/telegram_alerts.py) — Telegram alerts
- [src/telegram_bot_controller.py](src/telegram_bot_controller.py) — Telegram webhook/config controller
- [src/mobile_dashboard.py](src/mobile_dashboard.py) — live dashboard for Android/browser
- [android_app/main.py](android_app/main.py) — APK-ready UI
- [android_app/buildozer.spec](android_app/buildozer.spec) — Android packaging config
- [deploy/ubuntu_vps_one_click.sh](deploy/ubuntu_vps_one_click.sh) — Ubuntu deployment helper
- [tests/test_risk_manager.py](tests/test_risk_manager.py) — risk checks
- [tests/test_strategy.py](tests/test_strategy.py) — strategy validation

## Warning

This is an educational trading project and can lose money. Use it on demo accounts first. Gold and micro-gold are highly volatile, and the stop-at-entry rule is aggressive.
