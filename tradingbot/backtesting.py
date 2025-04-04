#!/usr/bin/env python
import pandas as pd
import yfinance as yf
from tradingbot.strategy import execute_strategy, open_positions
from tradingbot.utils import get_tickers, save_signals_to_csv

# function to run backtest on a given stock ticker
def backtest_strategy(ticker, period="1y", interval="1h"):
    # get historical data
    stock = yf.Ticker(ticker)
    data = stock.history(period=period, interval="1h")
    
    trade_signals = []  

    # start at a point where the moving average window is decently stable
    for i in range(20, len(data)):
        sub_data = data.loc[:data.index[i]].copy() # slice the data for each point in time and copy it
        signal = execute_strategy(ticker, sub_data)
        if signal:
            trade_signals.append(signal)

    # close any remaining open positions
    for positions in open_positions.values():
        for position in positions:
            if position["exit"] is None:  # if no exit was registered
                print(f"[{ticker:^4}] Exiting position at the end of backtest period due to timeout.")
                print(f"Profit: ${(position['entry'] - data["Close"].iloc[-1]):,.6f} due to timeout.\n")
                position["exit"] = data["Close"].iloc[-1]
                trade_signals.append({
                    "ticker": ticker,
                    "position": "EXIT",
                    "entry": position["entry"],
                    "exit": position["exit"],
                    "stop_loss": position["stop_loss"],
                    "take_profit": position["take_profit"],
                    "timestamp": data.index[-1],
                    "peak": position["peak"]
                })

    # save the trade signals to a CSV file for review
    if trade_signals:
        df_signals = pd.DataFrame(trade_signals)
        df_signals.to_csv(f"backtests/signals/{ticker}_backtest_signals_{period}.csv", index=False)
        print(f"[{ticker:^4}] Backtest complete. Signals saved to {ticker}_backtest_signals_{period}.csv")
    else:
        print(f"[{ticker:^4}] No signals generated.")
    
    return trade_signals, data


# function to run backtesting for multiple tickers
def backtest_multiple_tickers(tickers, period="2y"):
    for ticker in tickers:
        trade_signals, data = backtest_strategy(ticker, period)
        calculate_metrics(trade_signals, data, ticker, period)


# function to calculate performance metrics
def calculate_metrics(trade_signals, data, ticker, period):

    total_return = 0  # total return across all trades
    total_gains = 0   # total gains across all trades
    total_losses = 0  # total losses across all trades
    wins = 0          # count of winning trades
    losses = 0        # count of losing trades
    max_drawdown = 0  # maximum drawdown observed
    peak_value = 0    # peak value during the backtest period
    cumulative_return = []  # list to track cumulative return over time (it's total return's items, used to calculate mean)

    for signal in trade_signals:
        entry_price = signal["entry"]
        exit_price = signal.get("exit")  # safely get the exit price (might be None)

        if exit_price is None:  # skip trades that do not have an exit price
            continue

        
        # calculate the return for each trade
        trade_return = (exit_price - entry_price) / entry_price
        total_return += trade_return

        # add to gains/losses vars and track wins/losses
        if trade_return > 0:
            wins += 1
            total_gains += trade_return
        else:
            losses += 1
            total_losses += trade_return

        # calculate the maximum drawdown
        if exit_price < peak_value:
            drawdown = (peak_value - exit_price) / peak_value
            max_drawdown = max(max_drawdown, drawdown)
        else:
            peak_value = exit_price

        cumulative_return.append(total_return)

    # calculate the sharpe ratio for risk-adjusted return
    returns = pd.Series(cumulative_return)
    mean_return = returns.mean()
    std_dev = returns.std()
    sharpe_ratio = (mean_return - 0) / std_dev if std_dev != 0 else 0

    if total_losses != 0:
        profit_factor = total_gains / abs(total_losses)
    else:
        profit_factor = total_gains / 1


    # print the performance metrics
    print(f"\nMetrics for Ticker: {ticker} (Period: {period})")
    print(f"Total Return: {total_return * 100:.2f}%")
    print(f"Winning Trades: {wins}")
    print(f"Losing Trades: {losses}")
    print(f"Maximum Drawdown: {max_drawdown * 100:.2f}%")
    print(f"Sharpe Ratio: {sharpe_ratio:.2f}")
    print(f"Profit Factor: {profit_factor:.2f}")

    save_signals_to_csv(trade_signals, f"backtests/results/{ticker}_backtest_results_{period}.csv")
