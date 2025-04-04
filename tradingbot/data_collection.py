#! /bin/bash/env python

import asyncio
import yfinance as yf   
from asyncio import Queue
from tradingbot.utils import get_tickers

# async function to get historical data for a ticker
async def get_history(ticker):
    stock = yf.Ticker(ticker)
    data = await asyncio.to_thread(stock.history,period="30d")
    return ticker, data


# async function to collect data for all tickers in the background
async def collect_data(tickers, data_queue):
    # iterate over list of tickers and get data for each
    tasks = []
    for ticker in tickers:
        tasks.append(asyncio.create_task(get_history(ticker)))
    
    # process results as they arrive!
    for task in asyncio.as_completed(tasks):
        ticker, data = await task

        # self explanatory
        if data.empty:
            print(f"No data for {ticker}, skipping.")
            continue

        packet = (ticker, data)
        await data_queue.put(packet)
#        print(f"Data for {ticker} sent.")

# handler function to begin data collection
async def start_collecting(tickers, data_queue):
    await collect_data(tickers, data_queue)