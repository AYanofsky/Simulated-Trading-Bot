#!/usr/bin/env python

def get_tickers_from_file():
    with open('tradingbot-tickers-2025-04-04.txt', 'r') as file:
        tickers = file.read().split()
    return tickers