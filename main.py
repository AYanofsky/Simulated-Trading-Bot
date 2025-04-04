#!/usr/bin/env python

from tradingbot.utils import get_opening_cap, get_latest_cap, market_cap_percentage_delta, get_tickers


tickers = get_tickers()

opening, histories = get_opening_cap(tickers)
latest =  get_latest_cap(histories)
delta = market_cap_percentage_delta(opening,latests)

"""    if delta is not None:
        print(f"CAP @ OPEN ({ticker:<4})        ${opening:,.2f}")
        print(f"CAP @ N-RT ({ticker:<4})        ${latest:,.2f}")
        print(f"CAP @ CHNG ({ticker:<4})        ${delta:.2%}")
        print("")
    else:
        print(f"Could not calculate information for {ticker}.")
        print("")
"""