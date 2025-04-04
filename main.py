#!/usr/bin/env python

from tradingbot.utils import get_tickers
from tradingbot.multithreading import resolve_in_batches

tickers = get_tickers()
results = resolve_in_batches(tickers)
