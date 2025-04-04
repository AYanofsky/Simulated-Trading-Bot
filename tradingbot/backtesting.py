#!/usr/bin/env python
import pandas as pd
import yfinance as yf
from tradingbot.strategy import execute_strategy
from tradingbot.utils import get_tickers, save_signals_to_csv

# function to run backtest on a given stock ticker
def backtest_strategy(ticker, period="1y"):
    # get historical data
    stock = yf.Ticker(ticker)
    data = stock.history(period=period)
    
    trade_signals = []

    # start at a point where the moving average window is decently stable
    for i in range(20, len(data)):
        sub_data = data.loc[:data.index[i]].copy() # slice the data for each point in time and copy it
        signal = execute_strategy(ticker, sub_data)

        if signal:
            trade_signals.append(signal)

    # save the trade signals to a CSV file for review
    if trade_signals:
        df_signals = pd.DataFrame(trade_signals)
        df_signals.to_csv(f"backtests/signals/{ticker}_backtest_signals_{period}.csv", index=False)
        print(f"Backtest complete for {ticker}. Signals saved to {ticker}_backtest_signals_{period}.csv")
    else:
        print(f"No signals generated for {ticker}.")
    
    return trade_signals, data


# function to run backtesting for multiple tickers
def backtest_multiple_tickers(tickers, period="1y"):
    for ticker in tickers:
        trade_signals, data = backtest_strategy(ticker, period)
        calculate_metrics(trade_signals, data, ticker, period)


# function to calculate performance metrics
def calculate_metrics(trade_signals, data, ticker, period):
    # calculate total return
    total_return = 0
    wins = 0
    losses = 0
    max_drawdown = 0
    peak_value = 0
    cumulative_return = []

    for signal in trade_signals:
        entry_price = signal["entry"]
        exit_price = data.loc[signal["timestamp"]]["Close"]

        # calculate the return for each trade
        trade_return = (exit_price - entry_price) / entry_price
        total_return += trade_return

        # track if the trade was a win or loss
        if trade_return > 0:
            wins += 1
        else:
            losses += 1

        # calculate the maximum drawdown
        if exit_price < peak_value:
            drawdown = (peak_value - exit_price) / peak_value
            max_drawdown = max(max_drawdown, drawdown)
        else:
            peak_value = exit_price

        cumulative_return.append(total_return)

    # calculate the Sharpe ratio for risk-adjusted return (not great, since this is risky as stepping on rusty nails without a tetanus shot.)
    risk_free_rate = 0
    returns = pd.Series(cumulative_return)
    mean_return = returns.mean()
    std_dev = returns.std()
    sharpe_ratio = (mean_return - risk_free_rate) / std_dev if std_dev != 0 else 0

    profit_factor = sum([r for r in cumulative_return if r > 0]) / abs(sum([r for r in cumulative_return if r < 0])) if sum([r for r in cumulative_return if r < 0]) != 0 else 0

    # summary of metrics
    print(f"Ticker: {ticker}")
    print(f"Total Return: {total_return * 100:.2f}%")
    print(f"Winning Trades: {wins}")
    print(f"Losing Trades: {losses}")
    print(f"Maximum Drawdown: {max_drawdown * 100:.2f}%")
    print(f"Sharpe Ratio: {sharpe_ratio:.2f}")
    print(f"Profit Factor: {profit_factor:.2f}")

    save_signals_to_csv("backtests/results/" + ticker + "_backtest_results_" + period + ".csv")
