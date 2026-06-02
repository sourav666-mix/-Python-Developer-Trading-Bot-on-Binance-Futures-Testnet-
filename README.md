# Binance Futures Testnet Trading Bot

A lightweight Python CLI application that places **MARKET**, **LIMIT**, and **STOP_MARKET** orders on the [Binance Futures Testnet (USDT-M)](https://testnet.binancefuture.com), with clean logging, structured error handling, and a reusable API client layer.

---

## Project Structure

```
trading_bot/
├── bot/
│   ├── __init__.py
│   ├── client.py          # Binance REST API wrapper (signing, HTTP, error handling)
│   ├── orders.py          # Order placement logic (MARKET, LIMIT, STOP_MARKET)
│   ├── validators.py      # Input validation (symbol, side, type, qty, price)
│   └── logging_config.py  # File + console logger setup
├── cli.py                 # CLI entry point (argparse)
├── logs/                  # Auto-created; log files stored here
├── requirements.txt
└── README.md
```

---

## Setup

### 1. Clone / download the project

```bash
git clone https://github.com/your-username/trading_bot.git
cd trading_bot
```

### 2. Create a virtual environment (recommended)

```bash
python -m venv venv
source venv/bin/activate      # Linux / macOS
venv\Scripts\activate         # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Register on Binance Futures Testnet

1. Go to [https://testnet.binancefuture.com](https://testnet.binancefuture.com)
2. Sign in / register with a GitHub account.
3. Navigate to **API Management** and create a new API key pair.

### 5. Set your API credentials as environment variables

```bash
# Linux / macOS
export BINANCE_API_KEY=your_testnet_api_key
export BINANCE_API_SECRET=your_testnet_api_secret

# Windows (Command Prompt)
set BINANCE_API_KEY=your_testnet_api_key
set BINANCE_API_SECRET=your_testnet_api_secret

# Windows (PowerShell)
$env:BINANCE_API_KEY="your_testnet_api_key"
$env:BINANCE_API_SECRET="your_testnet_api_secret"
```

> **Never hard-code credentials in source files.**

---

## How to Run

### Check server connectivity

```bash
python cli.py server-time
```

### View account balance

```bash
python cli.py account-info
```

### Place a MARKET order

```bash
# Buy 0.001 BTC at market price
python cli.py place-order --symbol BTCUSDT --side BUY --type MARKET --quantity 0.001

# Sell 0.001 BTC at market price
python cli.py place-order --symbol BTCUSDT --side SELL --type MARKET --quantity 0.001
```

### Place a LIMIT order

```bash
# Sell 0.001 BTC at $60,000 (resting limit order)
python cli.py place-order --symbol BTCUSDT --side SELL --type LIMIT --quantity 0.001 --price 60000

# Buy 0.001 BTC at $55,000 with IOC time-in-force
python cli.py place-order --symbol BTCUSDT --side BUY --type LIMIT --quantity 0.001 --price 55000 --time-in-force IOC
```

### Place a STOP_MARKET order *(Bonus)*

```bash
# Trigger a market SELL if price falls to $58,000
python cli.py place-order --symbol BTCUSDT --side SELL --type STOP_MARKET --quantity 0.001 --stop-price 58000
```

### Full CLI help

```bash
python cli.py --help
python cli.py place-order --help
```

---

## Example Output

```
────────────────────────────────────────────────────────────
  ORDER REQUEST SUMMARY
────────────────────────────────────────────────────────────
  Symbol                : BTCUSDT
  Side                  : BUY
  Order Type            : MARKET
  Quantity              : 0.001

────────────────────────────────────────────────────────────
  ORDER RESPONSE
────────────────────────────────────────────────────────────
  Order ID              : 4512309817
  Client Order ID       : web_abc123
  Status                : FILLED
  Executed Qty          : 0.001
  Avg Price             : 57823.40
  Limit Price           : N/A
  Stop Price            : N/A
  Time In Force         : GTC

  ✓  Order placed successfully!
```

---

## Logging

Logs are written to `logs/trading_bot_YYYYMMDD.log`.

- **File handler** — DEBUG level (full request/response details, signatures excluded).
- **Console handler** — INFO level (order summaries, results, errors).

Sample log files are included in `logs/`:
- `market_order_sample.log`
- `limit_order_sample.log`

---

## Assumptions

| Item | Decision |
|---|---|
| Credentials | Loaded from environment variables only (no `.env` file dependency) |
| Futures type | USDT-M perpetual futures only |
| Leverage | Not set by the bot; uses your account's current leverage setting |
| Quantity precision | Passed as-is; Binance rejects invalid precision — adjust per symbol |
| Time In Force | Default `GTC` for LIMIT orders; overridable via `--time-in-force` |
| Bonus order type | `STOP_MARKET` implemented as the third order type |

---

## Dependencies

| Package | Purpose |
|---|---|
| `requests` | HTTP calls to the Binance REST API |

No other third-party libraries are required.

---

## Error Handling

The bot handles the following failure cases cleanly:

- **Invalid input** — validation errors printed before any API call is made.
- **Binance API errors** — error code and message displayed (e.g. insufficient balance, invalid price).
- **Network failures** — `requests.exceptions.RequestException` caught and reported.
- **Unexpected errors** — logged with full traceback for debugging.
