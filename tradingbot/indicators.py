#!/usr/bin/env python

import pandas as pd
import talib
from tqdm import tqdm

def calculate_sma(prices, window=20):
    return prices[-window:].mean()


def calculate_moving_averages(data):
    moving_averages = {}
    
    # short-term SMA (10-20 hours)
    moving_averages['sma_10'] = calculate_sma(data, window=10)
    moving_averages['sma_20'] = calculate_sma(data, window=20)
    
    # long-term SMA (50-100 hours)
    moving_averages['sma_50'] = calculate_sma(data, window=50)
    moving_averages['sma_100'] = calculate_sma(data, window=100)
    
    return moving_averages


def calculate_ema(data, window=20):
    return data['Close'].ewm(span=window, adjust=False).mean()


def calculate_exponential_moving_averages(data):
    exponential_moving_averages = {}
    
    # Short-term EMA (10-20 hours)
    exponential_moving_averages['ema_10'] = calculate_ema(data, window=10)
    exponential_moving_averages['ema_20'] = calculate_ema(data, window=20)
    
    # Long-term EMA (50-100 hours)
    exponential_moving_averages['ema_50'] = calculate_ema(data, window=50)
    exponential_moving_averages['ema_100'] = calculate_ema(data, window=100)
    
    return exponential_moving_averages


def calculate_rsi(data, window=14):
    return talib.RSI(data['Close'], timeperiod=window)


def calculate_rsi_values(data):
    rsi_values = {}
    
    # 14-hour RSI (classic)
    rsi_values['rsi_14'] = calculate_rsi(data, window=14)
    
    return rsi_values


def calculate_macd(data, fast_window=12, slow_window=26, signal_window=9):
    macd, macd_signal, macd_hist = talib.MACD(data['Close'], fastperiod=fast_window, slowperiod=slow_window, signalperiod=signal_window)
    return macd, macd_signal, macd_hist


def calculate_macd_values(data):
    macd_values = {}
    
    # Fast and Slow EMAs
    macd_values['macd'], macd_values['macd_signal'], macd_values['macd_hist'] = calculate_macd(data)
    
    return macd_values


def calculate_bollinger_bands(data, window=20):
    upperband, middleband, lowerband = talib.BBANDS(data['Close'], timeperiod=window, nbdevup=2, nbdevdn=2, matype=0)
    return upperband, middleband, lowerband


def calculate_bollinger_bands_values(data):
    bollinger_bands_values = {}
    
    # 20-hour Bollinger Bands
    bollinger_bands_values['upperband'], bollinger_bands_values['middleband'], bollinger_bands_values['lowerband'] = calculate_bollinger_bands(data, window=20)
    
    return bollinger_bands_values


def calculate_atr(data, window=14):
    return talib.ATR(data['High'], data['Low'], data['Close'], timeperiod=window)


def calculate_atr_values(data):
    atr_values = {}
    
    # 14-hour ATR
    atr_values['atr_14'] = calculate_atr(data, window=14)
    
    return atr_values


def calculate_support_resistance(data, window=50):
    # this will take the lowest and highest points within the last `window` hours
    support = data['Low'].rolling(window=window).min()
    resistance = data['High'].rolling(window=window).max()
    
    return support, resistance

def calculate_support_resistance_levels(data):
    support_resistance_levels = {}
    
    # 50-hour support and resistance
    support_resistance_levels['support_50'], support_resistance_levels['resistance_50'] = calculate_support_resistance(data, window=50)
    
    return support_resistance_levels


def calculate_adx(data, window=14):
    return talib.ADX(data['High'], data['Low'], data['Close'], timeperiod=window)


def calculate_adx_values(data):
    adx_values = {}
    
    # 14-hour ADX
    adx_values['adx_14'] = calculate_adx(data, window=14)
    
    return adx_values


def calculate_volatility(data, window=14):
    return data['Close'].rolling(window=window).std()


def calculate_volatility_values(data):
    volatility_values = {}
    
    # 14-hour volatility
    volatility_values['volatility_14'] = calculate_volatility(data, window=14)
    
    return volatility_values


def calculate_all_indicators(data):
    all_indicators = {}
    
    all_indicators.update(calculate_moving_averages(data))
    all_indicators.update(calculate_exponential_moving_averages(data))
    
    all_indicators.update(calculate_rsi_values(data))
    
    all_indicators.update(calculate_macd_values(data))
    
    all_indicators.update(calculate_bollinger_bands_values(data))
    
    all_indicators.update(calculate_atr_values(data))
    
    all_indicators.update(calculate_support_resistance_levels(data))
    
    all_indicators.update(calculate_adx_values(data))
    
    all_indicators.update(calculate_volatility_values(data))
    
    return all_indicators


def generate_indicator_dict(tickers, data):
    indicator_dict = {}

    with tqdm(total=len(tickers),desc="[SYSTEM]: Calculating indicators",unit=" ticker") as pbar:
        for ticker in tickers:
            # slice data for current ticker
            ticker_data = data.xs(ticker, level='Ticker')
#            print(ticker_data)

            # calculate the indicators for this ticker
            indicator_dict[ticker] = calculate_all_indicators(ticker_data)

            pbar.update(1)

    return indicator_dict