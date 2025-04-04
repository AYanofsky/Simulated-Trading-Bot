#!/usr/bin/env python
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime

# async function to decide what strategy to use
async def process_data(data_queue):
    while True:
        # get data from the queue
        ticker, data = await data_queue.get()
        print(f"Processing data for {ticker}...")
        
        # run the breakout detection and strategy execution
        breakout_up, breakout_down, processed_data = detect_breakout(data)
        
        if breakout_up:
            execute_strategy(ticker, processed_data)
        elif breakout_down:
            execute_strategy(ticker, processed_data)

        data_queue.task_done()  # Mark the task as done


# function to detect breakouts based on historical data
def detect_breakouts(data):

    # calculate moving average and standard deviation to handle volatility
    data['Moving_Avg'] = data['Close'].rolling(window=20).mean()
    data['Std_Dev'] = data['Close'].rolling(window=20).std()

    # define breakout levels
    breakout_threshold = 1.02
    breakdown_threshold = 0.98

    # current price and moving average
    current_price = data['Close'].iloc[-1]
    moving_avg = data['Moving_Avg'].iloc[-1]

    # detect breakouts by checking to see if the current price is above/below a percentage of the breakout/breakdown threshold
    breakout_up = current_price > moving_avg * breakout_threshold
    breakout_down = current_price < moving_avg * breakdown_threshold

    return breakout_up, breakout_down, data


# function to determine stop-loss and take-profit logic
def stop_loss_take_profit(entry_price,breakout_up=True): # breakout set to true for testing purposes

    # define stop-loss and take-profit margins
    stop_loss_percent = 0.05
    take_profit_percent = 0.10

    if breakout_up:
        stop_loss = entry_price * (1 - stop_loss_percent)
        take_profit = entry_price * (1 + take_profit_percent)
    else:
        stop_loss = entry_price * (1 + stop_loss_percent)
        take_profit = entry_price * (1 - take_profit_percent)

    return stop_loss, take_profit


# function to execute the trading strategy
def execute_strategy(ticker, data):
    # strategy will be triggered if a breakout is occurring
    current_price = data['Close'].iloc[-1]
    breakout_up, breakout_down, processed_data = detect_breakouts(data)
    
    # simulating breaking out to execute a trade
    if breakout_up:
        print(f"Breakout detected for {ticker}: Buying at {current_price}")
        stop_loss, take_profit = stop_loss_take_profit(current_price, breakout_up=True)
        print(f"Stop-loss: {stop_loss}, Take-profit: {take_profit}")
        
    elif breakout_down:
        print(f"Breakout detected for {ticker}: Selling at {current_price}")
        stop_loss, take_profit = stop_loss_take_profit(current_price, breakout_up=False)
        print(f"Stop-loss: {stop_loss}, Take-profit: {take_profit}")

    else:
        print(f"No breakout detected for {ticker}.")

# function to execute strategy for multiple tickets using data generated in the data-collection step
def execute_batch_strategy(tickers, data_dict):
    for ticker in tickers:
        if ticker in data_dict:
            execute_strategy(ticker, data_dict[ticker])
        else:
            print(f"No data available for {ticker}.")
