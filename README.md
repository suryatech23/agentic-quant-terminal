# Agentic Quantitative Trading Terminal

A modular, autonomous quantitative trading terminal built in Python. This system integrates real-time global market data, advanced technical momentum indicators, stateful portfolio management, and a Local/Cloud Large Language Model (LLM) for autonomous trade execution and strategy analysis.

## System Architecture

The codebase is structured using strict separation of concerns to maintain scalability and deterministic execution alongside non-deterministic AI routing:

* **`main.py`**: The central controller engine and AI routing interface.
* **`data_pipeline.py`**: Handles asynchronous API calls, multi-currency localization, historical backtesting, and complex Pandas dataframe telemetry (SMA, RSI, MACD).
* **`ledger.py`**: Manages persistent JSON-based state, simulated capital tracking, and immutable transaction logging.
* **`ui.py`**: Renders the localized Rich terminal dashboard and candlestick charting.

## Core Features

* **Real-Time Telemetry & Multi-Asset Tracking**: Fetches live ticker data globally, dynamically mapping native currency symbols and formatting price action.
* **Technical Analysis Engine**: Calculates 5-Day SMA, 14-Day RSI, and MACD (12, 26) to determine market momentum and overbought/oversold conditions.
* **Agentic Execution Loop**: Utilizes an OSS AI model (via Groq/OpenAI endpoints) to parse terminal commands, answer analytical queries, and generate strict JSON payloads for autonomous trading.
* **Stateful Brokerage Simulation**: Tracks a $100,000 simulated portfolio, validating capital requirements and inventory before executing deterministic buy/sell orders.
* **Historical Backtesting Engine**: Programmatically simulates 1-year trading strategies against historical market data to benchmark algorithmic returns against a standard Buy & Hold baseline.

## Quick Start

1. Clone the repository and navigate to the project directory.
2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt