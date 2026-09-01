import os
from urllib.request import Request, urlopen
from urllib.parse import urlencode


class TelegramAlerts:
    def __init__(self, bot_token=None, chat_id=None, enabled=False):
        self.bot_token = bot_token or os.getenv("TELEGRAM_BOT_TOKEN", "")
        self.chat_id = chat_id or os.getenv("TELEGRAM_CHAT_ID", "")
        self.enabled = enabled or os.getenv("TELEGRAM_ENABLED", "false").lower() == "true"

    def send(self, message: str):
        if not self.enabled or not self.bot_token or not self.chat_id:
            return False

        url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
        payload = urlencode({"chat_id": self.chat_id, "text": message, "parse_mode": "HTML"})
        request = Request(url, data=payload.encode("utf-8"), method="POST")
        try:
            with urlopen(request, timeout=10) as response:
                response.read()
            return True
        except Exception:
            return False

    def market_summary(self, symbol, signal, price, lot_size, action="open"):
        if signal == "BUY":
            return self.send(f"<b>BUY ORDER</b>\nSymbol: {symbol}\nPrice: {price}\nLot: {lot_size}\nAction: {action}")
        if signal == "SELL":
            return self.send(f"<b>SELL ORDER</b>\nSymbol: {symbol}\nPrice: {price}\nLot: {lot_size}\nAction: {action}")
        return self.send(f"<b>{signal}</b>\nSymbol: {symbol}\nPrice: {price}\nLot: {lot_size}\nAction: {action}")

    def buy_alert(self, symbol, price, lot_size):
        return self.market_summary(symbol, "BUY", price, lot_size, "entry")

    def sell_alert(self, symbol, price, lot_size):
        return self.market_summary(symbol, "SELL", price, lot_size, "entry")

    def stop_alert(self, symbol, price, reason="stop_at_entry"):
        return self.send(f"<b>STOP EVENT</b>\nSymbol: {symbol}\nPrice: {price}\nReason: {reason}")

    def closed_trade(self, symbol, side, pnl, price):
        return self.send(f"<b>TRADE CLOSED</b>\nSymbol: {symbol}\nSide: {side}\nP/L: {pnl}\nExit: {price}")

    def status_summary(self, status_data):
        symbol = status_data.get("symbol", "XAUUSD")
        signal = status_data.get("last_signal", "WAIT")
        status = status_data.get("status", "running")
        account = status_data.get("account_balance", 0)
        pnl = status_data.get("floating_pnl", 0)
        positions = status_data.get("positions_count", 0)
        return self.send(
            f"<b>BOT STATUS</b>\n"
            f"Status: {status}\n"
            f"Symbol: {symbol}\n"
            f"Signal: {signal}\n"
            f"Account: {account}\n"
            f"Floating P/L: {pnl}\n"
            f"Open positions: {positions}"
        )

    def handle_command(self, text, status_data=None):
        command = (text or "").strip().lower()
        if command in {"/status", "/stats"}:
            if status_data is None:
                return self.send("<b>BOT STATUS</b>\nStatus: running")
            return self.status_summary(status_data)
        if command == "/stop":
            return self.send("<b>STOP REQUEST</b>\nBot has been flagged for stop request. Confirm with your operator controls.")
        if command == "/start":
            return self.send("<b>START REQUEST</b>\nBot start request recorded.")
        if command in {"/help", "/commands"}:
            return self.send("<b>Commands</b>\n/status\n/start\n/stop\n/help")
        return self.send(f"<b>Unknown command</b>\n{text}")
