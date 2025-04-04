#!/usr/bin/env python

import os
import pandas as pd
import yfinance as yf
import requests
import datetime
import concurrent.futures

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
                file.write(line)
                file.write("\n")

        print("Tickers list written to disk.")
    else:
        print("Tickers list found on disk.")
        with open(filename, 'r') as file:
            lines = file.readlines()

    return lines


# function to get the day-to-day data of a list of stocks
def get_opening_cap(tickers):
    stocks = yf.Tickers(tickers)
    
    opening_caps = {}
    histories = {}

    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        # Get history data concurrently for each ticker
        future_histories = {executor.submit(get_history, ticker, stocks): ticker for ticker in tickers}
        for future in concurrent.futures.as_completed(future_histories):
            ticker = future_histories[future]
            hist = future.result()
            if hist is not None:
                histories[ticker] = hist
                opening_price = hist.iloc[0]['Open']
                
                # get number of investor-held shares
                stock = stocks.ticker[ticker]
                investor_held_shares = stock.info.get("sharesOutstanding", None)
                
                if opening_price is None or investor_held_shares is None:
                    print(f"Couldn't find opening data for {ticker}.")
                else:
                    opening_caps[ticker] = opening_price * investor_held_shares

    return opening_caps, histories


# function to get the latest market cap for each ticker
def get_latest_cap(histories):
    latest_caps = {}

    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        # Get latest market cap data concurrently
        future_caps = {executor.submit(get_latest_cap_for_ticker, ticker, histories): ticker for ticker in histories}
        
        for future in concurrent.futures.as_completed(future_caps):
            ticker = future_caps[future]
            latest_cap = future.result()
            if latest_cap is not None:
                latest_caps[ticker] = latest_cap

    return latest_caps


# function to get the latest market cap for a single ticker
def get_latest_cap_for_ticker(ticker, histories):
    try:
        stock = yf.Ticker(ticker)
        latest_price = stock.info.get("currentPrice", None)
        investor_held_shares = stock.info.get("sharesOutstanding", None)
        
        if latest_price is None or investor_held_shares is None:
            print(f"Skipping {ticker} due to missing data.")
            return None
        
        return latest_price * investor_held_shares
    except Exception as e:
        print(f"Error fetching data for {ticker}: {e}")
        return None


# function to get the history for a single ticker
def get_history(ticker, stocks):
    try:
        hist = stocks.tickers[ticker].history(period='1d', interval="1m")
        if hist.empty:
            print(f"No data found for {ticker}")
            return None
        print(f"data found for {ticker}")
        return hist
    except Exception as e:
        print(f"Error fetching history for {ticker}: {e}")
        return None


# function to calculate % delta in market cap from open to current day
def market_cap_percentage_delta(open_cap, latest_cap):
    if open_cap is None or latest_cap is None:
        return None
    delta = ((latest_cap - open_cap)) / open_cap
    return delta