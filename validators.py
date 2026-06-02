"""
Input validation helpers for the Trading Bot CLI.
All validation raises ValueError with a descriptive message on failure.
"""

from __future__ import annotations

VALID_SIDES = {"BUY", "SELL"}
VALID_ORDER_TYPES = {"MARKET", "LIMIT", "STOP_MARKET"}


def validate_symbol(symbol: str) -> str:
    """Normalise and validate a trading symbol (e.g. BTCUSDT)."""
    symbol = symbol.strip().upper()
    if not symbol.isalnum():
        raise ValueError(
            f"Invalid symbol '{symbol}'. Must contain only letters and numbers (e.g. BTCUSDT)."
        )
    if len(symbol) < 3:
        raise ValueError(f"Symbol '{symbol}' is too short.")
    return symbol


def validate_side(side: str) -> str:
    """Validate order side (BUY or SELL)."""
    side = side.strip().upper()
    if side not in VALID_SIDES:
        raise ValueError(
            f"Invalid side '{side}'. Must be one of: {', '.join(sorted(VALID_SIDES))}."
        )
    return side


def validate_order_type(order_type: str) -> str:
    """Validate order type (MARKET, LIMIT, STOP_MARKET)."""
    order_type = order_type.strip().upper()
    if order_type not in VALID_ORDER_TYPES:
        raise ValueError(
            f"Invalid order type '{order_type}'. Must be one of: {', '.join(sorted(VALID_ORDER_TYPES))}."
        )
    return order_type


def validate_quantity(quantity: str | float) -> float:
    """Validate order quantity (must be a positive number)."""
    try:
        qty = float(quantity)
    except (TypeError, ValueError):
        raise ValueError(f"Invalid quantity '{quantity}'. Must be a positive number.")
    if qty <= 0:
        raise ValueError(f"Quantity must be greater than zero, got {qty}.")
    return qty


def validate_price(price: str | float | None, order_type: str) -> float | None:
    """
    Validate order price.

    - LIMIT and STOP_MARKET orders require a price > 0.
    - MARKET orders ignore price (returns None).
    """
    order_type = order_type.strip().upper()
    if order_type == "MARKET":
        return None  # price not needed

    if price is None or str(price).strip() == "":
        raise ValueError(f"Price is required for {order_type} orders.")
    try:
        p = float(price)
    except (TypeError, ValueError):
        raise ValueError(f"Invalid price '{price}'. Must be a positive number.")
    if p <= 0:
        raise ValueError(f"Price must be greater than zero, got {p}.")
    return p


def validate_stop_price(stop_price: str | float | None, order_type: str) -> float | None:
    """Validate stop price (required for STOP_MARKET orders)."""
    if order_type.upper() != "STOP_MARKET":
        return None
    if stop_price is None or str(stop_price).strip() == "":
        raise ValueError("Stop price is required for STOP_MARKET orders.")
    try:
        sp = float(stop_price)
    except (TypeError, ValueError):
        raise ValueError(f"Invalid stop price '{stop_price}'. Must be a positive number.")
    if sp <= 0:
        raise ValueError(f"Stop price must be greater than zero, got {sp}.")
    return sp
