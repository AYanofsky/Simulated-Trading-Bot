#!/usr/bin/env python

import pandas as pd


def evaluate_buy_signal(indicators):
    # Example buy conditions:
    buy_score = 0

    # RSI condition (buy when RSI is under 30, oversold)
    if indicators.get('rsi_14', 0) < 30:
        buy_score += 1

    # MACD condition (buy when MACD crosses above the signal line)
    if indicators.get('macd', 0) > indicators.get('macd_signal', 0):
        buy_score += 1

    # Bollinger Band condition (buy when price is below lower Bollinger Band)
    if indicators.get('close', 0) < indicators.get('lowerband', 0):
        buy_score += 1

    # Check if moving averages show an uptrend (short-term MA above long-term MA)
    if indicators.get('sma_10', 0) > indicators.get('sma_50', 0):
        buy_score += 1

    return buy_score


def evaluate_sell_signal(indicators):
    # update conditions later
    sell_score = 0

    # RSI condition (RSI is above 70, overbought)
    if indicators.get('rsi_14', 0) > 70:
        sell_score += 1

    # MACD condition (sell when MACD crosses below the signal line)
    if indicators.get('macd', 0) < indicators.get('macd_signal', 0):
        sell_score += 1

    # Bollinger Band condition (sell when price is above upper Bollinger Band)
    if indicators.get('close', 0) > indicators.get('upperband', 0):
        sell_score += 1

    # check if moving averages show a downtrend (short-term MA below long-term MA)
    if indicators.get('sma_10', 0) < indicators.get('sma_50', 0):
        sell_score += 1

    return sell_score


def generate_trade_signal(indicators):
    # generate buy/sell/hold signals
    buy_score = evaluate_buy_signal(indicators)
    sell_score = evaluate_sell_signal(indicators)

    if buy_score >= 3:
        return "BUY"
    elif sell_score >= 3:
        return "SELL"
    else:
        return "HOLD"
