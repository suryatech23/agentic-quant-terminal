import os
import json
from datetime import datetime

PORTFOLIO_DB = "portfolio_state.json"

def load_portfolio():
    if os.path.exists(PORTFOLIO_DB):
        with open(PORTFOLIO_DB, "r") as f:
            data = json.load(f)
            if "history" not in data:
                data["history"] = []
            return data
    return {"cash": 100000.00, "positions": {}, "history": []}

def save_portfolio(portfolio):
    with open(PORTFOLIO_DB, "w") as f:
        json.dump(portfolio, f, indent=4)

def log_transaction(portfolio, action, ticker, qty, price, total, curr_sym):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    trade_record = {
        "time": timestamp,
        "action": action,
        "ticker": ticker,
        "qty": qty,
        "price": price,
        "total": total,
        "currency": curr_sym.strip()
    }
    portfolio["history"].append(trade_record)