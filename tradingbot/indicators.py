#!/usr/bin/env python

import pandas as pd
import numpy as np
import talib
from tqdm import tqdm

def precompute_indicators(data, tickers):
    indicators_cache = {}

    # extract necessary columns (Close, High, Low, Volume) for all tickers
    close = data['Close']
    high = data['High']
    low = data['Low']
    volume = data['Volume']

    # compute rolling indicators across the entire DataFrame at once
    close_rolling_20 = close.rolling(window=20)
    volume_rolling_20 = volume.rolling(window=20)

    # compute relative volume (20)
    relative_volume_20 = volume / volume_rolling_20.mean()

    # bollinger bands (20)
    upperband, middleband, lowerband = talib.BBANDS(close, timeperiod=20)
    bb_width_20 = (upperband - lowerband) / middleband

    # z-score (20)
    close_rolling_mean = close_rolling_20.mean()
    close_rolling_std = close_rolling_20.std()
    zscore_20 = (close - close_rolling_mean) / close_rolling_std

    # rsi (14)
    delta = close.diff()
    gain = delta.where(delta > 0, 0).rolling(window=14).mean()
    loss = -delta.where(delta < 0, 0).rolling(window=14).mean()
    rsi_14 = 100 - (100 / (1 + (gain / loss)))

    # macd (12, 26, 9)
    macd, macdsignal, macdhist = talib.MACD(close, fastperiod=12, slowperiod=26, signalperiod=9)

    # sma 10 and 50
    sma_10 = close.rolling(window=10).mean()
    sma_50 = close.rolling(window=50).mean()

    # atr (14)
    tr = pd.concat([
        high - low,
        (high - close.shift()).abs(),
        (low - close.shift()).abs()
    ], axis=1).max(axis=1)
    atr_14 = tr.rolling(window=14).mean()

    with tqdm(total=len(data.index), desc="[SYSTEM]: CALCULATING INDICATORS", unit=" datapoint") as pbar:
        # store all indicators in the cache for each ticker and timestamp
        for ticker in tickers:
            ticker_data = data.xs(ticker, level='Ticker')
            pbar.set_description(f"[SYSTEM]: CALCULATING INDICATORS FOR {ticker:<4}")
            
            # ensure that the indicators are calculated for each timestamp up to that point
            for idx, timestamp in enumerate(ticker_data.index):
                # use .iloc and index sorcery to get the data up to and including this timestamp
                indicator_data = {
                    'relative_volume_20': relative_volume_20.iloc[:idx + 1].iloc[-1],
                    'bb_width_20': bb_width_20.iloc[:idx + 1].iloc[-1],
                    'upperband': upperband.iloc[:idx + 1].iloc[-1],
                    'middleband': middleband.iloc[:idx + 1].iloc[-1],
                    'lowerband': lowerband.iloc[:idx + 1].iloc[-1],
                    'zscore_20': zscore_20.iloc[:idx + 1].iloc[-1],
                    'rsi_14': rsi_14.iloc[:idx + 1].iloc[-1],
                    'macd': macd.iloc[:idx + 1].iloc[-1],
                    'macd_signal': macdsignal.iloc[:idx + 1].iloc[-1],
                    'macd_hist': macdhist.iloc[:idx + 1].iloc[-1],
                    'sma_10': sma_10.iloc[:idx + 1].iloc[-1],
                    'sma_50': sma_50.iloc[:idx + 1].iloc[-1],
                    'atr': ticker_data['Close'].iloc[:idx + 1].iloc[-1] - atr_14.iloc[:idx + 1].iloc[-1]
                }
                pbar.update(1)
                indicators_cache[(ticker, timestamp)] = indicator_data

    return indicators_cache


def calculate_latest_indicators(data):
    indicators = {}

    # ensure enough data is available to calculate indicators
    if len(data) < 50:
        return indicators

    # extract necessary series from the data
    close = data['Close']
    high = data['High']
    low = data['Low']
    volume = data['Volume']

    # compute rolling statistics once, then reuse
    close_rolling_20 = close.rolling(window=20)
    volume_rolling_20 = volume.rolling(window=20)

    # relative volume (20)
    indicators['relative_volume_20'] = volume.iloc[-1] / volume_rolling_20.mean().iloc[-1]

    # bollinger bands (20)
    upperband, middleband, lowerband = talib.BBANDS(close, timeperiod=20)
    indicators['bb_width_20'] = (upperband.iloc[-1] - lowerband.iloc[-1]) / middleband.iloc[-1]
    indicators['upperband'] = upperband.iloc[-1]
    indicators['middleband'] = middleband.iloc[-1]
    indicators['lowerband'] = lowerband.iloc[-1]

    # z-score (20)
    z_mean = close_rolling_20.mean().iloc[-1]
    z_std = close_rolling_20.std().iloc[-1]
    indicators['zscore_20'] = (close.iloc[-1] - z_mean) / z_std if z_std != 0 else 0

    # rsi (14)
    delta = close.diff().iloc[-14:]
    gain = delta.where(delta > 0, 0).mean()
    loss = -delta.where(delta < 0, 0).mean()

    rsi = 100 - (100 / (1 + (gain / loss))) if loss != 0 else 100
    indicators['rsi_14'] = rsi

    # macd (12, 26, 9)
    macd, macdsignal, macdhist = talib.MACD(close, fastperiod=12, slowperiod=26, signalperiod=9)
    indicators['macd'] = macd.iloc[-1]
    indicators['macd_signal'] = macdsignal.iloc[-1]
    indicators['macd_hist'] = macdhist.iloc[-1]

    # sma 10 and 50
    indicators['sma_10'] = close.iloc[-10:].mean()
    indicators['sma_50'] = close.iloc[-50:].mean()

    # atr (14)
    tr = pd.concat([
        high - low,
        (high - close.shift()).abs(),
        (low - close.shift()).abs()
    ], axis=1).max(axis=1)
    indicators['atr'] = tr.rolling(window=14).mean().iloc[-1]

    return indicators