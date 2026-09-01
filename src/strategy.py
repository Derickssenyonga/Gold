import numpy as np


def ema(values, period):
    if len(values) < period:
        return None
    kernel = 2 / (period + 1)
    ema_values = np.empty(len(values), dtype=float)
    ema_values[0] = float(values[0])
    for i in range(1, len(values)):
        ema_values[i] = (float(values[i]) - ema_values[i - 1]) * kernel + ema_values[i - 1]
    return ema_values


def rsi(values, period=14):
    if len(values) < period + 1:
        return None
    deltas = np.diff(values)
    gains = np.clip(deltas, 0, None)
    losses = np.clip(-deltas, 0, None)

    avg_gain = np.mean(gains[:period])
    avg_loss = np.mean(losses[:period])
    rsi_values = np.empty(len(values), dtype=float)
    rsi_values[:] = np.nan

    if avg_loss == 0:
        rsi_values[period] = 100.0
    else:
        rs = avg_gain / avg_loss
        rsi_values[period] = 100.0 - (100.0 / (1.0 + rs))

    for i in range(period + 1, len(values)):
        gain = np.mean(gains[i - period:i])
        loss = np.mean(losses[i - period:i])
        if loss == 0:
            rsi_values[i] = 100.0
        else:
            rs = gain / loss
            rsi_values[i] = 100.0 - (100.0 / (1.0 + rs))

    return rsi_values


def atr(values, period=14):
    if len(values) < period + 1:
        return 0.0

    values = np.asarray(values, dtype=float)
    true_ranges = []
    for i in range(1, len(values)):
        high = values[i]
        low = values[i - 1]
        prev_close = values[i - 1]
        tr = max(high - low, abs(high - prev_close), abs(low - prev_close))
        true_ranges.append(tr)

    if not true_ranges:
        return 0.0

    return float(np.mean(true_ranges[-period:]))


def generate_signal(prices, fast_ema=8, mid_ema=21, slow_ema=50, rsi_period=14, atr_period=14, trend_filter=0.0003):
    if len(prices) < max(fast_ema, mid_ema, slow_ema, rsi_period + 2):
        return "WAIT", None

    closes = np.asarray(prices, dtype=float)
    fast = ema(closes, fast_ema)
    mid = ema(closes, mid_ema)
    slow = ema(closes, slow_ema)
    rsi_values = rsi(closes, rsi_period)
    atr_value = atr(closes, atr_period)

    last_fast = float(fast[-1])
    last_mid = float(mid[-1])
    last_slow = float(slow[-1])
    prev_fast = float(fast[-2])
    prev_mid = float(mid[-2])
    prev_slow = float(slow[-2])
    last_rsi = float(rsi_values[-1])
    signal_strength = abs(last_fast - last_slow) / max(abs(last_slow) * 0.0001, 1e-6)

    meta = {
        "fast": last_fast,
        "mid": last_mid,
        "slow": last_slow,
        "rsi": last_rsi,
        "atr": float(atr_value),
        "strength": float(signal_strength),
        "trend": "bullish" if last_fast > last_mid > last_slow else "bearish",
    }

    bullish = (last_fast > last_mid > last_slow) and (prev_fast <= prev_mid <= prev_slow) and (last_rsi > 52) and (atr_value > 0) and (signal_strength > trend_filter)
    bearish = (last_fast < last_mid < last_slow) and (prev_fast >= prev_mid >= prev_slow) and (last_rsi < 48) and (atr_value > 0) and (signal_strength > trend_filter)

    if bullish:
        return "BUY", meta
    if bearish:
        return "SELL", meta
    return "WAIT", meta
