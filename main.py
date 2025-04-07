#!/usr/bin/env python

from tradingbot.utils import get_tickers_from_file
from tradingbot.dataloader import dataloader
from tradingbot.preprocessing import preprocess_all_data

def main():
    tickers = get_tickers_from_file()

    # returns multindex dataframe
    raw = dataloader(tickers)

    # returns dict of tickers as keys with dataframes as values
    processed = preprocess_all_data(tickers, raw)

    print(processed)

if __name__ == '__main__':
    main()