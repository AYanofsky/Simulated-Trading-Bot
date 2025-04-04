#! /bin/bash/env python

from concurrent.futures import ThreadPoolExecutor, as_completed
from tradingbot.utils import get_history, get_opening_cap, get_latest_cap

# function to resolve a batch of tickers
def resolve_batch(tickers):
    
    histories = {}
    opening_caps = {}
    latest_caps = {}

    
    histories = get_history(tickers)

    tickers = histories.keys()

    for ticker in tickers:

        # this is disgusting, but this way we skip latest_caps entirely if opening_caps fails
        try:
            opening_caps[ticker] = get_opening_cap(ticker)

            try:
                latest_caps[ticker] = get_latest_cap(ticker)

            except Exception as ex:
                print(f"Error fetching latest market cap for {ticker}: {ex}")

        except Exception as ex:
            print(f"Error fetching opening market cap for {ticker}: {ex}")

    return histories, opening_caps, latest_caps

# function to split tickers into batches and process them in parallel
def resolve_in_batches(tickers, batch_size=20, max_workers=5):

    results = []

    # create batches of tickets to resolve
    batches = [tickers[i:i + batch_size] for i in range(0,len(tickers), batch_size)]

    with ThreadPoolExecutor(max_workers=max_workers) as executor:

        # map each batch to a thread
        futures = {executor.submit(resolve_batch, batch): batch for batch in batches}

        # collect results as they complete. a lot of the exception handling will occur here. it's gonna get messy.
        for future in as_completed(futures):
            try:
                batch_result = future.result()
                results.append(batch_result)
            except Exception as ex:
                print(f"Error processing batch: {ex}")

    return results