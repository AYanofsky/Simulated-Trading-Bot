#!/usr/bin/env python

import pandas as pd
import yfinance as yf
from algorithm import execute_strategy
from utils import save_signals_to_csv

# Function to get historical data for backtesting
def get_historical_data(ticker, period="1y", interval="1h"):
    stock = yf.Ticker(ticker)
    data = stock.history(period=period, interval=interval)
    return data

# Backtesting for a single ticker
def backtest_strategy(ticker, period="1y", interval="1h", open_positions={}):
    data = get_historical_data(ticker, period, interval)
    trade_signals = []

    # Iterate over the historical data
    for i in range(20, len(data)):
        sub_data = data[:data.index[i]].copy()  # Slice the data up to each point
        open_positions = execute_strategy(ticker, sub_data, open_positions)

        for position in open_positions.get(ticker, []):
            if position.get('exit') is not None:
                trade_signals.append(position)

    # Close remaining positions at the end of the backtest period
    for positions in open_positions.values():
        for position in positions:
            if position["exit"] is None:
                position["exit"] = data["Close"].iloc[-1]
                trade_signals.append(position)

    # Save trade signals to CSV
    save_signals_to_csv(trade_signals, f"{ticker}_backtest_results.csv")

# Backtesting for multiple tickers
def backtest_multiple_tickers(tickers, period="2y"):
    open_positions = {}
    for ticker in tickers:
        backtest_strategy(ticker, period, open_positions=open_positions)
