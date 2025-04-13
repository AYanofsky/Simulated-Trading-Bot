#!/usr/bin/env python

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from tqdm import tqdm
from tradingbot.scoring import generate_trade_signal
from tradingbot.indicators import calculate_latest_indicators, precompute_indicators
from tradingbot.utils import calculate_position_size

def process_ticker_data(timestamp, ticker, data, indicators_cache, take_profit_percent, stop_loss_percent, 
                        balance, position, position_price, pbar, commission_percent, slippage_percent, 
                        max_loss_count, cooling_off_period, cooling_off_counter, savings):
    ticker_data = data.xs(ticker, level='Ticker').loc[:timestamp].tail(50)

    # check if the indicators for this ticker and timestamp are already cached
    if (ticker, timestamp) not in indicators_cache:
        indicators_cache[(ticker, timestamp)] = calculate_latest_indicators(ticker_data)

    indicators = indicators_cache[(ticker, timestamp)]

    # generate trade signal
    signal = generate_trade_signal(indicators)

    # process trading logic for each tick
    position_data = position
    portfolio_history = []

    # cooling off period logic (no trades if cooling off is active)
    if cooling_off_counter > 0:
        cooling_off_counter -= 1
        return portfolio_history, position_data, position_price, balance, savings, cooling_off_counter

    # buying logic: if no position and signal is "BUY"
    if position_data is None and signal == "BUY":
        position_price = ticker_data['Close'].iloc[-1]

        # apply slippage and commission to the position price
        position_price *= (1 + slippage_percent / 100)
        position_price = position_price * (1 + commission_percent / 100)

        # calculate ATR for stop loss distance
        atr = indicators['atr']

        # calculate position size based on risk management (2% of balance risk per trade)
        max_shares = calculate_position_size(balance, position_price, stop_loss_percent, risk_percent=0.02)
        
        # update position and balance
        position_data = max_shares
        balance -= position_data * position_price

        # set cooling off period after buying
        cooling_off_counter = cooling_off_period

        if max_shares != 0:
            pbar.set_description(f"[SYSTEM]: {position_data:<3} SHARES OF {ticker:<4}")


    # selling logic: if position is open and the signal is SELL
    elif position_data is not None:
        # check take-profit/stop-loss conditions
        atr = indicators['atr']
        if ticker_data['Close'].iloc[-1] >= position_price + (take_profit_percent * atr):
            balance += position_data * ticker_data['Close'].iloc[-1] * 0.5
            savings += position_data * ticker_data['Close'].iloc[-1] * 0.5
            position_data = None

        elif ticker_data['Close'].iloc[-1] <= position_price - (stop_loss_percent * atr):
            balance += position_data * ticker_data['Close'].iloc[-1] * 0.5
            savings += position_data * ticker_data['Close'].iloc[-1] * 0.5
            position_data = None

        elif signal == "SELL":
            balance += position_data * ticker_data['Close'].iloc[-1]
            savings += position_data * ticker_data['Close'].iloc[-1] * 0.5
            position_data = None

    # track portfolio value
    portfolio_history.append({
        'timestamp': timestamp,
        'balance': balance,
        'savings': savings,
        'position': position_data,
        'portfolio_value': balance + savings if position_data is None else position_data * ticker_data['Close'].iloc[-1] + balance + savings
    })

    return portfolio_history, position_data, position_price, balance, savings, cooling_off_counter


def backtest(tickers, data, initial_balance=10000, stop_loss_percent=0.1356, take_profit_percent=0.1954, commission_percent=0.005, slippage_percent=0.002, max_loss_count=15, cooling_off_period=18):
    balance = initial_balance
    position = None
    position_price = 0
    savings = 0
    portfolio_history = []
    cooling_off_counter = 0

    # precompute all indicators for all tickers
    indicators_cache = precompute_indicators(data, tickers)
    
    with tqdm(total=len(data.index), desc="[SYSTEM]: RUNNING BACKTEST", unit=" datapoint") as pbar:
        for looper, (timestamp, ticker) in enumerate(data.index):
            # skip first 50 data points
            if looper < 50:
                pbar.update(1)
                continue

            # process each ticker data for each timestamp
            result, position, position_price, balance, savings, cooling_off_counter = process_ticker_data(
                timestamp, 
                ticker, 
                data, 
                indicators_cache, 
                take_profit_percent, 
                stop_loss_percent, 
                balance, position, 
                position_price, 
                pbar, 
                commission_percent, 
                slippage_percent, 
                max_loss_count, 
                cooling_off_period, 
                cooling_off_counter,
                savings
            )

            # append results to global portfolio history
            portfolio_history.extend(result)
            pbar.update(1)

    # at the end of the backtest, liquidate any open positions
    if position is not None:
        balance += position * data['Close'].iloc[-1] * (1 - commission_percent)
        print(f"[SYSTEM]: END OF BACKTEST: SOLD REMAINING POSITION AT {data['Close'].iloc[-1]}")

    # generate final portfolio report
    portfolio_history_df = pd.DataFrame(portfolio_history)
    portfolio_history_df.set_index('timestamp', inplace=True)
    portfolio_history_df['portfolio_value'].plot(title="Portfolio Value Over Time")

    final_value = portfolio_history_df['portfolio_value'].iloc[-1]
    returns = portfolio_history_df['portfolio_value'].pct_change().dropna()

    print(f"[SYSTEM]: FINAL VALUE: ${final_value:,.2f}")
    print(f"[SYSTEM]: FINAL SAVINGS: ${savings:,.2f}")
    print(f"[SYSTEM]: PERCENT GAINS: {(final_value - initial_balance) / initial_balance * 100 :,.2f}%")


    if len(returns) == 0:
        return 0.0, 0.0, 0.0, returns

    avg_return = np.mean(returns)
    volatility = np.std(returns) / avg_return
    sharpe = (avg_return - 0.005) / volatility if volatility > 0 else 0.0

    return {
        'final_value': final_value,
        'total_return': final_value / initial_balance - 1,
        'sharpe_ratio': sharpe,
        'avg_return': avg_return,
        'volatility': volatility,
        'returns': returns
    }