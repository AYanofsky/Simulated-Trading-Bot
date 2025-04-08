#!/usr/bin/env python

import pandas as pd

def evaluate_buy_signal(indicators):
    buy_score = 0

    # RSI condition (buy when RSI is under 30, oversold)
    if indicators.get('rsi_14', 0) < 30:
        buy_score += 1

    # Moving Average condition (short-term average above long-term average)
    if indicators.get('sma_10', 0) > indicators.get('sma_50', 0):
        buy_score += 1

    # Bollinger Bands condition (price near lower band, possible rebound)
    if indicators.get('bb_width_20', 0) > 0.2 and indicators.get('zscore_20', 0) < -1:
        buy_score += 1

    # MACD condition (MACD crossing above signal line)
    if indicators.get('macd', 0) > indicators.get('macd_signal', 0):
        buy_score += 1

    # Relative Volume condition (higher volume than average)
    if indicators.get('relative_volume_20', 0) > 1.5:
        buy_score += 1

    return buy_score


def evaluate_sell_signal(indicators):
    sell_score = 0

    # RSI condition (sell when RSI is above 70, overbought)
    if indicators.get('rsi_14', 0) > 70:
        sell_score += 1

    # Moving Average condition (short-term average below long-term average)
    if indicators.get('sma_10', 0) < indicators.get('sma_50', 0):
        sell_score += 1

    # Bollinger Bands condition (price near upper band, possible reversal)
    if indicators.get('bb_width_20', 0) > 0.2 and indicators.get('zscore_20', 0) > 1:
        sell_score += 1

    # MACD condition (MACD crossing below signal line)
    if indicators.get('macd', 0) < indicators.get('macd_signal', 0):
        sell_score += 1

    return sell_score


def generate_trade_signal(indicators, buy_threshold=3, sell_threshold=3):
    buy_score = evaluate_buy_signal(indicators)
    sell_score = evaluate_sell_signal(indicators)

    # Buy if score reaches threshold
    if buy_score >= buy_threshold:
        return "BUY"
    # Sell if score reaches threshold
    elif sell_score >= sell_threshold:
        return "SELL"
    # Else, Hold
    else:
        return "HOLD"


def calculate_trade_confidence(indicators):
    buy_score = evaluate_buy_signal(indicators)
    sell_score = evaluate_sell_signal(indicators)

    if buy_score >= 3:
        return "BUY", buy_score
    elif sell_score >= 3:
        return "SELL", sell_score
    else:
        return "HOLD", max(buy_score, sell_score)