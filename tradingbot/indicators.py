#!/usr/bin/env python

import pandas as pd
import talib
from tqdm import tqdm


def calculate_bollinger_bands(data, window=20):
    upperband, middleband, lowerband = talib.BBANDS(data['Close'], timeperiod=window)
    return upperband.iloc[-1], middleband.iloc[-1], lowerband.iloc[-1]


def calculate_sma(data, short_window=10, long_window=50):
    sma_short = data['Close'].rolling(window=short_window).mean()
    sma_long = data['Close'].rolling(window=long_window).mean()
    return sma_short.iloc[-1], sma_long.iloc[-1]


def calculate_macd(data, fastperiod=12, slowperiod=26, signalperiod=9):
    macd, macdsignal, macdhist = talib.MACD(data['Close'], fastperiod, slowperiod, signalperiod)
    return macd.iloc[-1], macdsignal.iloc[-1], macdhist.iloc[-1]


def calculate_rsi(data, window=14):
    rsi = talib.RSI(data['Close'], timeperiod=window)
    return rsi.iloc[-1] if rsi is not None else None


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
    indicator_dict['rsi_14'] = calculate_rsi(ticker_data)
    indicator_dict['macd'], indicator_dict['macd_signal'], indicator_dict['macd_hist'] = calculate_macd(ticker_data)
    indicator_dict['sma_10'], indicator_dict['sma_50'] = calculate_sma(ticker_data)
    indicator_dict['upperband'], indicator_dict['middleband'], indicator_dict['lowerband'] = calculate_bollinger_bands(ticker_data)

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