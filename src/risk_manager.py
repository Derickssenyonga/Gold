def compute_lot_size(
    account_balance: float,
    risk_percent: float,
    entry_price: float,
    stop_price: float,
    point_value: float,
    lot_step: float = 0.01,
) -> float:
    """Compute a lot size based on a fixed risk percentage.

    The risk rule requested by the customer is to place the stop at the entry,
    so the loss is effectively the full risk budget on a single trade.
    """
    if account_balance <= 0 or risk_percent <= 0:
        return 0.0

    risk_amount = account_balance * (risk_percent / 100.0)
    distance_points = abs(entry_price - stop_price)
    if distance_points <= 0:
        return 0.0

    # Gold is often priced in USD per ounce, thus point_value is approximate.
    risk_per_lot = distance_points * point_value
    if risk_per_lot <= 0:
        return 0.0

    lot_size = risk_amount / risk_per_lot
    return max(0.0, round(lot_size / lot_step) * lot_step)


def position_stop_level(entry_price: float, direction: str) -> float:
    """This project follows the customer's requested rule: stop at entry price."""
    if direction.upper() not in {"BUY", "SELL"}:
        raise ValueError("direction must be BUY or SELL")
    return float(entry_price)
