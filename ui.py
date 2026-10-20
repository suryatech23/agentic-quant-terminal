import mplfinance as mpf
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()

def render_candlestick_chart(ticker_symbol, df):
    market_colors = mpf.make_marketcolors(up='#00ff7f', down='#ff4500', wick={'up':'#00ff7f', 'down':'#ff4500'}, edge={'up':'#00ff7f', 'down':'#ff4500'}, volume='in')
    chart_style = mpf.make_mpf_style(base_mpf_style='nightclouds', marketcolors=market_colors, gridcolor='#2a2e39', facecolor='#131722')
    mpf.plot(df, type='candle', mav=(5), volume=True, title=f"\n{ticker_symbol.upper()} - 1 Month Technical Overview", style=chart_style, show_nontrading=False, block=False)

def display_terminal_dashboard(ticker, price, sma, rsi, macd, trend, curr_sym):
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Metric", style="cyan", width=22)
    table.add_column("Value", style="green")
    table.add_row("Target Asset", ticker.upper())
    table.add_row("Current Price", f"{curr_sym}{price:.2f}")
    table.add_row("5-Day SMA", f"{curr_sym}{sma:.2f}")
    table.add_row("14-Day RSI", f"{rsi:.2f}")
    table.add_row("MACD (12,26)", f"{macd:.3f}")
    table.add_row("Market Momentum", trend)
    console.print(Panel(table, title=f"[bold blue]QUANTITATIVE ANALYSIS: {ticker.upper()}[/bold blue]", expand=False))