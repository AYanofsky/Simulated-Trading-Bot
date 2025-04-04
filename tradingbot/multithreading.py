#! /bin/bash/env python

import concurrent.futures
import yfinance as yf
import numpy as np
from tradingbot.utils import get_history, get_opening_cap, get_latest_cap

# function to resolve a batch of tickers
def resolve_batch(tickers):
    tickers = tickers.tolist()
    stocks = yf.Tickers(tickers)
    
    # get history, open market cap, and latest market cap
    histories = {ticker: get_history(ticker, stocks) for ticker in tickers}
    opening_caps = {ticker: get_opening_cap(ticker) for ticker in tickers}
    latest_caps = {ticker: get_latest_cap(ticker) for ticker in tickers}

    return histories, opening_caps, latest_caps

# function to split tickers into batches and process them in parallel
def resolve_in_batches(tickers, batch_size=20, max_workers=5):
    batches = np.array_split(tickers, np.ceil(len(tickers)/batch_size))
    
    results = []

    with concurrent.futures.ProcessPoolExecutor(max_workers=max_workers) as executor:
        futures_to_batch = {executor.submit(resolve_batch, batch): batch for batch in batches}

        for future in concurrent.futures.as_completed(futures_to_batch):
            try:
                results.append(future.result())
            except Exception as ex:
                print(f"Batch failed with error {ex}")
                import traceback
                traceback.print_exc()

    return results