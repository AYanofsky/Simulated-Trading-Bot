#!/usr/bin/env python

import pandas as pd

# Dfunction to detect breakouts based on historical data
def detect_breakouts(data):
    # calculate moving average and standard deviation
    data['Moving_Avg'] = data['Close'].rolling(window=20).mean()
    data['Std_Dev'] = data['Close'].rolling(window=20).std()

    # define breakout levels
    breakout_threshold = 1.02
    breakdown_threshold = 0.99

    # current price and moving average
    current_price = data['Close'].iloc[-1]
    moving_avg = data['Moving_Avg'].iloc[-1]

    breakout_up = current_price > moving_avg * breakout_threshold
    breakout_down = current_price < moving_avg * breakdown_threshold

    return breakout_up, breakout_down

# function to provide stop-loss and take-profit logic
def stop_loss_take_profit(entry_price, breakout_up):
    stop_loss_percent = 0.04
    take_profit_percent = 0.15

    if breakout_up:
        stop_loss = entry_price * (1 - stop_loss_percent)
        take_profit = entry_price * (1 + take_profit_percent)
    else:
        stop_loss = entry_price * (1 + stop_loss_percent)
        take_profit = entry_price * (1 - take_profit_percent)

    return stop_loss, take_profit

# function for strategy execution
def execute_strategy(ticker, data, open_positions):
    current_price = data['Close'].iloc[-1]
    breakout_up, breakout_down = detect_breakouts(data)

    # check for open positions to manage stop-loss and take-profit orders
    if ticker in open_positions:
        for position in open_positions[ticker]:
            stop_loss, take_profit = position['stop_loss'], position['take_profit']
            if (position['position'] == "LONG" and (current_price <= stop_loss or current_price >= take_profit)) or \
                (position['position'] == "SHORT" and (current_price >= stop_loss or current_price <= take_profit)):
                print(f"[{ticker}] Exiting position at {current_price} due to stop-loss/take-profit hit.")
                position["exit"] = current_price
                open_positions[ticker].remove(position)

    # execute strategies if a breakout is occurring
    if breakout_up:
        stop_loss, take_profit = stop_loss_take_profit(current_price, breakout_up=True)
        print(f"[{ticker}] Breakout detected: BUY LONG at {current_price}")
        position = {"ticker": ticker, "position": "LONG", "entry": current_price, "exit": None,
                    "stop_loss": stop_loss, "take_profit": take_profit}
        open_positions.setdefault(ticker, []).append(position)

    elif breakout_down:
        stop_loss, take_profit = stop_loss_take_profit(current_price, breakout_up=False)
        print(f"[{ticker}] Breakout detected: SELL SHORT at {current_price}")
        position = {"ticker": ticker, "position": "SHORT", "entry": current_price, "exit": None,
                    "stop_loss": stop_loss, "take_profit": take_profit}
        open_positions.setdefault(ticker, []).append(position)

    else:
        print(f"[{ticker}] No breakout detected.")

    return open_positions