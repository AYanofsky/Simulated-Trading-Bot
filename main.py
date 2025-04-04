#!/usr/bin/env python

import argparse
#import asyncio
from tradingbot.utils import get_tickers
#from tradingbot.data_collection import start_collecting
from tradingbot.backtesting import backtest_multiple_tickers

# Main handler function
async def main(is_backtest=False):
    tickers = get_tickers()

    if is_backtest:
        print("Running backtest...")
        backtest_multiple_tickers(tickers)
    else:
        # this is where my "live" trading logic will go
        pass

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Trading Bot")
    parser.add_argument('--backtest', action='store_true', help="Run backtest instead of live mode.")
    args = parser.parse_args()
    asyncio.run(main(is_backtest=args.backtest))