#! /bin/bash/env python

from concurrent.futures import ThreadPoolExecutor, as_completed
from tradingbot.utils import get_history, get_opening_cap, get_latest_cap

# function to resolve a batch of tickers
def resolve_batch(tickers):
    histories = []
    opening_caps = []
    latest_caps = []

    # Sequentially fetch the data for each ticker
    for ticker in tickers:
        opening_caps.append(get_opening_cap(ticker))
        latest_caps.append(get_latest_cap(ticker))
        histories.append(get_history(ticker))

    return histories, opening_caps, latest_caps

# function to split tickers into batches and process them in parallel
def resolve_in_batches(tickers, batch_size=10, max_workers=4):
    results = []

    # Split tickers into smaller batches
    batches = [tickers[i:i + batch_size] for i in range(0, len(tickers), batch_size)]
    
    # Process each batch concurrently using ThreadPoolExecutor or asyncio
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Resolve each batch asynchronously
        futures = [executor.submit(resolve_batch, batch) for batch in batches]
        for future in as_completed(futures):
            results.append(future.result())
    
    return results