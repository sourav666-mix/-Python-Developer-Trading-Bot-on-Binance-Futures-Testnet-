"""
CLI entry point for the Binance Futures Testnet Trading Bot.

Usage examples:
    python cli.py place-order --symbol BTCUSDT --side BUY --type MARKET --quantity 0.001
    python cli.py place-order --symbol BTCUSDT --side SELL --type LIMIT --quantity 0.001 --price 60000
    python cli.py place-order --symbol BTCUSDT --side SELL --type STOP_MARKET --quantity 0.001 --stop-price 58000
    python cli.py account-info
    python cli.py server-time
"""

from __future__ import annotations

import argparse
import json
import os
import sys

from bot.client import BinanceClient, BinanceClientError
from bot.logging_config import setup_logger
from bot.orders import place_limit_order, place_market_order, place_stop_market_order
from bot.validators import (
    validate_order_type,
    validate_price,
    validate_quantity,
    validate_side,
    validate_stop_price,
    validate_symbol,
)

logger = setup_logger(__name__)

# ──────────────────────────────────────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────────────────────────────────────

SEPARATOR = "─" * 60


def _print_section(title: str) -> None:
    print(f"\n{SEPARATOR}")
    print(f"  {title}")
    print(SEPARATOR)


def _print_kv(label: str, value: object) -> None:
    print(f"  {label:<22}: {value}")


def _get_client() -> BinanceClient:
    """Build a BinanceClient from environment variables."""
    api_key = os.getenv("BINANCE_API_KEY", "").strip()
    api_secret = os.getenv("BINANCE_API_SECRET", "").strip()

    if not api_key or not api_secret:
        print(
            "\n[ERROR] BINANCE_API_KEY and BINANCE_API_SECRET environment variables must be set.\n"
            "  Export them before running:\n"
            "    export BINANCE_API_KEY=your_key\n"
            "    export BINANCE_API_SECRET=your_secret\n"
        )
        sys.exit(1)

    return BinanceClient(api_key=api_key, api_secret=api_secret)


# ──────────────────────────────────────────────────────────────────────────────
# Sub-command handlers
# ──────────────────────────────────────────────────────────────────────────────

def cmd_place_order(args: argparse.Namespace) -> None:
    """Validate inputs, place the order, and print the result."""
    # ── Validate ──────────────────────────────────────────────────────────────
    try:
        symbol = validate_symbol(args.symbol)
        side = validate_side(args.side)
        order_type = validate_order_type(args.type)
        quantity = validate_quantity(args.quantity)
        price = validate_price(args.price, order_type)
        stop_price = validate_stop_price(args.stop_price, order_type)
    except ValueError as exc:
        print(f"\n[VALIDATION ERROR] {exc}\n")
        logger.warning("Validation failed: %s", exc)
        sys.exit(1)

    # ── Print request summary ─────────────────────────────────────────────────
    _print_section("ORDER REQUEST SUMMARY")
    _print_kv("Symbol", symbol)
    _print_kv("Side", side)
    _print_kv("Order Type", order_type)
    _print_kv("Quantity", quantity)
    if price is not None:
        _print_kv("Price", price)
    if stop_price is not None:
        _print_kv("Stop Price", stop_price)

    # ── Place order ───────────────────────────────────────────────────────────
    client = _get_client()

    try:
        if order_type == "MARKET":
            result = place_market_order(client, symbol, side, quantity)
        elif order_type == "LIMIT":
            result = place_limit_order(client, symbol, side, quantity, price, args.time_in_force)
        elif order_type == "STOP_MARKET":
            result = place_stop_market_order(client, symbol, side, quantity, stop_price)
        else:
            print(f"\n[ERROR] Unsupported order type: {order_type}\n")
            sys.exit(1)

    except BinanceClientError as exc:
        _print_section("ORDER FAILED")
        _print_kv("Error Code", exc.code)
        _print_kv("Message", exc.message)
        print(f"\n  ✗  Order could not be placed.\n")
        sys.exit(1)

    except requests_exception() as exc:
        _print_section("NETWORK ERROR")
        print(f"  {exc}\n")
        sys.exit(1)

    except Exception as exc:
        _print_section("UNEXPECTED ERROR")
        print(f"  {exc}\n")
        logger.exception("Unexpected error during order placement")
        sys.exit(1)

    # ── Print response ────────────────────────────────────────────────────────
    _print_section("ORDER RESPONSE")
    _print_kv("Order ID", result.get("orderId"))
    _print_kv("Client Order ID", result.get("clientOrderId"))
    _print_kv("Status", result.get("status"))
    _print_kv("Executed Qty", result.get("executedQty"))
    _print_kv("Avg Price", result.get("avgPrice") or "N/A")
    _print_kv("Limit Price", result.get("price") or "N/A")
    _print_kv("Stop Price", result.get("stopPrice") or "N/A")
    _print_kv("Time In Force", result.get("timeInForce") or "N/A")

    print(f"\n  ✓  Order placed successfully!\n")
    logger.info("Order placement complete | orderId=%s", result.get("orderId"))


def cmd_account_info(args: argparse.Namespace) -> None:
    """Print futures account balance summary."""
    client = _get_client()
    try:
        info = client.get_account_info()
    except BinanceClientError as exc:
        print(f"\n[API ERROR] {exc}\n")
        sys.exit(1)

    _print_section("ACCOUNT INFO")
    _print_kv("Total Wallet Balance", info.get("totalWalletBalance"))
    _print_kv("Available Balance", info.get("availableBalance"))
    _print_kv("Total Unrealised PnL", info.get("totalUnrealizedProfit"))
    _print_kv("Total Margin Balance", info.get("totalMarginBalance"))
    print()


def cmd_server_time(args: argparse.Namespace) -> None:
    """Print Binance server time (connectivity check)."""
    client = _get_client()
    try:
        data = client.get_server_time()
    except Exception as exc:
        print(f"\n[ERROR] {exc}\n")
        sys.exit(1)

    _print_section("SERVER TIME")
    _print_kv("Server Time (ms)", data.get("serverTime"))
    print()


# ──────────────────────────────────────────────────────────────────────────────
# Requests exception helper (imported lazily to keep top-level clean)
# ──────────────────────────────────────────────────────────────────────────────

def requests_exception():
    import requests
    return requests.exceptions.RequestException


# ──────────────────────────────────────────────────────────────────────────────
# Argument parser
# ──────────────────────────────────────────────────────────────────────────────

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="trading_bot",
        description="Binance Futures Testnet Trading Bot",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  Place a MARKET BUY order:
    python cli.py place-order --symbol BTCUSDT --side BUY --type MARKET --quantity 0.001

  Place a LIMIT SELL order:
    python cli.py place-order --symbol BTCUSDT --side SELL --type LIMIT --quantity 0.001 --price 60000

  Place a STOP_MARKET SELL order (bonus):
    python cli.py place-order --symbol BTCUSDT --side SELL --type STOP_MARKET --quantity 0.001 --stop-price 58000

  Check account balance:
    python cli.py account-info

  Check server connectivity:
    python cli.py server-time
        """,
    )

    sub = parser.add_subparsers(dest="command", metavar="COMMAND")
    sub.required = True

    # ── place-order ───────────────────────────────────────────────────────────
    po = sub.add_parser("place-order", help="Place a new futures order")
    po.add_argument("--symbol", required=True, help="Trading symbol, e.g. BTCUSDT")
    po.add_argument(
        "--side",
        required=True,
        choices=["BUY", "SELL"],
        type=str.upper,
        help="Order side: BUY or SELL",
    )
    po.add_argument(
        "--type",
        required=True,
        dest="type",
        choices=["MARKET", "LIMIT", "STOP_MARKET"],
        type=str.upper,
        help="Order type: MARKET | LIMIT | STOP_MARKET",
    )
    po.add_argument("--quantity", required=True, type=float, help="Order quantity (e.g. 0.001)")
    po.add_argument("--price", type=float, default=None, help="Limit price (required for LIMIT orders)")
    po.add_argument("--stop-price", dest="stop_price", type=float, default=None,
                    help="Stop trigger price (required for STOP_MARKET orders)")
    po.add_argument(
        "--time-in-force",
        dest="time_in_force",
        default="GTC",
        choices=["GTC", "IOC", "FOK"],
        help="Time in force for LIMIT orders (default: GTC)",
    )
    po.set_defaults(func=cmd_place_order)

    # ── account-info ──────────────────────────────────────────────────────────
    ai = sub.add_parser("account-info", help="Show futures account balance")
    ai.set_defaults(func=cmd_account_info)

    # ── server-time ───────────────────────────────────────────────────────────
    st = sub.add_parser("server-time", help="Check server connectivity and time")
    st.set_defaults(func=cmd_server_time)

    return parser


# ──────────────────────────────────────────────────────────────────────────────
# Main
# ──────────────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
