import json
import time
from datetime import datetime

from config import CONFIG
from mt5_connector import MT5Connector
from risk_manager import compute_lot_size, position_stop_level
from strategy import generate_signal
from telegram_alerts import TelegramAlerts


class GoldScalperBot:
    def __init__(self):
        self.connector = MT5Connector(
            login=CONFIG.mt5_login,
            password=CONFIG.mt5_password,
            server=CONFIG.mt5_server,
            path=CONFIG.mt5_path,
        )
        self.last_signal = "WAIT"
        self.position_opened = False
        self.max_positions = 2
        self.telegram = TelegramAlerts(
            bot_token=CONFIG.telegram_bot_token,
            chat_id=CONFIG.telegram_chat_id,
            enabled=CONFIG.telegram_enabled,
        )
        self.log_path = "gold_mt5_trade_log.jsonl"
        self.status_path = "bot_status.json"
        self.running = True
        self.last_snapshot = {}
        self.last_position_tickets = set()

    def initialize(self):
        self.connector.connect()
        self.log_event("startup", {"message": "MT5 connected", "symbol": CONFIG.symbol})
        print("MT5 connected")
        self.telegram.send("<b>Gold MT5 bot started</b> - monitoring XAUUSD")
        self.update_status_snapshot()

    def log_event(self, event_type, payload):
        item = {
            "timestamp": datetime.now().isoformat(),
            "event": event_type,
            "symbol": CONFIG.symbol,
            "payload": payload,
        }
        try:
            with open(self.log_path, "a", encoding="utf-8") as fh:
                fh.write(json.dumps(item) + "\n")
        except Exception:
            pass

    def update_status_snapshot(self):
        try:
            account = self.connector.get_account_info()
            account_balance = getattr(account, "balance", CONFIG.account_balance)
            floating_pnl = getattr(account, "floating_pl", 0.0)
        except Exception:
            account_balance = CONFIG.account_balance
            floating_pnl = 0.0

        positions = self.connector.get_positions() or []
        symbol_positions = [p for p in positions if p.symbol == CONFIG.symbol]
        summary = {
            "status": "running" if self.running else "stopped",
            "symbol": CONFIG.symbol,
            "last_signal": self.last_signal,
            "account_balance": float(account_balance),
            "floating_pnl": float(floating_pnl),
            "positions_count": len(symbol_positions),
            "open_positions": [
                {"ticket": int(p.ticket), "type": int(p.type), "profit": float(getattr(p, "profit", 0.0))} for p in symbol_positions
            ],
            "last_update": datetime.now().isoformat(),
        }
        self.last_snapshot = summary
        try:
            with open(self.status_path, "w", encoding="utf-8") as fh:
                json.dump(summary, fh)
        except Exception:
            pass
        return summary

    def process_telegram_command(self, command_text):
        command = (command_text or "").strip().lower()
        if command in {"/status", "/stats"}:
            self.telegram.status_summary(self.last_snapshot or self.update_status_snapshot())
            return "status"
        if command == "/stop":
            self.running = False
            self.telegram.send("<b>STOP REQUEST</b>\nBot marked as stopped.")
            self.update_status_snapshot()
            return "stopped"
        if command == "/start":
            self.running = True
            self.telegram.send("<b>START REQUEST</b>\nBot marked as running.")
            self.update_status_snapshot()
            return "running"
        if command in {"/help", "/commands"}:
            self.telegram.send("<b>Commands</b>\n/status\n/start\n/stop\n/help")
            return "help"
        return "unknown"

    def get_market_snapshot(self):
        rates = self.connector.get_rates(CONFIG.symbol, 1, count=250)
        closes = [float(r[4)] for r in rates]
        signal, meta = generate_signal(closes, CONFIG.fast_ema, CONFIG.mid_ema, CONFIG.slow_ema, CONFIG.rsi_period, CONFIG.atr_period)
        return signal, meta

    def manage_existing_positions(self):
        positions = self.connector.get_positions() or []
        if not positions:
            return

        for pos in positions:
            if pos.symbol != CONFIG.symbol:
                continue
            self.connector.trailing_stop(pos.ticket, 30)

    def detect_closed_positions(self):
        positions = self.connector.get_positions() or []
        current_tickets = {int(p.ticket) for p in positions if p.symbol == CONFIG.symbol}
        previous = self.last_position_tickets.copy()
        closed = previous - current_tickets
        for ticket in sorted(closed):
            self.telegram.closed_trade(CONFIG.symbol, "CLOSE", 0.0, 0.0)
            self.log_event("position_closed", {"ticket": ticket, "symbol": CONFIG.symbol})
        self.last_position_tickets = current_tickets

    def send_alert_for_event(self, event_type, price, lot_size=None):
        if event_type == "BUY":
            self.telegram.buy_alert(CONFIG.symbol, price, lot_size)
        elif event_type == "SELL":
            self.telegram.sell_alert(CONFIG.symbol, price, lot_size)
        elif event_type == "STOP":
            self.telegram.stop_alert(CONFIG.symbol, price, reason="stop_at_entry")

    def handle_signal(self, signal, meta):
        if signal == "WAIT" or not self.running:
            return

        positions = self.connector.get_positions() or []
        symbol_positions = [p for p in positions if p.symbol == CONFIG.symbol]
        if len(symbol_positions) >= self.max_positions:
            return

        now = datetime.now()
        price = self.connector.get_rates(CONFIG.symbol, 1, count=2)[-1][4]
        stop_level = position_stop_level(price, signal)
        lot_size = compute_lot_size(
            account_balance=CONFIG.account_balance,
            risk_percent=CONFIG.risk_percent,
            entry_price=price,
            stop_price=stop_level,
            point_value=CONFIG.point_value,
            lot_step=CONFIG.lot_step,
        )

        if lot_size <= 0:
            message = f"[{now}] Risk too low to trade: {lot_size}"
            print(message)
            self.log_event("risk_blocked", {"signal": signal, "price": price, "lot_size": lot_size})
            self.send_alert_for_event("STOP", price)
            return

        if signal == "BUY":
            result = self.connector.market_buy(
                CONFIG.symbol,
                lot_size,
                price,
                stop_loss=stop_level,
                take_profit=price + (CONFIG.target_points * 0.01),
                comment="gold_scalper_buy",
            )
            trade_summary = {
                "signal": "BUY",
                "price": price,
                "lot_size": lot_size,
                "stop": stop_level,
                "take_profit": price + (CONFIG.target_points * 0.01),
                "result": str(result),
            }
            print(f"[{now}] BUY order result: {result}")
            self.log_event("buy_order", trade_summary)
            self.send_alert_for_event("BUY", price, lot_size)
        elif signal == "SELL":
            result = self.connector.market_sell(
                CONFIG.symbol,
                lot_size,
                price,
                stop_loss=stop_level,
                take_profit=price - (CONFIG.target_points * 0.01),
                comment="gold_scalper_sell",
            )
            trade_summary = {
                "signal": "SELL",
                "price": price,
                "lot_size": lot_size,
                "stop": stop_level,
                "take_profit": price - (CONFIG.target_points * 0.01),
                "result": str(result),
            }
            print(f"[{now}] SELL order result: {result}")
            self.log_event("sell_order", trade_summary)
            self.send_alert_for_event("SELL", price, lot_size)

        self.position_opened = True
        self.last_signal = signal
        self.update_status_snapshot()

    def run(self):
        self.initialize()
        try:
            while True:
                if self.running:
                    signal, meta = self.get_market_snapshot()
                    self.manage_existing_positions()
                    self.detect_closed_positions()
                    self.handle_signal(signal, meta)
                self.update_status_snapshot()
                time.sleep(1)
        finally:
            self.connector.disconnect()


if __name__ == "__main__":
    bot = GoldScalperBot()
    bot.run()
