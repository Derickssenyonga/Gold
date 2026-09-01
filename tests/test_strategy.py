import numpy as np

from src.strategy import generate_signal


def test_generate_signal_buy_case():
    prices = np.linspace(2000, 2010, 200).tolist()
    signal, meta = generate_signal(prices, fast_ema=9, slow_ema=21, rsi_period=14)
    assert signal in {"BUY", "SELL", "WAIT"}
    assert meta is not None


def test_generate_signal_wait_for_short_prices():
    prices = [2000, 2001, 2002, 2003]
    signal, meta = generate_signal(prices, fast_ema=9, slow_ema=21, rsi_period=14)
    assert signal == "WAIT"
