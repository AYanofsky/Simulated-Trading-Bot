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

# function to save trade signals to CSV for backtesting
def save_signals_to_csv(trades, filename="backtest_results.csv"):
    flattened_trades = []
    for ticker, records in trades.items():
        flattened_trades.extend(records)

    if not flattened_trades:
        print("\n\n\nNo trades to save.\n\n\n")
        return

    keys = ["ticker", "position", "entry", "exit", "stop_loss", "take_profit"]
    with open(filename, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        writer.writerows(flattened_trades)

    print(f"Trade signals saved to {filename}")
