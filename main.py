#!/usr/bin/env python

from tradingbot.utils import get_tickers, market_cap_percentage_delta
from tradingbot.multithreading import resolve_in_batches

# variable batch size and number of threads
batch_size = 20
max_workers = 5

tickers = get_tickers()

# process batches with multithreading
results = resolve_in_batches(tickers, batch_size=batch_size, max_workers=max_workers)

# iterate over each batch result
for histories, opening_caps, latest_caps in results:
    for ticker in opening_caps.keys():
        delta = market_cap_percentage_delta(opening_caps.get(ticker), latest_caps.get(ticker))

        if delta is not None and opening_caps.get(ticker) is not None and latest_caps.get(ticker) is not None:
            print(f"CAP @ OPEN ({ticker:<4})        ${opening_caps[ticker]:,.2f}")
            print(f"CAP @ N-RT ({ticker:<4})        ${latest_caps[ticker]:,.2f}")
            print(f"CAP @ CHNG ({ticker:<4})        {delta:.2%}")
            print("")
        else:
            print(f"Could not calculate information for {ticker}.")
            print("")