#!/usr/bin/env python

import argparse
import asyncio
from asyncio import Queue
from tradingbot.utils import get_tickers
from tradingbot.data_collection import start_collecting
from tradingbot.strategy import process_data
from tradingbot.backtesting import backtest_multiple_tickers

# main handler function
async def main(is_backtest=False):
     
    # get list of tickers from file
    tickers = get_tickers()

    # run backtest instead of getting live data
    if is_backtest:
        print("Running backtest...\n")
        backtest_multiple_tickers(tickers)
    # otherwise, run in live mode.
    else:

        # create a queue structure to pass collected data into
        data_queue = asyncio.Queue()

        # start collecting data in the background
        data_collection_task = asyncio.create_task(start_collecting(tickers,data_queue))

        # start strategy execution in the background
        strategy_execution_task = asyncio.create_task(process_data(data_queue))

        # wait for data collection to finish
        await data_collection_task

        # ensure all tasks are finished
        await data_queue.join()

        # cancel strategy execution since there's no more incoming data
        strategy_execution_task.cancel()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Trading Bot")

    parser.add_argument('--backtest', action='store_true',help="Run backtest instead of running on live data.")
    args = parser.parse_args()
    asyncio.run(main(is_backtest=args.backtest))