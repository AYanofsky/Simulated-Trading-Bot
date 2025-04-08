#!/usr/bin/env python

import pandas as pd
import numpy as np
import talib
from tqdm import tqdm

def calculate_latest_indicators(data):
    indicators = {}

    # Ensure enough data is available to calculate indicators
    if len(data) < 50:
        return indicators  # Not enough data to compute all indicators reliably

    # Extract necessary series from the data
    close = data['Close']
    high = data['High']
    low = data['Low']
    volume = data['Volume']

    # Compute rolling statistics once, then reuse
    close_rolling_20 = close.rolling(window=20)
    volume_rolling_20 = volume.rolling(window=20)

    # Relative Volume (20)
    indicators['relative_volume_20'] = volume.iloc[-1] / volume_rolling_20.mean().iloc[-1]

    # Bollinger Bands (20)
    upperband, middleband, lowerband = talib.BBANDS(close, timeperiod=20)
    indicators['bb_width_20'] = (upperband.iloc[-1] - lowerband.iloc[-1]) / middleband.iloc[-1]
    indicators['upperband'] = upperband.iloc[-1]
    indicators['middleband'] = middleband.iloc[-1]
    indicators['lowerband'] = lowerband.iloc[-1]

    # Z-score (20)
    z_mean = close_rolling_20.mean().iloc[-1]
    z_std = close_rolling_20.std().iloc[-1]
    indicators['zscore_20'] = (close.iloc[-1] - z_mean) / z_std if z_std != 0 else 0

    # --- CUSTOM RSI (14) ---
    delta = close.diff().iloc[-14:]
    gain = delta.where(delta > 0, 0).mean()
    loss = -delta.where(delta < 0, 0).mean()

    rsi = 100 - (100 / (1 + (gain / loss))) if loss != 0 else 100
    indicators['rsi_14'] = rsi

    # MACD (12, 26, 9)
    macd, macdsignal, macdhist = talib.MACD(close, fastperiod=12, slowperiod=26, signalperiod=9)
    indicators['macd'] = macd.iloc[-1]
    indicators['macd_signal'] = macdsignal.iloc[-1]
    indicators['macd_hist'] = macdhist.iloc[-1]

    # SMA 10 and 50
    indicators['sma_10'] = close.iloc[-10:].mean()
    indicators['sma_50'] = close.iloc[-50:].mean()

    # ATR (14)
    tr = pd.concat([
        high - low,
        (high - close.shift()).abs(),
        (low - close.shift()).abs()
    ], axis=1).max(axis=1)
    indicators['atr'] = tr.rolling(window=14).mean().iloc[-1]

    return indicators