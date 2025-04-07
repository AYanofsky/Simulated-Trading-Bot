#!/usr/bin/env python

from tradingbot.utils import get_tickers_from_file
from tradingbot.dataloader import dataloader

def main():
    tickers = get_tickers_from_file()
    dataloader(tickers)

if __name__ == '__main__':
    main()