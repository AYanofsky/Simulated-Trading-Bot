#!/usr/bin/env python

import os
import pandas as pd
import yfinance as yf
import requests
import datetime

# function to fetch data from repo
def get_tickers():

    today = datetime.date.today()
    filename = today.ctime().replace(" ", "_") + ".txt"

    # if file doesn't exist, download and save it
    if os.path.exists(filename) is not True:
        # link to github raw file from @rreichel3's repository: https://github.com/rreichel3/US-Stock-Symbols
        url = "https://github.com/rreichel3/US-Stock-Symbols/raw/refs/heads/main/nyse/nyse_tickers.txt"
        
        response = requests.get(url)

        if response.status_code != 200:
            print("Failed to download tickers list.")
            return []

        lines = response.text.split()
        
        with open(filename,'w') as file:
            for line in lines:
                file.write(line)
                file.write("\n")
            file.close()
    else:
        # if file exists, read it
        with open(filename, 'r') as file:
            lines = file.readlines()
            lines = lines.split()

    return lines

# function to get a list of stocks' history over a defined time period
def get_history(stocks):

    data = stocks.history(period="1d",interval="1m")

    return data

# function to get the day-to-day data of a list of stocks
def get_opening_cap(tickers):

    # convert list of tickers to a list of stocks
    stocks = yf.Tickers(tickers)

    # get history from list of stocks
    data = get_history(stocks)

    opening_caps = {}

    # get the opening prices for every ticker in the list of tickers
    for ticker in tickers:
        hist = data[ticker]
        opening_price = hist.iloc[0]['Open']

        # get number of investor-held shares
        stock = stocks.ticker[ticker]
        investor_held_shares = stock.info.get("sharesOutstanding",None)
        
        # ensure that the stock has information available
        if opening_price is None or investor_held_shares is None:
            print(f"Couldn't find opening data for {ticker}.")
            data.remove(ticker)
        else:
            opening_caps[ticker] = opening_price * investor_held_shares

    fake_tuple = [opening_caps, data]
    return fake_tuple


# function to return the latest market cap
def get_latest_cap(fake_tuple):
    

    stock = yf.Tickers(tickers)

    # current near-real-time stock price
    latest_price = stock.info.get("currentPrice", None)

    # current near-real-time number of shares held by investors
    investor_held_shares = stock.info.get("sharesOutstanding", None)

    if latest_price is None or investor_held_shares is None:
        print(f"Could not find near-real-time data for {ticker}")
        return None


    return latest_price * investor_held_shares

# function to calculate % delta in market cap from open to current day
def market_cap_percentage_delta(open_cap,latest_cap):
    if open_cap is None or latest_cap is None:
        return None

    # note that this returns DECIMAL percentage e.g. 100% is 1 and 50% is 0.5
    delta = ((latest_cap - open_cap))/open_cap
    return delta