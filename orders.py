"""
Order placement logic for the Trading Bot.

Wraps the BinanceClient with order-specific business logic,
response formatting, and structured logging.
"""

from __future__ import annotations

from typing import Any

from bot.client import BinanceClient, BinanceClientError
from bot.logging_config import setup_logger
from bot.validators import (
    validate_order_type,
    validate_price,
    validate_quantity,
    validate_side,
    validate_stop_price,
    validate_symbol,
)

logger = setup_logger(__name__)


def _format_order_response(order: dict) -> dict:
    """Extract the most relevant fields from a raw Binance order response."""
    return {
        "orderId": order.get("orderId"),
        "clientOrderId": order.get("clientOrderId"),
        "symbol": order.get("symbol"),
        "side": order.get("side"),
        "type": order.get("type"),
        "origQty": order.get("origQty"),
        "executedQty": order.get("executedQty"),
        "avgPrice": order.get("avgPrice"),
        "price": order.get("price"),
        "stopPrice": order.get("stopPrice"),
        "status": order.get("status"),
        "timeInForce": order.get("timeInForce"),
        "updateTime": order.get("updateTime"),
    }


def place_market_order(
    client: BinanceClient,
    symbol: str,
    side: str,
    quantity: float,
) -> dict[str, Any]:
    """
    Place a MARKET order on Binance Futures Testnet.

    Args:
        client: Authenticated BinanceClient instance.
        symbol: Trading pair symbol (e.g. BTCUSDT).
        side: BUY or SELL.
        quantity: Order quantity.

    Returns:
        Formatted order response dict.
    """
    symbol = validate_symbol(symbol)
    side = validate_side(side)
    quantity = validate_quantity(quantity)

    logger.info(
        "Placing MARKET order | symbol=%s side=%s qty=%s",
        symbol,
        side,
        quantity,
    )

    try:
        raw = client.place_order(
            symbol=symbol,
            side=side,
            type="MARKET",
            quantity=quantity,
        )
    except BinanceClientError as exc:
        logger.error("API error placing MARKET order: %s", exc)
        raise
    except Exception as exc:
        logger.error("Unexpected error placing MARKET order: %s", exc)
        raise

    result = _format_order_response(raw)
    logger.info("MARKET order placed successfully | orderId=%s status=%s", result["orderId"], result["status"])
    return result


def place_limit_order(
    client: BinanceClient,
    symbol: str,
    side: str,
    quantity: float,
    price: float,
    time_in_force: str = "GTC",
) -> dict[str, Any]:
    """
    Place a LIMIT order on Binance Futures Testnet.

    Args:
        client: Authenticated BinanceClient instance.
        symbol: Trading pair symbol (e.g. BTCUSDT).
        side: BUY or SELL.
        quantity: Order quantity.
        price: Limit price.
        time_in_force: GTC (default), IOC, or FOK.

    Returns:
        Formatted order response dict.
    """
    symbol = validate_symbol(symbol)
    side = validate_side(side)
    quantity = validate_quantity(quantity)
    price = validate_price(price, "LIMIT")

    logger.info(
        "Placing LIMIT order | symbol=%s side=%s qty=%s price=%s tif=%s",
        symbol,
        side,
        quantity,
        price,
        time_in_force,
    )

    try:
        raw = client.place_order(
            symbol=symbol,
            side=side,
            type="LIMIT",
            quantity=quantity,
            price=price,
            timeInForce=time_in_force,
        )
    except BinanceClientError as exc:
        logger.error("API error placing LIMIT order: %s", exc)
        raise
    except Exception as exc:
        logger.error("Unexpected error placing LIMIT order: %s", exc)
        raise

    result = _format_order_response(raw)
    logger.info("LIMIT order placed successfully | orderId=%s status=%s", result["orderId"], result["status"])
    return result


def place_stop_market_order(
    client: BinanceClient,
    symbol: str,
    side: str,
    quantity: float,
    stop_price: float,
) -> dict[str, Any]:
    """
    Place a STOP_MARKET order on Binance Futures Testnet (Bonus).

    Triggers a market order when the price reaches `stop_price`.

    Args:
        client: Authenticated BinanceClient instance.
        symbol: Trading pair symbol.
        side: BUY or SELL.
        quantity: Order quantity.
        stop_price: Trigger price.

    Returns:
        Formatted order response dict.
    """
    symbol = validate_symbol(symbol)
    side = validate_side(side)
    quantity = validate_quantity(quantity)
    stop_price = validate_stop_price(stop_price, "STOP_MARKET")

    logger.info(
        "Placing STOP_MARKET order | symbol=%s side=%s qty=%s stopPrice=%s",
        symbol,
        side,
        quantity,
        stop_price,
    )

    try:
        raw = client.place_order(
            symbol=symbol,
            side=side,
            type="STOP_MARKET",
            quantity=quantity,
            stopPrice=stop_price,
        )
    except BinanceClientError as exc:
        logger.error("API error placing STOP_MARKET order: %s", exc)
        raise
    except Exception as exc:
        logger.error("Unexpected error placing STOP_MARKET order: %s", exc)
        raise

    result = _format_order_response(raw)
    logger.info(
        "STOP_MARKET order placed successfully | orderId=%s status=%s",
        result["orderId"],
        result["status"],
    )
    return result
