import json
import os
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from flask import Flask, jsonify, request

from telegram_alerts import TelegramAlerts

app = Flask(__name__)

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")
WEBHOOK_URL = os.getenv("TELEGRAM_WEBHOOK_URL", "")
ENABLED = os.getenv("TELEGRAM_ENABLED", "false").lower() == "true"

alerts = TelegramAlerts(bot_token=BOT_TOKEN, chat_id=CHAT_ID, enabled=ENABLED)


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "telegram_enabled": ENABLED})


@app.route("/telegram/webhook", methods=["POST"])
def telegram_webhook():
    try:
        payload = request.get_json(force=True, silent=True) or {}
        message = payload.get("message", {})
        text = (message.get("text") or "").strip()
        chat = message.get("chat", {})
        chat_id = chat.get("id")

        if not text:
            return jsonify({"ok": True})

        if chat_id and str(chat_id) != str(CHAT_ID):
            return jsonify({"ok": True})

        if text in {"/help", "/status", "/stats", "/start", "/stop", "/commands"}:
            status_payload = {
                "symbol": "XAUUSD",
                "status": "running",
                "last_signal": "WAIT",
                "account_balance": 0.0,
                "floating_pnl": 0.0,
                "positions_count": 0,
            }
            alerts.handle_command(text, status_payload)

        return jsonify({"ok": True})
    except Exception:
        return jsonify({"ok": False})


@app.route("/telegram/setWebhook", methods=["GET"])
def set_webhook_route():
    if not BOT_TOKEN or not WEBHOOK_URL:
        return jsonify({"ok": False, "error": "Missing TELEGRAM_BOT_TOKEN or TELEGRAM_WEBHOOK_URL"})

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/setWebhook"
    data = urlencode({"url": WEBHOOK_URL})
    request_obj = Request(url, data=data.encode("utf-8"), method="POST")
    try:
        with urlopen(request_obj, timeout=15) as resp:
            body = json.loads(resp.read().decode("utf-8"))
        return jsonify(body)
    except Exception as exc:
        return jsonify({"ok": False, "error": str(exc)})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=False)
