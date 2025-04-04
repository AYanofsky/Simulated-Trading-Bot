#!/usr/bin/env python

import argparse
from tradingbot.utils import get_tickers
from tradingbot.backtesting import backtest_multiple_tickers

# main handler function
def main(is_backtest=False):
    tickers = get_tickers()

    if is_backtest:
        print("Running backtest...")
        backtest_multiple_tickers(tickers)
    else:
        # Implement :live" trading logic here
        pass

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Trading Bot")
    parser.add_argument('--backtest', action='store_true', help="Run backtest instead of live mode.")
    args = parser.parse_args()
    main(is_backtest=args.backtest)