import os
import json
import re
from dotenv import load_dotenv
from rich.prompt import Prompt
from rich.panel import Panel
from rich.markdown import Markdown
from rich.table import Table
from openai import OpenAI

from ledger import load_portfolio, save_portfolio, log_transaction
from data_pipeline import fetch_market_data, run_backtest
from ui import console, render_candlestick_chart, display_terminal_dashboard

load_dotenv()
client = OpenAI(api_key=os.getenv("GROQ_API_KEY"), base_url="https://api.groq.com/openai/v1")

def build_system_prompt(ticker, price, sma, rsi, macd, trend, curr_sym):
    return f"""You are an elite quantitative trading AI. You are analyzing {ticker.upper()}. 
    Price: {curr_sym}{price:.2f} | 5-Day SMA: {curr_sym}{sma:.2f} | 14-Day RSI: {rsi:.2f} | MACD: {macd:.3f} | Trend: {trend}.
    If RSI is > 70, the asset is overbought. If RSI is < 30, it is oversold.
    Keep answers highly analytical and concise."""

def agentic_chat_loop(initial_target, initial_price, initial_sma, initial_rsi, initial_macd, initial_trend, initial_curr_sym):
    portfolio = load_portfolio()
    target, price, sma, rsi, macd = initial_target, initial_price, initial_sma, initial_rsi, initial_macd
    trend, curr_sym = initial_trend, initial_curr_sym
    
    messages = [{"role": "system", "content": build_system_prompt(target, price, sma, rsi, macd, trend, curr_sym)}]
    console.print("\n[bold dark_orange]COMMANDS: 'buy <qty>', 'sell <qty>', 'portfolio', 'history', 'backtest', 'switch <ticker>', 'refresh', 'auto', 'exit'[/bold dark_orange]")
    
    while True:
        user_input = Prompt.ask(f"\n[bold yellow]Terminal ({target.upper()})[/bold yellow]").strip()
        parts = user_input.lower().split()
        if not parts: continue
        command = parts[0]
        
        if command in ['exit', 'quit']:
            console.print("[bold red]Shutting down...[/bold red]")
            break
            
        elif command == 'switch' and len(parts) > 1:
            new_target = parts[1].upper()
            try:
                df, price, sma, rsi, macd, trend, curr_sym = fetch_market_data(new_target)
                target = new_target
                display_terminal_dashboard(target, price, sma, rsi, macd, trend, curr_sym)
                render_candlestick_chart(target, df)
                messages[0] = {"role": "system", "content": build_system_prompt(target, price, sma, rsi, macd, trend, curr_sym)}
            except Exception as e: console.print(f"[bold red]Error:[/bold red] {e}")
            continue

        # --- NEW REFRESH COMMAND ---
        elif command == 'refresh':
            with console.status(f"[bold cyan]Fetching latest live snapshot for {target}...[/bold cyan]", spinner="dots"):
                try:
                    df, price, sma, rsi, macd, trend, curr_sym = fetch_market_data(target)
                    display_terminal_dashboard(target, price, sma, rsi, macd, trend, curr_sym)
                    messages[0] = {"role": "system", "content": build_system_prompt(target, price, sma, rsi, macd, trend, curr_sym)}
                except Exception as e: console.print(f"[bold red]Refresh Error:[/bold red] {e}")
            continue

        elif command in ['portfolio', 'balance']:
            console.print(f"\n[bold blue]=== GLOBAL PORTFOLIO LEDGER ===[/bold blue]")
            console.print(f"Liquid Cash:   {curr_sym}{portfolio['cash']:,.2f}")
            for sym, qty in portfolio['positions'].items(): console.print(f"Active Shares: {qty} {sym}")
            continue
            
        elif command == 'history':
            if not portfolio.get("history"):
                console.print("[bold yellow]No trade history found.[/bold yellow]")
                continue
            table = Table(title="[bold blue]TRANSACTION HISTORY[/bold blue]", show_header=True, header_style="bold magenta")
            table.add_column("Date/Time", style="cyan")
            table.add_column("Action", justify="center")
            table.add_column("Asset", style="bold")
            table.add_column("Qty", justify="right")
            table.add_column("Price", justify="right")
            table.add_column("Total Value", justify="right")
            for t in portfolio["history"]:
                action_style = "[bold green]BUY[/bold green]" if t['action'] == 'BUY' else "[bold red]SELL[/bold red]"
                c_sym = t.get('currency', '$')
                table.add_row(t['time'], action_style, t['ticker'], str(t['qty']), f"{c_sym}{t['price']:.2f}", f"{c_sym}{t['total']:.2f}")
            console.print(table)
            continue
            
        elif command == 'backtest':
            with console.status(f"[bold cyan]Running 1-Year historical strategy backtest on {target}...[/bold cyan]", spinner="dots"):
                try:
                    final_eq, algo_ret, bnh_ret, trades = run_backtest(target)
                    b_table = Table(title=f"[bold blue]1-YEAR BACKTEST: {target}[/bold blue]", show_header=True)
                    b_table.add_column("Metric", style="cyan")
                    b_table.add_column("Result", justify="right")
                    b_table.add_row("Starting Capital", f"{curr_sym}100,000.00")
                    b_table.add_row("Final Equity", f"{curr_sym}{final_eq:,.2f}")
                    b_table.add_row("Total Trades Executed", str(trades))
                    algo_color = "green" if algo_ret >= 0 else "red"
                    bnh_color = "green" if bnh_ret >= 0 else "red"
                    b_table.add_row("Algo Strategy Return", f"[{algo_color}]{algo_ret:,.2f}%[/{algo_color}]")
                    b_table.add_row("Buy & Hold Return", f"[{bnh_color}]{bnh_ret:,.2f}%[/{bnh_color}]")
                    console.print(b_table)
                    if algo_ret > bnh_ret: console.print("[bold green]Verdict: Strategy OUTPERFORMED the market.[/bold green]")
                    else: console.print("[bold red]Verdict: Strategy UNDERPERFORMED Buy & Hold.[/bold red]")
                except Exception as e: console.print(f"[bold red]Backtest Error:[/bold red] {e}")
            continue
            
        elif command == 'buy' and len(parts) > 1 and parts[1].isdigit():
            qty = int(parts[1])
            total_cost = qty * price
            if portfolio["cash"] >= total_cost:
                portfolio["cash"] -= total_cost
                portfolio["positions"][target] = portfolio["positions"].get(target, 0) + qty
                log_transaction(portfolio, "BUY", target, qty, price, total_cost, curr_sym)
                save_portfolio(portfolio)
                console.print(f"[bold green][EXECUTED][/bold green] BUY {qty} {target} @ {curr_sym}{price:.2f}")
            else: console.print("[bold red][REJECTED][/bold red] Insufficient Capital.")
            continue
            
        elif command == 'sell' and len(parts) > 1 and parts[1].isdigit():
            qty = int(parts[1])
            total_revenue = qty * price
            if portfolio["positions"].get(target, 0) >= qty:
                portfolio["cash"] += total_revenue
                portfolio["positions"][target] -= qty
                if portfolio["positions"][target] == 0: del portfolio["positions"][target]
                log_transaction(portfolio, "SELL", target, qty, price, total_revenue, curr_sym)
                save_portfolio(portfolio)
                console.print(f"[bold green][EXECUTED][/bold green] SELL {qty} {target} @ {curr_sym}{price:.2f}")
            else: console.print("[bold red][REJECTED][/bold red] Insufficient Inventory.")
            continue

        elif command == 'auto':
            console.print("[bold magenta]Initiating Autonomous AI Trading Protocol...[/bold magenta]")
            current_shares = portfolio["positions"].get(target, 0)
            auto_prompt = f"""Based on {target}'s Price ({curr_sym}{price:.2f}), SMA ({curr_sym}{sma:.2f}), RSI ({rsi:.2f}), and MACD ({macd:.3f}), make a trading decision. 
            You have {portfolio['cash']} cash and {current_shares} shares. 
            RESPOND ONLY WITH RAW JSON. Do not include markdown formatting or explanations outside the JSON.
            Format: {{"action": "BUY" or "SELL" or "HOLD", "qty": integer, "reason": "brief explanation"}}"""
            
            temp_messages = messages + [{"role": "user", "content": auto_prompt}]
            with console.status("[bold cyan]Agent is calculating execution matrix...[/bold cyan]", spinner="point"):
                try:
                    response = client.chat.completions.create(model="openai/gpt-oss-20b", messages=temp_messages, temperature=0.1)
                    ai_reply = response.choices[0].message.content
                    match = re.search(r'\{.*\}', ai_reply, re.DOTALL)
                    json_str = match.group(0) if match else ai_reply
                    
                    decision = json.loads(json_str)
                    action = decision.get("action", "HOLD").upper()
                    qty = int(decision.get("qty", 0))
                    reason = decision.get("reason", "No reason provided.")
                    
                    console.print(Panel(f"[bold white]Logic:[/bold white] {reason}", title=f"AI Decision: {action} {qty} {target}", border_style="cyan"))
                    
                    # --- HUMAN IN THE LOOP (HITL) CONFIRMATION ---
                    if action in ["BUY", "SELL"] and qty > 0:
                        confirm = Prompt.ask(f"[bold yellow]Authorize AI to {action} {qty} shares of {target}? (y/n)[/bold yellow]", choices=["y", "n"], default="n")
                        if confirm.lower() != 'y':
                            console.print("[bold red][ABORTED][/bold red] AI trade blocked by user.")
                            continue

                        if action == "BUY":
                            total_cost = qty * price
                            if portfolio["cash"] >= total_cost:
                                portfolio["cash"] -= total_cost
                                portfolio["positions"][target] = portfolio["positions"].get(target, 0) + qty
                                log_transaction(portfolio, "BUY", target, qty, price, total_cost, curr_sym)
                                save_portfolio(portfolio)
                                console.print(f"[bold green][AUTO-EXECUTED][/bold green] Bought {qty} shares.")
                            else: console.print("[bold red][AUTO-REJECTED][/bold red] AI attempted to buy without sufficient cash.")
                        
                        elif action == "SELL":
                            total_revenue = qty * price
                            if portfolio["positions"].get(target, 0) >= qty:
                                portfolio["cash"] += total_revenue
                                portfolio["positions"][target] -= qty
                                if portfolio["positions"][target] == 0: del portfolio["positions"][target]
                                log_transaction(portfolio, "SELL", target, qty, price, total_revenue, curr_sym)
                                save_portfolio(portfolio)
                                console.print(f"[bold green][AUTO-EXECUTED][/bold green] Sold {qty} shares.")
                            else: console.print("[bold red][AUTO-REJECTED][/bold red] AI attempted to sell unowned shares.")
                    else:
                        console.print("[bold yellow][AUTO-EXECUTED][/bold yellow] Agent decided to HOLD position.")
                except Exception as e:
                    console.print(f"[bold red]Execution Error:[/bold red] {e}")
            continue

        messages.append({"role": "user", "content": user_input})
        with console.status("[bold cyan]Agent is analyzing...[/bold cyan]", spinner="point"):
            try:
                response = client.chat.completions.create(model="openai/gpt-oss-20b", messages=messages, temperature=0.3)
                ai_reply = response.choices[0].message.content
                messages.append({"role": "assistant", "content": ai_reply})
                console.print(Panel(Markdown(ai_reply), title="[bold magenta]Stealth Quant AI[/bold magenta]", border_style="magenta"))
            except Exception as e: console.print(f"[bold red]API Error:[/bold red] {e}")

if __name__ == "__main__":
    console.clear()
    target = console.input("[bold yellow]Enter global ticker symbol: [/bold yellow]").strip().upper() or "AAPL"
    with console.status(f"[bold yellow]Tapping into real-time feeds for {target}...", spinner="dots"):
        try:
            df, price, sma, rsi, macd, trend, curr_sym = fetch_market_data(target)
            display_terminal_dashboard(target, price, sma, rsi, macd, trend, curr_sym)
            render_candlestick_chart(target, df)
        except Exception as e:
            console.print(f"[bold red]Pipeline Error:[/bold red] {e}")
            exit()
    agentic_chat_loop(target, price, sma, rsi, macd, trend, curr_sym)