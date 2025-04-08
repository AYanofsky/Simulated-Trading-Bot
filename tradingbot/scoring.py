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

    return buy_score


def evaluate_sell_signal(indicators):
    sell_score = 0

    # RSI condition (sell when RSI is above 70, overbought)
    if indicators.get('rsi_14', 0) > 70:
        sell_score += 1

    # Moving Average condition (short-term average below long-term average)
    if indicators.get('sma_10', 0) < indicators.get('sma_50', 0):
        sell_score += 1

    return sell_score


def generate_trade_signal(indicators, buy_threshold=2, sell_threshold=2):
    buy_score = evaluate_buy_signal(indicators)
    sell_score = evaluate_sell_signal(indicators)

    if buy_score >= buy_threshold:
        return "BUY"
    elif sell_score >= sell_threshold:
        return "SELL"
    else:
        return "HOLD"