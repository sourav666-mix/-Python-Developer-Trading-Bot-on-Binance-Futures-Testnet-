"""
Binance Futures Testnet REST API client.

Handles request signing, HTTP communication, and raw API responses.
All API calls are logged at DEBUG level.
"""

from __future__ import annotations

import hashlib
import hmac
import time
from typing import Any
from urllib.parse import urlencode

import requests

from bot.logging_config import setup_logger

BASE_URL = "https://testnet.binancefuture.com"

logger = setup_logger(__name__)


class BinanceClientError(Exception):
    """Raised when the Binance API returns an error response."""

    def __init__(self, code: int, message: str) -> None:
        self.code = code
        self.message = message
        super().__init__(f"Binance API error {code}: {message}")


class BinanceClient:
    """
    Lightweight wrapper around the Binance Futures Testnet REST API.

    Args:
        api_key: Testnet API key.
        api_secret: Testnet API secret.
        base_url: Base URL (defaults to testnet).
        timeout: HTTP request timeout in seconds.
    """

    def __init__(
        self,
        api_key: str,
        api_secret: str,
        base_url: str = BASE_URL,
        timeout: int = 10,
    ) -> None:
        if not api_key or not api_secret:
            raise ValueError("api_key and api_secret must not be empty.")
        self.api_key = api_key
        self.api_secret = api_secret.encode()
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update(
            {
                "X-MBX-APIKEY": self.api_key,
                "Content-Type": "application/x-www-form-urlencoded",
            }
        )
        logger.debug("BinanceClient initialised (base_url=%s)", self.base_url)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _sign(self, params: dict) -> dict:
        """Append HMAC-SHA256 signature to a params dict."""
        params["timestamp"] = int(time.time() * 1000)
        query_string = urlencode(params)
        signature = hmac.new(
            self.api_secret, query_string.encode(), hashlib.sha256
        ).hexdigest()
        params["signature"] = signature
        return params

    def _handle_response(self, response: requests.Response) -> Any:
        """Parse the response and raise BinanceClientError on API errors."""
        logger.debug(
            "HTTP %s %s → status=%s body=%s",
            response.request.method,
            response.url,
            response.status_code,
            response.text[:500],
        )
        try:
            data = response.json()
        except ValueError:
            response.raise_for_status()
            return response.text

        if isinstance(data, dict) and "code" in data and data["code"] != 200:
            raise BinanceClientError(data["code"], data.get("msg", "Unknown error"))

        response.raise_for_status()
        return data

    # ------------------------------------------------------------------
    # Public API methods
    # ------------------------------------------------------------------

    def get_server_time(self) -> dict:
        """Check connectivity and retrieve server time."""
        url = f"{self.base_url}/fapi/v1/time"
        logger.debug("GET %s", url)
        resp = self.session.get(url, timeout=self.timeout)
        return self._handle_response(resp)

    def get_exchange_info(self, symbol: str | None = None) -> dict:
        """Retrieve exchange info (optionally filtered by symbol)."""
        url = f"{self.base_url}/fapi/v1/exchangeInfo"
        params = {}
        if symbol:
            params["symbol"] = symbol.upper()
        logger.debug("GET %s params=%s", url, params)
        resp = self.session.get(url, params=params, timeout=self.timeout)
        return self._handle_response(resp)

    def get_account_info(self) -> dict:
        """Retrieve futures account balance and position info."""
        url = f"{self.base_url}/fapi/v2/account"
        params = self._sign({})
        logger.debug("GET %s (signed)", url)
        resp = self.session.get(url, params=params, timeout=self.timeout)
        return self._handle_response(resp)

    def place_order(self, **kwargs) -> dict:
        """
        Place a new order on Binance Futures Testnet.

        All keyword arguments are forwarded directly to the
        POST /fapi/v1/order endpoint after signing.

        Common kwargs:
            symbol, side, type, quantity, price, timeInForce,
            stopPrice, reduceOnly, newClientOrderId
        """
        url = f"{self.base_url}/fapi/v1/order"
        params = self._sign(dict(**kwargs))
        logger.debug("POST %s params=%s", url, {k: v for k, v in params.items() if k != "signature"})
        resp = self.session.post(url, data=params, timeout=self.timeout)
        return self._handle_response(resp)

    def get_order(self, symbol: str, order_id: int) -> dict:
        """Query an existing order by orderId."""
        url = f"{self.base_url}/fapi/v1/order"
        params = self._sign({"symbol": symbol.upper(), "orderId": order_id})
        logger.debug("GET %s orderId=%s", url, order_id)
        resp = self.session.get(url, params=params, timeout=self.timeout)
        return self._handle_response(resp)

    def cancel_order(self, symbol: str, order_id: int) -> dict:
        """Cancel an open order by orderId."""
        url = f"{self.base_url}/fapi/v1/order"
        params = self._sign({"symbol": symbol.upper(), "orderId": order_id})
        logger.debug("DELETE %s orderId=%s", url, order_id)
        resp = self.session.delete(url, params=params, timeout=self.timeout)
        return self._handle_response(resp)
