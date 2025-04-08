#!/usr/bin/env python

import pandas as pd
import talib
from tqdm import tqdm


def calculate_relative_volume(data, window=20):
    rel_volume = data['Volume'] / data['Volume'].rolling(window=window).mean()
    return rel_volume.iloc[-1]


def calculate_bollinger_band_width(data, window=20):
    upperband, middleband, lowerband = talib.BBANDS(data['Close'], timeperiod=window)
    width = (upperband - lowerband) / middleband
    return width.iloc[-1]


def calculate_zscore(data, window=20):
    mean = data['Close'].rolling(window=window).mean()
    std = data['Close'].rolling(window=window).std()
    zscore = (data['Close'] - mean) / std
    return zscore.iloc[-1]


def calculate_all_indicators(ticker, ticker_data):
    indicator_dict = {}

    indicator_dict['relative_volume_20'] = calculate_relative_volume(ticker_data)
    indicator_dict['bb_width_20'] = calculate_bollinger_band_width(ticker_data)
    indicator_dict['zscore_20'] = calculate_zscore(ticker_data)

    return indicator_dict


def generate_indicator_dict(tickers, data):
    indicator_dict = {}

    with tqdm(total=len(tickers),desc="[SYSTEM]: Calculating indicators",unit=" ticker") as pbar:
        for ticker in tickers:
            # slice data for current ticker
            ticker_data = data.xs(ticker, level='Ticker')
#            print(ticker_data)

            # calculate the indicators for this ticker
            indicator_dict[ticker] = calculate_all_indicators(ticker, ticker_data)
            pbar.update(1)

    return indicator_dict