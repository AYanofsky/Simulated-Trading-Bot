#!/usr/bin/env python

import pandas as pd
import yfinance as yf
from tradingbot.algorithm import execute_strategy, open_positions
from tradingbot.utils import save_signals_to_csv

# function to get historical data for backtesting
def get_historical_data(ticker, period="1y", interval="1h"):
    stock = yf.Ticker(ticker)
    data = stock.history(period=period, interval=interval)
    return data

# function to facilitate backtesting for a single ticker
def backtest_strategy(ticker, period="1y", interval="1h", breakout_up_threshold=1.02, 
                      breakout_down_threshold=0.98, stop_loss_percent=0.04, take_profit_percent=0.15):

    data = get_historical_data(ticker, period, interval)
    trade_signals = []

    # iterate over historical data
    for i in range(20, len(data)):
        sub_data = data[:data.index[i]].copy()  # Slice the data up to each point
        open_positions = execute_strategy(ticker, sub_data, breakout_up_threshold, 
                                          breakout_down_threshold, stop_loss_percent, take_profit_percent)

        for position in open_positions.get(ticker, []):
            if position.get('exit') is not None:
                trade_signals.append(position)

    # close remaining positions at the end of the backtest period
    for positions in open_positions.values():
        for position in positions:
            if position["exit"] is None:
                position["exit"] = data["Close"].iloc[-1]
                trade_signals.append(position)

    # save trade signals to CSV
    save_signals_to_csv(trade_signals, f"backtests/signals/{ticker}_signals_results.csv")

# function to iterate over every ticker and backtest it
def backtest_multiple_tickers(tickers, period, interval, breakout_up_threshold, breakout_down_threshold, stop_loss_percent, take_profit_percent):
    for ticker in tickers:
        open_positions[ticker] = []
        backtest_strategy(ticker, period, interval, breakout_up_threshold, breakout_down_threshold, stop_loss_percent, take_profit_percent)
