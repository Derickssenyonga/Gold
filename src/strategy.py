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


def generate_signal(prices, fast_ema=8, mid_ema=21, slow_ema=50, rsi_period=14, atr_period=14, trend_filter=0.0003, mode="trend", highs=None, lows=None, opens=None, spread_points=0.0, max_spread_points=50.0, stop_points=100.0, target_points=200.0, minimum_strength=7.0, minimum_risk_reward=1.5):
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
    if highs is None:
        highs = closes
    if lows is None:
        lows = closes
    if opens is None:
        opens = closes
    highs = np.asarray(highs, dtype=float)
    lows = np.asarray(lows, dtype=float)
    opens = np.asarray(opens, dtype=float)
    if len(highs) != len(closes) or len(lows) != len(closes) or len(opens) != len(closes):
        return "WAIT", None
    signal_strength = min(10.0, abs(last_fast - last_slow) / max(atr_value, 1e-6) * 3.0)
    lookback = min(20, len(closes) - 1)
    prior_high = float(np.max(highs[-lookback - 1:-1]))
    prior_low = float(np.min(lows[-lookback - 1:-1]))
    bullish_sweep = float(lows[-1]) < prior_low and closes[-1] > prior_low
    bearish_sweep = float(highs[-1]) > prior_high and closes[-1] < prior_high
    bullish_candle = closes[-1] > opens[-1]
    bearish_candle = closes[-1] < opens[-1]
    mean_reversion_buy = closes[-1] < last_mid and last_rsi <= 35
    mean_reversion_sell = closes[-1] > last_mid and last_rsi >= 65

    meta = {
        "fast": last_fast,
        "mid": last_mid,
        "slow": last_slow,
        "rsi": last_rsi,
        "atr": float(atr_value),
        "strength": float(signal_strength),
        "spread_points": float(spread_points),
        "risk_reward": float(target_points / max(stop_points, 1e-6)),
        "trend": "bullish" if last_fast > last_mid > last_slow else "bearish",
        "bullish_sweep": bool(bullish_sweep),
        "bearish_sweep": bool(bearish_sweep),
        "mean_reversion": "buy" if mean_reversion_buy else "sell" if mean_reversion_sell else "none",
    }

    bullish = (last_fast > last_mid > last_slow) and (prev_fast <= prev_mid <= prev_slow) and (last_rsi > 52) and (atr_value > 0) and (signal_strength > trend_filter)
    bearish = (last_fast < last_mid < last_slow) and (prev_fast >= prev_mid >= prev_slow) and (last_rsi < 48) and (atr_value > 0) and (signal_strength > trend_filter)

    mode = (mode or "trend").lower()
    acceptable_spread = spread_points <= max_spread_points
    acceptable_risk_reward = target_points / max(stop_points, 1e-6) >= minimum_risk_reward
    bullish_momentum = (
        last_fast > last_mid > last_slow
        and closes[-1] > last_slow
        and closes[-1] > closes[-2]
        and 45 <= last_rsi <= 65
        and bullish_candle
        and not bearish_sweep
        and atr_value > 0
        and signal_strength >= minimum_strength
        and acceptable_spread
        and acceptable_risk_reward
    )
    bearish_momentum = (
        last_fast < last_mid < last_slow
        and closes[-1] < last_slow
        and closes[-1] < closes[-2]
        and 35 <= last_rsi <= 55
        and bearish_candle
        and not bullish_sweep
        and atr_value > 0
        and signal_strength >= minimum_strength
        and acceptable_spread
        and acceptable_risk_reward
    )
    if mode in {"momentum", "trend_continuation", "trend-continuation"}:
        bullish = bullish_momentum
        bearish = bearish_momentum
    if mode in {"mean_reversion", "hybrid"}:
        bullish = mean_reversion_buy and bullish_sweep and atr_value > 0
        bearish = mean_reversion_sell and bearish_sweep and atr_value > 0

    if bullish:
        return "BUY", meta
    if bearish:
        return "SELL", meta
    return "WAIT", meta
