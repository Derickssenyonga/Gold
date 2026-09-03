import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()


@dataclass
class BotConfig:
    mt5_login: int = int(os.getenv("MT5_LOGIN", "0"))
    mt5_password: str = os.getenv("MT5_PASSWORD", "")
    mt5_server: str = os.getenv("MT5_SERVER", "")
    mt5_path: str = os.getenv("MT5_PATH", "")
    account_balance: float = float(os.getenv("ACCOUNT_BALANCE", "1000.0"))
    risk_percent: float = float(os.getenv("RISK_PERCENT", "1.0"))
    symbol: str = os.getenv("SYMBOL", "XAUUSD")
    alt_symbol: str = os.getenv("ALT_SYMBOL", "XAUUSDMICRO")
    broker_mode: str = os.getenv("BROKER_MODE", "mt5")
    strategy_mode: str = os.getenv("STRATEGY_MODE", "momentum").lower()
    stop_at_entry: bool = os.getenv("STOP_AT_ENTRY", "true").lower() == "true"
    fast_ema: int = int(os.getenv("FAST_EMA", "8"))
    mid_ema: int = int(os.getenv("MID_EMA", "21"))
    slow_ema: int = int(os.getenv("SLOW_EMA", "50"))
    rsi_period: int = int(os.getenv("RSI_PERIOD", "14"))
    atr_period: int = int(os.getenv("ATR_PERIOD", "14"))
    target_points: int = int(os.getenv("TARGET_POINTS", "20"))
    initial_stop_points: int = int(os.getenv("INITIAL_STOP_POINTS", "100"))
    breakeven_trigger_points: int = int(os.getenv("BREAKEVEN_TRIGGER_POINTS", "50"))
    max_hold_seconds: int = int(os.getenv("MAX_HOLD_SECONDS", "45"))
    lot_step: float = 0.01
    point_value: float = 100.0
    mobile_port: int = 5000
    telegram_bot_token: str = os.getenv("TELEGRAM_BOT_TOKEN", "")
    telegram_chat_id: str = os.getenv("TELEGRAM_CHAT_ID", "")
    telegram_enabled: bool = os.getenv("TELEGRAM_ENABLED", "false").lower() == "true"
    vps_user: str = os.getenv("VPS_USER", "root")
    vps_host: str = os.getenv("VPS_HOST", "")
    derive_bridge: bool = os.getenv("DERIVE_BRIDGE", "false").lower() == "true"


CONFIG = BotConfig()
