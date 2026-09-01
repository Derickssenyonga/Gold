import pytest

from src.risk_manager import compute_lot_size, position_stop_level


def test_compute_lot_size_basic():
    lot = compute_lot_size(
        account_balance=1000.0,
        risk_percent=1.0,
        entry_price=2000.0,
        stop_price=1999.5,
        point_value=100.0,
        lot_step=0.01,
    )
    assert lot > 0
    assert lot >= 0.01


def test_position_stop_level_uses_entry_price():
    stop = position_stop_level(2000.0, "BUY")
    assert stop == 2000.0

    stop = position_stop_level(2000.0, "SELL")
    assert stop == 2000.0


def test_compute_lot_size_never_negative():
    lot = compute_lot_size(
        account_balance=1000.0,
        risk_percent=0.0,
        entry_price=2000.0,
        stop_price=2000.0,
        point_value=100.0,
        lot_step=0.01,
    )
    assert lot == 0.0
