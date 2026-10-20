import yfinance as yf
import pandas as pd

def fetch_market_data(ticker_symbol):
    ticker = yf.Ticker(ticker_symbol)
    df = ticker.history(period="3mo")
    if df.empty: raise ValueError(f"No market data found for '{ticker_symbol}'.")

    currency_code = ticker.info.get('currency', 'USD')
    symbol_map = {'USD': '$', 'INR': '₹', 'EUR': '€', 'GBP': '£', 'JPY': '¥', 'CAD': 'C$'}
    curr_sym = symbol_map.get(currency_code, f"{currency_code} ")

    df['SMA_5'] = df['Close'].rolling(window=5).mean()
    
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))
    
    exp1 = df['Close'].ewm(span=12, adjust=False).mean()
    exp2 = df['Close'].ewm(span=26, adjust=False).mean()
    df['MACD'] = exp1 - exp2

    latest_close = float(df['Close'].iloc[-1])
    latest_sma = float(df['SMA_5'].iloc[-1])
    latest_rsi = float(df['RSI'].iloc[-1])
    latest_macd = float(df['MACD'].iloc[-1])
    
    trend = "BULLISH 🟢" if latest_close > latest_sma and latest_macd > 0 else "BEARISH 🔴"
    df_chart = df.tail(30)
    
    return df_chart, latest_close, latest_sma, latest_rsi, latest_macd, trend, curr_sym

def run_backtest(ticker_symbol, initial_capital=100000.0):
    ticker = yf.Ticker(ticker_symbol)
    df = ticker.history(period="1y")
    if df.empty: raise ValueError(f"No data for {ticker_symbol}")

    df['SMA_5'] = df['Close'].rolling(window=5).mean()
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))
    df['MACD'] = df['Close'].ewm(span=12, adjust=False).mean() - df['Close'].ewm(span=26, adjust=False).mean()
    
    df = df.dropna()
    
    cash = initial_capital
    shares = 0
    trades = 0
    
    # Baseline: Buy & Hold
    first_price = df['Close'].iloc[0]
    last_price = df['Close'].iloc[-1]
    bnh_shares = initial_capital / first_price
    bnh_value = bnh_shares * last_price
    bnh_return = ((bnh_value - initial_capital) / initial_capital) * 100
    
    # Strategy execution loop
    for i in range(1, len(df)):
        prev_macd = df['MACD'].iloc[i-1]
        curr_macd = df['MACD'].iloc[i]
        curr_rsi = df['RSI'].iloc[i]
        price = df['Close'].iloc[i]
        
        # BUY: MACD crosses above 0 and RSI is not overbought
        if prev_macd <= 0 and curr_macd > 0 and curr_rsi < 70:
            if cash >= price:
                qty = int(cash // price)
                cash -= qty * price
                shares += qty
                trades += 1
        # SELL: MACD crosses below 0 or RSI is overbought
        elif (prev_macd >= 0 and curr_macd < 0) or curr_rsi > 70:
            if shares > 0:
                cash += shares * price
                shares = 0
                trades += 1
                
    final_equity = cash + (shares * last_price)
    algo_return = ((final_equity - initial_capital) / initial_capital) * 100
    
    return final_equity, algo_return, bnh_return, trades