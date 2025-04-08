#!/usr/bin/env python

import pandas as pd
import numpy as np
import talib
from tqdm import tqdm

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

    # rsi (14) ---
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