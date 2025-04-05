#!/usr/bin/env python

import os
import requests
import csv
import datetime

# function to get list of tickers from a file
def get_tickers():
    today = datetime.date.today()
    filename = f"tradingbot-tickers-{today.isoformat()}.txt"

    if not os.path.exists(filename):
        print("Downloading tickers list...")
        url = "https://github.com/rreichel3/US-Stock-Symbols/raw/refs/heads/main/nyse/nyse_tickers.txt"
        response = requests.get(url)
        if response.status_code == 200:
            with open(filename, "w") as file:
                file.writelines(response.text.splitlines())
        else:
            print("Failed to download tickers.")
            return []

    with open(filename, "r") as file:
        return [line.strip() for line in file]


# function to flatten dict of dict of list
def flatten(ddl):
    flattened = []
    for key, value in ddl.items():
        flattened.extend(value)
    return flattened

# function to save trade signals to CSV for backtesting
def save_signals_to_csv(trades, filename="backtest_results.csv"):
    flattened_trades = flatten(trades)

    if not flattened_trades:
        print("\n\n\nNo trades to save.\n\n\n")
        return

    keys = ["ticker", "position", "entry", "exit", "stop_loss", "take_profit"]
    with open(filename, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        writer.writerows(flattened_trades)

#    print(f"Trade signals saved to {filename}")

# a function to calculate statistics
def calculate_statistics(trades):

    gross_profit = 0
    gross_loss = 0

    flattened_trades = flatten(trades)
    for trade in flattened_trades:
            if trade['exit'] - trade['entry'] > 0:
                gross_profit += trade['exit'] - trade['entry']
            else:
                gross_loss += abs(trade['exit'] - trade['entry'])

    if gross_loss == 0:
        profit_factor = gross_profit
    else:
        profit_factor = gross_profit / gross_loss

#    print(f"Gross Profit: ${gross_profit:.2f}")
#    print(f"Gross Loss: ${gross_loss:.2f}")
#    print(f"Profit Factor: {profit_factor:.2f}")
    return profit_factor