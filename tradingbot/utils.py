#!/usr/bin/env python

import os
import pandas as pd
import yfinance as yf
import requests
import datetime

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
    try:
        stock = yf.Ticker(ticker)
        history = stock.history(period="1d",interval="1m")

        # opening price of most recent trading day
        opening_price = history["Open"].iloc[0]

        # shares owned by investors
        shares_outstanding = stock.info.get("sharesOutstanding", None)

        if opening_price is None or shares_outstanding is None:
            raise ValueError(f"Missing data for {ticker}")
        
    except Exception as ex:
        print(f"Error fetching opening cap for {ticker}: {ex}")
        return None

    opening_cap = opening_price * shares_outstanding
    return opening_cap


# function to get the current market cap of a single ticker
def get_latest_cap(ticker):
    try:
        stock = yf.Ticker(ticker)
        
        # current market cap of the stock
        latest_cap = stock.info.get('marketCap', None)
        
        if latest_cap is None:
            raise ValueError(f"Missing market cap data for {ticker}")
        
        return latest_cap

    except Exception as ex:
        print(f"Error fetching latest cap for {ticker}: {ex}")
        return None

# function to get the history for a single ticker
def get_history(tickers):

    histories = {}

    for ticker in tickers:
        try:
            stock = yf.Ticker(ticker)
            history = stock.history(period="1d", interval="1m")

            if history.empty:
                raise ValueError (f"No historical data returned for {ticker}")

            histories[ticker] = history

        except Exception as ex:
            print(f"Error fetching history for ticker {ticker}: {ex}")
            continue

    return histories



# function to calculate % delta in market cap from open to current day
def market_cap_percentage_delta(open_cap, latest_cap):
    if open_cap is None or latest_cap is None:
        return None
    delta = ((latest_cap - open_cap)) / open_cap
    return delta