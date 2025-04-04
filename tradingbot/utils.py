#!/usr/bin/env python

import os
import csv
import yfinance as yf
import requests
import datetime
from threading import Lock

lock = Lock()

# function to fetch data from repo
def get_tickers():
   # get today's date and create a text file containing tickers
    today = datetime.date.today()
    filename = "tradingbot-tickers-" + today.isoformat() + ".txt"

    # if file doesn't exist, download and save it
    if os.path.exists(filename) is not True:
        print("Downloading tickers list.")
        # link to github raw file from @rreichel3's repository: https://github.com/rreichel3/US-Stock-Symbols
        url = "https://github.com/rreichel3/US-Stock-Symbols/raw/refs/heads/main/nyse/nyse_tickers.txt"

        response = requests.get(url)

        if response.status_code != 200:
            print("Failed to download tickers list.")
            return []

        lines = response.text.split()

        with open(filename, 'w') as file:
            for line in lines:
                file.write(line + '\n')

        print("Tickers list written to disk.")

    else:
        print("Tickers list found on disk.")
        with open(filename, 'r') as file:
            lines = file.readlines()

    return [line.strip() for line in lines]


# function to get the day-to-day data of a single ticker
def get_opening_cap(ticker):
    with lock:
        # get daily historical data
        stock = yf.Ticker(ticker)
        data = stock.history(period="1d")
        # get the opening price for the first day in history
        opening_cap = data['Open'].iloc[0]
    return opening_cap


# function to get the current market cap of a single ticker
def get_latest_cap(ticker):
    with lock:
        # get the ticker info
        stock = yf.Ticker(ticker)
        data = stock.info()
        # get the market cap from the info dictionary
        latest_cap = data.get('marketCap', None)
    return latest_cap

# function to save signals received to file for backtesting
def save_signals_to_csv(trade_signals, filename="backtest_results.csv"):
    if not trade_signals:
        print("No signals to save.")
        return

    # define headers for csv file
    keys = ["ticker", "position", "entry", "exit", "stop_loss", "take_profit", "timestamp"]
    
    with open(filename, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        writer.writerows(trade_signals)

    print(f"Trade signals saved to {filename}")