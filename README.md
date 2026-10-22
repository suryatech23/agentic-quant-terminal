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
    ```

## Student Add-on: Demo, Architecture, and Notes

### Demo idea
This project is a good demo for a student portfolio because it combines Python, APIs, finance, and AI. A simple demo flow could be:

1. Start the terminal app.
2. Load market data for a few symbols.
3. View the real-time dashboard.
4. Ask the AI assistant for a simple market summary.
5. Submit a simulated buy or sell decision.
6. Check the portfolio ledger and transaction log.

### Architecture summary
```text
+------------------+      +--------------------+      +-------------------+
| Market Data API  | ---> | data_pipeline.py   | ---> | main.py           |
+------------------+      +--------------------+      +-------------------+
                                  |                            |
                                  v                            v
                        +--------------------+      +-------------------+
                        | Technical Analysis|      | AI / LLM Layer    |
                        +--------------------+      +-------------------+
                                  |                            |
                                  v                            v
                        +--------------------+      +-------------------+
                        | ledger.py          |      | ui.py             |
                        +--------------------+      +-------------------+
```

### What this project teaches
- Python project structure
- API integration with live data sources
- Technical indicators and trend detection
- State handling with JSON storage
- Portfolio simulation and risk checks
- Basic AI prompt-to-action workflow

### Student notes
This is a very practical project and a nice example of how a student can connect a trading idea with actual coding work. It is not production-grade finance software, but it is a strong beginner-to-intermediate project that shows system design thinking, data handling, and automation.

### Possible next improvements
- Add a real database instead of JSON files
- Add paper trading history charts
- Add more technical indicators
- Add testing for portfolio logic
- Add better logging and deployment scripts
