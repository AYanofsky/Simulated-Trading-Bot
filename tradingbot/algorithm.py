#!/usr/bin/env python

from collections import defaultdict
import pandas as pd

trades = {}

# function to detect breakouts based on historical data
def detect_breakouts(data,breakout_up_threshold=1.02, breakout_down_threshold=0.98):
    # Calculate moving average and standard deviation
    data["Moving_Avg"] = data["Close"].rolling(window=20).mean()
    data["Std_Dev"] = data["Close"].rolling(window=20).std()

    # Current price and moving average
    current_price = data["Close"].iloc[-1]
    moving_avg = data["Moving_Avg"].iloc[-1]

    breakout_up = current_price > moving_avg * breakout_up_threshold
    breakout_down = current_price < moving_avg * breakout_down_threshold

    return breakout_up, breakout_down

# function to perform stop-loss and take-profit logic
def stop_loss_take_profit(entry_price, breakout_up,  stop_loss_percent=0.04, take_profit_percent=0.15):

    if breakout_up:
        stop_loss = entry_price * (1 - stop_loss_percent)
        take_profit = entry_price * (1 + take_profit_percent)
    else:
        stop_loss = entry_price * (1 + stop_loss_percent)
        take_profit = entry_price * (1 - take_profit_percent)

    return stop_loss, take_profit

# function to facilitate strategy execution
def execute_strategy(ticker, data, breakout_up_threshold=1.02, breakout_down_threshold=0.98, 
                     stop_loss_percent=0.04, take_profit_percent=0.15):
    current_price = data["Close"].iloc[-1]
    breakout_up, breakout_down = detect_breakouts(data, breakout_up_threshold, breakout_down_threshold)

    # check for open positions and manage stop-loss, take-profit, and trailing adjustments
    if ticker in trades:
        for position in trades[ticker]:
            stop_loss, take_profit = position["stop_loss"], position["take_profit"]
            if (position["position"] == "LONG" and (current_price <= stop_loss or current_price >= take_profit)) or \
                (position["position"] == "SHORT" and (current_price >= stop_loss or current_price <= take_profit)):
#                print(f"[{ticker}] Exiting {position["position"]} position at delta of {(current_price / position["entry"]):.2f}x due to stop-loss/take-profit hit.")
                position["position"] = "EXIT"
                position["exit"] = current_price

    # execute new strategy based on breakout
    if breakout_up:
        stop_loss, take_profit = stop_loss_take_profit(current_price, breakout_up=True, stop_loss_percent=stop_loss_percent, 
                                                       take_profit_percent=take_profit_percent)
#        print(f"[{ticker}] Breakout detected: BUY LONG at {current_price}")
        position = {"ticker": ticker,
                    "position": "LONG",
                    "entry": current_price,
                    "exit": None,
                    "stop_loss": stop_loss,
                    "take_profit": take_profit}

        trades[ticker].append(position)

    elif breakout_down:
        stop_loss, take_profit = stop_loss_take_profit(current_price, breakout_up=False, stop_loss_percent=stop_loss_percent, 
                                                       take_profit_percent=take_profit_percent)
#        print(f"[{ticker}] Breakout detected: SELL SHORT at {current_price}")
        position = {"ticker": ticker, 
                    "position": "SHORT", 
                    "entry": current_price, 
                    "exit": None,
                    "stop_loss": stop_loss, 
                    "take_profit": take_profit}

        trades[ticker].append(position)

    return trades