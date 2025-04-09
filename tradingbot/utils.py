#!/usr/bin/env python

import pandas as pd
import numpy as np


def get_tickers_from_file():
    with open('tradingbot-tickers-2025-04-04.txt', 'r') as file:
        tickers = file.read().split()
    return tickers


def calculate_position_size(balance, position_price, atr, risk_percent=0.02):
    # calculate the dollar amount you're willing to risk
    risk_amount = balance * risk_percent

    # calculate stop loss distance as a multiple of ATR (e.g., 1 ATR)
    stop_loss_distance = atr

    # calculate the number of shares to buy
    max_shares = np.clip(int(risk_amount / (stop_loss_distance * position_price)),0,100)
    
    return max_shares
