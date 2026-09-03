import os

try:
    import MetaTrader5 as mt5
except Exception:  # pragma: no cover
    mt5 = None


class MT5Connector:
    def __init__(self, login, password, server, path):
        self.login = login
        self.password = password
        self.server = server
        self.path = path
        self.connected = False

    def connect(self):
        if mt5 is None:
            raise RuntimeError("MetaTrader5 package is not installed.")

        if not os.path.exists(self.path):
            raise FileNotFoundError(f"MT5 terminal not found at: {self.path}")

        has_credentials = self.login > 0 and self.password and self.server and "your_" not in self.server.lower()
        initialize_args = {"path": self.path}
        if has_credentials:
            initialize_args.update({
                "login": self.login,
                "password": self.password,
                "server": self.server,
            })

        if not mt5.initialize(**initialize_args):
            error = mt5.last_error()
            raise RuntimeError(f"MT5 initialize failed: {error}")

        self.connected = True
        return True

    def disconnect(self):
        if mt5 is not None and self.connected:
            mt5.shutdown()
            self.connected = False

    def get_account_info(self):
        if mt5 is None:
            raise RuntimeError("MetaTrader5 package is not installed.")
        return mt5.account_info()

    def get_symbol_info(self, symbol):
        if mt5 is None:
            raise RuntimeError("MetaTrader5 package is not installed.")
        return mt5.symbol_info(symbol)

    def get_positions(self):
        if mt5 is None:
            raise RuntimeError("MetaTrader5 package is not installed.")
        return mt5.positions_get()

    def get_orders(self):
        if mt5 is None:
            raise RuntimeError("MetaTrader5 package is not installed.")
        return mt5.orders_get()

    def get_rates(self, symbol, timeframe, count=100):
        if mt5 is None:
            raise RuntimeError("MetaTrader5 package is not installed.")
        return mt5.copy_rates_from_pos(symbol, timeframe, 0, count)

    def send_order(self, symbol, order_type, volume, price, stop_loss=None, take_profit=None, comment=""):
        if mt5 is None:
            raise RuntimeError("MetaTrader5 package is not installed.")

        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": symbol,
            "volume": float(volume),
            "type": order_type,
            "price": float(price),
            "sl": float(stop_loss) if stop_loss is not None else 0.0,
            "tp": float(take_profit) if take_profit is not None else 0.0,
            "comment": comment,
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }
        return mt5.order_send(request)

    def market_buy(self, symbol, volume, price, stop_loss=None, take_profit=None, comment="gold_scalper_buy"):
        return self.send_order(symbol, mt5.ORDER_TYPE_BUY, volume, price, stop_loss, take_profit, comment)

    def market_sell(self, symbol, volume, price, stop_loss=None, take_profit=None, comment="gold_scalper_sell"):
        return self.send_order(symbol, mt5.ORDER_TYPE_SELL, volume, price, stop_loss, take_profit, comment)

    def close_position_by_ticket(self, ticket, comment="close_position"):
        if mt5 is None:
            raise RuntimeError("MetaTrader5 package is not installed.")
        pos = mt5.positions_get(ticket=ticket)
        if pos is None or len(pos) == 0:
            return None
        position = pos[0]
        order_type = mt5.ORDER_TYPE_SELL if position.type == mt5.ORDER_TYPE_BUY else mt5.ORDER_TYPE_BUY
        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": position.symbol,
            "volume": float(position.volume),
            "type": order_type,
            "position": int(position.ticket),
            "price": position.price_current,
            "comment": comment,
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }
        return mt5.order_send(request)

    def close_all_positions(self, symbol=None):
        if mt5 is None:
            raise RuntimeError("MetaTrader5 package is not installed.")
        positions = self.get_positions() or []
        results = []
        for pos in positions:
            if symbol and pos.symbol != symbol:
                continue
            results.append(self.close_position_by_ticket(pos.ticket))
        return results

    def modify_position_stop(self, ticket, stop_loss):
        if mt5 is None:
            raise RuntimeError("MetaTrader5 package is not installed.")
        pos = mt5.positions_get(ticket=ticket)
        if pos is None or len(pos) == 0:
            return None
        take_profit = float(getattr(pos[0], "tp", 0.0))
        request = {
            "action": mt5.TRADE_ACTION_SLTP,
            "position": int(ticket),
            "sl": float(stop_loss),
            "tp": take_profit,
        }
        return mt5.order_send(request)

    def move_stop_to_entry(self, ticket):
        if mt5 is None:
            raise RuntimeError("MetaTrader5 package is not installed.")
        pos = mt5.positions_get(ticket=ticket)
        if pos is None or len(pos) == 0:
            return None
        return self.modify_position_stop(ticket, pos[0].price_open)

    def trailing_stop(self, ticket, distance_points):
        pos = mt5.positions_get(ticket=ticket)
        if pos is None or len(pos) == 0:
            return None
        position = pos[0]
        current_price = position.price_current
        if position.type == mt5.ORDER_TYPE_BUY:
            new_sl = current_price - distance_points
        else:
            new_sl = current_price + distance_points
        return self.modify_position_stop(ticket, new_sl)
